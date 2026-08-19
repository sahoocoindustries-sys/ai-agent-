# RUDRA Master Architecture

## Subsystem Map & Design
RUDRA is built as a modular architecture targeting an offline-first ~8 GB USB environment.

### Core Foundation Subsystems
- **AX (AXIOM)**: Master orchestration and lifecycle controller. Coordinates tasks, module states, error recovery.
- **CN (CONNECT)**: Device and USB connection layer. OS and architecture discovery, connection state.
- **CP (CONSENT)**: Permission and authorization center. Session-scoped permissions, audit logging.
- **ST (SESSION)**: Secure session management. Lifecycle, events, isolation, termination.
- **MB (BRIDGE)**: Event and message bus. Standardized message schema across subsystems.
- **TR (TOOL REGISTRY)**: Executable tool registry. Strict schema, platform mapping, permission requirements.
- **EV (EVIDENCE)**: Structured evidence collection. Timestamps, sources, severity, confidence.
- **VR (VERITAS)**: Truth & verification engine. Prevents false status reports; enforces state checks.
- **DX (DIEX)**: Real hardware & OS diagnostics (CPU, RAM, storage, process inspection).
- **SV (SOVEREIGN)**: Defensive security analysis (services, firewall, persistence checks).
- **SD (SAGE)**: Software Doctor (project inspection, error analysis, runtime checks).
- **AI (COGNIS)**: Reasoning intelligence layer (operates strictly via Tool Registry & Consent).
- **PR (VEIL)**: Privacy inspection and log/report data redaction.
- **DR (AEGIS)**: Authorized defensive remediation actions.
- **RB (RECOVER)**: Recovery state management and rollback capabilities.
- **VX (VOX)**: Offline voice synthesis and speech recognition interface.
- **HC (HORIZON)**: Command dashboard UI (React + TS + Vite).
- **RP (REPORT)**: Standardized report generator (JSON/Markdown/HTML).
- **PX (PULSE)**: Performance metrics and resource monitoring.
- **UX (AURA)**: Accessible user experience components and progress indicators.
- **HM (PULSEWATCH)**: Continuous health monitoring agent.
- **UP (PORT)**: Portable deployment and USB storage manager.
