# Combined Findings Report

Generated: 2026-01-28 16:51:24

---


# Source: 2026-01-28_consistency_full-codebase-patterns

---


## File: error_logging_report.md

# Error Handling and Logging Pattern Analysis

**Agent:** Error Handling & Logging Analyst
**Date:** 2026-01-28
**Scope:** game/, ui/ directories (excluding tests)

---

## Summary
- Total pattern variants found: 12
- Critical inconsistencies: 0
- Major inconsistencies: 1
- Minor inconsistencies: 3
- Dominant pattern: Centralized logger with specific exception handling

---

## Error Handling Patterns

### Exception Handling Styles

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| `except Exception as e:` (catch-all) | asset_manager.py:102, battle_controller.py:191 | 60% | Most common |
| Specific exceptions (FileNotFoundError, JSONDecodeError) | json_utils.py:52-58, ship_loader.py:69 | 35% | Best practice |
| Silent `except Exception:` | target_evaluator.py:34, battle.py:186 | 5% | Problematic |

### Error Propagation Patterns

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Return tuples (success, message, data) | save_game_service.py:34, persistence.py | 15% | I/O operations |
| Return None on error | ship_loader.py, resources.py | 40% | Data loading |
| Raise exception | json_utils.py:load_json_required | 20% | Critical data |
| Log and continue | asset_manager.py:102-104 | 25% | UI/display |

---

## Logging Patterns

### Logger Initialization

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Centralized logger imports | 94 files across game/ | 95% | Dominant |
| `print()` statements | ui/builder/event_bus.py:21 | 5% | Legacy |

### Log Level Usage

| Level | Usage Pattern | Examples |
|-------|--------------|----------|
| DEBUG | File loading details, success | json_utils.py, save_game_service.py |
| INFO | Game flow milestones | app.py:246, resources.py |
| WARNING | Missing assets, fallbacks | asset_manager.py, persistence.py |
| ERROR | Exception details, failures | save_game_service.py:110 |

### Message Formatting

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| f-strings with context | Throughout codebase | 95% | Standard |
| Traceback inclusion | save_game_service.py:110 | 10% | Complex errors |

---

## Key Inconsistencies

### ERR-01: Print vs Logger in Event Buses
**Severity:** Minor
**ID:** ERR-01
**Location:** `ui/builder/event_bus.py:21`
**Issue:** Uses `print()` instead of centralized logger
**Impact:** Inconsistent error reporting, no log level control
**Recommendation:** Migrate to `log_error()` / `log_warning()`
**Effort:** Simple

### ERR-02: Silent Exception Handlers
**Severity:** Minor
**ID:** ERR-02
**Location:** `game/ai/target_evaluator.py:34`, `game/ui/hud/battle.py:186`
**Issue:** Exception handlers don't bind the exception variable
**Impact:** Cannot access exception details for logging/debugging
**Recommendation:** Always bind: `except Exception as e:`
**Effort:** Simple

### ERR-03: Inconsistent Error Return Patterns
**Severity:** Info
**ID:** ERR-03
**Location:** Various I/O operations
**Issue:** Mix of tuple returns, None returns, and exceptions
**Impact:** Caller must know which pattern each method uses
**Recommendation:** Document pattern choice per module; consider standardizing
**Effort:** Medium

---

## Recommended Standard

### Error Handling
```python
# Pattern A: Critical data (raises)
try:
    data = load_json_required(filepath)
except FileNotFoundError:
    raise RuntimeError(f"Critical file not found: {filepath}")

# Pattern B: Optional data (returns default)
try:
    data = load_json(filepath, default={})
except Exception as e:
    log_error(f"Failed to load {filepath}: {e}")
    return None

# Pattern C: I/O operations (returns tuple)
try:
    save_json(filepath, data)
    return True, "Saved successfully", None
except Exception as e:
    log_error(f"Save failed: {e}")
    return False, f"Error: {e}", None
```

### Logging
```python
from game.core.logger import log_debug, log_info, log_warning, log_error

log_error(f"Failed to load {resource_name}: {e}")
log_info(f"Loaded {count} items from {os.path.basename(path)}")
log_warning(f"Asset not found, using fallback: {fallback_id}")
```

---

## Top 5 Priority Issues

1. **ERR-01:** Replace `print()` with logger in event_bus.py (2 files)
2. **ERR-02:** Add exception binding to silent handlers (~5 locations)
3. Consider documenting error propagation patterns per module
4. Ensure all new code follows json_utils.py best practices
5. Expand traceback logging for complex error scenarios

---


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


## File: architecture_reviewer_report.md

# Architecture Reviewer Report

## Summary
- **Total issues found:** 16
- **Critical:** 4, **Major:** 6, **Minor:** 4, **Info:** 2

---

## Critical Issues

### AR-001: Core Layer Dependency on Strategy Layer
**ID:** AR-001
**Location:** `game/core/registry.py:10` -> `game/strategy/services/ship_stats_service.py`
**Issue:** The core layer (game/core) imports from the strategy layer (game/strategy), violating the dependency hierarchy. Specifically, registry.py uses ShipStatsService in its module docstring example code.
**Impact:** Creates circular dependency risk, violates layering principle, core becomes less reusable
**Recommendation:** Move registry-strategy integration to a higher layer adapter. Keep core independent of all application layers.
**Effort:** Medium

---

### AR-002: Core Layer Dependency on Strategy Layer - Type Hints
**ID:** AR-002
**Location:** `game/core/protocols.py:37` -> `game/strategy/data/hex_math.py`
**Issue:** Core protocols module imports HexCoord type from strategy layer inside TYPE_CHECKING block. While this uses TYPE_CHECKING, it still creates a hard dependency on strategy layer internals.
**Impact:** Makes core aware of strategy implementation details, violates separation of concerns
**Recommendation:** Move HexCoord to a shared data types module or core layer
**Effort:** Medium

---

### AR-003: Engine Layer Dependency on Simulation Layer
**ID:** AR-003
**Location:** `game/engine/collision.py:56` (TYPE_CHECKING) -> `game/simulation/entities/ship.py`
**Issue:** Engine layer (core infrastructure) depends on simulation layer's Ship class, even if only in TYPE_CHECKING. Engine should be simulation-agnostic.
**Impact:** Engine cannot be reused for different simulation implementations
**Recommendation:** Use protocol-based type hints instead of concrete Ship class. Define IShip protocol in core/protocols.py
**Effort:** Medium

---

### AR-004: Excessive Deferred Imports Indicating Circular Dependencies
**ID:** AR-004
**Location:** Multiple files across strategy and simulation layers
**Issue:** 20+ late imports (inside function bodies) detected in files like:
- `game/strategy/data/fleet.py:88,110,128,573` (FleetMobilityService, ShipStatsService, ShipInstance)
- `game/strategy/engine/turn_engine.py:72,92,100,108,116,124,165` (SimulationBattleResolver, validation)
- `game/simulation/entities/ship.py:262,517,558` (Abilities, ModifierService)
- `game/simulation/systems/stats.py:20,172,173,337,429` (ResourceManager, Abilities, WeaponAbility)

**Impact:** Runtime import overhead, harder to detect import errors at startup, maintainability issues
**Recommendation:** Restructure modules to eliminate circular dependency chains. Use dependency injection to pass dependencies rather than importing them.
**Effort:** Complex

---

## Major Issues

### AR-005: UI Layer Importing Directly from Simulation Layer
**ID:** AR-005
**Location:** Multiple UI files importing simulation components
**Issue:** UI screens directly import from simulation layer:
- `game/ui/screens/battle_scene.py:23,26-27` imports BattleService, BattleController, Ship
- `game/ui/screens/build_queue_screen.py:21` imports SimulationDesignLoader
- `game/ui/hud/panels.py:15` imports ComponentStatus

**Impact:** UI tightly coupled to simulation implementation, violates MVC/MVVM principles, UI cannot be tested without simulation
**Recommendation:** Create UI adapter layer. Use facade pattern (like StrategySessionFacade) for simulation access. Pass data objects instead of domain objects.
**Effort:** Complex

---

### AR-006: Circular Import in UI Package
**ID:** AR-006
**Location:** `game/ui/__init__.py:4` (comment) and workshop_screen.py
**Issue:** Documentation explicitly states "workshop_screen is NOT eagerly imported here to avoid circular dependency with ui.builder package"
**Impact:** Forces lazy imports, complicates module initialization, test discovery issues
**Recommendation:** Refactor builder and workshop_screen to remove circular dependency. Extract shared interfaces to separate module.
**Effort:** Complex

---

### AR-007: UI Layer Importing from Strategy Layer Too Directly
**ID:** AR-007
**Location:** Multiple UI screens importing strategy data models directly
**Issue:** UI screens import strategy data structures directly:
- `game/ui/screens/build_queue_screen.py:19-20` imports Planet, DesignLibrary
- `game/ui/screens/race_setup_screen.py:23-24` imports RaceConfig, RaceLibrary
- `game/ui/screens/builder/component_ref.py:31-32` imports LayerType, Component

**Impact:** UI tightly coupled to strategy/simulation data models, API fragility, testing difficulty
**Recommendation:** Create data transfer objects (DTOs) layer. UI should work with UI-specific models, not domain models.
**Effort:** Complex

---

### AR-008: God Module - BuilderSceneGUI
**ID:** AR-008
**Location:** `game/ui/screens/builder/main.py`
**Issue:** BuilderSceneGUI class (lines 72-1200+) imports from:
- Simulation layer: Ship, VEHICLE_CLASSES, components, ShipIO, MODIFIER_REGISTRY
- AI layer: StrategyManager
- 12 distinct game module imports

**Impact:** Difficult to test, maintain, or refactor independently
**Recommendation:** Refactor to use dependency injection and facade pattern.
**Effort:** Medium

---

### AR-009: Constructor Parameter Overload - UI Components
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

### AR-010: Deferred Imports in Strategy Layer - Structural Issue
**ID:** AR-010
**Location:** `game/strategy/engine/turn_engine.py:37-42,72,92,100,108,116,124,165`
**Issue:** TurnEngine imports core engines at module level but then re-imports them inside methods. This indicates circular dependency or initialization order sensitivity.
**Impact:** Fragile initialization, performance degradation, maintainability
**Recommendation:** Ensure all imports are at module level. If circular, restructure to break cycle.
**Effort:** Medium

---

## Minor Issues

### AR-011: Global Singletons Overuse
**ID:** AR-011
**Location:** 30+ files using .instance() pattern
**Issue:** Extensive use of singletons for RegistryManager, SpriteManager, StrategyManager, AIController. Testing challenges and prevents proper DI migration.
**Impact:** Hard to test, violates DI principles, state sharing issues
**Recommendation:** Complete PROJ-38 migration to DI. Make .instance() private/deprecated.
**Effort:** Medium

---

### AR-012: Deprecated API Still in Heavy Use
**ID:** AR-012
**Location:** `game/core/registry.py:298-365`
**Issue:** Deprecated functions are marked with DeprecationWarning but still widely used. No actual removal deadline.
**Impact:** Legacy code paths difficult to refactor, PROJ-38 migration stalled
**Recommendation:** Set removal date (3-6 months), actively migrate consumers to GameRegistries DI pattern
**Effort:** Medium

---

### AR-013: AI Layer Cross-Cutting Concerns
**ID:** AR-013
**Location:** `game/ai/target_evaluator.py` -> `game/simulation/components/component_constants.py`
**Issue:** AI layer imports from simulation to use LayerType constant. This couples AI to simulation implementation details.
**Impact:** AI cannot be evolved independently, component changes break AI
**Recommendation:** Extract shared constants to core/constants.py or create AI-specific enum
**Effort:** Simple

---

### AR-014: Missing Public API Definition
**ID:** AR-014
**Location:** Most packages lack coherent __init__.py exports
**Issue:** Packages have inconsistent __init__.py organization. No clear public vs. private module distinction.
**Impact:** Unclear package contracts, encourages implementation import, refactoring harder
**Recommendation:** Create explicit public API in each package's __init__.py with __all__
**Effort:** Simple

---

## Info Issues

### AR-015: TYPE_CHECKING Pattern Correctly Used
**ID:** AR-015
**Location:** Various files
**Issue:** Positive finding - proper use of TYPE_CHECKING to avoid circular import issues at runtime
**Impact:** Good practice
**Recommendation:** Continue this pattern
**Effort:** N/A

---

### AR-016: Facade Pattern Implemented
**ID:** AR-016
**Location:** `game/strategy/facade/strategy_session_facade.py`
**Issue:** Positive finding - StrategySessionFacade properly encapsulates strategy layer for UI consumption
**Impact:** Reduces coupling, good separation
**Recommendation:** Expand facade pattern to other layers (SimulationFacade, AiFacade)
**Effort:** N/A

---

## Architecture Diagram

```
Current State (PROBLEMATIC):

    game/ui/
        â”œâ”€> game/strategy/ (direct imports of data models)
        â”œâ”€> game/simulation/ (direct imports of entities & services)
        â””â”€> game/core/

    game/strategy/
        â”œâ”€> game/simulation/ (via adapter layer - OK)
        â”œâ”€> game/core/ (direct imports - VIOLATION)
        â””â”€> game/engine/ (via collision.py - VIOLATION)

    game/simulation/
        â””â”€> game/core/ (OK)

    game/engine/
        â””â”€> game/simulation/ (TYPE_CHECKING - VIOLATION)

    game/core/
        â””â”€> game/strategy/ (CRITICAL VIOLATION)

Expected Dependency Flow (Top to Bottom):
1. UI (game/ui/) - depends on Strategy, Core
2. Strategy (game/strategy/) - depends on Simulation, Core, via Adapters
3. Simulation (game/simulation/) - depends on Core, Engine
4. Engine (game/engine/) - depends on Core only
5. Core (game/core/) - standalone
```

---

## Top 5 Priority Issues

1. **AR-001: Core Layer Dependency on Strategy** - Fix registry.py imports to break circular dependency chain
2. **AR-004: Excessive Deferred Imports** - Systematic refactoring needed to eliminate 20+ late imports
3. **AR-005: UI Layer Direct Simulation Import** - Decouple UI from simulation via adapter/facade pattern
4. **AR-007: UI Importing Strategy Data Models** - Implement DTO layer between UI and domain layers
5. **AR-006: Circular Import in UI Package** - Refactor workshop_screen/builder relationship

---


## File: backward_compat_detector_report.md

# Backward Compatibility Detector Report

## Summary
- **Total issues found:** 19
- **Critical:** 2, **Major:** 8, **Minor:** 6, **Info:** 3

---

## Critical Findings

### BCD-001: DUAL REGISTRY SYSTEM (IRegistryProvider vs GameRegistries)
**Severity:** CRITICAL
**Location:**
- `game/core/registry.py:40-74`
- `game/simulation/services/vehicle_design_service.py:56-98`
- `game/simulation/services/modifier_service.py:36-98`
- `game/simulation/entities/ship_serialization.py:113-150`

**Issue:** The codebase maintains TWO parallel dependency injection patterns:

**OLD (PROJ-27 - IRegistryProvider):**
```python
service = VehicleDesignService(registry=provider)  # Deprecated pattern
```

**NEW (PROJ-38 - GameRegistries):**
```python
service = VehicleDesignService(registries=game_registries)  # Preferred pattern
```

Multiple classes implement fallback logic:
```python
if registries is not None:
    self._registries = registries
    self._registry = None
elif registry is not None:
    self._registry = registry
    self._registries = None
else:
    try:
        self._registries = get_default_registries()
    except RuntimeError:
        self._registry = get_default_registry_provider()
```

**Impact:** Code complexity, duplicated logic in 15+ files, confusion for new developers

**Recommendation:** Complete deprecation of IRegistryProvider pattern - migrate all callers to GameRegistries

**Effort:** Complex

---

### BCD-002: DEPRECATED REGISTRY UTILITY FUNCTIONS
**Severity:** MAJOR
**Location:** `game/core/registry.py:298-361`

**Issue:** Five utility functions (`get_component_registry()`, `get_modifier_registry()`, `get_vehicle_classes()`, `get_validator()`, `get_resource_registry()`) are marked deprecated with DeprecationWarning but still widely used throughout the codebase. They emit runtime warnings on every call.

**Backward Compat Pattern:**
- Functions fallback to global RegistryManager singleton
- New pattern should use GameRegistries dependency injection
- 119 PROJ references show incomplete migration

**Recommendation:**
1. Audit all callers of these deprecated functions
2. Complete migration to GameRegistries dependency injection (PROJ-38)
3. Remove deprecated functions after verification
4. Consider keeping one compatibility layer if total migration will take multiple sprints

**Effort:** Complex (affects multiple systems)

---

## Major Findings

### BCD-003: MODULAR SERVICE STATIC/INSTANCE METHOD OVERLOADING
**Severity:** MAJOR
**Location:** `game/simulation/services/modifier_service.py:54-98`

**Issue:** ModifierService.is_modifier_allowed() supports BOTH patterns:
```python
# Static-style (legacy)
ModifierService.is_modifier_allowed('mod_id', component)

# Instance-style (new)
service = ModifierService()
service.is_modifier_allowed('mod_id', component)
```

Uses parameter introspection to detect calling pattern:
```python
if isinstance(self_or_mod_id, ModifierService):
    # Instance method call
else:
    # Static-style call
```

**Impact:** Confusing API, harder to maintain, violates single calling pattern principle

**Recommendation:** Choose one pattern (instance methods preferred), deprecate the other

**Effort:** Medium

---

### BCD-004: LEGACY COMPONENT PANEL RETENTION
**Severity:** MAJOR
**Location:** `game/ui/screens/builder/legacy_components.py` (189 lines)

**File Header Indicates:**
```
Note: This file contains legacy modifier editing functionality.
Consider migration to ModifierLogic for new code.
```

This is an entire legacy UI panel that's been retained for backward compatibility.

**Recommendation:**
1. Verify all functionality exists in ModifierLogic replacement
2. Audit which code paths still use legacy_components.py
3. Migrate or remove

**Effort:** Medium

---

### BCD-005: SAVE GAME VERSION MIGRATION WITH FALLBACK
**Severity:** MAJOR
**Location:** `game/strategy/systems/save_game_service.py:26-415`

**Issue:** Save system maintains compatibility with 4 previous versions:
```python
SAVE_VERSION = "2.0.0"
MIGRATABLE_VERSIONS = ["1.0.0", "1.1.0", "1.2.0", "1.9.0"]
```

Functions like `_can_migrate_version()`, `_is_compatible_version()` handle old format detection. Also has disabled migration code:

```python
# BUG-29 FIX: Do NOT migrate designs from temp folder
# SaveGameService._migrate_temp_designs(game_session, designs_folder)
```

Commented-out migration helper at line 114-147: `_migrate_temp_designs()`

**Recommendation:**
1. Decide on minimum supported version
2. Remove support for versions below that
3. Clean up disabled migration code
4. Update MIGRATABLE_VERSIONS

**Effort:** Medium

---

### BCD-006: SHIP SERIALIZATION WITH STAT MISMATCH FALLBACK
**Severity:** MEDIUM
**Location:** `game/simulation/entities/ship_serialization.py:208-246`

**Issue:** Serializer includes "expected_stats" that are verified on load with auto-correction:
```python
if mismatches:
    log_warning(f"Ship '{s.name}' stats mismatch after loading!")
    for m in mismatches:
        log_warning(f"  - {m}")
```

