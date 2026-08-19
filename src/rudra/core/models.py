"""
RUDRA Core Data Models and Enums.
"""
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


class Status(str, Enum):
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    ACCESS_UNAVAILABLE = "ACCESS_UNAVAILABLE"
    UNCONFIRMED = "UNCONFIRMED"
    FAILED = "FAILED"
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    SUCCESS = "SUCCESS"
    RUNNING = "RUNNING"
    PENDING = "PENDING"


class PermissionLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    SYSTEM_READ = "SYSTEM_READ"
    FILE_READ = "FILE_READ"
    FILE_WRITE = "FILE_WRITE"
    EXECUTE = "EXECUTE"
    SYSTEM_MODIFY = "SYSTEM_MODIFY"
    ELEVATED = "ELEVATED"


class PermissionStatus(str, Enum):
    REQUESTED = "REQUESTED"
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Evidence:
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_subsystem: str = ""
    observed_fact: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    severity: Severity = Severity.INFO
    is_inferred: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "timestamp": self.timestamp,
            "source_subsystem": self.source_subsystem,
            "observed_fact": self.observed_fact,
            "raw_data": self.raw_data,
            "confidence": self.confidence,
            "severity": self.severity.value,
            "is_inferred": self.is_inferred,
        }


@dataclass
class VerificationResult:
    verification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_id: str = ""
    status: Status = Status.UNVERIFIED
    details: str = ""
    evidence_list: List[Evidence] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verification_id": self.verification_id,
            "target_id": self.target_id,
            "status": self.status.value,
            "details": self.details,
            "evidence_count": len(self.evidence_list),
            "timestamp": self.timestamp,
        }
