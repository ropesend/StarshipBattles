# ABS-LOAD: Loader & Serialization Abstraction Design Report

## Summary
- **Total issues found:** 8
- **Critical:** 2, **Major:** 4, **Minor:** 1, **Info:** 1
- **Scope:** Cluster 7 (JSON Loader Template) and Cluster 8 (DTO to_dict/from_dict Conversion)
- **Prior art incorporated:** DRY-CORE CQ-002, DRY-CROSS XL-006, DRY-STRAT-SYS CQ-006

---

## Part 1: Cluster 7 — JSON Loader Template (PC-015)

### Comprehensive Loader Inventory

The codebase contains **10 dedicated loader classes** and **8 standalone loader functions** that read JSON from disk, validate, and transform. Here is the complete inventory:

#### Dedicated Loader Classes

| # | Class | File | Lines | Pattern |
|---|-------|------|-------|---------|
| 1 | `SystemBlueprintsLoader` | `game/strategy/generation/loaders/system_blueprints_loader.py` | 174 | Instance, `load_json_required` -> validate -> return dict |
| 2 | `AstrophysicsLoader` | `game/strategy/generation/loaders/astrophysics_loader.py` | 150 | Instance, `load_json_required` -> validate -> return dict |
| 3 | `GalaxyLayoutsLoader` | `game/strategy/generation/loaders/galaxy_layouts_loader.py` | 173 | Static, `load_json_required` -> validate key -> return dict |
| 4 | `TechPresetLoader` | `game/simulation/systems/tech_preset_loader.py` | 203 | Static, `load_json_required` -> return dict (no schema validation) |
| 5 | `SimulationDesignLoader` | `game/simulation/services/design_loader.py` | 129 | Instance (registries), `load_json_required` -> `Ship.from_dict()` -> return Ship |
| 6 | `DesignLoaderAdapter` | `game/ui/services/design_loader_adapter.py` | 87 | Thin facade over `SimulationDesignLoader` (pure delegation) |
| 7 | `WorkshopDataLoader` | `game/ui/screens/workshop_data_loader.py` | 217 | Orchestrator, multiple `load_json_required` calls, registries |
| 8 | `WorkshopDataReloader` | `game/ui/screens/workshop_data_reloader.py` | 193 | UI orchestrator, delegates to `WorkshopDataLoader` |
| 9 | `RaceAssetLoader` | `game/ui/screens/race_asset_loader.py` | 277 | Image/asset loader (not JSON), uses `pygame.image.load` |
| 10 | `BuildQueuePortraitLoader` | `game/ui/panels/build_queue_portraits.py` | 217 | Image/asset loader (not JSON), uses `pygame.image.load` |

#### Standalone JSON Loader Functions

| # | Function | File | Lines | Pattern |
|---|----------|------|-------|---------|
| 1 | `load_components_data()` | `game/simulation/components/component.py:475` | ~72 | `load_json_required` -> iterate array -> create objects -> return dict |
| 2 | `load_components()` | `game/simulation/components/component.py:550` | ~38 | Cache check -> `load_components_data()` -> populate registry |
| 3 | `load_modifiers_data()` | `game/simulation/components/component.py:589` | ~58 | `load_json_required` -> iterate array -> create Modifier objects -> return dict |
| 4 | `load_modifiers()` | `game/simulation/components/component.py:649` | ~18 | Cache check -> `load_modifiers_data()` -> populate registry |
| 5 | `load_vehicle_classes_data()` | `game/simulation/entities/ship_loader.py:37` | ~60 | `load_json_required` -> post-process layer refs -> return dict |
| 6 | `load_vehicle_classes()` | `game/simulation/entities/ship_loader.py:100` | ~28 | `load_vehicle_classes_data()` -> populate registry |
| 7 | `load_stats_config()` | `game/ui/screens/builder/stats_config.py:288` | ~50 | Raw `open`/`json.load` -> validate groups key -> transform with resolver |
| 8 | `TechTree.load_from_json()` | `game/research/data/tech_tree.py:29` | ~64 | `load_json` -> iterate array -> create TechNode objects -> return TechTree |

#### Other JSON Loading Call Sites (not dedicated loaders, but use `load_json`/`load_json_required`)

These are inline usages scattered across files:
- `game/ai/strategy_manager.py:91-100` (3 calls in `load_data()`)
- `game/ui/services/input_mapper.py:114` (1 call in `_load_bindings_from_file`)
- `game/strategy/systems/save_game_service.py:138,175,297,398` (4 calls)
- `game/strategy/systems/design_library.py:150,215,244,284` (4 calls)
- `game/strategy/data/race_config.py:276` (1 call in `load()`)
- `game/core/profiling.py:88` (1 call)
- `game/core/resources.py:75` (1 call)
- `game/assets/asset_manager.py:46` (1 call)
- `game/strategy/quickstart_builder.py:73` (1 call)
- `game/strategy/generation/planet_image_registry.py:43` (1 call)
- `game/ui/screens/setup_data_io.py:42,71,103,196` (4 calls)
- `game/ui/screens/setup_screen.py:145` (1 call)
- `game/ui/screens/formation_editor.py:207` (1 call, raw `open`/`json.load`)
- `game/ui/screens/builder/stats_config.py:299` (1 call, raw `open`/`json.load`)
- `game/ui/assets/ship_theme_manager.py:82` (1 call)
- `game/strategy/data/homeworld_presets.py:40` (1 call)
- `game/strategy/data/build_queue_source.py:34` (1 call)
- `game/ui/screens/planet_list_presets.py:22` (1 call)
- `game/ui/screens/test_lab/data_extractor.py:100,127,152,201` (4 calls)
- `game/ui/screens/test_lab/screen.py:1878,1894` (2 calls)

### Loader Commonality Analysis

#### The Three Strategy Generation Loaders (Strongest Template Fit)

These three loaders are nearly identical in structure:

