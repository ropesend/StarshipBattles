# Test Quality Review: PROJ-331 + PROJ-332 + PROJ-333 + PROJ-341

**Review mode:** Fresh-eyes, CRITICAL/MAJOR only
**Scope:** Characterization tests for strategy/simulation engine cluster
**Request ID:** req_20260504_231829_287e98
**Date:** 2026-05-04
**Method:** 4 parallel subagents (one per project), compiled by OpenCode

---

## Overall Summary

| Project | CRITICAL | MAJOR | Verdict |
|---------|----------|-------|---------|
| PROJ-331 | 0 | 2 | Adequate |
| PROJ-332 | 0 | 2 | Good (minor gaps) |
| PROJ-333 | 5 | 7 | **NOT adequate** |
| PROJ-341 | 0 | 3 | Adequate |
| Cross-project | 0 | 1 | Doc inconsistency |
| **Total** | **5** | **15** | |

---

## PROJ-331 (battle_state + battle_controller + conflict_resolution)

### Verified: All 3 OBSERVATION-A/B/C correctly pinned

- **OBSERVATION-A** (`_collect_team_modifiers` broad-except): Pinned by `test_collect_team_modifiers_returns_none_and_logs_when_collector_raises` at `test_logging_and_lookups.py:251`. Real ConflictResolutionEngine created; only the external collector is patched. Correctly asserts return is None on exception.
- **OBSERVATION-B** (`load_state` UnboundedRegion fallback): Pinned by `test_load_state_restores_battle` at `test_state.py:42`. Asserts `isinstance(controller._retreat_manager.boundary, UnboundedRegion)`. Production line 639 exercised.
- **OBSERVATION-C** (`_extract_outcome_on_battle_end` capture-sink swallow): Pinned by `test_outcome_is_set_when_capture_sink_raises` at `test_state.py:292`. Asserts outcome set despite `on_battle_ended` raising RuntimeError. Commit 5364c3f62 applied all review-1 MAJOR fixes.

### MAJOR findings

- **F1 (MAJOR):** `BattleState` class fully mocked in controller `save_state`/`get_results` tests (`test_state.py:33,131,157`). `capture_from_engine` is independently tested, so this is a stacking concern, not a gap.
- **F2 (MAJOR):** No end-to-end `resolve_all_conflicts(tick != None)` integration test in PROJ-331 set. Individual components are covered; stitched path not exercised in this file.

### Missing surfaces: None. All public methods on 3 production files covered.

---

## PROJ-332 (turn_engine)

### Verified: phase_times keys pinned correctly

Both `test_turn_engine_init_precedence.py:45` and `test_turn_engine_phase_timing.py:33` assert the full 14-key canonical set includes `'harvesting'` (not `'harvest'`). Production code at `turn_engine.py:230` uses `'harvesting'`.

### Verified: Monkeypatch correct (Item 7)

`test_turn_engine_phase_timing.py:89-92` patches `turn_engine_mod.time.perf_counter` where `turn_engine_mod` is `import game.strategy.engine.turn_engine as turn_engine_mod`. Since production does `import time` at line 60, `turn_engine_mod.time` is the same module object. Patch target correct. Test creates real TurnEngine instance — not vacuous.

### MAJOR findings

- **F1 (MAJOR):** 5 of 15 lazy `@property` getters lack default-construction characterization: `action_engine`, `planet_action_engine`, `component_activation_engine`, `organics_consumption_engine`, `happiness_engine`. Their injected-mock paths are exercised but the "what gets constructed when no mock" path is not pinned.
- **F2 (MAJOR):** `create_default_turn_engine` factory function (`turn_engine.py:756-794`) has no characterization test.

### No vacuous tests. All 27 tests use real TurnEngine. 15 injectable engines mocked at boundary per D-002. All test names descriptive.

---

## PROJ-333 (per-turn engines — 8 test files)

### 5 CRITICAL findings

1. **CRITICAL: MAX_QUEUE_ITERATIONS assertion too weak** — `test_production_engine_queue.py:293`. Uses `call_count <= 10` instead of `== 10`. With 20 zero-cost items, a `<=` assertion passes even if only 2 items processed. Must use `== MAX_QUEUE_ITERATIONS` plus `len(queue) == 10` remaining assertion.

2. **CRITICAL: Auto-disable multi-component match untested** — `test_characterization.py` (consumable_management). Observation 8 says "Auto-disable iterates ALL components matching depleted resource." Existing tests only have one matching component. No test verifies multiple components disabling simultaneously. Also no test for same-tick re-disable path.

3. **CRITICAL: `FleetMovementEngine.calculate_next_hex` zero coverage** — Public method has zero characterization tests. Neither delegation to `FleetNavigationService` nor lazy-init path tested.

4. **CRITICAL: 3 production_spawner methods zero direct coverage** — `_load_and_create_ship`, `_create_and_place_facility`, `_spawn_fleet_ship` are all patched out in dispatch tests. Zero tests exercise their method bodies (design loading, facility creation, ShipInstance creation, event emission).

