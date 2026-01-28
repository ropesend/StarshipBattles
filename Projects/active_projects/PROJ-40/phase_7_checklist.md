# Phase 7: UI Layer Remediation

**Status:** Not Started
**Estimated Effort:** 6-8 hours
**Priority:** Medium

## Overview
Address remaining issues in `game/ui/` after Phase 1 critical fixes. Focus on code quality, type hints, and class size.

---

## Tasks

### 7.1 Consolidate CrewCapacity Logic (NEW-UI-004)
**Location:** `game/ui/screens/builder/stats_config.py:59-75, 73-75, 104-105`
**Effort:** Medium

- [ ] Create `get_crew_capacity_with_legacy_fallback()` helper function
- [ ] Place in `game/ui/utils/` or `game/ui/screens/builder/utils.py`
- [ ] Update all three locations to use helper
- [ ] Add deprecation warning in helper for legacy path
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 7.2 Add Type Hints to FormationEditor (NEW-UI-005)
**Location:** `game/ui/screens/formation_editor.py:17-1055`
**Effort:** Medium

- [ ] Add parameter type hints to all public methods
- [ ] Add return type hints to all public methods
- [ ] Focus on the 42 methods, prioritize public API
- [ ] Run mypy if available

---

### 7.3 Fix Bare Exception in Event Handlers (NEW-UI-008)
**Location:** `game/ui/screens/formation_editor.py:525, 533`
**Effort:** Simple

- [ ] Replace `except:` with `except ValueError as e:`
- [ ] Add user feedback for invalid input
- [ ] Log warning for debugging
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 7.4 Fix Fragile Path Construction (NEW-UI-009)
**Location:** `game/ui/screens/test_lab.py:38`
**Effort:** Simple

- [ ] Replace nested `os.path.dirname()` calls with pathlib
- [ ] Use `Path(__file__).parents[4]` or similar
- [ ] Or use `game.core.paths` utilities
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 7.5 Fix Module-level Logger (NEW-UI-010)
**Location:** `game/ui/screens/builder/main.py:46-48`
**Effort:** Medium

- [ ] Move logger initialization into class constructor
- [ ] Or use lazy loading pattern
- [ ] Remove hardcoded DEBUG level
- [ ] Use configuration-based log level
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 7.6 Fix tkinter Exception Handling (NEW-UI-011)
**Location:** `game/ui/screens/builder/main.py:34-39`
**Effort:** Simple

- [ ] Replace bare `except:` with `except tk.TclError as e:`
- [ ] Log the error for debugging
- [ ] Add fallback behavior documentation
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 7.7 Extract UI Layout Constants (NEW-UI-012)
**Location:** Multiple files (837 instances)
**Effort:** Complex (partial in this phase)

This is a large effort. In this phase:
- [ ] Create `game/ui/layout.py` or `game/ui/config.py`
- [ ] Define `UILayoutConfig` dataclass with common constants
- [ ] Migrate 10-20 most-used magic numbers as proof of concept
- [ ] Document pattern for future migrations
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 7.8 Plan RaceSetupScreen Decomposition (NEW-UI-014)
**Location:** `game/ui/screens/race_setup_screen.py:34-1227`
**Effort:** Complex (planning only)

- [ ] Document current responsibilities (1227 lines, 36 methods)
- [ ] Identify extraction candidates:
  - [ ] `TabManager` class
  - [ ] `RacePanelBuilder` class
  - [ ] `ColorPickerPanel` class
- [ ] Add decomposition plan to `decisions.md`
- [ ] Extract ONE component as proof of concept

---

### 7.9 Define ComponentRef Pattern (NEW-UI-015)
**Location:** Multiple builder files
**Effort:** Simple

- [ ] Create `ComponentRef` dataclass with explicit fields
- [ ] Define standard pattern for component references
- [ ] Document usage in builder README or comments
- [ ] Update 2-3 files to use new pattern as example

---

### 7.10 Fix Schematic Cache Key (NEW-UI-016)
**Location:** `game/ui/screens/builder/schematic_view.py:123-176`
**Effort:** Medium

- [ ] Include weapon stats in cache key, not just ID
- [ ] Or invalidate cache when weapon is modified
- [ ] Add test for cache invalidation on modifier change
- [ ] Run: `pytest tests/unit/ui/ -v`

---

## Verification

- [ ] Run UI tests: `pytest tests/unit/ui/ -v`
- [ ] Manual verification of UI screens
- [ ] Test formation editor with invalid inputs

---

## Notes
- Tasks 7.7 and 7.8 are too large for full completion - do partial implementation
- Focus on establishing patterns that can be followed later
- Phase 1 should have fixed the critical layer violations already
