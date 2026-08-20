"""
Unit tests for RUDRA Phase 1 Portable Core (UP, CN, CP, ST, AX).
"""
import pytest
import tempfile
from pathlib import Path
from rudra.core.portable import PortableRuntime
from rudra.core.connect import HostConnection, CapabilityRegistry
from rudra.core.permissions import ConsentCenter
from rudra.core.session import SessionManager
from rudra.core.orchestrator import AxiomOrchestrator
from rudra.core.models import PermissionLevel, PermissionStatus, Status


def test_portable_runtime_initialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = PortableRuntime(custom_root=Path(tmpdir))
        dirs = runtime.initialize_structure()
        assert Path(dirs["config"]).exists()
        assert Path(dirs["sessions"]).exists()

        capacity = runtime.get_storage_capacity()
        assert capacity["status"] == "OBSERVED"
        assert capacity["total_gb"] > 0

        validation = runtime.validate_environment()
        assert validation["is_writable"] is True


def test_host_connection_and_capability_registry():
    host_info = HostConnection.get_host_info()
    assert "os_name" in host_info
    assert "architecture" in host_info
    assert "hostname" in host_info

    capabilities = CapabilityRegistry()
    caps = capabilities.get_capabilities()
    assert caps["HOST_CONNECT"] == Status.VERIFIED.value
    assert caps["SYSTEM_DIAGNOSTICS"] == Status.NOT_IMPLEMENTED.value
    assert caps["MOBILE_CONTROL"] == Status.ACCESS_UNAVAILABLE.value
    assert capabilities.is_capability_available("HOST_CONNECT") is True
    assert capabilities.is_capability_available("SYSTEM_DIAGNOSTICS") is False


def test_permission_audit_and_revocation():
    consent = ConsentCenter()
    session_id = "sess-audit-1"

    grant = consent.request_permission(
        session_id=session_id,
        permission=PermissionLevel.SYSTEM_READ,
        justification="Inspect system status",
        capability_name="HOST_CONNECT",
    )
    assert grant.status == PermissionStatus.REQUESTED

    consent.authorize_permission(grant.grant_id)
    assert consent.check_permission(session_id, PermissionLevel.SYSTEM_READ) is True

    audit_logs = consent.get_audit_log(session_id)
    assert len(audit_logs) == 2  # REQUESTED and GRANTED

    consent.revoke_permission(session_id, PermissionLevel.SYSTEM_READ)
    assert consent.check_permission(session_id, PermissionLevel.SYSTEM_READ) is False


def test_session_persistence_and_recovery():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir)
        sm1 = SessionManager(storage_dir=storage_path)
        session = sm1.create_session(
            metadata={"device": "USB_TEST_DRIVE"},
            capabilities_snapshot={"HOST_CONNECT": "VERIFIED"},
        )
        session_id = session.session_id

        # Verify disk file exists
        assert (storage_path / f"{session_id}.json").exists()

        # Simulate fresh SessionManager instance recovering session from disk
        sm2 = SessionManager(storage_dir=storage_path)
        recovered = sm2.get_session(session_id)
        assert recovered.metadata["device"] == "USB_TEST_DRIVE"
        assert recovered.capabilities_snapshot["HOST_CONNECT"] == "VERIFIED"


def test_axiom_phase1_orchestrator():
    with tempfile.TemporaryDirectory() as tmpdir:
        from rudra.core.config import Config
        cfg = Config(usb_root_path=Path(tmpdir))
        ax = AxiomOrchestrator(config=cfg)

        assert ax.initialize() is True
        sess = ax.start_session(metadata={"client": "CLI_TEST"})
        assert sess.is_active is True
        assert sess.metadata["client"] == "CLI_TEST"
        assert "host" in sess.metadata

        assert ax.shutdown() is True
