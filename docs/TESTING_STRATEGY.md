# RUDRA Testing Strategy

## Philosophy
- Zero fake tests.
- Every subsystem test must test real python implementations and contracts.
- Unimplemented features must explicitly test that `NOT_IMPLEMENTED` or `ACCESS_UNAVAILABLE` status is returned rather than faking success.

## Test Categories
1. **Core Unit Tests**: Configuration, logging redaction, event bus delivery, error handling.
2. **Permission & Session Tests**: Permission granting, revocation, session lifecycle, expiration.
3. **Tool Registry Tests**: Schema validation, registration, invalid tool rejection.
4. **Evidence & Verification Tests**: Verification pipeline and state transitions.
5. **Orchestrator Integration Tests**: AXIOM lifecycle and message routing.
