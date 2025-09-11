"""
OpenTelemetry instrumentation configuration
"""
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
import os

logger = logging.getLogger(__name__)

def init_telemetry():
    """Initialize OpenTelemetry instrumentation"""
    
    # Create resource
    resource = Resource.create({
        "service.name": "taylordash-backend",
        "service.version": "1.0.0",
        "deployment.environment": os.getenv("ENVIRONMENT", "development")
    })
    
    # Set up tracing
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()
    
    # Configure span export (OTLP or console)
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    else:
        # Fallback to console for development
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        span_exporter = ConsoleSpanExporter()
    
    span_processor = BatchSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Set up metrics
    metrics.set_meter_provider(MeterProvider(resource=resource))
    
    # Auto-instrument FastAPI
    FastAPIInstrumentor().instrument()
    
    # Auto-instrument AsyncPG
    AsyncPGInstrumentor().instrument()
    
    # Auto-instrument HTTPX
    HTTPXClientInstrumentor().instrument()
    
    logger.info("OpenTelemetry instrumentation initialized")

def get_tracer(name: str):
    """Get tracer instance"""
    return trace.get_tracer(name)

def get_meter(name: str):
    """Get meter instance"""
    return metrics.get_meter(name)