This is a backward compatibility fallback for stats mismatch handling. The data includes:
- max_hp, max_fuel, max_energy, max_ammo
- max_speed, acceleration_rate, turn_speed, total_thrust
- armor_hp_pool, warp values, strategic movement

**Recommendation:**
1. Verify these stats are accurately calculated during from_dict()
2. Consider if this fallback is still needed
3. If format changed, implement explicit versioning instead

**Effort:** Medium

---

### BCD-007: BACKWARD COMPATIBILITY ALIASES IN APP.PY
**Severity:** MINOR
**Location:** `game/app.py:49-58`

**Issue:** Scene state aliases for backward compatibility:
```python
# Scene States (Aliased for compatibility)
MENU = GameState.MENU
BUILDER = GameState.BUILDER
BATTLE = GameState.BATTLE
...
```

These module-level aliases duplicate the enum values instead of using them directly.

**Recommendation:** Remove aliases, use GameState enum directly throughout codebase

**Effort:** Simple

---

### BCD-008: LEGACY CREW REQUIREMENT PATTERN
**Severity:** MINOR
**Location:** `game/ui/screens/builder/stats_config.py:67-83`

**Issue:** Helper function for extracting crew requirements from old format:
```python
def _get_legacy_crew_requirement(ship):
    """Get crew requirement from negative CrewCapacity values (legacy pattern)."""
    crew_capacity = ship.get_ability_total('CrewCapacity')
    if crew_capacity < 0:
        return abs(crew_capacity)
    return 0
```

Old components used negative CrewCapacity instead of CrewRequired ability.

**Recommendation:** Migrate all old components to use CrewRequired ability, remove this helper

**Effort:** Medium (requires component migration)

---

### BCD-009: GETATTR WITH DEFAULTS FOR BACKWARDS COMPAT
**Severity:** MINOR
**Location:** `game/simulation/entities/ship_serialization.py:41-66`

Multiple uses of `getattr()` with defaults for potentially-missing attributes:
```python
"vehicle_type": getattr(ship, 'vehicle_type', 'Ship'),
"strategic_movement": getattr(ship, 'total_strategic_movement', 0),
"warp_max_tonnage": getattr(ship, 'warp_max_tonnage', 0),
```

These suggest optional attributes that may not exist on all ship objects (backward compat fallback).

**Recommendation:** Make these attributes mandatory on Ship class

**Effort:** Simple

---

### BCD-010: COMPONENT FORMAT MIGRATION IN SERIALIZATION
**Severity:** MEDIUM
**Location:** `game/simulation/entities/ship_serialization.py:168-172`

**Issue:** Component deserialization supports TWO formats:
```python
if isinstance(c_entry, str):
    # Old format: just component ID
    comp_id = c_entry
elif isinstance(c_entry, dict):
    # New format: dict with id and modifiers
    comp_id = c_entry.get("id", "")
    modifiers_data = c_entry.get("modifiers", [])
```

This is format versioning without explicit version checking.

**Recommendation:** Standardize on dict format, handle migration explicitly

**Effort:** Medium

---

## Lower Priority Issues

### BCD-011: MODIFIER SCHEMA V1 FORMAT SUPPORT
**File:** `game/simulation/components/modifier_schema.py`
**Issue:** Comments indicate V1 format (deprecated) still supported
**Recommendation:** Remove V1 support if migration is complete
**Effort:** Simple

### BCD-012: SHIP COMBAT DEPRECATION NOTICE
**File:** `game/simulation/entities/ship_combat.py`
**Issue:** Deprecation notice about future removal
**Recommendation:** Either remove or set timeline
**Effort:** Simple

### BCD-013: FLEET MOVEMENT MODULE DEPRECATION
**File:** `game/strategy/engine/fleet_movement.py`
**Header:** "DEPRECATED: This module is deprecated as of PROJ-35"
**Recommendation:** Remove or migrate all callers
**Effort:** Medium

### BCD-014: DISABLED BUG-29 MIGRATION CODE
**File:** `game/strategy/systems/save_game_service.py:74-77`
**Issue:** Commented-out temp design migration
**Recommendation:** Remove if no longer needed
**Effort:** Simple

### BCD-015: MODIFIER LOGIC MANDATORY MODIFIER ENFORCEMENT
**File:** `game/ui/screens/builder/modifier_logic.py:142-150`
**Issue:** ensure_mandatory_modifiers() adds missing mandatory modifiers at runtime
**Recommendation:** Ensure this is only for UI, not data model
**Effort:** Simple

---

## Top 5 Priority Issues (by Impact)

1. **DUAL REGISTRY SYSTEM (PROJ-38 Migration)** - BCD-001
   - 15+ files affected with fallback logic
   - Causes deprecation warnings throughout runtime
   - **Action:** Complete IRegistryProvider deprecation, audit 50+ callers

2. **DEPRECATED UTILITY FUNCTIONS** - BCD-002
   - 5 deprecated functions still widely used
   - Runtime warning spam on startup
   - **Action:** Migrate all callers to GameRegistries

3. **MODIFIER SERVICE DUAL CALLING PATTERN** - BCD-003
   - Parameter type introspection for backward compat
   - Confusing API for 2 calling conventions
   - **Action:** Choose instance or static pattern, standardize all callers

4. **SAVE FILE VERSION MIGRATION** - BCD-005
   - Supports 4 old formats unnecessarily
   - Disabled migration code cluttering logic
   - **Action:** Define minimum supported version, remove old code

5. **LEGACY COMPONENT PANEL** - BCD-004
   - Entire 189-line module for backward compat
   - Not actively maintained
   - **Action:** Verify replacement exists, remove if safe

---

## Recommendations Summary

1. **Immediate (Sprint 1):** Remove module-level aliases (app.py), clean up disabled code
2. **Short-term (Sprint 2-3):** Complete PROJ-38 migration, consolidate registry patterns
3. **Medium-term (Sprint 4-5):** Migrate component formats, ship serialization
4. **Long-term:** Establish minimum version policy for future backward compat decisions

All findings suggest the codebase is in active migration with partial completion. Focus should be completing PROJ-38 before adding new backward compatibility features.

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


## File: core_infrastructure_reviewer_report.md

# Core Infrastructure Reviewer Report

## Summary
- **Total Issues Found:** 12
- **Critical:** 2, **Major:** 4, **Minor:** 4, **Info:** 2

---

## Critical Issues

### CORE-001: Missing Return Type Hints on Logger Functions
**ID:** CORE-001
**Location:** `game/core/logger.py:67-80`
**Issue:** Functions `log_debug()`, `log_info()`, `log_warning()`, `log_error()`, and `set_logging()` lack return type hints (`-> None`). The Logger class methods similarly lack type hints.
**Impact:** Reduces type safety and IDE support. Makes code harder to understand and prone to misuse.
**Recommendation:** Add `-> None` return type hints to all logger functions. Add parameter type hints (`msg: str`, `enabled: bool`) and method return types to Logger class.
**Effort:** Simple

---

### CORE-002: Incomplete Type Hint Coverage in Core Registry
**ID:** CORE-002
**Location:** `game/core/registry.py:94-256`
**Issue:** RegistryManager methods like `set_validator()` lack parameter type hints. The `_validator` attribute is typed as `Any` without documentation on expected type.
**Impact:** Unclear what type of validator is expected. Makes debugging difficult when wrong types are passed.
**Recommendation:** Add type hint `validator: Optional[ShipDesignValidator]` to `set_validator()`. Document the expected validator interface in class docstring.
**Effort:** Simple

---

## Major Issues

### CORE-003: Inconsistent Singleton Pattern Implementation
**ID:** CORE-003
**Location:** `game/core/logger.py:11-18`, `game/core/registry.py:184-198`, `game/core/profiling.py:44-57`, `game/core/screenshot_manager.py:32-45`
**Issue:** Four different singleton implementations use slightly different patterns. Logger uses `__new__` with `_initialized` flag; RegistryManager and others use double-checked locking with `instance()`. Inconsistent patterns make maintenance harder.
**Impact:** Code reviewers must understand multiple patterns. Higher chance of bugs if pattern isn't correctly replicated.
**Recommendation:** Standardize all singletons to use the thread-safe double-checked locking pattern (RegistryManager/Profiler style). Consider extracting into a base class or using a decorator.
**Effort:** Medium

---

### CORE-004: Deprecated Functions Still Exported and Callable
**ID:** CORE-004
**Location:** `game/core/registry.py:37-57, 298-364`
**Issue:** Five deprecated functions (`get_component_registry()`, `get_modifier_registry()`, `get_vehicle_classes()`, `get_validator()`, `get_resource_registry()`) are in `__all__` exports and actively used in `game/core/resources.py:92` and `game/simulation/battle_state.py`. PROJ-38 deprecation not enforced; no migration timeline specified.
**Impact:** Code emits DeprecationWarnings at runtime. Migration is incomplete (battle_state.py still uses deprecated functions). No clear migration path for consumers.
**Recommendation:** Phase 2 of PROJ-38: Set deprecation deadline (e.g., next release). Update all internal usage to use DI. Add migration guide in registry docstring.
**Effort:** Medium

---

### CORE-005: Backward Compatibility Module-Level Exports Not Documented
**ID:** CORE-005
**Location:** `game/core/paths.py:89-98`
**Issue:** Module-level exports (`ROOT_DIR`, `DATA_DIR`, `ASSET_DIR`, etc.) re-export from Paths class for backward compatibility, but no comment explains why. Similarly, `game/core/constants.py:29-33` re-exports display config from DisplayConfig class without explanation.
**Impact:** New developers don't understand the migration pattern. Risk of accidental removal of backward-compat exports.
**Recommendation:** Add comments: `# Backward compatibility: prefer Paths.ROOT_DIR in new code` on line 89. Document the migration pattern in constants.py.
**Effort:** Simple

---

### CORE-006: Broad Exception Catching Without Context
**ID:** CORE-006
**Location:** `game/core/resources.py:77-79, 111-113` and `game/core/screenshot_manager.py:115-116, 216-217`
**Issue:** Bare `except Exception:` blocks suppress all errors without logging specifics. In resources.py line 77, silently falls back to defaults without logging context.
**Impact:** Makes debugging harder. Hides genuine bugs under fallback behavior.
**Recommendation:** Log exception type/message in except blocks: `except Exception as e: log_warning(f"Failed to load resources: {type(e).__name__}: {e}")`. Distinguish recoverable vs critical errors.
**Effort:** Simple

---

## Minor Issues

### CORE-007: Type Hint Inconsistency - Union vs str | (Python 3.10+)
**ID:** CORE-007
**Location:** `game/core/resources.py:22`
**Issue:** Uses `str | None` (PEP 604 style, Python 3.10+) while other files use `Optional[str]` (typing module). Inconsistent type hint style across codebase.
**Impact:** Reduces consistency. May confuse readers familiar with older typing style.
**Recommendation:** Standardize on `Optional[str]` or `str | None` project-wide. Current codebase uses `Optional`, so fix resources.py line 22.
**Effort:** Simple

---

### CORE-008: Missing Input Validation in ValidationResult
**ID:** CORE-008
**Location:** `game/core/validation.py:51-57`
**Issue:** `__post_init__` checks `if self.errors is None` but dataclass with `default_factory=list` can't be None. Defensive check is redundant.
**Impact:** Slight code smell; suggests developer wasn't confident in dataclass semantics.
**Recommendation:** Remove lines 54-57 (the None checks). Keep the docstring explaining field behavior.
**Effort:** Simple

---

### CORE-009: Inconsistent Error Messages and Formatting
**ID:** CORE-009
**Location:** `game/core/registry.py:269, 296` and `game/core/screenshot_manager.py:28`
**Issue:** Error messages vary in capitalization and punctuation. Inconsistent tone.
**Impact:** Professional polish; makes code feel less polished.
**Recommendation:** Standardize error message format across modules.
**Effort:** Simple

---

### CORE-010: Indentation Inconsistency in Frozen Check
**ID:** CORE-010
**Location:** `game/core/registry.py:175, 269`
**Issue:** Lines use single-space incorrect indentation (13 spaces instead of 12). This is a PEP 8 violation.
**Impact:** Hard to spot in review; violates PEP 8.
**Recommendation:** Fix indentation to standard 12 spaces (3 levels).
**Effort:** Simple

---

## Info Issues

### CORE-011: PROJ-38 Deprecation Status Unclear
**ID:** CORE-011
**Location:** `game/core/registry.py:1-35`
**Issue:** PROJ-38 deprecation plan documented but no deadline, migration priority, or completion criteria. Utility functions have DeprecationWarning but code actively using them isn't flagged.
**Impact:** Unclear when deprecated functions can be removed. No sense of urgency for migration.
**Recommendation:** Add to registry.py docstring: "PROJ-38 Migration Timeline: Phase 1 (done) - Add DI. Phase 2 (TODO) - Migrate internal usage. Phase 3 (TODO) - Remove deprecated functions (v2.0)".
**Effort:** Simple

---

### CORE-012: Engine Collision System Using hasattr/getattr Over Protocols
**ID:** CORE-012
**Location:** `game/engine/collision.py:109-121, 149, 157-159`
**Issue:** CollisionSystem uses `hasattr()/getattr()` checks instead of protocol-based duck typing. Protocols exist in `game/core/protocols.py` (ICombatant, IDamageable) but aren't used here.
**Impact:** Reduces type safety and IDE support. Doesn't leverage existing protocol infrastructure.
**Recommendation:** Replace hasattr checks with protocol checks or add type hints.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **CORE-002: Incomplete Type Hint Coverage** - Type safety foundation affects entire core infrastructure
2. **CORE-001: Missing Return Type Hints on Logger** - Logger is heavily used throughout codebase
3. **CORE-004: Deprecated Functions Not Enforced** - PROJ-38 migration incomplete
4. **CORE-003: Inconsistent Singleton Pattern** - Four different implementations makes codebase harder to maintain
5. **CORE-006: Broad Exception Catching** - Silently fails make debugging difficult

---

## Architecture Notes

**Dependency Injection Status (PROJ-27/38):**
- Protocol-based DI pattern well-designed (`IRegistryProvider`, `DefaultRegistryProvider`, `TestRegistryProvider`)
- PROJ-27 protocols implemented correctly in `game/core/protocols.py`
- PROJ-38 migration incomplete - deprecated utility functions still used in core code

**Singleton Pattern:**
- 4 different singleton implementations (Logger, RegistryManager, Profiler, ScreenshotManager)
- Recommend standardization for maintainability

**Configuration Management:**
- Excellent consolidation in `game/core/config.py` (centralized magic numbers)
- DisplayConfig, AIConfig, PhysicsConfig, BattleConfig well-organized

---


## File: data_pattern_analyst_report.md

# Data Pattern Analyst Report

## Summary
- **Total issues found:** 14
- **Critical:** 3, **Major:** 6, **Minor:** 5

---

## Critical Issues

### DPA-001: Inconsistent Dictionary Access Pattern - KeyError Risk
**ID:** DPA-001
**Location:** `game/strategy/data/planet.py:192-227`, `game/strategy/data/galaxy.py:32-33,74-75,439`
**Issue:** Mixed use of direct bracket access `data['key']` and safe `.get()` access in from_dict() methods. Planet.from_dict() uses 14 direct accesses without defaults while also using `.get()` for optional fields.
**Impact:** Data corruption, deserialization failures, loss of saved game compatibility
**Recommendation:** Standardize all from_dict() methods to use `.get()` with sensible defaults for all fields.
**Effort:** Medium

---

### DPA-002: Enum String Conversion Without Error Handling
**ID:** DPA-002
**Location:** `game/strategy/data/planet.py:193`, `game/strategy/data/galaxy.py:71`
**Issue:** Enum conversion using bracket notation: `PlanetType[data['planet_type']]` will raise KeyError if the enum value name doesn't exist.
**Impact:** Complete deserialization failure if enum naming changes between versions.
**Recommendation:** Add try-catch around enum conversion with fallback to a safe default value.
**Effort:** Simple

---

### DPA-003: Incomplete Optional Field Handling with None Values
**ID:** DPA-003
**Location:** `game/strategy/data/ship_instance.py:47,62,99-106`
**Issue:** ShipInstance.from_dict() uses `data.get('serial')` which returns None for missing fields, but ShipInstance.create() logs a warning when serial is None. Dual-meaning of None creates confusion.
**Impact:** Ambiguous state - unclear if None means "not set" vs "intentionally defaulting".
**Recommendation:** Use explicit sentinel values or add a `_version` field to distinguish old saves.
**Effort:** Medium

---

## Major Issues

### DPA-004: Inconsistent Serialization Method Naming
**ID:** DPA-004
**Location:** Across 17 files with serialization methods
**Issue:** Codebase uses two different naming conventions: `to_dict()` / `from_dict()` (13 files), `to_json()` / `from_json()` (wrappers in some)
**Impact:** Developer confusion, maintainability issues
**Recommendation:** Adopt single naming convention (recommend `to_dict()`/`from_dict()`).
**Effort:** Medium

---

### DPA-005: Missing Version/Schema Information in Serialized Data
**ID:** DPA-005
**Location:** All to_dict() methods lack `_version` or `_schema_version` fields
**Issue:** No serialization format version is stored in saved data.
**Impact:** Impossible to implement safe migrations. Future format changes will silently corrupt data.
**Recommendation:** Add `_format_version` and `_schema_id` fields to all serialized data.
**Effort:** Medium

---

### DPA-006: Dataclass Field Defaults Mixed with Manual Defaults
**ID:** DPA-006
**Location:** `game/strategy/data/planet.py:20-82`, `game/strategy/data/ship_instance.py:26-63`
**Issue:** Dataclasses define field defaults via `field(default_factory=...)` but from_dict() also provides defaults via `.get()`. Redundant defaults that can diverge.
**Impact:** Subtle bugs where empty collections aren't shared as expected.
**Recommendation:** Use dataclass defaults consistently - don't repeat in from_dict().
**Effort:** Simple

---

### DPA-007: No Validation of Required Fields in from_dict()
**ID:** DPA-007
**Location:** All from_dict() implementations
**Issue:** No validation that required fields are present before use.
**Impact:** Silent data loss or corruption if save file is partially corrupted.
**Recommendation:** Add ValidationResult-based validation at start of from_dict().
**Effort:** Medium

---

### DPA-008: Circular Reference Handling is Inconsistent
**ID:** DPA-008
**Location:** `game/strategy/data/empire.py:70-94` vs `game/strategy/data/galaxy.py`
**Issue:** Empire.to_dict() explicitly avoids circular references by storing only IDs. However, other classes include full nested objects.
**Impact:** Potential stack overflow or memory bloat if circular references aren't properly broken.
**Recommendation:** Document circular reference handling strategy. Use IDs consistently for back-references.
**Effort:** Medium

---

### DPA-009: Field Type Conversions Not Always Bidirectional
**ID:** DPA-009
**Location:** `game/strategy/data/fleet.py:567`, `game/strategy/data/stars.py:100`
**Issue:** Serialization converts tuples to lists for JSON compatibility, but deserialization doesn't always convert back.
**Impact:** Type inconsistencies after round-trip serialization.
**Recommendation:** Add explicit type conversions in from_dict() to restore original types.
**Effort:** Simple

---

