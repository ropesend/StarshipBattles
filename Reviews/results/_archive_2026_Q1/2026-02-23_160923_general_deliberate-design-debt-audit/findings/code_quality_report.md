# Code Quality Analyst Report

## Summary
- Total issues found: 89 (grouped)
- Critical: 8, Major: 12, Minor: 11, Info: 5

## Findings

### CRITICAL: God Class - TestLabScreen
**ID:** CQ-001
**Location:** `game/ui/screens/test_lab/screen.py` (1906 lines, 74 methods)
**Issue:** Massive class violating Single Responsibility Principle. Handles UI creation, event routing, validation management, test execution, data extraction, JSON viewing, panel management, and more.
**Impact:** Extremely difficult to test, modify, or understand. Changes ripple unpredictably.
**Deliberate?:** Likely accidental accumulation - started as simple screen, grew organically
**Recommendation:** Extract into multiple classes: TestLabUIBuilder, TestLabEventHandler, TestLabDataManager, core TestLabScreen (coordination only)
**Effort:** Complex

### CRITICAL: Extreme Deep Nesting (20 levels)
**ID:** CQ-002
**Location:** `game/ui/screens/fleet_report_view_model.py:77` `toggle_filter()`
**Issue:** 20 levels of nesting in a simple filter toggle function - massive if/elif chain for 10+ filter types
**Impact:** Unmaintainable, error-prone, violates cyclomatic complexity limits
**Deliberate?:** Likely deliberate but poor design choice - chose explicit if/elif over dictionary dispatch for "clarity"
**Recommendation:** Use dictionary mapping for filter flags
**Effort:** Simple

### CRITICAL: Deep Nesting in Column Value Extraction (14 levels)
**ID:** CQ-003
**Location:**
- `game/ui/screens/column_manager.py:141` `get_column_value()` (14 levels)
- `game/ui/screens/fleet_report_filters.py:241` `get_sort_key()` (13 levels)
**Issue:** Massive if/elif chains for 15+ column types, repeated pattern across sorting and display
**Impact:** DRY violation, maintenance burden (adding a column requires 2-3 file changes)
**Deliberate?:** Likely deliberate - explicit dispatch chosen over polymorphism
**Recommendation:** Column strategy pattern or dictionary dispatch
**Effort:** Medium

### CRITICAL: Extremely Long Method - _init_sidebar (353 lines)
**ID:** CQ-004
**Location:** `game/ui/screens/fleet_report_window.py:_init_sidebar`
**Issue:** Single method creates entire sidebar UI with repeated button creation patterns
**Impact:** Impossible to understand at a glance, high duplication
**Deliberate?:** Likely deliberate - UI initialization kept in single method for "locality"
**Recommendation:** Extract filter group creation helpers
**Effort:** Simple

### CRITICAL: Massive Strategy Panel Creation (285 lines)
**ID:** CQ-005
**Location:** `game/ui/screens/strategy_panel_manager.py:285` `create_strategy_panels()`
**Issue:** 285-line method creating all UI panels with heavy procedural code
**Impact:** Monolithic, hard to test individual panels
**Deliberate?:** Likely deliberate - kept together for "initialization sequence"
**Recommendation:** Extract panel creation methods (one per panel type)
**Effort:** Medium

### CRITICAL: God Class - FormationEditorScreen (51 methods)
**ID:** CQ-006
**Location:** `game/ui/screens/formation_editor.py` (941 lines, 51 methods)
**Issue:** Handles rendering, input, UI creation, formation logic, ship management, file I/O
**Impact:** SRP violation, difficult to test
**Deliberate?:** Likely accidental accumulation
**Recommendation:** Extract FormationRenderer, FormationInputHandler, FormationFileIO
**Effort:** Complex

### CRITICAL: God Class - StrategyScreen (46 methods)
**ID:** CQ-007
**Location:** `game/ui/screens/strategy_screen.py` (823 lines, 46 methods, 44 imports)
**Issue:** Main strategy screen handles everything: rendering, input, camera, fleet ops, colonization, UI windows
**Impact:** Central point of failure
**Deliberate?:** Partially deliberate - coordinator pattern, but accumulated too many responsibilities
**Recommendation:** Continue extraction (partially done already)
**Effort:** Complex

### CRITICAL: Circular Dependency Workarounds (7 occurrences)
**ID:** CQ-008
**Location:**
- `game/ui/screens/fleet_report_filters.py:260-261`
- `game/ui/screens/column_manager.py:181-182`
- `game/strategy/data/fleet.py`
- `game/strategy/data/fleet_capability_calculator.py`
- `game/strategy/engine/game_session.py`
- `game/strategy/data/ship_instance.py`
- `game/simulation/entities/ship_stat_querier.py`
**Issue:** Architecture has circular dependencies "solved" with late imports marked "INTENTIONAL LATE IMPORT"
**Impact:** Indicates layering violation, confusing dependency graph, runtime import overhead
**Deliberate?:** Definitely deliberate workaround for deeper architectural issue
**Recommendation:** Fix actual dependencies - move shared calculations to neutral layer, use DI
**Effort:** Complex

