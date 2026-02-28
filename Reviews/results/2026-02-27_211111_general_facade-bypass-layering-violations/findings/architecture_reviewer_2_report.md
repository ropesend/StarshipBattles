# Architecture Review Report: Panels, Widgets & Secondary UI
## Reviewer: Architecture Reviewer 2 (Facade Bypass & CQRS Layering Violations)

**Date:** 2026-02-27
**Scope:** UI panels, widgets, research UI, and battle orchestration files

---

### Summary

- **Total issues found:** 16
- **Critical:** 3, **Major:** 7, **Minor:** 4, **Info:** 2

The most significant violations are in the **BuildQueueController** and **BuildQueueDragHandler**, which directly mutate domain object `construction_queue` lists (insert/append/pop) rather than routing through Commands. The **PlanetReportPanel** and **SystemTreePanel** hold and operate on raw domain objects (Planet, Star, WarpPoint) instead of DTOs. The **ResearchControlPanel** directly mutates `ResearchTracker` state from the UI layer.

---

### Findings

#### CRITICAL: BuildQueueController directly mutates domain construction_queue lists
**ID:** AR2-001
**Location:** `game/ui/panels/build_queue_controller.py:413, 416, 450, 453, 491, 535, 538`
**Violation Type:** Direct Mutation
**Issue:** The `BuildQueueController` calls `.insert()` and `.append()` directly on `source.construction_queue` (a domain object's mutable list) in seven places across `_add_to_single_queue()`, `_add_item_with_target_planet()`, `_add_to_multiple_queues()`, and `_add_to_fallback()`. This bypasses the command pipeline entirely for build queue modifications.
**Impact:** Build queue mutations are not validated, logged, or auditable through the standard command pipeline. Any validation logic in the command handler is circumvented. This is the single largest CQRS violation in the reviewed files.
**Recommendation:** Create a new `AddToConstructionQueueCommand` (and optionally `InsertIntoConstructionQueueCommand`) in `commands.py`. Route all queue additions through `facade.handle_command()`. The controller should construct command objects and dispatch them rather than manipulating lists directly.
**Effort:** Complex

---

#### CRITICAL: BuildQueueDragHandler directly pops items from domain construction_queue
**ID:** AR2-002
**Location:** `game/ui/panels/build_queue_drag_handler.py:182`
**Violation Type:** Direct Mutation
**Issue:** In `handle_mouse_motion()`, the drag handler calls `construction_queue.pop(idx)` to remove an item from the domain object's construction queue during a drag-reorder operation. This is a direct mutation of game state from a UI input handler.
**Impact:** Queue items are removed without any command validation. If the drag is canceled (dropped outside), the item is silently lost from the queue. Combined with AR2-001, the entire build queue reorder flow is outside the command pipeline.
**Recommendation:** Create a `RemoveFromConstructionQueueCommand` and `ReorderConstructionQueueCommand`. The drag handler should issue commands rather than directly manipulating the list. For drag-and-drop, consider a two-phase approach: issue a remove command on drag start and an insert command on drop.
**Effort:** Complex

---

#### CRITICAL: BuildQueueController directly accesses Galaxy and Empire domain objects
**ID:** AR2-003
**Location:** `game/ui/panels/build_queue_controller.py:313-316, 344-349, 376-379`
**Violation Type:** Direct Property Access + Command Bypass
**Issue:** The controller holds direct references to `Galaxy` and `Empire` domain objects (injected via constructor). It calls `self.galaxy.get_planets_at_global_hex(self.hex_coord)` and filters planets by `p.owner_id == self.empire.id` in three places (`_needs_planet_selection`, `_get_target_planet_id`, `_add_to_single_queue`). This gives the UI layer direct access to query the Galaxy's internal planet data and Empire identity.
**Impact:** The UI layer bypasses the facade query path for planet lookups. Changes to Galaxy's planet storage or Empire's ownership model would require changes in UI code. The facade already provides `get_planets_at_hex()` which returns `PlanetInfo` DTOs.
**Recommendation:** Replace `self.galaxy.get_planets_at_global_hex(self.hex_coord)` calls with facade queries like `facade.get_planets_at_hex(hex_coord)`. Filter by `planet_info.owner_id` on the returned DTOs. Remove the `galaxy` and `empire` constructor parameters.
**Effort:** Medium

---

#### MAJOR: PlanetReportPanel holds and operates on raw Planet domain objects
**ID:** AR2-004
**Location:** `game/ui/panels/planet_report_panel.py:72, 188, 220-222, 251, 270, 282, 289, 346-347`
**Violation Type:** Direct Property Access
**Issue:** `PlanetReportPanel` stores `self.planet` as a raw domain object and accesses its properties directly throughout: `planet.planet_type.name`, `planet.name`, `planet.atmosphere`, `planet.facilities`, `planet.resources`, `planet.owner_id`. The `update_planet()` method accepts a raw Planet object. The `_update_complexes_list()` method iterates `planet.facilities` and accesses `facility.design_id` and `facility.name`.
**Impact:** The panel is tightly coupled to the Planet domain model's internal structure. Any change to how Planet stores facilities, resources, or atmosphere would require UI changes. The PlanetInfo DTO exists but is not used here.
**Recommendation:** Accept `PlanetInfo` DTO (or an extended version with facilities/resources data) instead of raw Planet objects. Extend `PlanetInfo` with fields for `facilities`, `resources`, and `atmosphere` if not already present, or create a `PlanetDetailInfo` DTO. The `compute_planet_production()` helper function (lines 457-501) also takes a raw `IPlanet` -- this should move to a service/facade method.
**Effort:** Complex

---

#### MAJOR: SystemTreePanel receives and stores raw domain objects (planets, stars, warp points)
**ID:** AR2-005
**Location:** `game/ui/panels/system_tree_panel.py:7, 135-344`
**Violation Type:** Direct Property Access
**Issue:** `SystemTreePanel.set_items()` receives a list of raw domain objects (planets, stars, warp points, systems) and stores them in `SystemTreeItem.obj`. It accesses domain properties directly: `star.name` (line 209), `wp.destination_id` (lines 237, 249), `p.name` (lines 296, 309), `p.location` (line 266), `p.mass` (lines 273, 325). The `on_selection_callback` passes raw domain objects back to callers.
**Impact:** The tree panel is coupled to the internal properties of multiple domain classes. The selection callback leaks domain objects back into the broader UI layer.
**Recommendation:** Pass system contents as DTOs (e.g., a list of `SystemContentItem` DTOs with type, name, location, mass fields). Extend `SystemInfo` to include child object DTOs, or create a dedicated `SystemContentsDTO`. The selection callback should return an ID or DTO, not a domain object.
**Effort:** Complex

---

#### MAJOR: BuildQueuePortraitLoader accesses session.player_empire domain object
**ID:** AR2-006
**Location:** `game/ui/panels/build_queue_portraits.py:69, 93-94`
**Violation Type:** Direct Property Access
**Issue:** `BuildQueuePortraitLoader.__init__()` accepts a raw `session` object and stores it. In `load_design_portrait()`, it accesses `self.session.player_empire.empire_theme_id` -- reaching through the session to access the Empire domain object's theme property.
**Impact:** The portrait loader is coupled to the internal structure of both GameSession and Empire. The facade provides `get_empire()` which returns `EmpireInfo` with `theme_id`.
**Recommendation:** Replace the `session` parameter with a `theme_id: str` parameter (or a callback/facade query). The caller can obtain the theme_id from `EmpireInfo.theme_id` via the facade before constructing the portrait loader.
**Effort:** Simple

---

#### MAJOR: ResearchControlPanel directly mutates ResearchTracker state
**ID:** AR2-007
**Location:** `game/ui/research/research_controls.py:269, 281, 352, 357`
**Violation Type:** Direct Mutation
**Issue:** The control panel directly calls mutating methods on `ResearchTracker`: `self.tracker.set_rp_budget(new_budget)` (line 269), `self.tracker.set_allocation(node_id, new_allocation)` (line 281), `self.tracker.auto_spread_enabled = not self.tracker.auto_spread_enabled` (line 352), and `self.tracker.spread_rp_evenly(self.tech_tree)` (line 357). These are state mutations performed directly from UI code.
**Impact:** Research state mutations bypass any command/validation pipeline. While the research system may not yet have a facade/command layer, this is a clear CQRS violation pattern. If research state needs to be persisted or validated, all these mutations are untracked.
**Recommendation:** If a research facade exists, route mutations through commands. If not, this is a candidate for future facade wrapping. At minimum, the mutations should be routed through callback functions injected at construction time (inversion of control) rather than directly mutating the tracker.
**Effort:** Medium

---

#### MAJOR: ResearchTreeScene directly instantiates and mutates domain objects
**ID:** AR2-008
**Location:** `game/ui/research/research_scene.py:77-82, 341, 362-368`
**Violation Type:** Domain Instantiation + Direct Mutation
**Issue:** `ResearchTreeScene` directly instantiates domain objects: `TechTree.load_from_json()` (line 77), `ResearchTracker()` (line 79). It calls domain methods: `self.tech_tree.resolve_all_requirements()` (line 82), `self.tech_tree.validate_requirements()` (line 86). In `_on_next_turn()`, it calls `ResearchService.process_turn()` (line 341) directly. In `_on_reset()`, it creates a new `ResearchTracker()` (line 365) and re-resolves requirements (line 368).
**Impact:** The UI scene is acting as both a controller and a service layer. Domain logic (tree loading, resolution, turn processing) is embedded in UI code. This makes the research system harder to test independently and violates layer separation.
**Recommendation:** Create a `ResearchSessionFacade` or service that encapsulates TechTree loading, ResearchTracker management, and turn processing. The scene should interact only with this facade/service.
**Effort:** Complex

---

#### MAJOR: compute_planet_production accesses domain internals from UI utility
**ID:** AR2-009
**Location:** `game/ui/panels/planet_report_panel.py:457-501`
**Violation Type:** Direct Property Access + Domain Logic in UI
**Issue:** The `compute_planet_production()` function is defined in a UI panel module but performs domain-level calculations. It iterates `planet.facilities`, accesses `facility.is_operational`, `facility.design_data`, and performs production calculations using registry lookups. This is business logic embedded in the UI layer.
**Impact:** Production calculation logic is duplicated in the UI layer rather than being exposed through a service or facade method. Changes to production formulas require UI code changes.
**Recommendation:** Move `compute_planet_production()` to a strategy service (e.g., `EmpireEconomyCalculator` or a new `PlanetProductionService`). Expose production rates through the facade or include them in `PlanetInfo` DTO.
**Effort:** Medium

---

#### MAJOR: ShipDetailPanel operates on raw ShipInstance domain objects
**ID:** AR2-010
**Location:** `game/ui/panels/ship_detail_panel.py:163-178, 179-327, 340-408`
**Violation Type:** Direct Property Access
**Issue:** `ShipDetailPanel.update_ship()` accepts a raw `ShipInstance` domain object and accesses numerous domain properties: `ship.design_data`, `ship.get_display_id()`, `ship.instance_id`, `ship.name`, `ship.design_id`, `ship.get_status_text()`, `ship.get_hp_display()`, `ship.get_hp_percentage()`, `ship.get_resource_display()`, `ship.get_resource_percentage()`, `ship.get_damaged_component_count()`, `ship.battles_survived`, `ship.kills`, `ship.experience`, `ship.get_damaged_components_by_layer()`. The `_build_damage_section()` method iterates internal component damage data.
**Impact:** The panel is tightly coupled to ShipInstance's full API surface. However, ShipInstance is a strategy-layer data class specifically designed for UI consumption (it has display-oriented methods like `get_hp_display()`, `get_status_text()`). This is a softer violation since ShipInstance appears to serve a DTO-like role.
**Recommendation:** Consider whether ShipInstance should be formalized as a DTO or if a `ShipDetailInfo` DTO should be created. The current coupling is somewhat acceptable since ShipInstance has display-oriented methods, but it still allows the UI to access mutable state. Lower priority than AR2-001 through AR2-003.
**Effort:** Medium

---

#### MINOR: ship_stats_renderer accesses ICombatShip domain internals
**ID:** AR2-011
**Location:** `game/ui/panels/ship_stats_renderer.py:109-416`
**Violation Type:** Direct Property Access
**Issue:** All rendering functions in `ship_stats_renderer.py` accept `ICombatShip` protocol objects and access their properties directly: `ship.resources`, `ship.max_shields`, `ship.current_shields`, `ship.hp`, `ship.max_hp`, `ship.current_speed`, `ship.max_speed`, `ship.layers`, `ship.current_target`, `ship.secondary_targets`, etc.
**Impact:** This is the battle UI renderer, which needs real-time access to combat ship state for rendering during simulation. Using DTOs here would add unacceptable overhead during combat rendering. The `ICombatShip` protocol already provides a controlled interface.
**Recommendation:** No action needed. The protocol-based access (`ICombatShip`) is the correct pattern for battle rendering where performance matters. The protocol serves as the "DTO boundary" for combat display.
**Effort:** N/A

---

#### MINOR: DesignStatsPanel and DesignReportPanel accept raw Ship simulation objects
**ID:** AR2-012
**Location:** `game/ui/panels/design_stats_panel.py:129, 320, 376; game/ui/panels/design_report_panel.py:124, 131-143, 170`
**Violation Type:** Direct Property Access
**Issue:** Both panels accept `Ship` (simulation-layer entity) objects and access properties like `ship.name`, `ship.vehicle_type`, `ship.ship_class`, `ship.theme_id`, `ship.layers`, `ship.layer_status`, `ship.get_missing_requirements()`, `ship.get_validation_warnings()`, `ship.mass_limits_ok`, and `ship.construction_cost`.
**Impact:** These panels are used in the Design Workshop (ship builder) context, where the Ship object is the live, mutable design being edited. Using DTOs would be impractical since the design changes with every component modification and the stats must update in real-time. The Ship object serves as the live model in MVC pattern.
**Recommendation:** Low priority. The design workshop is a special case where the UI must interact with a live mutable Ship. Consider creating a `DesignShipView` protocol to formalize the interface, but this is not a blocking issue.
**Effort:** Medium

---

#### MINOR: ComponentModifierGridPanel and ModifierImpactGrid access Component domain objects
**ID:** AR2-013
**Location:** `game/ui/panels/component_modifier_grid_panel.py:95, 104-105; game/ui/panels/modifier_impact_grid.py:99, 115-148`
**Violation Type:** Direct Property Access
**Issue:** Both panels accept `Component` (simulation-layer) objects and access: `component.modifiers`, `component.get_modifier_stat_summary()`, `component.get_all_modifier_effects()`, `component.ability_instances`, and ability class `STAT_BINDINGS`. These are deep accesses into simulation-layer internals.
**Impact:** Similar to AR2-012, these are used in the Design Workshop context where components are being actively edited. The modifier grid needs real-time access to component modifier data that changes with each edit.
**Recommendation:** Low priority for the same reason as AR2-012. The design workshop context requires live object access. A `ComponentModifierView` protocol could formalize the interface.
**Effort:** Medium

---

#### MINOR: strategy_widgets.py accepts raw domain objects for rendering
**ID:** AR2-014
**Location:** `game/ui/panels/strategy_widgets.py:42-47, 123-126`
**Violation Type:** Direct Property Access
**Issue:** `SpectrumGraph.render()` accepts a `star` domain object and accesses `star.spectrum` with individual band attributes. `AtmosphereGraph.render()` accepts a `planet` domain object and accesses `planet.atmosphere`. Both use `is_star()` and `IPlanet` protocol checks.
**Impact:** These are pure rendering widgets that read data for visualization. They use protocol-based access (`is_star`, `IPlanet`) which provides a controlled interface. The data is read-only for display.
**Recommendation:** Low priority. The protocol-based access is acceptable for rendering widgets. Could be improved by passing data dicts directly instead of domain objects, but the coupling is minimal.
**Effort:** Simple

---

#### INFO: BattleOrchestrator cross-layer imports are intentional and documented
**ID:** AR2-015
**Location:** `game/ui/orchestration/battle_orchestrator.py:1-21`
**Violation Type:** N/A (Intentional design)
**Issue:** BattleOrchestrator imports from AI layer (`AIController`, `ShipControllableAdapter`) and engine layer (`SpatialGrid`). This is well-documented in the module docstring as intentional boundary-crossing for orchestration purposes.
**Impact:** None. This is the correct architectural pattern for UI-layer orchestration that coordinates between simulation and AI layers.
**Recommendation:** No action needed. This is good architecture. The cross-layer imports are intentional, documented, and serve the orchestrator's coordination role.
**Effort:** N/A

---

#### INFO: EmpireTreasuryPanel uses EmpireEconomySnapshot DTO correctly
**ID:** AR2-016
**Location:** `game/ui/panels/empire_treasury_panel.py:57`
**Violation Type:** N/A (Good pattern)
**Issue:** `EmpireTreasuryPanel` receives an `EmpireEconomySnapshot` dataclass and only reads its fields for display. It does not access any domain objects directly.
**Impact:** None. This is the correct CQRS pattern: the panel receives an immutable snapshot DTO and renders it.
**Recommendation:** No action needed. This is exemplary code that other panels should follow.
**Effort:** N/A

---

### Top 5 Priority Issues

1. **AR2-001 (Critical):** BuildQueueController directly mutates domain construction_queue lists -- 7 mutation sites bypassing the command pipeline entirely. This is the highest-priority fix because build queue operations are core game state mutations that should be validated and trackable.

2. **AR2-002 (Critical):** BuildQueueDragHandler pops items from construction_queue -- Direct list mutation from a mouse event handler. Tightly coupled to AR2-001 and should be fixed together.

3. **AR2-003 (Critical):** BuildQueueController holds Galaxy and Empire references -- The controller queries Galaxy internals and Empire state directly when the facade already provides equivalent query methods via DTOs.

4. **AR2-007 (Major) + AR2-008 (Major):** Research UI directly mutates ResearchTracker and instantiates domain objects -- The entire research UI bypasses any facade/command pattern. While the research system may not have a facade yet, this is a significant architectural gap.

5. **AR2-004 (Major):** PlanetReportPanel operates on raw Planet domain objects -- A widely-used panel that should consume PlanetInfo DTOs (possibly extended) rather than raw domain objects. This would also address AR2-009 (compute_planet_production domain logic in UI).

---

### Observations

**Well-architected patterns found:**
- `EmpireTreasuryPanel` correctly uses `EmpireEconomySnapshot` DTO (AR2-016)
- `BattleOrchestrator` properly documents its intentional cross-layer role (AR2-015)
- `ship_stats_renderer` uses `ICombatShip` protocol for controlled access (AR2-011)
- Design Workshop panels (AR2-012, AR2-013) have acceptable coupling to live Ship/Component objects given their editing context

**Systemic pattern:**
The build queue subsystem (controller + drag handler) is the most severe violator, with construction queue mutations happening entirely outside the command pipeline. This represents the highest-risk area for introducing bugs through unvalidated state changes.

The research UI subsystem has no facade/command layer at all, making it a self-contained CQRS gap. This is a good candidate for a future `ResearchSessionFacade` project.

**DTO coverage gaps:**
- No DTO exists for detailed planet data (facilities, resources, atmosphere) -- only `PlanetInfo` with basic fields
- No DTO exists for system contents (planets, stars, warp points as a collection)
- ShipInstance serves a DTO-like role but is a mutable domain object