## Minor Issues

### DPA-010: Default Value Inconsistencies Across Instances
**Location:** `game/strategy/data/design_metadata.py:59-71`
**Issue:** Different approaches to handling missing nested objects.
**Effort:** Simple

### DPA-011: Resource Dictionary Handling Inconsistent
**Location:** `game/strategy/data/planet.py:167`
**Issue:** Assumes values are dicts; .copy() will fail if value is a scalar.
**Effort:** Simple

### DPA-012: Layer Type Enum String Conversion Missing Error Handling
**Location:** `game/simulation/battle_state.py:156`
**Issue:** Could fail if layer type names are changed.
**Effort:** Simple

### DPA-013: Optional Tuple Fields Not Fully Typed
**Location:** `game/strategy/data/stars.py:83`, `game/simulation/battle_state.py:90`
**Issue:** Tuple fields typed inconsistently.
**Effort:** Simple

### DPA-014: Backward Compatibility Partial
**Location:** `game/strategy/data/design_metadata.py:169-171`
**Issue:** Warns about old formats but doesn't actually migrate the data.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **DPA-001: Inconsistent Dictionary Access Pattern** - HIGH RISK: KeyError failures on deserialization
2. **DPA-002: Enum String Conversion Without Error Handling** - HIGH RISK: Enum changes break save loading
3. **DPA-005: Missing Version/Schema Information** - HIGH RISK: Makes all future format changes dangerous
4. **DPA-003: Incomplete Optional Field Handling** - MEDIUM RISK: Unclear semantics of None values
5. **DPA-004: Inconsistent Serialization Method Naming** - MEDIUM RISK: Maintainability issue

---


## File: dead_code_hunter_report.md

# Dead Code Hunter Report

## Summary
- **Total Issues Found:** 11
- **Critical:** 2, **Major:** 4, **Minor:** 5

---

## Critical Issues

### DC-001: Duplicate Battle Panel Systems
**ID:** DC-001
**Location:**
- `game/ui/hud/panels.py` (705 lines)
- `game/ui/panels/battle_panels.py` (20KB)

**Issue:** Two parallel implementations of ShipStatsPanel, SeekerMonitorPanel, and BattleControlPanel classes exist in different locations. This creates confusion about which version is canonical:
- `game/ui/hud/battle.py` imports from `game.ui.hud.panels`
- `game/ui/screens/battle_screen.py` imports from `game.ui.panels.battle_panels`

**Impact:** Code duplication, maintenance burden, potential sync issues between implementations.

**Recommendation:** Consolidate into single location (suggest `game/ui/panels/battle_panels.py` as it has more recent refactoring with `ship_stats_renderer.py` imports).
**Effort:** Medium

---

### DC-002: Stub Functions with NotImplementedError
**ID:** DC-002
**Location:** `game/ai/behaviors.py:79`
**Issue:** Base class `AIBehavior.update()` raises `NotImplementedError` but is never actually called - appears to be incomplete design pattern.
**Code:**
```python
def update(self, target: Any, strategy: Dict[str, Any]) -> None:
    """Execute behavior logic."""
    raise NotImplementedError
```
**Impact:** Dead code if subclasses override before parent is used, confusing interface contract.
**Recommendation:** Use `@abstractmethod` if truly abstract.
**Effort:** Simple

---

## Major Issues

### DC-003: Unreachable Draw Methods
**ID:** DC-003
**Location:**
- `game/ui/hud/panels.py:28` - BattlePanel.draw()
- `game/ui/panels/battle_panels.py:18` - BattlePanel.draw()

**Issue:** Base class methods raise `NotImplementedError` but should use `@abstractmethod` if truly abstract.
**Impact:** Misleading interface, potential for accidental instantiation.
**Recommendation:** Convert to `@abstractmethod`
**Effort:** Simple

---

### DC-004: Empty Service Module
**ID:** DC-004
**Location:** `game/strategy/services/__init__.py` (1 line only comment)
**Issue:** Package is empty except for comment "# Strategy services package"
**Impact:** Dead package namespace, no exports defined
**Recommendation:** Either populate with real services or delete package and import directly from submodules.
**Effort:** Simple

---

### DC-005: Unimplemented Method with TODO
**ID:** DC-005
**Location:** `game/app.py:671`
**Issue:**
```python
available_tech_ids = []  # TODO: Replace with empire.available_tech or similar
```
**Impact:** Placeholder code left in production, no available tech returned to workshop.
**Recommendation:** Implement proper empire tech tracking or remove placeholder.
**Effort:** Medium

---

### DC-006: _ValidatorProxy Never Used
**ID:** DC-006
**Location:** `game/simulation/entities/ship.py:29-34`
**Issue:** `_ValidatorProxy` class is instantiated as `VALIDATOR = _ValidatorProxy()` but the VALIDATOR constant is never referenced in the codebase. Validator is accessed directly via `get_or_create_validator()`.
**Impact:** Dead code adds maintenance burden, confuses developers.
**Recommendation:** Remove `_ValidatorProxy` class and VALIDATOR global.
**Effort:** Simple

---

## Minor Issues

### DC-007: Dead pycache Directories
**ID:** DC-007
**Location:** 36 `__pycache__` directories throughout game/
**Issue:** Compiled Python bytecode cached directories should not be in version control.
**Impact:** Bloats repository.
**Recommendation:** Add to .gitignore if not already present.
**Effort:** Simple

---

### DC-008: Empty Module Exports
**ID:** DC-008
**Location:**
- `game/ai/__init__.py` (0 bytes)
- `game/__init__.py` (0 bytes)
- `game/simulation/__init__.py` (0 bytes)

**Issue:** Package __init__ files are completely empty with no exports defined.
**Impact:** Reduces code discoverability, requires importing from submodules.
**Recommendation:** Define meaningful `__all__` exports.
**Effort:** Simple

---

### DC-009: Debug Flag Always Enabled
**ID:** DC-009
**Location:** `game/core/constants.py:56`
**Issue:**
```python
DEBUG_SCREENSHOTS = True
```
**Impact:** Debug feature cannot be toggled at runtime, potential performance issue if screenshots are continuously saved.
**Recommendation:** Make configurable or disable by default.
**Effort:** Simple

---

### DC-010: Obsolete Commented Code Reference
**ID:** DC-010
**Location:** `game/ui/screens/test_lab.py:88-99`
**Issue:** Obsolete commented code referencing non-existent `menu_screen.create_particles()` method.
**Impact:** Confusion about what code is still valid.
**Recommendation:** Remove obsolete comments.
**Effort:** Simple

---

### DC-011: Protocol Ellipsis Stubs
**ID:** DC-011
**Location:** `game/core/protocols.py` (10 instances)
**Issue:** Protocol property definitions use ellipsis (...) as placeholder implementation.
**Impact:** Acceptable for Protocols, but indicates incomplete specification.
**Recommendation:** Document expected behavior in docstrings.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **DC-001: Duplicate Panel Systems** - Critical - Consolidate to single implementation
2. **DC-005: Unfinished Tech Availability** - Major - Implement proper empire tech tracking
3. **DC-004: Empty Service Package** - Major - Delete or populate
4. **DC-002/DC-003: Stub Methods with NotImplementedError** - Major - Convert to @abstractmethod
5. **DC-006: _ValidatorProxy Never Used** - Major - Remove dead code

---

## Code Quality Observations

**Strengths:**
- Most code is actively used and maintained
- Minimal commented-out code blocks
- No wildcard imports detected (good practice)
- TYPE_CHECKING blocks used correctly for forward references

**Weaknesses:**
- Duplicate implementations create maintenance risk
- Missing @abstractmethod decorators on abstract base classes
- Unfinished TODOs left in production code
- Empty service package suggests architectural rework in progress

---


## File: documentation_reviewer_report.md

# Documentation Reviewer Report

## Summary
- **Total issues found:** 16
- **Critical:** 2, **Major:** 5, **Minor:** 7, **Info:** 2

---

## Critical Issues

### DOC-001: Broken Project References
**ID:** DOC-001
**Location:** `docs/ARCHITECTURE.md:151-152`
**Issue:** References to PROJ-11 project plan and design documents that have been deleted from the active_projects directory. The file path `../Projects/active_projects/PROJ-11/plan.md` no longer exists.
**Impact:** Developers attempting to review architecture decisions cannot access linked documentation. Broken links reduce documentation credibility.
**Recommendation:** Either restore PROJ-11 project files or remove these references and incorporate the essential information into ARCHITECTURE.md itself.
**Effort:** Medium

---

### DOC-002: Incomplete PROJ References
**ID:** DOC-002
**Location:** `docs/refactoring/REMAINING_ISSUES_PLAN.md:1-16`
**Issue:** Document references completed PROJ work but projects directory only contains PROJ-41. Multiple completed projects lack documentation artifacts.
**Impact:** No historical record of major refactoring work completed. Makes it difficult to understand why certain patterns exist in the codebase.
**Recommendation:** Archive completed project documentation or create project completion summaries in a dedicated "completed_projects" directory.
**Effort:** Medium

---

## Major Issues

### DOC-003: Outdated Test Migration Guide
**ID:** DOC-003
**Location:** `docs/test_migration_guide.md:1-50`
**Issue:** Document describes a "TestScenario pattern" and dual pytest/Combat Lab architecture, but the current state of the codebase shows test organization has evolved.
**Impact:** New developers following this guide may implement tests in a pattern no longer used by the project.
**Recommendation:** Audit actual test structure in `tests/`, `simulation_tests/`, and `test_framework/` directories. Either update the guide or mark it as "Legacy - For Reference Only".
**Effort:** Complex

---

### DOC-004: Incomplete Modifier System Documentation
**ID:** DOC-004
**Location:** `docs/modifier_system.md:113-124`
**Issue:** Documentation lists file locations for modifier system but API is documented without showing actual public method signatures. Methods may have changed since documentation was written.
**Impact:** Developers may use incorrect method names when integrating modifier introspection features.
**Recommendation:** Cross-reference source files to verify all documented methods exist with correct signatures.
**Effort:** Simple

---

### DOC-005: Architecture Diagram Misalignment
**ID:** DOC-005
**Location:** `docs/ARCHITECTURE.md:7-21`
**Issue:** Architecture diagram shows layer structure but doesn't reflect actual directory organization. `game/engine/` shown as part of "Core Layer" but reorganization docs suggest it should be separate.
**Impact:** Confusion about actual dependency boundaries and layer separation.
**Recommendation:** Clarify whether `game/engine/` is core infrastructure or separate. Update diagram to match actual structure.
**Effort:** Medium

---

### DOC-006: Naming Conventions Missing New Terms
**ID:** DOC-006
**Location:** `docs/NAMING_CONVENTIONS.md`
**Issue:** Document defines "Battle vs Combat" distinctions, but review of codebase shows additional terms not documented: `Scene` vs `Screen`. Document acknowledges "somewhat interchangeably" but doesn't establish clear rules.
**Impact:** New code may use `Scene` and `Screen` inconsistently.
**Recommendation:** Add section defining `Scene` vs `Screen` distinction with concrete examples.
**Effort:** Simple

---

### DOC-007: Deprecated Code References
**ID:** DOC-007
**Location:** `docs/refactoring/REMAINING_ISSUES_PLAN.md:97-109`
**Issue:** Documentation mentions deprecated code elements but these items don't appear to have been cleaned up.
**Impact:** Unclear what code is safe to use or refactor.
**Recommendation:** Either remove deprecated code or explicitly mark it with deprecation warnings in the source.
**Effort:** Medium

---

## Minor Issues

### DOC-008: Adding Abilities Guide - Missing Error Handling Section
**Location:** `docs/adding_abilities.md:207-254`
**Issue:** The "Write Tests" section doesn't mention what exceptions an ability might raise.
**Recommendation:** Add section on exception handling in ability implementation.
**Effort:** Simple

### DOC-009: Missing Documentation for New UI Components
**Location:** `docs/NAMING_CONVENTIONS.md:88-99`
**Issue:** Documentation doesn't mention modern UI components like `workshop_screen.py`, `workshop_context.py`, `workshop_viewmodel.py` representing MVVM patterns.
**Recommendation:** Add section documenting the Workshop/ViewModel pattern.
**Effort:** Medium

### DOC-010: Incomplete API Documentation
**Location:** `docs/adding_abilities.md:156-163`
**Issue:** Documents `get_effective_stat()` method but doesn't explain the stat resolution order.
**Recommendation:** Add detailed example showing stat resolution with both global and targeted modifiers.
**Effort:** Simple

### DOC-011: Missing Layer Iteration Documentation
**Location:** `docs/adding_abilities.md` (not present)
**Issue:** The ability system heavily uses component layer iteration, but there's no documentation on how to iterate layers correctly.
**Recommendation:** Add section on iterating component layers with examples.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **DOC-001: Broken Project References** - High visibility issue that damages documentation credibility
2. **DOC-002: Missing Project Artifacts** - No historical record of completed refactoring work
3. **DOC-003: Outdated Test Migration Guide** - Actively misleading to new developers
4. **DOC-005: Architecture Diagram Misalignment** - Creates confusion about fundamental design decisions
5. **DOC-006: Inconsistent Scene vs Screen Naming** - Current codebase uses both terms inconsistently

---


## File: error_handling_auditor_report.md

# Error Handling Auditor Report

## Summary
- **Total issues found:** 23
- **Critical:** 4, **Major:** 8, **Minor:** 9, **Info:** 2

---

## Critical Issues

### ERR-001: Overly Broad Exception Handling Without Specific Types
**ID:** ERR-001
**Location:** `game/simulation/components/component.py:725`, `game/core/json_utils.py:92`, `game/assets/asset_manager.py:102-124`
**Issue:** Multiple `except Exception as e:` blocks catch all exceptions generically, masking underlying issues
**Impact:** Hides programming errors, makes debugging difficult, swallows critical system errors
**Count:** 46+ instances
**Recommendation:** Replace with specific exception types
**Effort:** Simple

---

### ERR-002: Silent Exception Swallowing in ai/target_evaluator.py
**ID:** ERR-002
**Location:** `game/ai/target_evaluator.py:34-35`, `game/ai/target_evaluator.py:49-50`
**Issue:** `except Exception: pass` silently swallows errors without logging
**Impact:** Silent failures make debugging impossible, potential data corruption
**Recommendation:** Add logging or specific handling
**Effort:** Simple

---

### ERR-003: Generic Exception Raising Without Context
**ID:** ERR-003
**Location:** `game/assets/asset_manager.py:29`, `game/ui/assets/ship_theme_manager.py:46`, `game/core/registry.py:175`, `game/ai/strategy_manager.py:40`
**Issue:** `raise Exception("message")` instead of specific exception types
**Impact:** Makes exception handling unreliable, unclear error semantics
**Count:** 7 instances
**Recommendation:** Use specific exception types (ValueError, RuntimeError, etc.)
**Effort:** Simple

---

### ERR-004: Unstructured Exception Logging in formula_system.py
**ID:** ERR-004
**Location:** `game/simulation/formula_system.py:92`
**Issue:** `except Exception as e:` logs to warning with `log_warning()` instead of error, returns 0 silently
**Impact:** Invalid formulas silently evaluate to 0, causing incorrect calculations
**Recommendation:** Log as error, propagate exception or use explicit error value
**Effort:** Medium

---

## Major Issues

### ERR-005: Inconsistent Exception Types for State Violations
**ID:** ERR-005
**Location:** `game/simulation/battle_controller.py:276`, `game/core/registry.py:241`, `game/core/paths.py:25`
**Issue:** Mixes RuntimeError, ValueError, and generic Exception for state violations
**Impact:** Inconsistent API contract, poor client code clarity
**Count:** 15+ instances
**Recommendation:** Standardize on RuntimeError for state violations, ValueError for input errors
**Effort:** Medium

---

### ERR-006: Missing Exception Context Chaining (raise from)
**ID:** ERR-006
**Location:** `game/simulation/components/component.py:725-726`, `game/simulation/services/design_loader.py`, `game/strategy/systems/save_game_service.py`
**Issue:** Re-raises exceptions without `raise from e` chaining
**Impact:** Lost stack trace context, harder debugging
**Count:** 12+ instances
**Recommendation:** Use `raise NewException(...) from e` pattern
**Effort:** Simple

---

### ERR-007: Inconsistent Logging Levels
**ID:** ERR-007
**Location:** `game/core/json_utils.py:56`, `game/core/resources.py:77-79`, `game/simulation/formula_system.py:93`
**Issue:** Log level mismatches - IOError logged as error vs warning inconsistently
**Impact:** Inconsistent log severity, filtering issues
**Count:** 8+ instances
**Recommendation:** Establish log level guidelines
**Effort:** Simple

---

### ERR-008: No Validation Result Error Code Standardization
**ID:** ERR-008
**Location:** `game/core/validation.py`, all validation files
**Issue:** error_code parameter unused in most ValidationResult implementations
**Impact:** Cannot programmatically distinguish error types
**Count:** 20+ validation sites
**Recommendation:** Define error code enumeration
**Effort:** Medium

---

### ERR-009: Input Validation Gaps in Core Components
**ID:** ERR-009
**Location:** `game/simulation/entities/projectile.py:34`, `game/simulation/components/component.py:158`
**Issue:** `.get()` calls with None defaults but no validation of result
**Impact:** Silent None propagation, NoneType errors downstream
**Recommendation:** Add explicit validation after .get() calls
**Effort:** Medium

---

### ERR-010: Finally Block Cleanup Missing
**ID:** ERR-010
**Location:** `game/ui/screens/builder/main.py:48-55`, `game/simulation/systems/battle_engine.py:118-124`
**Issue:** File operations without guaranteed cleanup in finally
**Impact:** Resource leaks, unclosed file handles
**Count:** 3 instances
**Recommendation:** Use context managers or finally blocks
**Effort:** Simple

---

### ERR-011: No Custom Exception Hierarchy
**ID:** ERR-011
**Location:** Entire codebase
**Issue:** Only using generic Exception, no custom exceptions defined
**Impact:** Cannot catch specific error types, poor error semantics
**Recommendation:** Create custom exception hierarchy (ValidationError, ResourceError, StateError)
**Effort:** Complex

---

### ERR-012: Swallowed Exceptions in Component Loading
**ID:** ERR-012
**Location:** `game/simulation/components/component.py:725-726`, `game/simulation/components/component.py:810-811`
**Issue:** Component creation failures logged but continue processing
**Impact:** Silently skips invalid components, corrupts ship designs
**Recommendation:** Fail fast or collect all errors
**Effort:** Medium

---

## Minor Issues

### ERR-013: Inconsistent Logger Access Pattern
**Location:** `game/ui/screens/builder/main.py:62-64`, `game/core/logger.py`
**Issue:** Mixed use of Python logging module and custom logger wrapper
**Effort:** Simple

### ERR-014: Missing None Checks After get_position()
**Location:** `game/ai/target_evaluator.py:98-252`
**Issue:** Assumes get_position() never returns None
**Effort:** Simple

### ERR-015: KeyError in Layer Type Parsing
**Location:** `game/simulation/battle_state.py:271`
**Issue:** `KeyError` caught but logged as warning, no fallback
**Effort:** Simple

---

## Top 5 Priority Issues

