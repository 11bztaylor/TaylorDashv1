"""
JSON Schema definitions for MQTT events
"""
from typing import Dict, Any
import jsonschema

# Event schemas
EVENT_BASE_SCHEMA = {
    "type": "object",
    "required": ["trace_id", "ts", "kind", "idempotency_key"],
    "properties": {
        "trace_id": {"type": "string", "format": "uuid"},
        "ts": {"type": "string", "format": "date-time"},
        "kind": {"type": "string"},
        "idempotency_key": {"type": "string"},
        "payload": {"type": "object"}
    },
    "additionalProperties": False
}

PROJECT_EVENT_SCHEMA = {
    "allOf": [EVENT_BASE_SCHEMA],
    "properties": {
        **EVENT_BASE_SCHEMA["properties"],
        "kind": {"enum": ["project.created", "project.updated", "project.deleted"]},
        "payload": {
            "type": "object",
            "required": ["project_id", "name"],
            "properties": {
                "project_id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "status": {"enum": ["active", "archived", "completed"]},
                "owner_id": {"type": "string"},
                "metadata": {"type": "object"}
            }
        }
    }
}

COMPONENT_EVENT_SCHEMA = {
    "allOf": [EVENT_BASE_SCHEMA],
    "properties": {
        **EVENT_BASE_SCHEMA["properties"],
        "kind": {"enum": ["component.created", "component.updated", "component.linked", "component.unlinked"]},
        "payload": {
            "type": "object",
            "required": ["component_id", "project_id"],
            "properties": {
                "component_id": {"type": "string"},
                "project_id": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string"},
                "status": {"enum": ["pending", "in_progress", "completed", "blocked"]},
                "progress": {"type": "number", "minimum": 0, "maximum": 100},
                "dependencies": {"type": "array", "items": {"type": "string"}},
                "position": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number"},
                        "y": {"type": "number"}
                    }
                }
            }
        }
    }
}

TASK_EVENT_SCHEMA = {
    "allOf": [EVENT_BASE_SCHEMA],
    "properties": {
        **EVENT_BASE_SCHEMA["properties"],
        "kind": {"enum": ["task.created", "task.updated", "task.completed", "task.assigned"]},
        "payload": {
            "type": "object",
            "required": ["task_id", "component_id"],
            "properties": {
                "task_id": {"type": "string"},
                "component_id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "status": {"enum": ["todo", "in_progress", "review", "done"]},
                "assignee_id": {"type": "string"},
                "due_date": {"type": "string", "format": "date-time"},
                "completed_at": {"type": "string", "format": "date-time"}
            }
        }
    }
}

METRICS_EVENT_SCHEMA = {
    "allOf": [EVENT_BASE_SCHEMA],
    "properties": {
        **EVENT_BASE_SCHEMA["properties"],
        "kind": {"enum": ["metric.gauge", "metric.counter", "metric.histogram"]},
        "payload": {
            "type": "object",
            "required": ["metric_name", "value"],
            "properties": {
                "metric_name": {"type": "string"},
                "value": {"type": "number"},
                "labels": {"type": "object"},
                "timestamp": {"type": "string", "format": "date-time"}
            }
        }
    }
}

# Schema registry
SCHEMA_REGISTRY: Dict[str, Dict[str, Any]] = {
    "project.created": PROJECT_EVENT_SCHEMA,
    "project.updated": PROJECT_EVENT_SCHEMA,
    "project.deleted": PROJECT_EVENT_SCHEMA,
    "component.created": COMPONENT_EVENT_SCHEMA,
    "component.updated": COMPONENT_EVENT_SCHEMA,
    "component.linked": COMPONENT_EVENT_SCHEMA,
    "component.unlinked": COMPONENT_EVENT_SCHEMA,
    "task.created": TASK_EVENT_SCHEMA,
    "task.updated": TASK_EVENT_SCHEMA,
    "task.completed": TASK_EVENT_SCHEMA,
    "task.assigned": TASK_EVENT_SCHEMA,
    "metric.gauge": METRICS_EVENT_SCHEMA,
    "metric.counter": METRICS_EVENT_SCHEMA,
    "metric.histogram": METRICS_EVENT_SCHEMA,
}

def validate_event(kind: str, event_data: Dict[str, Any]) -> bool:
    """Validate event against schema"""
    try:
        schema = SCHEMA_REGISTRY.get(kind, EVENT_BASE_SCHEMA)
        jsonschema.validate(event_data, schema)
        return True
    except jsonschema.ValidationError:
        return False

def get_schema(kind: str) -> Dict[str, Any]:
    """Get schema for event kind"""
    return SCHEMA_REGISTRY.get(kind, EVENT_BASE_SCHEMA)