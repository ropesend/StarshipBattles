# PROJ-382 Implementation Review

**Date:** 2026-05-09  
**Reviewer:** Codex  
**Verdict:** **FAIL - audit blocked, with confirmed implementation and execution issues.**

Protocol 04 says not to proceed with a completion audit when audit-readiness validation fails. I therefore do not certify PROJ-382 as audit-passed. The findings below are a skeptical post-implementation review of the current source and project records, limited to evidence that was practical to verify after the readiness blocker.

## Validation Result

`python Projects/scripts/validate_audit_ready.py PROJ-382` failed.

Observed validator output:

- Result: `FAILED`
- 12 errors, 1 warning
- Phase completion failures: Phases 1-5 are all reported as `Not Started`
- Task completion failures: 32 tasks have incomplete subtasks
- Status warning: index status is `Planning`

The project records are internally inconsistent. `plan.md` claims every phase is complete at lines 16-20 and says the active phase is closeout at line 24, but every phase checklist still has `**Status:** Not Started` (`phase_1_checklist.md:8`, `phase_2_checklist.md:8`, `phase_3_checklist.md:8`, `phase_4_checklist.md:8`, `phase_5_checklist.md:8`) and the plan's own verification boxes remain unchecked (`plan.md:76-77`).

## Tests Run

- `python Projects/scripts/validate_audit_ready.py PROJ-382` - **failed**, 12 errors, 1 warning.
- `pytest tests/static_guards/test_facade_bypass_guard.py tests/unit/simulation/entities/test_projectile.py -q -p no:cacheprovider` - **passed**, 692 passed.
- `pytest tests/unit/strategy/data/test_galaxy_spatial_index.py tests/unit/workshop/test_stat_getters.py tests/unit/ui/screens/builder/test_stat_getters.py tests/unit/strategy/engine/test_production_spawner.py -q -p no:cacheprovider` - **failed**, 15 failed, 67 passed. All observed failures were in `tests/unit/strategy/data/test_galaxy_spatial_index.py`.
- `pytest tests/unit/workshop/test_stat_getters.py tests/unit/ui/screens/builder/test_stat_getters.py tests/unit/strategy/engine/test_production_spawner.py -q -p no:cacheprovider` - **passed**, 55 passed.
- `pytest tests/unit/ui/screens/test_strategy_build_queue_manager.py tests/unit/ui/screens/strategy_windows/test_build_queue_windows.py tests/unit/ui/screens/test_empire_build_queue_window.py tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -q -p no:cacheprovider` - **passed**, 158 passed.

I did not run the full sharded suite because audit-readiness failed and a required focused Phase 2 test target is already red.

## Plan Goals vs Actual Implementation

Phase 1 mostly landed for the narrow build-queue command-dispatch bypass: `BuildQueueScreen` now dispatches through `self.facade.handle_command(...)` at `game/ui/screens/build_queue_screen.py:448`, `:482`, and `:515`, and `EmpireBuildQueueWindow` dispatches through `self._facade.handle_command(...)` at `game/ui/screens/empire_build_queue_window.py:420`. The static guard exists and passed.

Phase 1 did **not** fully meet the stated goal of eliminating the public `self.session` propagation chain. `plan.md:33` explicitly includes that goal, but `StrategyScreen.session` remains a public property at `game/ui/screens/strategy_screen.py:214-248`, and current UI code still reads `scene.session` or `screen.session` in multiple files, including `game/ui/screens/strategy_detail_formatter.py:112`, `:278`, `:395-396`, `game/ui/screens/strategy_game_state_manager.py:87`, `:175`, `:183`, and `game/ui/screens/strategy_windows/list_windows.py:60-61`.

Phase 2 is partially landed: TypeGuard usage is present in `game/strategy/data/galaxy_spatial_index.py:10` and `:38-39`; `WorkshopEventBus` exists at `game/ui/screens/builder/event_bus.py:19`; `DesignSelectorWindow` subclasses `StrategyModalWindow` at `game/ui/screens/design_selector_window.py:47`; and the hardcoded superweapon list was replaced with `SUPERWEAPONS`-derived names at `game/ui/screens/builder/stat_getters.py:329-330`. However, the required `galaxy_spatial_index` focused tests fail, and projectile event logging was not wired through production constructors.

Phase 3 is partly landed: `GameSession.handle_command` now dispatches unconditionally at `game/strategy/engine/game_session.py:379-382`; `superweapon_command_handlers.py` imports `BaseCommandHandler` from `handlers/base.py` at `game/strategy/engine/superweapon_command_handlers.py:15`; and `ProductionSpawner.registries` is a required keyword at `game/strategy/engine/production_spawner.py:34-40`. JSON cleanup was not literal to the checklist because some `json` imports were retained for exception types or in-memory pretty printing.

Phase 4 doc work appears present for Pattern #23 and Re-Export Shim (`docs/02_PATTERNS.md:438-450`, `:722-762`), and the Strategy Config Singleton variant appears documented at `docs/02_PATTERNS.md:277-281`.

Phase 5 line-count goals appear met in the current source by manual count: `battle_engine.py` 410 LOC, `fleet_navigation_service.py` 420 LOC, `conflict_resolution_engine.py` 423 LOC, `superweapon_order_processor.py` 434 LOC, and the new `planetary/` package modules are all below 500 LOC. This does not match the project records, which still say Task 5.4 was deferred (`phase_5_checklist.md:46-64`, `plan.md:20`, `plan.md:25`).

## Literal Checklist Execution

The literal checklist execution is not acceptable for audit:

