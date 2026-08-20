"""
RUDRA Session Management Subsystem (ST - SESSION).
"""
import uuid
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from rudra.core.errors import SessionError


@dataclass
class Session:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    terminated_at: Optional[str] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    capabilities_snapshot: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SessionManager:
    def __init__(self, storage_dir: Optional[Path] = None):
        self._sessions: Dict[str, Session] = {}
        self.storage_dir = storage_dir

    def create_session(
        self, metadata: Optional[Dict[str, Any]] = None, capabilities_snapshot: Optional[Dict[str, str]] = None
    ) -> Session:
        session = Session(
            metadata=metadata or {},
            capabilities_snapshot=capabilities_snapshot or {},
        )
        self._sessions[session.session_id] = session
        self._persist_session(session)
        return session

    def get_session(self, session_id: str) -> Session:
        if session_id not in self._sessions:
            loaded = self._load_session(session_id)
            if loaded:
                self._sessions[session_id] = loaded
            else:
                raise SessionError(f"Session '{session_id}' not found.")
        session = self._sessions[session_id]
        if not session.is_active:
            raise SessionError(f"Session '{session_id}' is inactive/terminated.")
        return session

    def terminate_session(self, session_id: str) -> Session:
        session = self.get_session(session_id)
        session.is_active = False
        session.terminated_at = datetime.now(timezone.utc).isoformat()
        self._persist_session(session)
        return session

    def _persist_session(self, session: Session) -> None:
        if not self.storage_dir:
            return
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            filepath = self.storage_dir / f"{session.session_id}.json"
            with open(filepath, "w") as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception:
            pass

    def _load_session(self, session_id: str) -> Optional[Session]:
        if not self.storage_dir:
            return None
        filepath = self.storage_dir / f"{session_id}.json"
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return Session(**data)
        except Exception:
            return None
