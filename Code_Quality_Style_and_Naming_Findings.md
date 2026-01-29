# Code Quality Style and Naming Findings

## File: naming_structure_report.md

# Naming and File Organization Pattern Analysis

**Agent:** Naming & Structure Analyst
**Date:** 2026-01-28
**Scope:** game/, ui/ directories (excluding tests)

---

## Summary
- Total pattern variants found: 18
- Critical inconsistencies: 0
- Major inconsistencies: 1
- Minor inconsistencies: 3
- Dominant pattern: Strong suffix conventions, snake_case methods

---

## Class Naming Patterns

### Class Suffixes

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Service (business logic) | BattleService, ResearchService | 40% | Dominant for logic |
| Manager (resource management) | AssetManager, ResourceManager | 27% | Singletons, collections |
| Panel (UI components) | BattlePanel, ShipStatsPanel | 20% | UI regions |
| Controller (orchestration) | AIController, InteractionController | 13% | Input handling |

### Other Class Patterns

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Engine suffix | BattleEngine, ShipCombatEngine | 2 classes | Core processors |
| Scene suffix | BattleScene, TestLabScene | 3 classes | Screen-level |
| Mixin suffix | ShipCombatMixin | 1 class | Compatibility |
| No suffix (data) | ComponentRef, ShipPanel | ~10% | Data holders |

---

## Method Naming Patterns

### Method Prefixes

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| `get_` (queries) | get_position(), get_velocity() | 60% | Read operations |
| `_` (private) | _calculate_firing_solution() | 70% | Internal methods |
| `is_` (boolean) | is_alive(), is_battle_over() | 40% | State checks |
| `set_` (mutations) | set_throttle(), set_value() | 35% | Property changes |
| `on_` (events) | on_selection_changed() | 15% | Event handlers |

### Verb Patterns (no prefix)

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| create_, add_, remove_ | create_battle(), add_ship() | 20% | CRUD operations |
| update(), reset() | Various managers | 15% | State changes |
| draw(), handle_ | UI components | 10% | UI operations |

---

## File Organization Patterns

### Module Structure

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Single class per file | BattleService.py, AssetManager.py | 80% | Standard |
| Related classes grouped | battle_panels.py (4 classes) | 15% | UI components |
| Many classes per file | test_lab_scene.py (10-40+) | 5% | Problematic |

### Directory Structure

```
game/
â”œâ”€â”€ core/           # Utilities, config (good)
â”œâ”€â”€ engine/         # Physics, spatial (good)
â”œâ”€â”€ simulation/     # Battle logic (good)
â”‚   â”œâ”€â”€ services/   # Business logic
â”‚   â”œâ”€â”€ systems/    # Manager systems
â”‚   â””â”€â”€ entities/   # Domain objects
â”œâ”€â”€ ai/             # AI behaviors (good)
â”œâ”€â”€ strategy/       # Strategy layer (good)
â””â”€â”€ research/       # Research system (good)

ui/ (root)          # INCONSISTENT - should be in game/ui/
â”œâ”€â”€ builder/        # Ship builder
â””â”€â”€ test_lab_scene.py
```

---

## Import Organization Patterns

### Import Ordering

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| stdlib â†’ 3rd party â†’ local | BattleService.py, most game/ | 90% | Standard |
| Mixed ordering | detail_panel.py (json after pygame) | 10% | Inconsistent |

### Import Styles

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Absolute `from game.*` | game/ directory | 85% | Dominant |
| Mixed `from ui.builder.*` | ui/ directory | 15% | Inconsistent |

---

## Key Inconsistencies

### NS-01: Dual UI Directory Structure
**Severity:** Major
**ID:** NS-01
**Location:** `game/ui/` and `ui/` (root level)
**Issue:** UI code split between two locations
**Impact:** Confusing organization, inconsistent import paths
**Recommendation:** Consolidate all UI code to `game/ui/`
**Effort:** Complex

### NS-02: Multi-Class Files
**Severity:** Minor
**ID:** NS-02
**Location:** `ui/test_lab_scene.py`, `ui/builder/` files
**Issue:** Some files contain 10-40+ classes
**Impact:** Harder to navigate, potential circular imports
**Recommendation:** Extract to single-class-per-file pattern
**Effort:** Medium