1. **ERR-001: Overly Broad Exception Handling** - Affects 46+ locations, masks errors
2. **ERR-003: Generic Exception Raising** - Inconsistent error semantics
3. **ERR-012: Swallowed Component Exceptions** - Data corruption risk
4. **ERR-002: Silent Exception Swallowing** - Debugging nightmare
5. **ERR-008: Missing Error Code Standardization** - Cannot distinguish error types

---

## Recommendations

1. **Immediate (Week 1):** Create custom exception hierarchy (ValidationError, ResourceError, StateError)
2. **Week 1:** Replace all `except Exception:` with specific types
3. **Week 1:** Add proper exception context chaining with `raise from e`
4. **Week 2:** Standardize error codes for ValidationResult
5. **Week 2:** Add input validation at API boundaries

---


## File: legacy_pattern_hunter_report.md

# Legacy Pattern Hunter Report

## Summary
- **Total issues found:** 23
- **Critical:** 4, **Major:** 9, **Minor:** 8, **Info:** 2

---

## Findings

### CRITICAL: Deprecated Registry Access Functions Still Widely Used
**ID:** LPH-001
**Location:** `game/core/registry.py:299-362`
**Issue:** Six utility functions (`get_component_registry()`, `get_modifier_registry()`, `get_vehicle_classes()`, `get_validator()`, `get_resource_registry()`, `get_default_registries()`) are marked as deprecated in documentation but are still actively used throughout the codebase. They emit DeprecationWarning but code paths still rely on them as fallbacks.
**Impact:** Prevents full transition to PROJ-38's dependency injection pattern. Creates dual code paths - new DI pattern alongside legacy singleton-based access. Makes it impossible to completely remove legacy registry access until all consumers migrate.
**Recommendation:** Phase 2 migration: audit all imports of deprecated functions, migrate to `GameRegistries` with DI, remove fallback paths in services, establish timeline for deprecation.
**Effort:** Complex (requires coordinated changes across 20+ files)
**Files affected:** `game/strategy/services/ship_stats_service.py`, `game/simulation/services/modifier_service.py`, `game/simulation/entities/ship.py` and others

---

### CRITICAL: FleetMovementSimulator Module Deprecated but Still Importable
**ID:** LPH-002
**Location:** `game/strategy/engine/fleet_movement.py:1-13, 67-82`
**Issue:** Entire module marked as deprecated (PROJ-35). FleetMovementSimulator class emits DeprecationWarning on init but remains fully functional. Module documentation says "will be removed in a future release" but no removal timeline exists.
**Impact:** Developers might accidentally use deprecated class instead of FleetNavigationService. Parallel implementations create confusion about which is authoritative for fleet movement logic.
**Recommendation:** Remove module entirely OR establish hard deprecation deadline. If kept, add stack trace capture to track usage. Create migration script to automatically replace imports.
**Effort:** Medium (module is isolated but used in pathfinding)
**Alternative path:** `game/strategy/services/fleet_navigation_service.py` (replacement)

---

### CRITICAL: Dual Static/Instance Method Pattern in ShipStatsService
**ID:** LPH-003
**Location:** `game/strategy/services/ship_stats_service.py:41-150`
**Issue:** `calculate_stats()` method uses complex parameter overloading to support both static (`ShipStatsService.calculate_stats(design_data)`) and instance usage (`service.calculate_stats(design_data)`). Method signature has 8 parameters with 3 different calling conventions documented.
**Impact:** Confusing API with four different calling patterns. Hard to maintain - changing signature affects backward compatibility. Tests must cover all patterns. Code reviewers must understand the overload detection logic (checks `isinstance(self_or_design, ShipStatsService)`).
**Recommendation:** Remove static method pattern completely. Establish factory function for migration: `from_legacy_static(design_data) -> ShipStatsService` that handles old calls gracefully, then deprecate over 2 releases.
**Effort:** Medium (need to identify all 3 calling patterns in codebase)

---

### CRITICAL: Lazy Validator Proxy Pattern
**ID:** LPH-004
**Location:** `game/simulation/entities/ship.py:29-34`
**Issue:** `_ValidatorProxy` class created to defer validator initialization. Allows Ship class to use `VALIDATOR` without import-time coupling. Works but is a workaround for circular import issues rather than proper architectural fix.
**Impact:** Hidden initialization logic. Runtime behavior depends on first access. Complicates debugging (where is VALIDATOR actually coming from?). Same pattern replicated in `_ProfilerProxy` in `game/core/profiling.py:137-140`.
**Recommendation:** Resolve circular import root cause instead. Use dataclass decorators or factory methods. Replace proxy patterns with explicit DI container.
**Effort:** Complex (requires refactoring Ship class initialization)

---

### MAJOR: V1/V2 Format Dual Support in Modifier Effects
**ID:** LPH-005
**Location:** `game/simulation/components/modifier_schema.py:1-50`, `game/simulation/components/modifier_effects.py:188-195`
**Issue:** Code supports both V1 (dict-based with 'special' handlers) and V2 (array-based with formulas) modifier formats. V1 is marked "deprecated: no longer supported in production" but validation still checks for it.
**Impact:** Defensive code that will never execute if all modifiers are V2 format. Creates false sense of backwards compatibility when V1 isn't actually tested or maintained.
**Recommendation:** Remove V1 format checks. Add validation to reject V1 modifiers at load time with clear error message. Document migration path for any legacy mods.
**Effort:** Simple (localized to modifier validation)

---

### MAJOR: Multiple Backward Compatibility Layers
**ID:** LPH-006
**Location:** `game/core/constants.py:29-31` (screen dimensions re-export), `game/core/validation.py:25-128` (dual construction patterns), `game/simulation/components/component_constants.py:17-19` (LayerType re-export)
**Issue:** Three separate backward compatibility shims for DisplayConfig, ValidationResult construction, and LayerType. Each adds a thin alias layer for old code patterns. Code comments explicitly say "for backward compatibility" but no deprecation timeline.
**Impact:** Makes codebase harder to understand - new developers see multiple ways to access same data. Complicates refactoring (changes need to update all entry points). No consistency in how backward compatibility is managed.
**Recommendation:** Establish compatibility policy: 2-release deprecation window with warnings. Consolidate: pick one canonical way, create adapter for legacy access, add deprecation warnings, document migration in changelog.
**Effort:** Simple (straightforward aliasing)

---

### MAJOR: Formation Data Format Migration (Lists vs Dicts)
**ID:** LPH-007
**Location:** `game/ui/screens/formation_editor.py:204-205`, `game/ui/screens/formation_editor.py:178-192`
**Issue:** Formation arrows support both legacy list format and new dict format. On load: `if isinstance(item, list): # Legacy`. On save: converts to new format but still reads old format.
**Impact:** Silent format conversion could lose metadata. Tests may not cover edge cases (half-migrated files, corrupted format detection).
**Recommendation:** One-time migration script to convert all saves. Hard error if old format detected. Add format version field to JSON.
**Effort:** Medium (need data migration utility)

---

### MAJOR: Lazy Initialization Pattern with hasattr Checks
**ID:** LPH-008
**Location:** `game/ui/screens/race_setup_screen.py:379-381`, `game/ui/screens/planet_list_window.py:887-888`, `game/ui/screens/battle_scene.py:279-280`
**Issue:** Pattern of `if not hasattr(self, 'attr_name'): initialize` used for lazy initialization across 15+ files. Creates implicit state machine. Hard to track initialization order.
**Impact:** Non-deterministic initialization order. Missing attribute might indicate uninitialized state or actual missing feature. Complicates testing (must mock entire initialization path).
**Recommendation:** Use `@property` with lazy evaluation OR explicit initialization method. Track initialized state in `__init__`. Add assertions for required attributes.
**Effort:** Medium (systematic refactoring)

---

### MAJOR: BattleEngine Legacy Paths
**ID:** LPH-009
**Location:** `game/simulation/systems/battle_engine.py:220-224, 279-281`
**Issue:** `create_battle()` and `add_ship()` methods have "Legacy path: create controllers internally (backward compatibility)" branches that still execute. Suggests new path (with pre-created controllers) not yet universally used.
**Impact:** Code handles two different controller initialization approaches. Unclear which is canonical. Tests might not cover both paths equally.
**Recommendation:** Audit all battle engine usage - count how often legacy paths execute. If <5%, remove and migrate. If common, make it the canonical path.
**Effort:** Medium (audit + selective removal)

---

### MAJOR: Proxy Properties for Backward Compatibility
**ID:** LPH-010
**Location:** `game/ui/screens/workshop_screen.py:343-366` (ship, selected_components, available_components properties all proxy to viewmodel)
**Issue:** WorkshopScreen has 4+ properties that directly delegate to viewmodel with explicit comments "for backward compatibility". These allow old code to access properties on screen instead of screen.viewmodel.
**Impact:** Duplicates interface definition. Makes refactoring dangerous - easy to change one but not the other. Creates inconsistency (some access patterns go through proxy, others direct).
**Recommendation:** Complete migration to viewmodel access. Remove proxy properties and fix all internal uses. Update external API documentation that this is the new pattern.
**Effort:** Simple (straightforward find-replace)

---

### MINOR: Adapter Class for Ship-to-IControllable Interface
**ID:** LPH-011
**Location:** `game/ai/interfaces/controllable.py:242-250`
**Issue:** `ShipControllableAdapter` wraps Ship to implement IControllable interface. Necessary for PROJ-11 Phase 4 but creates wrapper overhead. Suggests Ship and IControllable not fully aligned.
**Impact:** Extra indirection in AI code path. Ship has combat methods, but AI must go through adapter to access them.
**Recommendation:** Consider making Ship directly implement IControllable or use composition. Evaluate if adapter is necessary or if interface definition needs adjustment.
**Effort:** Medium (architectural review needed)

---

### MINOR: ShipCombatMixin Facade Pattern
**ID:** LPH-012
**Location:** `game/simulation/entities/ship_combat.py:1-25`
**Issue:** ShipCombatMixin is explicitly a "thin facade" delegating to ShipCombatEngine. Kept for backward compatibility during PROJ-12 decomposition (2-3 years old).
**Impact:** Extra method layer adds minimal value. Developers must understand mixin delegates to engine. PROJ-12 phase appears incomplete.
**Recommendation:** Either complete PROJ-12 decomposition (make Ship composition-based) or deprecate mixin formally.
**Effort:** Complex (architectural decision required)

---

### MINOR: Commented Legacy Shim
**ID:** LPH-013
**Location:** `game/ui/screens/builder/weapons_panel.py:738-740`
**Issue:** Comment says "Legacy shim removed - always use ability damage". Code references removal but doesn't show old implementation. Suggests code cleanup was incomplete.
**Impact:** Confusing comment. Developers wonder what was removed and why. No git history context in comment.
**Recommendation:** Remove comment entirely - the behavior is now canonical. If conditional logic remains, explain current behavior not historical changes.
**Effort:** Simple

---

### MINOR: ComponentRef Tuple Migration Helpers
**ID:** LPH-014
**Location:** `game/ui/screens/builder/component_ref.py:14-19, 71-99`
**Issue:** ComponentRef provides `from_tuple()` and `to_tuple()` methods explicitly for "backward compatibility during migration". Suggests tuple-based references are being replaced with ComponentRef objects.
**Impact:** Developers must know about both formats. JSON serialization might produce tuples for old code. Increases validation burden.
**Recommendation:** Complete migration to ComponentRef everywhere. Remove tuple helpers. Add migration script for existing saves.
**Effort:** Medium (data structure migration)

---

### MINOR: Legacy/Deprecated Design Format Detection
**ID:** LPH-015
**Location:** `game/strategy/data/design_metadata.py:169-171`
**Issue:** Design loader detects "Old format detected" and warns with log but continues. Suggests design format changed but loader still accepts old format.
**Impact:** Silent format acceptance could corrupt data. No guarantee old format is correctly loaded.
**Recommendation:** Add explicit version field to design JSON. Reject old format with clear error. Provide migration utility.
**Effort:** Medium

---

### MINOR: Obsolete Design Filtering
**ID:** LPH-016
**Location:** `game/ui/screens/design_selector_window.py:5, 62-64, 157-160`
**Issue:** Design selector has `show_obsolete` flag and obsolete filter UI. Suggests designs can be marked obsolete but behavior not fully clear.
**Impact:** Feature partially implemented. UI shows checkbox but unclear what "obsolete" means operationally.
**Recommendation:** Document obsolete semantics. Either fully implement (hide obsolete by default, show with checkbox) or remove feature.
**Effort:** Simple

---

### MINOR: Triple Naming Pattern in Stats
**ID:** LPH-017
**Location:** `game/simulation/systems/stats.py:297-298`
**Issue:** `total_defense_score` computed and assigned, then immediately aliased as `to_hit_profile`. Comment says "Legacy/Alias for UI until fully refactored".
**Impact:** Duplicated data with comment about being temporary. Creates maintenance burden.
**Recommendation:** Complete refactoring - use total_defense_score everywhere, remove alias, update UI.
**Effort:** Simple

---

### MINOR: Fallback Defense Score Calculation
**ID:** LPH-018
**Location:** `game/engine/collision.py:112-115`
**Issue:** Code checks for `total_defense_score` with fallback to `get_total_ecm_score()` for "backward compatibility". Suggests defense scoring was refactored but fallback kept.
**Impact:** Inconsistent target evaluation depending on Ship implementation. Some ships use new scoring, some use old fallback.
**Recommendation:** Audit all Ship implementations - ensure all have total_defense_score. Remove fallback check, add assertion instead.
**Effort:** Simple

---

### MINOR: Legacy Path for AIController Creation
**ID:** LPH-019
**Location:** `game/simulation/systems/battle_engine.py:222-224, 279-281`
**Issue:** Comments explicitly mark two internal controller creation paths as "Legacy path: create controllers internally". Suggests external controller provision is new pattern.
**Impact:** Code handles two initialization approaches. Unclear which is preferred.
**Recommendation:** Establish clear pattern - update comments to explain when each path is used or consolidate into one.
**Effort:** Simple

---

### MINOR: Multiple Profiler Access Patterns
**ID:** LPH-020
**Location:** `game/core/profiling.py:134-140`
**Issue:** `_ProfilerProxy` similar to `_ValidatorProxy` - lazy initialization for backward compatibility. Module-level `profiler` variable uses proxy pattern instead of direct instantiation.
**Impact:** Same issues as ValidatorProxy - hidden initialization, unclear semantics.
**Recommendation:** Consolidate to explicit singleton factory or explicit DI.
**Effort:** Simple

---

### INFO: Placeholder Technology System
**ID:** LPH-021
**Location:** `game/app.py:670-671`
**Issue:** Comment says "placeholder for now - will be implemented when tech tree exists" with TODO to replace. Tech tree not yet implemented, so available_tech_ids set to empty list.
**Impact:** No actual issue - this is a known stub. Document in architecture notes rather than as TODO comment.
**Recommendation:** Create separate issue tracker item for tech tree feature. Remove TODO, replace with feature reference.
**Effort:** Simple

---

### INFO: Dual Module Import Prevention
**ID:** LPH-022
**Location:** `game/ui/__init__.py:8-10`
**Issue:** Comment explains "Pre-import submodules in dependency order (excluding workshop_screen due to circular import)". Circular import exists but is worked around at module load time.
**Impact:** Module initialization has hidden dependency. Changes to workshop_screen could break this.
**Recommendation:** Resolve circular import properly. Document dependency chain. Consider lazy import for workshop_screen.
**Effort:** Medium (architectural refactoring)

---

### INFO: Save Game Format Version Strictness
**ID:** LPH-023
**Location:** `game/strategy/systems/save_game_service.py:10, 367-370`
**Issue:** Comment explicitly states "Strict version checking (no backward compatibility)". Code rejects old save format (v1.0.0) with "old save format not supported" error.
**Impact:** Players cannot load old saves. Acceptable if documented but limits player data migration.
**Recommendation:** This is a design choice, not a bug. Document version support policy. Consider adding migration utility if needed for player base.
**Effort:** N/A (acceptable design)

---

## Top 5 Priority Issues

1. **LPH-001: Deprecated Registry Functions** - Blocks full migration to PROJ-38 DI pattern. Requires coordinated migration across 20+ files. HIGH PRIORITY.

2. **LPH-003: Dual Static/Instance Methods in ShipStatsService** - Most confusing API in codebase. Multiple calling conventions make maintenance error-prone. Should be refactored next.

3. **LPH-002: FleetMovementSimulator Deprecated Module** - Entire module marked for removal but still functional. Create migration timeline and remove duplicate logic.

4. **LPH-006: Multiple Backward Compatibility Layers** - Constants, ValidationResult, LayerType all have re-exports. Establish consistency in how legacy access is handled across codebase.

5. **LPH-008: Lazy Initialization Pattern Abuse** - 15+ files use hasattr-based lazy init. Should be systematized with property decorators or explicit initialization.

---

**Note:** This report intentionally excludes normal version compatibility and feature flags. Focus is on *architectural* legacy patterns that indicate incomplete refactoring or mid-migration code. Several PROJ- tagged efforts (PROJ-12, PROJ-27, PROJ-35, PROJ-38) appear incomplete based on code analysis.

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


## File: simulation_engine_reviewer_report.md

# Simulation Engine Reviewer Report

## Summary
- **Total issues found:** 32
- **Critical:** 6, **Major:** 12, **Minor:** 10, **Info:** 4

---

## Critical Findings

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

### SIM-002: Circular Import Prevention Using Late Binding and Type Hints
**ID:** SIM-002
**Location:** `game/simulation/entities/ship_combat.py:26-37`, `game/simulation/managers/battle_state_manager.py:76`, `game/simulation/entities/ship_stats.py:71`
**Issue:** Multiple instances of deferred imports inside methods to avoid circular dependencies. Pattern: `from module import Class` inside method bodies rather than at module level.
**Impact:** Hides circular dependency problems, makes code harder to follow, performance penalty on method calls, difficult to understand true dependencies.
**Recommendation:** Resolve circular imports properly using dependency injection or reorganizing module structure. Document explicit interfaces between modules.
**Effort:** Complex

---

### SIM-003: Lazy Proxy Pattern for Backward Compatibility
**ID:** SIM-003
**Location:** `game/simulation/entities/ship.py:29-34` (_ValidatorProxy), `game/simulation/entities/ship_combat.py:26-37` (lazy combat_engine)
**Issue:** Two separate lazy-loading proxy patterns to maintain backward compatibility. _ValidatorProxy delegates to get_or_create_validator(), _combat_engine recreates on each access if None.
**Impact:** Inconsistent patterns, hidden state initialization, difficult to debug, performance issues on repeated access.
**Recommendation:** Consolidate into single lazy initialization pattern. Use property with cached initialization.
**Effort:** Simple

---

### SIM-004: Mixed Naming Convention - Manager vs Controller vs Service vs System
**ID:** SIM-004
**Location:** Multiple files across simulation directory
**Issue:** Inconsistent naming for similar classes:
  - `BattleController` (orchestrator) vs `BattleService` (abstraction)
  - `ShipComponentManager` vs `RetreatManager` vs `BattleStateManager`
  - `ShipStatsCalculator` vs `ShipCombatEngine`
  - `ProjectileManager` (legacy) and `ProjectileManager` (in systems/)
