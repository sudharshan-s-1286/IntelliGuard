import logging
import json
from datetime import datetime, timezone
import traceback

class JSONFormatter(logging.Formatter):
    """
    Custom logging formatter to output logs in JSON format for structured logging.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = "".join(traceback.format_exception(*record.exc_info))
            
        # Add execution_time_ms if present
        if hasattr(record, "execution_time_ms"):
            log_entry["execution_time_ms"] = record.execution_time_ms
            
        # Add request_id if present
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        # Extensibility for extra fields passed via extra={'field': 'value'}
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", 
                           "filename", "funcName", "levelname", "levelno", "lineno", 
                           "module", "msecs", "message", "msg", "name", "pathname", 
                           "process", "processName", "relativeCreated", "stack_info", 
                           "thread", "threadName"]:
                if key not in log_entry:
                    try:
                        # Attempt to serialize to JSON. If it fails, fallback to string.
                        json.dumps(value)
                        log_entry[key] = value
                    except TypeError:
                        log_entry[key] = str(value)

        return json.dumps(log_entry)

def setup_logging():
    """Configures the root logger to use JSONFormatter."""
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Tone down noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
