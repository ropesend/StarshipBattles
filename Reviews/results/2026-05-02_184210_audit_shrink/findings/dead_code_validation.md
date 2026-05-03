# Dead Code Validation Report

## Summary
- Total Candidates Reviewed: 18
- Confirmed Dead: 10
- Product Decision Required: 1
- False Positives: 7
- Documentation Discrepancies: 0

## Confirmed Dead Code (no tests, docs, or production references)

### Tier 1: Dead Files (delete entire files)
*None found.*

### Tier 2: Dead Classes (remove from files)
*None found.*

### Tier 3: Dead Functions/Methods
*None found.* (3 parameter removals + 1 unreachable-line removal below.)

### Tier 4: Dead Parameters, Imports, and Unreachable Code

| # | Item | File:Line | Source | LOC Impact | Test refs? | Doc refs? | Verified? |
|---|------|-----------|--------|------------|------------|-----------|-----------|
| 1 | `_ccm_mod` unused import | `game/context.py:116` | Vulture 80% | ~1 | No | No | Yes. `_ccm_module` at line 138 replaces it. |
| 2 | `naming_data_path` unused param | `game/strategy/data/galaxy.py:624` | Vulture 100% | ~3 | No | No | Yes. Zero callers pass this param. Method body never references it. |
| 3 | `age_ratio` unused param | `game/strategy/data/strs.py:303` | Vulture 100% | ~3 | No | No | Yes. `_determine_type_and_radius()` body (lines 310-361) never references `age_ratio`. |
| 4 | `MASS_MOON` unused import | `game/strategy/data/planet_gen.py:23` | Vulture 80% | ~1 | Separate import in test_planet_physics.py | No | Yes. Imported but never referenced in planet_gen.py. |
| 5 | `get_shield_info` unused import | `game/strategy/engine/planet_action_engine.py:25` | Vulture 80% | ~1 | No | No | Yes. Imported but never referenced in planet_action_engine.py. |
| 6 | `FleetType` unused TYPE_CHECKING import | `game/strategy/facade/dto/fleet_dto.py:11` | Vulture 80% | ~1 | No | No | Yes. Imported under TYPE_CHECKING as `Fleet as FleetType` but never used even in string annotations. |
| 7 | `unreachable return 1` | `game/strategy/services/action_time_resolver.py:115` | Vulture 100% | ~1 | No | No | Yes. `return 1` after if/else where both branches return (lines 104-113). |
| 8 | `sig_digits` unused param | `game/ui/panels/modifier_impact_grid.py:273` | Vulture 100% | ~2 | No | No | Yes. All 3 callers (lines 262, 264, 270) call without the param. Method uses hardcoded thresholds. |
| 9 | `ConfirmationDialog` unused import | `game/ui/screens/test_lab/screen.py:32` | Vulture 80% | ~1 | No | No | Yes. Imported from `.dialogs` but never referenced in screen.py. |
| 10 | `ShipIOType` unused TYPE_CHECKING import | `game/ui/services/ship_io_adapter.py:19` | Vulture 80% | ~1 | No | No | Yes. Imported under TYPE_CHECKING as `ShipIO as ShipIOType` but never used even in string annotations. |

## Product Decision Required
Items with zero production callers but referenced by tests or docs:

| Item | File:Line | Production refs | Test refs | Doc refs | Recommendation |
|------|-----------|-----------------|-----------|----------|----------------|
| `STAR_FALLBACK` import | `game/ui/screens/galaxy_test/system_mode.py:17` | 0 (import only) | 0 | `docs/06_UI_STYLE_GUIDE.md:415` | Remove the import from system_mode.py. The constant in colors.py stays (documented). The import in this file serves no purpose. |

## False Positives (Not Dead)

| # | Item | File:Line | Reason It's Actually Used |
|---|------|-----------|--------------------------|
| 1 | `exc_tb` | `game/simulation/systems/battle_engine.py:98` | `__exit__` context manager protocol parameter. Required by the `BattleLogger.__exit__` method signature per the context manager protocol. |
| 2 | `exc_type` | `game/simulation/systems/battle_engine.py:98` | Same as above — `__exit__` protocol parameter. |
| 3 | `exc_val` | `game/simulation/systems/battle_engine.py:98` | Same as above — `__exit__` protocol parameter. |
| 4 | `IControllableShip` | `game/ai/controller.py:56` | `TYPE_CHECKING` import used as string type annotation at line 87: `ship: 'IControllableShip'`. Standard pattern for breaking circular imports at the type-checking boundary. |
| 5 | `RegionClassifier` | `game/strategy/data/galaxy.py:30` | `TYPE_CHECKING` import used as string type annotation at line 578: `region_classifier: 'Optional[RegionClassifier]'`. |
| 6 | `RegionClassifier` | `game/strategy/data/galaxy_warp_generator.py:15` | `TYPE_CHECKING` import used as string type annotations at lines 206, 292, 331. |
| 7 | `BuildContext` | `game/ui/panels/build_queue_controller.py:18` | `TYPE_CHECKING` import used as string type annotation at line 59: `build_context: Union['Planet', 'Fleet', 'BuildContext']`. Also used in dedicated tests at `tests/unit/strategy/data/test_build_context.py`. |

## Documentation Discrepancies
*None found.* Searched `docs/` for all 18 candidate symbols — only `STAR_FALLBACK` appeared (in `docs/06_UI_STYLE_GUIDE.md`), and that is a valid reference to the color constant in `game/ui/colors.py`, not to the dead import in `system_mode.py`.

## Prioritized Cleanup Order

Ordered by safety (parameter removals with zero callers first) then by LOC savings:

| Priority | Item | Action | LOC | Risk |
|----------|------|--------|-----|------|
| 1 | `naming_data_path` param (galaxy.py) | Remove param from `from_dict()` signature + docstring | ~3 | None. Zero callers pass this param. |
| 2 | `age_ratio` param (stars.py) | Remove param from `_determine_type_and_radius()` signature + docstring | ~3 | None. Method body never uses it. |
| 3 | `sig_digits` param (modifier_impact_grid.py) | Remove param from `_format_sig_digits()` signature + docstring | ~2 | None. All callers use default. |
| 4 | `return 1` (action_time_resolver.py) | Delete unreachable line 115 | ~1 | None. Static analysis confirms unreachable. |
| 5 | `_ccm_mod` import (context.py) | Delete line 116 | ~1 | None. `_ccm_module` at line 138 replaces it. |
| 6 | `MASS_MOON` import (planet_gen.py) | Remove from import tuple at line 23 | ~1 | None. Not referenced in file. |
| 7 | `get_shield_info` import (planet_action_engine.py) | Delete line 25 | ~1 | None. Not referenced in file. |
| 8 | `FleetType` import (fleet_dto.py) | Delete line 11 | ~1 | None. Not used even in type annotations. |
| 9 | `ConfirmationDialog` import (screen.py) | Remove from import at line 32 (keep `JSONPopup`) | ~1 | None. Not referenced in file. |
| 10 | `ShipIOType` import (ship_io_adapter.py) | Delete line 19 | ~1 | None. Not used even in type annotations. |
| PD1 | `STAR_FALLBACK` import (system_mode.py) | Remove from import at line 17 | ~1 | Minimal. Color constant stays documented. |
| **Total** | | | **~16** | |
