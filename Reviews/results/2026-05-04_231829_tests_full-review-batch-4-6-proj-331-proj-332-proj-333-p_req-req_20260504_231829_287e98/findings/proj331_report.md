# PROJ-331 Test Quality Review Report

**Reviewer:** OpenCode
**Date:** 2026-05-04
**Scope:** BattleState + BattleController + ConflictResolutionEngine characterization tests

---

## 1. Behavior Accuracy — OBSERVATION-A/B/C Pinning (CRITICAL)

All three observations are correctly pinned by tests. Commit `5364c3f62` (MAJ-002 / MAJ-003) landed the OBSERVATION-C and OBSERVATION-B pinning that was previously only documented.

### OBSERVATION-A: broad `except Exception` in `_collect_team_modifiers`

**Production:** `game/strategy/engine/conflict_resolution_engine.py:552` — `except Exception as e:  # Intentional broad catch: external collector`

**Test:** `test_collect_team_modifiers_returns_none_and_logs_when_collector_raises`
**File:line:** `tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py:251`

**Verification:** The test creates a real `ConflictResolutionEngine` instance (via `_make_engine()`), sets `engine._galaxy` and `engine._empires`, builds fleet mocks, patches `collect_combat_modifiers` to raise `RuntimeError("boom")`, calls `engine._collect_team_modifiers(fleets_by_empire, empire_order)`, and asserts:
- `result is None` (the swallow returns None)
- Warning logged with "Failed to collect combat modifiers" in the message

This exercises the real production code path through `_collect_team_modifiers` with a real ConflictResolutionEngine — only the external `collect_combat_modifiers` is patched to trigger the except branch. **Correctly pinned.**

### OBSERVATION-B: `BattleController.load_state` defaults boundary to `UnboundedRegion`

**Production:** `game/simulation/battle_controller.py:639` — `self._retreat_manager = RetreatManager(boundary=UnboundedRegion())`

**Test:** `test_load_state_restores_battle`
**File:line:** `tests/unit/simulation/battle_controller/test_state.py:42`

**Verification:** The test creates a real controller, builds a mock `BattleState`, sets `restore_config_from_state.return_value = BattleConfig()` (which has `boundary=None`), calls `controller.load_state(mock_state)`, and asserts:
- `result.success is True`
- `isinstance(controller._retreat_manager.boundary, UnboundedRegion)` with the message "PROJ-331 OBSERVATION-B: load_state must default boundary to UnboundedRegion when the restored config has no boundary set."

The test exercises the real `load_state` method. The `state_manager` is mocked, but the boundary fallback path (line 639) is directly exercised by the controller logic. **Correctly pinned.**

### OBSERVATION-C: `_extract_outcome_on_battle_end` swallow when `on_battle_ended` raises

**Production:** `game/simulation/battle_controller.py:445` — `except Exception:  # Intentional broad catch: capture must not crash visual-mode battle end`

**Test:** `test_outcome_is_set_when_capture_sink_raises`
**File:line:** `tests/unit/simulation/battle_controller/test_state.py:292`

**Verification:** The test creates a real controller, sets `controller._spec = Mock()`, patches `extract_outcome` to return a sentinel, patches `get_default_capture_sink` to return a mock whose `on_battle_ended` raises `RuntimeError("sink broke")`, calls `controller._extract_outcome_on_battle_end()`, and asserts:
- `controller._outcome is sentinel_outcome` (the outcome is still set despite the exception)
- No exception propagates out

The test exercises the real `_extract_outcome_on_battle_end` method. `extract_outcome` and the capture sink are patched to control behavior, but the controller's try/except at line 445 is exercised directly. **Correctly pinned.**

---

## 2. Vacuous Tests (CRITICAL)

**No vacuous tests found.** Every test in all four files instantiates at least one real production class (`ComponentState`, `ShipState`, `ProjectileState`, `BattleState`, `BattleResults`, `BattleController`, or `ConflictResolutionEngine`) and exercises real production methods. Input objects (Ship, Component, Projectile, Fleet, Empire, Galaxy) are frequently mocked, but per decisions D-003/D-004/D-005 this is by design — constructing real Ship/Engine/Fleet objects requires heavy dependency chains beyond the unit-test boundary.