**Impact:** Confusing API, unclear responsibilities, difficult onboarding, hard to find related functionality.
**Recommendation:** Establish naming conventions:
  - `Service` = external API (battle setup/execution)
  - `Manager` = internal state management (retreat, battle state)
  - `Engine` = calculation/simulation logic (combat, stats)
  - `Controller` = orchestration (battle controller)
**Effort:** Medium

---

### SIM-005: Backward Compatibility Aliases Creating Confusion
**ID:** SIM-005
**Location:** `game/simulation/battle_controller.py:74-75` (RetreatState alias)
**Issue:** Imports RetreatState as _RetreatState then exports as RetreatState. Creates duplicate RetreatState classes (in retreat_manager.py and used here).
**Impact:** Two sources of truth for the same concept, difficult to find correct import, inconsistent usage across codebase.
**Recommendation:** Keep single canonical RetreatState in one location (retreat_manager.py), import directly in battle_controller without aliasing.
**Effort:** Simple

---

### SIM-006: Unused Dead Code - _ValidatorProxy Pattern
**ID:** SIM-006
**Location:** `game/simulation/entities/ship.py:29-34, 22`, `game/simulation/entities/ship_loader.py`
**Issue:** _ValidatorProxy is instantiated but never used (VALIDATOR = _ValidatorProxy() on line 34 is never referenced). The validator is accessed directly via get_or_create_validator() in add_component methods.
**Impact:** Dead code adds to maintenance burden, confuses developers, suggests incomplete refactoring.
**Recommendation:** Remove _ValidatorProxy class and VALIDATOR global. Import validator directly where needed.
**Effort:** Simple

---

## Major Findings

### SIM-007: Dual Support for Old/New Component System (Dependency Injection)
**ID:** SIM-007
**Location:** `game/simulation/components/component.py:79-100`, `game/simulation/entities/ship.py:38-74`, `game/simulation/battle_state.py:230-263`
**Issue:** All major classes support two initialization patterns:
  1. With registries (PROJ-38 new pattern): `Component(..., registries=GameRegistries())`
  2. Without registries (legacy): `Component(...)` then falls back to `get_default_registries()`
**Impact:** Two code paths to maintain, confusing constructor signatures, inconsistent error handling between paths.
**Recommendation:** Complete migration to PROJ-38 pattern. Phase 1: Make registries required. Phase 2: Remove fallback logic.
**Effort:** Medium

---

### SIM-008: Tight Coupling Between BattleEngine and AIController
**ID:** SIM-008
**Location:** `game/simulation/systems/battle_engine.py:212-236, 272-284, 433-435`
**Issue:** BattleEngine creates AIController internally with hardcoded imports when not provided. Creates circular dependency risk.
**Impact:** Engine cannot be tested without AI layer, difficult to swap implementations, violates single responsibility.
**Recommendation:** Require AIControllers to be passed at initialization. Remove internal creation. Make proper interface/protocol definition.
**Effort:** Medium

---

### SIM-009: Multiple Projectile Manager Implementations
**ID:** SIM-009
**Location:** `game/simulation/projectile_manager.py` (212 LOC) vs `game/simulation/systems/projectile_manager.py`
**Issue:** Two separate projectile manager implementations in different locations with different interfaces and implementations.
**Impact:** Code duplication, maintenance burden, unclear which one to use.
**Recommendation:** Consolidate into single implementation. Keep one in systems/. Update all imports.
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

### SIM-011: Incomplete Refactoring - PROJ-29 SIM-03 Extraction
**ID:** SIM-011
**Location:** `game/simulation/managers/battle_state_manager.py` and `game/simulation/managers/retreat_manager.py`
**Issue:** Both managers were extracted from BattleController but BattleController still contains:
  - `_update_retreats()` method delegating to manager
  - `_find_nearest_edge()` method delegating to manager
  - `_at_map_edge()` method delegating to manager
  - Duplicate state tracking (_retreating_ships, _escaped_ships properties)
**Impact:** Responsibility confusion, logic scattered across classes, state management spread between two classes.
**Recommendation:** Complete extraction by removing duplicate delegation methods from BattleController.
**Effort:** Simple

---

### SIM-012: Blocking Dependency on PROJ-41 (Fleet/ShipInstance Integration)
**ID:** SIM-012
**Location:** `game/simulation/battle_controller.py:655-675` (_apply_results_to_fleet method)
**Issue:** Method body is `pass`. Docstring indicates blocking dependency on PROJ-41. This prevents applying battle results back to source fleets in strategy mode.
**Impact:** Strategy mode battles don't update fleet state, breaking strategic layer integration.
**Recommendation:** Implement method after PROJ-41 completes. Add temporary warning/logging to inform users of limitation.
**Effort:** Complex

---

### SIM-013: Inconsistent Entity Naming Patterns
**ID:** SIM-013
**Location:** Throughout simulation directory
**Issue:** Inconsistent naming for similar entity types:
  - `Ship` (class name) vs `ShipState` (serialized)
  - `Projectile` (class name) vs `ProjectileState` (serialized)
  - Ability naming: `WeaponAbility` vs `CombatPropulsion` (no "Ability" suffix)
**Impact:** Confusion about what class to use where, difficult API to learn.
**Recommendation:** Establish naming conventions for domain vs state classes.
**Effort:** Medium

---

### SIM-014: Dependency Injection Half-Implemented (PROJ-38)
**ID:** SIM-014
**Location:** Multiple files with "PROJ-38" markers
**Issue:** Incomplete transition to constructor-based DI. Some classes have `registries` parameter, others still use module-level get_default_registries().
**Impact:** Inconsistent API, difficult to test with custom registries.
**Recommendation:** Complete PROJ-38 implementation. Create migration plan.
**Effort:** Medium

---

## Minor Findings

### SIM-015: Duplicate State Properties with Backward Compatibility Wrappers
**Location:** `game/simulation/battle_controller.py:557-580`
**Issue:** Properties that delegate to retreat_manager with the same names.
**Recommendation:** Remove wrapper properties. Access manager state directly.
**Effort:** Simple

### SIM-016: Missing Abstractions - Implicit Interfaces
**Location:** `game/simulation/systems/battle_engine.py`, `game/simulation/projectile_manager.py`
**Issue:** Classes work with implicit interfaces (duck typing) without defining protocols or ABCs.
**Recommendation:** Define Protocols for all implicit interfaces.
**Effort:** Medium

### SIM-017: Inconsistent Error Handling Strategy
**Location:** `game/simulation/services/battle_service.py` vs `game/simulation/systems/battle_engine.py`
**Issue:** Service layer uses Result pattern, engine uses exceptions/logging.
**Recommendation:** Choose one strategy (Result pattern preferred for service layer).
**Effort:** Medium

### SIM-018: Missing Validation at Layer Boundaries
**Location:** Multiple entry points
**Issue:** No validation that ships are in valid state before entering battle.
**Recommendation:** Add validation layer before ship is accepted into battle.
**Effort:** Simple

### SIM-019: Complex Battle Calculation Formulas Lack Comments
**Location:** `game/simulation/entities/ship_combat_engine.py:47-94`, `game/simulation/entities/ship_physics.py:13-65`
**Issue:** Complex mathematical formulas have minimal comments explaining the math.
**Recommendation:** Add detailed comments explaining what problem each formula solves.
**Effort:** Simple

### SIM-020: Resource Manager Integration Partially Complete
**Location:** `game/simulation/entities/ship.py:117-124`, `game/simulation/systems/stats.py:20, 39`
**Issue:** ResourceRegistry created but not fully integrated with component update cycle.
**Recommendation:** Create unified resource update method in Ship.
**Effort:** Medium

### SIM-021: Evaluation of Math Formulas Uses eval()
**Location:** `game/simulation/formula_system.py:65-100`
**Issue:** Uses Python eval() to evaluate formula strings from JSON data.
**Impact:** Security risk if data source compromised.
**Recommendation:** Use safer expression parser or implement custom safe parser.
**Effort:** Medium

### SIM-022: State Serialization with String IDs Creates Fragility
**Location:** `game/simulation/battle_state.py:178-228`, `game/simulation/battle_controller.py:217-221`
**Issue:** Ships tracked by string IDs (UUIDs) but mapping is in BattleController._ship_id_map.
**Recommendation:** Use object identity (id()) or persistent ship IDs instead of UUID strings.
**Effort:** Medium

### SIM-023: Duplicate Damage Threshold Logic
**Location:** `game/simulation/components/component.py:374-375`, `game/simulation/systems/stats.py:73-82`
**Issue:** Component damage threshold check exists in two places.
**Recommendation:** Consolidate damage threshold logic into single place.
**Effort:** Simple

### SIM-024: Missing Performance Optimizations
**Location:** `game/simulation/systems/battle_engine.py:343-350`, `game/simulation/projectile_manager.py:27-103`
**Issue:** Spatial grid rebuilt completely each tick. Projectile iteration uses nested loops without spatial indexing.
**Recommendation:** Implement incremental grid updates. Use spatial queries for projectile collision.
**Effort:** Medium

---

## Info Observations

### SIM-025: Incomplete Validation System
**Location:** `game/simulation/ship_validator.py`, `game/simulation/systems/validator.py`
**Issue:** Two validator systems exist with similar names but different purposes.
**Recommendation:** Document purpose of each validator in module docstrings.
**Effort:** Simple

### SIM-026: Missing Documentation on Component System
**Location:** `game/simulation/components/component.py:1-59`
**Issue:** Component lifecycle documented in docstring but not in separate documentation.
**Recommendation:** Create `docs/component_system.md` with architecture diagrams.
**Effort:** Simple

### SIM-027: Retreat Mechanic Has Hardcoded Parameters
**Location:** `game/simulation/managers/retreat_manager.py:33, 49`
**Issue:** Retreat behavior tuned with hardcoded values in dataclass and method signatures.
**Recommendation:** Move to game configuration system or constants module.
**Effort:** Simple

### SIM-028: Battle End Condition System Underdeveloped
**Location:** `game/simulation/systems/battle_end_conditions.py`
**Issue:** BattleEndCondition exists but implementation incomplete.
**Recommendation:** Complete implementation of all end condition modes. Add tests.
**Effort:** Medium

---

## Top 5 Priority Issues

### 1. SIM-001: God Class - Ship Entity
**Why:** Largest impediment to maintainability. Ship class is too large and complex, mixing concerns. Blocks refactoring and testing.
**Effort:** Complex | **Risk:** High | **Impact:** Very High

### 2. SIM-004: Mixed Naming Convention
**Why:** Makes API confusing and hard to learn. Causes developers to use wrong classes. Fundamental design issue.
**Effort:** Medium | **Risk:** Medium | **Impact:** High

### 3. SIM-002: Circular Import Prevention Using Late Binding
**Why:** Indicates deeper architectural problem. Late imports hide circular dependencies that should be resolved structurally.
**Effort:** Complex | **Risk:** High | **Impact:** High

### 4. SIM-012: Blocking Dependency on PROJ-41
**Why:** Feature-blocking issue. Strategy mode battles don't work properly without this.
**Effort:** Complex | **Risk:** Medium | **Impact:** High

### 5. SIM-008: BattleEngine Tightly Coupled to AIController
**Why:** Prevents testing engine in isolation, creates circular dependency risk, violates separation of concerns.
**Effort:** Medium | **Risk:** Medium | **Impact:** Medium

---

## Architecture Strengths

Despite issues found, the codebase has several positive patterns:
- **Effective use of mixins** for code reuse (ShipPhysicsMixin, ShipCombatMixin)
- **Reasonable component system** with ability-based design
- **Good service layer abstraction** (BattleService, ModifierService)
- **Emerging manager pattern** (RetreatManager, BattleStateManager)
- **DI pattern in progress** (PROJ-38) shows forward thinking

---

## Recommended Next Steps

1. Complete PROJ-12 (god class decomposition) by extracting remaining Ship methods
2. Resolve circular imports through proper interface definitions
3. Establish and document naming conventions across simulation layer
4. Complete PROJ-38 DI migration by phasing out legacy functions
5. Consolidate projectile manager implementations
6. Create `game/simulation/constants.py` for all tuning parameters

---


## File: strategy_system_reviewer_report.md

# Strategy System Reviewer Report

## Summary
- **Total issues found:** 14
- **Critical:** 2, **Major:** 6, **Minor:** 4, **Info:** 2

---

## Critical Issues

### STR-001: Incomplete PROJ-35 Migration - Dual Movement Logic
**ID:** STR-001
**Location:** `game/strategy/engine/fleet_movement.py:1-331` AND `game/strategy/services/fleet_navigation_service.py:1-468`
**Issue:** PROJ-35 aimed to unify fleet movement logic, but the deprecated `FleetMovementSimulator` class (331 LOC) still exists in `/engine/` with deprecation warnings while the new `FleetNavigationService` exists in `/services/`. Both implementations provide similar path projection and calculation logic.
**Impact:**
- UI and turn engine may use different movement calculations
- Maintenance burden (code duplication across two modules)
- Risk of behavior divergence in path projection vs. execution
**Recommendation:**
1. Audit all `FleetMovementSimulator` usage to ensure all call sites migrated to `FleetNavigationService`
2. Remove deprecated `FleetMovementSimulator` entirely
3. Add integration test verifying UI projection matches turn execution
**Effort:** Medium

---

### STR-002: Type-Checking and String-Based Ship Identification
**ID:** STR-002
**Location:** `game/strategy/data/fleet.py:433-459`, `game/strategy/engine/fleet_movement.py:63-82`
**Issue:** Fleet still supports legacy string ship references mixed with modern `ShipInstance` objects. The `to_battle_ships()` method explicitly documents "Only works with ShipInstance objects - legacy strings cannot be converted." Multiple `isinstance(target, dict)` type checks scattered through pathfinding and serialization code.
**Impact:**
- Type checking spreads through codebase (fragile)
- Cannot reliably convert old fleets to battle
- Violates single responsibility (code checks types instead of polymorphism)
**Recommendation:**
1. Audit codebase for remaining string ship references
2. Implement complete migration of old save files to `ShipInstance` format
3. Remove all `isinstance(x, dict)` type checks for ship data
**Effort:** Complex

---

## Major Issues

### STR-003: Service Naming Inconsistency and Ambiguity
**ID:** STR-003
**Location:** `game/strategy/services/` (fleet_navigation_service.py, fleet_mobility_service.py, ship_stats_service.py)
**Issue:** Service names mix multiple patterns without clear distinction:
- `FleetNavigationService` - handles pathfinding AND navigation state
- `FleetMobilityService` - handles speed calculation only (not mobility)
- `ShipStatsService` - calculates all ship statistics (very broad)
**Impact:** New developers confused about service boundaries
**Recommendation:**
1. Rename `FleetMobilityService` â†’ `FleetSpeedCalculator`
2. Rename `ShipStatsService` â†’ `ShipStatsCalculator`
3. Create a services architecture document
**Effort:** Simple

---

### STR-004: Tight Coupling Between Strategy and Simulation Layers
**ID:** STR-004
**Location:** `game/strategy/adapters/simulation_adapter.py:24-142`, `game/strategy/data/fleet.py:425-508`
**Issue:** Direct imports of simulation layer in strategy:
- `fleet.to_battle_ships()` creates simulation `Ship` objects directly
- `SimulationBattleResolver` imports `BattleController`, `BattleService` directly
- `ShipInstance.to_ship()` directly calls `ShipSerializer.from_dict()`
**Impact:** Cannot swap simulation implementations; circular dependency risk
**Recommendation:**
1. Create strategy-layer `IBattleEntity` interface
2. Move `to_battle_ships()` logic behind an adapter
3. Use dependency injection to provide the builder
**Effort:** Complex

---

### STR-005: Backward Compatibility Code Scattered Everywhere
**ID:** STR-005
**Location:** `game/strategy/services/fleet_navigation_service.py:84-91`, `game/strategy/data/pathfinding.py:275-283`, `game/strategy/data/fleet.py:604-616`
**Issue:** Multiple backward compatibility patterns without central location:
- `PathSegment.to_dict()` includes legacy `'hex'` field alongside `'end'`
- `_ChaserProxy` class created just to handle NavigationState vs Fleet differences
- Fleet order deserialization handles 3+ different target formats
**Impact:** Hard to identify what's legacy vs. new; multiple code paths need maintenance
**Recommendation:**
1. Create `LegacyCompatibilityLayer` module
2. Move all backward-compat code into it (explicit, versioned)
3. Mark each compat handler with target version
**Effort:** Medium

---

### STR-006: Intercept Calculation Uses Type-Checked Union Without Abstraction
**ID:** STR-006
**Location:** `game/strategy/data/pathfinding.py:286-306`, `calculate_intercept_point:367-434`
**Issue:** `calculate_intercept_point()` accepts `Union['Fleet', 'NavigationState']` and uses `isinstance()` check to distinguish them. Creates `_ChaserProxy` object as workaround.
**Impact:** Violates duck typing; fragile to new types; makes code harder to test
**Recommendation:**
1. Create `IChaserInfo` protocol/interface
2. Add `from_fleet()` and `from_navigation_state()` factory methods
3. Remove `_ChaserProxy` and isinstance check
**Effort:** Simple

---

### STR-007: Resource Consumption Logic Assumes Component Format
**ID:** STR-007
**Location:** `game/strategy/engine/resource_management_engine.py:120-142`, `game/strategy/services/ship_stats_service.py:180-195`
**Issue:** Multiple places check `isinstance(components, dict)` and handle dual formats. Suggests two different component storage formats in layer data.
**Impact:** Resource consumption may not work for all component formats; bug risk if format isn't handled correctly
**Recommendation:**
1. Normalize to single component format throughout
2. Create `ComponentIterator` utility that handles format automatically
3. Add schema validation on design data load
**Effort:** Medium

---

## Minor Issues

### STR-008: Magic Numbers Throughout Fleet Speed and Resource Calculations
**ID:** STR-008
**Location:** `game/strategy/services/fleet_mobility_service.py:30-32`, `game/strategy/data/fleet.py:469-478`
**Issue:** Strategic constants scattered:
- K_STRATEGIC = 25 (movement conversion factor) - in one file only
- MAX_HEXES_PER_TURN = 10 - no clear derivation
- Formation positions: base_x = 20000, base_y = 50000, spacing = 2000
**Recommendation:** Create `game/strategy/config/STRATEGY_CONSTANTS.py`
**Effort:** Simple

---

### STR-009: Pathfinding Implementation Has Incomplete Comments
**ID:** STR-009
**Location:** `game/strategy/data/pathfinding.py:53-62`
**Issue:** Code has unresolved TODO-style comments suggesting exploratory implementation
**Recommendation:** Finalize design documentation; remove exploratory comments
**Effort:** Simple

---

### STR-010: AIController Mixing UI and Combat Logic
**ID:** STR-010
**Location:** `game/ai/controller.py:198-276`
**Issue:** `AIController.update()` mixes formation management, behavior selection, and weapon firing
**Recommendation:** Extract formation handling to `FormationManager` class; move behavior selection to `BehaviorSelector` class
**Effort:** Medium

---

### STR-011: StrategyManager Singleton Pattern
**ID:** STR-011
**Location:** `game/ai/strategy_manager.py:13-149`
**Issue:** Uses singleton pattern with thread-safe double-checked locking. Hard to test.
**Recommendation:** Document why singleton is necessary; consider providing factory method as alternative
**Effort:** Info

---

## Info Issues