| Step | SystemBlueprintsLoader | AstrophysicsLoader | GalaxyLayoutsLoader |
|------|----------------------|---------------------|---------------------|
| **File path** | `data/system_blueprints.json` | `data/astrophysics.json` | `data/galaxy_layouts.json` |
| **Default path** | Class attr `DEFAULT_PATH` | Class attr `DEFAULT_PATH` | Class attr `DEFAULT_PATH` |
| **Load** | `load_json_required()` | `load_json_required()` | `load_json_required()` |
| **Validate** | `_validate_schema(data)` | `_validate_schema(data)` | Check for 'layouts' key |
| **Transform** | Return raw dict | Return raw dict | Return raw dict |
| **Return type** | `Dict[str, Any]` | `Dict[str, Any]` | `Dict[str, Any]` |
| **Error handling** | Let `load_json_required` raise | Let `load_json_required` raise | Let `load_json_required` raise |
| **Init style** | Instance with optional path | Instance with optional path | Static with optional path |

These share the exact same lifecycle: set default path -> `load_json_required()` -> validate -> return dict.

#### The Data Registry Loaders (Component/Modifier/VehicleClass)

These three function-pairs share a different pattern:

| Step | `load_components_data` | `load_modifiers_data` | `load_vehicle_classes_data` |
|------|----------------------|----------------------|---------------------------|
| **Path fallback** | CWD then relative to __file__ | CWD then relative to __file__ | CWD then Paths constant |
| **Load** | `load_json_required()` | `load_json_required()` | `load_json_required()` |
| **Validate** | Implicit (catches KeyError) | `validate_modifier_v2()` | Implicit |
| **Transform** | Iterate array -> `Component()` | Iterate array -> `Modifier()` | `copy.deepcopy` + layer resolution |
| **Error collect** | Per-item try/catch -> error list | Per-item try/catch -> error list | N/A |
| **Error handling** | Log and return `{}` | Log and return `{}` | Raise RuntimeError |
| **Return type** | `Dict[str, Component]` | `Dict[str, Modifier]` | `Dict[str, dict]` |

These share: path fallback logic (17+ duplicate lines), load-iterate-create-collect-error pattern.

#### Other Loaders (Lower Template Fit)

- `SimulationDesignLoader` - Specialized: loads JSON then creates `Ship` objects via `Ship.from_dict()`. Has registries DI.
- `WorkshopDataLoader` - Orchestrator: calls multiple other loaders, not a single-file loader itself.
- `TechTree.load_from_json` - Classmethod: loads JSON -> iterates array -> creates TechNode objects.
- `StrategyManager.load_data` - Loads 3 JSON files in sequence, very simple (no validation).

---

### Findings

#### CRITICAL: Strategy Generation Loader Template Duplication
**ID:** ABS-LOAD-001
**Location:** `game/strategy/generation/loaders/system_blueprints_loader.py`, `game/strategy/generation/loaders/astrophysics_loader.py`, `game/strategy/generation/loaders/galaxy_layouts_loader.py`
**Issue:** Three loaders in the same package repeat the identical open-validate-return pattern. Each has: a `DEFAULT_PATH`, a `load()` method that calls `load_json_required` then validates, and a `_validate_schema()` method. The only difference is the specific validation rules.
**Impact:** 497 lines across 3 files where ~60% is duplicated structural code. Any new loader in this package will copy-paste yet another instance.

**Proposed API:**

```python
# game/strategy/generation/loaders/base_config_loader.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Dict, Any, Optional, Union

from game.core.json_utils import load_json_required
from game.core.logger import log_info

T = TypeVar('T')


class BaseConfigLoader(ABC, Generic[T]):
    """
    Template method base class for JSON configuration loaders.

    Subclasses implement:
    - DEFAULT_PATH: Class attribute with default file path
    - _validate(data): Schema validation (raise ValueError on failure)
    - _transform(data): Optional transformation step (default: return as-is)

    The load() method handles:
    - File path resolution (default or custom)
    - JSON parsing via load_json_required
    - Error propagation (FileNotFoundError, json.JSONDecodeError, ValueError)
    - Optional logging
    """

    DEFAULT_PATH: Union[str, Path] = ""

    def __init__(self, file_path: Optional[Union[str, Path]] = None) -> None:
        self.file_path: Union[str, Path] = file_path or self.DEFAULT_PATH

    def load(self) -> T:
        """
        Load, validate, and transform configuration from JSON file.

        Returns:
            Validated and transformed configuration data.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file isn't valid JSON.
            ValueError: If schema validation fails.
        """
        data = load_json_required(str(self.file_path))
        self._validate(data)
        return self._transform(data)

    @abstractmethod
    def _validate(self, data: Dict[str, Any]) -> None:
        """
        Validate the loaded JSON data.

        Args:
            data: Parsed JSON data.

        Raises:
            ValueError: If validation fails.
        """
        ...

    def _transform(self, data: Dict[str, Any]) -> T:
        """
        Transform validated data into the target type.

        Default implementation returns data as-is.
        Override for custom transformation.
        """
        return data  # type: ignore
```

**Before (SystemBlueprintsLoader, 47 lines for load path):**
```python
class SystemBlueprintsLoader:
    DEFAULT_PATH = Path("data/system_blueprints.json")

    def __init__(self, file_path=None):
        self.file_path = file_path or self.DEFAULT_PATH

    def load(self) -> Dict[str, Any]:
        data = load_json_required(str(self.file_path))
        self._validate_schema(data)
        return data

    def _validate_schema(self, data):
        if not isinstance(data, dict):
            raise ValueError("Blueprints data must be a dict")
        if "blueprints" not in data:
            raise ValueError("Missing 'blueprints' key")
        # ... 40 more lines of validation ...
```

**After (SystemBlueprintsLoader, ~40 lines for validation only):**
```python
class SystemBlueprintsLoader(BaseConfigLoader[Dict[str, Any]]):
    DEFAULT_PATH = Path("data/system_blueprints.json")

    def _validate(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise ValueError("Blueprints data must be a dict")
        if "blueprints" not in data:
            raise ValueError("Missing 'blueprints' key")
        # ... validation rules only ...

    # get_blueprint(), select_random_blueprint() unchanged
```

