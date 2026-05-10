# DTO Coverage Analysis Report

## Summary

| Metric | Count |
|--------|-------|
| **Total issues found** | **21** |
| Critical | 3 |
| Major | 8 |
| Minor | 6 |
| Info | 4 |
| DTOs cataloged | 10 |
| Facade query methods | 20 |
| Raw domain imports in UI | 18 files |

---

## DTO Catalog

All DTOs are frozen dataclasses (immutable). Located in `game/strategy/facade/dto/`.

### fleet_dto.py

| DTO Class | Fields | Wraps | Immutable |
|-----------|--------|-------|-----------|
| `FleetOrderInfo` | `order_type: str`, `target_description: str`, `target_hex: Optional[HexCoord]`, `target_id: Optional[int]` | Fleet order objects | Yes (frozen) |
| `ShipInfo` | `instance_id: str`, `name: str`, `design_id: str`, `ship_class: str`, `is_combat_capable: bool`, `current_hp_percent: float` | ShipInstance | Yes (frozen) |
| `FleetInfo` | `fleet_id: int`, `owner_id: int`, `location: HexCoord`, `speed: float`, `ship_count: int`, `ships: Tuple[ShipInfo,...]`, `orders: Tuple[FleetOrderInfo,...]`, `has_orders: bool`, `can_use_warp: bool`, `projected_path: Tuple[HexCoord,...]`, `is_building: bool`, `has_space_shipyard: bool`, `construction_queue_size: int`, `passenger_capacity: int`, `passengers_current: int` | Fleet | Yes (frozen) |

### empire_dto.py

| DTO Class | Fields | Wraps | Immutable |
|-----------|--------|-------|-----------|
| `ColonySummary` | `planet_id: int`, `planet_name: str`, `has_shipyard: bool` | Planet (colonized) | Yes (frozen) |
| `FleetSummary` | `fleet_id: int`, `ship_count: int`, `has_orders: bool` | Fleet | Yes (frozen) |
| `EmpireInfo` | `empire_id: int`, `name: str`, `color: Tuple[int,int,int]`, `theme_id: str`, `flag_id: str`, `colony_count: int`, `fleet_count: int` | Empire | Yes (frozen) |

### system_dto.py

| DTO Class | Fields | Wraps | Immutable |
|-----------|--------|-------|-----------|
| `StarInfo` | `name: str`, `star_type: str`, `color: Tuple[int,int,int]`, `location: HexCoord` | Star | Yes (frozen) |
| `WarpPointInfo` | `destination_system_name: str`, `location: HexCoord` | WarpPoint | Yes (frozen) |
| `SystemInfo` | `name: str`, `global_location: HexCoord`, `primary_star: Optional[StarInfo]`, `planet_count: int`, `warp_point_count: int`, `colony_count: int` | StarSystem | Yes (frozen) |

### planet_dto.py

| DTO Class | Fields | Wraps | Immutable |
|-----------|--------|-------|-----------|
| `PlanetInfo` | `planet_id: int`, `name: str`, `planet_type: str`, `location: HexCoord`, `orbit_distance: int`, `owner_id: Optional[int]`, `is_colonized: bool`, `has_space_shipyard: bool`, `total_population: int`, `max_population: int`, `population_details: Tuple[Tuple[str,int,float],...]` | Planet | Yes (frozen) |

---

## Facade Query Methods

File: `game/strategy/facade/strategy_session_facade.py`

### Write Path (Commands)

| Method | Returns | Notes |
|--------|---------|-------|
| `handle_command(command)` | `ValidationResult` | Delegates to GameSession |
| `process_turn()` | `None` | Advances game state |

### Read Path (Queries)

