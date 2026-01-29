# PROJ-46: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Test Baseline
- **5199 passed, 3 skipped** (established 2026-01-28)
- 1 collection error in test_ship_factory.py (pre-existing, passes in isolation)

### Scope Determination
User confirmed:
1. Address ALL 30+ issues from findings_05_naming_consistency.md
2. Consolidate `ui/` into `game/ui/` (full merge)
3. Use "Screen" naming convention for UI classes

---

## Swarm Findings Summary

### 1. Duplicate Validator Analysis (NCA-001)

**Canonical Version:** `game/simulation/ship_validator.py`
- Phase 12 refactored with template method pattern
- Uses `game.simulation.validation.base` module
- 9+ test files specifically test this version
- Includes PROJ-38 DI enhancements
- Has HullOnly restriction fix (BUG-12)

**Legacy Version:** `game/simulation/systems/validator.py`
- Older monolithic implementation
- Duplicates guard clause logic across rules
- Only 3 importers remain:
  - `game/ui/screens/builder/left_panel.py:258`
  - `tests/unit/systems/test_mount_validation.py:9`
  - `tests/unit/builder/test_builder_validation.py:263`

**Decision:** Delete legacy, consolidate to canonical.

---

### 2. Parameter Naming Analysis (NCA-002)

**Current State:** 127 occurrences of `filepath` (no underscore)
**Target:** Standardize to `file_path` (snake_case, PEP 8 compliant)

**Files by Priority:**

| Priority | File | Functions Affected |
|----------|------|-------------------|
| Critical | `game/core/json_utils.py` | `load_json()`, `load_json_required()`, `save_json()` |
| Critical | `game/core/resources.py` | `_resolve_resource_path()`, `load_resources_data()`, `load_resources()` |
| High | `game/simulation/components/component.py` | 4 loader functions |
| High | `game/simulation/entities/ship_loader.py` | `load_vehicle_classes()` |
| Medium | `game/research/data/tech_tree.py` | `load_from_json()` |
| Medium | `game/strategy/data/design_metadata.py` | `from_design_file()` |
| Medium | `game/strategy/data/race_config.py` | `save()`, `load()` |
| Medium | `game/ui/screens/setup_data_io.py` | `save_battle_setup()`, `load_battle_setup()` |

---

### 3. Service/Engine/Manager Naming Analysis (NCA-006, SIM-004, STR-003)

**Established Patterns:**
- **Service**: Business logic, abstraction layers (BattleService, ModifierService)
- **Engine**: State machines, simulation loops (BattleEngine, TurnEngine)
- **Manager**: Collection/lifecycle management (BattleStateManager, RetreatManager)
- **Controller**: Orchestration, input handling (BattleController, AIController)

**Violations Found:**
| Current Name | Should Be | Reason |
|--------------|-----------|--------|
| `FleetMobilityService` | `FleetSpeedCalculator` | Only calculates speed, not full mobility |
| `ShipStatsService` | `ShipStatsCalculator` | Pure calculation, not service behavior |

---

### 4. Method Prefix Analysis (NCA-003, NCA-004)

**get_* Methods Doing I/O (Violations):**
| Method | File | Should Be |
|--------|------|-----------|
| `get_image()` | `game/assets/asset_manager.py:84` | `load_image()` |
| `get_group()` | `game/assets/asset_manager.py:106` | `load_group()` |

**calculate_* vs recalculate_* Convention:**
- `calculate_*`: Pure computation, returns new value
- `recalculate_*`: Mutates self in-place
- `update_*`: Alternative for mutation (proposed for `recalculate_fleet_speed()`)

---

### 5. Boolean Prefix Analysis (NCA-010)

**Violations Found:**
| Current | Should Be | File | Line |
|---------|-----------|------|------|
| `check()` | `has_sufficient()` | `game/simulation/systems/resource_manager.py` | 83 |
| `design_exists()` | `has_design()` | `game/strategy/systems/design_library.py` | 387 |
| `_at_map_edge()` | `_is_at_map_edge()` | `game/simulation/battle_controller.py` | 431 |