**Before (AstrophysicsLoader, same pattern):**
```python
class AstrophysicsLoader:
    DEFAULT_PATH = Path("data/astrophysics.json")

    def __init__(self, file_path=None):
        self.file_path = file_path or self.DEFAULT_PATH

    def load(self) -> Dict[str, Any]:
        data = load_json_required(str(self.file_path))
        self._validate_schema(data)
        return data

    # ... identical boilerplate ...
```

**After (AstrophysicsLoader):**
```python
class AstrophysicsLoader(BaseConfigLoader[Dict[str, Any]]):
    DEFAULT_PATH = Path("data/astrophysics.json")

    def _validate(self, data: Dict[str, Any]) -> None:
        required_sections = ["mass_distributions", "orbit_zones", ...]
        for section in required_sections:
            if section not in data:
                raise ValueError(f"Missing required section: {section}")
        # ... validation rules only ...
```

**Before (GalaxyLayoutsLoader, static but same pattern):**
```python
class GalaxyLayoutsLoader:
    DEFAULT_PATH = os.path.join("data", "galaxy_layouts.json")

    @staticmethod
    def load(file_path=None) -> Dict[str, Any]:
        if file_path is None:
            file_path = GalaxyLayoutsLoader.DEFAULT_PATH
        log_info(f"Loading galaxy layouts from: {file_path}")
        data = load_json_required(file_path)
        if 'layouts' not in data:
            raise ValueError(...)
        log_info(f"Loaded {len(data['layouts'])} ...")
        return data
```

**After (GalaxyLayoutsLoader):**
```python
class GalaxyLayoutsLoader(BaseConfigLoader[Dict[str, Any]]):
    DEFAULT_PATH = Path("data/galaxy_layouts.json")

    def _validate(self, data: Dict[str, Any]) -> None:
        if 'layouts' not in data:
            raise ValueError(f"Galaxy layouts file must contain 'layouts' key")
```

**Call Sites:**
- `game/strategy/generation/loaders/system_blueprints_loader.py` (entire file)
- `game/strategy/generation/loaders/astrophysics_loader.py` (entire file)
- `game/strategy/generation/loaders/galaxy_layouts_loader.py` (entire file)
- Future loaders in this package

**Lines Saved:** ~497 total -> ~420 target (~77 lines saved from boilerplate elimination, plus ~50 lines in new base class = net ~27 saved, but major maintainability gain)
**Risk:** Low. These loaders have well-defined interfaces. Changing from static to instance for GalaxyLayoutsLoader requires updating 1-2 call sites.
**Category:** Small Project
**Recommendation:** Create `BaseConfigLoader` in `game/strategy/generation/loaders/base_config_loader.py` (co-located with its primary consumers). Migrate the 3 strategy loaders first, then evaluate for broader adoption.
**Effort:** Simple

---

#### MAJOR: Data Registry Loader Path Resolution Duplication
**ID:** ABS-LOAD-002
**Location:** `game/simulation/components/component.py:475-547,589-646`, `game/simulation/entities/ship_loader.py:37-97`
**Issue:** Three standalone loader functions (`load_components_data`, `load_modifiers_data`, `load_vehicle_classes_data`) duplicate a 10-line path fallback pattern:
```python
if not os.path.exists(file_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(base_dir, file_path)
    if os.path.exists(abs_path):
        file_path = abs_path
    else:
        log_error(f"... file not found at {abs_path}")
        return {}
```
They also share the error collection pattern (per-item try/catch, log errors, return partial results).

**Impact:** ~30 duplicated lines across 3 functions. The path resolution logic is error-prone and inconsistent (`load_vehicle_classes_data` uses a slightly different approach with `Paths` constants).

**Proposed API:**
```python
# Addition to game/core/json_utils.py
def resolve_data_path(
    file_path: str,
    caller_file: str,
    fallback_name: str = "file"
) -> Optional[str]:
    """
    Resolve a data file path with CWD-then-relative fallback.

    Args:
        file_path: Primary path to check
        caller_file: __file__ of the calling module (for relative resolution)
        fallback_name: Human-readable name for error messages

    Returns:
        Resolved path, or None if not found.
    """
    if os.path.exists(file_path):
        return file_path
    base_dir = os.path.dirname(os.path.abspath(caller_file))
    abs_path = os.path.join(base_dir, file_path)
    if os.path.exists(abs_path):
        return abs_path
    log_error(f"{fallback_name} not found at {file_path} or {abs_path}")
    return None
```

**Before (load_components_data, 10 lines):**
```python
if not os.path.exists(file_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(base_dir, file_path)
    if os.path.exists(abs_path):
        file_path = abs_path
    else:
        log_error(f"components file not found at {abs_path}")
        return {}
```

**After (2 lines):**
```python
file_path = resolve_data_path(file_path, __file__, "components")
if file_path is None:
    return {}
```

**Call Sites:**
- `game/simulation/components/component.py:491-502` (load_components_data)
- `game/simulation/components/component.py:607-614` (load_modifiers_data)
- `game/simulation/entities/ship_loader.py:60-65` (load_vehicle_classes_data)

**Lines Saved:** ~30 total -> ~6 target = ~24 lines saved
**Risk:** Very low. Pure utility function extraction.
**Category:** Quick Win
**Recommendation:** Add `resolve_data_path()` to `game/core/json_utils.py`, update 3 call sites.
**Effort:** Simple

---

#### MAJOR: Raw json.load/open Bypassing json_utils
**ID:** ABS-LOAD-003
**Location:** `game/ui/screens/builder/stats_config.py:288-303`, `game/ui/screens/formation_editor.py:207-208`
**Issue:** Two files use raw `open()/json.load()` instead of the centralized `load_json()` or `load_json_required()` utility. This bypasses consistent error handling, encoding defaults, and logging.
**Impact:** Inconsistent error handling. `stats_config.py` has a redundant `os.path.exists` check followed by a broad except that catches `FileNotFoundError` anyway. `formation_editor.py` manually implements the same error handling that `load_json()` provides.