| Method | Returns | Return Type Category |
|--------|---------|---------------------|
| `get_fleet(fleet_id)` | `Optional[FleetInfo]` | DTO |
| `get_fleets_at_hex(hex_coord)` | `List[FleetInfo]` | DTO |
| `get_fleet_path_preview(fleet_id, target_hex)` | `Optional[List[HexCoord]]` | Primitive |
| `get_fleet_path_projection(fleet_id, max_turns)` | `List[dict]` | Primitive (dicts) |
| `get_all_systems()` | `List[SystemInfo]` | DTO |
| `get_system_at_hex(hex_coord)` | `Optional[SystemInfo]` | DTO |
| `get_system_containing_fleet(fleet_id)` | `Optional[SystemInfo]` | DTO |
| `get_system_near_hex(hex_coord, max_dist)` | `Optional[SystemInfo]` | DTO |
| `get_planet(planet_id)` | `Optional[PlanetInfo]` | DTO |
| `get_planets_at_hex(hex_coord)` | `List[PlanetInfo]` | DTO |
| `get_all_empires()` | `List[EmpireInfo]` | DTO |
| `get_empire(empire_id)` | `Optional[EmpireInfo]` | DTO |
| `get_empire_colonies(empire_id)` | `List[ColonySummary]` | DTO |
| `get_empire_fleets(empire_id)` | `List[FleetSummary]` | DTO |
| `get_human_player_ids()` | `List[int]` | Primitive |
| `get_turn_number()` | `int` | Primitive |
| `get_turn_events(turn)` | `List[dict]` | Primitive (dicts) |
| `get_all_events()` | `List[dict]` | Primitive (dicts) |
| `get_events_by_category(category)` | `List[dict]` | Primitive (dicts) |
| `can_colonize(fleet_id, planet_id)` | `ValidationResult` | Primitive |
| `can_move_to(fleet_id, target_hex)` | `ValidationResult` | Primitive |
| `get_fleet_remaining_pods(fleet_id)` | `dict` | Primitive |

### Internal Helpers (leak raw domain objects)

| Method | Returns | Notes |
|--------|---------|-------|
| `_get_fleet_by_id(fleet_id)` | `Fleet` (raw) | Private, but used internally |
| `_get_empire_by_id(empire_id)` | `Empire` (raw) | Private, but used internally |
| `_get_planet_by_id(planet_id)` | `Planet` (raw) | Private, but used internally |

---

## Raw Domain Model Exposure in UI

### Direct Runtime Imports (not TYPE_CHECKING)

| File | Domain Import | Usage |
|------|--------------|-------|
| `game/ui/screens/strategy_renderer.py` | `OrderType` from `fleet` | Enum comparison for path rendering |
| `game/ui/screens/strategy_renderer.py` | `PlanetType` from `planet` | Enum for color mapping |
| `game/ui/screens/strategy_detail_fmt.py` | `OrderType` from `fleet` | Enum comparison for order display |
| `game/ui/screens/fleet_orders_window.py` | `OrderType` from `fleet` | Enum comparison for order display |
| `game/ui/screens/galaxy_test/constants.py` | `PlanetType` from `planet` | Enum for color mapping |
| `game/ui/screens/galaxy_test/system_mode.py` | `PlanetType` from `planet` | Enum for color mapping |
| `game/ui/screens/galaxy_test/galaxy_mode.py` | `Galaxy` from `galaxy` | Direct Galaxy construction for test screen |
| `game/ui/panels/race_identity_panel.py` | `RaceConfig` constants | Enum/constant access |
| `game/ui/panels/race_aptitudes_panel.py` | `RacePointBudget` | Point calculation |
| `game/ui/panels/race_environment_panel.py` | `homeworld_presets` | Data constants |
| `game/ui/panels/empire_treasury_panel.py` | `EmpireEconomySnapshot` | Runtime data import |
| `game/ui/screens/empire_panel_window.py` | `EmpireEconomyCalculator` | Runtime import for economy data |

### TYPE_CHECKING Imports (type hints only - lower concern)

| File | Domain Import | Usage |
|------|--------------|-------|
| `game/ui/screens/strategy_screen.py` | `StarSystem`, `Fleet` | Type hints |
| `game/ui/screens/strategy_build_queue_manager.py` | `Fleet` | Type hints + `isinstance` checks |
| `game/ui/screens/strategy_superweapons.py` | `Fleet` | Type hints |
| `game/ui/panels/build_queue_controller.py` | `Planet`, `Fleet`, `Galaxy`, `Empire` | Type hints |
| `game/ui/screens/build_queue_screen.py` | `Galaxy`, `Empire` | Type hints |
| `game/ui/screens/empire_build_queue_window.py` | `Empire` | Type hints |
| `game/ui/panels/ship_detail_panel.py` | `ShipInstance` | Type hints |
| `game/ui/screens/galaxy_test/system_mode.py` | `StarSystem`, `Star`, `Planet` | Type hints + construction |