### MAJOR: Long Methods (30 occurrences >100 lines)
**ID:** CQ-009
**Location:**
- `game/ui/panels/system_tree_panel.py::set_items` (212 lines)
- `game/strategy/services/ship_stats_calculator.py::calculate_stats` (215 lines)
- `game/ui/screens/planet_list_sidebar.py::build_sidebar` (243 lines)
- `game/ui/research/research_controls.py::_create_ui` (174 lines)
- `game/strategy/engine/production_engine.py::_process_queue_tick_dynamic` (173 lines)
- `game/ui/screens/galaxy_test/galaxy_mode.py::create_ui` (162 lines)
- `game/research/systems/research_service.py::process_turn` (154 lines)
- `game/ui/panels/ship_detail_panel.py::_build_ship_display` (149 lines)
- `game/simulation/entities/ship.py::__init__` (144 lines)
- 19+ more >100 lines
**Issue:** Methods too long to understand at a glance, violate SRP
**Impact:** Hard to test, high cognitive load
**Deliberate?:** Mixed - some deliberate (Ship.__init__ initializing 40+ attributes), others accumulation
**Recommendation:** Extract helper methods, break into logical steps
**Effort:** Simple to Medium per method

### MAJOR: Deep Nesting in Input Handlers (8+ levels, 30 occurrences)
**ID:** CQ-010
**Location:**
- `game/ui/screens/formation_editor.py:727` `_handle_button_pressed()` (14 levels)
- `game/ui/screens/strategy_input_handler.py:235` `_handle_ui_action()` (14 levels)
- `game/ui/screens/strategy_input_handler.py:314` `handle_click()` (12 levels)
- `game/ui/screens/strategy_event_router.py:136` `_handle_button_pressed()` (12 levels)
- `game/ui/screens/workshop_event_router.py:290` `_handle_button_pressed()` (12 levels)
- 23+ more with 7-10 levels
**Issue:** Complex nested conditionals, hard to follow logic flow
**Impact:** High cyclomatic complexity, difficult to test all branches
**Deliberate?:** Likely deliberate - chose if/elif chains over command pattern
**Recommendation:** Extract methods for each branch, use command/strategy patterns, early returns
**Effort:** Medium

### MAJOR: God Classes (11 classes with >30 methods)
**ID:** CQ-011
**Location:**
- `Ship` (41 methods), `ShipInstance` (44 methods), `Fleet` (41 methods)
- `IControllable` (38 methods), `ShipControllableAdapter` (40 methods)
- `StrategyUI` (39 methods), `WorkshopViewModel` (37 methods)
- `Game` (39 methods), `BattleController` (30 methods)
- `BuildQueueScreen` (30 methods), `EmpireBuildQueueWindow` (30 methods)
**Issue:** Classes with too many responsibilities
**Impact:** Violates SRP, difficult to maintain/test
**Deliberate?:** Mixed - domain entities have legitimate complexity; UI coordinators accumulated
**Recommendation:** Domain entities: accept or extract services; UI classes: extract sub-coordinators
**Effort:** Medium to Complex

### MAJOR: Excessive Parameters (13 functions with >9 parameters)
**ID:** CQ-012
**Location:**
- `game/strategy/formulas/habitability.py:213` (13 params)
- `game/ui/screens/workshop_data_reloader.py:46` (13 params)
- `game/strategy/engine/turn_engine.py:97` (12 params)
- `game/ui/screens/build_queue_screen.py:45` (12 params)
- 6+ more with 9-10 params
**Issue:** Too many parameters, hard to call correctly
**Impact:** Function calls are error-prone, difficult to evolve API
**Deliberate?:** Likely deliberate - explicit parameters over config objects for "clarity"
**Recommendation:** Use parameter objects / data classes, builder pattern, DI
**Effort:** Medium

### MAJOR: Excessive Imports (9 files with >20 imports)
**ID:** CQ-013
**Location:**
- `game/app.py` (49 imports)
- `game/ui/screens/strategy_screen.py` (44 imports)
- `game/ui/screens/workshop_screen.py` (30 imports)
- `game/ui/screens/build_queue_screen.py` (29 imports)
- `game/simulation/components/component.py` (27 imports)
**Issue:** High coupling
**Impact:** Difficult to understand dependencies, circular dependency risk
**Deliberate?:** Partially - app.py is entry point (acceptable)
**Recommendation:** Consider facade pattern, extract submodules
**Effort:** Medium