**Before (stats_config.py:288-303, 16 lines):**
```python
def load_stats_config():
    import json
    import os
    path = os.path.join(os.getcwd(), 'data', 'stats_layout.json')
    if not os.path.exists(path):
        print(f"Warning: {path} not found. Using empty config.")
        return {}
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, OSError, json.JSONDecodeError, ...) as e:
        log_warning(f"Error loading stats config: {e}")
        return {}
```

**After (3 lines):**
```python
def load_stats_config():
    path = os.path.join(os.getcwd(), 'data', 'stats_layout.json')
    data = load_json(path, default={})
```

**Before (formation_editor.py:205-229, 25 lines):**
```python
def load_from_file(self, filename: str) -> None:
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            if 'arrows' in data:
                # ... transform logic ...
    except FileNotFoundError:
        log_error(...)
    except json.JSONDecodeError as e:
        log_error(...)
    except (KeyError, ValueError) as e:
        log_error(...)
    except OSError as e:
        ...
```

**After (15 lines):**
```python
def load_from_file(self, filename: str) -> None:
    data = load_json(filename)
    if data is None:
        return
    if 'arrows' in data:
        # ... transform logic (unchanged) ...
```

**Call Sites:**
- `game/ui/screens/builder/stats_config.py:288-303`
- `game/ui/screens/formation_editor.py:205-229`

**Lines Saved:** ~41 total -> ~18 target = ~23 lines saved
**Risk:** Very low. Using existing utility function.
**Category:** Quick Win
**Recommendation:** Replace raw `open()/json.load()` with `load_json()` from `game.core.json_utils`.
**Effort:** Simple

---

#### MINOR: TechPresetLoader Missing Schema Validation
**ID:** ABS-LOAD-004
**Location:** `game/simulation/systems/tech_preset_loader.py:80-109`
**Issue:** `TechPresetLoader.load_preset()` calls `load_json_required()` but performs zero schema validation. If a preset file is malformed (missing `unlocked_components` key), the error only surfaces later when downstream code accesses the missing key.
**Impact:** Low immediate risk but inconsistent with other loaders in the codebase that validate eagerly. If `BaseConfigLoader` is adopted, this could easily adopt validation.
**Proposed API:** Add minimal validation:
```python
def _validate(self, data: Dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError("Tech preset must be a dict")
    # Warn on missing standard keys
    for key in ('name', 'unlocked_components', 'unlocked_modifiers'):
        if key not in data:
            log_warning(f"Tech preset missing key: {key}")
```
**Call Sites:** `game/simulation/systems/tech_preset_loader.py:102-109`
**Lines Saved:** 0 (additive change)
**Risk:** Very low
**Category:** Quick Win
**Recommendation:** Add validation after adopting BaseConfigLoader, or as standalone improvement.
**Effort:** Simple

---

## Part 2: Cluster 8 — DTO to_dict/from_dict Conversion (PC-013)

### Comprehensive Inventory

The codebase contains **29 `to_dict()` methods** and **27 `from_dict()` methods** across **18 files** and **26 classes/dataclasses**, totaling approximately **1,302 lines** of serialization code.

#### Complete to_dict/from_dict Method Inventory

| # | Class | File | DC? | to_dict | from_dict | Category |
|---|-------|------|-----|---------|-----------|----------|
| 1 | `ComponentState` | `game/simulation/battle_state.py:40` | DC | 8 lines | 10 lines | Simple field copy |
| 2 | `ShipState` | `game/simulation/battle_state.py:118` | DC | 27 lines | 28 lines | Nested (components dict) + type coercion |
| 3 | `ProjectileState` | `game/simulation/battle_state.py:344` | DC | 19 lines | 20 lines | Simple field copy + type coercion |
| 4 | `BattleState` | `game/simulation/battle_state.py:499` | DC | 14 lines | 22 lines | Nested (ships, projectiles) |
| 5 | `BattleResults` | `game/simulation/battle_state.py:658` | DC | 11 lines | 20 lines | Nested (BattleState, ShipState lists) |
| 6 | `ModifierEffect` | `game/simulation/components/modifier_effects.py:82` | DC | 12 lines | N/A (no from_dict) | Simple + computed field |
| 7 | `ShipSerializer` | `game/simulation/entities/ship_serialization.py:22` | CLS | 65 lines | 37 lines | Custom (complex component tree) |
| 8 | `Ship` (delegates) | `game/simulation/entities/ship.py:768,781` | CLS | 2 lines | 3 lines | Delegation to ShipSerializer |
| 9 | `Spectrum` | `game/strategy/data/stars.py:48` | DC | 11 lines | 13 lines | Simple field copy |
| 10 | `Star` | `game/strategy/data/stars.py:107` | DC | 12 lines | 12 lines | Nested (Spectrum) + enum + HexCoord |
| 11 | `WarpPoint` | `game/strategy/data/galaxy.py:28` | CLS | 5 lines | 5 lines | Simple + HexCoord |
| 12 | `StarSystem` | `game/strategy/data/galaxy.py:64` | CLS | 12 lines | 12 lines | Nested (stars, warp_points, planets) |
| 13 | `Galaxy` | `game/strategy/data/galaxy.py:863` | CLS | 14 lines | 35+ lines | Complex (HexCoord keys, index rebuild) |
| 14 | `Planet` | `game/strategy/data/planet.py:304` | DC | 52 lines | 60+ lines | Complex (inline facility/population ser.) |
| 15 | `FleetOrder` | `game/strategy/data/fleet.py:41` | CLS | 28 lines | N/A | Custom (polymorphic target) |
| 16 | `Fleet` | `game/strategy/data/fleet.py:322` | CLS | 20 lines | 50+ lines | Complex (orders polymorphism, path) |
| 17 | `Empire` | `game/strategy/data/empire.py:137` | CLS | 30 lines | 40 lines | Nested + optional fields + galaxy ref |
| 18 | `ShipInstance` | `game/strategy/data/ship_instance.py:608` | DC | 23 lines | 20 lines | Simple field copy + optional cargo |
| 19 | `DesignMetadata` | `game/strategy/data/design_metadata.py:40` | DC | 17 lines | 20 lines | Simple field copy |
| 20 | `RaceConfig` | `game/strategy/data/race_config.py:150` | DC | 45 lines | 45 lines | Simple field copy (35+ fields!) |
| 21 | `PlayerConfig` | `game/strategy/engine/game_config.py:74` | DC | 18 lines | 19 lines | Nested (optional RaceConfig) |
| 22 | `GameConfig` | `game/strategy/engine/game_config.py:182` | DC | 10 lines | 12 lines | Nested (list of PlayerConfig) |
| 23 | `GameSession` | `game/strategy/engine/game_session.py:249` | CLS | 10 lines | 30+ lines | Complex (two-phase load with galaxy ref) |
| 24 | `Event` | `game/strategy/events/event_log.py:29` | DC | 8 lines | 10 lines | Simple field copy |
| 25 | `EventLog` | `game/strategy/events/event_log.py:88` | CLS | 3 lines | 5 lines | Nested (list of Event) |
| 26 | `NodeState` | `game/research/data/research_tracker.py:22` | DC | 5 lines | 6 lines | Simple field copy |
| 27 | `ResearchTracker` | `game/research/data/research_tracker.py:236` | CLS | 7 lines | 9 lines | Nested (dict of NodeState) |
| 28 | `KeyBinding` | `game/core/input_actions.py:290` | DC | 5 lines | 7 lines | Simple + frozenset |
| 29 | `PathSegment` | `game/strategy/services/fleet_navigation_service.py:78` | DC | 7 lines | N/A | Simple (to_dict only) |

