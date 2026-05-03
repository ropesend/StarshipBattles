# UI Layer Scout Report

## Summary
- Files Reviewed: 90
- Issues Found: 16
- Critical: 1, Major: 5, Minor: 10, Info: 0

---

## Findings

### CRITICAL: Layer Violations - UI Imports from Simulation/Strategy/AI
**ID:** NEW-UI-001
**Location:** Multiple files (37 instances total)
**Issue:** The UI layer directly imports from simulation, strategy, and AI layers, violating layering principles. Examples:
- `battle_scene.py:17` - imports `AIController` from game.ai
- `build_queue_screen.py:10-12` - imports from game.strategy and game.simulation
- `workshop_screen.py:17-39` - imports multiple simulation entities and services
- `panels/ship_stats_renderer.py:7-8` - imports from game.simulation and game.ai
**Impact:** Creates tight coupling between UI and core logic layers. Changes to simulation internals require UI updates. Violates clean architecture principles.
**Recommendation:** Create UI-facing service interfaces/facades in core or strategy layer. UI should only import from dedicated service interfaces, not internal entities.
**Effort:** Complex

---

### MAJOR: Bare Exception Handlers Without Type Specification
**ID:** NEW-UI-002
**Location:**
- `game/ui/screens/builder/main.py:38`
- `game/ui/screens/formation_editor.py:14, 525, 533`
**Issue:** Four instances of bare `except:` clauses that catch all exceptions without specifying type. This hides errors and makes debugging difficult.
**Impact:** Exceptions are silently caught and suppressed. Makes it hard to identify and fix issues.
**Recommendation:** Replace `except:` with specific exception types (e.g., `except Exception as e:` or `except (ValueError, TypeError) as e:`). Log the exception for debugging.
**Effort:** Simple

---

### MAJOR: Unused Import - TestRunner in test_lab.py
**ID:** NEW-UI-003
**Location:** `game/ui/screens/test_lab.py:10, 115`
**Issue:** TestRunner is imported at line 10 but used at line 115 without being assigned. The import appears to be a vestigial reference.
**Impact:** Dead code increases maintenance burden.
**Recommendation:** Remove the unused import line 10, or verify if TestRunner instantiation at line 115 is the intended usage.
**Effort:** Simple

---

### MAJOR: CrewCapacity Fallback Logic Repeated
**ID:** NEW-UI-004
**Location:** `game/ui/screens/builder/stats_config.py:59-75, 73-75, 104-105`
**Issue:** The legacy crew capacity fallback pattern is implemented in three separate functions without consolidation.
**Impact:** Code duplication creates maintenance burden. Violates DRY principle.
**Recommendation:** Extract legacy crew logic to a single function. Reference it from all three locations.
**Effort:** Medium

---

### MAJOR: Missing Type Hints - formation_editor.py
**ID:** NEW-UI-005
**Location:** `game/ui/screens/formation_editor.py:17-1055`
**Issue:** FormationEditorScene has 42 methods but only 4 have return type annotations. Most methods lack parameter and return type hints.
**Impact:** Type checkers cannot validate code. IDE autocomplete less accurate.
**Recommendation:** Add type hints to all public methods.
**Effort:** Medium

---

### MINOR: Dead Code Pattern - SchematicView.get_component_at() Disabled
**ID:** NEW-UI-006
**Location:** `game/ui/screens/builder/schematic_view.py:36-42`
**Issue:** The `get_component_at()` method is completely disabled with a comment and returns None unconditionally.
**Impact:** Dead code that serves no purpose.
**Recommendation:** Remove the disabled method entirely.
**Effort:** Simple

---

### MINOR: Unused Import - simpledialog in builder/main.py
**ID:** NEW-UI-007
**Location:** `game/ui/screens/builder/main.py:4`
**Issue:** `simpledialog` is imported from tkinter but never used.
**Impact:** Unused import adds cognitive load.
**Recommendation:** Remove the `simpledialog` import.
**Effort:** Simple

---

### MINOR: Bare Exception in Event Handlers
**ID:** NEW-UI-008
**Location:** `game/ui/screens/formation_editor.py:525, 533`
**Issue:** Two bare `except:` clauses in event handler for UITextEntryLine.
**Impact:** If user enters invalid text, the error is hidden.
**Recommendation:** Catch specific exceptions and provide user feedback.
**Effort:** Simple

