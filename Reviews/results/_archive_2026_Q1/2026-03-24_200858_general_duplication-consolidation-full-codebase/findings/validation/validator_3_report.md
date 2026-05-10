# Validation Report: Validator 3

## Summary
- **Findings Reviewed:** 28
- **Confirmed:** 14
- **Downgraded:** 8
- **Rejected:** 6
- **Rejection Rate:** 21.4%

## Verdicts

#### Finding: DUP-SD-02
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `register_planet` and `restore_planet` in `galaxy_entity_registry.py` share 4 identical lines (ID registry, reverse lookup, spatial index, zone registration). The only difference is that `register_planet` assigns a new ID while `restore_planet` preserves the existing one. A shared helper with a `assign_id` flag would eliminate the duplication.

#### Finding: DUP-SD-03
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The hex deserialization error handling pattern (`try: hex_from_dict(...) except (KeyError, TypeError): raise PersistenceException(...)`) is repeated in `Planet.from_dict`, `Star.from_dict`, `Storm.from_dict`, `WarpPoint.from_dict`, and `Galaxy.from_dict`. However, each has entity-specific context strings (source, field name). This is a standard serialization error-wrapping pattern that is idiomatic and each site is only ~8 lines. A shared utility would add complexity for marginal gain. Minor at best.

#### Finding: DUP-SD-04
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** `load_cargo_to_fleet` and `unload_cargo_from_fleet` in `FleetResourceAggregator` are NOT duplicates. They perform opposite operations (load vs unload) and delegate to different ship methods (`ship.load_cargo` vs `ship.unload_cargo`). The structural similarity (loop over ships, track remaining) is inherent to any distribute-across-ships algorithm. Consolidating them into one function would require a direction parameter, hurting readability for no real gain.

#### Finding: DUP-SD-05
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** `StarGenerator._generate_mass` generates STAR masses (solar masses, 0.1-100.0, log-normal distribution) while `PlanetGenerator._generate_mass_constrained` generates PLANET masses (kg, Ceres to Jupiter, Gaussian in log space with bias support). These operate in completely different domains with different units, distributions, parameters, and constraints. They are not duplicates.

#### Finding: DUP-SD-06
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `PlanetGenerator._generate_mass` (lines 406-428 in `planet_gen.py`) is an older method that duplicates the logic of `_generate_mass_constrained` (lines 197-240). Both generate planet masses in log space. `_generate_mass` uses a hardcoded `gauss(24.5, 1.5)` while `_generate_mass_constrained` has parameterized bias. `_generate_mass` appears to be dead code -- `_generate_orbital_slots` calls `_generate_mass_constrained`, and `_generate_moons` calls `_generate_moon_mass`. The old method should be deleted.

#### Finding: DUP-SD-07
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** The `to_dict`/`from_dict` serialization methods across `Planet`, `Star`, `Storm`, `Spectrum`, `WarpPoint`, `StarSystem`, and `Galaxy` each serialize entity-specific fields. There is no structural duplication beyond the method naming convention. Each class serializes its own unique fields. This is standard Python serialization practice, not actionable duplication.

#### Finding: DUP-SD-08
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** `Planet.can_build_type` and `FleetCapabilityCalculator.can_build_type` handle fundamentally different contexts. Planet: complexes always buildable, ships need shipyard. Fleet: needs shipyard for everything, complexes additionally need planet proximity. The logic is inverted -- they are NOT duplicates, they are context-specific implementations of the same interface.

#### Finding: DUP-SD-09
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Both `Star.occupied_hexes` and `Planet.occupied_hexes` compute `hex_circle_filled(self.location, max(0, self.radius_hexes - 1))`. The implementation is identical. This could be shared via a mixin or base class implementing the `IZoneOccupant` protocol. Minor since it is only 2 lines per property.

#### Finding: DUP-SD-10
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `_facility_is_shipyard` in `build_queue_source.py` is literally `return facility.is_shipyard` -- a one-line wrapper that adds no logic. Call sites could use `facility.is_shipyard` directly. However, it serves as a module-level function for filtering contexts. Technically a valid finding but extremely minor.

#### Finding: DUP-SE-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `_setup_mission_move` in `superweapon_command_handlers.py` and `add_move_order_if_needed` in `command_handlers.py` both calculate chain-aware start hex, find path via `find_hybrid_path`, queue a MOVE order, and set path if first order. They are structurally near-identical. The superweapon version checks only the last order for MOVE, while the command_handlers version iterates in reverse (slightly more robust). This is genuine duplication that should be consolidated.

#### Finding: DUP-SE-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** In `conflict_resolution_engine.py`, both `_resolve_combat` (RNG fallback, lines 206-231) and `_resolve_combat_simulated` (lines 283-306) contain nearly identical event logging: system name lookup, storm name extraction, and `log_event(EventType.COMBAT_RESOLVED, ...)` with the same fields. This is clear duplication that should be extracted to a shared helper.

#### Finding: DUP-SE-003
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `_spawn_complex` and `_spawn_fleet_complex` in `production_engine.py` both load design data via `DesignLibrary`, create a `PlanetaryFacility` with `uuid.uuid4()`, append to planet facilities, compute system_name/local_hex for event logging, and log `COMPLEX_BUILT`. The fleet version has extra logic for finding the planet at fleet location, but the core facility-creation and event-logging is duplicated.

#### Finding: DUP-SE-004
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `_spawn_ship` and `_spawn_fleet_ship` in `production_engine.py` share: load design data via `DesignLibrary`, create `ShipInstance.create(...)` with same parameters, `increment_built_count`, and log `SHIP_BUILT` event. The planet version creates a new fleet while the fleet version adds to existing fleet, but the design loading and ship creation is duplicated.

