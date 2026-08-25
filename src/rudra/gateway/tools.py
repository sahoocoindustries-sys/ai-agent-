"""
OmniRoute Tool Integration with RUDRA Controlled AI Execution Model.
Registers OmniRoute gateway functions into RUDRA's ToolRegistry with permission enforcement.
"""
from typing import Any, Dict, List
from rudra.core.models import PermissionLevel
from rudra.core.tools import ToolRegistry, ToolSchema
from rudra.core.permissions import ConsentCenter
from rudra.gateway.router import OmniRouter, OmniRouteRequest, RoutingStrategy, ProviderConfig


def register_omniroute_tools(registry: ToolRegistry, router: OmniRouter) -> None:
    """Register OmniRoute gateway functions into RUDRA Tool Registry."""

    def omniroute_route_chat_handler(prompt: str, strategy: str = "AUTO", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        req_strategy = RoutingStrategy(strategy.upper()) if hasattr(RoutingStrategy, strategy.upper()) else RoutingStrategy.AUTO
        req = OmniRouteRequest(prompt=prompt, strategy=req_strategy, metadata=metadata or {})
        res = router.route_chat(req)
        return {
            "content": res.content,
            "provider_used": res.provider_used,
            "model_used": res.model_used,
            "strategy_used": res.strategy_used.value,
            "status": res.status.value,
            "latency_ms": res.latency_ms,
            "fallback_history": res.fallback_history,
        }

    def omniroute_list_providers_handler() -> List[Dict[str, Any]]:
        return router.list_providers()

    chat_schema = ToolSchema(
        tool_id="omniroute_route_chat",
        name="OmniRoute AI Gateway Chat",
        description="Routes chat completion request through registered multi-tier AI model providers with auto-fallback.",
        version="1.0.0",
        required_permission=PermissionLevel.EXECUTE,
    )

    providers_schema = ToolSchema(
        tool_id="omniroute_list_providers",
        name="OmniRoute List Providers",
        description="Lists all registered AI model providers and their current status in OmniRoute Gateway.",
        version="1.0.0",
        required_permission=PermissionLevel.READ_ONLY,
    )

    registry.register_tool(chat_schema, omniroute_route_chat_handler)
    registry.register_tool(providers_schema, omniroute_list_providers_handler)
