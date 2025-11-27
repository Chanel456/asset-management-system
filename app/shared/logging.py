import logging, re, json
import os

from flask import g, request, has_request_context

SENSITIVE_KEYS = {'password', 'pass', 'pwd', 'secret', 'token', 'authorization', 'api_key'}

class RedactingFilter(logging.Filter):
    def filter(self, record):
        msg = str(record.getMessage())
        # Redact obvious credential patterns
        msg = re.sub(r'(Authorization:\s*Bearer\s+)[A-Za-z0-9\._-]+', r'\1[REDACTED]', msg, flags=re.IGNORECASE)
        msg = re.sub(r'(api_key=)[^&\s]+', r'\1[REDACTED]', msg, flags=re.IGNORECASE)

        record.msg = msg
        return True

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            'level': record.levelname,
            'event': record.msg,
            'logger': record.name,
            'timestamp': self.formatTime(record, '%Y-%m-%dT%H:%M:%S%z'),
        }

        if has_request_context():
            payload.update({
                'request_id': getattr(g, 'request_id', None),
                'path': request.path,
                'method': request.method,
                'remote_addr': request.headers.get('X-Forwarded-For', request.remote_addr),
            })

        excluded = {
            'name', 'msg', 'args', 'levelname', 'levelno',
            'pathname', 'filename', 'module', 'exc_info',
            'exc_text', 'stack_info', 'lineno', 'funcName',
            'created', 'msecs', 'relativeCreated', 'thread',
            'threadName', 'processName', 'process', 'taskName',
            'logger'
        }

        # Include any extra fields passed in
        for key, value in record.__dict__.items():
            if key not in payload and key not in excluded and not key.startswith("_"):
                payload[key] = value

        # Remove raw args which might contain sensitive content
        pretty = os.getenv("PRETTY_LOGS", "false").lower() == "true"
        return json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None)

def configure_logging(app):
    handler = logging.StreamHandler()
    handler.addFilter(RedactingFilter())
    handler.setFormatter(JsonFormatter())

    app.logger.handlers.clear()
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    # Align werkzeug/request logs
    logging.getLogger("werkzeug").handlers = app.logger.handlers
    # prevent noisy SQL values
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)