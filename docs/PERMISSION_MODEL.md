# RUDRA Permission Model

## Permission Levels
- `READ_ONLY`: Inspection of non-sensitive system status (CPU, RAM, public configs).
- `SYSTEM_READ`: Reading sensitive system state (processes, services, logs, security configs).
- `FILE_READ`: Reading project files and source code.
- `FILE_WRITE`: Modifying user files or configuration files (requires user confirmation).
- `EXECUTE`: Executing non-destructive utilities or test scripts.
- `SYSTEM_MODIFY`: Altering system settings, stopping processes, changing firewall rules (requires explicit high-impact confirmation).
- `ELEVATED`: Administrative / root privilege operations.

## Grant Lifecycle
- `REQUESTED` -> `GRANTED` / `DENIED` -> `REVOKED` / `EXPIRED`.
- Permissions are tied to an active `SessionID`.
