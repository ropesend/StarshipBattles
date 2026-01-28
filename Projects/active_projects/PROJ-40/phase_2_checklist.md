# Phase 2: Quick Wins - Dead Code & Duplicates

**Status:** Not Started
**Estimated Effort:** 2-3 hours
**Priority:** High - Low effort, immediate improvement

## Overview
Address simple issues that can be fixed quickly: duplicate code, unused imports, dead code patterns.

---

## Tasks

### 2.1 Remove Duplicate Statements (30 min)

#### NEW-SIM-002: Duplicate Import in ship.py
**Location:** `game/simulation/entities/ship.py:16, 85`
- [ ] Remove duplicate `ResourceRegistry` import on line 85
- [ ] Verify module-level import on line 16 is sufficient
- [ ] Run: `pytest tests/unit/entities/test_ship.py -v`

#### NEW-SIM-003: Duplicate Assignment in stats.py
**Location:** `game/simulation/systems/stats.py:42-43`
- [ ] Remove duplicate `ship.shield_regen_cost = 0` on line 43
- [ ] Run: `pytest tests/unit/systems/ -v`

---

### 2.2 Remove Dead Code Patterns (30 min)

#### NEW-SIM-004: Incomplete Code Block in stats.py
**Location:** `game/simulation/systems/stats.py:319-322`
- [ ] Review Phase 6 resource aggregation removal
- [ ] Either implement missing logic or remove pass statement
- [ ] Add comment if removal is intentional
- [ ] Run: `pytest tests/unit/systems/ -v`

#### NEW-UI-006: Disabled Method in schematic_view.py
**Location:** `game/ui/screens/builder/schematic_view.py:36-42`
- [ ] Remove disabled `get_component_at()` method
- [ ] Verify no callers exist
- [ ] Run: `pytest tests/unit/ui/ -v`

#### NEW-STRAT-004: Unused Method in turn_engine.py
**Location:** `game/strategy/engine/turn_engine.py:433-467`
- [ ] Verify `_apply_battle_results` is never called
- [ ] Remove unused method (35 lines)
- [ ] Run: `pytest tests/unit/strategy/ -v`

#### NEW-STRAT-005: Dead Code in save_game_service.py
**Location:** `game/strategy/systems/save_game_service.py:114-146`
- [ ] Review BUG-29 FIX note at line 77
- [ ] Remove `_migrate_temp_designs` if no longer needed
- [ ] Or document why it's kept for future use
- [ ] Run: `pytest tests/integration/test_save_load.py -v`

---

### 2.3 Remove Unused Imports (30 min)

#### NEW-UI-003: Unused TestRunner Import
**Location:** `game/ui/screens/test_lab.py:10`
- [ ] Remove unused `TestRunner` import
- [ ] Verify line 115 usage is valid or fix it
- [ ] Run: `pytest tests/unit/ui/ -v`

#### NEW-UI-007: Unused simpledialog Import
**Location:** `game/ui/screens/builder/main.py:4`
- [ ] Remove `simpledialog` import from tkinter
- [ ] Run: `pytest tests/unit/ui/ -v`

#### NEW-RES-008: Unused log_error Import
**Location:** `game/research/data/tech_tree.py:10`
- [ ] Remove unused `log_error` import
- [ ] Run: `pytest tests/unit/research/ -v`

---

### 2.4 Fix Bare Exception Handlers (30 min)

#### NEW-UI-002: Bare except clauses (4 instances)
**Locations:**
- `game/ui/screens/builder/main.py:38`
- `game/ui/screens/formation_editor.py:14, 525, 533`

For each location:
- [ ] Replace `except:` with `except Exception as e:`
- [ ] Add logging: `logger.warning(f"...: {e}")`
- [ ] Specify more precise exception types if possible

---

### 2.5 Fix Empty Lines / Formatting (15 min)

#### NEW-UI-013: Excessive Empty Lines
**Location:** `game/ui/screens/builder/main.py:52-58`
- [ ] Remove 7 consecutive empty lines
- [ ] Follow PEP 8 (max 2 blank lines between top-level definitions)

---

## Verification

- [ ] Run full test suite: `pytest`
- [ ] Verify no import errors: `python -c "import game"`
- [ ] Optional: Run linter to check for other unused imports

---

## Notes
- All tasks in this phase are independent and can be done in any order
- Each task includes its own test verification
- Total line count reduction: ~100-150 lines
