"""
RUDRA Executable Tool Registry Subsystem (TR - TOOL REGISTRY).
"""
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from rudra.core.models import PermissionLevel, Status
from rudra.core.errors import ToolError, PermissionDeniedError
from rudra.core.permissions import ConsentCenter


@dataclass
class ToolSchema:
    tool_id: str
    name: str
    description: str
    version: str
    required_permission: PermissionLevel
    supported_platforms: List[str] = field(default_factory=lambda: ["windows", "linux", "darwin"])


class RegisteredTool:
    def __init__(self, schema: ToolSchema, handler: Callable[..., Any]):
        self.schema = schema
        self.handler = handler

    def execute(self, session_id: str, consent_center: ConsentCenter, **kwargs) -> Any:
        # Enforce consent permission before executing real tool
        consent_center.enforce_permission(
            session_id=session_id,
            permission=self.schema.required_permission,
            justification=f"Execution of registered tool {self.schema.tool_id}"
        )
        return self.handler(**kwargs)


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, RegisteredTool] = {}

    def register_tool(self, schema: ToolSchema, handler: Callable[..., Any]) -> None:
        if schema.tool_id in self._tools:
            raise ToolError(f"Tool with ID '{schema.tool_id}' is already registered.", tool_id=schema.tool_id)
        if not callable(handler):
            raise ToolError(f"Handler for tool '{schema.tool_id}' must be callable.", tool_id=schema.tool_id)
        self._tools[schema.tool_id] = RegisteredTool(schema, handler)

    def get_tool(self, tool_id: str) -> RegisteredTool:
        if tool_id not in self._tools:
            raise ToolError(f"Tool '{tool_id}' not found in registry.", tool_id=tool_id)
        return self._tools[tool_id]

    def list_tools(self) -> List[ToolSchema]:
        return [tool.schema for tool in self._tools.values()]
