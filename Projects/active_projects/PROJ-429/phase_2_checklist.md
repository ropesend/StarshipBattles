# Phase 2: Migrate `design_role` classification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-429 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** lightweight

**Files (planned):**
- `game/strategy/data/design_role.py` (modify — delete seven frozensets + inline literal)
- `tests/unit/strategy/data/test_design_role.py` (modify — add new-ability classification test FIRST)

**Objective:** Delete every role-classification frozenset in `design_role.py` (`_WEAPON_ABILITIES`, `_SEEKER_ABILITIES`, `_BEAM_PROJECTILE_ABILITIES`, `_SENSOR_ABILITIES`, `_SUPPORT_ABILITIES`, `_CARRIER_ABILITIES`, `_COMMAND_ABILITIES`) and the inline `"CommandAndControl"` literal at line 105. Replace with `abilities_with_role_tag(...)` queries against the unified registry.

---

## Reading

- [ ] Re-read `design.md` "Per-Consumer Migration Order" Phase 2 row.
- [ ] Read `game/strategy/data/design_role.py` lines 56-167 (constants + `classify_design_role` + `classify_from_design_data`).
- [ ] Read `tests/unit/strategy/data/test_design_role.py` end-to-end.

---

## Tasks

### Task 2.1: Add the failing new-ability classification test (TDD red) [Simple]

**File:** `tests/unit/strategy/data/test_design_role.py`

- [ ] Add `test_new_carrier_ability_classifies_without_design_role_edit`:
      Create a hypothetical `FooLaunchAbility` ability fixture/registration with `RoleTag.CARRIER`, run `classify_design_role`, assert the result is `CARRIER`. **Do not touch `design_role.py` to make this pass** — the whole point is that registry tagging is sufficient.
- [ ] Confirm failure: with `design_role.py` still reading from its local frozensets, the new fixture is not recognized → test fails.

**Notes:** [Filled during implementation]

### Task 2.2: Replace frozenset reads with `abilities_with_role_tag(...)` (TDD green) [Medium]

**File:** `game/strategy/data/design_role.py`

- [ ] At each call site that reads `_WEAPON_ABILITIES`, `_SEEKER_ABILITIES`, `_BEAM_PROJECTILE_ABILITIES`, `_SENSOR_ABILITIES`, `_SUPPORT_ABILITIES`, `_CARRIER_ABILITIES`, `_COMMAND_ABILITIES`, swap to `abilities_with_role_tag(RoleTag.<TAG>)`.
- [ ] Replace inline `"CommandAndControl"` literal at line 105 with `abilities_with_role_tag(RoleTag.COMMAND)` membership check.
- [ ] Delete the seven module-level frozenset constants.
- [ ] Verify imports: nothing else in `game/strategy/` should import these constants (they are module-private `_`-prefixed). Confirm via grep.

**Notes:** [Filled during implementation]

### Task 2.3: Regression sweep [Simple]

**Tests:** `pytest tests/unit/strategy/data/test_design_role.py -q`

- [ ] All existing fixtures continue to produce the same role outcomes.
- [ ] New-ability test from Task 2.1 is green.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `design_role.py` contains zero hardcoded ability-name sets (grep for `_WEAPON_ABILITIES`, etc., returns no hits in `design_role.py`)
- [ ] Inline `"CommandAndControl"` literal removed
- [ ] `pytest tests/unit/strategy/data/test_design_role.py` is fully green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