#### Finding: DUP-SE-005
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** The "for empire in empires: for fleet/colony in empire.X" iteration pattern is a fundamental data access pattern, not actionable duplication. Each engine (movement, production, conflict) iterates to perform different operations. Abstracting this would create an over-engineered visitor pattern with no real benefit.

#### Finding: DUP-SE-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `process_join_fleet` (line 79-131) and `process_instant_orders` (line 656-704) both contain fleet merge logic: `fleet.merge_with(target_fleet)`, `empire.remove_fleet(fleet)`, and `log_event(EventType.FLEET_JOINED, ...)` with identical fields. The merge+event code is duplicated across both methods.

#### Finding: DUP-SE-007
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** The "registries resolution pattern" refers to `GameSession.__init__` and `GameSession.from_dict` both constructing `GameRegistries(...)` and `TurnEngine(registries=...)`. This is standard initialization in constructor vs factory method. The factory method MUST reconstruct these objects from saved state. This is not actionable duplication.

#### Finding: DUP-SE-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `session.turn_engine._registries.components` appears 11 times across `superweapon_command_handlers.py` and `command_handlers.py`. This accesses an internal attribute through a chain of private members. A convenience property like `session.component_registry` would reduce coupling and the repetition.

#### Finding: DUP-SE-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `process_end_turn_orders` in `fleet_order_processor.py` (line 645-654) is explicitly a backward compatibility alias for `execute_action_order`, with a docstring marking it as deprecated. It is only called from `game/strategy/interfaces/engines.py`. Per the project's System Migration Policy, this should be eradicated and callers updated.

#### Finding: DUP-SS-01
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** `CargoTransferService.get_load_items` and `get_inventory_items` both extract population from `PlanetInfo` objects with similar logic (check `population_details`, fallback to `total_population`). However, they operate on different data sources (facade-mediated list of colonies vs single PlanetInfo/FleetInfo). `get_inventory_items` also handles FleetInfo which `get_load_items` does not. The overlap is partial and the methods serve different UI contexts (quick dialog vs transfer dialog).

#### Finding: DUP-SS-02
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The "repetitive ability-check pattern" in `SuperweaponValidator` refers to each validation method calling `find_ship_with_ability(fleet, "AbilityName", registry)` with different ability names. This is parameterized dispatch, not duplication. Each method validates different business rules (location checks, star presence, etc.). The only shared part is the ability check, which is already delegated to `find_ship_with_ability`. The validation logic after the check differs per superweapon.

#### Finding: DUP-SS-03
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** `component_inspector.py` has a single `iterate_design_components` function used by `ship_has_ability`, `find_ship_with_ability`, `count_ability`, and `list_ship_abilities`. These are all distinct utility functions calling the same shared iterator. There is no "two component iteration implementations" -- the iterator is already consolidated. The claim appears to be false.

#### Finding: DUP-SS-04
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** `race_library._slugify` and `design_library._sanitize_design_id` both convert names to safe filenames, but they use completely different algorithms. `_slugify` uses regex for lowercase+underscore, while `_sanitize_design_id` uses character filtering keeping spaces/hyphens then replacing spaces with underscores. They also have different requirements (race IDs vs design filenames). The similarity is superficial.

#### Finding: DUP-SS-05
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The density primitives in `game/strategy/generation/density/primitives/` do NOT inline hex axial distance. They all use `hex_axial_to_cartesian` from `game.core.hex_math` to convert to Cartesian coordinates and then compute Euclidean distance (`math.sqrt(x*x + y*y)`). This is Cartesian distance for continuous density calculations, not hex axial distance. The claim is factually incorrect.

#### Finding: DUP-SS-06
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** `SystemBlueprintsLoader`, `GalaxyLayoutsLoader`, and `AstrophysicsLoader` share a structural pattern of "load JSON from file, parse, return data". This is the standard data loader pattern. Each loader parses different schemas with different validation. Abstracting to a shared base would save minimal lines and reduce clarity. This is design pattern usage, not duplication.

#### Finding: DUP-UIW-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `DesignReportPanel._update_portrait` and `BuildQueuePortraitLoader.load_design_portrait` both: (1) parse ship class names with the same regex `r"(.*)\s+\((.*)\)"`, (2) construct the same `{SubBase}_Portrait.jpg` filename, (3) try the same directory paths under `assets/ShipThemes/{theme}/Portraits/`, and (4) fall back to placeholder surfaces. The portrait loading logic and ship class parsing are clearly duplicated.

#### Finding: DUP-UIW-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Resource icon loading exists in 3 places: `BuildQueuePortraitLoader.load_resource_icons` (loads from "Resource Portraits"), `PlanetReportPanel._load_resource_icons` (loads from "Resource Portraits"), and `empire_treasury_panel.load_resource_icons` (loads from "Resource Icons" with different naming). The first two load from the same directory with similar fallback logic but different icon sizes. The treasury panel loads from a completely different directory with different filenames. Only the first two are genuine duplication; the treasury panel is a separate icon set.

#### Finding: DUP-UIW-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `ship_stats_renderer.get_hp_bar_color` and `ship_detail_panel.get_damage_color` both convert HP percentage to color with threshold-based logic. They use the same color constants (`HP_HEALTHY`, `HP_DAMAGED`, `HP_CRITICAL`) but with slightly different thresholds (0.5/0.2 vs 0.75/0.5) and `get_damage_color` adds a `HP_DESTROYED` case. These should be consolidated into a single function with consistent thresholds.

#### Finding: DUP-UIW-004
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Searching the UI screens for slider+label patterns, only `new_game_setup_screen.py` and `cargo_quick_dialog.py` use `UIHorizontalSlider`. The race config screens are not among them. There is no evidence of repeated slider+label boilerplate specifically in race config panels. The finding appears to reference code that does not exist.