- Every phase checklist still says `Status: Not Started`.
- Every task checkbox I inspected remains unchecked.
- The completion checklist in `plan.md` is unchecked.
- Phase verification commands are not recorded as complete in the checklists.
- Phase 5 says `superweapon_order_processor.py` is deferred, while current source is already under the 500 LOC ceiling. Either the records were never updated, or later work changed the code without synchronizing PROJ-382.

This is enough by itself to fail Protocol 04 readiness.

## Findings

### 1. Blocker: PROJ-382 cannot pass audit because project state is unsynchronized

**Severity:** Blocker  
**Evidence:** `validate_audit_ready.py` failed; `Projects/active_projects/PROJ-382/plan.md:16-20`, `:24`, `:76-77`; `phase_1_checklist.md:8`, `phase_2_checklist.md:8`, `phase_3_checklist.md:8`, `phase_4_checklist.md:8`, `phase_5_checklist.md:8`.

The plan claims all phases are complete, but the authoritative checklists still report Not Started and unchecked work. This is not just clerical: Protocol 04 explicitly blocks the audit when this validator fails.

### 2. Major: Required Phase 2 focused tests fail for `GalaxySpatialIndex`

**Severity:** Major  
**Evidence:** `Projects/active_projects/PROJ-382/phase_2_checklist.md:16-18`; `game/strategy/data/galaxy_spatial_index.py:51`, `:55`, `:66`, `:77`; `tests/unit/strategy/data/test_galaxy_spatial_index.py:16-26`, `:73-80`.

The Phase 2 checklist names `pytest tests/ -k galaxy_spatial_index --testmon` as the verification target. Running the direct unit file produced 15 failures. The production code now reads `self._state.planet_to_system`, `global_hex_planets`, and `global_hex_zones`, while the unit fixture still passes `_MockGalaxy` with underscored fields (`_planet_to_system`, `_global_hex_planets`, `_global_hex_zones`). Whether the production contract or the test fixture is stale, the required project verification target is currently red.

### 3. Major: Projectile event logging injection is incomplete

**Severity:** Major  
**Evidence:** `Projects/active_projects/PROJ-382/phase_2_checklist.md:47-49`; `game/simulation/entities/projectile.py:8-20`, `:40-42`, `:119-122`, `:138-141`; `game/simulation/combat/families/seeker.py:55-65`; `game/simulation/combat/families/projectile.py:33-43`; `game/simulation/battle_state.py:564-575`.

The plan required projectile lifecycle events to dispatch through an injected EventBus-compatible logger and specifically verify `SEEKER_EXPIRE` still records. The implementation added an `event_logger` kwarg, but current production constructors do not pass it, and the default logger is a no-op. `rg event_logger` under `game/simulation` finds only `projectile.py`. Result: missile expiration telemetry is silently dropped in normal construction paths.

### 4. Major: Facade registry access contradicts current pattern docs

**Severity:** Major  
**Evidence:** `docs/02_PATTERNS.md:96-104`; `game/strategy/facade/strategy_session_facade.py:367-375`; `game/ui/screens/build_queue_screen.py:210-213`, `:237-239`, `:520-523`; `game/ui/screens/empire_build_queue_window.py:188-190`.

The current Pattern #3 docs explicitly say UI code should use `get_default_registry_provider()` when needed and should not access registries through `scene.facade` because the facade does not expose them. PROJ-382 added exactly that facade exposure with `StrategySessionFacade.get_registries()` and uses it from UI build-queue screens. This is a code/docs conflict and undercuts the Phase 1 facade-integrity goal.

### 5. Moderate: The public `StrategyScreen.session` chain survived the project goal

**Severity:** Moderate  
**Evidence:** `Projects/active_projects/PROJ-382/plan.md:33`; `game/ui/screens/strategy_screen.py:214-248`; `game/ui/screens/strategy_detail_formatter.py:112`, `:278`, `:395-396`; `game/ui/screens/strategy_game_state_manager.py:87`, `:175`, `:183`; `game/ui/screens/strategy_windows/list_windows.py:60-61`.

The implementation guards against `session.handle_command(...)`, which is useful, but it keeps a public `session` property and many UI reads still depend on it. This may be an intentional compromise due deferred U1/U2/U3, but then the plan goal was overbroad and the project should not claim that the public session propagation chain was eliminated.

## Plan Gaps and Missed Assumptions

- The plan conflicted with itself by deferring U1/U2/U3 read-side UI bypasses while also setting a Phase 1 goal to eliminate the public `self.session` propagation chain.
- The plan did not define a clean registry-access boundary for build-queue helpers. The implementation chose `facade.get_registries()`, but current docs say not to expose registries through the facade.
- The JSON cleanup tasks assumed bare `json` imports were persistence calls. In current code, `race_library.py:14-20` and `setup_data_io.py:15-18` retain `json` only for `json.JSONDecodeError`, and `detail_panel.py:11-15`, `:201` retains `json.dumps` for in-memory debug formatting because `json_utils` has no string-format helper. Those are plan-quality gaps, not necessarily implementation bugs.
- Phase 5 underestimated the design work needed for `superweapon_order_processor.py`; the checklist says the task was deferred because the clean extraction requires registry restructuring. Current source is under 500 LOC anyway, so the project record no longer explains the actual state.

## Residual Risks

- Full sharded regression was not run.
- Manual UI smokes listed in the phase checklists were not run.
- Pattern audit was not run.
- The current code includes later PROJ references (`PROJ-390`, `PROJ-396`), so attribution between original PROJ-382 work and later cleanup is not clean from source alone.
- Focused tests emitted repeated `QualityImprovementAbility does not support scope 'system'` warnings during setup; I did not triage those because they were not the source of the observed failures.
