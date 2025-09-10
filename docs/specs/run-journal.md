# Run Journal — JSONL Schema

The Run Journal is the **append-only** execution log every agent writes to. It powers **resume** and **audit**.

## File format
- **One JSON object per line** (`.jsonl`)
- Rotation: daily files under `state/run_journal/YYMMDD.jsonl`
- Each record includes:

```json
{
  "ts": "2025-09-10T20:15:03Z",
  "trace_id": "f3d5a26b-2a0f-4e5f-9a9f-0d1f934f5b11",
  "agent": "backend",
  "task": "implement_mqtt_dlq",
  "inputs": { "topics": ["tracker/events/+"] },
  "outputs": { "metrics_added": ["taylor_dlq_total"] },
  "status": "success",
  "links": {
    "pr": "git://…",
    "docs": "docs/observability.md#metrics-inventory"
  }
}
```

## Correlation

`trace_id` ties spans (OTel) to logs and metrics; `/metrics` provides counters/histograms for external scraping.

## Validation

The QA/Tests agent rejects a session if required fields or correlation IDs are missing.