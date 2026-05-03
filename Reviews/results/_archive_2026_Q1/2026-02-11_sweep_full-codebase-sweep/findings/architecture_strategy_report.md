# Architecture Drift Sweep: Strategy

## Summary
- **Shard:** Strategy (`game/strategy/` and all subdirectories)
- **Files Scanned:** 95
- **Total Issues Found:** 13
- **Critical:** 0 | **Major:** 6 | **Minor:** 5 | **Info:** 2

## Findings

### Phase 1: Import Graph Analysis

No layer violations found. All imports follow the permitted dependency graph:
- Strategy imports from `game.core` (permitted)
- Strategy imports from `game.simulation` (permitted)
- No imports from `game.ui` or `game.ai` detected
- No `import pygame` detected

The simulation imports from strategy are concentrated in appropriate adapter/bridge code:
- `adapters/simulation_adapter.py` (BattleController, BattleConfig, BattleService)
- `services/ship_stats_calculator.py` (formula_system, modifiers)
- `data/ship_instance.py` (ShipSerializer - lazy import)
- `data/fleet_battle_adapter.py` (Ship - TYPE_CHECKING only)

All of these are allowed by the architecture rules (strategy depends on simulation).

### Phase 2: Pygame Boundary Violations

No violations found. Zero `import pygame` or `from pygame` statements in the strategy layer.

### Phase 3: Circular Dependencies

#### MINOR: Pervasive Lazy Imports to Avoid Circular Dependencies
**ID:** ADR-STR-001
**Location:** Multiple files (63+ lazy imports identified across the strategy layer)
**Issue:** The strategy layer uses an extensive pattern of function-level lazy imports to avoid circular dependency errors. Key clusters:
- `game_session.py` has 7 lazy imports inside methods (lines 85, 167, 191, 284-286)
- `turn_engine.py` has 12 lazy imports inside methods (lines 144, 173, 181, 189, 197, 208, 217, 225, 233, 241, 298)
- `command_handlers.py` has 8 lazy imports inside methods (lines 77, 130, 178, 203, 232-233, 315-316, 366)
- `fleet_order_processor.py` has 7 lazy imports inside methods (lines 185, 265-266, 319, 367, 426, 540)
- `design_library.py` has 10 lazy imports of `log_*` functions inside individual methods

While individually benign, this density of lazy imports indicates circular dependency pressure in the module graph. The `design_library.py` pattern of importing `log_warning` inside every method (lines 222, 226, 230, 270, 306, 310, 314, 402) instead of at module level is particularly suspicious.
**Impact:** Makes the dependency graph harder to reason about; IDE tools cannot fully analyze import structure; slight runtime overhead from repeated imports
**Recommendation:** Audit the module dependency graph with a tool like `pydeps` to identify the specific cycles, then restructure modules to break them. The `design_library.py` logger imports should be top-level.
**Effort:** Complex

#### MINOR: Galaxy Circular Dependency with Placement Strategies
**ID:** ADR-STR-002
**Location:** `game/strategy/data/galaxy.py:354-356`
**Issue:** `Galaxy.generate_star_systems()` uses a lazy import with the comment "Import here to avoid circular dependency" for `RandomPlacementStrategy` and `SpatialIndex`. The data layer module (`data/galaxy.py`) depends on the generation module (`generation/placement_strategies.py`), but placement_strategies also imports from data via `SpatialIndex`. This creates a circular reference that is broken by the lazy import.
**Impact:** Indicates the Galaxy class has generation responsibilities that should belong in a separate generator/builder
**Recommendation:** Extract `generate_star_systems()` and related generation methods from `Galaxy` into a dedicated `GalaxyBuilder` or move to the existing `game_initializer.py`
**Effort:** Medium

### Phase 4: God Classes and Inappropriate Intimacy

#### MAJOR: ProductionEngine God Class (701 lines, 14 methods)
**ID:** ADR-STR-003
**Location:** `game/strategy/engine/production_engine.py:31-731`
**Issue:** `ProductionEngine` is 701 lines with responsibilities spanning: base construction queue processing, shipyard facility queues, fleet yard queues, ship spawning, complex spawning, per-tick resource consumption, and completion event logging. It handles three distinct production contexts (planet base, planet shipyard, fleet yard) with partially duplicated logic.
**Impact:** Difficult to test individual production paths in isolation; changes to one production type risk breaking others; high cognitive load
**Recommendation:** Extract into `BaseConstructionEngine`, `ShipyardProductionEngine`, and `FleetYardProductionEngine` with a shared `ProductionProcessor` base
**Effort:** Complex

