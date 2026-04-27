# PROJ-310 Phase 2: Archetype Assignments

For each top-30 function (combined from `top30_by_function.md` and
`top30_by_visual_depth.md`), this doc records the archetype, verdict,
and a recommended approach. Assignments draw on Phase 1 metrics plus
direct reads of each function's body.

A new archetype — **`dispatch-ladder`** — was added during Phase 2.
The classic top-of-list offenders (`_format_orders` AST=15, `_handle_button`
AST=14, `_handle_button_pressed` AST=14) are not visually nested: they
are flat `if/elif/elif/...` chains that the AST exposes as nested
`If(orelse=[If(...)])` trees. Visual depth is 1-3, but cyclomatic
complexity is high (CC 22-52 per radon). The right fix is dispatch-table
or polymorphic dispatch, not de-nesting.

Verdicts use `refactor`, `legitimate`, `borderline`.

---

## Dispatch-ladder offenders (AST depth >= 9, visual <= 5)

### `game/ui/screens/strategy_detail_fmt.py::_format_orders`
**AST:** 15 / **Visual:** 3 / **elif_run:** 14 / **LOC:** 72
**Archetype:** dispatch-ladder
**Verdict:** refactor
**Approach:** Replace the OrderType elif ladder with a `dict[OrderType, Callable[[Order, Fleet], str]]`. Each handler returns its own line. The outer `for i, order` becomes a list-comprehension over `_HANDLERS[order.type](order, fleet)`. Fallback: `_HANDLERS.get(order.type, _default)`.

### `game/ui/screens/battle_setup/input_handler.py::BattleSetupInputHandler._handle_button`
**AST:** 14 / **Visual:** 2 / **elif_run:** 14 / **LOC:** 105
**Archetype:** dispatch-ladder
**Verdict:** refactor
**Approach:** Each branch matches on `hasattr(element, '_xxx_index')` or `element == named_button`. Convert to two passes: (1) attribute-tagged buttons via a `(attr_name, handler)` table; (2) named buttons via an `{element_id: handler}` dict built in `__init__`. Drops to depth 2 with one early-return scan loop.

### `game/ui/screens/fleet_report_filters.py::sort_ships` + `sort_ships.get_sort_key`
**AST:** 14 / **Visual:** 3 / **elif_run:** 13 / **LOC:** 61
**Archetype:** dispatch-ladder (sort-key ladder)
**Verdict:** refactor
**Approach:** The ladder maps `sort_field` strings to per-ship key extraction. Convert to `_SORT_KEY_BUILDERS: dict[str, Callable[[ship], Any]]`. The nested `get_sort_key` closure inherits the same fix.

### `game/ui/screens/strategy_event_router.py::StrategyEventRouter._handle_button_pressed`, `._handle_window_close`
**AST:** 14, 13 / **Visual:** 2, 1 / **elif_run:** 13, 12 / **LOC:** 40, 34
**Archetype:** dispatch-ladder
**Verdict:** refactor
**Approach:** Build a `{ui_element: handler}` lookup at `__init__`. Each handler is a tiny method already on `StrategyUI`. The outer guard becomes a `dict.get(...)`/`return` early-out.

### `game/ui/screens/strategy_ui_action_router.py::UIActionRouter.handle_ui_action`
**AST:** 12 / **Visual:** 1 / **elif_run:** 12 / **LOC:** 52
**Archetype:** dispatch-ladder
**Verdict:** refactor
**Approach:** UIAction enum → handler dict.

### `game/ui/screens/workshop_event_router.py::_handle_panel_action`, `_handle_button_pressed`
**AST:** 12 / **Visual:** 1-2 / **elif_run:** 12 / **LOC:** 35-47
**Archetype:** dispatch-ladder
**Verdict:** refactor
**Approach:** Same fix as strategy_event_router — `{ui_element: handler}` table + early-return.

