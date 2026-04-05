# Dead Code Analysis Report: `game/strategy/`

**Date:** 2026-04-05
**Scope:** `game/strategy/` (131 Python files, ~30,600 lines)
**Analyzer:** Dead Code Hunter Agent

---

### Summary

- Total issues found: 18
- Critical: 0, Major: 5, Minor: 10, Info: 3

**Breakdown by category:**
- Unused imports: 10 findings (44 individual import lines)
- Dead methods: 4 findings
- Unused variables: 3 findings
- Unused parameters (documented): 1 finding

**No orphaned files, no unreachable code, no commented-out code blocks, and no dead feature flags were found.** The codebase is generally clean. Backward-compatibility aliases (FleetOrder, ClearFleetOrdersCommand, etc.) are still actively used by UI and tests.

---

### Findings

#### MAJOR: Three unused imports in design_metadata.py
**ID:** DC-001
**Location:** `game/strategy/data/design_metadata.py:13-15`
**Issue:** Three imports are completely unused: `warnings` (line 13), `save_json` (line 14), and `iter_layers_and_components` (line 15). None of these symbols appear anywhere else in the file.
**Impact:** Unnecessary module loading at import time. `save_json` and `iter_layers_and_components` pull in additional dependencies. These look like remnants from a refactor where save/iteration functionality was removed from this module but imports were left behind.
**Recommendation:** Remove all three unused imports.
**Effort:** Simple

#### MAJOR: Four unused imports in galaxy.py
**ID:** DC-002
**Location:** `game/strategy/data/galaxy.py:2,6,15`
**Issue:** `Enum` and `auto` (line 2), `HexCoord` (line 6), and `PlanetType` (line 15) are imported but never used in the file body. `HexCoord` is used extensively but only via string annotations; it is imported from `hex_math` but never referenced as a runtime name. `PlanetType` is imported alongside `Planet` but only `Planet` is used. `Enum` and `auto` suggest a removed or never-created enum class.
**Impact:** Misleading imports suggest the file uses these types directly when it does not. `Enum`/`auto` imports suggest an incomplete cleanup from a past refactor.
**Recommendation:** Remove `Enum`, `auto`, and `PlanetType` imports. Move `HexCoord` import into a `TYPE_CHECKING` block since it's only used in annotations.
**Effort:** Simple

#### MAJOR: Dead methods in planet_energy_engine.py (2 functions)
**ID:** DC-003
**Location:** `game/strategy/engine/planet_energy_engine.py:34-57,60-81`
**Issue:** `get_strategic_generation_info()` and `get_resource_storage_info()` are defined but have zero callers anywhere in the entire codebase (game/ and tests/). Only `get_shield_info()` from the same module is actually used (imported by `planet_action_engine.py`).
**Impact:** ~48 lines of dead code. These appear to be helper functions that were written speculatively during PROJ-237/238 but never integrated into any engine or query path.
**Recommendation:** Remove both functions. If needed later, they can be re-derived from the existing `_extract_abilities` helper they both call.
**Effort:** Simple

#### MAJOR: Dead methods in AstrophysicsLoader (3 methods)
**ID:** DC-004
**Location:** `game/strategy/generation/loaders/astrophysics_loader.py:58-110`
**Issue:** Three methods have no callers: `get_mass_distribution()`, `get_orbit_zone()`, and `get_habitable_zone_factors()`. Only the `load()` and `_validate_schema()` methods are actually used. Callers load the raw dict and access keys directly rather than using these accessor methods.
**Impact:** ~53 lines of dead code. These are convenience accessors that were never adopted. Their existence implies an API contract that doesn't exist in practice.
**Recommendation:** Remove all three methods. If typed accessors are desired, they should be added when there are actual callers.
**Effort:** Simple

#### MAJOR: Dead methods: Empire.remove_colony, GameSession.get_current_player_empire, DesignLibrary.delete_design
**ID:** DC-005
**Location:** `game/strategy/data/empire.py:57-60`, `game/strategy/engine/game_session.py:163-168`, `game/strategy/systems/design_library.py:360-390`
**Issue:** Three methods with zero callers in the entire codebase:
- `Empire.remove_colony()` (4 lines) -- colonies are managed but never removed via this method
- `GameSession.get_current_player_empire()` (6 lines) -- empire lookup exists but is done differently elsewhere
- `DesignLibrary.delete_design()` (31 lines) -- design deletion feature that was never connected to UI
**Impact:** ~41 lines of dead code. `delete_design` in particular includes file deletion logic that is completely untested and unreachable.
**Recommendation:** Remove all three methods. If design deletion is needed as a feature, it should be built with TDD when the UI integration is ready.
**Effort:** Simple

#### MINOR: Unused imports in fleet.py
**ID:** DC-006
**Location:** `game/strategy/data/fleet.py:8,11,21`
**Issue:** `Tuple` (line 8), `IPostBattleShip` (line 11), `MOVEMENT_ORDER_TYPES`, and `ACTION_ORDER_TYPES` (line 21) are imported but never used.
**Impact:** `IPostBattleShip` is a cross-layer protocol import that creates an unnecessary dependency. The order type sets are imported from the extracted `order_types.py` but not referenced.
**Recommendation:** Remove all four unused imports.
**Effort:** Simple