#### MAJOR: Galaxy God Class (698 lines, 26 methods)
**ID:** ADR-STR-004
**Location:** `game/strategy/data/galaxy.py:99-796`
**Issue:** `Galaxy` is 698 lines with 26 methods spanning: system storage, system generation, warp link creation, warp link angle calculation, edge candidate building, MST computation, serialization/deserialization, and system lookup queries. It mixes data container responsibilities with generation algorithms and graph algorithms.
**Impact:** Violates Single Responsibility Principle; generation logic cannot be reused or tested without instantiating a full Galaxy; changes to warp generation risk breaking data access
**Recommendation:** Extract generation methods (`generate_star_systems`, `create_vars_link`, `_build_edge_candidates`, etc.) into a `GalaxyGenerator` or `WarpLinkGenerator`. Keep `Galaxy` as a pure data container + query interface.
**Effort:** Complex

#### MAJOR: ShipInstance God Class (658 lines, 44 methods)
**ID:** ADR-STR-005
**Location:** `game/strategy/data/ship_instance.py:31-688`
**Issue:** `ShipInstance` has 44 methods across 658 lines. While some responsibilities have been extracted to delegates (`ShipResourceManager`, `ShipCargoManager`, `ShipDisplayFormatter`), the class still has excessive responsibilities: state tracking, damage management, stat calculation, combat conversion, serialization, and resource management delegation. The 44 methods constitute a very wide API surface.
**Impact:** Wide API surface makes the class hard to understand and maintain; high coupling point for the entire strategy layer
**Recommendation:** Continue the existing extraction pattern. Consider extracting combat conversion (`to_ship`, `from_ship`, `update_from_ship`) into a `ShipBattleConverter` and serialization (`to_dict`, `from_dict`) into a `ShipInstanceSerializer`.
**Effort:** Medium

#### MAJOR: Fleet God Class (353 lines, 41 methods)
**ID:** ADR-STR-006
**Location:** `game/strategy/data/fleet.py:69-421`
**Issue:** `Fleet` has 41 methods despite being only 353 lines (average 8.6 lines per method). While delegates exist (`FleetResourceAggregator`, `FleetCapabilityCalculator`, `FleetBattleAdapter`), many delegate methods are re-exposed as thin wrappers on Fleet itself, inflating the method count. The class acts as a facade over its delegates while also managing state, orders, and serialization.
**Impact:** The 41-method API surface is difficult to navigate; facade pattern creates a "pass-through tax" where every new delegate method requires a corresponding wrapper
**Recommendation:** Consider exposing delegates directly via properties (e.g., `fleet.capabilities.can_colonize()` instead of `fleet.can_colonize()`) to reduce the wrapper count. This is partially done already with `fleet.capabilities`.
**Effort:** Medium

#### MINOR: FleetBattleAdapter Accesses Private Method
**ID:** ADR-STR-007
**Location:** `game/strategy/data/fleet_battle_adapter.py:124`
**Issue:** `FleetBattleAdapter.update_from_battle_results()` calls `self._fleet._trigger_speed_recalculation()`, accessing a private method (underscore-prefixed) on the `Fleet` object from an external class. This violates encapsulation.
**Impact:** Creates tight coupling between FleetBattleAdapter and Fleet's internal implementation; private methods can change without notice
**Recommendation:** Either make `_trigger_speed_recalculation` a public method (rename to `trigger_speed_recalculation`) since it is called from an external delegate, or have Fleet expose a `notify_ship_roster_changed()` method that internally triggers recalculation.
**Effort:** Simple

### Phase 5: Data Flow Violations

#### MAJOR: ShipDisplayFormatter in Strategy Data Layer
**ID:** ADR-STR-008
**Location:** `game/strategy/data/ship_display_formatter.py:1-111`
**Issue:** The `ShipDisplayFormatter` class is explicitly documented as handling "UI/display concerns" and its own docstring states "These methods are UI concerns that don't belong in the data layer." Despite this self-awareness, it resides in `game/strategy/data/` and is imported by `ShipInstance` (a core data class). It formats strings like "DesignName-000001", "OK"/"DAMAGED"/"DERELICT"/"DESTROYED", and "150/200" -- all presentation logic.
**Impact:** Display/presentation logic coupled into the strategy data layer; if display format requirements change (e.g., localization), the strategy data layer must be modified
**Recommendation:** Move to `game/ui/` or `game/strategy/facade/` where it belongs, or make it a utility that the UI layer calls rather than being embedded in ShipInstance
**Effort:** Medium

#### MINOR: Color Tuples Embedded in Strategy Game Configuration
**ID:** ADR-STR-009
**Location:** `game/strategy/engine/game_config.py:26-31,61`
**Issue:** `THEME_DEFAULTS` contains hardcoded RGB color tuples like `(0, 100, 255)` and `PlayerConfig.color` defaults to `(128, 128, 128)`. These are rendering concerns embedded in strategy-layer game configuration. The `Star` class (`data/stars.py:84`) also stores a `color: tuple` RGB value.
**Impact:** Mixes visual presentation data with game logic configuration; colors should be determined by the UI/theme layer, not hardcoded in strategy config. However, star color derived from temperature is arguably domain data (astrophysics), so the Star case is debatable.
**Recommendation:** For `THEME_DEFAULTS` and `PlayerConfig.color`: move color definitions to a UI theme/assets configuration file. For `Star.color`: consider renaming to `apparent_color` and documenting it as astrophysical data rather than rendering data.
**Effort:** Medium