### Categorization

#### Category A: Pure Simple Field Copy (auto-generatable)
These classes simply copy each field to/from a dict with no transformation beyond `data.get('field', default)`:

| Class | Fields | Lines (to+from) | Could auto-generate? |
|-------|--------|-----------------|---------------------|
| `ComponentState` | 6 | 18 | YES |
| `NodeState` | 3 | 11 | YES |
| `Event` | 6 | 18 | YES |
| `DesignMetadata` | 12 | 37 | YES |
| `KeyBinding` | 2 | 12 | YES (frozenset needs hint) |
| `ShipInstance` | 13 | 43 | YES (optional cargo needs hint) |

**Total: 6 classes, ~139 lines auto-generatable**

#### Category B: Simple Field Copy + Type Coercion (semi-auto-generatable)
These classes copy fields but need `tuple(data['color'])`, `list(self.color)`, `EnumType[data['field']]`, or `HexCoord` conversion:

| Class | Coercions | Lines (to+from) |
|-------|-----------|-----------------|
| `Spectrum` | None (pure numeric) | 24 |
| `Star` | Spectrum nested, StarType enum, tuple, HexCoord | 24 |
| `WarpPoint` | HexCoord | 10 |
| `ProjectileState` | tuple coercion (2x) | 39 |
| `RaceConfig` | None (35+ fields, all simple) | 90 |
| `GameConfig` | List[PlayerConfig] nested | 22 |
| `PlayerConfig` | Optional RaceConfig nested, tuple | 37 |
| `BattleState` | Nested dict of ShipState, list of ProjectileState | 36 |

**Total: 8 classes, ~282 lines semi-auto-generatable (with type hint declarations)**

#### Category C: Nested Object Serialization
These classes serialize child objects by calling their `to_dict()`/`from_dict()`:

| Class | Nested Types | Lines (to+from) |
|-------|-------------|-----------------|
| `ShipState` | Dict[str, List[ComponentState]] | 55 |
| `BattleResults` | BattleState (optional), List[ShipState] | 31 |
| `StarSystem` | List[Star], List[WarpPoint], List[Planet] | 24 |
| `EventLog` | List[Event] | 8 |
| `ResearchTracker` | Dict[str, NodeState] | 16 |

**Total: 5 classes, ~134 lines**

#### Category D: Custom/Complex Transformation (cannot auto-generate)
These have logic beyond field mapping that cannot be auto-generated:

| Class | Why Custom? | Lines (to+from) |
|-------|------------|-----------------|
| `ShipSerializer` | Complex component tree, format versioning, stat verification | ~102 |
| `Galaxy` | HexCoord dict keys, index rebuild on load | ~50 |
| `Planet` | Inline facility/population serialization, no dedicated DTO | ~112 |
| `Fleet` | Polymorphic order targets (7 format types), path with mixed types | ~70 |
| `FleetOrder` | Polymorphic target serialization (hasattr dispatch) | ~28 |
| `Empire` | Galaxy reference resolution, two-phase load | ~70 |
| `GameSession` | Two-phase load (galaxy first, then empires) | ~40 |

**Total: 7 classes, ~472 lines (NOT auto-generatable)**

### Design Recommendation

#### Option A: `SerializableMixin` with auto-generation from dataclass fields

```python
class SerializableMixin:
    """
    Auto-generates to_dict/from_dict for @dataclass classes.

    For simple field copies, declare no overrides.
    For type coercions, declare field_serializers class attribute.
    """

    # Subclass-configurable type coercion rules
    _field_serializers: ClassVar[Dict[str, FieldSerializer]] = {}

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for field in fields(self):
            value = getattr(self, field.name)
            serializer = self._field_serializers.get(field.name)
            if serializer:
                result[field.name] = serializer.serialize(value)
            elif hasattr(value, 'to_dict'):
                result[field.name] = value.to_dict()
            elif isinstance(value, list) and value and hasattr(value[0], 'to_dict'):
                result[field.name] = [v.to_dict() for v in value]
            else:
                result[field.name] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        kwargs = {}
        for field in fields(cls):
            serializer = cls._field_serializers.get(field.name)
            if serializer:
                kwargs[field.name] = serializer.deserialize(data.get(field.name, field.default))
            else:
                kwargs[field.name] = data.get(field.name, field.default)
        return cls(**kwargs)
```

