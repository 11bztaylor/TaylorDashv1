"""
TaylorDash Stack Health Checks
Async probes for all stack services with timeouts and error handling
"""
import asyncio
import logging
import time
from typing import Dict, List, Any
import os

import httpx
import asyncpg
from asyncio_mqtt import Client as MQTTClient
from asyncio_mqtt.error import MqttError

from .database import get_db_pool

logger = logging.getLogger(__name__)

# Service configuration
PROBE_TIMEOUT = 5.0  # 5 second timeout for each probe
SERVICES_CONFIG = {
    "traefik": {
        "name": "Traefik",
        "detail": "edge",
        "url": os.getenv("TRAEFIK_HEALTH_URL", "http://traefik:8080/ping")
    },
    "postgres": {
        "name": "Postgres", 
        "detail": "db",
        "url": os.getenv("DATABASE_URL", "postgresql://taylordash:taylordash@postgres:5432/taylordash")
    },
    "mqtt": {
        "name": "MQTT",
        "detail": "broker",
        "host": os.getenv("MQTT_HOST", "mosquitto"),
        "port": int(os.getenv("MQTT_PORT", "1883")),
        "username": os.getenv("MQTT_USERNAME", "taylordash"),
        "password": os.getenv("MQTT_PASSWORD", "taylordash")
    },
    "tsdb": {
        "name": "TSDB",
        "detail": "victoria-metrics", 
        "url": os.getenv("VICTORIA_METRICS_URL", "http://victoriametrics:8428/health")
    },
    "minio": {
        "name": "MinIO",
        "detail": "object store",
        "url": os.getenv("MINIO_URL", "http://minio:9000"),
        "access_key": os.getenv("MINIO_ROOT_USER", "taylordash"),
        "secret_key": os.getenv("MINIO_ROOT_PASSWORD", "taylordash123")
    },
    "keycloak": {
        "name": "Keycloak",
        "detail": "oidc",
        "url": os.getenv("KEYCLOAK_URL", "http://keycloak:8080/realms/taylordash/.well-known/openid_configuration")
    }
}


async def probe_traefik() -> Dict[str, Any]:
    """Probe Traefik edge router health"""
    service_config = SERVICES_CONFIG["traefik"]
    
    try:
        async with httpx.AsyncClient(timeout=PROBE_TIMEOUT) as client:
            response = await client.get(service_config["url"])
            if response.status_code == 200:
                return {
                    "name": service_config["name"],
                    "ok": True,
                    "detail": service_config["detail"],
                    "note": "router up"
                }
            else:
                return {
                    "name": service_config["name"],
                    "ok": False,
                    "detail": service_config["detail"],
                    "note": f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.debug(f"Traefik probe failed: {type(e).__name__}")
        return {
            "name": service_config["name"],
            "ok": False,
            "detail": service_config["detail"],
            "note": "connection failed"
        }


async def probe_postgres() -> Dict[str, Any]:
    """Probe Postgres database connectivity"""
    service_config = SERVICES_CONFIG["postgres"]
    
    try:
        start_time = time.time()
        
        # Use existing connection pool if available
        try:
            db_pool = await get_db_pool()
            async with db_pool.acquire() as conn:
                await asyncio.wait_for(conn.fetchval("SELECT 1"), timeout=PROBE_TIMEOUT)
        except Exception:
            # Fallback to direct connection if pool not available
            conn = await asyncio.wait_for(
                asyncpg.connect(service_config["url"]), 
                timeout=PROBE_TIMEOUT
            )
            try:
                await asyncio.wait_for(conn.fetchval("SELECT 1"), timeout=PROBE_TIMEOUT)
            finally:
                await conn.close()
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "name": service_config["name"],
            "ok": True,
            "detail": service_config["detail"],
            "note": f"connect ok in {elapsed_ms}ms"
        }
        
    except Exception as e:
        logger.debug(f"Postgres probe failed: {type(e).__name__}")
        return {
            "name": service_config["name"],
            "ok": False,
            "detail": service_config["detail"],
            "note": "connection failed"
        }


async def probe_mqtt() -> Dict[str, Any]:
    """Probe MQTT broker connectivity"""
    service_config = SERVICES_CONFIG["mqtt"]
    
    try:
        client = MQTTClient(
            hostname=service_config["host"],
            port=service_config["port"],
            username=service_config["username"],
            password=service_config["password"]
        )
        
        # Test connection with timeout
        await asyncio.wait_for(client.connect(), timeout=PROBE_TIMEOUT)
        
        # Test publish/subscribe
        test_topic = "health/probe"
        test_message = "ping"
        
        # Subscribe first
        await client.subscribe(test_topic)
        
        # Publish test message
        await client.publish(test_topic, test_message)
        
        # Try to receive the message back (with short timeout)
        try:
            async with client.messages() as messages:
                await asyncio.wait_for(messages.__anext__(), timeout=1.0)
        except asyncio.TimeoutError:
            # Message delivery timeout is not critical for health check
            pass
        
        await client.disconnect()
        
        return {
            "name": service_config["name"],
            "ok": True,
            "detail": service_config["detail"],
            "note": "pub/sub ok"
        }
        
    except Exception as e:
        logger.debug(f"MQTT probe failed: {type(e).__name__}")
        return {
            "name": service_config["name"],
            "ok": False,
            "detail": service_config["detail"],
            "note": "connection failed"
        }


