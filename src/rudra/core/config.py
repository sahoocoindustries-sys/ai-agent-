"""
RUDRA Configuration Management.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    app_name: str = "RUDRA"
    version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    usb_mode: bool = False
    usb_root_path: Path = field(default_factory=lambda: Path(os.getenv("RUDRA_ROOT", ".")))
    log_level: str = "INFO"
    session_timeout_seconds: int = 3600
    redact_sensitive_logs: bool = True

    @classmethod
    def load(cls, overrides: Optional[Dict[str, Any]] = None) -> "Config":
        overrides = overrides or {}
        env_debug = os.getenv("RUDRA_DEBUG")
        if env_debug is not None:
            overrides["debug"] = env_debug.lower() in ("true", "1", "yes")

        env_log_level = os.getenv("RUDRA_LOG_LEVEL")
        if env_log_level:
            overrides["log_level"] = env_log_level

        return cls(**overrides)
