"""
OmniRoute AI Gateway module for RUDRA.
Provides multi-provider AI model routing, auto-fallback, and consent-controlled execution.
"""
from rudra.gateway.router import (
    OmniRouter,
    ProviderConfig,
    RoutingStrategy,
    OmniRouteRequest,
    OmniRouteResponse,
)

__all__ = [
    "OmniRouter",
    "ProviderConfig",
    "RoutingStrategy",
    "OmniRouteRequest",
    "OmniRouteResponse",
]
