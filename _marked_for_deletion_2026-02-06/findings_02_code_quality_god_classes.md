# Code Quality & God Classes

**Theme:** Oversized classes, Single Responsibility Principle violations, code duplication, SOLID violations, and maintainability issues.

---

## Critical Issues - God Classes

### CQ-001: RaceSetupScreen Exceeds Size Limit
**ID:** CQ-001
**Location:** `game/ui/screens/race_setup_screen.py:1-1231` (1,231 lines)
**Issue:** UIWindow subclass with 1,231 lines, handling 5 tabs, multiple galleries, validation, and persistence
**Impact:** Very difficult to test, maintain, and extend. Multiple responsibilities merged
**Recommendation:** Extract each tab into a dedicated panel component. Create RaceSetupCoordinator to manage tab transitions
**Effort:** Complex

---

### CQ-002: FormationEditor Exceeds Size Limit
**ID:** CQ-002
**Location:** `game/ui/screens/formation_editor.py:1-1103` (1,103 lines)
**Issue:** Single class handling UI, data model, rendering, and event handling
**Impact:** Difficult to test rendering vs. data model logic separately
**Recommendation:** Separate FormationCore (data) and FormationEditor (UI). Create FormationRenderer
**Effort:** Complex

---

### CQ-003: BuilderSceneGUI Exceeds Size Limit
**ID:** CQ-003
**Location:** `game/ui/screens/builder/main.py:1-1100` (1,100 lines)
**Issue:** 72+ methods handling component selection, stats, modifiers, rendering, and serialization
**Impact:** Single point of failure, hard to parallelize work
**Recommendation:** Extract component selection to ComponentSelectionController, stats to StatsPanel, modifier editing to ModifierController
**Effort:** Complex

---

### CQ-004: Ship Class Exceeds Limit
**ID:** CQ-004
**Location:** `game/simulation/entities/ship.py:1-834` (834 lines)
**Issue:** Combines physics (ShipPhysicsMixin), combat (ShipCombatMixin), and core ship data
**Impact:** Hard to test physics separate from combat; multiple reasons to change
**Recommendation:** Fully decompose using composition instead of mixins. Consider Strategy pattern
**Effort:** Complex

---

### CQ-005: ShipCombatEngine Exceeds Reasonable Size
**ID:** CQ-005
**Location:** `game/simulation/entities/ship_combat_engine.py:1-655` (655 lines)
**Issue:** Handles targeting, lead calculation, firing, damage - single responsibility violated
**Impact:** Changes to any weapon type affect entire system
**Recommendation:** Extract into WeaponFiringStrategy, TargetSelector, DamageCalculator
**Effort:** Complex

---

### CQ-006: BattleController High Complexity
**ID:** CQ-006
**Location:** `game/simulation/battle_controller.py:1-889` (889 lines)
**Issue:** 40+ methods managing battle setup, execution, retreat, reinforcements across 4 battle modes
**Impact:** Difficult to test individual battle modes independently
**Recommendation:** Extract each mode into dedicated BattleMode handler
**Effort:** Complex

---

### CQ-01: God Class - Component System (878 LOC)
**ID:** CQ-01
**Location:** `game/simulation/components/component.py:1-879`
**Issue:** Single Component class handles all aspects: initialization, abilities, modifiers, stats recalculation, damage tracking, and resource management across 878 lines. The class violates SRP with 40+ methods covering disparate concerns.
**Impact:** Extremely difficult to test, maintain, and extend. Changes to any feature risk cascading failures.
**Recommendation:** Extract separate classes: AbilityManager, ModifierManager, StatsCalculator, ResourceCostCalculator. Use composition pattern.
**Effort:** Complex

---

### CQ-09: God Class - Builder GUI (1100 LOC)
**ID:** CQ-09
**Location:** `game/ui/screens/builder/main.py:1-1100`
**Issue:** BuilderSceneGUI mixes UI rendering, event handling, selection logic, data persistence, and validation. 40+ attributes.
**Impact:** New developers need 2+ days to understand flow. Adding features breaks existing code.
**Recommendation:** Split into BuilderPresentation, BuilderModel, BuilderController using MVC.
**Effort:** Complex

---

### SIM-001: God Class - Ship Entity Too Large and Complex
**ID:** SIM-001
**Location:** `game/simulation/entities/ship.py:1-835 (834 LOC)`
**Issue:** Ship class has 834 lines with multiple responsibilities: physics, combat, components, stats, serialization, and formation. Contains 60+ attributes and mixes presentation with domain logic.
**Impact:** Difficult to test, high maintenance burden, difficult to extend without side effects. Already partially decomposed but still oversized.
**Recommendation:** Complete PROJ-12 decomposition by extracting remaining methods into:
  - ShipPhysicsCalculator (movement calculations)
  - ShipComponentValidator (validation logic)
  - ShipLoadingController (initialization logic)
