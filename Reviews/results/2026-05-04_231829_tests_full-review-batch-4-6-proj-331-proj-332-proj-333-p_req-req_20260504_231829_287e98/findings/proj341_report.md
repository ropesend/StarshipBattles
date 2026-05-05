# PROJ-341 Test Quality Review — Findings Report

**Reviewer:** OpenCode (fresh-eyes review)
**Date:** 2026-05-04
**Files reviewed:**
- `tests/unit/strategy/engine/test_environmental_hazard_engine.py` (409 LOC, 18 tests)
- `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py` (594 LOC, 16 tests)
- `tests/unit/strategy/engine/test_action_execution_engine_gaps.py` (306 LOC, 10 tests)
- Production: `environmental_hazard_engine.py`, `superweapon_order_processor.py`, `action_execution_engine.py`
- Docs: `PROJ-341/design.md`, `PROJ-341/decisions.md`, `PROJ-336/decisions.md`

---

## 1. Behavior Accuracy — OBS-003 Fuel Drain Verification (CRITICAL)

**Verdict: PASS** — No issues found.

### OBS-003 (per-ship fuel drain without division)
- **Production** `environmental_hazard_engine.py:140-143`: fuel drain loop applies `fuel_drain_per_tick` to each ship directly, with NO division by `len(combat_ships)`. Contrast with damage at lines 135-138 which divides by ship count.
- **Test** `test_process_environmental_tick_drains_fuel_per_ship_without_dividing` (line 184): Creates 3 ships, `fuel_drain_per_tick=3.0`, asserts total `fuel_drained == 9.0` (3×3.0). Each ship's `consume_resource("fuel", 3.0)` verified individually.
- **Result:** Test correctly exercises the production path. Total drain scales with ship count — each ship pays full drain.

### OBS-002 (negative damage produces zero events)
- **Test** `test_process_environmental_tick_returns_no_event_when_aggregate_values_are_zero` (line 286): Single negative-damage row `-50.0` passes the empty-list filter but hits `damage_per_turn <= 0 and fuel_per_turn <= 0` guard at line 122. Returns `[]`, ship HP untouched.
- **Result:** Correctly pins negative-damage avoidance. No healing, no event, no error.

### OBS-005 (legacy plain-string target for close_warp_point)
- **Test** `test_close_warp_point_accepts_legacy_string_target_without_sector_check` (line 354): `Order(OrderType.CLOSE_WARP_POINT, target="Beta")` — plain string. Asserts warp link removed, no sector-hex check applies.
- **Result:** Correctly pins legacy back-compat path.

---

## 2. Vacuous Tests (CRITICAL)

**Verdict: PASS** — No vacuous tests found.

- All three test files instantiate real engine classes (`EnvironmentalHazardEngine()`, `SuperweaponOrderProcessor()`, `ActionExecutionEngine(proc)`). No engine-under-test is ever mocked.
- All superweapon tests use real `Order(OrderType.X, ...)` with real `OrderType` enum values.
- No test asserts only `mock.called == True` without verifying arguments or state changes.
- Assertions check concrete outcomes: `fuel_drained` totals, `current_hp` values, `success` flags, `result.message` contents, `pop_order` call counts, warp-point list contents, Dyson planet atmosphere dict values, `execution_progress` values, etc.

---

## 3. Mocking Discipline (MAJOR)

**Verdict: 1 MAJOR finding**

### F-001 — D-003 violation: Fleet and Empire mocked in two of three test files

- **Severity:** MAJOR
- **Files:** `test_environmental_hazard_engine.py`, `test_superweapon_order_processor_gaps.py`
- **Decision:** PROJ-341 D-003 explicitly states: *"Use real `Order`, `HexCoord`, `WarpPoint`, `Fleet`, `Empire`"* and *"Mock the galaxy / system / collector / SystemDestroyer / SuperweaponValidator at module level"*
- **Actual:**
  - `test_environmental_hazard_engine.py`: `_make_fleet()` and `_make_empire()` both return bare `MagicMock()` — no `spec`, no real class. Fleet and Empire are fully mocked.
  - `test_superweapon_order_processor_gaps.py`: `mock_fleet` uses `MagicMock(spec=Fleet)`, `empire` is bare `MagicMock()` (no spec). Both mocked.
  - `test_action_execution_engine_gaps.py`: Uses real `Fleet(fleet_id=..., ...)` and `Empire(empire_id=..., ...)`. **This file follows D-003 correctly.**