Tests that patch the `Ship` or `Projectile` constructor still exercise the real `to_ship()`/`to_projectile()` method bodies. No tests assign an attribute to a mock and then assert it equals that same attribute. No tests rely solely on `mock.called == True` without inspecting arguments.

---

## 3. Mocking Discipline (MAJOR)

### MAJOR: `BattleState` class is fully mocked in controller-level tests

**File:line:** `tests/unit/simulation/battle_controller/test_state.py:33,131,157`
**Tests:** `test_save_state_captures_state`, `test_get_results_returns_battle_results`, `test_get_results_categorizes_escaped_ships`

**Description:** These tests patch `game.simulation.managers.battle_state_manager.BattleState` and use `MockState.capture_from_engine.return_value = mock_state`. The controller's own `save_state()` / `get_results()` methods call `BattleState.capture_from_engine()` which is replaced by the mock. This means the controller's integration with `BattleState.capture_from_engine` is not tested — only the controller wrapper logic is.

**Recommendation:** Consider adding at least one test where the real `BattleState.capture_from_engine` is exercised (mocking only the engine, not the state class itself). The `TestBattleStateCaptureFromEngine` class in `test_battle_state_live_object_bridges.py` covers `capture_from_engine` independently, so this is a stacking concern, not a gap. Not blocking.

### D-003 / D-004 / D-005 compliance: Satisfactory

`to_ship` / `from_ship` tests use MagicMock for Ship (per D-003), `capture_from_engine` uses mock engines (per D-004), and `start_from_spec` patches `start_engine_from_spec` (per D-005). All three design decisions are followed. The `TestShipStateToShip` class patches the Ship constructor but exercises the real `to_ship()` logic including component restoration, modifier ordering, layer resolution, and unknown-layer warning.

---

## 4. Test Names (MAJOR)

Spot-checked all test names across the four files. Four vague names found — all in `test_state.py`, which mostly contains pre-existing tests (not PROJ-331 new work):

| Test name | File:line | Issue |
|-----------|-----------|-------|
| `test_save_state_captures_state` | `test_state.py:21` | Doesn't describe what aspect of state capture is verified |
| `test_load_state_restores_battle` | `test_state.py:42` | Too broad — "restores battle" could mean many things |
| `test_load_state_handles_error` | `test_state.py:99` | Doesn't say what error or how it's handled |
| `test_get_results_returns_battle_results` | `test_state.py:119` | Tautological — of course `get_results` returns `BattleResults` |

**Recommendation:** Rename for clarity if these files are revisited. Not blocking — the docstrings partially compensate.

All PROJ-331 new test names (in `test_start_from_spec.py` and `test_logging_and_lookups.py`) are descriptive.

---

## 5. Missing Surfaces (MAJOR)

### Production method coverage audit

**battle_state.py:** 22 methods. All query methods (`get_ships_by_team`, `get_alive_ships`, `get_surviving_ships`, `get_escaped_ships`, `get_destroyed_ships`) are tested either in these files or in the pre-existing `test_battle_state_serialization.py`. `to_dict`/`from_dict`/`to_json`/`from_json` are covered in `test_battle_state_serialization.py` (1395 LOC). `from_ship`/`to_ship`/`from_projectile`/`to_projectile`/`from_component`/`capture_from_engine` are all covered in `test_battle_state_live_object_bridges.py`. **No gaps in the reviewed scope.**

**battle_controller.py:** 31 methods. These test files cover `save_state`, `load_state`, `start_from_spec`, `_extract_outcome_on_battle_end`, `get_results`, and `_require_registries_for_state_restore`. The remaining methods (`add_ships`, `update`, `run_ticks`, `request_retreat`, etc.) are covered in sibling test files: `test_mechanics.py`, `test_execution.py`, `test_utilities.py`, `test_outcome_emission.py`, `test_initialization.py`. **No gaps in the full battle_controller test suite.**