#### MINOR: Unused Optional/TYPE_CHECKING in consumable_management_engine.py
**ID:** DC-007
**Location:** `game/strategy/engine/consumable_management_engine.py:14`
**Issue:** Both `Optional` and `TYPE_CHECKING` are imported but never used anywhere in the file.
**Impact:** Minor import clutter. Suggests a planned TYPE_CHECKING block was never added.
**Recommendation:** Remove both from the import line.
**Effort:** Simple

#### MINOR: Scattered unused typing imports across 10+ files
**ID:** DC-008
**Location:** Multiple files (see list below)
**Issue:** Various typing imports that are never used:
- `game/strategy/data/galaxy_warp_generator.py:9` -- `Optional`
- `game/strategy/data/order_serializer.py:10` -- `Optional`
- `game/strategy/data/pathfinding.py:3,6` -- `Sequence`, `OrderType`
- `game/strategy/data/planet.py:7` -- `math`
- `game/strategy/data/star_generation_config.py:9` -- `List`
- `game/strategy/data/storm.py:7` -- `field`
- `game/strategy/engine/atmosphere_engine.py:11` -- `Dict`
- `game/strategy/engine/command_handlers.py:15` -- `Any`
- `game/strategy/engine/order_processor.py:31` -- `HexCoord`
- `game/strategy/engine/superweapon_command_handlers.py:11` -- `Any`
- `game/strategy/engine/superweapon_order_processor.py:22` -- `StarSystem`
- `game/strategy/facade/dto/system_dto.py:5,6` -- `field`, `List`
- `game/strategy/generation/density/primitives/noise.py:9` -- `field`
- `game/strategy/generation/loaders/galaxy_layouts_loader.py:10` -- `Optional`
- `game/strategy/generation/loaders/system_blueprints_loader.py:6` -- `json`
- `game/strategy/generation/region_classifier.py:10` -- `Optional`
- `game/strategy/services/design_validator.py:8` -- `Optional`
- `game/strategy/services/fleet_cargo_projector.py:13` -- `Any`, `Dict`
- `game/strategy/services/fleet_navigation_service.py:30` -- `ACTION_ORDER_TYPES`
- `game/strategy/services/modifier_resolver.py:7` -- `Optional`
- `game/strategy/systems/save_game_service.py:20` -- `PersistenceException`
- `game/strategy/validation/transfer_validator.py:7` -- `Dict`
- `game/strategy/data/planet_gen.py:22` -- `MASS_MOON`
- `game/strategy/engine/empire_economy_calculator.py:211` -- `Fleet` (lazy import, never used as type)
**Impact:** Import clutter across the codebase. Individually minor, but collectively they obscure actual dependencies and make it harder to understand what each module actually uses.
**Recommendation:** Remove all unused imports in a single cleanup pass. A linting tool like `ruff` or `autoflake` can automate this.
**Effort:** Simple (mechanical, can be automated)

#### MINOR: BattleService imported but unused in simulation_adapter.py
**ID:** DC-009
**Location:** `game/strategy/adapters/simulation_adapter.py:30`
**Issue:** `BattleService` is imported from `game.simulation.services.battle_service` but never referenced. Only `BattleController` and `BattleConfig` are used.
**Impact:** Creates an unnecessary cross-layer dependency from the strategy adapter to a simulation service that it doesn't use. This is the most architecturally significant unused import because it pulls simulation internals into the strategy layer without need.
**Recommendation:** Remove the import.
**Effort:** Simple

#### MINOR: Unused variable `owning_empire` in command_handlers.py
**ID:** DC-010
**Location:** `game/strategy/engine/command_handlers.py:526`
**Issue:** In `TransferCommandHandler.execute()`, `owning_empire` is assigned on line 526 but never read afterward. The validation checks `fleet.owner_id` bounds but doesn't use the resolved empire object.
**Impact:** Dead assignment wastes a lookup. If the empire object is needed for validation, it should be used; if not, the assignment is misleading.
**Recommendation:** Remove the assignment. If empire validation is needed beyond the bounds check, add it explicitly.
**Effort:** Simple

#### MINOR: Unused variable `removed_item` in command_handlers.py
**ID:** DC-011
**Location:** `game/strategy/engine/command_handlers.py:943`
**Issue:** In `RemoveFromConstructionQueueCommandHandler.execute()`, `removed_item = queue.pop(cmd.item_index)` captures the popped item but never uses it. The item is logged by index but the actual item content is discarded.
**Impact:** Minor. The variable name suggests the removed item should be logged or returned for UI feedback, but it isn't.
**Recommendation:** Replace with `queue.pop(cmd.item_index)` (no assignment) or log the removed item's details.
**Effort:** Simple

