# Validation Report: Validator 2

## Summary
- **Findings Reviewed:** 27
- **Confirmed:** 22
- **Downgraded:** 4
- **Rejected:** 1
- **Rejection Rate:** 3.7%

## Verdicts

#### Finding: CQ-016
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** The `_get_reference_planet` method at line 798-815 does indeed use a for loop (`for planet in planets: return planet`) that immediately returns the first element. While functionally equivalent to `planets[0] if planets else None`, it is an unusual idiom. The severity of Info is appropriate since it is intentional per the comment.

#### Finding: CQ-017
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Galaxy.__init__ at lines 179 and 187 calls `os.path.join(os.getcwd(), 'data', ...)` to load YAML and JSON files, making it dependent on the current working directory. Verified in source.

#### Finding: CQ-018
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** The facade's `_get_fleet_by_id` at line 94 calls `self._session._get_fleet_by_id()`, accessing a private method on GameSession. Similarly `_get_empire_by_id` follows the same pattern. Info severity is appropriate since both sides are private.

#### Finding: DC-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 13-15 of design_metadata.py import `warnings`, `save_json`, and `iter_layers_and_components`. Grep confirms none of these are referenced anywhere else in the file beyond the import statements.

#### Finding: DC-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** `Enum` and `auto` are imported at line 2 but never used in galaxy.py body -- confirmed. `HexCoord` IS used extensively throughout the file (in type hints, dict keys, etc.), so that part of the claim is FALSE. `PlanetType` is imported at line 15 but only appears on the import line -- confirmed unused. Downgraded because only 3 of 4 claimed imports are actually unused, and HexCoord is a false positive.

#### Finding: DC-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `get_strategic_generation_info()` and `get_resource_storage_info()` in planet_energy_engine.py have zero callers across the entire codebase -- grep found them only in their own definition file.

#### Finding: DC-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `get_mass_distribution()`, `get_orbit_zone()`, and `get_habitable_zone_factors()` in astrophysics_loader.py are only found in their own file -- no callers anywhere in the codebase.

#### Finding: DC-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `Empire.remove_colony` has zero callers (only defined in empire.py). `GameSession.get_current_player_empire` is only defined in game_session.py with no callers. `DesignLibrary.delete_design` is only defined in design_library.py with no `.delete_design` calls anywhere. All three are dead code.

#### Finding: DC-006
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** `Tuple` is in the typing import at line 8 but AST analysis shows 0 references in the file body. `IPostBattleShip` is imported at line 11 with 0 references. `MOVEMENT_ORDER_TYPES` and `ACTION_ORDER_TYPES` are imported at lines 24-25 with 0 references. All confirmed unused. However, the order type imports may be there for re-export purposes (common pattern in this codebase), and `IPostBattleShip` could be for type-checking. Downgraded to Info since these are in a data file that may serve as a namespace.

#### Finding: DC-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 14 of consumable_management_engine.py imports `Optional` and `TYPE_CHECKING` from typing, but neither appears anywhere else in the file. Both are unused.

#### Finding: DC-008
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** The finding claims "scattered unused typing imports across 10+ files" with location "Unknown" and gives example files. While some unused typing imports likely exist, the finding is too vague -- no specific locations, no specific imports. Downgraded to Info due to lack of specificity; each file would need individual verification.

#### Finding: DC-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 30 of simulation_adapter.py imports `BattleService` but grep shows it is never referenced elsewhere in the file.

#### Finding: DC-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 526 of command_handlers.py assigns `owning_empire = session.empires[fleet.owner_id]` but the variable is never read afterward in the method. The method proceeds to resolve a planet and do transfer validation without using `owning_empire`.

#### Finding: DC-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 943 of command_handlers.py assigns `removed_item = queue.pop(cmd.item_index)` but `removed_item` is never referenced afterward. The pop is needed for its side effect but the return value is unused.

#### Finding: DC-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 183 of fleet_movement_engine.py assigns `old_location = fleet.location` but the variable is never used subsequently. The fleet location is immediately overwritten on the next line.

#### Finding: DC-013
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 65 of linear.py computes `parallel_clamped = max(-half_length, min(half_length, parallel))` but the variable is never referenced afterward. The code uses `parallel` and `perpendicular` instead.

#### Finding: DC-014
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 257 of region_classifier.py computes `cluster_regions = [r for r in self._regions if r.region_type == 'cluster']` but the list comprehension result is never used. The subsequent loop iterates over `self._cluster_centers` instead.

#### Finding: DC-015
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Line 548 of production_engine.py documents `empire` parameter as "unused fallback" in the docstring. This is a deliberate design choice for signature consistency, and Info severity is appropriate.

#### Finding: DC-016
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Line 7 of planet.py has `import math` but grep confirms zero `math.` calls in the file.

#### Finding: DC-017
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Lines 10-11 of planet.py import `Any` twice: once from `typing` on line 10, and again on line 11 via `from typing import TYPE_CHECKING as _TC, Any`. This is a duplicate import.

#### Finding: DC-018
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Line 20 of planet_action_engine.py imports `get_shield_info` from planet_energy_engine, but grep shows it is never called anywhere else in the file.

#### Finding: DOCC-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** The orders_system.md document uses `FleetOrder` 7 times (per grep count). Per PROJ-238, the class was renamed from `FleetOrder` to `Order`. The doc still shows `class FleetOrder:` in its code example and references `FleetOrder` throughout.

#### Finding: DOCC-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `ACTIVATE_ABILITY` and `DEACTIVATE_ABILITY` are defined in order_types.py (lines 36-37) and included in `ACTION_ORDER_TYPES` (lines 62-63, 68-69), but grep confirms they do not appear anywhere in orders_system.md.

#### Finding: DOCC-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Turn engine lines 380-384 show QualityEngine and AtmosphereEngine running after the 100-tick loop and population growth. These post-loop phases are not documented in the orders_system.md or the module docstring's phase list.

#### Finding: DOCC-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `SetAtmosphereTargetCommand` exists in commands.py and has handlers registered in command_handlers.py and planet_command_handlers.py, but grep confirms it does not appear in strategy_layer.md's command table.

#### Finding: DOCC-005
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** The docs list `ClearFleetOrdersCommand`, `DeleteFleetOrderCommand`, `ReorderFleetOrderCommand` as the command names in the table. The code defines the primary names as `ClearOrdersCommand`, `DeleteOrderCommand`, `ReorderOrderCommand` with the `FleetOrder` variants as compatibility aliases. However, the docs table shows these alongside the correct handler names (`ClearOrdersCommandHandler`, `DeleteFleetOrderCommandHandler`, `ReorderFleetOrderCommandHandler`). Both old and new names work due to the alias registration (line 1015: `registry.register('ClearFleetOrdersCommand', ClearOrdersCommandHandler())`). The finding claims the doc names are "stale" but they are valid registered aliases. The doc could be updated to use the primary names, but the current names are not incorrect. Rejected as the aliases are intentionally maintained.

#### Finding: DOCC-006
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** The module docstring (lines 1-23) omits Phase 0c1 (PlanetEnergyEngine), Phase 0f (EnvironmentalHazardEngine), Phase 1.6 (PlanetActionEngine), and post-loop phases (QualityEngine, AtmosphereEngine). This is confirmed -- the module docstring lists only 10 phases while the actual code has 14. However, the `_process_tick` method docstring (lines 430-443) documents some of these (0f specifically). Downgraded from Critical to Major because the issue is a stale docstring, not a functional bug, and some phases are documented in the method-level docstring.
