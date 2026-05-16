# Phase 1: Delete remaining save-format fallbacks + canonical error type

**Status:** Complete
**Objective:** Remove the two surviving save-format compat surfaces and normalize the missing-`components` error to `PersistenceException`. Replace legacy-path tests with negative regression tests.

---

## Tasks

### Task 1.1: Read all four files + confirm current shapes [Simple]
**File:** see manifest

- [x] Read `ship_instance_serializer.py` around line 106 (the `resource_levels` fallback) and around line 87,124 (`require_keys` call + `data['components']` access).
- [x] Read `battle_setup_state.py:117-130` (`BattleSetupSide.from_dict`).
- [x] Read existing tests in both test modules to identify which ones encode the legacy paths.
- [x] Locate `require_keys()` and `PersistenceException` so you have the canonical error route.
- [x] Decide whether the canonical save-format requires `consumable_levels` to be present, or whether absent → `{}` is the new contract. Document in `decisions.md`.

**Notes:** `require_keys` lives in `game/core/validation_helpers.py`; `PersistenceException` in `game/core/exceptions.py`. Decision (see decisions.md): `consumable_levels` absent → `{}`; missing `components` raises via `require_keys`; both `*_complex_toggles` keys required via `require_keys`.

### Task 1.2: TDD — write failing negative regression tests [Medium]
**File:** `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py`, `tests/unit/ui/screens/test_battle_setup_state.py`

- [x] Add a test asserting `ShipInstanceSerializer.from_dict({...without 'components'...})` raises `PersistenceException`, not raw `KeyError`.
- [x] Add a test asserting that a payload containing only legacy `resource_levels` (no `consumable_levels`) raises a meaningful error or returns the documented new shape — choose based on Task 1.1 decision.
- [x] Add a test asserting `BattleSetupSide.from_dict({...without 'system_complex_toggles'...})` raises (after the tolerance is deleted).
- [x] Run all three tests against unmodified production — they should fail (currently the legacy paths are tolerated).

**Notes:** Confirmed RED: 4 negative tests failed against unmodified production (missing-components raised raw `KeyError`; missing-toggles silently defaulted; legacy `resource_levels` was silently mapped). Positive `test_canonical_consumable_levels_round_trip` already passed (good).

### Task 1.3: Delete the `resource_levels` fallback + route `components` through `require_keys()` [Simple]
**File:** `game/strategy/data/ship_instance_serializer.py`

- [x] Change line 106 from `data.get('consumable_levels', data.get('resource_levels', {}))` to `data.get('consumable_levels', {})` (or per Task 1.1 decision).
- [x] Add `components` to the `require_keys(...)` call so missing `components` raises `PersistenceException` rather than raw `KeyError` on later access.
- [x] Run focused tests — passing tests should still pass; new negative tests should now pass.

**Notes:** `require_keys` call at line 87 expanded to include `'components'`. Line 106 reduced to `data.get('consumable_levels', {})`.

### Task 1.4: Delete the `*_complex_toggles` tolerance [Simple]
**File:** `game/ui/screens/battle_setup_state.py:117-130`

- [x] Remove the legacy-tolerance branch and the docstring framing.
- [x] Update the new-format constructor to require both keys (or call `require_keys`).
- [x] Run focused tests — new negative test should pass; legacy-path test should now fail.

**Notes:** `require_keys` call added at the top of `BattleSetupSide.from_dict`; `*_complex_toggles` are now read via direct `data[key]` indexing (require_keys has already validated presence). Docstring rewritten to drop legacy framing.

### Task 1.5: Delete legacy-path tests [Simple]
**File:** `tests/unit/ui/screens/test_battle_setup_state.py:223-235` (the "Legacy saves ... Don't crash" test) and any equivalent serializer test that asserts legacy shapes succeed.

- [x] Delete those test functions outright. Do not "soften" them — Rule 3 says old saves are disposable, so the tests for legacy success are no longer valid behavior to preserve.
- [x] Run the test modules — should pass.

**Notes:** Deleted: `test_battle_setup_state.py::TestBattleSetupSideComplexToggles::test_from_dict_defaults_missing_toggle_fields_to_empty` (the "Legacy saves... Don't crash" test, lines 223-235). The serializer test module had no equivalent legacy-shape test asserting silent success — only the existing `test_raises_on_missing_required_keys` test, which remains valid (missing `instance_id` etc. still raises). The `resource_levels` rename had no dedicated positive test in this module, so nothing to delete there. Both legacy paths are now blocked by negative tests added in Task 1.2.

### Task 1.6: Run round-trip + battle-setup integration suites [Simple]
**Tests:** `pytest tests/integration/save_load/test_roundtrip_ships.py tests/integration/ui/test_battle_setup_three_sides.py -v`

- [x] Both pass.
- [x] If anything fails because it relied on legacy shapes, fix the test to use the canonical shape.

**Notes:** All 15 integration tests pass with no fixture changes. Production callers (`replay_ship_builder`, `BattleSetupState.from_dict`) consume `to_dict` output which always emits canonical shapes.

### Task 1.7: Closeout
- [x] Update Phase 1 status to `Complete`
- [x] Update plan.md Quick Status + Current State
- [x] Update `Projects/projects_index.md` row for PROJ-404 to `Complete`
- [x] Validators pass
- [x] Commit `PROJ-404 phase 1: delete save-format compat surfaces + canonical PersistenceException`

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Status at top of this file is `Complete`
- [x] plan.md updated
- [x] Focused + integration suites pass
- [x] `python Projects/scripts/validate_phase.py PROJ-404 1` PASSED
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-404` PASSED
