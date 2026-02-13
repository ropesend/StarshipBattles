# PROJ-108: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Deep-dive of 40 duplication findings from the 2026-02-10 full-codebase sweep. After examining
source code for all CRITICAL and MAJOR findings, the actual singleton count is **8** (not 5),
and several findings overlap significantly (DUP-STR-001/002/003/006 share root cause).

### Key Discovery: 8 Singleton Classes

All use identical double-checked locking pattern:

| Class | File | Exception Type | Has reset() | Has clear() |
|-------|------|---------------|-------------|-------------|
| Logger | `game/core/logger.py:9-34` | (uses __new__) | Yes (lock) | No |
| RegistryManager | `game/core/registry.py:123-210` | StateException | Yes (no lock) | Yes |
| Profiler | `game/core/profiling.py:14-68` | RuntimeError | Yes (lock) | Yes |
| ScreenshotManager | `game/core/screenshot_manager.py:10-58` | RuntimeError | Yes (lock) | No |
| StrategyManager | `game/ai/strategy_manager.py:19-98` | StateException | Yes (lock) | Yes |
| AssetManager | `game/assets/asset_manager.py:10-64` | StateException | Yes (lock) | Yes |
| SpriteManager | `game/ui/renderer/sprites.py:6-56` | Exception | Yes (lock) | No |
| ShipThemeManager | `game/ui/assets/ship_theme_manager.py:10-78` | StateException | Yes (lock) | Yes |
| ComponentCacheManager | `game/simulation/components/component.py:427-464` | (no guard) | Yes (lock, reset data) | No |

**Logger is special**: Uses `__new__` instead of `instance()` classmethod. All others use `cls.instance()`.

### Key Discovery: Strategy Validation Overlap

DUP-STR-001, DUP-STR-002, DUP-STR-003, and DUP-STR-006 all share the same root cause:
no shared utility for iterating design_data layers and checking component abilities.
The same `for ship -> for layer -> for comp -> check ability` nested loop appears in:
- `ColonizeValidator._get_component_abilities()` (lines 14-37)
- `SuperweaponValidator._get_component_abilities()` (lines 13-36) -- **IDENTICAL**
- `SuperweaponValidator.find_ship_with_ability()` (lines 38-70)
- `ColonizeValidator.find_ship_with_colony_pod()` (lines 124-167)
- `ColonizeValidator.get_available_colony_pods()` (lines 169-212)
- `FleetCapabilityCalculator.ship_has_spaceyard()` (lines 24-45)
- `FleetCapabilityCalculator.space_shipyard_count` (lines 67-81)
- `FleetCapabilityCalculator._ship_has_ability()` (lines 181-202)

All these can be consolidated with a single `iterate_design_components()` utility
and a `find_ship_with_ability()` that takes the ability name as parameter.

### Key Discovery: UI Service Lazy Init Is Already Clean

DUP-UI2-001 reports duplication in 4 UI services, but examination shows:
- `ComponentService.__init__` + `_get_provider()` = 6 lines each
- `ValidationService.__init__` + `_get_validator()` = 6 lines each
- `VehicleClassService` already has strict DI (no lazy init)
- `ShipFactory._get_registries()` uses 3-tier resolution (explicit > stored > global)

The "duplication" is really just the lazy-init pattern (~6 lines per class). A base class
would add complexity for minimal gain. **Recommendation: SKIP this finding.**

## Architecture

### Phase Dependencies

```
Phase 1: SingletonMeta metaclass (foundation utility)
   |
   +-- Phase 2: Uses SingletonMeta (all 8 singleton classes)
   |
Phase 3: Component iteration utilities (strategy layer)
   |
   +-- Phase 4: Uses iteration utilities (validators, calculators)
   |
Phase 5: Simulation deduplication (ability aggregator, modifier schema)
   |
Phase 6: UI deduplication (value formatting, galleries, column managers)
```

### Design Patterns

#### 1. SingletonMeta Metaclass (Phase 1)