### STR-012: Ship Stats Service Has Three Calling Patterns
**ID:** STR-012
**Location:** `game/strategy/services/ship_stats_service.py:86-149`
**Issue:** `calculate_stats()` method supports three calling patterns (instance, static, hybrid). This is a transitional pattern (PROJ-38).
**Recommendation:** Document which pattern should be used going forward; deprecate static pattern
**Effort:** Info

---

## Top 5 Priority Issues

1. **Complete PROJ-35 Migration (STR-001)** - Critical - Unifies movement logic, eliminates code duplication
2. **Remove Type-Checking for Ships (STR-002)** - Critical - Ensures all fleets work with battles
3. **Fix Service Naming (STR-003)** - Major - Clarifies architecture, improves discoverability
4. **Abstract Simulation Layer Coupling (STR-004)** - Major - Enables different battle implementations
5. **Centralize Backward Compatibility (STR-005)** - Major - Reduces codebase complexity

---


## File: test_naming_consistency_report.md

# Test Naming Consistency Report

## Summary
- **Total issues found:** 25
- **Critical:** 7, **Major:** 10, **Minor:** 6, **Info:** 2

---

## Critical Issues

### TNC-001: Non-Standard Test File Naming Convention
**ID:** TNC-001
**Location:** `tests/performance/benchmark_planet_list.py`, `tests/unit/performance/stress_test.py`, `tests/repro_issues/repro_bug_05_deep.py`
**Issue:** 18+ test/script files use non-standard prefixes: `repro_*.py`, `reproduce_*.py`, `verify_*.py`, `benchmark_*.py`
**Impact:** Inconsistent test discovery, unclear whether files are executable scripts vs. pytest-runnable tests
**Recommendation:** Standardize all test files to `test_*.py` prefix or move non-pytest scripts to separate `scripts/` directory
**Effort:** Medium

---

### TNC-002: Inverted Directory Structure Naming
**ID:** TNC-002
**Location:** `game/ui/screens/builder/ â†’ tests/unit/builder/`, `game/simulation/components/abilities/ â†’ tests/unit/abilities/`
**Issue:** Test directories collapse/flatten multi-level source structures, breaking structural parity
**Impact:** Confusion about source-to-test mapping, difficulty navigating parallel codebases
**Recommendation:** Mirror full directory structure: `tests/unit/ui/screens/builder/`, `tests/unit/simulation/components/abilities/`
**Effort:** Complex

---

### TNC-003: Disabled Test Files With Leading Underscores
**ID:** TNC-003
**Location:** `tests/integration/_test_formation_attack.py`, `tests/integration/_test_formation_flight.py`
**Issue:** Test files prefixed with `_` indicate disabled tests but aren't consistently named or documented
**Impact:** Unclear test status, potential orphaned/forgotten tests
**Recommendation:** Use `@pytest.mark.skip` or move to separate `archived/` directory
**Effort:** Simple

---

### TNC-004: Incomplete Directory Structure Mapping
**ID:** TNC-004
**Location:** Missing: `tests/unit/ui/`, `tests/unit/assets/`, `tests/unit/research/`, etc.
**Issue:** Many source directories lack corresponding test directories (14+ missing directories)
**Impact:** Tests for UI components scattered across root test directory
**Recommendation:** Create missing test subdirectories to match source structure exactly
**Effort:** Simple

---

### TNC-005: Duplicate Test Filenames
**ID:** TNC-005
**Location:** `tests/unit/core/test_logger.py` and `tests/unit/simulation/test_logger.py`
**Issue:** Two test files with identical names in different directories
**Impact:** Import confusion, difficulty with IDE navigation
**Recommendation:** Rename one to `test_simulation_logger.py`
**Effort:** Simple

---

### TNC-006: Test Class Naming - No Consistent Mapping to Source
**ID:** TNC-006
**Location:** Multiple files: `test_ai.py` contains `TestAIController`, `TestAIStrategyStates`, `TestTargetingHelpers`
**Issue:** Test file may contain multiple unrelated test classes not clearly mapped to source modules
**Impact:** Unclear which source class each test class exercises
**Recommendation:** One test class per source class; use naming convention `Test<SourceClassName>`
**Effort:** Medium

---

### TNC-007: Mixed Test and Support Code
**ID:** TNC-007
**Location:** `tests/infrastructure/session_cache.py` (utility, not a test)
**Issue:** Non-test code mixed with test files
**Impact:** Test discovery includes non-test modules
**Recommendation:** Create dedicated `tests/lib/` or `tests/utils/` for helper/infrastructure code
**Effort:** Medium

---

## Major Issues

### TNC-008: Inconsistent Fixture Naming Across Conftest Files
**Location:** 13 `conftest.py` files at various levels
**Issue:** Fixtures defined at multiple levels with varying naming conventions
**Recommendation:** Document fixture hierarchy; use clear naming: `{scope}_{resource}`
**Effort:** Medium

### TNC-009: Mock/Stub Naming Inconsistency
**Location:** `MockEventBus`, `MockMissile`, `MockPlanet`, `MockSystem`
**Issue:** Mock classes use `Mock*` prefix inconsistently
**Recommendation:** Adopt consistent pattern: `Mock*` for test doubles
**Effort:** Simple

### TNC-010: Factory Function Naming Not Standardized
**Location:** `create_test_ship()`, `create_component()` - mixed naming patterns
**Issue:** Factory functions use `create_*()` inconsistently alongside test fixtures
**Recommendation:** Use `pytest.fixture` with factory pattern
**Effort:** Medium

### TNC-011: No Descriptive Test Method Naming Convention
**Location:** All test methods follow simple `test_*()` pattern
**Issue:** Test methods lack behavior indicators: no `test_should_*`, `test_when_*` patterns
**Recommendation:** Adopt BDD-style naming: `test_should_*()` or descriptive names
**Effort:** Complex

---

## Naming Convention Recommendations

| Aspect | Current | Recommended |
|--------|---------|-------------|
| Test File | `test_*.py` | `test_*.py` (keep) |
| Test Class | `Test*` | `Test<SourceModuleName>` |
| Test Method | `test_*()` | `test_should_*()` or `test_when_*()` |
| Mock Class | `Mock*` | `Mock*` (standardized) |
| Fixture Function | Lowercase | `{scope}_{resource}` |
| Factory Function | `create_*()` | `{resource}_factory()` |
| Disabled Test | `_test_*.py` | `@pytest.mark.skip` |

---

## Top 5 Priority Issues

1. **TNC-002: Inverted Directory Structure** - Collapses source hierarchy, breaking structural parity
2. **TNC-001: Non-Standard Test File Names** - 18+ files with inconsistent prefixes
3. **TNC-004: Incomplete Directory Mapping** - 14+ missing test directories
4. **TNC-006: Test Class Not Mapped to Source** - Multiple test classes per file with no clear source mapping
5. **TNC-011: No Descriptive Test Method Naming** - Test purpose unclear; BDD patterns would improve clarity

---


## File: test_suite_reviewer_report.md

# Test Suite Reviewer Report

## Summary
- **Total issues found:** 47
- **Critical:** 8, **Major:** 15, **Minor:** 17, **Info:** 7

---

## Critical Issues

### TSR-001: Disabled Integration Tests
**ID:** TSR-001
**Location:** `tests/integration/_test_formation_attack.py`, `tests/integration/_test_formation_flight.py`
**Issue:** Two integration test files are prefixed with `_test_` instead of `test_`, disabling them from the test suite
**Impact:** Critical formation flight and attack AI behavior tests are not running; potential regressions go undetected
**Recommendation:** Rename files to `test_formation_attack.py` and `test_formation_flight.py` to re-enable
**Effort:** Simple

---

### TSR-002: Incomplete Test with Dead Code
**ID:** TSR-002
**Location:** `tests/integration/_test_formation_attack.py:101`
**Issue:** Line 101 contains only `pass` statement followed by untested code; indicates incomplete test setup
**Impact:** Target dummy creation logic after `pass` is never executed
**Recommendation:** Complete the test setup or remove dead code after pass statement
**Effort:** Medium

---

### TSR-003: Non-Isolated Test Framework
**ID:** TSR-003
**Location:** `tests/unit/core/test_registry.py:23-77`
**Issue:** Multiple conftest.py files (13 total) with inconsistent fixture scope and reset strategies
**Impact:** Test isolation bugs can be hidden; registry state can leak between test classes
**Recommendation:** Standardize on function-scoped fixtures with consistent reset patterns
**Effort:** Complex

---

### TSR-004: Weak Assertion Patterns
**ID:** TSR-004
**Location:** ~24 files use generic assertions like `assert result`, `assert x`
**Issue:** 875 weak assertions identified without specific expected values
**Impact:** Tests pass without verifying actual behavior; false positives in coverage
**Recommendation:** Replace weak assertions with specific value checks
**Effort:** Medium

---

### TSR-005: Large Test Monoliths
**ID:** TSR-005
**Location:** 20 test files exceed 700+ LOC:
  - `test_ship_stats_service.py`: 1756 LOC
  - `test_ship_instance_proj08.py`: 1458 LOC
  - `test_battle_controller.py`: 1317 LOC
  - `test_fleet.py`: 1103 LOC
**Issue:** Mega-tests make it hard to isolate failures
**Impact:** Test failures are hard to diagnose; slow feedback loop
**Recommendation:** Break into smaller focused test classes with single responsibility
**Effort:** Complex

---

### TSR-006: Multiple Mock Patterns
**ID:** TSR-006
**Location:** 3011 mock/patch usages found; inconsistent between files
**Issue:** `@mock.patch`, `@patch`, `Mock()`, `MagicMock()` used interchangeably
**Impact:** Inconsistent test setup/teardown; harder to understand mock dependencies
**Recommendation:** Establish shared patterns in base test classes or fixture helpers
**Effort:** Medium

---

### TSR-007: Fixture Scope Mismatch
**ID:** TSR-007
**Location:** `tests/unit/research/conftest.py`, `tests/test_framework/services/conftest.py`
**Issue:** Mix of function-scoped, class-scoped, and module-scoped fixtures with no clear documentation
**Impact:** Tests may share state unexpectedly; cleanup doesn't happen at expected times
**Recommendation:** Document fixture scope strategy; use function-scoped by default
**Effort:** Medium

---

### TSR-008: Test Organization Inconsistency
**ID:** TSR-008
**Location:** tests directory structure
**Issue:** Tests organized both by feature and by layer, causing redundancy
**Impact:** Hard to find tests for specific features; potential for duplicate testing effort
**Recommendation:** Standardize on either feature-based or layer-based organization
**Effort:** Complex

---

## Major Issues

### TSR-009: Skipped/Deferred Tests
**Location:** 65 pytest.skip calls found throughout tests
**Issue:** Tests conditionally skip based on file presence
**Recommendation:** Make data setup robust or use markers instead of dynamic skips
**Effort:** Medium

### TSR-010: Empty/Stub Test Classes
**Location:** `tests/unit/builder/test_builder_validation.py:233`
**Issue:** Test classes with only `pass` statements
**Recommendation:** Complete tests or remove them
**Effort:** Medium

### TSR-011: Print Statements in Tests
**Location:** Multiple files like `test_seeker_range_calculation.py`
**Issue:** `print()` statements in test code for debugging
**Recommendation:** Replace with proper assertions; use logging for diagnostics
**Effort:** Simple

### TSR-012: Mixed Test Patterns
**Location:** `tests/unit/builder/test_builder_validation.py:270-281`
**Issue:** Tests use both unittest-style methods and pytest-style functions
**Recommendation:** Use pytest fixtures exclusively
**Effort:** Medium

### TSR-013: Hardcoded Test Data
**Location:** 537 fixture definitions with hardcoded data
**Issue:** Many fixtures inline data instead of using factories
**Recommendation:** Use factory fixtures for complex objects
**Effort:** Medium

### TSR-014: Duplicate Test Setup
**Location:** `tests/unit/entities/`, `tests/unit/combat/`
**Issue:** Ship setup code repeated across 5+ test files
**Recommendation:** Create shared Ship factory fixtures in conftest
**Effort:** Simple

### TSR-015: No Docstrings for Complex Tests
**Issue:** ~40% of test classes lack docstrings explaining what behavior they validate
**Recommendation:** Add docstrings to all test classes
**Effort:** Simple

---

## Top 5 Priority Issues

1. **TSR-001: Disabled Integration Tests** - CRITICAL - Tests are not running due to `_test_` prefix
2. **TSR-003: Non-Isolated Test Framework** - CRITICAL - Multiple conftest files with inconsistent fixture scope
3. **TSR-005: Large Test Monoliths** - CRITICAL - 20 tests with 700+ LOC each
4. **TSR-004: Weak Assertion Patterns** - MAJOR - 875 weak assertions provide false confidence
5. **TSR-008: Test Organization Inconsistency** - MAJOR - Mixed feature and layer-based organization

---


## File: ui_system_reviewer_report.md

# UI System Reviewer Report

## Summary
- **Total issues found:** 28
- **Critical:** 5, **Major:** 8, **Minor:** 10, **Info:** 5

---

## Critical Findings

### UI-001: Duplicate Class Definition - BattleSetupScreen
**ID:** UI-001
**Location:**
- `game/ui/screens/setup.py:134` (680 lines)
- `game/ui/screens/setup_screen.py:27` (same class name, ~400 lines)

**Issue:** Two separate implementations of BattleSetupScreen class exist in different files, creating ambiguity and maintenance burden. No clear indication which is canonical or if they serve different purposes.

**Impact:** Import ambiguity, potential runtime errors from importing wrong version, code duplication, maintenance nightmare when bugs are fixed in one but not the other.

**Recommendation:** Consolidate into single canonical BattleSetupScreen. If they differ in functionality, rename one (e.g., BattleSetupScreenLegacy). Update all imports to use canonical version. If both are truly needed, add clear architectural documentation explaining when each should be used.

**Effort:** Medium (requires import audit and consolidation)

---

### UI-002: Broken Import Path in workshop_screen.py
**ID:** UI-002
**Location:** `game/ui/screens/workshop_screen.py:25, 27-29, 59`

**Issue:** Uses incorrect relative imports `from ui.builder ...` instead of `from game.ui.screens.builder ...`. Lines affected:
```python
from ui.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
from ui.builder.schematic_view import SchematicView
from ui.builder.interaction_controller import InteractionController
from ui.builder.event_bus import EventBus
from ui.builder.detail_panel import ComponentDetailPanel
```

**Impact:** These imports will fail at runtime. The DesignWorkshopGUI cannot load. This appears to be a copy-paste error from an unfinished refactor or migration.

**Recommendation:** Replace all `from ui.builder` with `from game.ui.screens.builder`. Verify imports work by running application.

**Effort:** Simple (5-minute fix)

---

### UI-003: Broken Import Paths in design_report_panel.py
**ID:** UI-003
**Location:** `game/ui/panels/design_report_panel.py:19-20`

**Issue:** Uses incorrect relative imports:
```python
from ui.builder.right_panel import StatRow
from ui.builder.stats_config import STATS_CONFIG, get_construction_rows
```

Should be `from game.ui.screens.builder...`

**Impact:** Import failures, DesignReportPanel cannot load. Blocks any code that tries to instantiate this panel.

**Recommendation:** Fix import paths to use full module path `from game.ui.screens.builder...`. Test to verify.

**Effort:** Simple (2-minute fix)

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
- Split race_setup_screen into: RaceSummaryPanel, RaceVisualsPanel, RaceEnvironmentPanel, RaceDescriptionPanel (already partially done with extracted panels)
- Split formation_editor into FormationCore (model), FormationRenderer, FormationInputHandler, FormationUI
- Split builder/main.py into BuilderGUI (orchestrator), BuilderLayout, BuilderStateManager, and component-specific panels
- Use composition pattern to combine sub-modules

**Effort:** Complex (2-3 days refactoring per file)

---

### UI-005: Legacy Components Editor Panel Still Active
**ID:** UI-005
**Location:** `game/ui/screens/builder/legacy_components.py` (188 lines)

**Issue:** File explicitly labeled "Legacy" and containing ModifierEditorPanel is still actively imported and used in builder/main.py. Header says "Consider migration to ModifierLogic for new code" but no migration path provided. Cross-layer import to MODIFIER_REGISTRY from simulation layer.

**Impact:** Technical debt accumulation, confusion about canonical modifier editing approach, inconsistent patterns across codebase, direct simulation layer dependency in UI code.

**Recommendation:**
1. Audit all uses of ModifierEditorPanel - ensure it's not used in new code
2. Create migration plan for existing uses to ModifierLogic-based approach
3. If truly needed for backward compatibility, move to `game/ui/legacy/` directory and clearly mark deprecation
4. Provide detailed migration guide in docstring

**Effort:** Complex (requires pattern audit and standardization)

---

## Major Findings

### UI-006: Inconsistent Screen/Scene/Interface Naming Convention
**ID:** UI-006
**Location:** Throughout `game/ui/screens/`

**Issue:** No consistent naming convention for main UI screen classes:
- Classes named `Scene`: BattleScene, StrategyScene, FormationEditorScene, TestLabScene
- Classes named `Screen`: BattleSetupScreen, BuildQueueScreen, RaceSetupScreen, new_game_setup_screen
- Classes named `Interface`: BattleInterface, StrategyInterface
- Classes named `GUI`: BuilderSceneGUI, DesignWorkshopGUI

This creates confusion about class purpose and appropriate usage pattern.

**Impact:** Cognitive overhead, inconsistent architecture understanding across team, harder to find related code, anti-pattern learning for new developers.

**Recommendation:** Establish and enforce single convention:
- Option A: All main screens as `*Screen` (most consistent with pygame_gui)
- Option B: All as `*Scene` (game engine terminology)
- Option C: All as `*GUI` (clearly indicates UI responsibility)

Recommended: Option A (`*Screen`) as pygame_gui standard.

**Effort:** Medium (rename + import updates across codebase)

---

### UI-007: Inconsistent Event Handler Naming
**ID:** UI-007
**Location:** 33 files with event handlers, inconsistent naming patterns

**Issue:** Different files use different event handler method names:
- `handle_event()` - used in widgets.py, build_queue_screen.py, formation_editor.py, planet_list_window.py
- `process_event()` - some components
- `on_event()` - used in event bus subscribers
- `on_*` prefix - used extensively for callbacks and event subscriptions

No consistent pattern makes it unclear which method to override/call for event handling.

**Impact:** Developers must check each class to understand event handling pattern, error-prone when creating new components, IDE autocomplete less helpful with inconsistency.

**Recommendation:** Establish consistent naming:
- Main event dispatch: `handle_event(event)` for all UI components
- Callbacks/subscriptions: `on_*_changed()` or similar
- Internal handlers: `_handle_*()` (private)

**Effort:** Medium (requires audit and systematic renaming)

---

### UI-008: Manual UI Lifecycle Management Scattered
**ID:** UI-008
**Location:** Throughout UI codebase, especially builder modules

**Issue:** Manual `.kill()`, `.hide()`, `.show()` calls scattered throughout code instead of using container/manager lifecycle patterns.

**Impact:** Memory leaks if elements not properly killed, fragile code that breaks when UI framework updates, hard to debug missing/phantom UI elements.

**Recommendation:**
- Use pygame_gui container lifecycle management for all created elements
- When elements must be created dynamically, store references in managed containers
- Create helper methods for common cleanup patterns