### Domain Object Mutation from UI (CRITICAL)

| File | Mutation | Line(s) |
|------|----------|---------|
| `game/ui/screens/fleet_report_window.py` | `fleet.remove_ship(ship)` | 239, 245, 269 |
| `game/ui/screens/fleet_report_window.py` | `empire.add_fleet(new_fleet)` | 247, 273 |
| `game/ui/screens/fleet_report_window.py` | `new_fleet.add_ship(ship)` | 284 |
| `game/ui/screens/fleet_report_window.py` | `Fleet(...)` constructor in UI | 278-281 |
| `game/ui/screens/fleet_orders_window.py` | `fleet.orders.pop(index)` | 298 |
| `game/ui/screens/fleet_orders_window.py` | `fleet.orders.insert(index, order)` | 319 |
| `game/ui/screens/fleet_orders_window.py` | `fleet.orders[i], fleet.orders[j] = ...` swap | 287 |
| `game/ui/screens/fleet_orders_window.py` | `fleet.path = []` | 291, 302 |
| `game/ui/panels/build_queue_controller.py` | `source.construction_queue.insert(...)` | 413, 450 |
| `game/ui/panels/build_queue_controller.py` | `source.construction_queue.append(...)` | 416, 453, 491 |
| `game/ui/panels/build_queue_controller.py` | `build_context.construction_queue.insert/append(...)` | 535, 538 |
| `game/ui/screens/empire_build_queue_window.py` | `source.construction_queue.append(dict(item))` | 361 |

---

## DTO Gap Analysis

### COVERED (DTO exists, UI uses it through facade)

| Domain Concept | DTO | Facade Method | UI Consumer |
|---------------|-----|---------------|-------------|
| Fleet basic info | `FleetInfo` | `get_fleet()`, `get_fleets_at_hex()` | `strategy_fleet_ops.py` (via `fleet.id` for commands) |
| System info | `SystemInfo` | `get_all_systems()`, `get_system_at_hex()` | `strategy_colonization.py` (partial) |
| Planet info | `PlanetInfo` | `get_planet()`, `get_planets_at_hex()` | `strategy_colonization.py` (partial) |
| Empire info | `EmpireInfo` | `get_all_empires()`, `get_empire()` | (minimal direct DTO usage) |
| Event log | `List[dict]` | `get_turn_events()`, `get_all_events()` | `strategy_window_manager.py`, `event_log_window.py` |
| Colonize validation | `ValidationResult` | `can_colonize()` | `strategy_colonization.py` |
| Fleet path preview | `List[HexCoord]` | `get_fleet_path_preview()` | `strategy_fleet_ops.py` |
| Turn processing | N/A | `process_turn()` | `strategy_game_state_manager.py` |

### BYPASSED (DTO exists, but UI uses raw domain objects instead)

These are the most concerning findings. DTOs exist but the UI bypasses them to access raw domain objects.

| Domain Concept | DTO Available | Raw Access Location | What's Accessed |
|---------------|--------------|---------------------|-----------------|
| Fleet | `FleetInfo` | `strategy_screen.py:105` | `self.selected_fleet` stores raw Fleet object |
| Fleet | `FleetInfo` | `strategy_renderer.py:872-875` | Iterates `emp.fleets` directly for rendering |
| Fleet | `FleetInfo` | `strategy_fleet_ops.py:58-61` | `emp.fleets` iteration to find fleet at hex |
| Fleet | `FleetInfo` | `strategy_renderer.py:937` | `session.get_fleet_path_projection(fleet, ...)` with raw Fleet |
| Empire | `EmpireInfo` | `strategy_screen.py:139-162` | `session.empires`, `session.player_empire` etc. |
| Empire | `EmpireInfo` | `strategy_renderer.py:379` | `emp.color`, `emp.id` direct access |
| Empire | `EmpireInfo` | `strategy_window_manager.py:111,137,163,247` | `scene.current_empire` raw Empire passed to windows |
| Planet | `PlanetInfo` | `strategy_build_queue_manager.py:49` | `isinstance(selected_object, Planet)` |
| Planet | `PlanetInfo` | `strategy_colonization.py:77-78` | `start_sys.planets`, `p.location`, `p.owner_id` |
| System | `SystemInfo` | `strategy_renderer.py:259,315` | `galaxy.systems.values()` direct iteration |
| System | `SystemInfo` | `strategy_colonization.py:72,316` | `galaxy.systems.values()` direct iteration |

