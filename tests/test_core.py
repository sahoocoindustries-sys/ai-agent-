"""
Unit tests for RUDRA Core Foundation (Phase 0).
"""
import pytest
import logging
from rudra.core.config import Config
from rudra.core.logging import setup_logger, SensitiveDataRedactor
from rudra.core.errors import PermissionDeniedError, SessionError, ToolError
from rudra.core.models import Status, PermissionLevel, Severity
from rudra.core.bus import EventBus, Message
from rudra.core.permissions import ConsentCenter
from rudra.core.session import SessionManager
from rudra.core.tools import ToolRegistry, ToolSchema
from rudra.core.evidence import EvidenceCollector
from rudra.core.verification import VeritasEngine
from rudra.core.orchestrator import AxiomOrchestrator


def test_config_loading():
    cfg = Config.load({"debug": False})
    assert cfg.app_name == "RUDRA"
    assert cfg.debug is False


def test_sensitive_data_logging(caplog):
    logger = setup_logger("TestLogger", level="INFO")
    with caplog.at_level(logging.INFO):
        logger.info("Connecting with password=supersecret123 and secret='my_token'")
    assert "supersecret123" not in caplog.text
    assert "[REDACTED]" in caplog.text


def test_event_bus():
    bus = EventBus()
    received = []

    def handler(msg: Message):
        received.append(msg)

    bus.subscribe("TEST_EVENT", handler)
    msg = Message(event_type="TEST_EVENT", source_subsystem="TEST", payload={"key": "val"})
    bus.publish(msg)

    assert len(received) == 1
    assert received[0].payload["key"] == "val"
    assert len(bus.get_history()) == 1


def test_permission_enforcement():
    consent = ConsentCenter()
    session_id = "sess-123"

    grant = consent.request_permission(session_id, PermissionLevel.SYSTEM_READ, "Check services")
    assert consent.check_permission(session_id, PermissionLevel.SYSTEM_READ) is False

    with pytest.raises(PermissionDeniedError):
        consent.enforce_permission(session_id, PermissionLevel.SYSTEM_READ)

    consent.authorize_permission(grant.grant_id)
    assert consent.check_permission(session_id, PermissionLevel.SYSTEM_READ) is True
    consent.enforce_permission(session_id, PermissionLevel.SYSTEM_READ)  # Should not raise exception


def test_session_lifecycle():
    sm = SessionManager()
    session = sm.create_session(metadata={"device": "USB_DEV_1"})
    assert session.is_active is True

    fetched = sm.get_session(session.session_id)
    assert fetched.metadata["device"] == "USB_DEV_1"

    sm.terminate_session(session.session_id)
    with pytest.raises(SessionError):
        sm.get_session(session.session_id)


def test_tool_registry_and_permission_execution():
    registry = ToolRegistry()
    consent = ConsentCenter()
    session_id = "sess-tool-1"

    schema = ToolSchema(
        tool_id="test_tool",
        name="Test Tool",
        description="A tool for testing",
        version="1.0",
        required_permission=PermissionLevel.FILE_READ,
    )

    def dummy_handler(filepath: str):
        return f"Reading {filepath}"

    registry.register_tool(schema, dummy_handler)
    tool = registry.get_tool("test_tool")

    # Execution without permission should fail
    with pytest.raises(PermissionDeniedError):
        tool.execute(session_id, consent, filepath="/tmp/test.txt")

    # Grant permission and execute
    grant = consent.request_permission(session_id, PermissionLevel.FILE_READ, "Read test file")
    consent.authorize_permission(grant.grant_id)

    res = tool.execute(session_id, consent, filepath="/tmp/test.txt")
    assert res == "Reading /tmp/test.txt"


def test_evidence_and_veritas_verification():
    collector = EvidenceCollector()
    veritas = VeritasEngine(collector)

    ev = collector.collect(
        source_subsystem="DX",
        observed_fact="Service 'sshd' is running on port 22",
        raw_data={"port": 22, "service": "sshd"},
        severity=Severity.INFO,
    )

    result = veritas.verify_action(
        target_id="check_sshd",
        evidence_ids=[ev.evidence_id],
        expected_outcome="sshd",
    )

    assert result.status == Status.VERIFIED
    assert "verified by real evidence" in result.details.lower()


def test_axiom_orchestrator_initialization_and_unimplemented_status():
    orchestrator = AxiomOrchestrator()
    assert orchestrator.initialize() is True

    sess = orchestrator.start_session()
    assert sess.is_active is True

    status_unbuilt = orchestrator.get_unimplemented_status("SAGE")
    assert status_unbuilt["status"] == Status.NOT_IMPLEMENTED.value

    assert orchestrator.shutdown() is True
