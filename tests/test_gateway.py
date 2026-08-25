"""
Unit tests for OmniRoute AI Gateway in RUDRA framework.
"""
import pytest
from rudra.core.bus import EventBus
from rudra.core.tools import ToolRegistry
from rudra.core.permissions import ConsentCenter
from rudra.core.models import PermissionLevel, Status
from rudra.core.errors import PermissionDeniedError
from rudra.gateway.router import (
    OmniRouter,
    ProviderConfig,
    RoutingStrategy,
    OmniRouteRequest,
    GatewayError,
)
from rudra.gateway.tools import register_omniroute_tools


def test_provider_registration_and_listing():
    router = OmniRouter()
    provider1 = ProviderConfig(
        provider_id="provider_a",
        name="Provider Alpha",
        model_id="alpha-v1",
        is_free_tier=True,
        priority=1,
    )
    provider2 = ProviderConfig(
        provider_id="provider_b",
        name="Provider Beta",
        model_id="beta-v2",
        is_free_tier=False,
        priority=2,
    )
    router.register_provider(provider1)
    router.register_provider(provider2)

    providers = router.list_providers()
    assert len(providers) == 2
    assert providers[0]["provider_id"] == "provider_a"
    assert providers[1]["provider_id"] == "provider_b"

    assert router.remove_provider("provider_a") is True
    assert len(router.list_providers()) == 1


def test_omniroute_routing_success_and_fallback():
    event_bus = EventBus()
    events = []
    event_bus.subscribe("GATEWAY_ROUTED_SUCCESS", lambda msg: events.append(msg))

    router = OmniRouter(event_bus=event_bus)

    # Provider 1 fails
    def failing_handler(prompt, meta):
        raise RuntimeError("API Rate limit exceeded on Primary Provider")

    # Provider 2 succeeds
    def backup_handler(prompt, meta):
        return f"Response to '{prompt}' from Backup Provider"

    p1 = ProviderConfig(
        provider_id="p1_primary",
        name="Primary",
        model_id="claude-3-5-sonnet",
        priority=1,
        handler=failing_handler,
    )
    p2 = ProviderConfig(
        provider_id="p2_backup",
        name="Backup",
        model_id="gpt-4o",
        priority=2,
        handler=backup_handler,
    )

    router.register_provider(p1)
    router.register_provider(p2)

    req = OmniRouteRequest(prompt="Hello OmniRoute!", strategy=RoutingStrategy.PRIORITY)
    resp = router.route_chat(req)

    assert resp.content == "Response to 'Hello OmniRoute!' from Backup Provider"
    assert resp.provider_used == "p2_backup"
    assert resp.model_used == "gpt-4o"
    assert resp.status == Status.VERIFIED
    assert len(resp.fallback_history) == 1
    assert resp.fallback_history[0]["provider_id"] == "p1_primary"
    assert resp.fallback_history[0]["status"] == Status.FAILED.value
    assert len(events) == 1


def test_omniroute_all_providers_failed():
    router = OmniRouter()

    def failing_handler(prompt, meta):
        raise RuntimeError("Service unavailable")

    p1 = ProviderConfig(provider_id="p1", name="P1", model_id="m1", handler=failing_handler)
    router.register_provider(p1)

    req = OmniRouteRequest(prompt="Test failure")
    with pytest.raises(GatewayError) as exc_info:
        router.route_chat(req)

    assert "All candidate providers failed" in str(exc_info.value)
    assert len(exc_info.value.fallback_history) == 1


def test_omniroute_tool_registry_and_permission_enforcement():
    event_bus = EventBus()
    router = OmniRouter(event_bus=event_bus)

    def mock_handler(prompt, meta):
        return f"Echo: {prompt}"

    p = ProviderConfig(provider_id="p1", name="P1", model_id="m1", handler=mock_handler)
    router.register_provider(p)

    registry = ToolRegistry()
    register_omniroute_tools(registry, router)

    consent = ConsentCenter()
    session_id = "test_gateway_session"

    # Initially permission is not granted -> should raise PermissionDeniedError
    chat_tool = registry.get_tool("omniroute_route_chat")
    with pytest.raises(PermissionDeniedError):
        chat_tool.execute(session_id=session_id, consent_center=consent, prompt="Hi")

    # Request and authorize EXECUTE permission
    grant = consent.request_permission(session_id, PermissionLevel.EXECUTE, "Allow gateway chat")
    consent.authorize_permission(grant.grant_id)

    # Now tool execution succeeds
    res = chat_tool.execute(session_id=session_id, consent_center=consent, prompt="Hi")
    assert res["content"] == "Echo: Hi"
    assert res["provider_used"] == "p1"
    assert res["status"] == Status.VERIFIED.value

    # Test list_providers tool with READ_ONLY permission
    list_tool = registry.get_tool("omniroute_list_providers")
    with pytest.raises(PermissionDeniedError):
        list_tool.execute(session_id=session_id, consent_center=consent)

    grant_read = consent.request_permission(session_id, PermissionLevel.READ_ONLY, "Allow listing providers")
    consent.authorize_permission(grant_read.grant_id)
    prov_list = list_tool.execute(session_id=session_id, consent_center=consent)
    assert len(prov_list) == 1
    assert prov_list[0]["provider_id"] == "p1"
