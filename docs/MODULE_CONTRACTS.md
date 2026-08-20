# RUDRA Module Contracts

Each subsystem in RUDRA implements standard contract interfaces:

```python
class BaseSubsystem(Protocol):
    subsystem_id: str
    name: str

    def initialize(self) -> bool: ...
    def get_status(self) -> SubsystemStatus: ...
    def shutdown(self) -> bool: ...
```

## Standard Message Structures (BRIDGE)
- `TaskRequest`: Subject, task payload, requested permissions, session ID.
- `TaskResult`: Task ID, status (`VERIFIED`, `FAILED`, `NOT_IMPLEMENTED`), output, errors.
- `Finding`: Evidence ID, source subsystem, severity, details.
- `PermissionRequest`: Required permission, scope, justification.
