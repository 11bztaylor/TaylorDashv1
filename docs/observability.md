# Observability

TaylorDash implements comprehensive observability through Prometheus metrics, OpenTelemetry tracing, and structured logging.

## Metrics Exposition

### Prometheus Text Format

TaylorDash exposes metrics at `/metrics` endpoint using the [Prometheus text exposition format](https://prometheus.io/docs/instrumenting/exposition_formats/). All metrics follow the [OpenMetrics](https://openmetrics.io/) specification.

#### Format Structure

Each metric family includes:
- **`# HELP`**: Human-readable description
- **`# TYPE`**: Metric type (counter, gauge, histogram, summary)
- **Labels**: Key-value pairs for dimensionality

#### Example Metric Families

**Counter - MQTT Events Processed**
```
# HELP mqtt_ingest_total Total number of MQTT events processed
# TYPE mqtt_ingest_total counter
mqtt_ingest_total{topic="tracker/project/status",status="success"} 1234
mqtt_ingest_total{topic="tracker/project/status",status="error"} 5
mqtt_ingest_total{topic="tracker/system/health",status="success"} 891
```

**Gauge - Active Connections**
```
# HELP database_connections_active Current number of active database connections
# TYPE database_connections_active gauge
database_connections_active{pool="postgres"} 8
database_connections_active{pool="redis"} 12
```

**Histogram - Request Duration**
```
# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",path="/api/v1/projects",le="0.1"} 245
http_request_duration_seconds_bucket{method="GET",path="/api/v1/projects",le="0.25"} 312
http_request_duration_seconds_bucket{method="GET",path="/api/v1/projects",le="0.5"} 341
http_request_duration_seconds_bucket{method="GET",path="/api/v1/projects",le="+Inf"} 350
http_request_duration_seconds_sum{method="GET",path="/api/v1/projects"} 45.2
http_request_duration_seconds_count{method="GET",path="/api/v1/projects"} 350
```

### TaylorDash Metric Categories

#### Application Metrics
- `taylordash_events_total`: Total events processed by type
- `taylordash_active_projects`: Current number of active projects
- `taylordash_plugin_loads_total`: Plugin loading attempts and successes

#### Infrastructure Metrics
- `mqtt_broker_connections`: Active MQTT connections
- `database_query_duration_seconds`: Database query performance
- `cache_hits_total` / `cache_misses_total`: Cache effectiveness

#### Business Metrics
- `project_state_changes_total`: Project status transitions
- `user_sessions_active`: Current active user sessions
- `dashboard_views_total`: Dashboard page views by type

## OpenTelemetry Tracing

### Distributed Tracing

TaylorDash implements [OpenTelemetry](https://opentelemetry.io/) for distributed tracing across:
- **HTTP Requests**: API endpoint tracing
- **MQTT Events**: Message processing spans
- **Database Queries**: SQL execution tracing
- **Plugin Interactions**: Cross-plugin communication

#### Trace Structure

```
Root Span: HTTP POST /api/v1/projects
├── Database Span: INSERT project
├── MQTT Span: publish project.created
│   └── Event Processing Span: handle project.created
│       ├── Database Span: UPDATE project_stats
│       └── Cache Span: invalidate project_cache
└── Response Span: serialize project response
```

#### Custom Attributes

All spans include:
- `service.name`: TaylorDash component (api, mqtt, worker)
- `deployment.environment`: dev/staging/prod
- `user.id`: Authenticated user identifier
- `trace.id`: Unique trace identifier for correlation

### Span Examples

**HTTP Request Span**
```python
with tracer.start_as_current_span("api_create_project") as span:
    span.set_attribute("http.method", "POST")
    span.set_attribute("http.route", "/api/v1/projects")
    span.set_attribute("user.id", user_id)
    # ... request processing
    span.set_attribute("http.status_code", 201)
```

**MQTT Event Span**
```python
with tracer.start_as_current_span("mqtt_process_event") as span:
    span.set_attribute("messaging.system", "mqtt")
    span.set_attribute("messaging.destination", topic)
    span.set_attribute("messaging.operation", "process")
    # ... event processing
```

## Logging Strategy

### Structured Logging

All logs use JSON format for machine parsing:

```json
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "level": "INFO",
  "service": "taylordash-api",
  "trace_id": "abc123def456",
  "span_id": "789xyz321",
  "user_id": "user_123",
  "message": "Project created successfully",
  "project_id": "proj_789",
  "duration_ms": 245
}
```

### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General application flow
- **WARN**: Potentially harmful situations
- **ERROR**: Error events that allow application to continue
- **FATAL**: Serious errors that cause application termination

### Security Considerations

- **No Secrets**: Never log passwords, API keys, or sensitive data
- **PII Scrubbing**: Remove or hash personally identifiable information
- **Sanitization**: Escape user input in log messages
- **Retention**: Configure appropriate log retention policies

## Monitoring Stack

### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'taylordash'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
    metrics_path: /metrics
```

### Grafana Dashboards

Key dashboard panels:
- **Request Rate**: `rate(http_requests_total[5m])`
- **Error Rate**: `rate(http_requests_total{status=~"5.."}[5m])`
- **Response Time**: `histogram_quantile(0.95, http_request_duration_seconds_bucket)`
- **MQTT Throughput**: `rate(mqtt_ingest_total[1m])`

### Alerting Rules

```yaml
# alerts.yml
groups:
  - name: taylordash
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: High error rate detected
    
    - alert: DatabaseConnectionExhaustion
      expr: database_connections_active / database_connections_max > 0.9
      for: 1m
      labels:
        severity: critical
```

## Performance Monitoring

### Key Performance Indicators

1. **Latency**: 95th percentile response time < 500ms
2. **Throughput**: Handle 1000+ events/minute
3. **Availability**: 99.9% uptime for core services
4. **Error Rate**: < 1% error rate for API requests

### Health Checks

#### Endpoint: `/health/ready`
```json
{
  "status": "ready",
  "checks": {
    "database": "healthy",
    "mqtt": "healthy",
    "cache": "healthy"
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### Endpoint: `/health/live`
```json
{
  "status": "alive",
  "uptime": "7d 14h 23m",
  "version": "0.1.0",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## References

- [Prometheus Exposition Formats](https://prometheus.io/docs/instrumenting/exposition_formats/)
- [OpenMetrics Specification](https://openmetrics.io/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)

---

Comprehensive observability enables proactive monitoring, faster incident response, and data-driven optimization of TaylorDash performance.