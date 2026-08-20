"""
RUDRA Custom Error Hierarchy.
"""


class RudraError(Exception):
    """Base exception for all RUDRA errors."""
    def __init__(self, message: str, code: str = "RUDRA_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class PermissionDeniedError(RudraError):
    """Raised when an operation lacks required permission authorization."""
    def __init__(self, permission: str, justification: str = ""):
        msg = f"Permission denied for '{permission}'."
        if justification:
            msg += f" Reason: {justification}"
        super().__init__(msg, code="PERMISSION_DENIED")
        self.permission = permission


class SessionError(RudraError):
    """Raised when session is invalid, expired, or inactive."""
    def __init__(self, message: str):
        super().__init__(message, code="SESSION_ERROR")


class ToolError(RudraError):
    """Raised when tool registration or execution fails."""
    def __init__(self, message: str, tool_id: str = ""):
        super().__init__(message, code="TOOL_ERROR")
        self.tool_id = tool_id


class VerificationError(RudraError):
    """Raised when verification checks fail or evidence is insufficient."""
    def __init__(self, message: str):
        super().__init__(message, code="VERIFICATION_ERROR")


class ConfigurationError(RudraError):
    """Raised when configuration loading or validation fails."""
    def __init__(self, message: str):
        super().__init__(message, code="CONFIGURATION_ERROR")


class PlatformError(RudraError):
    """Raised when an operation is unsupported on the host platform."""
    def __init__(self, message: str):
        super().__init__(message, code="PLATFORM_ERROR")