**conflict_resolution_engine.py:** 10 methods. These test files cover `_validate_tick_inputs`, `resolve_all_conflicts` (tick=None shortcut), `_log_combat_result` (4 tests), `_lookup_environmental_effects` (2 tests), `_collect_team_modifiers` (1 test), and `_resolve_combat_at_hex` (ordering + shortcuts). `_should_trigger_combat_for_fleet` is covered in `tests/unit/strategy/engine/test_conflict_round_budget.py`. `_generate_battle_seed` is covered in `tests/unit/strategy/conflict_resolution/test_core.py`. `_resolve_conflicts` is indirectly exercised through `_resolve_combat_at_hex` tests. **No gaps in the reviewed scope.**

### MAJOR: No end-to-end resolve_all_conflicts test with tick != None

**Description:** The only `resolve_all_conflicts` test that exercises the full path (`test_validate_tick_inputs_passes_when_all_fleets_have_locations`, line 99) has a single empire with one fleet at a hex, which means `_resolve_conflicts` will find no opposing empire and skip combat. There is no test in this file that exercises the full chain: `resolve_all_conflicts(tick=20)` → `_resolve_conflicts` → `_should_trigger_combat_for_fleet` → `_resolve_combat_at_hex` → resolver call → `_log_combat_result` → fleet destruction tracking.

The individual components are tested in isolation (`_resolve_combat_at_hex` ordering, shortcuts, `_log_combat_result` emission, etc.), but the integration path that stitches them together is not covered in this file. The `test_core.py` file may have this, but this review is scoped to the PROJ-331 characterization set.

**Recommendation:** Consider a single integration-style test in a follow-up that feeds `resolve_all_conflicts` a multi-empire setup at the same hex with `tick != None` and verifies the resolver is called and `ConflictResult` reflects destroyed fleets. Not blocking — the decomposed coverage is strong.

---

## 6. OBSERVATION Docs Sync (MAJOR)

### Verification: All three observations documented

| Observation | decisions.md | Test pinned |
|-------------|-------------|-------------|
| OBSERVATION-A | Line 15: "broad except Exception in _collect_team_modifiers (line 552)" | `test_logging_and_lookups.py:251` — `test_collect_team_modifiers_returns_none_and_logs_when_collector_raises` |
| OBSERVATION-B | Line 16: "BattleController.load_state defaults boundary to UnboundedRegion" | `test_state.py:42` — `test_load_state_restores_battle` (MAJ-003 fix) |
| OBSERVATION-C | Line 17: "_extract_outcome_on_battle_end replay-id capture failure swallows broadly" | `test_state.py:292` — `test_outcome_is_set_when_capture_sink_raises` (MAJ-002 fix) |

**All three observations are both documented in `decisions.md` and pinned by tests.** No undocumented observations found in the production code within the reviewed scope.

### Commit 5364c3f62 verification

```
5364c3f62 test(331+334+335): apply Wave 1 review-1 MAJOR fixes (4 items)
```

This commit:
- **MAJ-002:** Added the OBSERVATION-C pinning test (`test_outcome_is_set_when_capture_sink_raises`) to `test_state.py`
- **MAJ-003:** Added the OBSERVATION-B boundary assertion to `test_load_state_restores_battle` in `test_state.py`
- **MAJ-004:** Unrelated (PROJ-335, order types)
- **MAJ-001:** Unrelated (PROJ-334, galaxy generator)

All PROJ-331 MAJOR fixes from the original review-1 are applied. Verified by `git show 5364c3f62 --stat`.

---

## Verdict

**Total findings:** 0 CRITICAL, 2 MAJOR

| ID | Severity | Category | Summary |
|----|----------|----------|---------|
| F1 | MAJOR | Mocking | `BattleState` class fully mocked in controller-level state save/get_results tests |
| F2 | MAJOR | Coverage | No end-to-end `resolve_all_conflicts(tick != None)` integration test in the PROJ-331 characterization set |

**Assessment:** The PROJ-331 characterization test suite is well-structured and achieves its goals. All three observations (A/B/C) are correctly pinned by tests that exercise real production code paths. The mocking strategy follows the documented design decisions (D-003 through D-005). Test names are descriptive (with 4 pre-existing exceptions in `test_state.py`). No vacuuous tests were found. Production method coverage is comprehensive both within the reviewed files and across the broader test suite. The two MAJOR findings are stacking/scope concerns, not blocking gaps.

**Verdict: Test coverage is adequate for PROJ-331 characterization goals.**
