# Validation Report: Validator 3

## Summary
- **Findings Reviewed:** 21
- **Confirmed:** 14
- **Downgraded:** 5
- **Rejected:** 2
- **Rejection Rate:** 9.5%

## Verdicts

#### Finding: DCA-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:239-284`. The UI directly calls `fleet.remove_ship(ship)`, constructs `Fleet(...)` domain objects (line 281), and calls `empire.add_fleet(new_fleet)`. These are unmediated domain mutations from the UI layer with no command pipeline involvement.

#### Finding: DCA-002
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:281-328`. The UI directly swaps `orders[index], orders[new_index]` (line 287), calls `orders.pop(index)` (line 298), `orders.insert(original_index, order)` (line 319), and writes `fleet.path = []` (lines 291, 302, 323). All are direct domain state mutations from the UI.

#### Finding: DCA-003
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `build_queue_controller.py:413,416,450,453,491,535,538` and `empire_build_queue_window.py:361`. Multiple methods directly call `source.construction_queue.insert()` and `source.construction_queue.append()` from the UI layer. No command pipeline is used for these mutations.

#### Finding: DCA-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_screen.py:134-162`. Properties `galaxy`, `empires`, `systems`, `player_empire`, `enemy_empire` all delegate directly to `self.session.*`, exposing raw mutable domain objects to all sub-modules. The comment at line 131 acknowledges this is for "internal convenience" and "external callers should use the facade," but every sub-module accesses these properties freely.

#### Finding: DCA-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_renderer.py:259,315,329,374,402-429,872-933,937`. The renderer directly iterates `galaxy.systems.values()`, accesses `sys.planets`, `sys.warp_points`, `sys.stars`, `emp.fleets`, `star.color`, `star.diameter_hexes`, `emp.color`, and calls `session.get_fleet_path_projection(fleet, ...)` bypassing the facade (which takes `fleet_id`, not a raw Fleet). This is the most extensive bypass in the codebase.

#### Finding: DCA-006
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_colonization.py:72-94,189-200,291-319`. The module directly iterates `start_sys.planets`, accesses `p.location`, `p.owner_id`, `p.planet_type.name`, and iterates `galaxy.systems.values()` for planet resolution. The facade's `get_planets_at_hex()` and `can_colonize()` exist but are only partially used (validation only, not discovery).

#### Finding: DCA-007
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_superweapons.py:76,132,178,234,278,323`. Six distinct `fleet.capabilities.has_ability(...)` calls and one `fleet.capabilities.ships_with_ability(...)` call at line 323. Also accesses `galaxy.systems.values()` (line 192) and `wp.destination_id` (lines 248, 251, 258). FleetInfo DTO has no `capabilities` field, forcing raw access.

#### Finding: DCA-008
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_build_queue_manager.py:48-49,210-211`. Uses `isinstance(selected_object, Planet)` and `isinstance(selected_object, Fleet)` with runtime imports of domain classes. The codebase already has `is_planet()` and `is_fleet()` protocol checks available (imported in other files like `fleet_orders_window.py:17`), making this a straightforward fix.

#### Finding: DCA-009
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `build_queue_screen.py:59-61`. Constructor accepts raw `Galaxy` and `Empire` domain objects as parameters. Confirmed at `strategy_build_queue_manager.py:82-84,197-199,243-245` where `galaxy=self._screen.session.galaxy` and `empire=self._screen.current_empire` are passed directly. Raw mutable domain objects propagate into the build queue UI tree.

#### Finding: DCA-010
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_fleet_ops.py:48-62`. `get_fleet_at_hex()` iterates `emp.fleets` for all empires to find a fleet at a hex. The facade already provides `get_fleets_at_hex(hex_coord)` returning `List[FleetInfo]`. This is a clear bypass of an existing facade method.

#### Finding: DCA-011
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified at `strategy_game_state_manager.py:77,110`. The `session.save_path` access (line 77) is a simple string property read, and `session.turn_engine.last_scuttle_events` (line 110) is a read-only access for post-turn notification display. While these bypass the facade, they are read-only accesses to simple data, not mutable domain state. The missing facade methods are a legitimate gap, but the severity does not rise to Major since no mutation or complex domain traversal occurs.

