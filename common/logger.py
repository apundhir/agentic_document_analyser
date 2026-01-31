import structlog
import logging
import sys
from common.config import settings

def configure_logger(service_name: str):
    """
    Configures structured logging for a service.
    """
    
    # Set standard logging level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL),
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.ENV == "dev" else structlog.processors.JSONRenderer()
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    log = structlog.get_logger(service_name=service_name)
    return log
