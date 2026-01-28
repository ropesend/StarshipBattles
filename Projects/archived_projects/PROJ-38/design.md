# PROJ-38: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Problem Statement
The `RegistryManager` singleton in `game/core/registry.py` creates global state accessible from anywhere. Classes like `ShipDesignUtils`, `Component`, and `Ship` pull from `RegistryManager.instance()` implicitly, hiding their true dependencies.

**Impact:**
- Unit testing requires complex `setUp/tearDown` logic (`reset()`, `hydrate()`) to avoid pollution between tests
- Parallel test execution (`pytest-xdist`) requires `SessionRegistryCache` workarounds
- Difficult to reason about which classes depend on which registries
- Module-level references (`COMPONENT_REGISTRY`, `VEHICLE_CLASSES`) create hidden dependencies at import time

### Current State Analysis

**Registry Consumers (19 files identified):**

| Category | Files | Access Pattern |
|----------|-------|----------------|
| Module-level refs | `component.py`, `ship.py` | `COMPONENT_REGISTRY = get_component_registry()` at module load |
| Heavy services | `ship_stats_service.py`, `modifier_service.py` | Multiple `get_*()` calls in methods |
| Design services | `vehicle_design_service.py` | Instance methods calling `get_*()` |
| Serialization | `ship_serialization.py`, `battle_state.py` | `get_*()` during deserialization |
| UI layer | `workshop_screen.py`, `workshop_viewmodel.py`, `builder_widgets.py` | Various `get_*()` calls |
| Loaders | `ship_loader.py`, `resources.py` | Populate registries + `set_validator()` |

**Composition Root:** `Game.__init__()` in `app.py` (lines 68-131) is where all registries are populated and scenes created.

## Swarm Findings Summary

### Architecture

**Good Pattern Already Exists:**
`ShipStatsCalculator` at `game/simulation/entities/ship_stats.py:64` demonstrates proper DI:
```python
class ShipStatsCalculator:
    def __init__(self, vehicle_classes):
        self.vehicle_classes = vehicle_classes
```

**Initialization Order:**
1. `pygame.init()`
2. `load_components()` -> populates `RegistryManager.instance().components`
3. `load_modifiers()` -> populates `RegistryManager.instance().modifiers`
4. `load_resources()` -> populates `RegistryManager.instance().resources`
5. `initialize_ship_data()` -> populates `RegistryManager.instance().vehicle_classes`
6. `freeze_registry()` -> locks registries
7. Scene creation (passes registries implicitly via globals)

### Key Patterns to Reuse
- **ShipStatsCalculator DI**: `game/simulation/entities/ship_stats.py:64` - constructor injection of `vehicle_classes`
- **TurnEngine DI**: Already accepts `battle_resolver` via constructor - extend pattern
- **WorkshopContext**: Already acts as a context object - can carry registries

### Dependencies & Risks
1. **Module-level references execute at import time** - Must ensure registries are set before any module imports `component.py` or `ship.py`. Mitigation: Transitional fallback pattern with `get_default_registries()`.

2. **Circular imports** - Adding registries parameter might create cycles. Mitigation: Use `TYPE_CHECKING` imports for type hints, lazy imports inside methods.

3. **Deep call chains** - Some components are created deep in call stacks (e.g., `Ship` -> `Component` -> `Modifier`). Mitigation: Pass registries object through chain.

4. **Test fixture changes** - Tests rely on `reset_singletons()` fixture. Mitigation: Keep old fixture during transition, add new DI fixtures in parallel.

### Opportunities Discovered
- Can eliminate `SessionRegistryCache` workaround after DI migration
- Can simplify test setup significantly
- `GameRegistries` container enables easier mocking in tests
- Frozen dataclass prevents accidental mutation (replaces `freeze_registry()`)

## Design Decisions

### Decision 1: Single Container vs Individual Registries
**Choice:** Single `GameRegistries` frozen dataclass

**Rationale:**
- Reduces parameter count in constructors (1 vs 4-5)
- Easier to pass through deep call chains
- Natural grouping of related data
- Allows future registry additions without signature changes
- Frozen dataclass prevents accidental mutation

```python
@dataclass(frozen=True)
class GameRegistries:
    components: Dict[str, Any]
    modifiers: Dict[str, Any]
    vehicle_classes: Dict[str, Any]
    resources: Dict[str, Any]
```

### Decision 2: Loading Functions
**Choice:** Convert to pure functions that return data

**Rationale:**
- Pure functions are easier to test
- No side effects = predictable behavior
- Existing functions become thin wrappers for backward compatibility

```python
# New (pure)
def load_components_data(filepath) -> Dict[str, Component]:
    ...
    return component_dict

# Old (wrapper for compatibility)
def load_components(filepath):
    data = load_components_data(filepath)
    RegistryManager.instance().components.update(data)
```

### Decision 3: Transitional Fallback Pattern
**Choice:** `get_default_registries()` function during migration

**Rationale:**
- Allows incremental migration without breaking everything at once
- Classes can use `registries or get_default_registries()` pattern
- Removed in final cleanup phase

```python
_default_registries: Optional[GameRegistries] = None

def set_default_registries(registries: GameRegistries) -> None:
    global _default_registries
    _default_registries = registries

def get_default_registries() -> GameRegistries:
    if _default_registries is None:
        raise RuntimeError("Default registries not initialized")
    return _default_registries
```

### Decision 4: Constructor Signature Pattern
**Choice:** Optional registries parameter with fallback

**Pattern:**
```python
class Ship:
    def __init__(self, ..., registries: Optional[GameRegistries] = None):
        self._registries = registries or get_default_registries()
```

**Rationale:**
- Backward compatible during migration
- Explicit DI when provided
- Final phase removes Optional and fallback

See [decisions.md](decisions.md) for the full log with rationale.
