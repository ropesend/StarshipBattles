# Phase 3: Relocate Misplaced Test Files [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-267 3`
> 2. Only proceed if output shows PASSED

**Objective:** Move test files to correct directories based on what layer they test.
**Status:** Not Started

---

## Task 3.1: Move test_ship_theme_logic.py [Simple]
- [ ] Verify imports `game.ui.assets.ShipThemeManager`
- [ ] `git mv tests/unit/entities/test_ship_theme_logic.py tests/unit/ui/test_ship_theme_logic.py`
- [ ] Check conftest dependencies
- [ ] Run at new location — passes

## Task 3.2: Move or skip test_hex_math_strategy.py [Simple]
- [ ] Check if PROJ-263 already deleted it
- [ ] If deleted: skip. If exists: `git mv tests/integration/strategy/test_hex_math_strategy.py tests/unit/core/`
- [ ] Run at new location — passes

## Task 3.3: Move test_battle_setup_logic.py [Simple]
- [ ] Verify imports `game.ui.screens.battle_screen.BattleScreen`
- [ ] `git mv tests/unit/combat/test_battle_setup_logic.py tests/unit/ui/screens/`
- [ ] Run at new location — passes

## Task 3.4: Move DTO tests from integration/ to unit/ [Simple]
- [ ] Verify all 3 files test only frozen dataclass creation
- [ ] `git mv tests/integration/strategy/facade/test_empire_dto.py tests/unit/strategy/facade/`
- [ ] `git mv tests/integration/strategy/facade/test_fleet_dto.py tests/unit/strategy/facade/`
- [ ] `git mv tests/integration/strategy/facade/test_system_dto.py tests/unit/strategy/facade/`
- [ ] Check conftest dependencies
- [ ] Run all at new locations — pass

## Phase 3 Verification
- [ ] All moved files pass at new locations
- [ ] Full test suite: `pytest tests/ --testmon`
- [ ] Test count unchanged
