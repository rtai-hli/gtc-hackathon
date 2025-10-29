# observability_utils.py

import os
import logging

def get_observability(service_name: str = "default-service", DEBUG_MODE=None):
    if DEBUG_MODE is None:
        DEBUG_MODE = os.getenv("DEBUG", "0") == "1"

    logging.basicConfig(
        level=logging.DEBUG if DEBUG_MODE else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logger = logging.getLogger(service_name)

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.trace import Status, StatusCode, SpanKind
        from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

        # Avoid overwriting globally if already set
        if not isinstance(trace.get_tracer_provider(), TracerProvider):
            provider = TracerProvider(resource=Resource.create({
                "service.name": service_name
            }))
            endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
            if endpoint:
                processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
                provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)

        tracer = trace.get_tracer(service_name)
        propagator = TraceContextTextMapPropagator()

        def traced(name: str):
            def decorator(func):
                async def wrapper(*args, **kwargs):
                    with tracer.start_as_current_span(name, kind=SpanKind.INTERNAL) as span:
                        span.set_attribute("function", func.__name__)
                        try:
                            return await func(*args, **kwargs)
                        except Exception as e:
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                            raise
                return wrapper
            return decorator
        
        return logger, tracer, propagator, traced

    except Exception as e:
        logger.warning(f"OpenTelemetry setup failed: {e}")

        def traced(name: str): return lambda f: f

        class StreamingWrapper:
            def __init__(self, inner_gen, span=None):
                self.inner = inner_gen
            async def __aiter__(self):
                async for chunk in self.inner:
                    yield chunk

        return logger, None, None, traced