### MISSING (No DTO for this data, UI accesses raw domain objects)

| Domain Concept | UI Access Pattern | Files |
|---------------|-------------------|-------|
| Galaxy (full object) | `session.galaxy` exposed as property | `strategy_screen.py:136`, renderer, colonization, superweapons |
| Empire.colonies list | `empire.colonies` iterated for camera centering | `strategy_game_state_manager.py:55,88` |
| Empire.fleets list | `empire.fleets` iterated for rendering | `strategy_renderer.py:872`, `strategy_fleet_ops.py:58` |
| Empire.resource_pool | `empire.resource_pool` for treasury display | `empire_panel_window.py` |
| Empire.race_config | `empire.race_config` for population display | `empire_panel_window.py` |
| Fleet.capabilities | `fleet.capabilities.has_ability(...)` | `strategy_superweapons.py:76,132,178,234,278,323` |
| Fleet.construction_queue (full list) | Direct list read/write | `build_queue_controller.py`, `fleet_orders_window.py:194` |
| Fleet.orders (mutable list) | Direct list read/write/reorder | `fleet_orders_window.py:284-319` |
| Fleet.ships (mutable list) | Direct list read/mutate | `fleet_report_window.py:239-284` |
| Fleet.is_building property | Direct access | `strategy_fleet_ops.py:83` |
| ShipInstance (full object) | Passed to `ShipDetailPanel` | `ship_detail_panel.py` |
| Star (full object) | `star.color`, `star.location`, `star.diameter_hexes` | `strategy_renderer.py:402-429` |
| StarSystem (full object) | `.planets`, `.warp_points`, `.stars`, `.global_location` | `strategy_renderer.py:306-336` |
| WarpPoint.destination_id | Direct property access | `strategy_superweapons.py:195,248` |
| OrderType enum | Runtime import for display/comparison | `strategy_renderer.py`, `fleet_orders_window.py`, `strategy_detail_fmt.py` |
| PlanetType enum | Runtime import for color mapping | `strategy_renderer.py`, `galaxy_test/constants.py` |

---

## Findings

### CRITICAL-1: UI Directly Mutates Fleet Domain Object (Ship Removal)

**ID:** DCA-001
**Location:** `game/ui/screens/fleet_report_window.py:235-286`
**Issue:** FleetReportWindow directly calls `fleet.remove_ship(ship)`, `empire.add_fleet(new_fleet)`, and constructs new `Fleet(...)` objects. The UI creates and mutates domain objects without going through any command pipeline or facade.
**Impact:** Violates CQRS pattern. State mutations bypass validation, event logging, and undo support. Can cause state inconsistencies if the session has integrity constraints.
**Recommendation:** Create commands: `SplitFleetCommand(fleet_id, ship_instance_ids)` and route through `facade.handle_command()`. The UI should only receive read-only fleet data.
**Effort:** Medium

### CRITICAL-2: UI Directly Mutates Fleet Orders (Reorder/Delete/Insert)

**ID:** DCA-002
**Location:** `game/ui/screens/fleet_orders_window.py:281-319`
**Issue:** FleetOrdersWindow directly mutates `fleet.orders` list via `pop()`, `insert()`, and index swap. It also directly sets `fleet.path = []`. These are uncontrolled state mutations from the UI layer.
**Impact:** Bypasses command pipeline, validation, and event logging. Order manipulation has no undo support via the command system. Direct `fleet.path = []` is a write to internal navigation state.
**Recommendation:** Create commands: `ReorderFleetOrderCommand`, `DeleteFleetOrderCommand`, `UndoDeleteFleetOrderCommand`. Route through facade.
**Effort:** Medium

### CRITICAL-3: UI Directly Mutates Construction Queues

**ID:** DCA-003
**Location:** `game/ui/panels/build_queue_controller.py:413-538`, `game/ui/screens/empire_build_queue_window.py:361`
**Issue:** BuildQueueController and EmpireBuildQueueWindow directly append/insert items into `source.construction_queue` and `build_context.construction_queue`. These are uncontrolled state mutations from the UI layer.
**Impact:** Bypasses command pipeline for queue additions. No validation, no event logging, no undo support. Inconsistent with the CQRS-lite pattern established by the facade.
**Recommendation:** Create commands: `AddToConstructionQueueCommand(source_id, item, index)`. Route through facade.
**Effort:** Medium