5. **CRITICAL: Fleet context branches zero coverage** — `_log_resource_shortage` and `_apply_resource_consumption` both dispatch on `context_type` with three branches (planet/fleet/empire-fallback). Only planet and empire-fallback tested. Fleet context (`fleet.get_cargo_resource()`/`fleet.consume_cargo_resource()`) has zero characterization.

### 7 MAJOR findings

1. **MAJOR: Monkeypatch fragility** — `test_production_engine_queue.py` uses `monkeypatch.setattr` on internal module-level functions (`_colony_has_planetary_yard`, `_get_facility_production_rates`) instead of setting mock colony attributes per D-002 boundary-mocking guidance.

2. **MAJOR: `context_type=None` fixture ambiguity** — Queue file's `colony` fixture sets `context_type=None`, exercises only empire-pool fallback path. Design.md explicitly warns this must be set explicitly per engine. Consumption file sets it correctly.

3. **MAJOR: Fleet-to-fleet transfer with `amount>0` untested** — `_execute_fleet_transfer` integration tests all use `amount=0`. No test for actual cargo movement between fleets.

4. **MAJOR: Resource unloading untested** — Only resource loading tested. `_execute_unload` (fleet→planet resource transfer) has zero coverage.

5. **MAJOR: Passenger `amount=0` ("load all") path untested** — Only `amount>0` tested for passenger loading.

6. **MAJOR: Superweapon dispatch untested** — `execute_action_order` superweapon handler dict (6 order types) has zero characterization in PROJ-333 files.

7. **MAJOR: `apply_movements()` accumulator loop untested** — Singular `apply_movement` well-tested, but the plural loop iterating `move_queue` has no test.

### Observation coverage: 13/15 pinned. 2 with weak assertions (findings above). Vacuous tests: none. Test names: all descriptive.

---

## PROJ-341 (residual engines)

### Verified: OBS-003 fuel drain correctly pinned

Production `environmental_hazard_engine.py:140-143` applies fuel drain per-ship without division by ship count. Test `test_process_environmental_tick_drains_fuel_per_ship_without_dividing` (line 184) creates 3 ships, asserts total drain = 9.0 (3 × 3.0). Correctly pins the production bug.

### Verified: OBS-002 (negative damage), OBS-005 (legacy string)

OBS-002 pinned: single negative-damage row produces zero events. OBS-005 pinned: legacy plain-string target bypasses sector-hex validation.

### MAJOR findings

1. **F-001 (MAJOR): D-003 violation** — Fleet and Empire are mocked (bare `MagicMock()`) in `test_environmental_hazard_engine.py` and `test_superweapon_order_processor_gaps.py`. D-003 explicitly says "Use real Fleet, Empire." `test_action_execution_engine_gaps.py` follows D-003 correctly.

2. **F-002 (MAJOR): `_drain_fuel_from_ship` zero-fuel branch untested** — Only the `drain_amount > 0` path tested. When ship has zero fuel, the guard at line 216 returns 0.0 without calling `consume_resource` — this path is untested.

3. **F-003 (MAJOR): PROJ-336 D-008 doc incorrect and uncorrected** — `PROJ-336/decisions.md` D-008 still says "An order with amount=-50, direction='load' would reduce projected." Production behavior (pinned at `test_fleet_cargo_projector.py:138`) actually treats negative as fill-to-capacity sentinel. Documentation contradicts pinned behavior. Needs correction.

### Missing surfaces: Mostly adequate. All 7 observations (OBS-001 through OBS-007) pinned. All stabilizer-blocking cancellation paths tested. Far-end geometry (OBS-004) pinned. Legacy compat paths pinned.

---

## Cross-Project Item 8: PROJ-336 D-008 Doc Inconsistency

**MAJOR:** `Projects/active_projects/PROJ-336/decisions.md` line 15 (D-008) still documents incorrect behavior for `FleetCargoProjector.get_projected_cargo` with negative amounts. The characterization test at `tests/unit/strategy/services/test_fleet_cargo_projector.py:138` correctly pins that negative load fills to capacity (not reduces). D-008 must be corrected to match actual production behavior.

---

## Per-Project Verdict

| Project | Verdict | Key Issue |
|---------|---------|-----------|
| PROJ-331 | **PASS** — Adequate | All 3 observations pinned; 2 minor stacking concerns |
| PROJ-332 | **PASS** — Adequate | 5 lazy-property default paths + factory untested (straightforward to fill) |
| PROJ-333 | **FAIL** — Not adequate | 5 critical gaps: weak assertion, multi-match untested, 3 methods zero coverage, fleet context zero coverage |
| PROJ-341 | **PASS** — Adequate | All 7 observations pinned; 3 MAJOR are process/doc issues rather than behavioral gaps |