- **Practical impact:** The env hazard engine accesses only duck-typed attributes (`fleet.id`, `fleet.location`, `fleet.get_combat_capable_ships()`) so mock vs. real doesn't miss behavior. The superweapon processor interacts more deeply with Fleet (`.ships`, `.remove_ship()`, `.pop_order()`, `.orders`) — a real Fleet would validate the API contract. Using spec-MagicMock provides partial protection but won't catch API signature changes.
- **Recommendation:** Either upgrade the two files to use real `Fleet`/`Empire` instances (consistent with D-003 and with the action-execution gap-fill file), or update D-003 to document the per-file exception and why it's acceptable.

### D-004 and D-005 adherence

- **D-004 (stabilizer patching):** `FBS_PATH = "game.strategy.services.stabilizer_registry.find_blocking_stabilizer"` is the correct import site. All 5 stabilizer-blocking cancellation tests patch this path. ✓
- **D-005 (collect_sector_effects patching):** `COLLECT_PATH = "game.strategy.services.system_effects_collector.collect_sector_effects"` matches the deferred import inside `process_environmental_tick`. ✓
- **EnvironmentalHazardEngine never mocked in its own test file:** Confirmed — all tests use `engine = EnvironmentalHazardEngine()`. ✓

---

## 4. Test Names (MAJOR)

**Verdict: PASS** — All 44 test names across the three files are descriptive and specific.

Spot-checked every test name. Examples of good naming:
- `test_process_environmental_tick_drains_fuel_per_ship_without_dividing` — states the WHAT and the HOW
- `test_implode_planet_cancels_when_stabilizer_blocks` — states the trigger and expected outcome
- `test_process_action_ticks_handles_multiple_consumed_fleets_in_same_empire` — states the scenario

No `test_basic`, `test_default`, `test_simple`, `test_1`, or vague names found.

---

## 5. Missing Surfaces (MAJOR)

**Verdict: 1 MAJOR gap, 4 MINOR gaps noted but not elevated to MAJOR**

### F-002 — `_drain_fuel_from_ship` zero-fuel branch untested

- **Severity:** MAJOR
- **File:** `tests/unit/strategy/engine/test_environmental_hazard_engine.py`
- **Production code:** `environmental_hazard_engine.py:203-219`. The `drain_amount > 0` guard at line 216 is untested. When `ship.get_current_resource("fuel")` returns `0`, `drain_amount = min(amount, 0) = 0`, `consume_resource` is NOT called, and `0.0` is returned.
- **Current test:** `test_drain_fuel_from_ship_caps_at_current_fuel` (line 402) only tests the `drain_amount > 0` branch (fuel=5.0, amount=20.0 → drains 5.0).
- **Recommendation:** Add a test where ship fuel is 0, verify `drain_amount == 0.0` and `consume_resource` is NOT called.

### Surfaces adequately covered

| Surface | Coverage | Notes |
|---------|----------|-------|
| `_validate_tick_inputs` (both engines) | ✓ | Raise + no-raise paths tested; validates before mutation |
| `_apply_damage_to_ship` (all branches) | ✓ | Normal damage, lethal damage, damage=0 branch (OBS-001) |
| `process_environmental_tick` (all skip branches) | ✓ | No galaxy, no system, no effects, zero aggregates, no combat ships |
| `process_implode_planet` (stabilizer cancel) | ✓ | |
| `process_stellerate_star` (stabilizer cancel) | ✓ | Also asserts `fleet_consumed=False` on cancel; collector/destroy not called |
| `process_open_warp_point` (stabilizer cancel + far-end geometry) | ✓ | OBS-004 axial and diagonal cases |
| `process_close_warp_point` (stabilizer cancel + legacy + preconditions) | ✓ | OBS-005 legacy string; empty destination_id; fleet-not-at-system |
| `process_create_dyson_sphere` (stabilizer cancel + race_config fallback) | ✓ | Default atmosphere values pinned |
| `process_self_destruct` (all branches) | ✓ | Empty fleet removal, non-empty preserve, empty target list, non-list target |
| `_get_reference_planet` | ✓ | OBS-006 first-planet semantics |
| `_finalize_superweapon` | ✓ | Indirectly through all 5 non-self-destruct process_* methods |
| `_check_blocking_stabilizer` | ✓ | Indirectly through all 5 cancellation tests |
| `action_execution_engine` completion/in-progress | ✓ | OBS-007: engine does NOT pop orders |
| `action_execution_engine` kwarg threading | ✓ | `component_registry` and `all_empires` forwarded correctly |
| `action_execution_engine` iteration safety | ✓ | 3-fleet consumption mid-loop |