---

### MAJOR-1: StrategyScreen Exposes Raw Session Properties to All Sub-Modules

**ID:** DCA-004
**Location:** `game/ui/screens/strategy_screen.py:134-162`
**Issue:** StrategyScreen exposes raw domain objects via properties: `galaxy`, `empires`, `systems`, `player_empire`, `enemy_empire`. Every sub-module (renderer, fleet_ops, colonization, superweapons, camera_nav, game_state_manager, build_queue_manager) accesses these raw domain objects through `self.scene.galaxy`, `self.scene.empires`, etc.
**Impact:** This is the root cause of most bypass findings. The entire UI layer has unrestricted read access to mutable domain objects. Any sub-module can read or (accidentally) mutate game state without facade mediation.
**Recommendation:** Remove raw property accessors. Sub-modules should receive the facade and use DTO query methods instead. This is a large refactor affecting 10+ files.
**Effort:** Complex

### MAJOR-2: Renderer Directly Iterates Galaxy, Systems, Planets, Fleets

**ID:** DCA-005
**Location:** `game/ui/screens/strategy_renderer.py:259-930`
**Issue:** StrategyRenderer directly accesses `galaxy.systems.values()`, iterates `sys.planets`, `sys.warp_points`, `sys.stars`, and `emp.fleets` for rendering. It reads properties like `star.color`, `star.diameter_hexes`, `planet.owner_id`, `fleet.location`, `fleet.orders`, `emp.color`.
**Impact:** The renderer bypasses all DTOs and reads raw domain objects extensively. SystemInfo, PlanetInfo, FleetInfo, StarInfo DTOs all exist but are unused by the renderer. Performance concern: converting to DTOs per frame may be expensive, but the architecture violation is significant.
**Recommendation:** For the renderer, consider a "render snapshot" DTO or view-model that pre-computes all rendering data once per frame, rather than converting individual entities. Alternatively, accept the renderer as a special case with read-only access via protocols.
**Effort:** Complex

### MAJOR-3: Colonization System Accesses Raw Galaxy/Systems/Planets

**ID:** DCA-006
**Location:** `game/ui/screens/strategy_colonization.py:72-94, 189-200, 291-319`
**Issue:** ColonizationSystem directly iterates `galaxy.systems.values()`, accesses `start_sys.planets`, `p.location`, `p.owner_id`, `p.planet_type.name`. Despite the facade having `can_colonize()` and `get_planets_at_hex()`, the colonization module does its own planet discovery by iterating raw domain objects.
**Impact:** DTOs exist but are bypassed. The module reads planet properties that are available in PlanetInfo DTO but goes directly to domain objects instead.
**Recommendation:** Use `facade.get_planets_at_hex()` for planet discovery. Add a `get_colonizable_planets(fleet_id)` query to the facade that returns filtered PlanetInfo DTOs.
**Effort:** Medium

### MAJOR-4: Superweapon Operations Accesses Raw Galaxy/Fleet Capabilities

**ID:** DCA-007
**Location:** `game/ui/screens/strategy_superweapons.py:76-339`
**Issue:** SuperweaponOperations accesses `fleet.capabilities.has_ability(...)`, `fleet.capabilities.ships_with_ability(...)`, `galaxy.systems.values()`, `system.warp_points`, `wp.destination_id` directly. None of these are available through DTOs.
**Impact:** Fleet capability checks have no DTO coverage. The `FleetInfo` DTO has no `capabilities` field, so UI code must access raw Fleet objects for ability checks.
**Recommendation:** Add `capabilities: Tuple[str,...]` to FleetInfo listing available ability names. Add a facade query `get_fleet_capabilities(fleet_id) -> dict` for detailed ability info.
**Effort:** Medium

### MAJOR-5: Build Queue Manager Uses isinstance on Raw Domain Objects