```python
# game/core/singleton.py
class SingletonMeta(type):
    """Thread-safe singleton metaclass with double-checked locking.

    Usage:
        class MyManager(metaclass=SingletonMeta):
            def __init__(self):
                self.data = {}

            def clear(self):
                self.data = {}

    Access: MyManager.instance()
    Reset:  MyManager.reset()  # Testing only
    """
    _instances = {}
    _locks = {}

    def __init_subclass__(cls, **kwargs): ...
    def instance(cls): ...
    def reset(cls): ...
```

**Key design decisions:**
- Metaclass (not base class) to avoid MRO issues with existing class hierarchies
- Each class gets its own lock (stored in `_locks` dict keyed by class)
- `instance()` uses double-checked locking (preserves existing pattern)
- `reset()` acquires lock and sets instance to None (testing only)
- **Logger special case**: Logger uses `__new__` pattern and has 109 lines of unrelated
  code. Converting it would require changing all module-level accessor calls.
  **Decision: Skip Logger conversion; convert the other 7.**

#### 2. Design Component Iterator (Phase 3)

```python
# game/strategy/services/component_inspector.py
class ComponentInspector:
    """Utility for inspecting ship design_data for component abilities."""

    @staticmethod
    def get_component_abilities(comp_def) -> Dict[str, Any]:
        """Extract abilities from a component definition (dict or Component)."""

    @staticmethod
    def iterate_design_components(design_data, component_registry):
        """Yield (comp_entry, comp_def, abilities) for each component in design."""

    @staticmethod
    def ship_has_ability(ship, ability_name, component_registry) -> bool:
        """Check if ship design has a component with given ability."""

    @staticmethod
    def find_ship_with_ability(fleet_ships, ability_name, component_registry):
        """Find first ship in list with given ability. Returns ship or None."""

    @staticmethod
    def count_ability(ship, ability_name, component_registry) -> int:
        """Count components with given ability in ship design."""
```

This replaces:
- `ColonizeValidator._get_component_abilities()` (delete)
- `SuperweaponValidator._get_component_abilities()` (delete)
- `SuperweaponValidator.find_ship_with_ability()` (delegate)
- `ColonizeValidator.find_ship_with_colony_pod()` (delegate, with filter)
- `FleetCapabilityCalculator.ship_has_spaceyard()` (delegate)
- `FleetCapabilityCalculator._ship_has_ability()` (delegate)
- `FleetCapabilityCalculator.space_shipyard_count` (delegate)

#### 3. Ability Aggregator Consolidation (Phase 5)

Merge `calculate_ability_totals()` and `calculate_ability_totals_for_layer()` into
a single function with optional parameters:

```python
def calculate_ability_totals(
    components,
    layer: Optional[AbilityLayer] = None,
    scope_filter: Optional[AbilityScope] = None
) -> Dict[str, Any]:
```

When `layer is None`, processes all abilities (current behavior).
When `layer` is provided, filters by `ab.applies_to_layer(layer)`.
When `scope_filter` is provided, filters by `ab.scope == scope_filter`.

The `_for_layer` variant skips raw dict processing (no layer info in dicts).
This is preserved by skipping the dict fallback when `layer is not None`.

#### 4. Gallery Base Class (Phase 6)

```python
# game/ui/panels/base_gallery.py
class BaseGallery:
    """Base class for asset selection galleries (portraits, flags, themes)."""

    def __init__(self, panel, manager, race_config, x, y, width, height,
                 on_select_callback, asset_loader): ...

    # Template methods (override in subclasses)
    def _get_asset_key(self) -> str: ...          # 'portrait_id', 'flag_id'
    def _discover_assets(self) -> List[...]: ...   # Discovery logic
    def _create_preview(self, asset_id): ...       # Preview rendering

    # Shared logic (same across galleries)
    def _create_content(self): ...
    def _create_gallery_buttons(self): ...
    def handle_event(self, event): ...
    def _handle_selection(self, asset_id): ...
```

### Findings Triage

#### Include (CRITICAL + MAJOR with clear ROI)

