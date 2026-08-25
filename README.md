# RUDRA & OmniRoute AI Gateway

**RUDRA** is a portable, consent-based, offline-first AI-assisted diagnostic and defensive-security system designed for ~8 GB USB drives with a Windows-first architecture.

**OmniRoute** is built-in as a self-owned AI Gateway engine within RUDRA (`src/rudra/gateway`), allowing owner-controlled AI agent execution, multi-provider model routing, auto-fallback resilience, and permission-governed tool execution.

---

## Key Features

- **Self-Owned AI Gateway Engine (`OmniRouter`)**: Full ownership to connect, run, and route AI models across free tiers and custom provider endpoints without third-party lock-in.
- **Routing Strategies**:
  - `PRIORITY`: Route to highest priority / free-tier providers first.
  - `ROUND_ROBIN`: Balance load evenly across active provider connections.
  - `FAILOVER`: Dedicated primary-to-backup fallback cascade.
  - `AUTO`: Intelligent dynamic candidate selection.
- **Resilient Auto-Fallback**: Automatically cascades to remaining healthy providers if a primary provider fails or hits rate limits.
- **Controlled Execution & Consent (`CP - CONSENT`)**: All gateway tools (`omniroute_route_chat`, `omniroute_list_providers`) route through `ToolRegistry` and require user-permission grants before executing real operations.
- **Zero Fake Creation**: Adheres strictly to RUDRA's `NO FAKE CREATION` engineering rules. All statuses are real (`VERIFIED`, `FAILED`, `NOT_IMPLEMENTED`).

---

## Quick Start & Usage

### 1. Running Unit Tests

Run the full pytest suite including core, portable runtime, and OmniRoute Gateway tests:

```bash
PYTHONPATH=src pytest -v
```

### 2. Basic Python Usage

```python
from rudra.gateway import OmniRouter, ProviderConfig, RoutingStrategy, OmniRouteRequest

# Initialize OmniRouter
router = OmniRouter()

# Register providers
def my_openai_handler(prompt, meta):
    return f"Response from OpenAI model: {prompt}"

router.register_provider(
    ProviderConfig(
        provider_id="openai_primary",
        name="OpenAI GPT-4o",
        model_id="gpt-4o",
        priority=1,
        is_free_tier=False,
        handler=my_openai_handler,
    )
)

# Route chat request
request = OmniRouteRequest(
    prompt="Explain quantum computing simply",
    strategy=RoutingStrategy.AUTO,
)

response = router.route_chat(request)
print(f"Used Provider: {response.provider_used}")
print(f"Content: {response.content}")
```

### 3. Tool Registry Integration

```python
from rudra.core.tools import ToolRegistry
from rudra.core.permissions import ConsentCenter
from rudra.core.models import PermissionLevel
from rudra.gateway import OmniRouter
from rudra.gateway.tools import register_omniroute_tools

router = OmniRouter()
registry = ToolRegistry()
consent = ConsentCenter()

register_omniroute_tools(registry, router)

# Request and authorize session permissions
session_id = "user_session_1"
grant = consent.request_permission(session_id, PermissionLevel.EXECUTE, "Run OmniRoute Chat")
consent.authorize_permission(grant.grant_id)

# Execute registered tool
tool = registry.get_tool("omniroute_route_chat")
result = tool.execute(session_id=session_id, consent_center=consent, prompt="Hello agent!")
```

---

## Architecture Overview

```
USER / AGENT
     │
     ▼
COGNIS (Reasoning Layer)
     │
     ▼
TOOL REGISTRY (omniroute_route_chat)
     │
     ▼
PERMISSION CHECK (CP - CONSENT)
     │
     ▼
OMNIROUTE GATEWAY (Auto-fallback & Routing)
     │ ├── Provider 1 (Primary)
     │ ├── Provider 2 (Backup)
     │ └── Provider 3 (Free Tier)
     ▼
EVENT BUS (Audit Logging & Telemetry)
```

---

## License

MIT License
