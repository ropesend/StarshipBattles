# Review Scope: PROJ-383 — command_handlers.py shim eradication

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260509_020618_c49644
**Scope:** 3 commits on `feat/03c-phase-aware-execution`:
- `db061fe90` — production migrations (Tasks 1.1 + 1.3)
- `e171d3573` — test migrations (Task 1.4)
- `f37514b78` — closeout (Task 1.5 + state updates, file deletion)

**Production files:**
- `game/strategy/engine/planet_command_handlers.py` (4 lazy imports at lines 55, 127, 149, 185 → migrated to `game.strategy.engine.handlers.base`)
- `game/strategy/engine/game_session.py` (1 import at line 67 → migrated to `game.strategy.engine.handlers`)
- `game/strategy/engine/superweapon_command_handlers.py` (already done by PROJ-382 phase 3 commit `73eb2a635`)

**Test files (25 sites across 10 files):**
- `tests/unit/strategy/test_command_handlers.py`
- `tests/unit/strategy/engine/test_command_handlers_public_api.py`
- `tests/unit/strategy/engine/test_base_command_handler.py`
- `tests/unit/strategy/engine/test_command_ownership.py`
- `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
- `tests/unit/strategy/engine/test_colonize_mission_handler.py`
- `tests/unit/strategy/engine/test_build_order_command_handler.py`
- `tests/integration/colonization/test_explicit_orders.py`
- `tests/integration/strategy/test_warp_orders.py`
- `tests/integration/strategy/test_fleet_join_redirect.py`

**Deleted file:** `game/strategy/engine/command_handlers.py` (82 LOC)

**Instructions:** Verify the deletion is total — no hidden references anywhere in the repo. Seven specific verification tasks: (1) grep verification, (2) already-done claim verification, (3) production migration correctness, (4) test migration correctness, (5) CLAUDE.md Rule 3 compliance, (6) cross-check with PROJ-380, (7) smoke-test the import.

**Context:** Seventh of 11 sequential PROJ runs. Stage 2 closeout. Sits on top of PROJ-380's 12 commits, PROJ-386's commit, and the merge bringing in PROJ-385/387/388. Pre-existing test failures (PROJ-393 species-id fallback) noted as independent.
