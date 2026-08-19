"""
RUDRA Structured Logging with Sensitive Data Redaction.
"""
import logging
import re
import json
from typing import Any, Dict


# Common patterns for sensitive data redaction
REDACTION_PATTERNS = [
    (re.compile(r'(?i)(password|passwd|secret|api_key|token|auth_token)\s*[:=]\s*["\']?([^"\'\s]+)["\']?'), r'\1="[REDACTED]"'),
    (re.compile(r'bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*', re.IGNORECASE), 'Bearer [REDACTED]'),
]


class SensitiveDataRedactor(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact(record.msg)
        if record.args:
            if isinstance(record.args, str):
                record.args = self.redact(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(self.redact(str(arg)) if isinstance(arg, str) else arg for arg in record.args)
            elif isinstance(record.args, dict):
                record.args = {k: (self.redact(str(v)) if isinstance(v, str) else v) for k, v in record.args.items()}
        return True

    @staticmethod
    def redact(text: str) -> str:
        redacted = text
        for pattern, replacement in REDACTION_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted


def setup_logger(name: str = "RUDRA", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addFilter(SensitiveDataRedactor())
    return logger
