"""
Async MQTT client with reconnect, backoff, DLQ, and Postgres mirror
"""
import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

import aiomqtt
from opentelemetry import trace
from prometheus_client import Counter, Histogram, Gauge
import asyncpg

from .otel import get_tracer
from .logging_utils import get_logger, MQTTError

# Metrics
mqtt_ingest_total = Counter('taylor_ingest_total', 'Total MQTT events ingested', ['topic', 'kind'])
mqtt_dlq_total = Counter('taylor_dlq_total', 'Total events sent to DLQ', ['topic', 'reason'])
mqtt_event_latency = Histogram('taylor_event_latency_seconds', 'Event processing latency')
mqtt_connections = Gauge('taylor_mqtt_connections_active', 'Active MQTT connections')

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)

class MQTTEventProcessor:
    """Async MQTT client with DLQ and Postgres mirroring"""
    
    def __init__(self, broker_host: str, broker_port: int, username: str, password: str,
                 db_pool: asyncpg.Pool):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.db_pool = db_pool
        self.client: Optional[asyncio_mqtt.Client] = None
        self.running = False
        
        # Reconnect settings
        self.max_retries = 5
        self.base_delay = 1.0
        self.max_delay = 60.0
        
    async def start(self):
        """Start MQTT client with reconnect logic"""
        self.running = True
        retry_count = 0
        struct_logger = get_logger()
        
        await struct_logger.info(
            "Starting MQTT processor",
            category="MQTT",
            severity="INFO",
            context={
                "broker_host": self.broker_host,
                "broker_port": self.broker_port,
                "max_retries": self.max_retries
            }
        )
        
        while self.running:
            try:
                await self._connect_and_process()
                retry_count = 0  # Reset on successful connection
            except Exception as e:
                retry_count += 1
                if retry_count <= self.max_retries:
                    delay = min(self.base_delay * (2 ** (retry_count - 1)), self.max_delay)
                    
                    await struct_logger.warn(
                        f"MQTT connection failed, retrying in {delay}s",
                        category="MQTT",
                        severity="MEDIUM",
                        context={
                            "retry_count": retry_count,
                            "delay_seconds": delay,
                            "broker_host": self.broker_host,
                            "error": str(e)
                        },
                        details=str(e)
                    )
                    
                    await asyncio.sleep(delay)
                else:
                    await struct_logger.error(
                        "MQTT max retries exceeded",
                        exc=MQTTError("Connection failed after maximum retries", str(e)),
                        category="MQTT",
                        severity="CRITICAL",
                        context={
                            "max_retries": self.max_retries,
                            "broker_host": self.broker_host,
                            "final_error": str(e)
                        }
                    )
                    break
    
    async def _connect_and_process(self):
        """Connect to MQTT broker and process messages"""
        async with aiomqtt.Client(
            hostname=self.broker_host,
            port=self.broker_port,
            username=self.username,
            password=self.password
        ) as client:
            self.client = client
            mqtt_connections.inc()
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            
            # Subscribe to all tracker topics
            await client.subscribe("tracker/events/+/+")
            await client.subscribe("tracker/commands/+")
            await client.subscribe("tracker/metrics/+")
            
            async for message in client.messages:
                await self._process_message(message)
                
    async def _process_message(self, message):
        """Process incoming MQTT message with DLQ on failure"""
        start_time = time.time()
        topic = str(message.topic)
        
        with tracer.start_as_current_span("mqtt.process_message") as span:
            span.set_attributes({
                "mqtt.topic": topic,
                "mqtt.qos": message.qos,
                "mqtt.payload_size": len(message.payload)
            })
            
            try:
                # Parse JSON payload
                try:
                    payload = json.loads(message.payload.decode())
                except json.JSONDecodeError as e:
                    await self._send_to_dlq(topic, message.payload, f"JSON decode error: {e}")
                    return
                
                # Validate required fields
                required_fields = ['trace_id', 'ts', 'kind', 'idempotency_key']
                missing_fields = [f for f in required_fields if f not in payload]
                if missing_fields:
                    await self._send_to_dlq(topic, payload, f"Missing fields: {missing_fields}")
                    return
                
                # Set trace context
                span.set_attributes({
                    "event.trace_id": payload['trace_id'],
                    "event.kind": payload['kind']
                })
                
                # Mirror to Postgres
                await self._mirror_to_postgres(topic, payload)
                
                # Update metrics
                mqtt_ingest_total.labels(topic=topic, kind=payload['kind']).inc()
                mqtt_event_latency.observe(time.time() - start_time)
                
                logger.debug(f"Processed event {payload['kind']} from {topic}")
                
            except Exception as e:
                logger.error(f"Error processing message from {topic}: {e}")
                await self._send_to_dlq(topic, message.payload, f"Processing error: {e}")
    
    async def _mirror_to_postgres(self, topic: str, payload: Dict[str, Any]):
        """Mirror event to Postgres events_mirror table"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO events_mirror (topic, payload, created_at)
                VALUES ($1, $2, $3)
            """, topic, json.dumps(payload), datetime.now(timezone.utc))
    
    async def _send_to_dlq(self, original_topic: str, payload: Any, reason: str):
        """Send failed message to Dead Letter Queue"""
        dlq_topic = f"tracker/dlq/{original_topic.replace('/', '_')}"
        
        dlq_payload = {
            "original_topic": original_topic,
            "failure_reason": reason,
            "failure_timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload if isinstance(payload, dict) else payload.decode() if isinstance(payload, bytes) else str(payload)
        }
        
        try:
            if self.client:
                await self.client.publish(dlq_topic, json.dumps(dlq_payload), qos=1)
                
            # Also store in DLQ table
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO dlq_events (original_topic, failure_reason, payload, created_at)
                    VALUES ($1, $2, $3, $4)
                """, original_topic, reason, json.dumps(dlq_payload), datetime.now(timezone.utc))
                
            mqtt_dlq_total.labels(topic=original_topic, reason=reason).inc()
            logger.warning(f"Sent message to DLQ: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to send to DLQ: {e}")
    
    async def publish_event(self, topic: str, kind: str, payload: Dict[str, Any], 
                          trace_id: Optional[str] = None, max_retries: int = 3) -> str:
        """Publish event with required metadata and retry logic"""
        if not trace_id:
            trace_id = str(uuid.uuid4())
            
        event = {
            "trace_id": trace_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "idempotency_key": f"{kind}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}",
            "payload": payload
        }
        
        struct_logger = get_logger()
        
        with tracer.start_as_current_span("mqtt.publish_event") as span:
            span.set_attributes({
                "mqtt.topic": topic,
                "event.trace_id": trace_id,
                "event.kind": kind
            })
            
            # Retry logic with exponential backoff
            for attempt in range(max_retries):
                try:
                    if not self.client:
                        raise MQTTError("MQTT client not connected", "Client instance is None")
                    
                    await self.client.publish(topic, json.dumps(event), qos=1)
                    
                    await struct_logger.debug(
                        f"Published {kind} event to {topic}",
                        category="MQTT",
                        severity="INFO",
                        trace_id=trace_id,
                        context={
                            "topic": topic,
                            "kind": kind,
                            "attempt": attempt + 1,
                            "payload_size": len(json.dumps(payload))
                        }
                    )
                    
                    return trace_id
                
                except Exception as e:
                    is_last_attempt = attempt == max_retries - 1
                    
                    if is_last_attempt:
                        # Final attempt failed - send to DLQ and log error
                        await self._send_to_dlq(topic, event, f"Publish failed after {max_retries} attempts: {e}")
                        
                        await struct_logger.error(
                            f"Failed to publish {kind} event after {max_retries} attempts",
                            exc=MQTTError("Event publishing failed", str(e)),
                            category="MQTT",
                            severity="HIGH",
                            trace_id=trace_id,
                            context={
                                "topic": topic,
                                "kind": kind,
                                "max_retries": max_retries,
                                "event": event
                            }
                        )
                        raise MQTTError(f"Failed to publish event after {max_retries} attempts", str(e))
                    else:
                        # Retry with backoff
                        delay = min(2 ** attempt, 10)  # Max 10s delay
                        
                        await struct_logger.warn(
                            f"MQTT publish attempt {attempt + 1} failed, retrying in {delay}s",
                            category="MQTT",
                            severity="MEDIUM",
                            trace_id=trace_id,
                            context={
                                "topic": topic,
                                "kind": kind,
                                "attempt": attempt + 1,
                                "delay_seconds": delay,
                                "error": str(e)
                            }
                        )
                        
                        await asyncio.sleep(delay)
        
        return trace_id
    
    async def stop(self):
        """Stop MQTT client"""
        self.running = False
        if self.client:
            mqtt_connections.dec()
            logger.info("Disconnected from MQTT broker")

# Global instance
mqtt_processor: Optional[MQTTEventProcessor] = None

async def get_mqtt_processor() -> MQTTEventProcessor:
    """Get global MQTT processor instance"""
    if mqtt_processor is None:
        raise RuntimeError("MQTT processor not initialized")
    return mqtt_processor

async def init_mqtt_processor(broker_host: str, broker_port: int, username: str, 
                            password: str, db_pool: asyncpg.Pool):
    """Initialize global MQTT processor"""
    global mqtt_processor
    mqtt_processor = MQTTEventProcessor(broker_host, broker_port, username, password, db_pool)
    return mqtt_processor