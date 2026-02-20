# Phase 3: Delete Old Directory Trees

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-155 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove 4 old test directories confirmed as strict subsets of newer simulation/ tests.
**Priority:** High

---

## PROJ-157 Overlap Summary

PROJ-157 completed Phase 4 (old directory tree cleanup) which maps to this phase. It:
- Fully deleted `tests/unit/services/` (6 test files) and `tests/unit/components/` (4 test files)
- Deleted 13 files from `tests/unit/combat/` (2 files kept for manual review)
- Deleted 31 files from `tests/unit/entities/` (11 files + ship_helpers/ subdir kept — no clear counterparts)

---

## CRITICAL: Approach

**DO NOT wholesale-delete directories.** Delete file-by-file after verifying each pair.

For each file:
1. Identify the corresponding new file in `tests/unit/simulation/`
2. Verify test count: new file should have >= old file's test count
3. Delete the old file
4. Run tests to confirm no regressions

Validation review 4 warned that old files sometimes use real objects (integration-style) while new files use MagicMock (unit-style). If an old file has no clear new counterpart, KEEP it and note in decisions.md.

---

## Tasks

### Task 3.1: Delete tests/unit/services/ [Medium] — DONE by PROJ-157

- [x] All 6 test files verified as strict subsets and deleted — PROJ-157
- [x] Directory removed — PROJ-157

**PROJ-157 verified pairs:**
| Old File | New Counterpart | Tests |
|----------|----------------|-------|
| test_battle_service.py | simulation/services/test_battle_service.py | 15→77 |
| test_modifier_service.py | simulation/services/test_modifier_service.py | 29→63 |
| test_modifier_service_di.py | simulation/services/test_modifier_service.py | 11→63 |
| test_vehicle_design_service.py | simulation/services/test_vehicle_design_service.py | 17→50 |
| test_vehicle_design_service_di.py | simulation/services/test_vehicle_design_service.py | 6→50 |
| test_ship_stats_calculator_di.py | strategy/ship_stats/test_edge_cases.py | 6→48 |

### Task 3.2: Delete tests/unit/components/ [Simple] — DONE by PROJ-157

- [x] All 4 test files verified as strict subsets and deleted — PROJ-157
- [x] Directory removed — PROJ-157

**PROJ-157 verified pairs:**
| Old File | New Counterpart | Tests |
|----------|----------------|-------|
| test_component_health_manager.py | simulation/components/test_component_health_manager.py | 9→43 |
| test_component_health_edge_cases.py | simulation/components/test_component_health_manager.py | 10→43 |
| test_component_resource_manager.py | simulation/components/test_component_resource_manager.py | 12→44 |
| test_resource_costs.py | simulation/components/test_component_resource_manager.py | 6→44 |

### Task 3.3: Delete subset files from tests/unit/combat/ [Complex] — Partially done by PROJ-157

**PROJ-157 deleted 13 files (confirmed subsets) + Phase 1 deleted 4 files.**

**Remaining 2 files that need manual review:**
- [x] `tests/unit/combat/test_combat.py` (11 tests) — KEEP: Unique integration-style damage/layer/regen tests with real Ships, no simulation/ counterpart
- [x] `tests/unit/combat/test_battle_setup_logic.py` (3 tests) — KEEP: Unique BattleScreen.start() tests, no simulation/ counterpart
- [x] `tests/unit/combat/conftest.py` — KEEP: Supports the 2 test files above
- [x] All combat/ files verified as UNIQUE - keeping entire directory
- [x] Run `pytest tests/ -n 12 -q` to verify no regressions

**Notes:** Only 2 test files + conftest remain. Low effort.

### Task 3.4: Delete subset files from tests/unit/entities/ [Complex] — Partially done by PROJ-157

**PROJ-157 deleted 31 files. Phase 1 deleted 3 files.**

**Remaining 12 files that need review:**

| File | Tests | PROJ-157 Reason for Keeping |
|------|-------|-----------------------------|
| test_ship_stat_querier.py | 45 | UNIQUE: No counterpart in simulation/ |
| test_ability_interface.py | 17 | REVIEW: May have unique interface tests |
| test_component_di.py | 10 | REVIEW: DI pattern tests |
| test_components.py | 22 | REVIEW: Old file has more tests than counterpart |
| test_component_cache.py | 7 | NO_COUNTERPART: Caching tests not found elsewhere |
| test_ship_di.py | 7 | NO_COUNTERPART: Ship DI tests |
| test_ship.py | 12 | NO_COUNTERPART: Core ship tests |
| test_ship_theme_logic.py | 14 | NO_COUNTERPART: Theme logic tests |
| test_planetary_complex.py | 5 | NO_COUNTERPART: Planetary tests |
| test_bridge_requirement_removal.py | 1 | NO_COUNTERPART: Migration test |
| test_abilities.py | 14 | REVIEW: Need to verify coverage |
| ship_helpers/ (subdir) | ~50 | REVIEW: Component getter/operation tests |

- [x] All files verified: NO simulation/ counterparts exist for any entities/ file
- [x] test_ship_stat_querier.py (45 tests) — KEEP: ShipStatQuerier tests, no counterpart
- [x] test_bridge_requirement_removal.py (1 test) — KEEP: Important regression test
- [x] test_component_cache.py (7 tests) — KEEP: Thread safety tests, no counterpart
- [x] test_ship.py (12 tests) — KEEP: Core Ship tests, no counterpart
- [x] test_ability_interface.py (17 tests) — KEEP: Unique interface tests
- [x] test_component_di.py (10 tests) — KEEP: DI pattern tests
- [x] test_components.py (22 tests) — KEEP: Component tests
- [x] test_ship_di.py (7 tests) — KEEP: Ship DI tests
- [x] test_ship_theme_logic.py (14 tests) — KEEP: Theme tests
- [x] test_planetary_complex.py (5 tests) — KEEP: Planetary tests
- [x] test_abilities.py (14 tests) — KEEP: Abilities tests
- [x] ship_helpers/ (50 tests) — KEEP: All unique component getter/operation tests
- [x] All entities/ files verified as UNIQUE - keeping entire directory

**Notes:** These are the files PROJ-157 was conservative about. Several may genuinely need to be kept. Expect this task to result in a mix of deletions and "keep" decisions.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12 -q` — verify no new failures vs baseline
- [ ] Record total lines removed in this phase in decisions.md
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