**Established Conventions:**
- `is_*`: State queries (is_alive, is_operational)
- `has_*`: Possession checks (has_components, has_fuel)
- `can_*`: Capability checks (can_fire, can_move)

---

### 6. UI Directory Structure (NS-01)

**Current State:**
```
ui/                          # 18 Python files
├── __init__.py
├── test_lab_scene.py        # 11 classes, 4096 lines
├── battle_state_viewer.py   # 3 classes, 687 lines
└── builder/                 # 14 files

game/ui/                     # Primary UI location
├── screens/
│   ├── builder/            # Some duplicates with ui/builder/
│   ├── strategy_scene.py
│   └── battle_scene.py
├── panels/
├── hud/
└── services/
```

**Dependency Analysis:**
- `game/ui/` imports FROM `ui/`: 12 files
- `ui/` imports FROM `game/ui/`: 0 files (no reverse dependency)
- **Safe to consolidate** - one-way dependency

---

### 7. UI Class Naming Analysis (UI-006)

**Current Mixed Naming:**
| Pattern | Count | Examples |
|---------|-------|----------|
| Scene | 4 | BattleScene, StrategyScene, FormationEditorScene, TestLabScene |
| Screen | 6 | NewGameSetupScreen, RaceSetupScreen, BattleSetupScreen |
| Interface | 2 | BattleInterface, StrategyInterface |
| GUI | 2 | BuilderSceneGUI, DesignWorkshopGUI |

**Decision:** Standardize to "Screen" (most common, pygame_gui convention)

---

### 8. Type Hint Analysis (CORE-007)

**Current State:**
- 113 uses of `Optional[str]` (typing module style)
- 1 use of `str | None` (PEP 604 style) in `game/core/resources.py:22`

**Decision:** Standardize on `Optional[str]` (99% prevalence)

---

## Architecture

### Key Patterns to Preserve

**Validation Module Pattern:**
```python
# game/simulation/validation/base.py
class ValidationRule(ABC):
    def validate() -> ValidationResult      # Template method
    def _should_validate() -> bool          # Guard clause hook
    def _do_validate() -> ValidationResult  # Abstract implementation

class AdditionValidationRule(ValidationRule):  # For component addition
class DesignValidationRule(ValidationRule):    # For full design validation
```

**Registry Access Pattern:**
```python
# Preferred: Dependency Injection
def __init__(self, *, registries: Optional['GameRegistries'] = None):
    self._registries = registries or get_default_registries()

# Legacy (deprecated): Global getters
from game.core.registry import get_component_registry  # Shows deprecation warning
```

**Service/Calculator Pattern:**
```python
# Calculator: Pure functions, no state mutation
class ShipStatsCalculator:
    @staticmethod
    def calculate_stats(design_data: Dict) -> Stats:
        ...  # Returns new Stats object

# Service: Business logic, may have state
class BattleService:
    def start_battle(self, config: BattleConfig) -> Battle:
        ...  # Manages lifecycle
```

---

## Dependencies & Risks

### Test Impact Matrix

| Change | Test Files | Test Methods | Risk |
|--------|------------|--------------|------|
| Validator consolidation | 5 | 8-15 | LOW |
| UI directory consolidation | 31 | ~200 | HIGH |
| FleetMobilityService rename | 2 | 18 | MEDIUM |
| ShipStatsService rename | 2 | 77 | HIGH |
| filepath standardization | 15 | ~50 | MEDIUM |

**Total Impact:** ~45 test files, ~330 test methods

### Risk Mitigation Strategy

1. **Commit after each sub-phase** - Easy rollback
2. **Run tests continuously** - Catch breaks early
3. **Use IDE refactoring** - Reduce manual errors
4. **Process in dependency order** - Bottom-up through import graph

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
