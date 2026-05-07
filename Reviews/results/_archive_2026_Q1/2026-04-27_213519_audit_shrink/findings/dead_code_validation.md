# Dead Code Validation Report

## Summary
- **Total Candidates Reviewed:** 18 (unique items from Vulture 100% + 80% confidence)
- **Confirmed Dead:** 11
- **False Positives:** 7
- **Documentation Discrepancies:** 0

---

## Confirmed Dead Code

### Tier 1: Dead Files
*None*

### Tier 2: Dead Classes
*None*

### Tier 3: Dead Functions/Methods

| Function | File:Line | Source | LOC | Verified? |
|----------|-----------|--------|-----|-----------|
| `_format_sig_digits` `sig_digits` param | `game/ui/panels/modifier_impact_grid.py:273` | Vulture 100% | ~1 | Yes — param `sig_digits` declared but never used; method body uses hardcoded thresholds (1000, 100, 10). All 3 callers (lines 262, 264, 270) call without the param. |
| `_determine_type_and_radius` `age_ratio` param | `game/strategy/data/stars.py:303` | Vulture 100% | ~3 | Yes — param `age_ratio` declared but never referenced in method body (lines 310-361). All 3 callers (lines 576, 662, 714) call with only `mass`. |
| `from_dict` `naming_data_path` param | `game/strategy/data/galaxy.py:624` | Vulture 100% | ~3 | Yes — param `naming_data_path` declared but never used in method body (lines 642-694). Zero callers pass this param. |
| Unreachable `return 1` | `game/strategy/services/action_time_resolver.py:115` | Vulture 100% | 1 | Yes — both if/else branches (lines 104-113) return. Line 115 is unreachable. |

### Tier 4: Dead Imports

| Import | File:Line | Source | Verified? |
|--------|-----------|--------|-----------|
| `MASS_MOON` | `game/strategy/data/planet_gen.py:23` | Vulture 80% | Yes — imported from `planet_physics`, never referenced in file body. |
| `get_shield_info` | `game/strategy/engine/planet_action_engine.py:25` | Vulture 80% | Yes — imported from `planet_energy_engine`, never called in file. |
| `STAR_FALLBACK` | `game/ui/screens/galaxy_test/system_mode.py:17` | Vulture 80% | Yes — imported from `game.ui.colors`, never referenced in file body. |
| `ConfirmationDialog` | `game/ui/screens/test_lab/screen.py:32` | Vulture 80% | Yes — imported from `.dialogs`, never instantiated or referenced. `JSONPopup` from same import IS used (lines 722, 731, 733). Not re-exported via `__init__.py`. |
| `_ccm_mod` (import alias) | `game/context.py:96` | Vulture 80% | Yes — imports `get_default_cache_manager as _ccm_mod`; the alias `_ccm_mod` is never called. Actual module-level ref set via separate import at lines 115-116 (`_ccm_module`). |
| `FleetType` (TYPE_CHECKING alias) | `game/strategy/facade/dto/fleet_dto.py:11` | Vulture 80% | Yes — `from ...fleet import Fleet as FleetType` under TYPE_CHECKING, but `FleetType` never used in type annotations. The real `Fleet` is imported at line 13. Runtime-noop but truly dead. |
| `ShipIOType` (TYPE_CHECKING alias) | `game/ui/services/ship_io_adapter.py:19` | Vulture 80% | Yes — `from ...ship_io import ShipIO as ShipIOType` under TYPE_CHECKING, but `ShipIOType` never used in type annotations. Runtime-noop but truly dead. |

---

## False Positives (Not Dead)

| Item | Reason It's Actually Used |
|------|--------------------------|
| `exc_type, exc_val, exc_tb` in `battle_engine.py:98` | Standard `__exit__` context manager protocol parameters. Required by Python's `__exit__` signature even if unused in body. |
| `RegionClassifier` in `galaxy.py:30` | Under `if TYPE_CHECKING:`. Used in type annotations at lines 578, 592 (`Optional[RegionClassifier]`). |
| `RegionClassifier` in `galaxy_warp_generator.py:15` | Under `if TYPE_CHECKING:`. Used in type annotations at lines 206, 220, 292, 304, 331, 345. |
| `IControllableShip` in `controller.py:55` | Under `if TYPE_CHECKING:`. Used in `__init__` type annotation at line 84 (`ship: 'IControllableShip'`). |
| `BuildContext` in `build_queue_controller.py:18` | Under `if TYPE_CHECKING:`. Used in type annotation at line 59 (`Union['Planet', 'Fleet', 'BuildContext']`). |
| `unused import 'FleetType'` at 80% (fleet_dto.py:11) | Under `if TYPE_CHECKING:` and the underlying `Fleet` class is used at runtime (line 13 import). Dead alias but zero runtime impact. Listed in confirmed dead above for thoroughness but safe to leave. |
| `unused import 'ShipIOType'` at 80% (ship_io_adapter.py:19) | Under `if TYPE_CHECKING:`. Dead alias but zero runtime impact. Listed in confirmed dead above for thoroughness but safe to leave. |

---

## Documentation Discrepancies
*None found*. Searched `docs/` for references to `naming_data_path`, `age_ratio`, `MASS_MOON`, `get_shield_info`, `_ccm_mod` — no matches.

---

## Prioritized Cleanup Order

Ordered by safety (lowest regression risk first) then by LOC savings:

| Priority | Item | File | Action | Est. LOC |
|----------|------|------|--------|----------|
| 1 | `return 1` unreachable line | `action_time_resolver.py:115` | Delete line | 1 |
| 2 | `_ccm_mod` dead alias | `context.py:96` | Remove `as _ccm_mod` alias from import | 1 |
| 3 | `MASS_MOON` dead import | `planet_gen.py:23` | Remove from multi-import line | 0.5 |
| 4 | `STAR_FALLBACK` dead import | `system_mode.py:17` | Remove from multi-import line | 0.5 |
| 5 | `get_shield_info` dead import | `planet_action_engine.py:25` | Delete import line | 1 |
| 6 | `ConfirmationDialog` dead import | `test_lab/screen.py:32` | Remove token from import line | 0.5 |
| 7 | `FleetType` dead TYPE_CHECKING alias | `fleet_dto.py:11` | Delete import line | 1 |
| 8 | `ShipIOType` dead TYPE_CHECKING alias | `ship_io_adapter.py:19` | Delete import line | 1 |
| 9 | `sig_digits` unused param | `modifier_impact_grid.py:273` | Remove param + update docstring | 2 |
| 10 | `age_ratio` unused param | `stars.py:303` | Remove param + update docstring | 3 |
| 11 | `naming_data_path` unused param | `galaxy.py:624` | Remove param + update docstring | 3 |

**Total estimated LOC savings: ~15 lines**

### Notes
- Items 1-8 are zero-risk removals (trivially safe).
- Items 9-11 (unused parameters) require updating the method signature. All verified that no callers pass these parameters.
- No Tier 1 (dead files) or Tier 2 (dead classes) found — all dead code is at the import/parameter/line level.
- The Vulture-detected orphan modules and unreachable files are not production dead code; they are artifacts of the dependency graph tool using a different base path. See the main audit report for details.