**Pros:** Declarative, eliminates boilerplate for simple cases.
**Cons:** Complex `_field_serializers` declaration for non-trivial types. Mixin inheritance conflicts possible. Harder to debug.

#### Option B: `@serializable` decorator

```python
@serializable
@dataclass
class Event:
    event_type: str
    category: str
    # ... fields auto-serialized
```

**Pros:** Clean syntax.
**Cons:** Decorator interaction with `@dataclass` is fragile. Hard to customize per-field behavior.

#### Option C: Standalone `dataclass_to_dict()` / `dataclass_from_dict()` utility functions

```python
# game/core/serialization.py

from dataclasses import fields, MISSING
from typing import Type, TypeVar, Dict, Any, get_type_hints

T = TypeVar('T')

# Type coercion registry
_COERCERS: Dict[type, Callable] = {
    tuple: lambda v: tuple(v) if isinstance(v, list) else v,
    frozenset: lambda v: frozenset(v) if isinstance(v, list) else v,
}


def dataclass_to_dict(
    obj,
    *,
    exclude: frozenset[str] = frozenset(),
    custom: Dict[str, Callable] = None,
) -> Dict[str, Any]:
    """
    Auto-serialize a @dataclass instance to a dict.

    Args:
        obj: Dataclass instance to serialize.
        exclude: Field names to skip.
        custom: Dict of field_name -> serializer_function overrides.

    Returns:
        JSON-compatible dict.
    """
    result = {}
    custom = custom or {}

    for field in fields(obj):
        if field.name in exclude:
            continue
        value = getattr(obj, field.name)

        if field.name in custom:
            result[field.name] = custom[field.name](value)
        elif hasattr(value, 'to_dict'):
            result[field.name] = value.to_dict()
        elif isinstance(value, (list, tuple)):
            result[field.name] = [
                v.to_dict() if hasattr(v, 'to_dict') else v
                for v in value
            ]
        elif isinstance(value, dict):
            result[field.name] = {
                k: (v.to_dict() if hasattr(v, 'to_dict') else v)
                for k, v in value.items()
            }
        elif isinstance(value, Enum):
            result[field.name] = value.name
        else:
            result[field.name] = value

    return result


def dataclass_from_dict(
    cls: Type[T],
    data: Dict[str, Any],
    *,
    custom: Dict[str, Callable] = None,
) -> T:
    """
    Auto-deserialize a dict into a @dataclass instance.

    Args:
        cls: The dataclass type to create.
        data: Dict with serialized data.
        custom: Dict of field_name -> deserializer_function overrides.

    Returns:
        New instance of cls populated from data.
    """
    custom = custom or {}
    kwargs = {}

    for field in fields(cls):
        if field.name in custom:
            kwargs[field.name] = custom[field.name](data)
            continue

        if field.name not in data:
            if field.default is not MISSING:
                kwargs[field.name] = field.default
            elif field.default_factory is not MISSING:
                kwargs[field.name] = field.default_factory()
            continue

        value = data[field.name]

        # Apply type coercion if registered
        field_type = get_type_hints(cls).get(field.name)
        if field_type in _COERCERS:
            kwargs[field.name] = _COERCERS[field_type](value)
        else:
            kwargs[field.name] = value

    return cls(**kwargs)
```

**Recommendation: Option C (Standalone utility functions)**

**Rationale:**
1. **No inheritance needed** -- works with existing `@dataclass` classes without changing their class hierarchy.
2. **Incremental adoption** -- Each class can adopt individually. No big-bang migration needed.
3. **Easy to understand** -- Functions, not metaclasses or descriptors. Python developers can reason about them.
4. **Custom overrides** -- The `custom` parameter handles all Category B-C cases without declaring a `_field_serializers` class variable.
5. **Coexistence** -- Category D classes (Ship, Galaxy, Fleet, etc.) keep their hand-written methods. No forced migration.
6. **Testing** -- Utility functions are trivially unit-testable in isolation.

---

### Findings

#### CRITICAL: Dataclass Serialization Boilerplate (14 dataclasses)
**ID:** ABS-LOAD-005
**Location:** 14 `@dataclass` classes across 8 files (see inventory above)
**Issue:** 14 dataclass types implement hand-written `to_dict()`/`from_dict()` that are pure field-by-field copies. For simple cases like `ComponentState`, `NodeState`, and `Event`, the entire to_dict/from_dict pair can be replaced with a single utility call. Even for cases with type coercions (Spectrum, Star, ProjectileState), a `custom` parameter handles the exceptions.
**Impact:** ~421 lines of boilerplate serialization code (Categories A + B) that could be reduced to ~100 lines of utility calls + ~80 lines for the utility module itself.

**Proposed API:** See Option C above (`dataclass_to_dict` / `dataclass_from_dict` in `game/core/serialization.py`).

**Before (ComponentState, 18 lines):**
```python
@dataclass
class ComponentState:
    component_id: str
    current_hp: int
    max_hp: int
    is_active: bool
    layer: str
    modifiers: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'component_id': self.component_id,
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'is_active': self.is_active,
            'layer': self.layer,
            'modifiers': self.modifiers,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentState':
        return cls(
            component_id=data['component_id'],
            current_hp=data['current_hp'],
            max_hp=data['max_hp'],
            is_active=data['is_active'],
            layer=data['layer'],
            modifiers=data.get('modifiers', []),
        )
```

**After (2 lines + import):**
```python
from game.core.serialization import dataclass_to_dict, dataclass_from_dict

@dataclass
class ComponentState:
    component_id: str
    current_hp: int
    max_hp: int
    is_active: bool
    layer: str
    modifiers: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentState':
        return dataclass_from_dict(cls, data)
```