### NS-03: Mixed Import Paths
**Severity:** Minor
**ID:** NS-03
**Location:** `ui/builder/detail_panel.py`, others
**Issue:** Mix of absolute (`game.*`) and root-relative (`ui.*`) imports
**Impact:** Inconsistent import style
**Recommendation:** Standardize on absolute imports
**Effort:** Simple

### NS-04: Import Order Inconsistency
**Severity:** Info
**ID:** NS-04
**Location:** ~10 files in ui/builder/
**Issue:** stdlib imports not always first
**Impact:** Minor readability issue
**Recommendation:** Use isort or similar tool
**Effort:** Simple

---

## Recommended Standard

### Class Naming
```python
class ComponentManager:    # For resource/collection management
class BattleService:       # For business logic operations
class ShipStatsPanel:      # For UI components
class AIController:        # For input/orchestration
```

### Method Naming
```python
def get_component(self) -> Component:  # getter
def is_active(self) -> bool:           # boolean check
def _calculate_internal(self):         # private method
def on_button_clicked(self):           # event handler
def create_ship(self, config):         # factory method
```

### Import Organization
```python
# Standard library
import os
import json
from dataclasses import dataclass
from typing import Optional, List

# Third-party
import pygame
import pygame_gui

# Local (absolute)
from game.core.logger import log_error
from game.simulation.entities import Ship
```

---

## Top 5 Priority Issues

1. **NS-01:** Consider consolidating `ui/` into `game/ui/` (Major)
2. **NS-03:** Standardize import paths in ui/builder/ (~15 files)
3. **NS-04:** Apply import sorting to inconsistent files (~10 files)
4. **NS-02:** Consider splitting large multi-class files
5. Document naming conventions in coding standards

---


## File: style_idioms_report.md

# Code Style and Idiom Pattern Analysis

**Agent:** Style & Idiom Analyst
**Date:** 2026-01-28
**Scope:** game/, ui/ directories (excluding tests)

---

## Summary
- Total pattern variants found: 15
- Critical inconsistencies: 0
- Major inconsistencies: 0
- Minor inconsistencies: 2
- Dominant pattern: Modern Python with strong type hints

---

## Type Annotation Patterns