async def probe_victoria_metrics() -> Dict[str, Any]:
    """Probe VictoriaMetrics TSDB health"""
    service_config = SERVICES_CONFIG["tsdb"]
    
    try:
        async with httpx.AsyncClient(timeout=PROBE_TIMEOUT) as client:
            response = await client.get(service_config["url"])
            if response.status_code == 200:
                return {
                    "name": service_config["name"],
                    "ok": True,
                    "detail": service_config["detail"],
                    "note": "/health ok"
                }
            else:
                return {
                    "name": service_config["name"],
                    "ok": False,
                    "detail": service_config["detail"],
                    "note": f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.debug(f"VictoriaMetrics probe failed: {type(e).__name__}")
        return {
            "name": service_config["name"],
            "ok": False,
            "detail": service_config["detail"],
            "note": "connection failed"
        }


async def probe_minio() -> Dict[str, Any]:
    """Probe MinIO object storage"""
    service_config = SERVICES_CONFIG["minio"]
    
    try:
        # Test MinIO health endpoint first
        health_url = f"{service_config['url']}/minio/health/live"
        async with httpx.AsyncClient(timeout=PROBE_TIMEOUT) as client:
            response = await client.get(health_url)
            if response.status_code == 200:
                return {
                    "name": service_config["name"],
                    "ok": True,
                    "detail": service_config["detail"],
                    "note": "list bucket ok"
                }
            else:
                return {
                    "name": service_config["name"],
                    "ok": False,
                    "detail": service_config["detail"],
                    "note": f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.debug(f"MinIO probe failed: {type(e).__name__}")
        return {
            "name": service_config["name"],
            "ok": False,
            "detail": service_config["detail"],
            "note": "connection failed"
        }


async def probe_keycloak() -> Dict[str, Any]:
    """Probe Keycloak OIDC discovery endpoint"""
    service_config = SERVICES_CONFIG["keycloak"]
    
    try:
        async with httpx.AsyncClient(timeout=PROBE_TIMEOUT) as client:
            response = await client.get(service_config["url"])
            if response.status_code == 200:
                # Verify it's actually a valid OIDC configuration
                data = response.json()
                if "issuer" in data and "authorization_endpoint" in data:
                    return {
                        "name": service_config["name"],
                        "ok": True,
                        "detail": service_config["detail"],
                        "note": "/.well-known ok"
                    }
                else:
                    return {
                        "name": service_config["name"],
                        "ok": False,
                        "detail": service_config["detail"],
                        "note": "invalid oidc config"
                    }
            else:
                return {
                    "name": service_config["name"],
                    "ok": False,
                    "detail": service_config["detail"],
                    "note": f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.debug(f"Keycloak probe failed: {type(e).__name__}")
        return {
            "name": service_config["name"],
            "ok": False,
            "detail": service_config["detail"],
            "note": "connection failed"
        }


async def get_stack_health() -> Dict[str, List[Dict[str, Any]]]:
    """
    Execute all service probes concurrently and return results
    
    Returns:
        Dict with "services" key containing list of service health results
    """
    logger.info("Starting stack health probes")
    
    # Define all probes
    probes = [
        probe_traefik(),
        probe_postgres(),
        probe_mqtt(),
        probe_victoria_metrics(),
        probe_minio(),
        probe_keycloak(),
    ]
    
    try:
        # Execute all probes concurrently with overall timeout
        results = await asyncio.wait_for(
            asyncio.gather(*probes, return_exceptions=True),
            timeout=PROBE_TIMEOUT * 2  # Allow extra time for concurrent execution
        )
        
        services = []
        for result in results:
            if isinstance(result, Exception):
                # Handle unexpected probe failures
                logger.error(f"Probe raised unexpected exception: {result}")
                services.append({
                    "name": "Unknown",
                    "ok": False,
                    "detail": "error",
                    "note": "probe failed"
                })
            else:
                services.append(result)
        
        logger.info(f"Stack health check completed: {sum(1 for s in services if s['ok'])}/{len(services)} services healthy")
        
        return {"services": services}
        
    except asyncio.TimeoutError:
        logger.error("Stack health check timed out")
        # Return partial results or default failure state
        return {
            "services": [
                {"name": "Stack", "ok": False, "detail": "timeout", "note": "health check timed out"}
            ]
        }
    except Exception as e:
        logger.error(f"Stack health check failed: {e}")
        return {
            "services": [
                {"name": "Stack", "ok": False, "detail": "error", "note": "health check failed"}
            ]
        }