### `game/ui/screens/builder/layer_panel.py::LayerPanel.handle_item_action`
**AST:** 13 / **Visual:** 3 / **elif_run:** 11 / **LOC:** 61
**Archetype:** dispatch-ladder (action-string)
**Verdict:** refactor
**Approach:** `{action_string: handler}` table. Already a Command-pattern docstring claim — the table makes that real.

### `game/strategy/data/order_types.py::Order.to_dict`
**AST:** 10 / **Visual:** 2 / **elif_run:** 9 / **LOC:** 52
**Archetype:** dispatch-ladder (serialization)
**Verdict:** refactor
**Approach:** Move serialization onto OrderType (e.g., `target_serializer: dict[OrderType, Callable[[Order], Any]]` in this module, or per-OrderSubtype if a subclass tree gets introduced later). Eliminates accreted PROJ-102/PROJ-207/PROJ-238 markers cleanly.

### `game/ui/screens/strategy_fleet_command_router.py::FleetCommandRouter.handle_fleet_action`, `.handle_detail_action`
**AST:** 10 / **Visual:** 3 / **elif_run:** 8-9 / **LOC:** 51-86
**Archetype:** dispatch-ladder
**Verdict:** refactor
**Approach:** Action-name → handler dict.

### `game/ui/screens/orders_window.py::OrdersWindow._get_order_description`
**AST:** 9 / **Visual:** 3 / **elif_run:** 8 / **LOC:** 47
**Archetype:** dispatch-ladder (OrderType formatter — duplicates `_format_orders`)
**Verdict:** refactor
**Approach:** Same formatter table as `_format_orders`; share a single registry between both functions. Removes a real duplication smell.

### `game/ui/screens/strategy_input_handler.py::StrategyInputHandler._handle_button_press`
**AST:** 9 / **Visual:** 2 / **elif_run:** 9 / **LOC:** 25
**Archetype:** dispatch-ladder
**Verdict:** refactor
**Approach:** Button → handler dict.

### `game/ui/screens/battle_screen.py::BattleScreen._handle_keydown`
**AST:** 9 / **Visual:** 1 / **elif_run:** 9 / **LOC:** 24
**Archetype:** dispatch-ladder (key-binding)
**Verdict:** refactor
**Approach:** `{pygame.K_*: handler}` dict. Borderline — only 24 LOC, but it duplicates a pattern that recurs across input handlers and is the "right" design for keybindings.

### `game/ui/screens/transfer_dialog.py::TransferDialog.process_event`
**AST:** 8 / **Visual:** 2 / **elif_run:** 7 / **LOC:** 34
**Archetype:** dispatch-ladder
**Verdict:** refactor

### `game/ui/screens/builder/modifier_row.py::ModifierControlRow.handle_event`
**AST:** 8 / **Visual:** 3 / **elif_run:** 5 / **LOC:** 69
**Archetype:** dispatch-ladder + minor defensive
**Verdict:** refactor

### `game/ui/screens/strategy_detail_formatter.py::StrategyDetailFormatter.show_detailed_report`
**AST:** 7 / **Visual:** 1 / **elif_run:** 7 / **LOC:** 73
**Archetype:** dispatch-ladder (object-type → formatter)
**Verdict:** refactor
**Approach:** Type-tag dispatch (`is_planet`, `is_fleet`, `is_star`) to a registered set of formatters.

---

## Loop-stack offenders (visual depth >= 5, real multi-level data)

### `game/ui/screens/builder/layer_panel.py::LayerPanel.rebuild`
**AST:** 7 / **Visual:** 7 / **elif_run:** 1 / **LOC:** 175
**Archetype:** loop-stack (genuinely 3-level: layer -> group -> individual)
**Verdict:** refactor (size driven, not depth driven)
**Approach:** Extract three helpers — `_rebuild_layer_header(l_type, ...)`, `_rebuild_group_item(group_key, ...)`, `_rebuild_individual_item(comp, ...)`. Also extract a `cache_or_create(key, ctor)` helper to remove the duplicated cache-hit/miss block at every level. Visual depth drops from 7 to 3, function size from 175 LOC to ~40 LOC + three small helpers.

