"""
RUDRA Master Orchestrator and Lifecycle Controller (AX - AXIOM).
"""
from typing import Dict, Any, Optional
from rudra.core.config import Config
from rudra.core.logging import setup_logger
from rudra.core.bus import EventBus, Message
from rudra.core.permissions import ConsentCenter
from rudra.core.session import SessionManager, Session
from rudra.core.tools import ToolRegistry
from rudra.core.evidence import EvidenceCollector
from rudra.core.verification import VeritasEngine
from rudra.core.platform import PlatformAbstraction
from rudra.core.models import Status


class AxiomOrchestrator:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.load()
        self.logger = setup_logger("AXIOM", level=self.config.log_level)
        self.event_bus = EventBus()
        self.consent_center = ConsentCenter()
        self.session_manager = SessionManager()
        self.tool_registry = ToolRegistry()
        self.evidence_collector = EvidenceCollector()
        self.veritas_engine = VeritasEngine(self.evidence_collector)
        self.platform_info = PlatformAbstraction.get_platform_info()
        self._initialized = False

    def initialize(self) -> bool:
        self.logger.info("Initializing RUDRA AXIOM Master Orchestrator...")
        self.event_bus.publish(
            Message(
                event_type="SYSTEM_INITIALIZING",
                source_subsystem="AXIOM",
                payload={"platform": self.platform_info},
            )
        )
        self._initialized = True
        self.event_bus.publish(
            Message(
                event_type="SYSTEM_READY",
                source_subsystem="AXIOM",
                payload={"status": "INITIALIZED"},
            )
        )
        return True

    def start_session(self, metadata: Optional[Dict[str, str]] = None) -> Session:
        if not self._initialized:
            self.initialize()
        session = self.session_manager.create_session(metadata=metadata)
        self.event_bus.publish(
            Message(
                event_type="SESSION_STARTED",
                source_subsystem="AXIOM",
                payload={"session_id": session.session_id},
            )
        )
        return session

    def shutdown(self) -> bool:
        self.logger.info("Shutting down RUDRA AXIOM Orchestrator...")
        self.event_bus.publish(
            Message(
                event_type="SYSTEM_SHUTDOWN",
                source_subsystem="AXIOM",
                payload={"status": "SHUTDOWN"},
            )
        )
        self._initialized = False
        return True

    def get_unimplemented_status(self, subsystem_name: str) -> Dict[str, Any]:
        """Utility method returning NOT_IMPLEMENTED status for unbuilt subsystems."""
        return {
            "subsystem": subsystem_name,
            "status": Status.NOT_IMPLEMENTED.value,
            "message": f"Subsystem {subsystem_name} is deferred to a future phase.",
        }
