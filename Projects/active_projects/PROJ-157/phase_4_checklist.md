# Phase 4: Old Directory Tree Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-157 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete old test directories file-by-file after verifying each is a strict subset of the newer version.

**CRITICAL RULES:**
1. Do NOT delete wholesale. Verify EACH file individually.
2. For each old file, find the new counterpart in `tests/unit/simulation/`
3. List all `def test_` methods in old file, confirm each has an equivalent in new file
4. If ANY old test lacks an equivalent → SKIP that file (do not delete)
5. Run `pytest tests/ -x -q` after each batch of deletions
6. Record which files were skipped and why

---

## Pre-Work
- [ ] Record current test count: _____ tests passed
- [ ] Catalog all .py files in `tests/unit/services/` (expected: ~7 files)
- [ ] Catalog all .py files in `tests/unit/combat/` (remaining after Phase 1 deletions)
- [ ] Catalog all .py files in `tests/unit/entities/` (expected: ~45 files)
- [ ] Catalog all .py files in `tests/unit/components/` (remaining after Phase 2 merge)

---

## Task 4.1: Clean up tests/unit/services/ [Medium]
**New counterparts in:** `tests/unit/simulation/services/`

For each file in `tests/unit/services/`:
- [ ] List test methods in old file
- [ ] Find simulation/services/ counterpart
- [ ] Verify ALL old tests have equivalents in new file
- [ ] Delete verified subset files

**Verified spot-check from validation:** `test_battle_service.py` (15 methods → 77 in new file, strict subset)

**Files processed:**
| Old File | New Counterpart | Subset? | Action |
|----------|----------------|---------|--------|
| | | | |

- [ ] Run `pytest tests/ -x -q`

**Notes:**

---

## Task 4.2: Clean up tests/unit/entities/ [Medium]
**New counterparts in:** `tests/unit/simulation/entities/`

For each file in `tests/unit/entities/` (excluding already-deleted scaffolds):
- [ ] List test methods in old file
- [ ] Find simulation/entities/ counterpart
- [ ] Verify ALL old tests have equivalents
- [ ] Delete verified subset files

**Verified spot-checks from validation:**
- `test_layer_data.py` (24 methods → 64 in new, strict subset)
- `test_ship_formation.py` (14 methods → 76 in new, strict subset)
- `test_combat_endurance.py` (5 methods → 45 in new, strict subset)

**Files processed:**
| Old File | New Counterpart | Subset? | Action |
|----------|----------------|---------|--------|
| | | | |

- [ ] Run `pytest tests/ -x -q`

**Notes:**

---

## Task 4.3: Clean up tests/unit/combat/ [Medium]
**New counterparts in:** `tests/unit/simulation/` (various subdirs)

For each remaining file in `tests/unit/combat/` (after Phase 1 deleted edge cases, lead, ccd):
- [ ] List test methods in old file
- [ ] Find simulation/ counterpart
- [ ] Verify ALL old tests have equivalents
- [ ] Delete verified subset files

**SPECIAL ATTENTION:** `test_projectile_manager.py` - validation found `test_projectile_movement` may NOT have a 1:1 mapping in new file. Verify this specific test before deleting.

**Files processed:**
| Old File | New Counterpart | Subset? | Action |
|----------|----------------|---------|--------|
| | | | |

- [ ] Run `pytest tests/ -x -q`

**Notes:**

---

## Task 4.4: Clean up tests/unit/components/ [Medium]
**New counterparts in:** `tests/unit/simulation/components/`

For each remaining file in `tests/unit/components/` (after Phase 2 merged health_manager):
- [ ] List test methods in old file
- [ ] Find simulation/components/ counterpart
- [ ] Verify ALL old tests have equivalents
- [ ] Delete verified subset files

**Verified spot-check from validation:** `test_component_health_manager.py` (9 methods → 43 in new, strict subset - but already merged in Phase 2)

**Files processed:**
| Old File | New Counterpart | Subset? | Action |
|----------|----------------|---------|--------|
| | | | |

- [ ] Run `pytest tests/ -x -q`

**Notes:**

---

## Task 4.5: Clean up empty directories [Simple]
- [ ] Check if `tests/unit/services/` is now empty → delete directory
- [ ] Check if `tests/unit/combat/` is now empty → delete directory
- [ ] Check if `tests/unit/entities/` is now empty → delete directory
- [ ] Check if `tests/unit/components/` is now empty → delete directory
- [ ] Remove any orphaned `__init__.py` or `conftest.py` in cleaned directories
- [ ] Run `pytest tests/ -x -q` final check

**Notes:**

---

## Skipped Files Log
Files that were NOT strict subsets and were kept:
| File | Reason |
|------|--------|
| | |

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked (or documented as skipped)
- [ ] Record post-phase test count: _____ tests passed (delta: _____)
- [ ] Skipped files documented with reasons
- [ ] Run `pytest tests/ -n 12` - full parallel verification
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
