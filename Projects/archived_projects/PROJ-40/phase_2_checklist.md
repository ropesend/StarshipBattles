# Phase 2: Quick Wins - Dead Code & Duplicates

**Status:** Complete
**Estimated Effort:** 1.5 hours
**Priority:** High - Low effort, immediate improvement

## Overview
Address simple issues that can be fixed quickly: duplicate code, unused imports, dead code patterns.

> **Note:** This phase was reduced from 15 tasks to 9 after Category 3 audit verification:
> - Task 2.2c (NEW-STRAT-004) REMOVED - Method does not exist
> - Task 2.2d (NEW-STRAT-005) REMOVED - Properly documented with BUG-29 comment
> - Task 2.3a (NEW-UI-003) REMOVED - TestRunner IS used at line 115

---

## Tasks

### 2.1 Remove Duplicate Statements (30 min)

#### 2.1a NEW-SIM-002: Duplicate Import in ship.py
**Location:** `game/simulation/entities/ship.py:19, 118`
**Issue:** ResourceRegistry imported at module level AND inside `__init__`

- [x] Remove duplicate `ResourceRegistry` import on line 118 (inside __init__)
- [x] Verify module-level import on line 19 is sufficient
- [x] Note: Line 118 import is AFTER line 117 usage - this is a bug
- [x] Run: `pytest tests/unit/entities/test_ship.py -v`

**Evidence from audit:** The import at line 118 appears AFTER line 117 where ResourceRegistry() is instantiated. The module-level import at line 19 already makes it available.

#### 2.1b NEW-SIM-003: Duplicate Assignment in stats.py
**Location:** `game/simulation/systems/stats.py:42-43`
- [x] Remove duplicate `ship.shield_regen_cost = 0` on line 43
- [x] Run: `pytest tests/unit/systems/ -v`

---

### 2.2 Remove Dead Code Patterns (30 min)

#### 2.2a NEW-SIM-004: Dead Pass Statements in stats.py
**Location:** `game/simulation/systems/stats.py:322, 391`
**Issue:** Pass statements with deprecation comments are dead code

- [x] Remove pass statement at line 322 (keep comment in git history)
- [x] Remove pass statement at line 391 (keep comment in git history)
- [x] Run: `pytest tests/unit/systems/ -v`

**Note:** While documented, dead pass statements are code smell. Comments preserved in git history.

#### ~~2.2b NEW-UI-006: Disabled Method in schematic_view.py~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** Method is deliberately disabled per user request and has callers in interaction_controller.py.
Removing would break code. The method returning None is intentional behavior.

---

### 2.3 Remove Unused Imports (15 min)

#### 2.3a NEW-UI-007: Unused simpledialog Import
**Location:** `game/ui/screens/builder/main.py:4`
- [x] Verify `simpledialog` is not used in file
- [x] Remove import if unused
- [x] Run: `pytest tests/unit/ui/ -v`

**Notes:** Removed `simpledialog` from import, kept `filedialog` which is used at line 819. Updated comment to reference filedialog.

#### 2.3b NEW-RES-008: Unused log_error Import
**Location:** `game/research/data/tech_tree.py:10`
- [x] Verify `log_error` is not used in file
- [x] Remove import if unused
- [x] Run: `pytest tests/unit/research/ -v`

**Notes:** Removed `log_error` from import, kept `log_info` which is used 4 times in the file.

---

### 2.4 Fix Bare Exception Handlers (15 min)

#### NEW-UI-002: Bare except clauses (4 instances)
**Locations:**
- `game/ui/screens/builder/main.py:38`
- `game/ui/screens/formation_editor.py:14, 525, 533`

For each location:
- [x] Replace `except:` with `except Exception as e:` or specific type
- [x] main.py:38 - Changed to `except Exception:`
- [x] formation_editor.py:14 - Changed to `except Exception:`
- [x] formation_editor.py:525, 533 - Changed to `except ValueError:` (int() conversion)

---

### 2.5 Fix Empty Lines / Formatting (15 min)

#### NEW-UI-013: Excessive Empty Lines
**Location:** `game/ui/screens/builder/main.py:52-58`
- [x] Remove 7 consecutive empty lines
- [x] Follow PEP 8 (max 2 blank lines between top-level definitions)

---

## Removed Tasks (Audit Verification)

### ~~2.2c NEW-STRAT-004: Unused Method in turn_engine.py~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** Method `_apply_battle_results` does not exist. The file is only 223 lines.

### ~~2.2d NEW-STRAT-005: Dead Code in save_game_service.py~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** `_migrate_temp_designs` is properly documented with BUG-29 comment at line 77. Intentionally disabled code.

### ~~2.3a NEW-UI-003: Unused TestRunner Import~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** TestRunner IS used at line 115, methods called at line 119.

---

## Verification

- [x] Run full test suite: `pytest`
- [x] Verify no import errors: `python -c "import game"`
- [ ] Optional: Run linter to check for other unused imports

---

## Notes
- All tasks in this phase are independent and can be done in any order
- Each task includes its own test verification
- Total line count reduction: ~50-80 lines