**ID:** DCA-008
**Location:** `game/ui/screens/strategy_build_queue_manager.py:48-49, 210-211`
**Issue:** Uses `isinstance(selected_object, Planet)` and `isinstance(selected_object, Fleet)` for type discrimination, importing the domain classes to do so. This couples UI to concrete domain types.
**Impact:** Violates layer separation. The UI should use protocol type guards (already available: `is_planet()`, `is_fleet()`) or DTO type discrimination.
**Recommendation:** Replace `isinstance(selected_object, Planet)` with `is_planet(selected_object)` protocol checks (already used elsewhere in the codebase, e.g., `strategy_screen.py` uses `is_planet`, `is_fleet`).
**Effort:** Simple

### MAJOR-6: Build Queue Screen Receives Raw Galaxy and Empire Objects

**ID:** DCA-009
**Location:** `game/ui/screens/build_queue_screen.py:59-61`, `strategy_build_queue_manager.py:82-84,197-199,243-245`
**Issue:** BuildQueueScreen constructor receives raw `Galaxy` and `Empire` domain objects and stores them as instance attributes. These are then passed to `collect_build_queues_at_hex()` which further accesses raw domain internals.
**Impact:** Raw mutable domain objects are propagated deep into UI component trees. Changes to Galaxy or Empire structure would ripple through UI code.
**Recommendation:** The build queue system needs its own facade method to collect queue sources, returning DTOs. e.g., `facade.get_build_queue_sources(hex_coord, empire_id)`.
**Effort:** Complex

### MAJOR-7: Fleet Operations Gets Fleet at Hex by Iterating Raw Empires/Fleets

**ID:** DCA-010
**Location:** `game/ui/screens/strategy_fleet_ops.py:48-62`
**Issue:** `FleetOperations.get_fleet_at_hex()` iterates through `self.empires` -> `emp.fleets` to find a fleet at a hex coordinate. The facade already has `get_fleets_at_hex()` which returns FleetInfo DTOs.
**Impact:** Completely bypasses the facade's `get_fleets_at_hex()` query. Returns raw Fleet domain objects instead of FleetInfo DTOs.
**Recommendation:** Use `self.facade.get_fleets_at_hex(hex_coord)` and work with FleetInfo DTOs. Note: some callers need the raw Fleet for command dispatch -- those should use fleet_id from the DTO.
**Effort:** Simple

### MAJOR-8: Game State Manager Accesses Raw Session and Turn Engine

**ID:** DCA-011
**Location:** `game/ui/screens/strategy_game_state_manager.py:77,110`
**Issue:** Accesses `session.save_path` and `session.turn_engine` directly. The turn_engine is then used to read `last_scuttle_events` -- a property not exposed through any DTO or facade method.
**Impact:** Bypasses facade for game state queries. Scuttle events have no facade exposure at all.
**Recommendation:** Add `facade.get_save_path() -> str` and `facade.get_scuttle_events(turn) -> List[dict]` to the facade.
**Effort:** Simple

---

### MINOR-1: FleetInfo DTO Missing Capabilities Field

**ID:** DCA-012
**Location:** `game/strategy/facade/dto/fleet_dto.py`
**Issue:** FleetInfo has no `capabilities` or `available_abilities` field. UI must access raw Fleet to check `fleet.capabilities.has_ability("DestroyPlanet")`.
**Impact:** Forces superweapon UI to bypass DTOs for capability checks. 6 separate ability checks in `strategy_superweapons.py`.
**Recommendation:** Add `capabilities: Tuple[str,...] = field(default_factory=tuple)` to FleetInfo, populated from `fleet.capabilities.list_abilities()`.
**Effort:** Simple

### MINOR-2: SystemInfo DTO Missing Stars, Planets, and WarpPoints Detail Lists

**ID:** DCA-013
**Location:** `game/strategy/facade/dto/system_dto.py`
**Issue:** SystemInfo only has `planet_count`, `warp_point_count`, and `primary_star`. It lacks detailed lists of stars, planets, and warp points. The renderer needs to iterate `sys.stars`, `sys.planets`, `sys.warp_points` for drawing.
**Impact:** Renderer must bypass SystemInfo DTO entirely, accessing raw StarSystem domain objects for all detail rendering.
**Recommendation:** Add `stars: Tuple[StarInfo,...]`, `planets: Tuple[PlanetInfo,...]`, `warp_points: Tuple[WarpPointInfo,...]` to SystemInfo. Consider performance -- this could be a separate "SystemDetailInfo" DTO.
**Effort:** Medium

### MINOR-3: EmpireInfo DTO Missing Resource Pool, Race Config, Treasury Data