| ID | Severity | Phase | Lines Saved | Risk |
|----|----------|-------|-------------|------|
| DUP-FND-001 | CRITICAL | 1-2 | ~175 | Low |
| DUP-SIM-001 | CRITICAL | 5 | ~60 | Medium |
| DUP-SIM-003 | CRITICAL | 5 | ~50 | Medium |
| DUP-STR-001 | CRITICAL | 3-4 | ~90 | Low |
| DUP-STR-002 | CRITICAL | 3-4 | (overlap with STR-001) | Low |
| DUP-UI1-001 | CRITICAL | 6 | ~100 | High |
| DUP-UI1-002 | CRITICAL | 6 | ~30 | Low |
| DUP-UI1-003 | CRITICAL | 6 | ~12 | Low |
| DUP-FND-002 | MAJOR | 4 | ~30 | Low |
| DUP-FND-004 | MAJOR | 4 | ~15 | Low |
| DUP-SIM-002 | CRITICAL | 5 | ~20 | Low |
| DUP-SIM-005 | MAJOR | 5 | ~20 | Low |
| DUP-STR-003 | MAJOR | 3-4 | (overlap with STR-001) | Low |
| DUP-STR-006 | MAJOR | 3-4 | (overlap with STR-001) | Low |
| DUP-UI1-005 | MAJOR | 6 | ~110 | Medium |
| DUP-UI2-004 | MAJOR | 2 | ~50 | Low |

#### Defer / Skip

| ID | Severity | Reason |
|----|----------|--------|
| DUP-FND-003 | MAJOR | JSON loading: 15 files, low ROI per file, high blast radius |
| DUP-FND-005 | MINOR | ValidationResult: cosmetic, low value |
| DUP-FND-006 | MINOR | Distance calc: simple math, low ROI |
| DUP-SIM-004 | MAJOR | Ability retrieval: Complex, touches test infrastructure |
| DUP-SIM-006 | MAJOR | Ability value extraction: 3 different aggregation semantics are intentional |
| DUP-SIM-007 | MAJOR | Serialization verification: test coverage issue, not code dup |
| DUP-SIM-008-010 | MINOR | Low ROI |
| DUP-STR-004 | MAJOR | Pod counting: only 2 methods in same file, low ROI |
| DUP-STR-005 | MAJOR | Resource consumption: atomic patterns intentionally similar for clarity |
| DUP-STR-007-009 | MINOR | Low ROI |
| DUP-UI2-001 | CRITICAL | UI Service init: only ~6 lines per class, base class adds complexity |
| DUP-UI2-002 | MAJOR | Cache pattern: internal to ShipThemeManager, refactor during god-class work |
| DUP-UI2-003 | MAJOR | Placeholder images: only 2-3 lines each, low ROI |
| DUP-UI2-005 | MINOR | Scale utilities: grouped but intentionally different |
| DUP-UI1-004 | MAJOR | Format functions: already delegating in strategy_ui.py |
| DUP-UI1-006-010 | MAJOR/MINOR | Low ROI or internal to single files |
| DUP-UI1-007 | MAJOR | Filter manager: different enough that base class adds complexity |
| DUP-UI1-008 | MAJOR | Build queue: already consolidated via format_empire_resources delegation |

### Dependencies & Risks

1. **SingletonMeta must come first** - All other singletons depend on it. If metaclass
   has any subtle behavior differences, it cascades everywhere.
   Mitigation: Exhaustive test coverage of SingletonMeta before conversion.

2. **RegistryManager is special** - Has `__init__` guard, freeze/hydrate/clear, and is
   the most complex singleton. Convert this one last in Phase 2.
   Mitigation: Convert simpler singletons first to validate pattern.

3. **ComponentInspector must not break validators** - Strategy validation tests are
   critical for game correctness.
   Mitigation: Run full test suite after each validator update.

4. **Ability aggregator refactor changes function signature** - Callers of
   `calculate_ability_totals_for_layer()` must be updated.
   Mitigation: Keep old function as a thin wrapper during migration, then delete.

5. **ColumnManager name collision** - Both `column_manager.py` and `planet_list_columns.py`
   export a class named `ColumnManager`. After extraction, one must be renamed.
   Mitigation: Rename planet_list_columns.py's class to `PlanetColumnManager`.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
