"""
RUDRA Session Management Subsystem (ST - SESSION).
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional
from dataclasses import dataclass, field
from rudra.core.errors import SessionError


@dataclass
class Session:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    terminated_at: Optional[str] = None
    is_active: bool = True
    metadata: Dict[str, str] = field(default_factory=dict)


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create_session(self, metadata: Optional[Dict[str, str]] = None) -> Session:
        session = Session(metadata=metadata or {})
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Session:
        if session_id not in self._sessions:
            raise SessionError(f"Session '{session_id}' not found.")
        session = self._sessions[session_id]
        if not session.is_active:
            raise SessionError(f"Session '{session_id}' is inactive/terminated.")
        return session

    def terminate_session(self, session_id: str) -> Session:
        session = self.get_session(session_id)
        session.is_active = False
        session.terminated_at = datetime.now(timezone.utc).isoformat()
        return session