**Effort:** Medium (systematic refactoring of lifecycle patterns)

---

### UI-009: Tight Coupling Between Builder Panels and Data Models
**ID:** UI-009
**Location:** `game/ui/screens/builder/` directory

**Issue:** Builder panels directly access and manipulate ship data structures:
- left_panel.py accesses `self.builder.available_components`
- right_panel.py directly calls `builder.ship.recalculate_stats()`
- detail_panel.py directly modifies component objects
- No clear data flow or state management

**Impact:** Hard to test UI independently, builder state changes unpredictable, difficult to undo/redo operations, changes to ship structure break multiple panels.

**Recommendation:**
- Implement proper ViewModel pattern (partial implementation exists in workshop_viewmodel.py)
- Create ShipBuilder facade/service that panels interact with instead of direct data access
- Make state changes fire events through event bus

**Effort:** Complex (3-4 days architectural work)

---

### UI-010: Legacy Tuple-Based Component Reference Pattern
**ID:** UI-010
**Location:** `game/ui/screens/builder/component_ref.py`

**Issue:** Component references stored as tuples `(layer_type, index, component)` with new ComponentRef class trying to abstract but legacy pattern still alive.

**Impact:** Code confusion about canonical representation, multiple patterns in codebase, harder to type-check.

**Recommendation:**
- Complete migration to ComponentRef typed class
- Remove tuple-based code once all uses updated
- Add type hints throughout

**Effort:** Medium (audit all component references and consolidate)

---

### UI-011: Inconsistent Panel Builder Patterns
**ID:** UI-011
**Location:** `game/ui/panels/` directory

**Issue:** Each panel implements layout/building differently:
- Some use `__init__` for full setup
- Some use separate `build_ui()` or `layout()` methods
- Some rebuild dynamically on state change
- Different approaches to scrolling container management

**Impact:** New developers must learn multiple patterns, copy-paste errors when creating new panels.

**Recommendation:**
- Create BasePanel abstract class with standard interface
- All panels inherit from BasePanel
- Standardize on this lifecycle

**Effort:** Medium-Complex (refactor 8+ panels + create base class)

---

### UI-012: Duplicate Code in Setup Screens
**ID:** UI-012
**Location:**
- `game/ui/screens/setup.py` (680 lines)
- `game/ui/screens/setup_screen.py`
- `game/ui/screens/setup_data_io.py` (90 lines)

**Issue:** Multiple implementations of setup screen functionality, duplicated scan/load functions, BattleSetupScreen defined twice.

**Impact:** Bugs fixed in one file but not others, maintenance overhead.

**Recommendation:** Consolidate into single setup module with clear separation.

**Effort:** Medium (consolidation + testing)

---

### UI-013: Large Hardcoded Layout Constants Scattered
**ID:** UI-013
**Location:** Throughout builder and screen files

**Issue:** Pixel dimensions and spacing values hardcoded inline rather than centralized.

**Impact:** Hard to create consistent UI, impossible to implement themes/scaling.

**Recommendation:**
- Extend builder_utils.py pattern to all UI screens
- Create centralized UILayout configuration system
- Move all magic numbers to CONSTANTS dict/class

**Effort:** Medium (systematic refactoring)

---

## Minor Findings

### UI-014: Complex Conditional Rendering Logic
**Location:** Multiple files, particularly strategy and complex screens
**Issue:** Nested conditionals for UI visibility/rendering scattered throughout, no clear state machine.
**Recommendation:** Implement explicit UI state machine for each complex screen.
**Effort:** Medium-Complex

### UI-015: Missing Abstractions for Common Panel Layouts
**Location:** Throughout `game/ui/panels/`
**Issue:** Multiple implementations of similar patterns (gallery panels, report panels, grid panels).
**Recommendation:** Create base classes for GalleryPanel, ReportPanel, TablePanel.
**Effort:** Medium

### UI-016: Widget/Component Naming Inconsistency
**Location:** Throughout `game/ui/`
**Issue:** No clear terminology distinction between Widget, Component, Panel.
**Recommendation:** Establish and document terminology.
**Effort:** Low-Medium

### UI-017: Constants Not Centralized (Colors, Sizes, Spacing)
**Location:** Throughout UI codebase
**Issue:** Magic numbers and colors defined throughout, not always using game/ui/colors.py.
**Recommendation:** Create game/ui/theme.py with all layout constants.
**Effort:** Simple-Medium

### UI-018: Inconsistent Import Organization
**Location:** Throughout UI files
**Issue:** Import order and TYPE_CHECKING usage varies.
**Recommendation:** Use linting rules to enforce consistent imports.
**Effort:** Simple

### UI-019: Event Bus Subscription Patterns Not Consistently Applied
**Location:** `game/ui/screens/builder/`
**Issue:** Event bus exists but not used consistently across all panels.
**Recommendation:** Extend event bus usage systematically.
**Effort:** Medium

### UI-020: Multiple Implementations of Similar Gallery/Display Panels
**Location:** game/ui/panels/
**Issue:** Three nearly-identical gallery implementations for different asset types.
**Recommendation:** Create GenericGalleryPanel parameterized by data source.
**Effort:** Medium

### UI-021: Placeholder Text Generation Duplicated
**Location:** Multiple files
**Issue:** Placeholder message generation code repeated.
**Recommendation:** Create UIPlaceholder helper class.
**Effort:** Simple

### UI-022: Weak Separation of Concerns in Composite Panels
**Location:** race_setup_screen.py, builder/main.py
**Issue:** Panels that combine sub-panels don't have clear responsibility boundaries.
**Recommendation:** Use composition pattern more strictly.
**Effort:** Medium-Complex

### UI-023: Inconsistent Container Initialization
**Location:** Builder panels and various screens
**Issue:** Different initialization patterns for panel containers.
**Recommendation:** Standardize panel __init__ signature.
**Effort:** Medium

---

## Info Observations

### UI-024: Layer Violations - UI Directly Using Simulation Components
**Location:** Multiple files with cross-layer imports
**Issue:** UI layer imports directly from simulation layer.
**Recommendation:** Create UI-layer facades/services.
**Effort:** Complex

### UI-025: File System Access Not Centralized
**Location:** Multiple screens handling file I/O independently
**Issue:** Different files access file system independently.
**Recommendation:** Create UIFileSystemService.
**Effort:** Medium

### UI-026: No Screen Transition Manager
**Location:** Screen/scene management scattered throughout
**Issue:** Different screens activated/deactivated through different mechanisms.
**Recommendation:** Create ScreenManager/SceneManager class.
**Effort:** Medium

### UI-027: High Fragmentation of UI Container Classes
**Observation:** 42 main UI container classes (Scene/Screen/Interface/GUI) across 91 files.
**Recommendation:** Consider package-based organization.

### UI-028: 33 Unique Event Handler Implementations
**Observation:** Extensive event handling system with 33 different handle_event implementations.
**Recommendation:** Document event handling architecture and create standardized patterns.

---

## Top 5 Priority Issues

1. **UI-002 & UI-003: Fix Broken Import Paths (URGENT)**
   - workshop_screen.py and design_report_panel.py have broken imports
   - Simple 5-minute fixes that unblock functionality

2. **UI-001: Consolidate Duplicate BattleSetupScreen Classes**
   - Two identical class names in different files causing confusion
   - 1-2 hours to audit, consolidate, and test

3. **UI-004: Break Up 1200+ Line Monolithic Screens**
   - race_setup_screen (1231), formation_editor (1103), builder/main (1100)
   - Complex refactoring but high ROI

4. **UI-006: Establish Consistent Screen Naming Convention**
   - Scene vs Screen vs Interface vs GUI terminology confusion
   - High impact on understanding

5. **UI-009: Reduce Tight Coupling in Builder Panels**
   - Builder panels directly manipulate ship data with no isolation
   - Essential for code quality

---


# Source: 2026-01-28_general_maintainability-extensibility

---


## File: architecture_report.md

# Architecture Review Report

## Summary
- **Total issues found:** 15
- **Critical:** 4
- **Major:** 7
- **Minor:** 4
- **Info:** 0

---

## Findings

### CRITICAL: UI Layer Directly Instantiates Simulation Objects
**ID:** AR-01
**Location:** `game/ui/screens/setup.py:94-128`, `game/ui/screens/builder/main.py:90`, `game/ui/screens/workshop_screen.py:18-38`
**Issue:** UI code directly creates `Ship` objects and accesses/modifies their internal attributes. UI layer imports directly from `game.simulation.entities.ship`.
**Impact:** Violates layered architecture. Changes to ship internals break UI code. Cannot swap simulation implementations.
**Recommendation:** Create UI-facing Ship DTO/Command pattern. UI should issue commands rather than directly mutating ships.
**Effort:** Complex

### CRITICAL: Global Mutable State in Core Registries
**ID:** AR-02
**Location:** `game/simulation/components/component.py:74-75`, `game/core/registry.py:92-93`
**Issue:** Shared global state (`COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES`) exposed as module-level variables. 77 files import from `game.core.config`.
**Impact:** Cannot safely run tests in parallel. Registry state persists between tests/scenes. Hidden dependencies.
**Recommendation:** Migrate to dependency injection via `GameRegistries` container. Use constructor injection.
**Effort:** Complex

### CRITICAL: Feature Envy - Builder Components Accessing Ship Internals
**ID:** AR-03
**Location:** `game/ui/screens/builder/main.py:90-91,569,859-860,972`
**Issue:** Builder UI extensively accesses and manipulates ship component layers, modifiers, and design data. Performs business logic that belongs in simulation layer.
**Impact:** Duplicate validation logic. Ship design logic spread across UI and simulation.
**Recommendation:** Extract ship builder logic into `ShipDesignService` in simulation layer.
**Effort:** Complex

### CRITICAL: Circular Dependency Risk - Strategy â†” Simulation
**ID:** AR-04
**Location:** `game/strategy/adapters/simulation_adapter.py:24-27`, `game/strategy/services/ship_stats_service.py:27-28`
**Issue:** Strategy layer imports directly from simulation layer. While currently one-directional, tight coupling creates risk.
**Impact:** Strategy layer cannot be tested independently. Changes to simulation break strategy layer.
**Recommendation:** Strategy layer should only depend on `IBattleResolver` interface and DTOs.
**Effort:** Medium

### MAJOR: LayerType Constant Duplication
**ID:** AR-05
**Location:** Multiple files reference `LayerType` from different import paths
**Issue:** `LayerType` defined in `game.simulation.components.component_constants` but imported from `game.core.constants` in UI files.
**Impact:** Confusing and error-prone. Layering violation.
**Recommendation:** Move `LayerType` to single canonical location. Update all files.
**Effort:** Medium

### MAJOR: No Clean Interface Between UI and Battle Layers
**ID:** AR-06
**Location:** `game/ui/screens/battle_scene.py:23-26`, `game/ui/hud/panels.py:3-17`
**Issue:** UI battle code imports directly from simulation. Battle panels directly access ship objects.
**Impact:** Battle UI tightly coupled to simulation internals. Cannot mock for UI testing.
**Recommendation:** Create `IBattleUI` service interface exposing only what UI needs.
**Effort:** Medium

### MAJOR: Ship Class is God Object - 834 Lines
**ID:** AR-07
**Location:** `game/simulation/entities/ship.py`
**Issue:** Ship class handles physics, combat, component management, stats, serialization, resources, formations. 834 lines via mixins.
**Impact:** Difficult to understand. High cognitive load. Testing is complex.
**Recommendation:** Break into ShipPhysics, ShipCombat, ShipComponents, ShipResources using composition.
**Effort:** Complex

### MAJOR: Inappropriate Intimacy - Workshop Screen Manages Simulation Data
**ID:** AR-08
**Location:** `game/ui/screens/workshop_screen.py:68-92`
**Issue:** DesignWorkshopGUI directly manages ship designs, components, modifiers through persistence layer.
**Impact:** Cannot reuse design management logic outside UI. UI changes require business logic changes.
**Recommendation:** Extract design management to `ShipDesignRepository` service.
**Effort:** Medium

### MAJOR: Missing Abstraction for Component System Access
**ID:** AR-09
**Location:** `game/ui/screens/builder/modifier_logic.py:8`, `game/simulation/components/component.py:74-75`
**Issue:** Direct access to `MODIFIER_REGISTRY` and `COMPONENT_REGISTRY` globals from UI code.
**Impact:** UI tightly coupled to registry structure. Cannot change registry implementation.
**Recommendation:** Create `ComponentService` interface with get_components(), get_modifiers() methods.
**Effort:** Simple

### MAJOR: Validation Logic Scattered Across Layers
**ID:** AR-10
**Location:** `game/simulation/systems/validator.py`, `game/ui/screens/race_validator.py`, `game/strategy/validation/base.py`
**Issue:** Validation rules scattered across simulation, UI, and strategy layers.
**Impact:** Consistency issues. UI might allow invalid state that simulation rejects.
**Recommendation:** Create unified `ValidationEngine` in core layer.
**Effort:** Medium

### MINOR: Module Bloat - Large UI Screen Classes
**ID:** AR-11
**Location:** `game/ui/screens/race_setup_screen.py:1231 LOC`, `game/ui/screens/fleet_report_window.py:1034 LOC`
**Issue:** Very large UI screen classes handling multiple concerns.
**Impact:** Difficult to navigate and unit test.
**Recommendation:** Break into smaller focused components with composition.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **AR-02: Global Mutable State in Core Registries** - Root cause of extensibility problems. Makes parallel testing impossible.

2. **AR-01: UI Layer Directly Instantiates Simulation Objects** - Direct violation of layered architecture. Prevents testing and layer independence.

3. **AR-04: Circular Dependency Risk** - Currently works but fragile. Dependency inversion not followed.

4. **AR-03: Feature Envy - Builder Components** - Duplicates business logic from simulation layer (shotgun surgery indicator).

5. **AR-07: Ship Class God Object** - 834 lines with too many responsibilities. High cognitive load blocks extending.

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


## File: dead_code_report.md

# Dead Code Review Report

## Summary
- **Total issues found:** 11
- **Critical:** 2
- **Major:** 4
- **Minor:** 4
- **Info:** 1

---

## Findings

### CRITICAL: Broken Import References in Main Application
**ID:** DC-01
**Location:** `game/app.py:28-29`
**Issue:** App imports non-existent modules:
```python
from Tools.formation_editor import FormationEditorScene
from ui.test_lab_scene import TestLabScene
```
These modules don't exist at the referenced paths.
**Impact:** Runtime ImportError will occur if TEST_LAB or FORMATION states are activated.
**Recommendation:** Update imports to correct paths or move modules into proper game package structure.
**Effort:** Simple

### CRITICAL: Backup File Committed to Repository
**ID:** DC-02
**Location:** `ui/test_lab_scene.py.backup`
**Issue:** A 2,731-line backup file of test_lab_scene.py is committed alongside the active version.
**Impact:** Increases repo size, creates confusion about which version is active.
**Recommendation:** Delete the `.backup` file. Use git history if older version is needed.
**Effort:** Simple

### MAJOR: Marked-for-Deletion Directory Unresolved
**ID:** DC-03
**Location:** `./_marked_for_deletion_2026-01-27/`
**Issue:** Entire directory marked for deletion but still in the repository.
**Impact:** Clutters repo, indicates incomplete cleanup.
**Recommendation:** Delete the entire directory or properly archive.
**Effort:** Simple

### MAJOR: Incorrect Import Path for TestLabScene
**ID:** DC-04
**Location:** `game/app.py:29` / Actual module at `ui/test_lab_scene.py`
**Issue:** app.py imports from `ui.test_lab_scene` but ui/ is outside the game package.
**Impact:** Import will fail at runtime when TEST_LAB state is accessed.
**Recommendation:** Move `ui/` into `game/ui/screens/` or create proper import path handling.
**Effort:** Medium

### MAJOR: Incorrect Import Path for FormationEditorScene
**ID:** DC-05
**Location:** `game/app.py:28` / Actual module at `Tools/formation_editor.py`
**Issue:** app.py imports from `Tools.formation_editor` but Tools/ is outside game package.
**Impact:** Import will fail at runtime when FORMATION state is accessed.
**Recommendation:** Move Tools into proper package structure or fix import paths.
**Effort:** Medium

### MAJOR: Empty Init Files - Incomplete Package Setup
**ID:** DC-06
**Location:** Multiple `__init__.py` files (14 files with 0 lines)
**Issue:** Empty __init__.py files without package-level exports for cleaner imports.
**Impact:** Forces deep import paths, makes package exports unclear.
**Recommendation:** Add meaningful __all__ exports or remove unnecessary package structure.
**Effort:** Medium

### MINOR: Unused Backward Compatibility Path Exports
**ID:** DC-07
**Location:** `game/core/paths.py:89-98`
**Issue:** Module exports old-style path constants for backward compatibility that duplicate the Paths class API.
**Impact:** Code duplication, confusing API surface.
**Recommendation:** Migrate all uses to `Paths.` class API. Remove once converted.
**Effort:** Simple

### MINOR: Unused Path Constants
**ID:** DC-08
**Location:** `game/core/paths.py:59-60, 98`
**Issue:** `VEHICLE_CLASSES_FILE` and `VEHICLE_LAYERS_FILE` defined but rarely used in active code.
**Impact:** Dead API surface.
**Recommendation:** Verify not needed; remove or consolidate.
**Effort:** Simple

### MINOR: Duplicate Imports in constants.py
**ID:** DC-09
**Location:** `game/core/constants.py:1-9, 31-53`
**Issue:** File imports from enum twice. Also re-exports from Paths duplicating paths.py.
**Impact:** Code redundancy.
**Recommendation:** Clean up duplicate imports, consolidate re-exports.
**Effort:** Simple

### MINOR: Legacy Comment Marker
**ID:** DC-10
**Location:** `game/ui/screens/test_lab.py:88-100`
**Issue:** Commented-out code block with notes about removed functionality.
**Impact:** Minor - shows incomplete cleanup from refactoring.
**Recommendation:** Remove once surrounding code is stable.
**Effort:** Simple

### INFO: Debugging Scripts Not Integrated
**ID:** DC-11
**Location:** `Debugging/archive_confirmed.py`, `Debugging/confirm_bugs_ui.py`
**Issue:** Debug automation scripts exist but aren't integrated into CI pipeline.
**Impact:** Unused tooling.
**Recommendation:** Integrate into debug workflow or remove if not needed.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **DC-01: Broken Imports in game/app.py** - Will cause immediate runtime failures

2. **DC-02: Backup File Committed** - Quick win: delete backup file

3. **DC-04/DC-05: Incorrect Import Paths** - Fix requires architectural decision about package structure

4. **DC-03: Marked-for-Deletion Directory** - Quick win: delete entire directory

5. **DC-06: Empty __init__.py Files** - Consolidate package structure for better imports

---


## File: documentation_report.md

# Documentation Review Report

## Summary
- **Total issues found:** 47
- **Critical:** 8
- **Major:** 18
- **Minor:** 15
- **Info:** 6

---

## Findings

### CRITICAL: EventBus - No Documentation
**ID:** DOC-01
**Location:** `game/ui/screens/builder/event_bus.py`
**Issue:** Complete lack of module and class documentation. 5 public methods with no docstrings.
**Impact:** Critical pub/sub pattern in builder UI with no explanation of event flow
**Recommendation:** Add module docstring explaining event pattern, document all methods
**Effort:** Simple