### MAJOR: Massive if/elif Chains for Modifier Logic
**ID:** CQ-014
**Location:**
- `game/simulation/services/modifier_service.py:134` (10 levels)
- `game/ui/screens/builder/modifier_logic.py:75` (8 levels)
- `game/simulation/components/modifiers.py:51` (9 levels)
**Issue:** Deep nesting in modifier evaluation
**Impact:** Hard to add new modifier types
**Deliberate?:** Likely deliberate - explicit handling over data-driven config
**Recommendation:** Use modifier registry with formula evaluation
**Effort:** Complex

### MAJOR: Repeated UI Creation Code (30 occurrences)
**ID:** CQ-016
**Location:**
- `game/ui/screens/design_selector_window.py` - 30 near-identical button creation blocks
- `game/ui/panels/race_aptitudes_panel.py` - 18 repeated header creation
- `game/ui/screens/test_lab/test_run_details.py` - 17 repeated label blitting
- `game/strategy/engine/command_handlers.py` - 16 repeated fleet lookups
- `game/simulation/components/abilities/crew.py` - 15 repeated ability __init__
**Issue:** Severe DRY violation, copy-paste programming
**Impact:** Bug multiplication, maintenance burden
**Deliberate?:** Mixed
**Recommendation:** Extract factory methods/builders for UI creation patterns
**Effort:** Simple to Medium

### MAJOR: Single-Letter Parameter Names (56 occurrences)
**ID:** CQ-018
**Location:** Throughout codebase: `r` (13), `q` (10), `w` (7), `h` (6), `p` (6)
**Issue:** Poor readability, unclear parameter purpose
**Impact:** Hard to understand function signatures
**Deliberate?:** Likely deliberate - brevity for "simple" functions
**Recommendation:** Use descriptive names: rect, queue, width, height
**Effort:** Simple

### MAJOR: Missing Class Docstrings (37 classes)
**ID:** CQ-019
**Location:** Ship, Projectile, Component, PhysicsBody, AttackType, GameState, ComponentStatus, OrderType, CrewCapacity, LifeSupportCapacity, FleetOrder, WarpPoint, StarSystem, AIBehavior, etc.
**Issue:** Core classes lack documentation
**Impact:** Hard for new developers to understand purpose
**Deliberate?:** Likely accidental - documentation debt
**Recommendation:** Add docstrings to core classes
**Effort:** Simple (per class)

### MINOR: Explicit return None (190 occurrences)
**ID:** CQ-020
**Location:** 79 files
**Issue:** Functions explicitly return None instead of implicit
**Impact:** Minor verbosity
**Deliberate?:** Likely deliberate - explicit is better than implicit
**Recommendation:** Accept as style choice
**Effort:** Simple

### MINOR: Magic Numbers in UI Code (48 occurrences)
**ID:** CQ-021
**Location:** Various UI panels and screens
**Issue:** Hardcoded pixel positions, colors, sizes
**Impact:** Difficult to maintain consistent spacing/sizing
**Deliberate?:** Likely deliberate - pragmatic UI layout
**Recommendation:** Extract to layout constants
**Effort:** Medium

### MINOR: String Concatenation in Loops (12 occurrences)
**ID:** CQ-022
**Location:** Various UI rendering and data formatting files
**Issue:** Using += for string building in loops
**Impact:** Performance issue for large loops
**Deliberate?:** Likely accidental
**Recommendation:** Use list join or StringIO
**Effort:** Simple

### MINOR: Global Statement Usage (39 files)
**ID:** CQ-023
**Location:** Widespread - facades, data, engine, UI services, core
**Issue:** Module-level singletons and globals
**Impact:** Hidden coupling, difficult to test
**Deliberate?:** Likely deliberate - singletons for registries
**Recommendation:** Continue DI migration away from globals
**Effort:** Complex (ongoing)

### MINOR: Broad except Exception (3 occurrences)
**ID:** CQ-025
**Location:** tkinter_utils.py, race_environment_panel.py, workshop_data_reloader.py
**Issue:** Catching all exceptions masks errors
**Impact:** Bugs may be silently swallowed
**Deliberate?:** Likely deliberate - defensive UI code
**Recommendation:** Catch specific exceptions, log unexpected ones
**Effort:** Simple

### INFO: Good Practices Observed
**ID:** CQ-030
**Issue:** No mutable default arguments, no wildcard imports, consistent snake_case, no bare except clauses, growing type hints, appropriate @staticmethod/@classmethod usage (208 occurrences)

## Top 5 Priority Issues

1. **CQ-008 (CRITICAL):** Circular Dependency Workarounds — fundamental architectural issue
2. **CQ-001 (CRITICAL):** God Class TestLabScreen — 1906 lines, most extreme SRP violation
3. **CQ-002/003 (CRITICAL):** Deep Nesting in Filters/Columns — 20 levels, simple fix available
4. **CQ-016 (MAJOR):** Repeated UI Creation Code — 30+ DRY violations, high ROI fix
5. **CQ-009 (MAJOR):** Long Methods >100 lines — 30+ methods, incremental fix