**ID:** DCA-014
**Location:** `game/strategy/facade/dto/empire_dto.py`
**Issue:** EmpireInfo lacks resource pool, race config, and treasury information. The EmpirePanelWindow imports `EmpireEconomyCalculator` at runtime and accesses `empire.resource_pool`, `empire.race_config` directly.
**Impact:** Empire panel window cannot use DTOs for economic or population display, forcing raw domain access.
**Recommendation:** Create `EmpireTreasuryInfo` DTO or add `resource_pool: dict`, `race_name: str` to EmpireInfo. Add facade query `get_empire_treasury(empire_id) -> EmpireTreasuryInfo`.
**Effort:** Medium

### MINOR-4: PlanetInfo DTO Missing Production, Facilities, and Resources Data

**ID:** DCA-015
**Location:** `game/strategy/facade/dto/planet_dto.py`
**Issue:** PlanetInfo lacks production rates, facilities, surface resources, atmosphere, and environment data. UI `strategy_detail_fmt.py` accesses raw planet properties extensively for detail display.
**Impact:** Planet detail formatting must use raw domain objects. The `format_atmosphere_raw()` function and production calculations access planet internals directly.
**Recommendation:** Consider a `PlanetDetailInfo` DTO with production, facility, and environment data for the detail panel. Keep `PlanetInfo` lightweight for list views.
**Effort:** Medium

### MINOR-5: No ShipInstance DTO

**ID:** DCA-016
**Location:** `game/ui/panels/ship_detail_panel.py`
**Issue:** ShipDetailPanel receives raw `ShipInstance` domain objects. No DTO exists for individual ship instances with component-level damage data.
**Impact:** Ship detail display requires raw domain object access. The `ShipInfo` DTO in fleet_dto.py is too lightweight (only 6 fields) to replace full ShipInstance access.
**Recommendation:** Create `ShipDetailInfo` DTO with component damage, layer HP, design stats for ship detail panel.
**Effort:** Medium

### MINOR-6: WarpPointInfo DTO Missing destination_id Field

**ID:** DCA-017
**Location:** `game/strategy/facade/dto/system_dto.py`
**Issue:** WarpPointInfo has `destination_system_name` but not `destination_id`. The `strategy_superweapons.py` accesses `wp.destination_id` for warp point operations.
**Impact:** Minor inconsistency -- the field exists under a different name. But the DTO is also never included in SystemInfo, so it's unused.
**Recommendation:** Align field naming and include WarpPointInfo in SystemInfo detail DTOs.
**Effort:** Simple

---

### INFO-1: OrderType Enum Used Directly in UI