### `game/strategy/services/system_effects_collector.py::_collect_effects`
**AST:** 6 / **Visual:** 6 / **elif_run:** 3 / **LOC:** 122
**Archetype:** loop-stack (planet -> facility -> component -> ability -> entry)
**Verdict:** refactor
**Approach:** Extract `_iter_ability_entries(planets, empire_id, registries, allowed_scopes) -> Iterator[(planet, facility, comp_key, ability_name, entry)]` generator. The main function becomes a single `for ctx in _iter_...:` loop populating `raw_providers`. Visual depth drops from 6 to 2.

### `game/simulation/entities/combat_endurance.py::calculate_combat_endurance`
**AST:** 8 / **Visual:** 6 / **elif_run:** 3 / **LOC:** 114
**Archetype:** loop-stack + dispatch-ladder (resource_type if-chain)
**Verdict:** refactor
**Approach:** Replace `if ab.resource_type == "fuel": ... elif "energy": ... elif "ammo":` with a `defaultdict(float)` keyed by `resource_type`. Replace the inner `for inst in c.ability_instances: if is_weapon(inst): reload_t = inst.reload_time; break` with `next((i.reload_time for i in c.ability_instances if is_weapon(i)), 1.0)`. Visual depth 6 -> 3.

### `game/ui/components/table/virtual_table.py::VirtualTable.update_visible_rows`
**AST:** 6 / **Visual:** 6 / **elif_run:** 2 / **LOC:** 86
**Archetype:** loop-stack
**Verdict:** borderline
**Approach:** Smaller win — depth would drop from 6 to ~4 with helper extraction. Defer unless this file is on PROJ-309's list.

### `game/strategy/engine/planet_energy_engine.py::PlanetEnergyEngine._process_planet`
**AST:** 6 / **Visual:** 6 / **elif_run:** 1 / **LOC:** 69
**Archetype:** loop-stack with shape-defensive (entry can be dict or list)
**Verdict:** refactor
**Approach:** Extract `_iter_resource_entries(comp, abilities, ability_name, resource) -> Iterator[float]`. The two parallel `if ResourceStorage / if StrategicResourceGeneration` blocks become two `sum(...)` lines. Visual depth 6 -> 3.

### `game/ui/screens/builder/stat_rows_dynamic.py` — five functions: `get_planetary_engineering_rows`, `get_planetary_defense_rows`, `get_strategic_modifier_rows`, `_get_strategic_abilities`, `_get_constant_consumption`
**AST:** 6-8 / **Visual:** 4-6 / **LOC:** 14-42 each
**Archetype:** loop-stack (DUPLICATED across all five)
**Verdict:** refactor
**Approach:** All five functions iterate `(ability_dict.items()) -> (ship.get_all_components()) -> (comp.has_ability(ab_name)) -> (closure that re-iterates components to sum a stat)`. Extract two helpers: `_first_component_with_ability(ship, ability_name) -> Optional[(Component, Ability)]` and `_sum_ability_attr(ship, ability_name, attr) -> float`. Each function collapses from depth 6 to depth 2. Strong cluster — five sites, one refactor.

### `game/strategy/data/build_queue_source.py::colony_has_planetary_yard`, `_get_planetary_yard_size_multiplier`
**AST:** 6 / **Visual:** 6 / **LOC:** 33-41
**Archetype:** loop-stack (planet -> facility -> component -> ability)
**Verdict:** refactor
**Approach:** Extract `_iter_facility_components_with_ability(planet, ability_name) -> Iterator[(facility, comp, ability)]`. Both functions reduce to flat searches.

