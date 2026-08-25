"""
OmniRoute Core AI Gateway Router.
Handles provider registration, routing strategies (PRIORITY, ROUND_ROBIN, FAILOVER, AUTO),
resilient auto-fallback across multi-tier AI model providers, and audit logging via RUDRA EventBus.
"""
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from rudra.core.bus import EventBus, Message
from rudra.core.models import Status
from rudra.core.errors import RudraError


class RoutingStrategy(str, Enum):
    PRIORITY = "PRIORITY"
    ROUND_ROBIN = "ROUND_ROBIN"
    FAILOVER = "FAILOVER"
    AUTO = "AUTO"


@dataclass
class ProviderConfig:
    provider_id: str
    name: str
    model_id: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    is_free_tier: bool = True
    priority: int = 1  # Lower number = higher priority
    is_active: bool = True
    handler: Optional[Callable[[str, Dict[str, Any]], str]] = None


@dataclass
class OmniRouteRequest:
    prompt: str
    model_alias: str = "auto"
    strategy: RoutingStrategy = RoutingStrategy.AUTO
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OmniRouteResponse:
    content: str
    provider_used: str
    model_used: str
    strategy_used: RoutingStrategy
    status: Status
    latency_ms: float
    fallback_history: List[Dict[str, Any]] = field(default_factory=list)


class GatewayError(RudraError):
    """Raised when OmniRoute Gateway fails to route or execute a request across all available providers."""
    def __init__(self, message: str, fallback_history: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, code="GATEWAY_ERROR")
        self.fallback_history = fallback_history or []


class OmniRouter:
    """
    Self-owned OmniRoute AI Gateway for owner-controlled agent execution.
    Routes requests through registered AI providers with fallback resilience.
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        self.providers: Dict[str, ProviderConfig] = {}
        self.event_bus = event_bus or EventBus()
        self._round_robin_idx = 0

    def register_provider(self, provider: ProviderConfig) -> None:
        """Register or update an AI model provider configuration."""
        self.providers[provider.provider_id] = provider
        self.event_bus.publish(
            Message(
                event_type="PROVIDER_REGISTERED",
                source_subsystem="OMNIROUTE",
                payload={"provider_id": provider.provider_id, "name": provider.name, "model_id": provider.model_id},
            )
        )

    def remove_provider(self, provider_id: str) -> bool:
        """Remove a provider from the gateway."""
        if provider_id in self.providers:
            del self.providers[provider_id]
            self.event_bus.publish(
                Message(
                    event_type="PROVIDER_REMOVED",
                    source_subsystem="OMNIROUTE",
                    payload={"provider_id": provider_id},
                )
            )
            return True
        return False

    def list_providers(self) -> List[Dict[str, Any]]:
        """List registered providers and their status."""
        return [
            {
                "provider_id": p.provider_id,
                "name": p.name,
                "model_id": p.model_id,
                "is_free_tier": p.is_free_tier,
                "priority": p.priority,
                "is_active": p.is_active,
            }
            for p in self.providers.values()
        ]

    def _select_candidate_order(self, strategy: RoutingStrategy) -> List[ProviderConfig]:
        """Determine candidate provider evaluation order based on routing strategy."""
        active_providers = [p for p in self.providers.values() if p.is_active]
        if not active_providers:
            return []

        if strategy in (RoutingStrategy.PRIORITY, RoutingStrategy.FAILOVER, RoutingStrategy.AUTO):
            # Sort by priority ascending, then free-tier first
            return sorted(active_providers, key=lambda p: (p.priority, not p.is_free_tier))
        elif strategy == RoutingStrategy.ROUND_ROBIN:
            if not active_providers:
                return []
            idx = self._round_robin_idx % len(active_providers)
            self._round_robin_idx += 1
            # Put selected index first, followed by remaining
            return active_providers[idx:] + active_providers[:idx]

        return sorted(active_providers, key=lambda p: p.priority)

    def route_chat(self, request: OmniRouteRequest) -> OmniRouteResponse:
        """
        Route a prompt across candidate providers with auto-fallback resilience.
        Strictly follows NO FAKE CREATION rule - if real handlers fail, raises GatewayError.
        """
        candidates = self._select_candidate_order(request.strategy)
        if not candidates:
            raise GatewayError("No active providers available in OmniRoute Gateway.")

        fallback_history = []
        start_time = time.time()

        for candidate in candidates:
            attempt_info = {"provider_id": candidate.provider_id, "model_id": candidate.model_id}
            try:
                if candidate.handler is not None:
                    # Execute owner-defined real provider handler
                    result_text = candidate.handler(request.prompt, request.metadata)
                    latency = (time.time() - start_time) * 1000.0

                    response = OmniRouteResponse(
                        content=result_text,
                        provider_used=candidate.provider_id,
                        model_used=candidate.model_id,
                        strategy_used=request.strategy,
                        status=Status.VERIFIED,
                        latency_ms=latency,
                        fallback_history=fallback_history,
                    )

                    self.event_bus.publish(
                        Message(
                            event_type="GATEWAY_ROUTED_SUCCESS",
                            source_subsystem="OMNIROUTE",
                            payload={
                                "provider_id": candidate.provider_id,
                                "model_id": candidate.model_id,
                                "latency_ms": latency,
                                "fallbacks": len(fallback_history),
                            },
                        )
                    )
                    return response
                else:
                    # Unimplemented provider handler
                    attempt_info["status"] = Status.NOT_IMPLEMENTED.value
                    attempt_info["reason"] = "Provider handler is not implemented."
                    fallback_history.append(attempt_info)
            except Exception as e:
                attempt_info["status"] = Status.FAILED.value
                attempt_info["reason"] = str(e)
                fallback_history.append(attempt_info)

        # If all candidates fail or lack handlers
        raise GatewayError(
            f"All candidate providers failed or are unimplemented for request '{request.prompt[:30]}...'",
            fallback_history=fallback_history,
        )