### Known MINOR gaps (not elevated to MAJOR — out-of-scope branches)

1. `_process_fleet_action_tick` skip branches: `fleet.speed <= 0`, `tick % interval != 0`, `order is None`, `order.type in MOVEMENT_ORDER_TYPES`, `order.type == BUILD`, `order.type not in ACTION_ORDER_TYPES`. These are intentionally handled by other engines (FleetMovementEngine, ProductionEngine) or are guard clauses. Testing them here would be testing those engines' responsibilities.
2. Ship-consumption vs. preserve paths in the *successful* (non-cancellation) execution path for IMPLODE_PLANET, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE. These are in the original `test_superweapon_order_processor.py` (27 existing tests), out of scope for the gap-fill file per D-002.

---

## 6. Cross-Reference: PROJ-336 D-008 Doc Inconsistency (MAJOR)

**Verdict: 1 MAJOR finding**

### F-003 — PROJ-336 decisions.md D-008 is incorrect and uncorrected

- **Severity:** MAJOR
- **File:** `Projects/active_projects/PROJ-336/decisions.md` line 15 (D-008)
- **What D-008 says:** *"An order with `amount=-50, direction='load'` would compute `delta=-50` and reduce `projected`."*
- **What production actually does (pinned by test):** `test_fleet_cargo_projector.py:138` — `test_load_with_negative_amount_fills_to_capacity_like_zero` — negative amounts are treated as auto-fill/auto-drain sentinels. A negative load FILLS to capacity, it does NOT reduce. The test's own docstring at line 131-134 explicitly states: *"D-008 in the project's decisions.md documented this as 'negative load reduces projected', which was INCORRECT — these tests pin the actual behavior."*
- **Impact:** A future developer reading D-008 would incorrectly believe negative amounts reduce cargo projection. The decisions document and the actual behavior are in direct contradiction.
- **Recommendation:** Correct PROJ-336 `decisions.md` D-008 to match actual production behavior (negative amounts treated as zero/fill-to-capacity sentinels, not as arithmetic deltas). Add a note that the test at `test_fleet_cargo_projector.py:138` pins the corrected behavior.

---

## Overall Verdict

| Category | Count |
|----------|-------|
| CRITICAL | **0** |
| MAJOR    | **3** |
| MINOR    | 4 (noted but not elevated) |

**Coverage:** Adequate for characterization purposes. The three test files collectively pin the key observable behaviors defined in PROJ-341's scope, including all observation-candidates (OBS-001 through OBS-007), all stabilizer-blocking cancellation paths, far-end geometry math, legacy back-compat paths, and engine responsibility boundaries. The 3 MAJOR findings relate to process/documentation adherence rather than behavioral gaps in the testing.

### Finding summary

| ID | Severity | File(s) | Description |
|----|----------|---------|-------------|
| F-001 | MAJOR | `test_environmental_hazard_engine.py`, `test_superweapon_order_processor_gaps.py` | D-003 violation: Fleet and Empire mocked instead of real; contradicts project decision |
| F-002 | MAJOR | `test_environmental_hazard_engine.py` | `_drain_fuel_from_ship` zero-fuel branch (`drain_amount <= 0`) untested |
| F-003 | MAJOR | `Projects/active_projects/PROJ-336/decisions.md` | D-008 documented behavior contradicts actual production behavior pinned by characterization test; doc uncorrected |