**Effort:** Complex

---

### CQ-044: No Type Safety in Ship Component System
**ID:** CQ-044
**Location:** `game/simulation/components/component.py:91`
**Issue:** Component data stored as Dict[str, Any]; no schema validation
**Impact:** JSON schema mismatches not caught until runtime
**Recommendation:** Use Pydantic models or dataclass with validation
**Effort:** Complex

---

### UI-004: Massive Monolithic Screen Files (1200+ LOC)
**ID:** UI-004
**Location:**
- `game/ui/screens/race_setup_screen.py` - **1231 lines**
- `game/ui/screens/formation_editor.py` - **1103 lines**
- `game/ui/screens/builder/main.py` - **1100 lines**
- `game/ui/screens/fleet_report_window.py` - **1034 lines**

**Issue:** Single files handling multiple unrelated concerns (UI layout, event handling, data management, business logic). Makes testing, debugging, and modification extremely difficult. Changes to one concern risk breaking another. Lines of code exceed recommended threshold (400-600 lines per file).
**Impact:** High cognitive load for developers, difficult to test individual features, hard to reuse components, tight coupling between concerns, slow to compile/load these modules.
**Recommendation:**
- Split race_setup_screen into: RaceSummaryPanel, RaceVisualsPanel, RaceEnvironmentPanel, RaceDescriptionPanel
- Split formation_editor into FormationCore (model), FormationRenderer, FormationInputHandler, FormationUI
- Split builder/main.py into BuilderGUI (orchestrator), BuilderLayout, BuilderStateManager, and component-specific panels
- Use composition pattern to combine sub-modules
**Effort:** Complex (2-3 days refactoring per file)

---

## Major Issues - DRY Violations

### CQ-007: Duplicate Quickstart Methods
**ID:** CQ-007
**Location:** `game/app.py:280-328`
**Issue:** `start_quickstart_1p()` and `start_quickstart_2p()` are nearly identical (48 lines each)
**Impact:** Maintenance burden - bug fixes must be applied twice
**Recommendation:** Extract common logic to `_start_quickstart(empire_ids)` helper
**Effort:** Simple

---

### CQ-008: Duplicate Window Creation Pattern
**ID:** CQ-008
**Location:** `game/app.py:211-360`
**Issue:** Three window creation methods all follow identical pattern - 40+ duplicated lines
**Impact:** Layout/positioning code duplicated
**Recommendation:** Create `_create_centered_window(width, height, WindowClass, ...)` helper
**Effort:** Simple

---

### CQ-009: Duplicate Tab/Panel Navigation
**ID:** CQ-009
**Location:** `game/ui/screens/race_setup_screen.py`
**Issue:** Each tab has identical create/show/hide lifecycle but no shared pattern
**Recommendation:** Create TabManager or PanelController base class
**Effort:** Medium

---

### CQ-010: Repeated Magic Rect Calculations
**ID:** CQ-010
**Location:** Multiple UI files
**Issue:** Calculations like `pygame.Rect(x, y - self.scroll_offset, w, h)` appear in 6+ files
**Recommendation:** Create UILayoutHelper with preset calculations
**Effort:** Medium

---

### CQ-04: Duplicate Code - Image Scaling Pattern
**ID:** CQ-04
**Location:** `game/ui/screens/race_setup_screen.py:879-914` (and 10+ other files)
**Issue:** Same image scaling pattern repeated verbatim across 10+ files.
**Impact:** Bug fixes require changes in 10+ places. Maintenance burden.
**Recommendation:** Extract utility function `scale_to_fit(surface, max_w, max_h)` in ui/utils.py
**Effort:** Simple

---

## Major Issues - Long Methods

### CQ-011: ShipStatsCalculator.calculate()
**ID:** CQ-011
**Location:** `game/simulation/systems/stats.py:14-300+` (200+ lines)
**Issue:** Single method handling 6 phases of stat calculation
**Recommendation:** Extract each phase into dedicated method
**Effort:** Medium

---

### CQ-012: BuilderSceneGUI._create_ui()
**ID:** CQ-012
**Location:** `game/ui/screens/builder/main.py:150-250`
**Issue:** Creates all UI panels in single method; unclear dependency between elements
**Recommendation:** Extract to dedicated panel creators
**Effort:** Medium

---

