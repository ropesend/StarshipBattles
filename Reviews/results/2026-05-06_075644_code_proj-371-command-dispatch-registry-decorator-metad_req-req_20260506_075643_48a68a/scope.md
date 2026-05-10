# Review Scope: PROJ-371 Command Dispatch Registry

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260506_075643_48a68a
**Scope:** Three commits on `feat/03c-phase-aware-execution` — PROJ-371 Phase 1-3: `CommandRegistry`, `@command_spec` decorator, facade forwarder collapse, `specs.py` deletion, consumer migrations, AST regression, third-party command smoke test.
**Instructions:** 8 focus areas (see request for detail): decorator-metadata-only contract, reset/seed cycle, facade forwarder design decision, specs.py deletion, consumer migrations, WARP silent-drift cleanup, cross-project handler overlap, general code hygiene.
**Context:** Wave B project 3/5. PROJ-371 is the third strategy-chain project. Decorator-metadata-only contract is the central design constraint per joint Codex+Claude review. Sharded suite: 18944/18948 pass.
**Review mode:** normal — full code review of production + test files in scope.