#### INFO: Misleading Docstring in ShipStatsCalculator
**ID:** ADR-STR-010
**Location:** `game/strategy/services/ship_stats_calculator.py:12`
**Issue:** The module docstring states "Only imports from game.core.registry (no simulation layer coupling)" but lines 25-26 directly import from `game.simulation.formula_system` and `game.simulation.components.modifiers`. The imports themselves are architecturally valid (strategy is permitted to depend on simulation), but the documentation is misleading.
**Impact:** Developers trusting the docstring may make incorrect assumptions about the module's dependency footprint
**Recommendation:** Update the docstring to accurately reflect the simulation dependency: "Imports from game.core and game.simulation (formula evaluation, modifier calculation)"
**Effort:** Simple

### Phase 6: Dependency Direction Violations

#### MAJOR: hex_to_pixel/pixel_to_hex Usage in Galaxy Data Layer
**ID:** ADR-STR-011
**Location:** `game/strategy/data/galaxy.py:5,440,461-462,478,484,622-623`
**Issue:** `Galaxy` imports `hex_to_pixel` and `pixel_to_hex` from `game.core.hex_math` and uses them extensively for warp link placement (lines 440, 461-462, 478, 484) and edge candidate filtering (lines 622-623). While these are core utilities (not pygame), the names suggest coordinate conversion for rendering. In practice, they are used as a geometric transformation for angle calculations in the strategy layer -- essentially converting hex coordinates to Cartesian for trigonometry. This is not a true layer violation but the naming creates confusion about whether pixel/rendering concerns have leaked into the strategy layer.
**Impact:** Confusing naming suggests rendering dependency; makes code review harder; new developers may assume pixel coordinates imply UI coupling
**Recommendation:** Consider adding a comment clarifying these are used for geometric calculations (angles, distances) rather than rendering. Alternatively, create a `hex_to_cartesian` alias in `hex_math` for non-rendering use cases.
**Effort:** Simple

#### INFO: DesignMetadata Contains sprite_preview Field
**ID:** ADR-STR-012
**Location:** `game/strategy/data/design_metadata.py:35`
**Issue:** `DesignMetadata` has a `sprite_preview: Optional[str]` field documented as "Base64 encoded image (future)". While currently always None, this field's purpose is to store a UI rendering artifact (a preview image) in strategy-layer metadata that gets serialized to disk.
**Impact:** Currently no impact (field is unused), but when implemented, it would embed UI-specific rendering data into strategy-layer persistent state
**Recommendation:** When this feature is implemented, store sprite previews in a separate UI cache rather than in the strategy-layer design metadata
**Effort:** Simple (preventive)

#### MINOR: EmpireEconomyCalculator Provides "Display-Ready" Data
**ID:** ADR-STR-013
**Location:** `game/strategy/engine/empire_economy_calculator.py:5,19`
**Issue:** The module docstring describes its output as "display-ready snapshot" and the `EmpireEconomySnapshot` dataclass is documented as "Display-ready snapshot of empire economic state." While the actual data is pure numeric game state (dicts of resource amounts), the "display-ready" framing suggests the strategy layer is aware of and catering to UI presentation needs.
**Impact:** Minor conceptual issue; the actual implementation is clean data without formatting. The naming/documentation creates the impression of UI awareness.
**Recommendation:** Rename or re-document as "economic state snapshot" without the "display-ready" qualifier
**Effort:** Simple

## Top 5 Priority Issues

1. **ADR-STR-008 (MAJOR): ShipDisplayFormatter in Strategy Data Layer** -- Presentation logic that explicitly acknowledges it does not belong in the data layer, yet remains there. Move to UI or facade layer.

2. **ADR-STR-003 (MAJOR): ProductionEngine God Class** -- At 701 lines, this is the largest single class and handles three distinct production pathways. Decomposition would significantly improve testability.

3. **ADR-STR-004 (MAJOR): Galaxy God Class** -- At 698 lines with generation, graph algorithms, and data access mixed together. The generation methods should be extracted.

4. **ADR-STR-005 (MAJOR): ShipInstance God Class** -- 44 methods is an extremely wide API. Continue the delegate extraction pattern already started.

5. **ADR-STR-009 (MINOR): Color Tuples in Game Configuration** -- RGB colors hardcoded in strategy-layer configuration mix visual concerns with game logic. Theme colors should come from the UI/assets layer.