### CQ-03: High Cyclomatic Complexity - Validation Rules
**ID:** CQ-03
**Location:** `game/simulation/systems/validator.py:120-180`
**Issue:** LayerRestrictionDefinitionRule.validate() has 7 nested conditionals checking block/allow rules with repeated string parsing and loose coupling to rule format.
**Impact:** Hard to add new rule types. String parsing errors go undetected.
**Recommendation:** Create Rule class hierarchy (BlockRule, AllowRule) with polymorphic validate().
**Effort:** Medium

---

## Major Issues - SOLID Violations

### CQ-023: Single Responsibility Violation (RaceSetupScreen)
**ID:** CQ-023
**Location:** `game/ui/screens/race_setup_screen.py:38`
**Issue:** Class responsible for: tab management, visual asset selection, environment configuration, text entry, validation, persistence - 7 reasons to change
**Recommendation:** Decompose into RaceSetupCoordinator + dedicated panel classes
**Effort:** Complex

---

### CQ-024: Open/Closed Violation (BattleMode Handling)
**ID:** CQ-024
**Location:** `game/simulation/battle_controller.py`
**Issue:** Each new battle mode requires modifying BattleController with new case
**Recommendation:** Use Strategy pattern with BattleMode interface implementations
**Effort:** Complex

---

### CQ-025: Interface Segregation Violation
**ID:** CQ-025
**Location:** `game/simulation/entities/ship.py`
**Issue:** Ships forced to implement physics, combat, and formation interfaces even if not needed
**Recommendation:** Use composition over inheritance; inject only needed behaviors
**Effort:** Complex

---

### CQ-026: Dependency Inversion Violation
**ID:** CQ-026
**Location:** `game/ui/screens/`
**Issue:** High-level UI depends on low-level simulation entities
**Recommendation:** Create ViewModel/Adapter layer - expand WorkshopContext usage
**Effort:** Complex

---

### AR-03: Feature Envy - Builder Components Accessing Ship Internals
**ID:** AR-03
**Location:** `game/ui/screens/builder/main.py:90-91,569,859-860,972`
**Issue:** Builder UI extensively accesses and manipulates ship component layers, modifiers, and design data. Performs business logic that belongs in simulation layer.
**Impact:** Duplicate validation logic. Ship design logic spread across UI and simulation.
**Recommendation:** Extract ship builder logic into `ShipDesignService` in simulation layer.
**Effort:** Complex

---

## Major Issues - Magic Values

### CQ-016: Hardcoded Magic Numbers in UI Layout
**ID:** CQ-016
**Location:** Multiple UI files
**Issue:** Magic values throughout: `WEAPON_ROW_HEIGHT = 45`, `WEAPON_ICON_SIZE = 32`, window dimensions 1800x1200, 650x600 without constants
**Recommendation:** Create `UIConstants` class or `ui_layout.yaml` config file
**Effort:** Simple-Medium

---

### CQ-017: Hardcoded Resolution Values
**ID:** CQ-017
**Location:** `game/app.py:82-87`, 10+ files
**Issue:** Resolution checks scattered: `if monitor_w >= 3840 and monitor_h >= 2160:`
**Recommendation:** Centralize to `DisplayConfig`
**Effort:** Simple

---

### CQ-018: Magic Damage Threshold
**ID:** CQ-018
**Location:** `game/simulation/systems/stats.py:75`, `game/strategy/services/ship_stats_service.py:32`
**Issue:** Two different damage thresholds (50% vs 30%) in different modules
**Recommendation:** Centralize damage model to single constant; add documentation
**Effort:** Simple

**FLAG - CONFLICTING VALUES:** This issue identifies that different modules use different damage thresholds (50% vs 30%). This needs resolution to determine which is correct.

---

### CQ-07: Magic Numbers Throughout
**ID:** CQ-07
**Location:** Multiple UI screens: `builder/weapons_panel.py:10-75`, `race_setup_screen.py:862`
**Issue:** Hardcoded values like `0.5` for damage threshold, `150` for ship preview size with no context.
**Impact:** Hard to maintain consistent UI theme. Scaling to different resolutions requires grep-and-replace.
**Recommendation:** Create UIConstants class with named fields.
**Effort:** Medium

---

### SIM-010: Magic Numbers and Constants Scattered Throughout
**ID:** SIM-010
**Location:** Multiple files:
  - `game/simulation/managers/retreat_manager.py:33` (required_ticks: int = 500)
  - `game/simulation/managers/retreat_manager.py:49` (DEFAULT_EDGE_THRESHOLD = 500)
  - `game/simulation/battle_controller.py:51` (max_ticks: int = 100000)
  - `game/simulation/battle_controller.py:71` (map_bounds: tuple = (0, 0, 100000, 100000))
