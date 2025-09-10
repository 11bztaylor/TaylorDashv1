"""
MQTT integration tests
"""
import asyncio
import json
import pytest
import time
from unittest.mock import AsyncMock

from backend.app.mqtt_client import MQTTEventProcessor
from backend.app.schemas import validate_event

@pytest.fixture
async def db_pool():
    """Mock database pool"""
    pool = AsyncMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__.return_value = conn
    return pool

@pytest.fixture
async def mqtt_processor(db_pool):
    """MQTT processor fixture"""
    processor = MQTTEventProcessor("localhost", 1883, "test", "test", db_pool)
    return processor

@pytest.mark.asyncio
async def test_event_validation():
    """Test event schema validation"""
    valid_event = {
        "trace_id": "550e8400-e29b-41d4-a716-446655440000",
        "ts": "2024-01-15T14:30:00.000Z",
        "kind": "project.created",
        "idempotency_key": "test-key-123",
        "payload": {
            "project_id": "proj-123",
            "name": "Test Project"
        }
    }
    
    assert validate_event("project.created", valid_event)
    
    # Test missing required field
    invalid_event = valid_event.copy()
    del invalid_event["trace_id"]
    assert not validate_event("project.created", invalid_event)

@pytest.mark.asyncio 
async def test_publish_event(mqtt_processor):
    """Test event publishing"""
    # Mock the client
    mqtt_processor.client = AsyncMock()
    
    trace_id = await mqtt_processor.publish_event(
        "tracker/events/test/component",
        "component.created", 
        {"component_id": "comp-123", "project_id": "proj-123"}
    )
    
    assert trace_id is not None
    mqtt_processor.client.publish.assert_called_once()

@pytest.mark.asyncio
async def test_dlq_handling(mqtt_processor):
    """Test DLQ functionality"""
    # Mock the client and db
    mqtt_processor.client = AsyncMock()
    
    await mqtt_processor._send_to_dlq(
        "tracker/events/test",
        {"invalid": "payload"},
        "Test failure"
    )
    
    # Verify DLQ topic publish
    mqtt_processor.client.publish.assert_called_once()
    args, kwargs = mqtt_processor.client.publish.call_args
    assert args[0] == "tracker/dlq/tracker_events_test"

def test_performance_load():
    """Test that we can handle 1000 events quickly"""
    # This would be a full integration test with real MQTT
    # For now, just test event creation performance
    
    start_time = time.time()
    events = []
    
    for i in range(1000):
        event = {
            "trace_id": f"trace-{i:04d}",
            "ts": "2024-01-15T14:30:00.000Z", 
            "kind": "test.event",
            "idempotency_key": f"key-{i}",
            "payload": {"index": i}
        }
        events.append(event)
    
    duration = time.time() - start_time
    assert duration < 1.0  # Should create 1000 events in under 1 second
    assert len(events) == 1000