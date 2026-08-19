"""
RUDRA Consent and Permission Management Subsystem (CP - CONSENT).
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Set
from dataclasses import dataclass, field
from rudra.core.models import PermissionLevel, PermissionStatus
from rudra.core.errors import PermissionDeniedError


@dataclass
class PermissionGrant:
    grant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    permission: PermissionLevel = PermissionLevel.READ_ONLY
    status: PermissionStatus = PermissionStatus.REQUESTED
    granted_at: Optional[str] = None
    revoked_at: Optional[str] = None
    justification: str = ""
    session_id: str = ""


class ConsentCenter:
    def __init__(self):
        self._grants: Dict[str, PermissionGrant] = {}
        self._active_permissions: Dict[str, Set[PermissionLevel]] = {}

    def request_permission(
        self, session_id: str, permission: PermissionLevel, justification: str
    ) -> PermissionGrant:
        grant = PermissionGrant(
            permission=permission,
            status=PermissionStatus.REQUESTED,
            justification=justification,
            session_id=session_id,
        )
        self._grants[grant.grant_id] = grant
        return grant

    def authorize_permission(self, grant_id: str) -> PermissionGrant:
        if grant_id not in self._grants:
            raise KeyError(f"Grant ID {grant_id} not found.")
        grant = self._grants[grant_id]
        grant.status = PermissionStatus.GRANTED
        grant.granted_at = datetime.now(timezone.utc).isoformat()

        if grant.session_id not in self._active_permissions:
            self._active_permissions[grant.session_id] = set()
        self._active_permissions[grant.session_id].add(grant.permission)
        return grant

    def deny_permission(self, grant_id: str) -> PermissionGrant:
        if grant_id not in self._grants:
            raise KeyError(f"Grant ID {grant_id} not found.")
        grant = self._grants[grant_id]
        grant.status = PermissionStatus.DENIED
        return grant

    def check_permission(self, session_id: str, permission: PermissionLevel) -> bool:
        session_perms = self._active_permissions.get(session_id, set())
        return permission in session_perms

    def enforce_permission(self, session_id: str, permission: PermissionLevel, justification: str = "") -> None:
        if not self.check_permission(session_id, permission):
            raise PermissionDeniedError(permission.value, justification)

    def revoke_permission(self, session_id: str, permission: PermissionLevel) -> None:
        if session_id in self._active_permissions:
            self._active_permissions[session_id].discard(permission)
