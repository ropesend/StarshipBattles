# Code Quality Analyst Report

## Summary
- **Total Issues Found:** 47
- **Critical:** 8, **Major:** 19, **Minor:** 15, **Info:** 5

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

### CQ-036: Unclear Layering
**ID:** CQ-036
**Location:** Throughout codebase
**Issue:** Cross-imports between UI, Strategy, and Simulation layers; no clear boundaries
**Impact:** Circular dependencies possible; hard to reason about data flow
**Recommendation:** Enforce strict layer boundaries; create explicit Adapter/Facade layer
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

---

## Major Issues - Cross-Layer Dependencies

### CQ-019: UI Layer Imports Simulation
**ID:** CQ-019
**Location:** `game/ui/screens/setup.py:14-15`, `game/ui/screens/builder/main.py:30-32`
**Issue:** UI files import Ship, VEHICLE_CLASSES, design components from simulation layer
**Recommendation:** Create Adapter/Facade layer - expand workshop_context.py usage
**Effort:** Complex

---

### CQ-020: Inconsistent Import Patterns
**ID:** CQ-020
**Location:** Throughout codebase
**Issue:** Mix of relative and absolute imports
**Recommendation:** Standardize to absolute imports
**Effort:** Simple (automated)

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

## Top 5 Priority Issues (By Impact + Effort Ratio)

1. **CQ-007: Extract Duplicate Quickstart Methods** (Impact: High, Effort: Low)
   - 48 lines of duplicated code; easy wins for code cleanliness

2. **CQ-016: Centralize Magic UI Constants** (Impact: Medium, Effort: Low)
   - ~200+ magic numbers scattered; consolidating improves maintainability

3. **CQ-001: Refactor RaceSetupScreen** (Impact: High, Effort: High)
   - Largest UI class at 1,231 lines; highest complexity

4. **CQ-021: Add Missing Docstrings** (Impact: Medium, Effort: Medium)
   - 19 files without documentation; improves understanding

5. **CQ-036: Establish Clear Layering** (Impact: Critical, Effort: High)
   - Architectural issue affecting entire codebase; enables future refactoring
