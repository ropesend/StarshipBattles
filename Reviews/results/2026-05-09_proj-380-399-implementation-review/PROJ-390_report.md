# PROJ-390 Implementation Review

**Date:** 2026-05-09  
**Reviewer:** Codex  
**Verdict:** Not audit-clean. The runtime/code removal goal is met, and regression coverage is green, but current documentation and checklist evidence still contradict the completed implementation.

## Validation Result

- `python Projects/scripts/validate_audit_ready.py PROJ-390`: PASSED.
  - Warning: `Projects/projects_index.md` still lists PROJ-390 as `Planning`.
- `python Projects/scripts/validate_phase.py PROJ-390 1`: PASSED.
  - Warnings: all five completed tasks have empty `Notes`.

## Tests And Checks Run

- `rg` checks for `log_event`, `set_event_handler`, `get_event_handler`, and `_event_handler` across `game/`, `tests/`, `combat_lab/`, `Tools/`, `docs/`, and the project files.
- `python -c "import game.core as c; ..."`: `EventBus` is exported; `log_event`, `set_event_handler`, and `get_event_handler` are not exported.
- `python -c "from game.core.event_logging import log_event"`: failed with `ImportError`, as expected after shim deletion.
- `pytest tests/unit/core/event_logging tests/unit/systems/test_event_bus.py tests/unit/strategy/test_game_session_events.py tests/integration/strategy/test_event_log_integration.py tests/integration/strategy/test_event_log_empire_filter.py`: 51 passed.
- `pytest tests/unit/strategy/engine/order_handlers tests/unit/strategy/engine/test_production_spawner.py tests/unit/strategy/engine/test_production_engine_consumption.py tests/unit/strategy/engine/test_planet_energy_engine.py tests/unit/strategy/engine/test_planet_action_engine.py tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py tests/unit/strategy/engine/test_conflict_resolution_event_replay.py tests/unit/strategy/engine/test_superweapon_event_payloads.py`: 168 passed.
- `pytest tests/unit/simulation/entities/test_projectile.py tests/unit/simulation/test_projectile_manager.py tests/unit/simulation/projectile_guidance tests/unit/ai/target_evaluator/test_projectile_candidate_guards.py tests/unit/modifiers/test_projectile_weapon_bindings.py tests/unit/simulation/combat/test_combat_events.py tests/unit/simulation/combat/test_damage_calculator_events.py`: 163 passed.
- `python Tools/test_sharded/test_sharded.py`: 19803 collected; 19799 passed, 4 skipped.

## Plan Goals Vs Actual Implementation

- **Migrate production callers to injected event handling:** Met for live code. Most caller migration had already landed in PROJ-382; PROJ-390's remaining live caller was `game/simulation/entities/projectile.py`, whose default callback is now a no-op while injected `event_logger=` remains available.
- **Delete module-level `log_event`, `set_event_handler`, `get_event_handler`, and `_event_handler`:** Met. `game/core/event_logging.py` now exposes only `EventBus`, and `game/core/__init__.py` re-exports only `EventBus` for this area.
- **Update `docs/02_PATTERNS.md` section 10:** Met. That section now states constructor injection is the only supported event-emission pattern.
- **Preserve session-scoped isolation:** Met in code. `GameSession` owns an `EventBus`; the deleted process-global handler is gone.

## Literal Checklist Execution

- Task 1.1 caller enumeration was performed and recorded at `AgentCoordination/Scratchpad/reports/proj_390_event_logging_callers.md`. The exact filename differs from the checklist text, but the artifact exists and explains the narrowed scope.
- Task 1.2 is not literally true as checked. The checklist says to add/confirm `ctx.event_bus`, but `game/context.py` has no `event_bus` or `EventBus` wiring. The project's own verification report correctly states that `ApplicationContext` wiring would be the wrong scope, but the checklist was not revised and has no notes.
- Tasks 1.3 through 1.5 are materially complete for live code and tests.
- The checklist claim that a "full grep for the deleted symbols returns zero hits" is overbroad. The current codebase still has live documentation/comment hits outside historical/project-plan markdown.

## Plan Gaps And Missed Assumptions

- The plan scoped the documentation update to `docs/02_PATTERNS.md` only. It missed current docs in `docs/01_ARCHITECTURE.md` and `docs/05_ERROR_HANDLING.md` that still describe the deleted module-level API.
- The original plan assumed `EventBus` should be available from `ApplicationContext` as `ctx.event_bus`. That was the wrong architecture for this project because the event bus must be session-scoped. The implementation made the right code choice, but the plan/checklist remained stale instead of being corrected.
- The plan did not require a tracked negative-import/static guard for the deleted module-level API. The runtime surface is currently correct, but future reintroduction is protected only by review/static grep discipline, not a focused guard test.

## Findings

### Major: Current docs still tell agents/developers to use the deleted API

`docs/05_ERROR_HANDLING.md:147-154` says `game/core/event_logging.py` exposes a session-scoped `EventBus`, then immediately says module-level `set_event_handler()`, `get_event_handler()`, and `log_event()` remain compatibility API. `docs/01_ARCHITECTURE.md:96` also lists `event handler accessors` and `log_event` as part of `event_logging.py`. That is now false: importing `log_event` from `game.core.event_logging` raises `ImportError`. This violates the project goal of retiring the compatibility shim cleanly and the repo rule to keep docs consistent.

### Minor: Phase checklist overclaims `ApplicationContext` execution

`Projects/active_projects/PROJ-390/phase_1_checklist.md:24-28` marks the `ctx.event_bus` work complete, but `game/context.py` has no `EventBus` or `event_bus` wiring. `Projects/active_projects/PROJ-390/findings/verification_report.md:56-65` explains why that wiring would be wrong and why `GameSession` should own the bus. The implementation decision is sound, but the checklist should have been revised or annotated instead of checked as if the original task happened.

### Minor: Source comments still mention the old global path

`game/strategy/engine/game_session.py:275-280` says `_create_event_handler()` creates a callback for the "global log_event() system." `game/simulation/entities/projectile.py:36-38` still says the projectile default preserves behavior through a module-level dispatcher, even though `_default_event_logger` is now a no-op. These are not runtime regressions, but they are stale guidance in touched implementation areas.

## Residual Risks

- The full suite is green, so runtime regression risk is low.
- Audit-clean status is blocked on documentation/checklist cleanup, not on the core shim deletion itself.
- Because the project intentionally did not add a negative-import guard, future accidental reintroduction of the module-level API would rely on audit grep rather than an explicit test.
