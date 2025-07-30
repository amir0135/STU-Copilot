import os
import logging
from typing import Dict, Any, Optional
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor


class AppInsightsService:
    """Service for Azure Application Insights integration with OpenTelemetry."""

    def __init__(self):
        self.connection_string = os.getenv("APP_INSIGHTS_CONNECTION_STRING")
        self.tracer = None
        self.meter = None
        self.is_configured = False

        if self.connection_string:
            self._configure_telemetry()
        else:
            logging.warning(
                "Application Insights connection string not found. Telemetry will be disabled.")

    def _configure_telemetry(self):
        """Configure Azure Monitor with OpenTelemetry."""
        try:
            # Configure Azure Monitor
            configure_azure_monitor(
                connection_string=self.connection_string,
                disable_offline_storage=False,
            )

            # Get tracer and meter instances
            self.tracer = trace.get_tracer(__name__)
            self.meter = metrics.get_meter(__name__)

            # Configure automatic instrumentation
            LoggingInstrumentor().instrument(set_logging_format=True)
            RequestsInstrumentor().instrument()
            URLLib3Instrumentor().instrument()

            self.is_configured = True
            logging.info(
                "Application Insights telemetry configured successfully")

        except Exception as e:
            logging.error(f"Failed to configure Application Insights: {e}")
            self.is_configured = False

    def start_operation(self, operation_name: str, **kwargs) -> Optional[trace.Span]:
        """Start a new operation/span for tracking."""
        if not self.is_configured or not self.tracer:
            return None

        span = self.tracer.start_span(operation_name)

        # Add custom attributes
        for key, value in kwargs.items():
            span.set_attribute(key, str(value))

        return span

    def track_event(self, event_name: str, properties: Dict[str, Any] = None, measurements: Dict[str, float] = None):
        """Track a custom event."""
        if not self.is_configured or not self.tracer:
            return

        with self.tracer.start_as_current_span(f"event_{event_name}") as span:
            span.set_attribute("event.name", event_name)

            if properties:
                for key, value in properties.items():
                    span.set_attribute(f"event.property.{key}", str(value))

            if measurements:
                for key, value in measurements.items():
                    span.set_attribute(f"event.measurement.{key}", value)

    def track_exception(self, exception: Exception, properties: Dict[str, Any] = None):
        """Track an exception."""
        if not self.is_configured:
            return

        span = trace.get_current_span()
        if span:
            span.record_exception(exception)
            span.set_status(Status(StatusCode.ERROR, str(exception)))

            if properties:
                for key, value in properties.items():
                    span.set_attribute(f"exception.property.{key}", str(value))

    def track_dependency(self, dependency_name: str, command: str, duration: float, success: bool, dependency_type: str = "HTTP"):
        """Track a dependency call."""
        if not self.is_configured or not self.tracer:
            return

        with self.tracer.start_as_current_span(f"dependency_{dependency_name}") as span:
            span.set_attribute("dependency.name", dependency_name)
            span.set_attribute("dependency.command", command)
            span.set_attribute("dependency.duration", duration)
            span.set_attribute("dependency.success", success)
            span.set_attribute("dependency.type", dependency_type)

            if not success:
                span.set_status(
                    Status(StatusCode.ERROR, "Dependency call failed"))

    def track_chat_message(self, user_id: str, agent_name: str, message_length: int, response_time: float):
        """Track chat message interactions."""
        self.track_event("chat_message", {
            "user_id": user_id,
            "agent_name": agent_name,
            "message_length": str(message_length)
        }, {
            "response_time": response_time
        })

    def track_agent_selection(self, selected_agent: str, user_id: str):
        """Track agent selection events."""
        self.track_event("agent_selection", {
            "selected_agent": selected_agent,
            "user_id": user_id
        })

    def track_user_session(self, user_id: str, session_start: bool = True):
        """Track user session events."""
        event_name = "session_start" if session_start else "session_end"
        self.track_event(event_name, {
            "user_id": user_id
        })


# Global instance
app_insights_service = AppInsightsService()