**ID:** DCA-018
**Location:** `game/ui/screens/strategy_renderer.py:17`, `fleet_orders_window.py:18`, `strategy_detail_fmt.py:16`
**Issue:** `OrderType` enum is imported at runtime in 3 UI files for display/comparison logic. This is a lightweight enum dependency, not a full domain object.
**Impact:** Low risk. Enums are value types and inherently immutable. However, it couples UI to strategy layer enum definitions.
**Recommendation:** Acceptable as-is. Alternatively, use string comparisons against order type names (already done in FleetOrderInfo DTO's `order_type: str`).
**Effort:** Simple

### INFO-2: PlanetType Enum Used Directly in UI

**ID:** DCA-019
**Location:** `game/ui/screens/strategy_renderer.py:18`, `galaxy_test/constants.py:6`, `galaxy_test/system_mode.py:19`
**Issue:** `PlanetType` enum imported for color mapping in renderer and test screen. Lightweight enum dependency.
**Impact:** Low risk. The PlanetInfo DTO already converts planet type to string, but the renderer needs the enum for color lookup in the `PLANET_TYPE_COLORS` dict.
**Recommendation:** Acceptable as-is. Could create a `get_planet_color(planet_type_name: str)` utility in UI layer.
**Effort:** Simple

### INFO-3: Galaxy Test Screen Uses Raw Domain Objects Extensively

**ID:** DCA-020
**Location:** `game/ui/screens/galaxy_test/galaxy_mode.py`, `system_mode.py`
**Issue:** The galaxy test screen directly constructs `Galaxy` objects, `StarSystem` objects, `Star` objects, and `Planet` objects for testing/visualization purposes.
**Impact:** Low risk. This is a developer test/debug screen, not a gameplay UI. It legitimately needs to construct domain objects for testing.
**Recommendation:** Acceptable as-is. Consider marking these files as "dev tools" with a comment.
**Effort:** N/A

### INFO-4: Race Config Panels Use Domain Data Directly

**ID:** DCA-021
**Location:** `game/ui/panels/race_identity_panel.py`, `race_aptitudes_panel.py`, `race_environment_panel.py`, etc.
**Issue:** Race configuration panels import `RaceConfig`, `RacePointBudget`, and `homeworld_presets` directly. These are used in the game setup screen for race creation.
**Impact:** Low risk. Race configuration is an input form, not a read-only display of game state. The data flows from UI to domain, which is the opposite of the DTO read concern.
**Recommendation:** Acceptable as-is for setup/creation screens. DTOs are designed for game state reads, not creation forms.
**Effort:** N/A

---

## Recommended DTO Enhancements

### 1. Add to FleetInfo DTO
```python
capabilities: Tuple[str, ...] = field(default_factory=tuple)  # Ability names
```
This would eliminate 6 raw Fleet accesses in `strategy_superweapons.py`.

### 2. Create SystemDetailInfo DTO (or expand SystemInfo)
```python
@dataclass(frozen=True)
class SystemDetailInfo:
    name: str
    global_location: HexCoord
    stars: Tuple[StarInfo, ...]
    planets: Tuple[PlanetInfo, ...]
    warp_points: Tuple[WarpPointInfo, ...]
    # ... other fields
```
This would serve the renderer's needs for system detail rendering.

### 3. Create EmpireTreasuryInfo DTO
```python
@dataclass(frozen=True)
class EmpireTreasuryInfo:
    empire_id: int
    resource_pool: Dict[str, float]
    production_rates: Dict[str, float]
    expenses: Dict[str, float]
```
With facade method: `get_empire_treasury(empire_id) -> Optional[EmpireTreasuryInfo]`

### 4. Create ShipDetailInfo DTO
```python
@dataclass(frozen=True)
class ShipDetailInfo:
    instance_id: str
    name: str
    design_id: str
    design_data: dict
    hp_current: float
    hp_max: float
    layer_damage: Tuple[LayerDamageInfo, ...]
    cargo_contents: Dict[str, int]
```
This would replace raw ShipInstance access in ship_detail_panel.py.

### 5. Add Facade Methods
- `get_scuttle_events(turn) -> List[dict]`
- `get_save_path() -> Optional[str]`
- `get_colonizable_planets(fleet_id) -> List[PlanetInfo]`
- `get_fleet_capabilities(fleet_id) -> List[str]`
- `get_build_queue_sources(hex_coord, empire_id) -> List[BuildQueueSourceInfo]`
- `get_empire_treasury(empire_id) -> EmpireTreasuryInfo`

### 6. Create Fleet Mutation Commands
- `SplitFleetCommand(fleet_id, ship_instance_ids)`
- `ReorderFleetOrderCommand(fleet_id, from_index, to_index)`
- `DeleteFleetOrderCommand(fleet_id, order_index)`
- `AddToConstructionQueueCommand(entity_id, entity_type, item, index)`

---

## Top 5 Priority Issues

1. **DCA-001 (CRITICAL):** Fleet Report Window directly mutates Fleet and Empire domain objects (ship removal, fleet creation). This is the most egregious violation -- the UI constructs domain objects and mutates state without any command pipeline.

2. **DCA-002 (CRITICAL):** Fleet Orders Window directly manipulates `fleet.orders` list (pop, insert, swap) and writes to `fleet.path`. Uncontrolled state mutation from UI with no validation.

3. **DCA-003 (CRITICAL):** Build Queue Controller directly mutates `construction_queue` lists. Multiple UI files append/insert to domain object queues without going through commands.

4. **DCA-004 (MAJOR):** StrategyScreen exposes raw domain properties (`galaxy`, `empires`, etc.) to all sub-modules. This is the systemic root cause -- fixing this would cascade fixes to many bypass issues.

5. **DCA-010 (MAJOR):** FleetOperations.get_fleet_at_hex() iterates raw empires/fleets when `facade.get_fleets_at_hex()` already exists. Low-hanging fruit that demonstrates the bypass pattern -- the facade method exists but is ignored.