### `game/ui/screens/builder_selection.py::process_selection_change`
**AST:** 6 / **Visual:** 6 / **LOC:** 60
**Archetype:** loop-stack + defensive
**Verdict:** refactor
**Approach:** Inverse-condition early-return guards collapse the outer `if a: if b: if c:` chain.

### `game/strategy/quickstart_builder.py::QuickstartBuilder.copy_quickstart_designs`
**AST:** 6 / **Visual:** 6 / **LOC:** 56
**Archetype:** loop-stack with try-block
**Verdict:** borderline — copy-with-error-handling is legitimately three loops + a try. Extracting `_copy_one(design, dest)` brings the body to depth 3 cleanly.

### `game/ui/panels/system_tree_panel.py::SystemTreePanel.set_items`
**AST:** 5 / **Visual:** 5 / **LOC:** 232
**Archetype:** accretion (overlong) + nested closure (def inside if)
**Verdict:** refactor (size driven)
**Approach:** 232 LOC. Already in PROJ-309 territory. **Absorbed by PROJ-309.**

### `game/strategy/services/combat_modifier_collector.py::collect_combat_modifiers`
**AST:** 5 / **Visual:** 5 / **LOC:** 115
**Archetype:** loop-stack
**Verdict:** refactor
**Approach:** Same pattern as `_collect_effects`: extract iterator generator.

### `game/ui/panels/planet_report_panel.py::PlanetReportPanel._build_resource_grid`
**AST:** 5 / **Visual:** 5 / **LOC:** 107
**Archetype:** loop-stack
**Verdict:** borderline — size suggests it deserves splitting per-section, but the depth alone is not alarming.

### `game/simulation/battle_state.py::ShipState.to_ship`
**AST:** 5 / **Visual:** 5 / **LOC:** 99
**Archetype:** loop-stack (parser-like — restoring state from save)
**Verdict:** **legitimate**
**Approach:** This is a parser/deserializer mirroring the ShipState shape. Leave alone.

### `game/strategy/engine/game_session.py::GameSession.from_dict`
**AST:** 5 / **Visual:** 5 / **LOC:** 124
**Archetype:** parser (save deserializer)
**Verdict:** **legitimate**
**Approach:** Mirrors save shape. Leave alone.

### `game/ui/screens/race_setup_screen.py::RaceSetupScreen.process_event`
**AST:** 9 / **Visual:** 5 / **elif_run:** 5 / **LOC:** 154
**Archetype:** accretion
**Verdict:** refactor
**Approach:** Multiple `PROJ-XX:` markers signal organic growth. Extract per-event-type handlers (`_handle_llm_dialog_button(event)`, `_handle_description_button(event)`, `_handle_button(event)`, `_handle_dropdown(event)`, `_handle_slider(event)`, `_handle_text_entry(event)`). Top-level becomes a 6-line dispatch on `event.type`. **Already in PROJ-309's top-10 — absorbed by PROJ-309.**

### `game/ui/screens/strategy_detail_fmt.py::format_planet_info`
**AST:** 7 / **Visual:** 5 / **LOC:** 156
**Archetype:** accretion
**Verdict:** refactor
**Approach:** Extract `_format_mass(planet)`, `_format_population_block(planet, view)`, `_format_facilities_block(planet)`, `_format_ability_status_block(planet)`, `_format_uncolonized_section(planet, empire, race_registry)`. Visual depth 5 -> 2.

### `game/ui/renderer/game_renderer.py::draw_ship`
**AST:** 7 / **Visual:** 5 / **LOC:** 117
**Archetype:** loop-stack + state-machine (LayerType radius elif chain) + accretion
**Verdict:** refactor
**Approach:** (1) `LAYER_RADIUS_FACTOR: dict[LayerType, float]` replaces the LayerType→radius elif chain. (2) `COMPONENT_COLOR: list[(predicate, color)]` replaces the weapon/propulsion/armor elif. (3) Extract `_draw_overlay_layers(...)` and `_draw_overlay_components(...)`. Visual depth 5 -> 2.