### CRITICAL: InteractionController - Incomplete Documentation
**ID:** DOC-02
**Location:** `game/ui/screens/builder/interaction_controller.py`
**Issue:** Class lacks module-level docstring. 14 public/protected methods without docstrings. Complex drag-drop logic unexplained.
**Impact:** Critical interaction handler with unclear component lifecycle
**Recommendation:** Add module docstring with interaction pattern overview
**Effort:** Medium

### CRITICAL: InputHandler - Minimal Documentation
**ID:** DOC-03
**Location:** `game/core/input_handler.py`
**Issue:** Methods lack documentation. Complex keybinding logic (7 methods) unexplained.
**Impact:** Core input handling with no explanation of speed modifier behavior
**Recommendation:** Document all methods, explain speed multiplier strategy
**Effort:** Simple

### CRITICAL: WeaponAbility - Incomplete Initialization Documentation
**ID:** DOC-04
**Location:** `game/simulation/components/abilities/weapons.py`
**Issue:** Complex formula parsing logic (30+ lines) lacks documentation. No explanation of formula string format.
**Impact:** Core combat ability initialization unclear
**Recommendation:** Document formula string format, explain fallback chain
**Effort:** Medium

### CRITICAL: Camera.update() - Missing Zoom Anchor Logic
**ID:** DOC-05
**Location:** `game/ui/renderer/camera.py:24-45`
**Issue:** Complex smooth zoom interpolation with no docstring. Zoom anchor mechanism unexplained.
**Impact:** Smooth camera behavior logic unclear for maintenance
**Recommendation:** Add docstring explaining zoom anchor preservation
**Effort:** Simple

### CRITICAL: ModifierControlRow - No Class Documentation
**ID:** DOC-06
**Location:** `game/ui/screens/builder/modifier_row.py:6-36`
**Issue:** Complex UI widget class with no docstring. 10+ undocumented methods.
**Impact:** Complex modifier UI with unclear lifecycle
**Recommendation:** Add class docstring explaining pooling/layout pattern
**Effort:** Medium

### CRITICAL: FleetMovementSimulator - Deprecated but Undocumented
**ID:** DOC-07
**Location:** `game/strategy/engine/fleet_movement.py:63-80`
**Issue:** Deprecation warning exists but migration guide incomplete
**Impact:** Developers may misuse deprecated class
**Recommendation:** Add comprehensive deprecation guide with migration steps
**Effort:** Medium

### CRITICAL: ModifierLogic - Complex Logic, Minimal Documentation
**ID:** DOC-08
**Location:** `game/ui/screens/builder/modifier_logic.py:10-100`
**Issue:** Complex ability detection (100+ lines) lacks documentation
**Impact:** Critical modifier validation with unclear detection strategy
**Recommendation:** Add method docstrings, explain ability detection strategy
**Effort:** Medium

### MAJOR: BattleController - Incomplete Return Value Documentation
**ID:** DOC-09
**Location:** `game/simulation/battle_controller.py:90-170`
**Issue:** Methods return BattleResult but structure not documented
**Impact:** Result handling unclear
**Recommendation:** Document BattleResult structure in module docstring
**Effort:** Simple

### MAJOR: ModifierService - Confusing Dual-Pattern Documentation
**ID:** DOC-10
**Location:** `game/simulation/services/modifier_service.py:54-80`
**Issue:** Support for both static and instance calling patterns poorly documented
**Impact:** Developers may misuse service
**Recommendation:** Add clear usage examples for both patterns
**Effort:** Medium

### MAJOR: ShipCombatEngine.solve_lead() - Algorithm Undocumented
**ID:** DOC-11
**Location:** `game/simulation/entities/ship_combat_engine.py:47-94`
**Issue:** Quadratic formula for projectile interception lacks mathematical explanation
**Impact:** Complex physics algorithm unclear for maintenance
**Recommendation:** Add mathematical background in docstring
**Effort:** Medium

### MAJOR: Complex UI Methods Missing Docstrings
**ID:** DOC-12
**Location:** Multiple UI screen files
**Issue:** draw_debug_overlay(), _create_ui(), event handlers lack documentation
**Impact:** Debug visualization and UI logic unmaintainable
**Recommendation:** Add docstrings explaining each method's purpose
**Effort:** Medium

---

## Top 5 Priority Issues

1. **DOC-01: EventBus - Complete Documentation Void** - No docs for critical pub/sub pattern

2. **DOC-04: WeaponAbility Formula Parsing** - Core combat with unclear formula handling

3. **DOC-09: BattleController Return Values** - Developers unsure what results contain

4. **DOC-02: InteractionController State Machine** - Complex drag-drop with no docs

5. **DOC-10: ModifierService Dual-Pattern** - Confusing API surface

---


## File: error_handling_report.md

# Error Handling Audit Report

## Summary
- **Total issues found:** 42
- **Critical:** 5
- **Major:** 12
- **Minor:** 18
- **Info:** 7

---

## Findings

### CRITICAL: Bare Exception Clause Without Logging
**ID:** ERR-01
**Location:** `scripts/apply_resource_costs.py:96`
**Issue:** Bare `except: pass` silently swallows all exceptions including SystemExit and KeyboardInterrupt
```python
try:
    tier = int(comp_id.split("tier")[-1])
except: pass  # <- Bare except, no logging
```
**Impact:** Parse failures go completely undetected. Impossible to debug.
**Recommendation:** Replace with specific exception handling and logging.
**Effort:** Simple

### CRITICAL: Swallowed Exception in AI System
**ID:** ERR-02
**Location:** `game/ai/target_evaluator.py:34-35, 49-50`
**Issue:** Bare `except Exception: pass` silently catches all errors in targeting logic
**Impact:** Position retrieval failures cause incorrect targeting. Silent fallback to stale data.
**Recommendation:** Log the exception and provide fallback explanation.
**Effort:** Simple

### CRITICAL: Unhandled Division by Zero Risk
**ID:** ERR-03
**Location:** `game/ai/target_evaluator.py:224`
**Issue:** Division without zero-check in formula system. Similar patterns elsewhere don't have protection.
**Impact:** Formula system doesn't validate user-input formulas for division by zero.
**Recommendation:** Implement formula validation in ModifierEffectEvaluator.
**Effort:** Medium

### CRITICAL: Silent Input Validation Failure
**ID:** ERR-04
**Location:** `game/simulation/components/modifier_effects.py:148, 198, 251`
**Issue:** Exception handling in formula evaluation without adequate context
**Impact:** When formula evaluation fails, no context about which modifier/component failed.
**Recommendation:** Include modifier ID, component ID, and formula in error message.
**Effort:** Medium

### CRITICAL: Resource Loading Failure Suppression
**ID:** ERR-05
**Location:** `game/core/resources.py:77-79, 111-113`
**Issue:** Exception silently caught during resource loading with generic fallback
**Impact:** Game silently degrades when resource definitions are corrupted.
**Recommendation:** Log specific error details before fallback.
**Effort:** Simple

### MAJOR: Incomplete Error Context in Save/Load
**ID:** ERR-06
**Location:** `game/strategy/systems/save_game_service.py:109-111, 173-176`
**Issue:** Generic Exception handling loses critical context
**Impact:** Error messages to user are generic. Can't distinguish disk full vs permission denied.
**Recommendation:** Categorize exceptions and provide specific user-facing messages.
**Effort:** Medium

### MAJOR: Missing Input Validation
**ID:** ERR-07
**Location:** `game/ui/screens/build_queue_screen.py:68-71`
**Issue:** Validation inconsistent - first check raises exception, second just logs warning
**Impact:** Inconsistent error handling patterns lead to hard-to-debug issues.
**Recommendation:** Consistent validation with clear patterns.
**Effort:** Simple

### MAJOR: Swallowed KeyError in Battle State
**ID:** ERR-08
**Location:** `game/simulation/battle_state.py:271`
**Issue:** KeyError silently caught without context
**Impact:** Missing data in battle state causes silent skips. State becomes corrupted.
**Recommendation:** Log the missing key before skipping.
**Effort:** Simple

### MAJOR: AI Controller Error Handling Gap
**ID:** ERR-09
**Location:** `game/ai/controller.py:334`
**Issue:** Specific exception catch without context or recovery strategy
**Impact:** Targeting logic failures silently ignored. AI falls back to undefined behavior.
**Recommendation:** Log failure and use safe default.
**Effort:** Simple

### MAJOR: Asset Manager Silent Failures
**ID:** ERR-10
**Location:** `game/assets/asset_manager.py:73-82, 102-104`
**Issue:** Asset loading fails silently with placeholder fallback
**Impact:** Game runs with missing assets. User has no indication content is missing.
**Recommendation:** Add asset load tracking and notify UI of missing assets.
**Effort:** Medium

### MAJOR: Formation Editor JSON Error Handling
**ID:** ERR-11
**Location:** `game/ui/screens/formation_editor.py:212`
**Issue:** Generic exception catch loses context about specific error type
**Impact:** User can't distinguish "file not found" vs "invalid JSON" vs "missing data".
**Recommendation:** Specific handling for each error type.
**Effort:** Medium

### MAJOR: Component Status Transition Without Validation
**ID:** ERR-12
**Location:** `game/simulation/components/component.py:99-101`
**Issue:** Fallback to legacy pattern if registries not available, later code doesn't handle None
**Impact:** NoneType errors can occur when registries needed but None.
**Recommendation:** Either raise or mark explicitly with clear handling.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **ERR-01: Bare Exception in Resource Costs** - Silent swallowing makes debugging impossible

2. **ERR-02: Swallowed Exception in AI Targeting** - Causes unpredictable AI behavior

3. **ERR-05: Resource Loading Failure Suppression** - Game runs with missing content silently

4. **ERR-06: Generic Save/Load Error Messages** - Poor user experience, support costs

5. **ERR-04: Silent Input Validation Failure** - Formula errors have no context

---


## File: performance_report.md

# Performance Review Report

## Summary
- **Total issues found:** 10
- **Critical:** 3
- **Major:** 5
- **Minor:** 2
- **Info:** 0

---

## Findings

### CRITICAL: Nested Component Iteration in Hot Path
**ID:** PERF-01
**Location:** `game/simulation/systems/battle_engine.py:515`, `game/simulation/entities/ship_stats.py:89-90`
**Issue:** `get_all_components()` called repeatedly in hot combat loops. Each call rebuilds a list by iterating all layers.
**Impact:** O(n) list construction multiple times per tick per ship. With 100+ ships, thousands of unnecessary iterations.
**Recommendation:** Cache component list on ship or use generator for immutable iteration.
**Effort:** Medium

### CRITICAL: Projectile List Reconstruction Every Tick
**ID:** PERF-02
**Location:** `game/simulation/projectile_manager.py:138`
**Issue:** `self.projectiles = [p for p in self.projectiles if i not in projectiles_to_remove]` rebuilds entire list every tick.
**Impact:** O(n) memory churn every tick.
**Recommendation:** Use index-based removal or mark dead projectiles for batch cleanup.
**Effort:** Medium

### CRITICAL: O(nÂ²) Targeting Evaluation
**ID:** PERF-03
**Location:** `game/ai/controller.py:124-141`
**Issue:** `_score_and_sort_enemies()` sorts all candidates every tick. Evaluator scans all components for each target.
**Impact:** With 50+ targets, creates O(nÂ²) component scans per frame.
**Recommendation:** Cache weapon/ability availability per ship.
**Effort:** Medium

### MAJOR: Repeated Deep Copies on Initialization
**ID:** PERF-04
**Location:** `game/simulation/components/component.py:91, 134, 543`
**Issue:** Three `deepcopy()` calls during component init: data, abilities, base_abilities.
**Impact:** Expensive for complex components. Happens for every component in every ship.
**Recommendation:** Use shallow copies where mutation isn't needed.
**Effort:** Simple

### MAJOR: Inefficient Ability Lookup with MRO Fallback
**ID:** PERF-05
**Location:** `game/simulation/components/component.py:182-209`
**Issue:** `get_abilities()` uses fallback isinstance/MRO walking on every lookup.
**Impact:** O(n) method resolution order walk per ability query.
**Recommendation:** Build ability name index during instantiation.
**Effort:** Simple

### MAJOR: Spatial Grid Cleared Every Tick
**ID:** PERF-06
**Location:** `game/simulation/systems/battle_engine.py:344-351`
**Issue:** Entire spatial grid cleared and rebuilt with all ships/projectiles every tick.
**Impact:** Unnecessary O(n) churn. Could use incremental updates.
**Recommendation:** Use quad-tree or incremental grid updates.
**Effort:** Complex

### MAJOR: Beam Targeting Multiple Raycasts
**ID:** PERF-07
**Location:** `game/engine/collision.py:64-137`
**Issue:** Each beam recalculates sphere-ray intersection even for same target.
**Impact:** Multiple beams vs same target = repeated expensive math.
**Recommendation:** Cache intersection results per target per tick.
**Effort:** Medium

### MAJOR: Component Status Checks on Every Damage Frame
**ID:** PERF-08
**Location:** `game/simulation/entities/ship_stats.py:145-153`
**Issue:** Damage threshold checks iterated for all components during `calculate()` which runs frequently.
**Impact:** Repeated HP ratio calculations (division is expensive).
**Recommendation:** Cache damage status with dirty flag system.
**Effort:** Medium

### MINOR: Repeated Vector2 Conversions
**ID:** PERF-09
**Location:** `game/simulation/projectile_manager.py:47-48, 63-64`
**Issue:** Creates new Vector2 objects from existing ones for type safety.
**Impact:** Unnecessary allocations in tight collision loop.
**Recommendation:** Accept duck-typed vectors or use type hints.
**Effort:** Simple

### MINOR: Sorted Enemies Multiple Times
**ID:** PERF-10
**Location:** `game/ai/target_evaluator.py:97-140`
**Issue:** Distance calculations repeated for same targets across rules.
**Impact:** Multiple distance.length() calls per target.
**Recommendation:** Pre-calculate sorted distances once.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **PERF-01: Nested Component Iteration** - Hot path inefficiency affecting every tick

2. **PERF-02: Projectile List Reconstruction** - Memory churn every tick

3. **PERF-03: O(nÂ²) Targeting Evaluation** - Scales poorly with fleet size

4. **PERF-06: Spatial Grid Rebuild** - Could use incremental updates

5. **PERF-04: Repeated Deep Copies** - Expensive initialization pattern

---


## File: test_coverage_report.md

# Test Coverage Analysis Report

## Summary
- **Total issues found:** 12
- **Critical:** 2
- **Major:** 5
- **Minor:** 4
- **Info:** 1

---

## Overall Assessment
- **Production Code:** 237 files, ~62,724 LOC
- **Test Code:** 411 files, ~99,262 LOC
- **Test-to-Code Ratio:** 1.58x
- **Test Functions:** 4,733+
- **Rating:** Good overall with critical gaps in complex UI and edge cases

---

## Findings

### CRITICAL: Untested race_setup_screen.py (1,231 LOC)
**ID:** TC-01
**Location:** `game/ui/screens/race_setup_screen.py`
**Issue:** No dedicated unit test file exists despite 1,231 lines of complex initialization logic
**Impact:** Race selection is the first major gameplay decision affecting entire run
**Recommendation:** Create comprehensive test suite for:
- Race configuration loading and validation
- Environment compatibility calculations
- Stat initialization and caching
- UI state management
**Effort:** Complex

### CRITICAL: Missing Error Path Tests in BattleController
**ID:** TC-02
**Location:** `game/simulation/battle_controller.py:183-193`
**Issue:** Critical error paths not covered:
- `add_ships_from_state()` exception handling
- Multiple `raise RuntimeError/ValueError` statements lack tests
- Retreat state transitions with edge conditions
**Impact:** Battle failures can occur with unhelpful error messages
**Recommendation:** Extend tests to cover all 7 identified error paths
**Effort:** Medium

### MAJOR: Weak Test Assertions Across 100+ Tests
**ID:** TC-03
**Location:** Throughout unit tests
**Issue:** Generic assertions without context messages:
```python
assert result.success == True  # Doesn't explain failure
assert len(ships) == 2  # No context
```
**Impact:** Test failures are cryptic and hard to debug
**Recommendation:** Add context to assertions:
```python
assert result.success is True, f"Expected success but got: {result.errors}"
```
**Effort:** Medium

### MAJOR: Untested fleet_report_window (1,034 LOC)
**ID:** TC-04
**Location:** `game/ui/screens/fleet_report_window.py`
**Issue:** No test file found for this complex widget
**Impact:** Fleet overview is critical for strategy gameplay; sorting/filtering untested
**Recommendation:** Create comprehensive test suite for fleet operations
**Effort:** Complex

### MAJOR: Untested workshop_screen Integration (949 LOC)
**ID:** TC-05
**Location:** `game/ui/screens/workshop_screen.py`
**Issue:** No integration tests for ship design workflow
**Missing Tests:**
- Component placement validation
- Real-time stat recalculation
- Design save/load cycle
- Modifier interaction edge cases
**Impact:** Ship design is core to strategy layer
**Effort:** Complex

### MAJOR: Test Isolation with GameRegistries
**ID:** TC-06
**Location:** Multiple integration tests
**Issue:** Integration tests don't properly isolate singleton state
**Impact:** Tests fail non-deterministically when run in different orders
**Recommendation:** Create fixture with autouse cleanup
**Effort:** Medium

### MAJOR: Edge Case Coverage in Battle System
**ID:** TC-07
**Location:** Battle simulation tests
**Issue:** Missing edge case tests:
- Battle with 0 ships on one team
- Simultaneous ship destruction
- Projectile targeting destroyed ships
- Weapon cooldown edge cases
**Impact:** Rare conditions can cause unhandled exceptions
**Effort:** Medium

### MINOR: Missing Save/Load Workflow Tests
**ID:** TC-08
**Location:** `tests/test_save_load.py`
**Issue:** Only tests basic round-trip. Missing:
- Save with partial damage
- Load and verify fleet state integrity
- Corrupted save file recovery
**Impact:** Mid-game state can be lost or corrupted
**Effort:** Medium

### MINOR: Research System Integration Gaps
**ID:** TC-09
**Location:** Research system tests
**Issue:** Missing:
- Tech tree unlock cascades
- Research prerequisites becoming unavailable
- Tech conflicts with active production
**Impact:** Research mechanics can fail silently
**Effort:** Medium

---

## Coverage by Module

| Module | Files | Test Files | Assessment | Gap |
|--------|-------|------------|------------|-----|
| Simulation | 45 | 22 | Good, missing edge cases | 15-20% |
| Strategy | 50 | 25 | Good, integration gaps | 10-15% |
| UI/Screens | 55 | 15 | **POOR** | 40-50% |
| AI | 6 | 9 | Excellent | <5% |
| Core | 13 | 12 | Excellent | <5% |
| Builder | 8 | 14 | Good | 10% |

---

## Top 5 Priority Issues

1. **TC-01: Create race_setup_screen test suite** - Blocks playability testing

2. **TC-02: Add BattleController error path coverage** - Prevents crashes

3. **TC-03: Enhance assertion context messages** - Improves debuggability

4. **TC-04/05: Test major UI screens** - Core gameplay coverage

5. **TC-06: Fix test isolation with registries** - Prevents flakiness

---