#### MINOR: Unused variable `old_location` in fleet_movement_engine.py
**ID:** DC-012
**Location:** `game/strategy/engine/fleet_movement_engine.py:183`
**Issue:** `old_location = fleet.location` is saved before updating fleet location but never used afterward.
**Impact:** Suggests intent to log or event-track movement origin that was never implemented.
**Recommendation:** Remove the assignment, or use it in event logging if movement tracking is desired.
**Effort:** Simple

#### MINOR: Unused variable `parallel_clamped` in linear.py density primitive
**ID:** DC-013
**Location:** `game/strategy/generation/density/primitives/linear.py:65`
**Issue:** `parallel_clamped` is computed but never referenced. The perpendicular distance calculation and past-end logic use `parallel` (the unclamped value) directly instead.
**Impact:** Dead computation. The clamped value was likely intended for distance calculation but the algorithm evolved to use a different approach.
**Recommendation:** Remove the unused assignment.
**Effort:** Simple

#### MINOR: Unused variable `cluster_regions` in region_classifier.py
**ID:** DC-014
**Location:** `game/strategy/generation/region_classifier.py:257`
**Issue:** `cluster_regions` list comprehension is computed but never used. The subsequent loop iterates `self._cluster_centers` directly instead of using the filtered regions list.
**Impact:** Wasted list comprehension. The variable name suggests it was intended to be used in the neighbor-finding logic below but was superseded by direct index-based iteration.
**Recommendation:** Remove the unused assignment.
**Effort:** Simple

#### INFO: Documented unused parameters in interface methods
**ID:** DC-015
**Location:** `game/strategy/engine/production_engine.py:548`, `game/strategy/engine/superweapon_order_processor.py:644`
**Issue:** Two parameters are documented as "unused" in their docstrings: `empire` parameter in production_engine.py and `galaxy` parameter in superweapon_order_processor.py. Both are kept for "signature consistency" with related methods.
**Impact:** None -- these are intentionally unused for API consistency. Documented properly.
**Recommendation:** No action needed. These are acceptable for interface conformity.
**Effort:** N/A

#### INFO: `math` imported but unused in planet.py
**ID:** DC-016
**Location:** `game/strategy/data/planet.py:7`
**Issue:** `import math` appears at the top of planet.py but no `math.` calls exist in the file.
**Impact:** Minimal. May have been used before planet_physics.py was extracted.
**Recommendation:** Remove the import.
**Effort:** Simple

#### INFO: Duplicate `Any` import in planet.py
**ID:** DC-017
**Location:** `game/strategy/data/planet.py:10-11`
**Issue:** `Any` is imported twice -- once on line 10 (`from typing import Dict, FrozenSet, List, Optional, Any`) and again on line 11 (`from typing import TYPE_CHECKING as _TC, Any`). Python handles this silently but it indicates a careless merge of import lines.
**Impact:** No runtime impact but indicates import lines should be consolidated.
**Recommendation:** Merge into a single import line: `from typing import Any, Dict, FrozenSet, List, Optional, TYPE_CHECKING`.
**Effort:** Simple

#### INFO: `get_shield_info` imported but unused in planet_action_engine.py
**ID:** DC-018
**Location:** `game/strategy/engine/planet_action_engine.py:20`
**Issue:** `get_shield_info` is imported from `planet_energy_engine` but never called in the file.
**Impact:** Minimal unused import.
**Recommendation:** Remove the import.
**Effort:** Simple

---

### Top 5 Priority Issues

1. **DC-003 (MAJOR)**: Dead functions `get_strategic_generation_info` and `get_resource_storage_info` in `planet_energy_engine.py` -- 48 lines of completely dead code with no callers
2. **DC-004 (MAJOR)**: Dead methods in `AstrophysicsLoader` -- 53 lines of accessor methods with zero callers
3. **DC-005 (MAJOR)**: Dead methods `Empire.remove_colony`, `GameSession.get_current_player_empire`, `DesignLibrary.delete_design` -- 41 lines total, `delete_design` includes untested file-deletion logic
4. **DC-001 (MAJOR)**: Three unused imports in `design_metadata.py` including `save_json` and `iter_layers_and_components` -- these are cross-module dependencies that add unnecessary coupling
5. **DC-008 (MINOR, high volume)**: 24+ unused imports scattered across the codebase -- best addressed with automated tooling (`ruff check --select F401 --fix`) for a clean sweep

---

### Recommendations

**Quick wins (< 1 hour):**
- Run `ruff check --select F401 --fix game/strategy/` to auto-remove all unused imports (DC-001, DC-002, DC-006, DC-007, DC-008, DC-009, DC-016, DC-017, DC-018)
- Delete the 5 dead methods (DC-003, DC-004, DC-005)
- Remove the 4 unused variable assignments (DC-010, DC-011, DC-012, DC-013, DC-014)

**Estimated total dead code:** ~190 lines removable across all findings.

**No DOC-prefix issues found.** The `__init__.py` exports match the documented public API in `docs/01_ARCHITECTURE.md`. All backward-compatibility aliases are still actively used by UI and test code.