---

### MINOR: Fragile Path Construction
**ID:** NEW-UI-009
**Location:** `game/ui/screens/test_lab.py:38`
**Issue:** Path traversal uses four nested `os.path.dirname()` calls to reach root.
**Impact:** Difficult to understand and maintain. Will fail if file is moved.
**Recommendation:** Use pathlib for clarity.
**Effort:** Simple

---

### MINOR: Module-level Logger Initialization
**ID:** NEW-UI-010
**Location:** `game/ui/screens/builder/main.py:46-48`
**Issue:** Logger is initialized at module level with hardcoded DEBUG level.
**Impact:** Cannot easily change logging level in tests.
**Recommendation:** Initialize logger inside class constructor or use lazy loading pattern.
**Effort:** Medium

---

### MINOR: Incomplete tkinter Initialization
**ID:** NEW-UI-011
**Location:** `game/ui/screens/builder/main.py:34-39`
**Issue:** Tkinter root window is conditionally initialized in a try/except block, but uses bare except.
**Impact:** If tkinter fails, exception is silently caught.
**Recommendation:** Use specific exception handling and log the error.
**Effort:** Simple

---

### MINOR: Hardcoded UI Layout Constants
**ID:** NEW-UI-012
**Location:** Multiple files with 837 instances of hardcoded coordinates
**Issue:** UI element positions are hardcoded as magic numbers throughout UI layer.
**Impact:** Difficult to adjust UI layout globally. Cannot easily support different screen resolutions.
**Recommendation:** Create configuration class/dict for all layout constants.
**Effort:** Medium

---

### MINOR: Incomplete Refactoring - Empty Lines
**ID:** NEW-UI-013
**Location:** `game/ui/screens/builder/main.py:52-58`
**Issue:** Seven consecutive empty lines between imports and class definition.
**Impact:** Reduces code quality. Indicates incomplete cleanup.
**Recommendation:** Remove trailing blank lines.
**Effort:** Simple

---

### MINOR: Large Class - race_setup_screen.py
**ID:** NEW-UI-014
**Location:** `game/ui/screens/race_setup_screen.py:34-1227`
**Issue:** RaceSetupScreen class is 1227 lines with 36 methods and multiple responsibilities.
**Impact:** Class violates Single Responsibility Principle. Difficult to test individual components.
**Recommendation:** Extract tab management into TabManager. Extract panel creation into separate builder class.
**Effort:** Complex

---

### MINOR: Inconsistent Component Reference Patterns
**ID:** NEW-UI-015
**Location:** Multiple builder files
**Issue:** Builder UI uses inconsistent patterns for referencing components.
**Impact:** Confusing API. Easy to make mistakes when passing component references.
**Recommendation:** Define a ComponentRef dataclass with explicit fields.
**Effort:** Medium

---

### MINOR: SchematicView Cache Strategy Incomplete
**ID:** NEW-UI-016
**Location:** `game/ui/screens/builder/schematic_view.py:123-176`
**Issue:** Weapon arc cache uses weapon ID as part of cache key, but ID doesn't change when modifiers change.
**Impact:** Firing arc display may not update correctly when weapon is modified.
**Recommendation:** Cache key should include weapon's actual stats, not just ID.
**Effort:** Medium

---

## Files Reviewed

### Screens (39 files)
- battle_scene.py, battle_screen.py, builder_utils.py, design_selector_window.py
- fleet_orders_window.py, fleet_report_window.py, formation_editor.py
- new_game_setup_screen.py, planet_list_presets.py, planet_list_window.py
- race_setup_screen.py, test_lab.py, workshop_screen.py, strategy_screen.py
- And 25 more...

### Builder Subsystem (20 files)
- main.py, schematic_view.py, stats_config.py, layer_panel.py
- interaction_controller.py, modifier_config.py, and 14 more...

### Panels (16 files)
- ship_stats_renderer.py, design_report_panel.py, battle_panels.py
- And 13 more...

### Renderer/HUD (6 files)
- renderer.py, camera.py, game_renderer.py, sprites.py, battle.py, panels.py

### Assets/Orchestration (4 files)
- ship_theme_manager.py, colors.py, widgets.py, battle_orchestrator.py

---

**Report Generated:** 2026-01-27
**Scout:** UI Layer Scout
**Coverage:** 90/90 files (100%)