#### Finding: DCA-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified by reading `fleet_dto.py`. FleetInfo has no `capabilities` field. The `strategy_superweapons.py` file makes 6 separate `fleet.capabilities.has_ability()` calls and 1 `ships_with_ability()` call that cannot be served by the DTO. Adding a capabilities tuple to FleetInfo is a straightforward enhancement.

#### Finding: DCA-013
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified by reading `system_dto.py`. SystemInfo only contains `planet_count`, `warp_point_count`, and `primary_star`. It lacks `stars`, `planets`, and `warp_points` detail lists. The renderer at `strategy_renderer.py:329,334-335` iterates `sys.stars`, `sys.planets`, and `sys.warp_points` extensively, none of which are available via SystemInfo DTO.

#### Finding: DCA-014
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified by reading `empire_dto.py`. EmpireInfo has no resource pool, race config, or treasury fields. The `empire_panel_window.py:19` imports `EmpireEconomyCalculator` at runtime, and `empire_treasury_panel.py:17` imports `EmpireEconomySnapshot` at runtime. Both access empire internals that the EmpireInfo DTO cannot provide.

#### Finding: DCA-015
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Verified by reading `planet_dto.py`. PlanetInfo indeed lacks production, facilities, surface resources, atmosphere, and environment data. However, the finding references `strategy_detail_fmt.py` as the consumer, which is a display formatting utility. The claim that this is a gap is accurate, but at this stage of facade adoption, it is more of an observation about future DTO expansion than an actionable issue. Many planet detail properties would need to be enumerated to create a useful PlanetDetailInfo, and the detail formatter accesses dozens of properties.

#### Finding: DCA-016
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Verified that `ship_detail_panel.py` imports `ShipInstance` under `TYPE_CHECKING` only (line 23) and receives ship instances for display. However, `ShipInstance` is a complex object with layer-level damage, component states, and design data. Creating a DTO that covers all of this is a substantial design effort. This is more of a future architecture observation than an actionable Minor finding.

#### Finding: DCA-017
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified by reading `system_dto.py:49-59`. WarpPointInfo has `destination_system_name` but not `destination_id`. In `strategy_superweapons.py:248,251,258`, the code accesses `warp_point.destination_id` directly. Additionally, WarpPointInfo is never included in SystemInfo, so it is effectively unused. The field name mismatch (`destination_system_name` vs. `destination_id`) suggests incomplete DTO design.

#### Finding: DCA-018
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_renderer.py:17`, `fleet_orders_window.py:18`, and `strategy_detail_fmt.py:16`. All three files import `OrderType` enum at runtime from `game.strategy.data.fleet`. This is a lightweight enum dependency -- enums are immutable value types. Info severity is appropriate.

#### Finding: DCA-019
**Original Severity:** Info
**Verdict:** DOWNGRADED(Info)
**Reason:** Verified at `strategy_renderer.py:18`, `galaxy_test/constants.py:6`, and `galaxy_test/system_mode.py:19`. PlanetType enum is imported at runtime. Two of the three locations are in the galaxy_test dev tool screen, which per instructions should be treated as Info. The severity was already Info, so this is effectively confirmed at Info. However, the galaxy_test files should be noted as dev tools where this is fully acceptable.

#### Finding: DCA-020
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** The finding accurately describes that galaxy_test files construct raw domain objects, but it already correctly identifies this as a developer test/debug screen where this is legitimate. The finding itself concludes "Acceptable as-is" and assigns no recommended effort. This is not an issue -- it is expected behavior for a test harness. Reporting a non-issue as a finding, even at Info level, adds noise to the report.

#### Finding: DCA-021
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** The finding accurately describes that race config panels import domain data directly, but it already correctly identifies these as creation forms where DTOs do not apply. The finding itself concludes "Acceptable as-is" and assigns no recommended effort. Like DCA-020, this is not an issue but rather an expected pattern for input forms. Reporting a non-issue as a finding adds noise.