**Issue:** Constants like 500, 100000 repeated without explanation. Threshold values hardcoded in method parameters.
**Impact:** Difficult to tune game behavior, inconsistent values across code, no single source of truth.
**Recommendation:** Create `game/simulation/constants.py` with all tuning constants. Document what each one controls.
**Effort:** Simple

---

## Major Issues - Code Smells

### CQ-027: Feature Envy
**ID:** CQ-027
**Location:** `game/ui/screens/strategy_renderer.py:305+`
**Issue:** Methods access object properties and methods more than their own
**Recommendation:** Move methods closer to data they operate on
**Effort:** Medium

---

### CQ-028: Data Clumps
**ID:** CQ-028
**Location:** Various coordinate/rect calculations
**Issue:** (x, y, width, height) used together but not grouped into objects
**Recommendation:** Create dedicated layout helper objects
**Effort:** Medium

---

### CQ-029: Primitive Obsession
**ID:** CQ-029
**Location:** `game/strategy/data/ship_instance.py`, `game/simulation/battle_state.py`
**Issue:** Using Dict[str, Any] instead of typed dataclasses for ship damage tracking
**Recommendation:** Create ComponentDamageInfo, ResourceLevels dataclasses
**Effort:** Medium

---

### AR-09: Constructor Parameter Overload - UI Components
**ID:** AR-009
**Location:** `game/ui/screens/builder/structure_list_items.py`
**Issue:** Multiple UI component classes have excessive constructor parameters (9+ params):
- `IndividualComponentItem.__init__` (9 params)
- `LayerHeaderItem.__init__` (9 params)
- `ComponentGroupItem.__init__` (10+ params)

**Impact:** Difficult to instantiate, violates Single Responsibility Principle
**Recommendation:** Use builder pattern or configuration objects.
**Effort:** Simple

---

## Minor Issues

### CQ-10: Inconsistent Naming
**ID:** CQ-10
**Location:** `game/ui/screens/fleet_report_window.py:45-65`
**Issue:** Mix of naming conventions: `sidebar_width` vs `self.header_height`. Some abbreviations, others spelled out.
**Impact:** New contributors follow wrong patterns.
**Recommendation:** Establish naming guide with consistent suffixes.
**Effort:** Simple

---

### CQ-11: Unused Parameters
**ID:** CQ-11
**Location:** `game/ui/screens/race_setup_screen.py:250`
**Issue:** Methods with partially used parameters like `stats` passed but not always accessed.
**Impact:** IDE warnings ignored. Dead code pathway confusion.
**Recommendation:** Remove unused params or document why retained.
**Effort:** Simple

---

### CQ-06: Single Letter Variables
**ID:** CQ-06
**Location:** Multiple files - `game/ui/screens/planet_list_window.py:156-157`, `game/ui/screens/race_setup_screen.py:810-926`
**Issue:** Loop variables named `i`, `x`, `y`, `w`, `h` in complex layout logic.
**Impact:** Cognitive overhead. Copy-paste bugs when similar loops are duplicated.
**Recommendation:** Use descriptive names: `formation_index`, `x_pos`, `panel_width`.
**Effort:** Simple

---

### CQ-08: Complex Conditional - Ship Stats Calculation
**ID:** CQ-08
**Location:** `game/simulation/systems/stats.py:74-82`
**Issue:** Damage threshold check uses conditional with inverted logic and duplicated damage checks.
**Impact:** Armor damage logic scattered. Hard to verify correctness.
**Recommendation:** Extract `check_component_damage(comp)` method with clear intent.
**Effort:** Simple

---

## Code Quality Metrics

| Metric | Count |
|--------|-------|
| Files >500 LOC | 24 files (god class risk) |
| Methods without type hints | 202 methods |
| Files without docstrings | 19 files |
| Bare except clauses | 68 files |
| Average file size | 265 LOC (highest: 1,231) |
| Classes with >20 methods | ~8 |
| Cross-layer imports | 15+ UI files importing from simulation |

---

## Top Priority Issues

1. **CQ-001/CQ-002/CQ-003: Refactor God Classes** - RaceSetupScreen, FormationEditor, BuilderSceneGUI each exceed 1000+ LOC
2. **CQ-007/CQ-008: Extract Duplicate Code** - Quick wins for code cleanliness with quickstart and window creation
3. **CQ-016/CQ-07: Centralize Magic UI Constants** - ~200+ magic numbers scattered; consolidating improves maintainability
4. **CQ-01: Component System God Class** - 878 LOC affects entire simulation layer
5. **SIM-001: Ship Entity Decomposition** - Complete PROJ-12 to finish decomposition
