# Resume Brief — Structure & Lifecycle

A **Resume Brief** is a concise, human-readable summary saved to **MinIO** after each session; DB stores its `versionId` and SHA.

## JSON structure (stored alongside Markdown)
```json
{
  "session": "2025-09-10T20:16:00Z",
  "trace_id": "c1db1a24-1f8d-4a1f-8d0f-3b8b8a0e8c2a",
  "summary": "DLQ implemented; added metrics; docs updated.",
  "what_changed": ["Compose mosquitto TLS", "New metric taylor_dlq_total"],
  "risks": ["TLS misconfig on broker"],
  "next_plan": ["Add DLQ replay UI", "Threshold alert"],
  "artifacts": [
    { "type": "doc", "path": "docs/observability.md", "hash": "…" },
    { "type": "grafana", "path": "infra/grafana/dashboards/dlq.json", "hash": "…" }
  ]
}
```

## Retrieval

On Resume Mode, Scribe loads latest brief and the last 50 Run Journal entries to propose a new Session Plan.