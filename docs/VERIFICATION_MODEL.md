# VERITAS Verification Model

VERITAS (VR) is responsible for ensuring that all reported system findings and actions reflect real verified facts.

## Status Enum Standards
- `VERIFIED`: The action/finding was independently confirmed by real system check.
- `PARTIALLY_VERIFIED`: Outcome was partially confirmed with some unknown variables.
- `UNVERIFIED`: Action performed but not yet checked for confirmation.
- `UNCONFIRMED`: Insufficient evidence to confirm or deny.
- `NOT_IMPLEMENTED`: Feature/tool capability is not yet implemented.
- `ACCESS_UNAVAILABLE`: Insufficient OS or system permissions to perform check.
- `FAILED`: Execution or verification step returned an error.

## Rule Engine
VERITAS inspects evidence objects before any claim of completion is presented to the user.
