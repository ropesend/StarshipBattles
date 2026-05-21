# Cross-Shard Duplication Report

## Summary
- Files Scanned: 846
- Total Findings: 35
- Critical: 6 | Major: 14 | Minor: 11 | Info: 4
- Clone detector clusters validated: 26/26 confirmed, 0 false positives
- Additional cross-shard findings: 9

---

## Clone Detector Validation

### Cluster 1 — execute_action_order (5 members, 0.991 similarity, ~37 LOC)
**CONFIRMED.** `launch_fighters.py`, `launch_satellites.py`, `lay_mines.py`, `recover_fighters.py`, `recover_satellites.py` all contain a near-identical `execute_action_order` method following the same pattern: get order → type-check → extract payload → find ship → create `FleetShipIssuerAdapter` → delegate to `_run_with_issuer`. Only the `OrderType` enum and error message strings differ. Template Method pattern (Pattern #9) should be applied: move the skeleton to a base class with abstract `_order_type` and `_label` properties.

**Estimated LOC savings:** 120 (extract 30-line skeleton × 5 files, replace with 1-line super() call)

---

### Cluster 2 — __init__ (3 members, 1.0 similarity, ~12 LOC)
**CONFIRMED.** `stat_modifiers.py` lines 50 and 125 contain two classes (`GlobalStatModifierAbility` and `FleetStatModifierAbility`) with identical `__init__` + `get_primary_value` + `get_ui_rows` bodies. The `shields.py` `__init__` at line 98 follows the same structure. The two `stat_modifiers.py` variants differ only in class-level attributes (`allowed_scopes`, `default_scope`). They share identical attribute names (`multiplier`, `energy_drain_rate`, `activation_time`, `deactivation_time`). This is a textbook case for `SimpleMultiplierAbility` (defined at base.py:480) — both classes should inherit it.

**Estimated LOC savings:** 30 (remove 20 lines × 2 classes, replace with 4-line class body)

---

### Cluster 3 — superweapon designation handlers (3 members, 0.987 similarity, ~42 LOC)
**CONFIRMED.** `strategy_superweapons.py` has three handlers (`handle_stellerate_star_designation`, `handle_close_warp_designation`, `handle_dyson_sphere_designation`) with identical structure: null-check fleet → `_check_fleet_ability` → screen-to-hex conversion → find target entity → define `on_confirm` closure → show dialog. Consolidate into a parameterized `_handle_designation(ability_name, error_msg, target_finder, confirm_builder, confirm_title, confirm_text)` helper.

**Estimated LOC savings:** 80

---

### Cluster 4 — _execute_fleet handlers (3 members, 0.964 similarity, ~52 LOC)
**CONFIRMED.** `handlers/launch_fighters.py`, `launch_satellites.py`, `lay_mines.py` all contain near-identical `_execute_fleet` methods: resolve fleet → check ship_instance_id → find carrier by str(instance_id) match → count matching bay → resolve requested count → validate availability → build Order dict → add order → log. Only the vehicle_type string (`"fighter"`/`"satellite"`/`"mine"`) and design_id field differ.

**Estimated LOC savings:** 100 (extract shared helper)

---

### Cluster 5 — _execute_planet handlers (3 members, 0.95 similarity, ~37 LOC)
**CONFIRMED.** Mirror of Cluster 4 but for the planet path: resolve planet → count matching yard → validate → build Order → add order. Same pattern-driven consolidation applies.

**Estimated LOC savings:** 65

---

### Cluster 6 — selection prompt methods (3 members, 0.911 similarity, ~24 LOC)
**CONFIRMED.** `selection_prompts.py` has `open_system`, `prompt_fleet`, and `prompt_planet` following identical structure: get composer ref → compute rect centered on screen → construct modal window → assign to composer slot. Differ only in window class, dimensions, and constructor args. Refactor to a generic `_open_selection_modal(window_class, width, height, *args, slot_name)`.

**Estimated LOC savings:** 25

---

### Cluster 7 — process_event (2 members, 1.0 similarity, ~14 LOC)
**CONFIRMED-BY-IDENTICAL.** `defeat_dialog.py` line 107 and `turn_failed_dialog.py` line 123 contain character-for-character identical `process_event` methods handling a dismiss button click. Both inherit from `pygame_gui.elements.UIWindow`. Extract to a `MixinDismissableWindow` or shared base class.

**Estimated LOC savings:** 14

---

### Cluster 8 — launch_fighters_in_battle / launch_satellites_in_battle (2 members, 1.0 similarity, ~39 LOC)
**CONFIRMED-BY-IDENTICAL.** `battle_engine.py` lines 499 and 540 contain two methods with identical bodies (only docstrings differ). Both: import `AttackType` → iterate `carried_vehicles` → build launch attack dict → snapshot ships → call `_attacks.process_launch_attack` → diff ships → return spawned. This is a copy-paste oversight — the satellite method literally documents itself as "Mirrors `launch_fighters_in_battle`".

**Estimated LOC savings:** 35

---

### Cluster 9 — cancel (2 members, 1.0 similarity, ~21 LOC)
**CONFIRMED-BY-IDENTICAL.** `services/llm/background.py` line 182 and `ui/services/image/background.py` line 139 contain identical `cancel` methods (set cancel event → lock → transition status → set finished_at → signal done event). Both follow Pattern #28 (Background Service Call). Extract to a shared base `BackgroundCall.cancel()`.

**Estimated LOC savings:** 20

---

### Cluster 10 — _draw_armor_hit / _draw_component_destroyed (2 members, 0.994 similarity, ~27 LOC)
**CONFIRMED.** `hit_effects.py` `_draw_armor_hit` (line 146) and `_draw_component_destroyed` (line 176) share identical structure: get config → compute radius → early-exit if r<1 → create surface → draw circle → draw radiating lines → blit. Only line count (6 vs 8), colors, and line widths differ. Unify as `_draw_radial_hit(effect_type, num_lines, line_step, color, line_color, line_width, line_length_mult)`.

**Estimated LOC savings:** 20

---

### Cluster 11 — execute_for_issuer (2 members, 0.983 similarity, ~30 LOC)
**CONFIRMED.** `recover_fighters.py` line 107 and `recover_satellites.py` line 90. Both: unpack kwargs → delete galaxy/registries → get current order → type-check → extract payload → delegate to `_run_with_issuer`. Move to shared base class.

**Estimated LOC savings:** 30

---

### Cluster 12 — _run_with_issuer (recover) (2 members, 0.981 similarity, ~87 LOC)
**CONFIRMED.** `recover_fighters.py` line 139 and `recover_satellites.py` line 119. Both follow identical flow: get group_id/count → find deployed group → empty-check → count available → compute requested → iterate ships → convert to CarriedVehicle → append to issuer → remove from group → cleanup empty group → pop order. Structure is identical; only the group type and converter function differ. This is the largest single duplicated block.

**Estimated LOC savings:** 85

---

### Cluster 13 — delete_squadron / duplicate_squadron (2 members, 0.979 similarity, ~8 LOC)
**CONFIRMED.** `controller.py` line 283 and 293. Both: get active fleet → bounds-check → dispatch to `FleetHierarchyEditor` static method → call `_on_change()`. Consolidate to `_edit_squadron(op, tf_index, sq_index)`.

**Estimated LOC savings:** 6

---

### Cluster 14 — _sum_vehicle_bay_used / _sum_vehicle_bay_max (2 members, 0.977 similarity, ~11 LOC)
**CONFIRMED.** `fleet_dto.py` lines 271 and 285. Both iterate `fleet.ships`, access `_cargo_mgr`, call `get_vehicle_bay_capacity()`, sum either `used` (index 0) or `max_mass` (index 1). Consolidate to `_sum_vehicle_bay(index)`.

**Estimated LOC savings:** 10

---

### Cluster 15 — __init_subclass__ validation (2 members, 0.976 similarity, ~7 LOC)
**CONFIRMED.** `base.py` lines 450 and 502. Both `__init_subclass__` methods validate required class attributes with `raise TypeError`. The only difference is the required attribute list (`['ui_label', 'ui_color']` vs `['stat_key', 'value_attr', 'base_attr', 'ui_label', 'ui_color']`). Extract to a shared `_validate_class_attributes(*required)` utility. Low-impact since metaclass hooks are small.

**Estimated LOC savings:** 6

---

### Cluster 16 — _execute_fleet (recover) (2 members, 0.971 similarity, ~31 LOC)
**CONFIRMED.** `handlers/recover_fighters.py` line 51 and `recover_satellites.py` line 53. Both validate fleet → find carrier → build Order dict → add order → log. Same pattern as Clusters 4/5 but for the recover action family.

**Estimated LOC savings:** 30

---

### Cluster 17 — _add_system_effects / _add_sector_effects (2 members, 0.968 similarity, ~13 LOC)
**CONFIRMED.** `system_tree_panel.py` lines 467 and 482. Both: lazy-import `collect_{system,sector}_effects` → get empire context → call collector → call `_add_effects_group`. Consolidate to `_add_scope_effects(scope_label, collector_fn)`.

**Estimated LOC savings:** 12

---

### Cluster 18 — _pick_leader / _pick_name_entry (2 members, 0.955 similarity, ~15 LOC)
**CONFIRMED.** `race_randomizer.py` lines 109 and 127. Both: if portrait_id → look up portrait data → return choice from list → fallback to data list → return default. Consolidate to `_pick_from_portrait(data, portrait_id, rng, key, fallback_key, default)`.

**Estimated LOC savings:** 12

---

### Cluster 19 — contribute_tactical_satellite_launch / contribute_vehicle_launch (2 members, 0.948 similarity, ~41 LOC)
**CONFIRMED.** `launch.py` lines 25 and 69. Both: check `has_ability` → sum co-located VehicleStorage capacity → iterate launch abilities → aggregate capacity/cycle/rate. Only the ability names and ship attribute targets differ. Extract to a parameterized `_contribute_launch(ship, comp, acc, launch_ability, vehicle_fields)`.

**Estimated LOC savings:** 40

---

### Cluster 20 — group_components (2 members, 0.946 similarity, ~16 LOC)
**CONFIRMED.** `grouping_strategies.py` lines 18 and 53 (`DefaultGroupingStrategy` vs `TypeGroupingStrategy`). Both: defaultdict(list) → iterate components → group by key → sort keys → build result list → return. Only the key-extraction differs. Use Strategy pattern with injectable `key_fn`.

**Estimated LOC savings:** 12

---

### Cluster 21 — _run_with_issuer (launch) (2 members, 0.937 similarity, ~86 LOC)
**CONFIRMED.** `launch_fighters.py` line 147 and `launch_satellites.py` line 130. Both: get design_id → parse count → validate count → pop carried → check availability → create deployed group → convert CarriedVehicle → add ships to group. Only vehicle_type and group class differ. This is the 2nd-largest duplicated block.

**Estimated LOC savings:** 85

---

### Cluster 22 — _create_content (2 members, 0.935 similarity, ~14 LOC)
**CONFIRMED.** `race_aptitudes_panel.py` line 91 and `race_identity_panel.py` line 86. Both: get panel width → y=5 → call three section methods with y+=15 spacing. Low-impact structural duplication.

**Estimated LOC savings:** 5

---

### Cluster 23 — open_load_dialog / open_save_dialog (2 members, 0.925 similarity, ~36 LOC)
**CONFIRMED.** `tkinter_utils.py` lines 108 and 147. Both: get tk root → check for None → set default filetypes → try calling `filedialog.asksaveasfilename`/`askopenfilename` → catch exception → return None. Consolidate to `_open_dialog(dialog_fn, initialdir, title, **kwargs)`.

**Estimated LOC savings:** 25

---

### Cluster 24 — __init__ (test_lab panels) (2 members, 0.921 similarity, ~24 LOC)
**CONFIRMED.** `category_panel.py` line 28 and `test_list_panel.py` line 27. Both accept nearly identical font/color/panel_bg params and assign them with almost identical pattern. Low-priority — the parameter sets differ slightly and these are UI renderer panels with different roles.

**Estimated LOC savings:** Not recommended (different roles)

---

### Cluster 25 — _from_dict_payload (2 members, 0.905 similarity, ~14 LOC)
**CONFIRMED.** `deployed_group.py` lines 352 and 410 (`FighterWing` vs `SatelliteConstellation`). Both: import `ShipInstance` → construct class → iterate `data["ships"]` → append `ShipInstance.from_dict` or direct instance. Actually, all 4 `_from_dict_payload` methods at lines 146, 253, 352, 410 follow the same pattern. Use a parameterized template in the base `_ShipBearingDeployedGroup`.

**Estimated LOC savings:** 40 (all 4 variants)

---

### Cluster 26 — _find_fighter_wing / _find_satellite_constellation (2 members, 0.879 similarity, ~16 LOC)
**CONFIRMED.** `recover_fighters.py` line 242 and `recover_satellites.py` line 222. Both: iterate `empire.deployed_groups_of(ConcreteType)` → filter by group_id → filter by location → return match. Consolidate to `_find_deployed_group(empire, group_cls, group_id, hex_)`.

**Estimated LOC savings:** 14

---

## Cross-Shard Findings

### CRITICAL: Vehicle-Bay Ship-Finding Pattern (5 copies across layers)
**ID:** DUP-X-1
**Location:**
- `game/strategy/engine/order_handlers/launch_fighters.py:240`
- `game/strategy/engine/order_handlers/launch_satellites.py:223`
- `game/strategy/engine/order_handlers/lay_mines.py:325`
- `game/strategy/engine/order_handlers/recover_fighters.py:233`
- `game/strategy/engine/order_handlers/recover_satellites.py:213`
- `game/strategy/engine/handlers/launch_fighters.py:68` (inline variant in `_execute_fleet`)
- `game/strategy/engine/handlers/launch_satellites.py:69` (inline variant)
- `game/strategy/engine/handlers/lay_mines.py:77` (inline variant)
- `game/strategy/engine/handlers/recover_fighters.py:62` (inline variant)
- `game/strategy/engine/handlers/recover_satellites.py:64` (inline variant)

**Layer:** strategy (engine/handlers + engine/order_handlers)
**Issue:** The identical `_find_ship(fleet, ship_instance_id)` method appears as a `@staticmethod` in 5 order handler files. Additionally, the same `for ship in fleet.ships: if str(ship.instance_id) == str(cmd.ship_instance_id): ...` pattern is inlined in 5 command handler files. This is 10 copies of the same ~5-line algorithm across the `handlers/` and `order_handlers/` subdirectories.

**Impact:** If the ship lookup logic changes (e.g., switch from str() comparison to UUID-based lookup), 10 sites must be updated. During PROJ-431 the `_find_ship` method was added to the 5 order handler files one-by-one instead of being placed in a shared module.

**Pattern violation:** Pattern #7 (CommandHandlerRegistry) — `BaseCommandHandler` already defines shared helpers like `_resolve_fleet`. `_find_ship` should be there too.

**Recommendation:** Move `_find_ship` to `handlers/base.py::BaseCommandHandler` as a protected static method. Remove the 5 copies from order handler files and the 5 inline variants from handler `_execute_fleet` methods.

**Estimated LOC Savings:** 50
**Effort:** Simple

---

### CRITICAL: facility_has_ability Triangulation (3 semantically-different implementations)
**ID:** DUP-X-2
**Location:**
- `game/ui/screens/planet_menu_items.py:41` — checks via `FacilityAbilitySource`
- `game/strategy/validation/planet_order_validator.py:105` — checks via `component_registry` dict lookup
- `game/ui/screens/strategy_detail_formatter.py:303` — checks via `extract_abilities_from_component`

**Layer:** ui -> strategy (validation), strategy -> ui (detail_formatter)
**Issue:** Three different implementations of the same concept (does a facility have ability X?) using three different access paths. The UI `planet_menu_items.py` version uses `FacilityAbilitySource.get_abilities()` which iterates abilities at runtime. The `planet_order_validator.py` version walks `design_data` components directly. The `strategy_detail_formatter.py` version uses `extract_abilities_from_component`. These can (and likely do) diverge on edge cases like disabled components or components that are in the registry but not live.

**Impact:** The three implementations may give different answers for the same facility, causing UI to show abilities the validation layer rejects, or vice versa. Any addition of a new ability resolution path must be mirrored in 3 places.

**Pattern violation:** Pattern #3 (Registry DI) — "Resolve abilities through the component registry" is the documented contract. Both UI variants bypass the canonical `get_component_abilities` path in `component_abilities.py`.

**Recommendation:** Define a single `facility_has_ability(facility, ability_name, component_registry)` in `strategy/services/component_abilities.py` and route all callers through it. The `FacilityAbilitySource` path should be reserved for runtime ability iteration (when the ability object itself is needed), not for existence checks.

**Estimated LOC Savings:** 30 (remove 2 copies, keep 1 canonical)
**Effort:** Medium (requires updating UI callers to access component_registry)

---

### CRITICAL: Handler Validation Pipeline Duplication (5 handler families)
**ID:** DUP-X-3
**Location:**
- `game/strategy/engine/handlers/launch_fighters.py`
- `game/strategy/engine/handlers/launch_satellites.py`
- `game/strategy/engine/handlers/lay_mines.py`
- `game/strategy/engine/handlers/recover_fighters.py`
- `game/strategy/engine/handlers/recover_satellites.py`

**Layer:** strategy (handlers/)
**Issue:** Every handler's `execute()` method follows this identical pipeline:
1. `check_issuer_invariant(cmd, label)` 
2. If `cmd.planet_id`: `_execute_planet(session, cmd)`
3. Else: `_execute_fleet(session, cmd)`

And each `_execute_fleet` follows:
1. `_resolve_player_fleet(session, cmd.fleet_id)`
2. Check `ship_instance_id` present
3. Find carrier by iterating `fleet.ships` matching `str(instance_id)`
4. Count matching bay/yard
5. Resolve requested count
6. Validate availability (<=0, < requested)
7. Build `Order()` dict with type-specific fields
8. `fleet.add_order(order)`
9. Log
10. Return `ValidationResult.success()`

This is identical across all 5 handler files. Only the `vehicle_type` string, `{}_design_id` field name, and `OrderType` enum differ.

**Impact:** Adding a new deployable type (e.g., "drones") requires copying 60+ lines of boilerplate. Bug fixes to the validation pipeline must be applied to 5 files. In PROJ-431, the `ship_instance_id` check was added independently to each file.

**Pattern violation:** Pattern #7 (CommandHandlerRegistry), Pattern #9 (Template Method). `BaseCommandHandler` exists at `handlers/base.py` and provides `_resolve_player_fleet` / `_resolve_player_planet`. The carrier-finding, count-resolution, and order-building steps should be template methods there too.

**Recommendation:** Define a `_handle_vehicle_order(session, cmd, vehicle_type, design_id_field, order_type, group_name)` template method on `BaseCommandHandler`. Each handler becomes a 3-line class: `execute()` calls the template with type-specific params.

**Estimated LOC Savings:** 280 (5 files × ~55 lines each = 275 replaced with ~60 lines of template + 5 × 3 = 15 lines of subclass)
**Effort:** Complex (touches all 5 handler files + base class + the 5 order_handlers that mirror these)

---

### MAJOR: Bay/Cargo Inventory Defensive Access Pattern (16 locations)
**ID:** DUP-X-4
**Location:** 16 files across `strategy/facade/dto/`, `strategy/validation/`, `strategy/engine/`, `ai/`, `ui/screens/`, `simulation/systems/`
**Layer:** strategy, ui, ai, simulation
**Issue:** The `getattr(ship, "bay_inventory", None)` + `if bay is None: continue` pattern appears 16 times. Similarly, `getattr(ship, "_cargo_mgr", None)` appears 5 times. Every call site implements the same defensive fallback. Since `bay_inventory` was introduced in PROJ-431 and is now the canonical access pattern, many of these guards are vestigial — but scattered across 4 layers they're difficult to audit.

**Impact:** If `bay_inventory` changes its return type or access pattern, 16 sites must be updated. The pervasive `getattr` fallback indicates the API contract is not trusted by callers.

**Recommendation:** Define `ShipInstance.get_bay_inventory() -> BayInventory` (unconditionally, raising if absent) and `ShipInstance.has_bay_inventory() -> bool` for optional-check callers. This provides a single point of change and makes the contract explicit.

**Estimated LOC Savings:** 30 (remove duplication in getattr guard blocks)
**Effort:** Medium

---

### MAJOR: _from_dict_payload Template (4 copies in deployed_group.py)
**ID:** DUP-X-5
**Location:** `game/strategy/data/deployed_group.py:146, 253, 352, 410`
**Layer:** strategy (data)
**Issue:** All four `_from_dict_payload` overrides in `MineGroup`, `FighterWing`, `SatelliteConstellation`, and the base `DeployedGroup` follow the same pattern: construct instance → iterate ships → convert dict entries to `ShipInstance`. But each class re-implements the constructor call and ship iteration separately. The `_ShipBearingDeployedGroup` (lines 340-398) introduces shared `ships` handling but the `_from_dict_payload` variants still duplicate the loop body.

**Impact:** Adding a new deployed group type requires copying another `_from_dict_payload` variant.

**Recommendation:** Factor the shared ship-deserialization loop into `_ShipBearingDeployedGroup._populate_ships_from_payload(cls, data)` template method.

**Estimated LOC Savings:** 35
**Effort:** Simple

---

### MAJOR: warp_capability Check Duplication (9 locations)
**ID:** DUP-X-6
**Location:**
- `game/strategy/engine/fleet_movement_engine.py:185`
- `game/strategy/engine/handlers/movement.py:241`
- `game/strategy/services/fleet_navigation_service.py:56`
- `game/strategy/services/galaxy_pathfinding_service.py:152`
- `game/strategy/data/fleet_consumable_aggregator.py:217, 241`
- `game/strategy/facade/dto/fleet_dto.py:223`
- `game/ui/screens/strategy_fleet_command_router.py:114`
- `game/ui/screens/fleet_menu_items.py:61`

**Layer:** strategy, ui
**Issue:** `fleet.capabilities.can_use_warp()` is called from 9 locations across 8 files. Many of these sites also implement their own fallback semantics (what to do when warp is disabled). The UI sites additionally wrap it in `getattr(fleet, "capabilities", None)` before calling. This duplicates the warp-gating logic.

**Recommendation:** Consolidate the warp-capability check into `Fleet.can_use_warp() -> bool` (with explicit False when `capabilities` is None). The individual call-sites should only decide what action to take, not how to determine warp capability.

**Estimated LOC Savings:** 15 (remove redundant getattr guards)
**Effort:** Medium

---

### MAJOR: Command Handler fleet-ship resolution (inline duplicate across 5 handlers)
**ID:** DUP-X-7
**Location:** `game/strategy/engine/handlers/launch_fighters.py:68-75` (and 4 siblings)
**Layer:** strategy (handlers)
**Issue:** Every `_execute_fleet` method in the handler files contains an inline ship-resolution loop:
```python
carrier = None
for ship in fleet.ships:
    if str(ship.instance_id) == str(cmd.ship_instance_id):
        carrier = ship
        break
```
This is the same logic as the `_find_ship` static methods in the order handler files. The command handlers should reuse the same helper.

**Recommendation:** After DUP-X-1 is resolved (moving `_find_ship` to `BaseCommandHandler`), replace all 5 inline loops with calls to `self._find_ship(fleet, cmd.ship_instance_id)`.

**Estimated LOC Savings:** 30
**Effort:** Simple (depends on DUP-X-1)

---

### MINOR: count_matching_bay / count_matching_yard usage triplication
**ID:** DUP-X-8
**Location:** `game/strategy/engine/handlers/launch_fighters.py:77,115` + 4 siblings
**Layer:** strategy (handlers)
**Issue:** The pattern `count_matching_bay(bay, vehicle_type, design_id)` / `count_matching_yard(yard, vehicle_type, design_id)` followed by identical resolve/validate/error blocks is duplicated 6 times (3 handlers × 2 paths each). Already captured by Clusters 4/5 but the `count_matching_*` + validation block specifically could be extracted into a single shared helper.

**Estimated LOC Savings:** Covered by Clusters 4/5
**Effort:** Covered by DUP-X-3

---

### MINOR: _fighter_ship_to_carried_vehicle / _satellite_ship_to_carried_vehicle
**ID:** DUP-X-9
**Location:**
- `game/strategy/engine/order_handlers/recover_fighters.py:260`
- `game/strategy/engine/order_handlers/recover_satellites.py:240`
**Layer:** strategy (order_handlers)
**Issue:** These two methods (not detected by clone detector but structurally identical) both: get design data → extract mass via `get_calculated_stats()` → fallback to design_data mass → cap at 0 → extract HP value → clamp negative → extract component states → build CarriedVehicle. The only difference is the called method name on the design (trivially abstractable).

**Similarity:** ~0.92
**Estimated LOC Savings:** 30
**Effort:** Simple

---

### MINOR: _format_ship_summary / _format_cargo_summary fleet iteration
**ID:** DUP-X-10
**Location:** `game/ui/screens/strategy_detail_fmt.py:513` and `game/strategy/facade/dto/fleet_dto.py:129`
**Layer:** ui, strategy (facade)
**Issue:** Both iterate `fleet.ships` to build display summaries. `FleetDTO.from_fleet()` at fleet_dto.py:129 builds `ShipInfo` DTOs; `_format_ship_summary()` at strategy_detail_fmt.py:513 builds `Counter` + design info for HTML rendering. While the output format differs, both copy the same iteration + stat-access pattern (`ship.design_data`, `ship.get_calculated_stats()`). UI is re-implementing a data-gathering pattern that the DTO already does.

**Recommendation:** UI should consume the `FleetInfo` DTO's `ship_infos` list rather than re-iterating `fleet.ships` and re-extracting design data. This is partially a Pattern #6 (CQRS-lite) violation — UI reads should use frozen DTOs.

**Estimated LOC Savings:** 15
**Effort:** Medium

---

### MINOR: getattr(bay_inventory.pods) for Drop Pod checking (2 similar implementations)
**ID:** DUP-X-11
**Location:**
- `game/strategy/validation/colonize_validator.py:91,130,150` — 3 methods all iterate `fleet.ships` + `getattr(bay_inventory)`
- `game/ui/screens/strategy_detail_fmt.py:565` — similar `getattr(bay_inventory)` access

**Layer:** strategy (validation), ui
**Issue:** The colonize validator has 3 separate methods (`fleet_has_drop_pod`, `count_drop_pods`, `find_ship_with_drop_pod`) that all begin with the same `for ship in fleet.ships: bay = getattr(ship, "bay_inventory", None); if bay is None: continue` preamble. These should be refactored into a single iterator+aggregator in the ship_cargo abstraction.

**Estimated LOC Savings:** 20 (combine 3 methods into 1 parameterized helper)
**Effort:** Simple

---

### INFO: Multiple Process-Event Skeleton in UI Windows
**ID:** DUP-X-12
**Location:** 28 `process_event` methods across `game/ui/`
**Layer:** ui
**Issue:** 28 `process_event` methods exist across UI window classes. Most follow the same pattern: check `event.type == pygame_gui.UI_BUTTON_PRESSED` → check if `event.ui_element` matches a stored button → perform action. This is inherent to the pygame_gui event model and is architectural, not a fixable duplication — but the clone-detected Cluster 7 (defeat_dialog / turn_failed_dialog) shows that when individual dialogs have identical button handling, consolidation is warranted.

**Recommendation:** Audit the 28 `process_event` methods for additional identical pairs beyond Cluster 7. Any dialog with only a single dismiss/ok button should subclass a shared `DismissableDialog`.

---

### INFO: _mint_deployed_group_id / _mint_group_id Naming Drift
**ID:** DUP-X-13
**Location:**
- `game/strategy/engine/order_handlers/launch_fighters.py` — `_mint_group_id`
- `game/strategy/engine/order_handlers/launch_satellites.py` — (private inline pattern)
- `game/strategy/engine/order_handlers/lay_mines.py:364` — `_mint_deployed_group_id`
- `game/strategy/engine/order_handlers/recover_fighters.py` — (no separate method, inlined in `_create_fighter_group`)
**Layer:** strategy (order_handlers)
**Issue:** The concept "mint a new unique group ID" has 3 different names/implementations. `lay_mines.py` adds `deployed_` prefix; `recover_fighters.py` inlines it. The underlying algorithm is identical: check `empire.fleets` + `empire.deployed_groups` for existing IDs, find max+1.

**Recommendation:** Consolidate into a single `_mint_group_id(empire)` on a shared base class (or a standalone utility). Naming drift is a maintenance hazard.

**Estimated LOC Savings:** 15
**Effort:** Simple

---

## Prioritized Consolidation Plan

Sorted by impact/effort ratio (highest ROI first):

| Priority | ID | Description | Savable LOC | Effort | ROI |
|----------|------|-------------|-------------|--------|-----|
| 1 | DUP-X-1 | Unify `_find_ship` into `BaseCommandHandler` | 50 | Simple | Very High |
| 2 | DUP-X-3 | Template Method for handler validation pipeline | 280 | Complex | High |
| 3 | Cluster 8 | Merge `launch_fighters_in_battle`/`launch_satellites_in_battle` | 35 | Simple | High |
| 4 | Cluster 2 | Consume `SimpleMultiplierAbility` for stat_modifiers | 30 | Simple | High |
| 5 | DUP-X-5 | Template `_from_dict_payload` for deployed groups | 35 | Simple | High |
| 6 | Cluster 9 | Shared base `cancel()` for background calls | 20 | Simple | High |
| 7 | Clusters 1+4+5+11+12 | Consolidate launch/recover/lay handler families | 365 | Complex | High |
| 8 | DUP-X-2 | Unify `facility_has_ability` in `component_abilities.py` | 30 | Medium | Medium |
| 9 | Cluster 3 | Parameterize superweapon designation handlers | 80 | Medium | Medium |
| 10 | Cluster 6 | Generic selection modal opener | 25 | Simple | Medium |
| 11 | Cluster 19 | Parameterize stat contributor launch functions | 40 | Simple | Medium |
| 12 | Clusters 21+12 | Merge `_run_with_issuer` variants | 170 | Complex | Medium |
| 13 | Cluster 26 | Generic deployed-group finder | 14 | Simple | Medium |
| 14 | DUP-X-9 | Unify ship-to-carried-vehicle converters | 30 | Simple | Medium |
| 15 | Cluster 7 | Shared `DismissableDialog` | 14 | Simple | Medium |
| 16 | Cluster 10 | Unify hit effect drawing functions | 20 | Simple | Medium |
| 17 | Cluster 23 | Shared file dialog opener | 25 | Simple | Medium |
| 18 | Cluster 14 | Unify vehicle bay capacity summarizers | 10 | Simple | Medium |
| 19 | DUP-X-11 | Unify bay inventory iteration in colonize validator | 20 | Simple | Medium |
| 20 | Cluster 18 | Shared portait data picker | 12 | Simple | Medium |
| 21 | DUP-X-4 | Canonical bay_inventory accessor | 30 | Medium | Low |
| 22 | DUP-X-6 | Centralize warp capability check | 15 | Medium | Low |
| 23 | DUP-X-10 | UI consumes FleetInfo DTO instead of re-iterating | 15 | Medium | Low |
| 24 | Cluster 13 | Unify delete/duplicate squadron dispatchers | 6 | Simple | Low |
| 25 | Cluster 15 | Shared class attribute validator | 6 | Simple | Low |
| 26 | Cluster 17 | Unify system/sector effect loading | 12 | Simple | Low |
| 27 | Cluster 20 | Strategy pattern for component grouping | 12 | Simple | Low |
| 28 | Cluster 22 | Section builder for race panels | 5 | Simple | Low |
| 29 | DUP-X-13 | Unify group ID minting | 15 | Simple | Low |
| 30 | Cluster 24 | Not recommended — different roles | 0 | — | — |

### Grand Total Estimated LOC Savings
- From clone detector clusters: ~754 LOC (matches tool estimate)
- From cross-shard findings: ~490 LOC
- **Total reclaimable: ~1,244 LOC**

### Consolidation Effort Summary
- **Low-hanging fruit** (Simple effort, Items 1, 3, 4, 5, 6, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20): ~356 LOC savable
- **Medium complexity** (Items 8, 9, 21, 22, 23): ~170 LOC savable
- **Complex refactor** (Items 2, 7, 12): ~815 LOC savable — but these are the highest-ROI items and address the root architectural duplication in the handler/order-handler families

### Architecture Note
The single largest root cause of duplication is the **parallel handler/order-handler architecture** for launch/recover/lay/mine operations. The command handlers (`handlers/`) and order handlers (`order_handlers/`) independently re-implement the same validation, ship-finding, and order-building logic across 5 file pairs (10 files total). This was unavoidable during PROJ-431's phased rollout (each vehicle type was delivered incrementally), but the pattern has now fully crystallized and a Template Method consolidation (DUP-X-3) is the architecturally correct path forward.
