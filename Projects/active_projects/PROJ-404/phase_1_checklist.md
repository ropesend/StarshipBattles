# Phase 1: Delete remaining save-format fallbacks + canonical error type

**Status:** Not Started
**Objective:** Remove the two surviving save-format compat surfaces and normalize the missing-`components` error to `PersistenceException`. Replace legacy-path tests with negative regression tests.

---

## Tasks

### Task 1.1: Read all four files + confirm current shapes [Simple]
**File:** see manifest

- [ ] Read `ship_instance_serializer.py` around line 106 (the `resource_levels` fallback) and around line 87,124 (`require_keys` call + `data['components']` access).
- [ ] Read `battle_setup_state.py:117-130` (`BattleSetupSide.from_dict`).
- [ ] Read existing tests in both test modules to identify which ones encode the legacy paths.
- [ ] Locate `require_keys()` and `PersistenceException` so you have the canonical error route.
- [ ] Decide whether the canonical save-format requires `consumable_levels` to be present, or whether absent → `{}` is the new contract. Document in `decisions.md`.

**Notes:**

### Task 1.2: TDD — write failing negative regression tests [Medium]
**File:** `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py`, `tests/unit/ui/screens/test_battle_setup_state.py`

- [ ] Add a test asserting `ShipInstanceSerializer.from_dict({...without 'components'...})` raises `PersistenceException`, not raw `KeyError`.
- [ ] Add a test asserting that a payload containing only legacy `resource_levels` (no `consumable_levels`) raises a meaningful error or returns the documented new shape — choose based on Task 1.1 decision.
- [ ] Add a test asserting `BattleSetupSide.from_dict({...without 'system_complex_toggles'...})` raises (after the tolerance is deleted).
- [ ] Run all three tests against unmodified production — they should fail (currently the legacy paths are tolerated).

**Notes:**

### Task 1.3: Delete the `resource_levels` fallback + route `components` through `require_keys()` [Simple]
**File:** `game/strategy/data/ship_instance_serializer.py`

- [ ] Change line 106 from `data.get('consumable_levels', data.get('resource_levels', {}))` to `data.get('consumable_levels', {})` (or per Task 1.1 decision).
- [ ] Add `components` to the `require_keys(...)` call so missing `components` raises `PersistenceException` rather than raw `KeyError` on later access.
- [ ] Run focused tests — passing tests should still pass; new negative tests should now pass.

**Notes:**

### Task 1.4: Delete the `*_complex_toggles` tolerance [Simple]
**File:** `game/ui/screens/battle_setup_state.py:117-130`

- [ ] Remove the legacy-tolerance branch and the docstring framing.
- [ ] Update the new-format constructor to require both keys (or call `require_keys`).
- [ ] Run focused tests — new negative test should pass; legacy-path test should now fail.

**Notes:**

### Task 1.5: Delete legacy-path tests [Simple]
**File:** `tests/unit/ui/screens/test_battle_setup_state.py:223-235` (the "Legacy saves ... Don't crash" test) and any equivalent serializer test that asserts legacy shapes succeed.

- [ ] Delete those test functions outright. Do not "soften" them — Rule 3 says old saves are disposable, so the tests for legacy success are no longer valid behavior to preserve.
- [ ] Run the test modules — should pass.

**Notes:**

### Task 1.6: Run round-trip + battle-setup integration suites [Simple]
**Tests:** `pytest tests/integration/save_load/test_roundtrip_ships.py tests/integration/ui/test_battle_setup_three_sides.py -v`

- [ ] Both pass.
- [ ] If anything fails because it relied on legacy shapes, fix the test to use the canonical shape.

**Notes:**

### Task 1.7: Closeout
- [ ] Update Phase 1 status to `Complete`
- [ ] Update plan.md Quick Status + Current State
- [ ] Update `Projects/projects_index.md` row for PROJ-404 to `Complete`
- [ ] Validators pass
- [ ] Commit `PROJ-404 phase 1: delete save-format compat surfaces + canonical PersistenceException`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Status at top of this file is `Complete`
- [ ] plan.md updated
- [ ] Focused + integration suites pass
- [ ] `python Projects/scripts/validate_phase.py PROJ-404 1` PASSED
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-404` PASSED
