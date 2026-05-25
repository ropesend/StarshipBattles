# Phase 5: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-495 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address verified in-scope findings from the Codex mid-project review. See `findings/audit_verification.md` for the full verification table and `AgentCoordination/Scratchpad/Consult/20260523T152252Z_audit-PROJ-495/response.md` for the raw audit.

---

## Tasks

### Task 5.1: T3.3 retry — parametrize 3 single-attribute squadron roundtrips
**File:** `tests/unit/strategy/data/test_squadron_characterization.py`
**Tests:** `pytest tests/unit/strategy/data/test_squadron_characterization.py`

PROJ-495 Phase 3 dropped T3.3 entirely on the grounds that "each [of 5 round-trips] asserts on a different attribute". Codex audit verified that 3 of the 5 share the *identical structural shape*: `Squadron(name="Alpha", node_id="id-1", <kwarg>=value); restored = Squadron.from_dict(original.to_dict()); assert restored.<attr> == value`. Those 3 are: `test_round_trip_with_battle_role_enum` (lines 125-134, BattleRole.VANGUARD), `test_round_trip_preserves_spatial_behavior_when_set` (lines 149-160, spatial_behavior + spatial_behavior_params), `test_round_trip_preserves_flagship_id` (lines 162-171, flagship_id). The combat_policy case (lines 136-147) has nested-attribute assertions (`policy.targeting`, `.movement`, `.retreat`) and stays distinct.

- [x] Parametrize the 3 single-attribute roundtrips into one `test_round_trip_preserves_single_attribute` on `(squadron_kwargs, expected_attrs_dict)` where `squadron_kwargs` is the additional kwargs passed to `Squadron(...)` and `expected_attrs_dict` maps `attr_name -> expected_value`. Use `pytest.param(..., id='battle_role')` / `'spatial_behavior'` / `'flagship_id'` for readable IDs.
- [x] For the spatial_behavior case, the parametrize value can include BOTH `spatial_behavior` and `spatial_behavior_params` since both are kwargs of the same input case.
- [x] Keep `test_round_trip_with_combat_policy` (lines 136-147) distinct — it has multi-level nested-attribute assertions (`restored.policy.targeting`, `.movement`, `.retreat`) and policy construction is a separate concern.
- [x] Keep `test_round_trip_with_default_fields` (the test immediately above at ~lines 110-124, which asserts spatial_behavior is None and spatial_behavior_params is {}) distinct — that's a default-fields contract, not a preserves-this-kwarg case.
- [x] Update `Projects/active_projects/PROJ-495/phase_3_checklist.md` Task 3.3 note to read: "3 of 5 single-attribute roundtrips parametrized (Phase 5); combat_policy (multi-level nested asserts) and default-fields (different contract) kept distinct."
- [x] Verify: tests pass; expected method count -2 (3 tests merged into 1 parametrize).

### Task 5.2: T2.12 retry — eliminate 7 missed-caller MagicMock empire stubs
**File:** `tests/unit/strategy/engine/test_resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

PROJ-495 Phase 2 said T2.12 was "absorbed by PROJ-479 DUP-005" and stopped at importing the canonical helper for the colony-side tests. The fleet-resupply test cluster at lines 560-749 still hand-rolls 7 empire stubs as `empire = MagicMock(); empire.fleets = [fleet]`. Codex audit verified all 7 sites are mechanically interchangeable with `make_mock_empire(fleets=...)`.

The 7 sites (line numbers approximate, re-grep before editing):
- `test_resupply_engine.py:560-561` (test_owner_fleet_with_planet_fuel-style success path)
- `test_resupply_engine.py:589-590` (test_fleet_not_at_planet_no_fuel)
- `test_resupply_engine.py:621-624` (test_owner_fleet_priority_over_others — TWO empires, both stubbed inline)
- `test_resupply_engine.py:666-667` (test_fuel_distributed_to_equalize_range)
- `test_resupply_engine.py:713-714` (test_tanker_ships_partially_fueled)
- `test_resupply_engine.py:743-744` (test_facility_with_no_fuel_no_transfer)

The file already imports `make_mock_empire as _make_mock_empire_canonical` at line 97. The local wrapper `_make_empire(colonies=None)` at line 100 sets `empire_id=0`. The cleanest fix is to extend that wrapper to accept fleets too:

```python
def _make_empire(colonies=None, fleets=None):
    return _make_mock_empire_canonical(empire_id=0, colonies=colonies, fleets=fleets)
```

- [x] Extend the existing local `_make_empire` wrapper at `tests/unit/strategy/engine/test_resupply_engine.py:100-101` to accept `fleets=None` and forward to the canonical helper.
- [x] Replace each of the 7 `empire = MagicMock(); empire.fleets = [fleet]` patterns (or `empire.fleets = [...]`) with `empire = _make_empire(fleets=[fleet])` (or equivalent list). For the two-empire site at lines 621-624, replace both inline stubs.
- [x] Confirm no `empire.<other_attr>` is set on those mocks after the stub line — if so, preserve the additional attribute via either a follow-up `setattr` or a kwarg through `**overrides` (the canonical helper accepts `**overrides`).
- [x] Update `Projects/active_projects/PROJ-495/phase_2_checklist.md` Task 2.12 (or wherever T2.12 lives in the checklist) note to read: "Colony-side helper wrapping landed in Phase 2 (PROJ-479 DUP-005); fleet-side cleanup landed in Phase 5 — 7 ad-hoc MagicMock empire stubs replaced with `_make_empire(fleets=...)`."
- [x] Verify: tests pass; LOC delta ≈ -7 (one line per site collapsed).

### Task 5.3: Log F3 discovered issue (orphan helper)
**Type:** Documentation / discovered-issue log
**Note:** This is NOT a code change — it's a notebook entry for the user to triage.

The helper `_assert_roundtrip_property` at `tests/conftest.py:380-392` was introduced by PROJ-479 (DUP-003) but has zero call sites in the live tree. PROJ-495's T3.28 chose inline parametrize rather than adopting the helper, and Codex agreed that decision was correct (the helper has no comparator hook and the ship_serialization color comparisons need `tuple(...)` normalization). The orphan helper is now stale debt against PROJ-479, not PROJ-495.

- [x] Run `/claude-di-log` (or directly append to `AgentCoordination/discovered_issues/log.jsonl`) with a one-line entry naming `tests/conftest.py:_assert_roundtrip_property` as an orphan helper introduced by PROJ-479 DUP-003 with zero call sites; suggest either deleting it OR redesigning the API with a comparator hook so existing inline parametrize sites (e.g., the new `tests/unit/simulation/entities/test_ship_serialization.py:337-355`) can adopt it. **Logged as `DI-2026-05-23-007`.**
- [x] Cross-reference: PROJ-479 DUP-003, PROJ-495 Phase 5 audit, consult leaf `AgentCoordination/Scratchpad/Consult/20260523T152252Z_audit-PROJ-495/`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Phases 0-5 Complete" (no Phase 6 planned)