### `game/ui/screens/strategy_renderer.py::_draw_system_details`, `_draw_fleets`, `_draw_warp_lanes`
**AST:** 5-7 / **Visual:** 5 / **LOC:** 58-132
**Archetype:** loop-stack
**Verdict:** refactor — **absorbed by PROJ-309** (`strategy_renderer.py` is in PROJ-309's top-10).

### `game/ui/screens/strategy_click_dispatcher.py::ClickModeDispatcher._hit_test_planets`
**AST:** 7 / **Visual:** 4 / **LOC:** 108
**Archetype:** loop-stack + defensive (multiple `getattr(... is None)` guards inside loops)
**Verdict:** refactor
**Approach:** Early-return guards on `getattr` results; extract `_hit_test_planet_in_system(planet, click_pos, ...)` worker. Depth 4 -> 2.

### `game/ui/screens/test_lab/renderer.py::TestLabRenderer._is_condition_verified`
**AST:** 5 / **Visual:** 5 / **LOC:** 82
**Archetype:** loop-stack with try-block
**Verdict:** borderline — relatively small, leave for now unless test_lab is being actively reworked.

### `game/ui/screens/builder_selection.py::process_selection_change`
(Already covered above)

### `game/ui/screens/planet_list_presets.py::apply_planet_list_state`
**AST:** 5 / **Visual:** 5 / **LOC:** 92
**Archetype:** state-machine (preset application)
**Verdict:** borderline
**Approach:** Could split per-preset-section, but the structure mirrors the preset shape. Defer.

### `game/ui/screens/planet_selection_window.py::PlanetSelectionWindow.update`
**AST:** 5 / **Visual:** 5 / **LOC:** 66
**Archetype:** defensive
**Verdict:** refactor
**Approach:** Early-return guards.

### `game/engine/collision.py::CollisionSystem.process_beam_attack`
**AST:** 6 / **Visual:** 5 / **LOC:** 84
**Archetype:** defensive (target-resolution + LOS checks)
**Verdict:** borderline — collision is a hot path; touch carefully.
**Approach:** Extract `_resolve_beam_target(...)` to flatten outer guards.

### `game/ui/screens/builder/layer_panel.py::LayerPanel.get_range_selection`
**AST:** 6 / **Visual:** 5 / **LOC:** 65
**Archetype:** loop-stack
**Verdict:** refactor — covered by the layer_panel rebuild project.

### `game/ui/screens/strategy_colonization.py::ColonizationSystem.on_colonize_click`
**AST:** 5 / **Visual:** 5 / **LOC:** 65
**Archetype:** defensive (planet/fleet/empire null-checks)
**Verdict:** refactor
**Approach:** Early-return guards.

### `game/ui/screens/star_list_filters.py::sort_stars`, `planet_list_filters.py::sort_planets`
**AST:** 12, 10 / **Visual:** 5 / **elif_run:** 7, 5 / **LOC:** 52, 48
**Archetype:** dispatch-ladder + nested closure
**Verdict:** refactor
**Approach:** Same fix as `sort_ships` — sort-key dict.

### `game/simulation/entities/ship_layer_manager.py::ShipLayerManager.change_class`
**AST:** 5 / **Visual:** 5 / **LOC:** 56
**Archetype:** loop-stack (component re-layering)
**Verdict:** borderline — domain logic mirrors ship-layer hierarchy.

---

## Cross-cutting patterns

### Pattern 1: UI event-router elif ladders (DISPATCH-LADDER)
**Sites:** ~14 functions in `game/ui/screens/` and `game/ui/screens/builder/`.

These are flat-but-long elif chains that match a button/element identity or
a UIAction enum and dispatch to a handler. AST depth shows 9-15; visual
depth is 1-3. **The right fix is uniform across them all:** build a
`{event_id: handler}` dict at `__init__` and replace the body with a single
`dict.get(event.ui_element, default)()` call. A small "EventDispatcher"
helper class would defang the entire pattern in one project.

**Idiom-level fix:** introduce `game/ui/event_dispatch.py` with
`ButtonDispatcher` / `ActionDispatcher` helpers. Each event router stops
being a 30-50-line if-chain and becomes a `__init__` table + a 2-line
dispatch.

### Pattern 2: `for component / for ability_entry` loop-stack (LOOP-STACK)
**Sites:** `_collect_effects`, `combat_endurance`, `planet_energy_engine._process_planet`,
`stat_rows_dynamic.py` (x5), `build_queue_source.py` (x2),
`combat_modifier_collector`, `_hit_test_planets` (planet/component variant).

All of these iterate `(planet | ship) -> facilities/components -> abilities/ability-entries`.
The body of the inner loop varies, but the iteration scaffolding is identical.

**Idiom-level fix:** add to `game/strategy/services/abilities_iter.py` (or
similar) a small set of generator helpers:
- `iter_planet_abilities(planet, ability_name) -> Iterator[(facility, comp, entry)]`
- `iter_ship_abilities(ship, ability_name) -> Iterator[(comp, entry)]`
- `first_ship_ability(ship, ability_name) -> Optional[(comp, ability)]`
- `sum_ship_ability_attr(ship, ability_name, attr) -> float`

These would defang the pattern at all ~10 sites.

### Pattern 3: OrderType / LayerType / SortField string-or-enum dispatch
**Sites:** `_format_orders`, `_get_order_description`, `Order.to_dict`,
`draw_ship` (LayerType), `sort_ships` / `sort_stars` / `sort_planets`
(SortField), `_draw_system_details` (object kind).

These all switch on a small enum/string set to produce a value or
side-effect. AST depth 7-15. Visual depth 1-5.

**Idiom-level fix:** none — these don't share a single helper. But each
deserves a module-level dispatch table. Notably, `_format_orders` and
`_get_order_description` should share ONE OrderType formatter registry.

### Pattern 4: Deep-nesting cluster in `game/ui/screens/`
**Files:** of the top-30 visual-depth offenders, **20 of 30 are in `game/ui/screens/`**.
The rest split between `game/strategy/services/` (loop-stacks),
`game/simulation/` (3 functions), and `game/ui/renderer/` (1).

**Implication:** the production code that does NOT live in UI screens is
largely well-structured. Refactor budget should target UI first.
Conversely, UI files are where the highest-value PROJ-309 decompositions
already are — substantial overlap with PROJ-309.

### Pattern 5: Parser/deserializer functions are NOT in the top-30 by visual depth
Notable absence: only `ShipState.to_ship` (visual 5, legit) and
`GameSession.from_dict` (visual 5, legit) qualify as parser-archetype.
Most save/restore code is below depth 4 — a sign of healthy decomposition
already.

### Pattern 6: try-ladder is essentially absent
No `try` block in this codebase contains another `try`. The few
deeply-nested-with-try functions are `try` siblings to `for` / `if`,
not nested. **Try-ladder is not a category requiring a project here.**

---

## Summary tally (top 30 by visual depth)

| Archetype          | Count | Verdict      |
|--------------------|------:|--------------|
| dispatch-ladder    |    14 | refactor     |
| loop-stack         |     9 | refactor     |
| accretion          |     3 | refactor     |
| defensive          |     2 | refactor     |
| state-machine      |     2 | borderline   |
| parser             |     2 | legitimate   |
| try-ladder         |     0 | n/a          |

Of the 192 functions at visual depth >= 4 in the wider data set
(`nesting_metrics.csv`), the top-30 ratios should generalize: ~60-70%
fall into dispatch-ladder or loop-stack patterns that have a small set
of idiom-level fixes. ~10% are legitimate (parsers, state-machines on
real domain hierarchies). The remainder is accretion / defensive that
benefits from helper extraction.