**Before (RaceConfig, 90 lines -- most extreme case):**
```python
def to_dict(self) -> Dict[str, Any]:
    return {
        "race_id": self.race_id,
        "name": self.name,
        "faction_name": self.faction_name,
        # ... 35+ more fields, each a simple copy ...
        "modified_date": self.modified_date,
    }

@classmethod
def from_dict(cls, data: dict) -> 'RaceConfig':
    return cls(
        race_id=data.get("race_id", ""),
        name=data.get("name", ""),
        # ... 35+ more fields, each with a default ...
        modified_date=data.get("modified_date", ""),
    )
```

**After (2 lines):**
```python
def to_dict(self) -> Dict[str, Any]:
    return dataclass_to_dict(self)

@classmethod
def from_dict(cls, data: dict) -> 'RaceConfig':
    return dataclass_from_dict(cls, data)
```

**Before (Star, 24 lines with type coercions):**
```python
def to_dict(self) -> Dict[str, Any]:
    from game.core.hex_math import hex_to_dict
    return {
        'name': self.name,
        'mass': self.mass,
        'diameter_hexes': self.diameter_hexes,
        'temperature': self.temperature,
        'luminosity': self.luminosity,
        'spectrum': self.spectrum.to_dict(),
        'star_type': self.star_type.name,
        'color': list(self.color),
        'age': self.age,
        'location': hex_to_dict(self.location)
    }

@classmethod
def from_dict(cls, data: dict) -> 'Star':
    from game.core.hex_math import hex_from_dict
    return cls(
        name=data['name'],
        mass=data['mass'],
        diameter_hexes=data['diameter_hexes'],
        temperature=data['temperature'],
        luminosity=data['luminosity'],
        spectrum=Spectrum.from_dict(data['spectrum']),
        star_type=StarType[data['star_type']],
        color=tuple(data['color']),
        age=data['age'],
        location=hex_from_dict(data['location'])
    )
```

**After (with custom overrides for non-trivial fields):**
```python
def to_dict(self) -> Dict[str, Any]:
    from game.core.hex_math import hex_to_dict
    return dataclass_to_dict(self, custom={
        'color': lambda v: list(v),
        'location': lambda v: hex_to_dict(v),
    })
    # star_type enum and spectrum nested to_dict handled automatically

@classmethod
def from_dict(cls, data: dict) -> 'Star':
    from game.core.hex_math import hex_from_dict
    return dataclass_from_dict(cls, data, custom={
        'spectrum': lambda d: Spectrum.from_dict(d['spectrum']),
        'star_type': lambda d: StarType[d['star_type']],
        'color': lambda d: tuple(d['color']),
        'location': lambda d: hex_from_dict(d['location']),
    })
```

**Call Sites (Category A -- fully auto-generatable):**
- `game/simulation/battle_state.py:40-59` (ComponentState)
- `game/research/data/research_tracker.py:22-37` (NodeState)
- `game/strategy/events/event_log.py:29-50` (Event)
- `game/strategy/data/design_metadata.py:40-79` (DesignMetadata)
- `game/core/input_actions.py:290-316` (KeyBinding)
- `game/strategy/data/ship_instance.py:608-652` (ShipInstance)

**Call Sites (Category B -- semi-auto with custom):**
- `game/strategy/data/stars.py:48-75` (Spectrum)
- `game/strategy/data/stars.py:107-138` (Star)
- `game/simulation/battle_state.py:344-385` (ProjectileState)
- `game/strategy/data/race_config.py:150-244` (RaceConfig)
- `game/strategy/engine/game_config.py:74-112` (PlayerConfig)
- `game/strategy/engine/game_config.py:182-208` (GameConfig)

**Call Sites (Category C -- nested, partial auto):**
- `game/simulation/battle_state.py:118-174` (ShipState)
- `game/simulation/battle_state.py:499-542` (BattleState)

**Lines Saved:** ~421 lines (Category A+B) -> ~120 lines = ~301 lines saved, plus ~80 lines for utility module = net ~221 lines saved
**Risk:** **MEDIUM.** These methods are used in save/load. Any bug in the utility functions would corrupt save files. Mitigation: (1) comprehensive unit tests for the utility functions, (2) round-trip tests for every class, (3) incremental migration starting with non-save classes (BattleState DTOs first, which are ephemeral, not persisted).
**Category:** Medium Project
**Recommendation:** Create `game/core/serialization.py` with `dataclass_to_dict` and `dataclass_from_dict`. Migrate Category A classes first (6 classes, no type coercion). Then Category B (8 classes, with `custom` parameter). Leave Category D classes unchanged.
**Effort:** Medium

---

#### MAJOR: Non-Dataclass Classes with Boilerplate Serialization
**ID:** ABS-LOAD-006
**Location:** `game/strategy/data/galaxy.py` (WarpPoint, StarSystem, Galaxy), `game/strategy/events/event_log.py` (EventLog), `game/research/data/research_tracker.py` (ResearchTracker)
**Issue:** Several non-dataclass classes have simple to_dict/from_dict methods that could benefit from refactoring to `@dataclass` + utility, but require more structural changes.
**Impact:** ~70 lines of serialization in non-dataclass classes that have simple field mappings but use `__init__` with positional args.

**Proposed approach:** Convert `WarpPoint`, `StarSystem` to `@dataclass` (they already have simple `__init__`s), then use `dataclass_to_dict`. `Galaxy` and `Empire` are too complex (Category D).

**Call Sites:**
- `game/strategy/data/galaxy.py:28-41` (WarpPoint)
- `game/strategy/data/galaxy.py:64-88` (StarSystem)
- `game/strategy/events/event_log.py:88-98` (EventLog)
- `game/research/data/research_tracker.py:236-255` (ResearchTracker)

**Lines Saved:** ~30 lines (from WarpPoint + StarSystem conversion)
**Risk:** Low for WarpPoint/StarSystem (simple classes). Higher for EventLog/ResearchTracker (have additional methods).
**Category:** Small Project (dependent on ABS-LOAD-005)
**Recommendation:** Convert after ABS-LOAD-005 utility is proven. Start with WarpPoint and StarSystem.
**Effort:** Medium

