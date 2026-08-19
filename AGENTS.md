# AGENTS.md — RUDRA Permanent Engineering Rules

## 1. ABSOLUTE RULE: NO FAKE CREATION
- NEVER create fake scan results, simulated security vulnerabilities, or mock hardware information presented as real.
- NEVER claim an action succeeded when it did not or describe placeholder functions as completed features.
- NEVER fabricate AI response tools or report "fixed" unless the operation was executed and verified.

## 2. EXPLICIT STATUS CONVENTIONS
When an operation or capability is queried, use exact status codes:
- `NOT_IMPLEMENTED`: Feature is planned but code is not yet written.
- `ACCESS_UNAVAILABLE`: Feature exists but required system/OS permissions are lacking.
- `UNCONFIRMED`: Evidence is insufficient to verify finding or claim.
- `FAILED`: Action was attempted but failed during execution.
- `VERIFIED`: Action was completed and independently verified by VERITAS.
- `PARTIALLY_VERIFIED`: Action was partially completed or partially verified.

## 3. CONTROLLED AI EXECUTION MODEL
- The reasoning engine (COGNIS) MUST NOT execute unrestricted shell commands directly.
- All system execution flow MUST follow:
  `USER -> COGNIS -> TOOL REGISTRY -> PERMISSION CHECK -> REAL TOOL -> REAL RESULT -> EVIDENCE -> VERITAS -> USER`
- Tools must be explicitly registered in the Tool Registry with schema and required permission levels.

## 4. SECURITY & ETHICAL BOUNDARIES
- Operates strictly on user-authorized devices with least privilege.
- Respects OS security boundaries (Windows, Android, iOS); no silent privilege elevation or exploit usage.
- Does not perform destructive actions without explicit user confirmation.
- Redacts sensitive credentials, tokens, and personal data from logs and reports.

## 5. DEVELOPMENT & VERIFICATION WORKFLOW
Every engineering task must follow:
`OBSERVE -> PLAN -> IMPLEMENT -> TEST -> VERIFY -> DOCUMENT -> REPORT`
- All changes must be backed by real `pytest` test suites.
- Do not claim completion without test execution and verification.
