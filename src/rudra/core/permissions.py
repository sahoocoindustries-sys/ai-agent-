"""
RUDRA Consent and Permission Management Subsystem (CP - CONSENT).
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Set, List
from dataclasses import dataclass, field
from rudra.core.models import PermissionLevel, PermissionStatus
from rudra.core.errors import PermissionDeniedError


@dataclass
class PermissionGrant:
    grant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    permission: PermissionLevel = PermissionLevel.READ_ONLY
    capability_name: str = ""
    status: PermissionStatus = PermissionStatus.REQUESTED
    granted_at: Optional[str] = None
    expires_at: Optional[str] = None
    revoked_at: Optional[str] = None
    justification: str = ""
    session_id: str = ""


@dataclass
class PermissionAuditEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str = ""
    permission: str = ""
    action: str = ""
    details: str = ""


class ConsentCenter:
    def __init__(self):
        self._grants: Dict[str, PermissionGrant] = {}
        self._active_permissions: Dict[str, Set[PermissionLevel]] = {}
        self._audit_log: List[PermissionAuditEvent] = []

    def request_permission(
        self,
        session_id: str,
        permission: PermissionLevel,
        justification: str,
        capability_name: str = "",
        ttl_seconds: Optional[int] = 3600,
    ) -> PermissionGrant:
        grant = PermissionGrant(
            permission=permission,
            capability_name=capability_name,
            status=PermissionStatus.REQUESTED,
            justification=justification,
            session_id=session_id,
        )
        self._grants[grant.grant_id] = grant
        self._log_audit(session_id, permission.value, "REQUESTED", f"Justification: {justification}")
        return grant

    def authorize_permission(self, grant_id: str, ttl_seconds: Optional[int] = 3600) -> PermissionGrant:
        if grant_id not in self._grants:
            raise KeyError(f"Grant ID {grant_id} not found.")
        grant = self._grants[grant_id]
        grant.status = PermissionStatus.GRANTED
        now = datetime.now(timezone.utc)
        grant.granted_at = now.isoformat()
        if ttl_seconds:
            grant.expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()

        if grant.session_id not in self._active_permissions:
            self._active_permissions[grant.session_id] = set()
        self._active_permissions[grant.session_id].add(grant.permission)
        self._log_audit(grant.session_id, grant.permission.value, "GRANTED", f"Grant ID: {grant_id}")
        return grant

    def deny_permission(self, grant_id: str) -> PermissionGrant:
        if grant_id not in self._grants:
            raise KeyError(f"Grant ID {grant_id} not found.")
        grant = self._grants[grant_id]
        grant.status = PermissionStatus.DENIED
        self._log_audit(grant.session_id, grant.permission.value, "DENIED", f"Grant ID: {grant_id}")
        return grant

    def check_permission(self, session_id: str, permission: PermissionLevel) -> bool:
        session_perms = self._active_permissions.get(session_id, set())
        return permission in session_perms

    def enforce_permission(self, session_id: str, permission: PermissionLevel, justification: str = "") -> None:
        if not self.check_permission(session_id, permission):
            self._log_audit(session_id, permission.value, "ENFORCE_FAILED", f"Reason: {justification}")
            raise PermissionDeniedError(permission.value, justification)

    def revoke_permission(self, session_id: str, permission: PermissionLevel) -> None:
        if session_id in self._active_permissions:
            self._active_permissions[session_id].discard(permission)
            self._log_audit(session_id, permission.value, "REVOKED", "User/System initiated revocation")

    def get_audit_log(self, session_id: Optional[str] = None) -> List[PermissionAuditEvent]:
        if session_id:
            return [ev for ev in self._audit_log if ev.session_id == session_id]
        return list(self._audit_log)

    def _log_audit(self, session_id: str, permission: str, action: str, details: str):
        self._audit_log.append(
            PermissionAuditEvent(
                session_id=session_id,
                permission=permission,
                action=action,
                details=details,
            )
        )