---

#### MAJOR: Category D Complex Serializers Remain Hand-Written (Acceptable)
**ID:** ABS-LOAD-007
**Location:** 7 classes (ShipSerializer, Galaxy, Planet, Fleet, FleetOrder, Empire, GameSession)
**Issue:** These 7 classes have complex serialization logic (polymorphic dispatch, two-phase loading, reference resolution, index rebuilding) that cannot and should not be auto-generated. They represent ~472 lines of serialization code.
**Impact:** This is a documentation/awareness finding. No action needed beyond documenting why they remain hand-written.

**Why they stay hand-written:**
- **ShipSerializer:** Format versioning (`_format_version`), component tree traversal, stat verification, hull layer skipping. Domain-specific logic.
- **Galaxy:** `HexCoord` keys must be converted to/from dicts. Index rebuilding (`planets_by_id`, `name_map`, zone registration) on load. Cannot be declarative.
- **Planet:** Inline serialization of `PlanetaryFacility` and `Population` objects that don't have their own `to_dict`/`from_dict`. Would need to extract DTOs first.
- **Fleet:** Polymorphic `FleetOrder.target` supports 7 different serialization formats (HexCoord, fleet_ref, transfer, planet_ref, ship_id_list, warp_params, raw). This is inherently procedural.
- **Empire:** Two-phase load requires `galaxy` parameter to resolve colony planet references. Conditional field inclusion (flag_id, portrait_id, race_config).
- **GameSession:** Orchestrates two-phase deserialization (galaxy first, then empires with galaxy reference).

**Call Sites:** All 7 files listed above.
**Lines Saved:** 0 (intentionally not auto-generated)
**Risk:** N/A
**Category:** Info (no action needed)
**Recommendation:** Document these as intentional hand-written serializers. Consider extracting `PlanetaryFacility` and `Population` DTOs from Planet in a future project.
**Effort:** N/A

---

#### INFO: ModifierEffect and PathSegment Have to_dict Without from_dict
**ID:** ABS-LOAD-008
**Location:** `game/simulation/components/modifier_effects.py:82`, `game/strategy/services/fleet_navigation_service.py:78`
**Issue:** Two classes have `to_dict()` but no `from_dict()`, indicating they are serialized for introspection/logging only, not for save/load round-tripping.
**Impact:** None. These are correctly write-only serializers. `ModifierEffect.to_dict()` includes a computed `description` field. `PathSegment.to_dict()` includes an alias (`hex` for `end`).
**Call Sites:**
- `game/simulation/components/modifier_effects.py:82-94`
- `game/strategy/services/fleet_navigation_service.py:78-91`
**Lines Saved:** 0
**Risk:** N/A
**Category:** Info
**Recommendation:** No action. Document as intentional.
**Effort:** N/A

---

## Risk Assessment: Save/Load Regression

The to_dict/from_dict methods are the backbone of the save game system. A serialization abstraction change could break save file compatibility. Key mitigations:

1. **Round-trip tests are mandatory.** Every class that adopts `dataclass_to_dict`/`dataclass_from_dict` must have a test: `assert Cls.from_dict(obj.to_dict()) == obj` (or equivalent field-by-field comparison).

2. **Start with ephemeral DTOs.** `ComponentState`, `ShipState`, `ProjectileState`, `BattleState`, and `BattleResults` are used for battle state viewer serialization, not persisted save games. These are the safest to migrate first.

3. **Save game classes come last.** `Fleet`, `Empire`, `Galaxy`, `Planet`, `GameSession`, `ShipInstance` -- these are used in the save system. Migrate only after the utility is battle-tested.

4. **CLAUDE.md policy: "Save files are disposable."** Per project conventions, old saves are discarded, not migrated. This reduces the risk of format changes, but doesn't eliminate the risk of runtime bugs.

5. **Field ordering matters.** The utility must handle `data.get('field', default)` correctly for all fields, matching the existing behavior where some fields use `data['field']` (required) and others use `data.get('field', default)` (optional). The `dataclass_from_dict` utility should use `field.default` / `field.default_factory` from the dataclass definition.

---

## Top 5 Priority Issues

| Rank | ID | Title | Impact | Effort | Lines Saved |
|------|-----|-------|--------|--------|-------------|
| 1 | ABS-LOAD-005 | Dataclass serialization utility | ~221 net lines | Medium | 301 boilerplate -> 80 utility + 120 calls |
| 2 | ABS-LOAD-001 | Strategy generation loader template | Maintainability | Simple | ~27 net + major consistency |
| 3 | ABS-LOAD-002 | Path resolution utility | ~24 lines | Simple | 30 -> 6 |
| 4 | ABS-LOAD-003 | Replace raw json.load with json_utils | ~23 lines | Simple | 41 -> 18 |
| 5 | ABS-LOAD-006 | Non-dataclass serialization cleanup | ~30 lines | Medium | Depends on ABS-LOAD-005 |

### Recommended Implementation Order

1. **Phase 1 (Quick Wins):** ABS-LOAD-002 (path resolution), ABS-LOAD-003 (raw json.load) -- 1 hour, ~47 lines saved
2. **Phase 2 (Loader Template):** ABS-LOAD-001 (BaseConfigLoader for 3 strategy loaders) -- 2 hours, consistency gain
3. **Phase 3 (Serialization Utility):** ABS-LOAD-005 (create utility, migrate 6 Category A dataclasses) -- 4 hours, ~139 lines saved
4. **Phase 4 (Serialization Expansion):** ABS-LOAD-005 Category B (8 more dataclasses with custom overrides) -- 4 hours, ~162 more lines
5. **Phase 5 (Optional):** ABS-LOAD-006 (convert WarpPoint/StarSystem to dataclass) -- 2 hours

**Total estimated effort:** ~13 hours
**Total lines saved:** ~350+ (net, after accounting for new utility code)

---
*Report compiled: 2026-02-23*
*Agent: ABS-LOAD (Loader & Serialization Abstraction Designer)*
