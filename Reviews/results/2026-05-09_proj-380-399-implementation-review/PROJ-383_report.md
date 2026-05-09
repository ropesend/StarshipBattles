# PROJ-383 Implementation Review

**Project:** PROJ-383 - Legacy removal: `command_handlers.py` shim eradication  
**Review date:** 2026-05-09  
**Reviewer:** Codex  
**Verdict:** **Not audit-clean.** The implementation meets the core code goals: callers were migrated, the shim file is deleted, and focused command-handler tests pass. However, repository docs still describe the deleted shim as current/transitional, and the project index still marks PROJ-383 as `Planning`.

## Validation Result

`python Projects/scripts/validate_audit_ready.py PROJ-383` passed.

- Phase completion: PASS
- Task completion: PASS
- Blockers/status: PASS
- Warning: `Index status: Planning`

`python Projects/scripts/validate_phase.py PROJ-383 1` also passed with 0 errors and 5 warnings for empty task notes.

## Tests And Checks Run

| Command | Result |
|---|---|
| `python Projects/scripts/validate_audit_ready.py PROJ-383` | PASS, warning: index status `Planning` |
| `python Projects/scripts/validate_phase.py PROJ-383 1` | PASS, 0 errors, 5 warnings |
| `pytest tests/unit/strategy/engine/test_command_handlers_public_api.py tests/unit/strategy/engine/test_command_registry_contract.py tests/unit/strategy/engine/test_command_registry_seeding.py -q -p no:cacheprovider` | 85 passed |
| `pytest tests/unit/strategy/engine/test_planet_command_handlers.py -q -p no:cacheprovider` | 36 passed |
| `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/engine/test_superweapon_handler_validation.py tests/unit/strategy/engine/test_superweapon_edge_cases.py -q -p no:cacheprovider` | 69 passed |
| `pytest tests/ -k game_session -q -p no:cacheprovider` | 41 passed |
| `Test-Path game/strategy/engine/command_handlers.py` | Missing, as intended |
| `rg "game\.strategy\.engine\.command_handlers\|from game\.strategy\.engine\.command_handlers\|import game\.strategy\.engine\.command_handlers" game tests combat_lab Tools` | No hits |

I did not run the full sharded suite during this review. The focused coverage exercises the touched command-handler import surfaces and registry construction paths.

## Plan Goals Vs Actual Implementation

| Plan goal | Review result |
|---|---|
| Migrate all production callers from `game.strategy.engine.command_handlers` to canonical `game.strategy.engine.handlers/` paths. | Met for current source. `planet_command_handlers.py`, `superweapon_command_handlers.py`, and `game_session.py` import from `game.strategy.engine.handlers` or `handlers.base`; `rg` found no legacy import path in production code. |
| Migrate all 25 test callers. | Met for current tests. `rg` found no legacy import path in `tests/`; focused tests passed. |
| Delete `game/strategy/engine/command_handlers.py`. | Met. The file is absent. |
| Preserve command handler behavior while removing the shim. | Supported by focused tests: command-handler public API, registry contract/seeding, planet handlers, superweapon handlers, and `game_session` tests passed. |

The implementation also handled a plan drift correctly: Task 1.2 was already completed by PROJ-382, so PROJ-383 treated it as a no-op and documented that in `Projects/active_projects/PROJ-383/findings/verification_report.md`.

## Literal Checklist Execution

Phase 1 is marked `Complete`, and every task checkbox in `phase_1_checklist.md` is checked.

- Task 1.1: The four lazy `BaseCommandHandler` imports in `planet_command_handlers.py` now point to `game.strategy.engine.handlers.base`.
- Task 1.2: The `superweapon_command_handlers.py` import was already migrated before this project and is correctly checked as a no-op.
- Task 1.3: `game_session.py` imports `create_default_registry` from `game.strategy.engine.handlers`.
- Task 1.4: Test imports were migrated; no test imports from the deleted shim remain.
- Task 1.5: The shim file is deleted; focused tests pass.

Process caveat: `validate_phase.py` reports all five tasks as complete but with empty task notes. Some execution notes exist in `findings/verification_report.md`, so this is not blocking by itself, but the checklist file did not carry per-task implementation notes.

## Plan Gaps And Missed Assumptions

The initial plan treated this as a code/test import migration and deletion task, but it did not include documentation updates or a docs grep in closeout. That was a missed assumption: the deleted shim was explicitly documented in architecture/pattern/order-system docs. Because the final grep scope focused on `game/`, `tests/`, `combat_lab/`, and `Tools/`, stale docs survived the implementation.

The plan also did not account for syncing `Projects/projects_index.md`; audit-readiness validation still warns that PROJ-383 is indexed as `Planning` despite the project plan marking it complete.

## Findings

### Major: Docs still reference the deleted shim as current

**Evidence:**
- `docs/02_PATTERNS.md:167-170` says `game/strategy/engine/command_handlers.py` is a transitional re-export shim.
- `docs/02_PATTERNS.md:726-736` still lists `game/strategy/engine/command_handlers.py` as one of the confirmed re-export shim sites.
- `docs/systems/strategy_layer.md:67-89` says command dispatch lives in `game/strategy/engine/command_handlers.py` and lists that deleted file as the runtime `CommandHandlerRegistry` location.
- `docs/systems/orders_system.md:129` and `docs/systems/orders_system.md:406` still say `game/strategy/engine/command_handlers.py` is a transitional re-export shim.
- The actual file is gone, and `rg` found no import path remaining in `game`, `tests`, `combat_lab`, or `Tools`.

**Impact:** Agents following the docs will import or inspect a non-existent file. This violates the repository rule to keep code and docs consistent in the same change and undermines the stated goal of eradicating the shim as a current architectural surface.

**Needed fix:** Update the command dispatch and re-export-shim documentation to point to `game/strategy/engine/handlers/base.py`, `game/strategy/engine/handlers/registry_factory.py`, and the `game/strategy/engine/handlers/` package as the canonical runtime command-handler API. Remove `command_handlers.py` from current shim lists.

### Minor: Project index still marks PROJ-383 as Planning

**Evidence:**
- `Projects/projects_index.md:23` lists PROJ-383 status as `Planning`.
- `validate_audit_ready.py PROJ-383` passed but emitted `Index status: Planning`.

**Impact:** This does not affect runtime behavior, but it leaves project management state inconsistent with `plan.md` and audit validation output.

**Needed fix:** Sync the project index after the implementation/docs cleanup is complete.

## Residual Risks

- Full sharded regression was not rerun during this review; only focused command-handler and `game_session` tests were run.
- Documentation drift is the main unresolved risk. The code removal itself appears mechanically sound.
- The project plan claims final focused regression had 1319 passing tests with 2 unrelated PROJ-393 failures, but this review did not independently reproduce that larger run.