### Coverage

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Full return type annotations | Most game/ files | 95% | Excellent |
| Parameter type annotations | Most game/ files | 88% | Very good |
| Missing annotations | game/ui/screens/builder/*.py | 12% | UI builders gap |

### Style

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| `Optional[T]` style | protocols.py, fleet.py | 100% | Standard |
| `T \| None` style | resources.py | 1 occurrence | Rare/avoid |
| TYPE_CHECKING blocks | Throughout | 215+ uses | Good practice |

---

## Docstring Patterns

### Coverage

| Level | Coverage | Notes |
|-------|----------|-------|
| Module docstrings | 92% | Excellent |
| Class docstrings | 68% | Acceptable |
| Method docstrings | 52% | Weak in UI builders |

### Format

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| One-liner summary | Simple methods | 60% | Common |
| Extended with Args/Returns | Complex methods | 40% | When needed |
| PROJ-references | Throughout | 263 occurrences | Architecture tracking |

---

## Python Idiom Usage

### String Formatting

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| f-strings | Throughout codebase | 99% | Dominant |
| `.format()` method | Legacy code | ~50 occurrences | Declining |
| % formatting | Minimal | <1% | Rare |

### Comprehensions

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| List comprehensions | fleet.py, many files | 142 occurrences | Well-adopted |
| Dict comprehensions | Various | 22 occurrences | Moderate |
| Generator expressions | Data processing | Moderate | Good |

### Other Idioms

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| @property decorators | ship.py, many files | 273 uses | Heavy use |
| Context managers (with) | File I/O, resources | 215 uses | Could expand |
| @classmethod/@staticmethod | Various | ~75 uses | Appropriate |

---

## Configuration Patterns

### Constants Organization

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Class-based configs | game/core/config.py | Primary | DisplayConfig, AIConfig |
| Module constants | game/core/constants.py | Secondary | PLANET_RESOURCES |
| Color dictionaries | game/ui/colors.py | UI-specific | COLORS dict |
| Enums | Throughout | 22+ enums | AttackType, GameState |

### Issues

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Scattered constants | Multiple locations | 3+ files | Fragmented |
| Magic numbers | UI builders | ~15-20 files | Should extract |

---

## Key Inconsistencies

### STY-01: Type Annotation Gaps in UI Builders
**Severity:** Minor
**ID:** STY-01
**Location:** `game/ui/screens/builder/*.py`
**Issue:** ~12% of methods missing type annotations
**Impact:** Reduced IDE support, harder to understand interfaces
**Recommendation:** Add type hints to public methods
**Effort:** Medium

### STY-02: Docstring Coverage Gap
**Severity:** Minor
**ID:** STY-02
**Location:** `game/ui/screens/builder/*.py`, `ui/builder/*.py`
**Issue:** ~48% of methods missing docstrings
**Impact:** Reduced code discoverability
**Recommendation:** Add docstrings to public methods
**Effort:** Medium

### STY-03: Context Manager Underutilization
**Severity:** Info
**ID:** STY-03
**Location:** Various file I/O locations
**Issue:** Some file operations don't use `with` statements
**Impact:** Potential resource leaks
**Recommendation:** Migrate to context managers
**Effort:** Simple

---

## Recommended Standard

### Type Annotations
```python
from typing import Optional, Dict, List

def process_items(
    self,
    items: List[Item],
    count: int = 10
) -> Optional[Result]:
    """Process items and return result."""
    ...
```

### Docstrings
```python
def calculate_damage(self, attacker: Ship, target: Ship) -> float:
    """Calculate damage from attacker to target.

    Args:
        attacker: The attacking ship entity.
        target: The target ship entity.

    Returns:
        The calculated damage value.

    Raises:
        ValueError: If either ship is invalid.
    """
```

### Python Idioms
```python
# Prefer list comprehension
items = [x.value for x in objects if x.valid]

# Always use context manager for resources
with open(path, 'r') as f:
    data = f.read()

# Use f-strings
message = f"Processing {count} items"

# Use dictionary.get() with default
value = config.get('key', default_value)
```

### Configuration
```python
# Use class-based configuration
class UIConfig:
    PANEL_WIDTH: int = 300
    PANEL_HEIGHT: int = 400

    @classmethod
    def panel_size(cls) -> Tuple[int, int]:
        return (cls.PANEL_WIDTH, cls.PANEL_HEIGHT)
```

---

## Pattern Consistency Summary

| Category | Consistency | Standard |
|----------|-------------|----------|
| Type annotations | 95% | `Optional[T]`, not `T \| None` |
| f-strings | 99% | Always use f-strings |
| Comprehensions | High | Use when readable |
| Properties | 95% | For computed values |
| Context managers | Moderate | Expand usage |
| Constants | 75% | Class-based preferred |

---

## Top 5 Priority Issues

1. **STY-01:** Add missing type hints in UI builders (~12% gap)
2. **STY-02:** Add missing docstrings in UI builders (~48% gap)
3. Consolidate constants locations (3+ files â†’ 1-2 files)
4. Expand context manager usage for file I/O
5. Document style guidelines in coding standards

---


# Source: 2026-01-28_general_full-codebase-legacy-consistency-audit

---


## File: code_quality_analyst_report.md

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

---


## File: naming_consistency_analyst_report.md

# Naming Consistency Analyst Report

## Summary
- **Total issues found:** 24
- **Critical:** 3, **Major:** 8, **Minor:** 13

---

## Critical Issues

### NCA-001: Duplicate ShipDesignValidator Classes
**ID:** NCA-001
**Location:** `game/simulation/systems/validator.py` AND `game/simulation/ship_validator.py`
**Issue:** Two classes with identical name `ShipDesignValidator` exist in different locations, creating namespace confusion and potential import conflicts.
**Impact:** Developers may import from the wrong location; maintenance becomes difficult; refactoring errors likely.
**Recommendation:** Consolidate into single file or rename one to `ShipValidator` and `ShipDesignValidator` with clear separation of concerns.
**Effort:** Medium

---

### NCA-002: File Path Naming Inconsistency (filepath vs file_path)
**ID:** NCA-002
**Location:** Multiple locations:
  - `game/core/json_utils.py:10` uses `filepath` parameter
  - `game/assets/asset_manager.py` uses `file_path` variable
**Issue:** Parameter/variable naming mixes `filepath` and `file_path` conventions throughout the codebase (209 occurrences).
**Impact:** Inconsistent code style, harder to search/grep for file path handling, confusion for contributors.
**Recommendation:** Standardize on `file_path` (snake_case is more Pythonic). Update `json_utils.py` and all usages.
**Effort:** Simple

---

### NCA-003: Method Naming Ambiguity: get_ vs fetch_ vs retrieve_ vs load_ vs read_
**ID:** NCA-003
**Location:** 134 retrieval methods across codebase with inconsistent prefixes
**Issue:** Methods for obtaining data use varied prefixes without clear distinction:
  - `get_components()` in multiple files
  - `load_components()` in component.py
  - `load_json_required()` in json_utils.py
  - `get_all_components()` in ability_aggregator.py
**Impact:** Inconsistent API design; developers unsure which prefix to use for new methods.
**Recommendation:** Establish convention: use `get_` for simple access, `load_` for file/resource I/O, `fetch_` for remote/expensive operations.
**Effort:** Medium (requires API audit)

---

## Major Issues

### NCA-004: Calculation Method Naming Inconsistency
**ID:** NCA-004
**Location:** Multiple files across game/simulation and game/strategy
**Issue:** Methods for computing values use `calculate_` vs `recalculate_` vs `compute_`:
  - `calculate_stats()` in multiple files
  - `recalculate_stats()` in Ship and Component
  - `compute_next_step()` in pathfinding
  - `compute_path()` vs `calculate_path()`
**Impact:** Developers unsure when to use `calculate` vs `recalculate` vs `compute`.
**Recommendation:** Define: `calculate_*` for initial computation, `recalculate_*` for recomputation, avoid `compute_*`.
**Effort:** Medium

---

### NCA-005: LayerType vs Layer Terminology Inconsistency
**ID:** NCA-005
**Location:**
  - `game/simulation/components/component_constants.py` defines `LayerType` enum
  - `game/simulation/entities/ship.py:93-94` uses `layer_assigned` and `LayerType.HULL`
  - `game/simulation/battle_state.py:36` uses `layer: str` (string, not enum)
**Issue:** Component layer handling mixes enum type names with string representations; inconsistent parameter naming.
**Impact:** Type confusion; serialization issues; unclear intent in code.
**Recommendation:** Use `LayerType` enum consistently; avoid string fallback except in serialization.
**Effort:** Medium

---

### NCA-006: Service vs System vs Engine Naming Confusion
**ID:** NCA-006
**Location:** Multiple locations
  - `game/simulation/services/` has BattleService, ModifierService, VehicleDesignService
  - `game/simulation/systems/` has BattleEngine, Stats, Validator, ProjectileManager
  - `game/strategy/engine/` has TurnEngine, ConflictResolutionEngine, etc.
  - `game/strategy/services/` has ShipStatsService, FleetNavigationService
**Issue:** No clear distinction between Service/System/Engine naming across layers. Same patterns appear with different suffixes.
**Impact:** Architectural confusion; unclear responsibility distribution; difficulty in onboarding.
**Recommendation:**
  - **Service**: Business logic (ModifierService, BattleService)
  - **Engine**: State machines/simulation loops (BattleEngine, TurnEngine)
  - **Manager**: Collection/lifecycle management (ProjectileManager, BattleStateManager)
  - Consolidate Systems directory or rename appropriately
**Effort:** Complex (requires comprehensive refactoring)

---

### NCA-007: Handler Naming Inconsistency
**ID:** NCA-007
**Location:** `game/core/input_handler.py` vs `game/ui/screens/strategy_input_handler.py`
**Issue:** Input handlers use different naming patterns (InputHandler vs StrategyInputHandler). No consistent naming convention documented.
**Impact:** Unclear when to create new handlers; inconsistent class naming.
**Recommendation:** Establish pattern: `{Context}InputHandler`. Document in NAMING_CONVENTIONS.md (already started but incomplete).
**Effort:** Simple

---

### NCA-008: Validation Module Split
**ID:** NCA-008
**Location:**
  - `game/simulation/validation/base.py` (empty package)
  - `game/simulation/ship_validator.py`
  - `game/simulation/systems/validator.py` (duplicate ShipDesignValidator)
  - `game/strategy/validation/colonize_validator.py`
  - `game/ui/screens/race_validator.py`
**Issue:** Validation logic scattered across multiple directories with inconsistent organization. The `validation/` directory exists but is mostly empty.
**Impact:** Difficult to locate validation logic; potential for duplicate implementations.
**Recommendation:** Consolidate all validators into `game/simulation/validation/` directory with clear organization.
**Effort:** Medium

---

### NCA-009: Registry Access Pattern Inconsistency
**ID:** NCA-009
**Location:** Multiple locations
  - `game/simulation/entities/ship.py` uses `self._registries` (with underscore)
  - `game/simulation/components/component.py` uses `self._registries`
  - `game/simulation/battle_state.py` uses `registries.components` and `registries.modifiers`
  - `game/core/registry.py` provides both `get_component_registry()` and `get_modifier_registry()`
**Issue:** Mix of DI pattern (injected registries) and global getter functions. Inconsistent attribute naming (`_registries` vs plain access).
**Impact:** Confusion about dependency injection vs global state; inconsistent patterns.
**Recommendation:** Document registry access pattern clearly; standardize on one approach per context.
**Effort:** Medium

---

### NCA-010: Boolean Method Prefix Inconsistency
**ID:** NCA-010
**Location:** Multiple locations
**Issue:** Boolean methods use `is_`, `has_`, `can_`, `should_` inconsistently:
  - `is_operational` vs `has_space_shipyard` vs `can_fire` vs `is_damaged`
  - No clear pattern for attribute vs capability vs state distinction
**Impact:** Developers unsure which prefix to use for new boolean methods.
**Recommendation:** Establish convention:
  - `is_*`: State (is_alive, is_damaged, is_operational)
  - `has_*`: Possession/containment (has_components, has_fuel)
  - `can_*`: Capability/permission (can_fire, can_move)
  - `should_*`: Recommendation/logic (rarely used)
**Effort:** Medium

---

### NCA-011: Manager Suffix Inconsistency
**ID:** NCA-011
**Location:** `game/simulation/entities/`
**Issue:** Only two mixins found with Mixin suffix:
  - `ShipPhysicsMixin`
  - `ShipCombatMixin`
  Other behavioral classes don't follow Mixin pattern (e.g., ShipStatsCalculator, ShipComponentManager).
**Impact:** Inconsistent code style; unclear composition pattern.
**Recommendation:** Either apply Mixin suffix consistently or rename existing mixins to appropriate suffixes.
**Effort:** Simple

---

## Minor Issues

### NCA-012: Private Attribute Base Value Naming
**Location:** `game/simulation/components/abilities/` (multiple files)
**Issue:** Private base value attributes use `_base_` prefix inconsistently:
  - `_base_damage`, `_base_range`, `_base_reload` in weapons.py
  - `_base_amount` in crew.py
  - `_base_value` in defense.py
  - `_base_capacity` in markers.py
  - `_base_rate` in resources.py
**Recommendation:** Standardize on consistent naming: `_original_*` or `_base_*` uniformly.
**Effort:** Simple

### NCA-013: UI Component Naming: Panel vs Widget
**Location:** `game/ui/` directory
**Issue:** UI components use Panel suffix but not Widget (no Widget classes found despite builder_widgets.py existing).
**Recommendation:** Use Panel for major sections, Widget for smaller composable elements. Document in UI_STYLE_GUIDE.md.
**Effort:** Simple

### NCA-014: Document Terminology Mismatch: "modifier" vs "effect"
**Location:** Across multiple documentation files
**Issue:**
  - `docs/modifier_system.md` uses "modifier"
  - `game/simulation/components/modifier_effects.py` uses "effect"
  - `game/simulation/components/modifiers.py` has `apply_modifier_effects()` mixing both terms
**Recommendation:** Consistently use "Modifier" as the domain concept and "ModifierEffect" as the evaluated result. Update all docs.
**Effort:** Simple

### NCA-015: Stat vs Attribute Naming
**Location:** Multiple locations
**Issue:**
  - Some files use "stat" (stats.py, stat_keys.py, calculate_stats)
  - Some contexts reference "attributes" (core/protocols.py)
  - NAMING_CONVENTIONS refers to "stats"
**Recommendation:** Standardize terminology docs explicitly; use "stat" throughout code, "attribute" for UI display only.
**Effort:** Simple

### NCA-016: Test File Naming Inconsistency
**Location:** `simulation_tests/` vs `tests/`
**Issue:** Test files use inconsistent naming:
  - `test_framework/scenarios/gun_accuracy_test.py` (suffix: test)
  - `simulation_tests/tests/test_beam_weapons.py` (prefix: test_)
  - `tests/integration/test_fleet_combat.py` (prefix: test_)
**Recommendation:** Standardize on `test_*` prefix for all test files. Consolidate test directories.
**Effort:** Medium

### NCA-017: Ability vs Component Terminology
**Location:** Across codebase
**Issue:**
  - Components contain Abilities
  - But naming sometimes mixes them: "ability_instances", "ability_aggregator"
  - Documentation (NAMING_CONVENTIONS.md) distinguishes them clearly, but code doesn't always follow.
**Recommendation:** Code already follows conventions well; ensure documentation is referenced.
**Effort:** Simple (docs/education only)

### NCA-018: Formation vs Composition Naming
**Location:** `game/simulation/entities/ship.py:154`
**Issue:** Comment says "Formation (Composition - delegates to ShipFormation)" but attribute is `formation` not `composition`.
**Recommendation:** Either rename `formation` to `composition` or remove confusing comment.
**Effort:** Simple

### NCA-019: Strategy vs Game Session Naming
**Location:** `game/strategy/engine/game_session.py`
**Issue:** Strategy layer uses GameSession for overall orchestration, but similar concepts exist at other layers without consistent naming.
**Recommendation:** Document strategy layer naming conventions clearly.
**Effort:** Simple

### NCA-020: Renderer vs Rendering Class Naming
**Location:**
  - `game/research/ui/research_renderer.py` - class `ResearchRenderer`
  - `game/ui/screens/strategy_renderer.py` - class `StrategyRenderer`
  - Many other rendering functions not using class-based approach
**Recommendation:** Document UI rendering patterns; consider consistency in approach.
**Effort:** Simple

### NCA-021: Cache/Caching Naming
**Location:** `game/simulation/entities/ship.py`
**Issue:**
  - `_cached_mass`, `_cached_max_hp`, `_cached_hp` use `_cached_` prefix
  - Property names don't reflect cached nature (e.g., `mass` property)
  - `_cached_summary` also uses same pattern
**Recommendation:** Document this caching pattern or consider using @cached_property decorator.
**Effort:** Simple

### NCA-022: Resource Management Naming
**Location:** Multiple locations
**Issue:**
  - `game/simulation/systems/resource_manager.py` (System)
  - `game/strategy/engine/resource_management_engine.py` (Engine)
  - `game/simulation/components/abilities/resources.py` (Ability types)
  - `game/core/resources.py` (Resource registration)
**Recommendation:** Consolidate resource handling or clarify naming by adding layer prefix (e.g., `SimulationResourceManager`).
**Effort:** Medium

### NCA-023: Ship Instance vs Ship Design Naming
**Location:**
  - `game/strategy/data/ship_instance.py` (uses "instance")
  - `game/simulation/services/vehicle_design_service.py` (uses "design")
  - `game/simulation/components/component.py` references "component definition"
**Recommendation:** Clearly document strategy layer vs simulation layer object naming.
**Effort:** Medium

### NCA-024: Constructor Parameter Naming
**Location:** Multiple constructors
**Issue:** Parameter naming for similar concepts varies:
  - Some use `data: Dict`, others `definition: Dict`, others explicit naming
  - No consistent pattern for dependency injection parameters (sometimes `registries`, sometimes `registry`)
**Recommendation:** Establish parameter naming conventions: `data` for JSON-like dicts, `definition` for schema-validated dicts, `registries` for DI.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **NCA-002 (filepath vs file_path)** - Quick win; affects 209 locations; impacts code consistency
2. **NCA-001 (Duplicate ShipDesignValidator)** - Critical bug; immediate refactoring needed
3. **NCA-003 (get_ vs fetch_ vs retrieve_)** - Design decision needed; affects future API design
4. **NCA-006 (Service vs System vs Engine)** - Architectural clarity needed; guides future organization
5. **NCA-004 (calculate_ vs recalculate_)** - Common pattern; needs standardization

---

## Terminology Recommendations

| Concept | Recommended Term | Usage Context | Examples |
|---------|-----------------|----------------|----------|
| Ship unit | **ship** | Code, docs, all contexts | Ship, ShipState, ship_instance |
| Equipment piece | **component** | Code, docs | Component, add_component() |
| Simulation event | **battle** | Large scope, orchestration | BattleEngine, BattleState |
| Per-entity behavior | **combat** | Component/system level | ShipCombatMixin, combat_cooldowns |
| Turn/round | **turn** | Strategy layer | TurnEngine, turn_based |
| Tick/step | **tick** | Simulation layer | battle tick, tick loop |
| Modification | **modifier** | Data-driven changes | Modifier, apply_modifiers() |
| Evaluated change | **effect** | Runtime application | ModifierEffect, apply_effects() |
| Capability | **ability** | Component functionality | Ability, WeaponAbility, ability_instances |
| Health points | **hp/max_hp** | Internal; never "health" | current_hp, max_hp |
| Data retrieval | **get_** or **load_** | `get_` for properties, `load_` for I/O | get_component(), load_ship_data() |
| Computation | **calculate_** or **recalculate_** | `calculate_` initial, `recalculate_` update | calculate_stats(), recalculate_mass() |
| Boolean state | **is_** | Object state | is_alive, is_operational |
| Boolean possession | **has_** | Containment | has_components, has_fuel |
| Boolean capability | **can_** | Potential action | can_fire, can_move |
| File path | **file_path** | Variable/parameter name | file_path, not filepath |

---

## Cross-Reference Observations

- Documentation in `NAMING_CONVENTIONS.md` is well-structured for Battle vs Combat distinction but incomplete for other terms
- Code generally follows documented conventions better than older patterns
- Strategy layer and Simulation layer use similar concepts with slightly different naming
- Test files are scattered across multiple directories without consistent organization
- UI code uses Panel suffix consistently but lacks Widget pattern documentation

---


## File: code_quality_report.md

# Code Quality Analysis Report

## Summary
- **Total issues found:** 23
- **Critical:** 3
- **Major:** 8
- **Minor:** 12
- **Info:** 0

---

## Findings

### CRITICAL: God Class - Component System (878 LOC)
**ID:** CQ-01
**Location:** `game/simulation/components/component.py:1-879`
**Issue:** Single Component class handles all aspects: initialization, abilities, modifiers, stats recalculation, damage tracking, and resource management across 878 lines. The class violates SRP with 40+ methods covering disparate concerns.
**Impact:** Extremely difficult to test, maintain, and extend. Changes to any feature risk cascading failures.
**Recommendation:** Extract separate classes: AbilityManager, ModifierManager, StatsCalculator, ResourceCostCalculator. Use composition pattern.
**Effort:** Complex

### CRITICAL: Deeply Nested UI Screen (1231 LOC)
**ID:** CQ-02
**Location:** `game/ui/screens/race_setup_screen.py:1-1231`
**Issue:** Single UIWindow subclass handles tab switching, preview rendering, event routing, and state management. Methods contain nested loops and conditionals 5+ levels deep.
**Impact:** New team members cannot quickly understand flow. Tab-specific bug fixes create high regression risk.
**Recommendation:** Extract TabPanel base class with specialized subclasses. Use ViewModel pattern to separate state from UI.
**Effort:** Complex

### CRITICAL: High Cyclomatic Complexity - Validation Rules
**ID:** CQ-03
**Location:** `game/simulation/systems/validator.py:120-180`
**Issue:** LayerRestrictionDefinitionRule.validate() has 7 nested conditionals checking block/allow rules with repeated string parsing and loose coupling to rule format.
**Impact:** Hard to add new rule types. String parsing errors go undetected.
**Recommendation:** Create Rule class hierarchy (BlockRule, AllowRule) with polymorphic validate().
**Effort:** Medium

### MAJOR: Duplicate Code - Image Scaling Pattern
**ID:** CQ-04
**Location:** `game/ui/screens/race_setup_screen.py:879-914` (and 10+ other files)
**Issue:** Same image scaling pattern repeated verbatim across 10+ files.
**Impact:** Bug fixes require changes in 10+ places. Maintenance burden.
**Recommendation:** Extract utility function `scale_to_fit(surface, max_w, max_h)` in ui/utils.py
**Effort:** Simple

### MAJOR: Missing Error Handling - Resource Consumption
**ID:** CQ-05
**Location:** `game/simulation/components/component.py:335-357`
**Issue:** `try_activate()`, `consume_activation()` methods silently return False/None without logging.
**Impact:** Silent failures in activation logic. Debugging UI issues becomes difficult.
**Recommendation:** Add logging at WARN level for failures. Return typed Result objects.
**Effort:** Simple

### MAJOR: Single Letter Variables
**ID:** CQ-06
**Location:** Multiple files - `game/ui/screens/planet_list_window.py:156-157`, `game/ui/screens/race_setup_screen.py:810-926`
**Issue:** Loop variables named `i`, `x`, `y`, `w`, `h` in complex layout logic.
**Impact:** Cognitive overhead. Copy-paste bugs when similar loops are duplicated.
**Recommendation:** Use descriptive names: `formation_index`, `x_pos`, `panel_width`.
**Effort:** Simple

### MAJOR: Magic Numbers Throughout
**ID:** CQ-07
**Location:** Multiple UI screens: `builder/weapons_panel.py:10-75`, `race_setup_screen.py:862`
**Issue:** Hardcoded values like `0.5` for damage threshold, `150` for ship preview size with no context.
**Impact:** Hard to maintain consistent UI theme. Scaling to different resolutions requires grep-and-replace.
**Recommendation:** Create UIConstants class with named fields.
**Effort:** Medium

### MAJOR: Complex Conditional - Ship Stats Calculation
**ID:** CQ-08
**Location:** `game/simulation/systems/stats.py:74-82`
**Issue:** Damage threshold check uses conditional with inverted logic and duplicated damage checks.
**Impact:** Armor damage logic scattered. Hard to verify correctness.
**Recommendation:** Extract `check_component_damage(comp)` method with clear intent.
**Effort:** Simple

### MAJOR: God Class - Builder GUI (1100 LOC)
**ID:** CQ-09
**Location:** `game/ui/screens/builder/main.py:1-1100`
**Issue:** BuilderSceneGUI mixes UI rendering, event handling, selection logic, data persistence, and validation. 40+ attributes.
**Impact:** New developers need 2+ days to understand flow. Adding features breaks existing code.
**Recommendation:** Split into BuilderPresentation, BuilderModel, BuilderController using MVC.
**Effort:** Complex

### MINOR: Inconsistent Naming
**ID:** CQ-10
**Location:** `game/ui/screens/fleet_report_window.py:45-65`
**Issue:** Mix of naming conventions: `sidebar_width` vs `self.header_height`. Some abbreviations, others spelled out.
**Impact:** New contributors follow wrong patterns.
**Recommendation:** Establish naming guide with consistent suffixes.
**Effort:** Simple

### MINOR: Unused Parameters
**ID:** CQ-11
**Location:** `game/ui/screens/race_setup_screen.py:250`
**Issue:** Methods with partially used parameters like `stats` passed but not always accessed.
**Impact:** IDE warnings ignored. Dead code pathway confusion.
**Recommendation:** Remove unused params or document why retained.
**Effort:** Simple

### MINOR: Cross-Layer Imports
**ID:** CQ-12
**Location:** `game/ui/screens/builder/main.py:30-36`
**Issue:** UI layer directly imports Ship, VEHICLE_CLASSES from simulation layer.
**Impact:** Simulation refactoring requires UI changes. Hard to test UI in isolation.
**Recommendation:** Create DTO/facade layer: BuilderShipAdapter.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **CQ-01: God Class - Component System (878 LOC)** - Root of maintainability problems. Every new feature risks regressions. Highest maintenance burden.

2. **CQ-02: Deeply Nested UI Screen (1231 LOC)** - Most complex screen. Blocks new UI features. Constant bug reports.

3. **CQ-04: Duplicate Code - Image Scaling** - Low effort, high ROI. Bug fix in one place prevents 10+ locations.

4. **CQ-07: Magic Numbers Throughout** - Blocks UI theme consistency. Scaling to new resolutions hard.

5. **CQ-09: God Class - Builder GUI (1100 LOC)** - Second most complex. Builder features blocked.

---


