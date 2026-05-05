# Deep Nesting Review (PROJ-310)

**Status:** Investigation complete. Awaiting user accept/reject/defer
on the recommended follow-up projects.

**Read-only project.** No production source files were modified.

## 1. Executive Summary

The "69.1% of files at 4+ indent levels" figure that motivated this
project is misleading. Two corrections, both produced by the AST tool
in `findings/nesting_analysis.py`:

1. **The right unit of measurement is the function, not the file.**
   A file is flagged the moment any one of its functions is deep, even
   if the rest of the file is fine. At the function level, only **5.6%
   (297 of 5313) of functions reach AST depth >= 4**.
2. **Even that 5.6% double-counts `elif` chains.** Python parses
   `elif` as `If(orelse=[If(...)])`, so a flat 12-way dispatch like
   `if event == A: ... elif event == B: ...` shows AST depth 12 but
   visual depth 1. After distinguishing AST depth from *visual* depth
   (treating elif chains as one level), only **3.6% (192 of 5313)
   functions are genuinely visually nested at 4+ levels**.

Of those 192, the top-30 sample categorizes as: **14 dispatch-ladder**
(refactor with dispatch tables — they are not visually nested but they
are real complexity smells), **9 loop-stack** (refactor with iterator
helpers; the data really is multi-level but the boilerplate is
duplicated), **3 accretion** (refactor by extracting per-section
helpers), **2 defensive** (refactor with early-return guards),
**2 parser** and **2 state-machine** (legitimate, leave alone). The
`try-ladder` archetype is essentially absent — no `try` block in
this codebase contains another `try`.

**Bottom line.** The "69%" headline overstates the problem by an
order of magnitude. The honest figure is closer to **3.6% of functions
deserve attention**, of which roughly 90% fall into two patterns
(dispatch-ladder, loop-stack) that have small idiom-level fixes
covering many sites at once. **20 of the top-30 deeply-nested
functions live in `game/ui/screens/`** — the same area PROJ-309 is
already decomposing — so a substantial fraction of the work is
already in flight.

---

## 2. Quantitative Tables

### 2.1 Top-10 Functions by Visual Depth

These are the functions a human reads as deeply indented. Sorted
visual depth desc, then LOC desc.

| # | Visual | AST | LOC | File | Function |
|--:|-------:|----:|----:|------|----------|
| 1 | 7 | 7 | 175 | `game/ui/screens/builder/layer_panel.py` | `LayerPanel.rebuild` |
| 2 | 7 | 7 | 24  | `game/ui/screens/builder/stat_rows_dynamic.py` | `get_planetary_engineering_rows` |
| 3 | 6 | 6 | 122 | `game/strategy/services/system_effects_collector.py` | `_collect_effects` |
| 4 | 6 | 8 | 114 | `game/simulation/entities/combat_endurance.py` | `calculate_combat_endurance` |
| 5 | 6 | 6 | 86  | `game/ui/components/table/virtual_table.py` | `VirtualTable.update_visible_rows` |
| 6 | 6 | 6 | 69  | `game/strategy/engine/planet_energy_engine.py` | `PlanetEnergyEngine._process_planet` |
| 7 | 6 | 6 | 60  | `game/ui/screens/builder_selection.py` | `process_selection_change` |
| 8 | 6 | 6 | 56  | `game/strategy/quickstart_builder.py` | `QuickstartBuilder.copy_quickstart_designs` |
| 9 | 6 | 6 | 41  | `game/strategy/data/build_queue_source.py` | `colony_has_planetary_yard` |
| 10 | 6 | 6 | 34 | `game/ui/screens/builder/stat_rows_dynamic.py` | `get_planetary_defense_rows` |

### 2.2 Top-10 Files by Aggregate Score

Score = sum of `max(0, max_depth - 3)` over all functions in the file.
Note this uses AST max_depth, so dispatch-ladder offenders score
heavily (they earn a separate refactor anyway).

| # | Score | Deep Funcs | Worst | File |
|--:|------:|-----------:|------:|------|
| 1 | 25 | 6 | 15 | `game/ui/screens/strategy_detail_fmt.py` |
| 2 | 23 | 4 | 14 | `game/ui/screens/strategy_event_router.py` |
| 3 | 23 | 5 | 12 | `game/ui/screens/workshop_event_router.py` |
| 4 | 21 | 2 | 14 | `game/ui/screens/fleet_report_filters.py` |
| 5 | 20 | 6 | 8  | `game/ui/screens/builder/stat_rows_dynamic.py` |
| 6 | 18 | 4 | 13 | `game/ui/screens/builder/layer_panel.py` |
| 7 | 18 | 3 | 10 | `game/ui/screens/strategy_fleet_command_router.py` |
| 8 | 14 | 2 | 14 | `game/ui/screens/battle_setup/input_handler.py` |
| 9 | 11 | 6 | 7  | `game/ui/screens/strategy_click_dispatcher.py` |
| 10| 10 | 4 | 10 | `game/ui/screens/race_setup_screen.py` |

### 2.3 Distribution Histograms

**Visual depth (the real signal):**

| Depth | Count | %      |
|------:|------:|-------:|
|     0 | 2584  | 48.6 % |
|     1 | 1504  | 28.3 % |
|     2 | 665   | 12.5 % |
|     3 | 368   | 6.9 %  |
|     4 | 137   | 2.6 %  |
|     5 | 42    | 0.8 %  |
|     6 | 11    | 0.2 %  |
|     7 | 2     | < 0.1 %|
|   8+  | 0     | 0      |

**AST depth (inflated by elif chains, kept for completeness):**

| Depth | Count |
|------:|------:|
|     0 | 2584  |
|     1 | 1415  |
|     2 | 622   |
|     3 | 395   |
|     4 | 156   |
|     5 | 69    |
|     6 | 31    |
|     7 | 17    |
|     8 | 4     |
|   9+  | 20    |

**Where the 192 visual-depth >= 4 functions live:**

| Count | Subdirectory                  |
|------:|-------------------------------|
|    74 | `game/ui/screens/` (incl. builder/, battle_setup/, test_lab/) |
|    24 | `game/strategy/engine/`       |
|    18 | `game/strategy/data/`         |
|    12 | `game/ui/panels/`             |
|    11 | `game/simulation/entities/`   |
|     9 | `game/strategy/services/`     |
|     5 | `game/simulation/combat/`     |
|     4 | `game/simulation/components/` |
|     4 | `game/ui/components/`         |
|     3 | `game/research/data/`         |

**38% of all visual-deep functions are in `game/ui/screens/`** —
the area PROJ-309 is decomposing. The non-UI deep code is concentrated
in two places: strategy data/engine (loop-stack iteration over saves
and over planets/facilities/components/abilities) and combat endurance
math.

### 2.4 Cross-Reference with `radon` Cyclomatic Complexity

The top-10 by radon cyclomatic complexity (`findings/radon_top30.txt`)
overlaps strongly with the top-10 by AST depth. Examples:

| File::Function | radon CC | AST | Visual |
|----------------|---------:|----:|-------:|
| `race_setup_screen.py::process_event` | 52 | 9 | 5 |
| `battle_setup/input_handler.py::_handle_button` | 37 | 14 | 2 |
| `system_tree_panel.py::set_items` | 31 | 5 | 5 |
| `strategy_detail_fmt.py::format_planet_info` | 28 | 7 | 5 |
| `strategy_detail_fmt.py::_format_orders` | 28 | 15 | 3 |
| `strategy_detail_fmt.py::_collect_effects` | 28 | 6 | 6 |
| `builder/left_panel.py::update_component_list` | 28 | n/a | n/a |
| `game_renderer.py::draw_ship` | 27 | 7 | 5 |
| `formula_evaluator.py::_eval_node` | 27 | n/a | n/a |
| `order_processor.py::process_transfer` | 26 | n/a | n/a |

**Interpretation:** when a function tops one list, it usually appears
on the other. Dispatch-ladder offenders score very high on radon
(they are cyclomatically complex even though visually flat) and high
on AST depth — this is consistent with our diagnosis that they need
a different fix (dispatch table) than the loop-stack offenders
(iterator helper).

---

## 3. Archetype Catalog

### 3.1 dispatch-ladder
**What it looks like.** A long `if/elif/elif/.../else` chain that
matches a discrete event identity (button, key, OrderType, sort field,
UIAction enum) and dispatches to a per-case action. Visually flat
(1-3 indent levels) but cyclomatically complex (CC 25-50).

**Why it appears as deep nesting in some metrics.** Python parses
`elif X:` as `If(test=X, orelse=[next_if])`. Tools that count AST
depth (including some lint plugins) treat this as 12+ levels deep.
The PROJ-310 AST tool surfaces both AST depth and visual depth so the
distinction is explicit.

**Concrete example** — `game/ui/screens/strategy_detail_fmt.py:580-634`:
```python
for i, order in enumerate(fleet.orders):
    if order.type == OrderType.MOVE:
        text += f" {i+1}. MOVE {order.target}<br>"
    elif order.type == OrderType.WARP:
        text += f" {i+1}. WARP through {order.target}<br>"
    elif order.type == OrderType.MOVE_TO_FLEET:
        ...  # 13 more elif branches
```

**Concrete example** — `game/ui/screens/strategy_event_router.py:152`:
40 LOC of `if event.ui_element == ui.btn_X: do_x(); elif ui_element == ui.btn_Y: do_y(); ...` covering 14 buttons.

**Verdict: REFACTOR.** Replace the elif chain with a
`{key: handler}` dict built once at module / `__init__` time. Two
practical idioms cover all cases:
1. **Static** (compile-time keys, e.g. OrderType): module-level
   `_HANDLERS: dict[OrderType, Callable]` constant.
2. **Instance-bound** (runtime UI element references): build the dict
   in `__init__` after pygame_gui creates the buttons.

### 3.2 loop-stack
**What it looks like.** Nested `for` loops over a real multi-level
data structure: `(planet | ship) -> facility/component -> ability/
ability_entry`. The structure mirrors the domain. Visual depth 5-7,
elif_run typically 1-3.

**Concrete example** — `game/strategy/services/system_effects_collector.py:189-246`:
```python
for planet in planets:                                    # depth 1
    if getattr(planet, 'owner_id', None) != empire_id:
        continue
    for facility in planet.facilities:                    # depth 2
        if not getattr(facility, 'is_operational', True):
            continue
        for comp_key, layer_name, comp in iter_keyed_components(facility.design_data):  # depth 3
            abilities = extract_abilities_from_component(comp, registries)
            for ability_name in SYSTEM_EFFECT_ABILITIES:  # depth 4
                ability_data = abilities.get(ability_name)
                if ability_data is None: continue
                entries = ability_data if isinstance(ability_data, list) else [ability_data]
                for entry in entries:                     # depth 5
                    if not isinstance(entry, dict): continue
                    entry_scope = entry.get('scope', 'self')
                    if entry_scope not in allowed_scopes: continue  # depth 6 reached here
                    ...
```

**Concrete example** — `game/ui/screens/builder/stat_rows_dynamic.py:376-433`:
The same shape repeats five times across `get_planetary_engineering_rows`,
`get_planetary_defense_rows`, `get_strategic_modifier_rows`,
`_get_strategic_abilities`, `_get_constant_consumption`. Each iterates
an ability-name dict, then components, then closes over the body to
produce a `getter` callback that re-iterates.

**Verdict: REFACTOR.** The data really is multi-level — the iteration
itself is legitimate. The smell is the duplicated boilerplate. The fix
is an iterator helper:
- `iter_planet_abilities(planet, ability_name) -> Iterator[(facility, comp, entry)]`
- `iter_ship_abilities(ship, ability_name) -> Iterator[(comp, entry)]`
- `first_ship_ability(ship, ability_name) -> Optional[(comp, ability)]`
- `sum_ship_ability_attr(ship, ability_name, attr) -> float`

After extraction, the call site becomes a single flat `for` loop.

### 3.3 accretion
**What it looks like.** A long event handler or formatter (100-200 LOC)
that grew over time, with `PROJ-XX:` markers in comments and discrete
`if event.type == X: ... elif event.type == Y:` blocks each adding more
inline branches. Visual depth 3-5; the depth comes from "I'll just add
one more `if`" rather than a single deep nest.

**Concrete example** — `game/ui/screens/race_setup_screen.py:1443-1596`:
154 LOC. Comments mark PROJ-66 Phase 6, PROJ-299 (multiple), PROJ-12
Phase 4, PROJ-285. Mixes a 30-line LLM-dialog dispatch, button-handler
guards, dropdown handler, slider handler, and text-entry handler in
one function.

**Verdict: REFACTOR.** Split per-event-type handlers
(`_handle_button(e)`, `_handle_dropdown(e)`, `_handle_slider(e)`,
`_handle_text_entry(e)`) and let the top-level become a 6-line
dispatch.

### 3.4 defensive
**What it looks like.** Outer `if obj is not None: if obj.x is not None:
if obj.x.y is not None: ...` chain.

**Concrete example** — `game/ui/screens/strategy_colonization.py::on_colonize_click`,
`PlanetSelectionWindow.update`. Each is 5-6 indent levels purely from
defensive null-checks before the actual logic.

**Verdict: REFACTOR.** Invert each guard into an early `if obj is None:
return` and let the body run flat.

### 3.5 state-machine
**What it looks like.** Branching on a discrete state value (LayerType,
preset section, condition phase) where each branch does substantively
different work. Sometimes legitimate.

**Concrete example** — the LayerType radius elif inside `draw_ship`:
```python
if ltype == LayerType.CORE:
    radius = base_radius * (LayerDefaults.CORE_RADIUS_PCT / 2)
elif ltype == LayerType.INNER:
    radius = base_radius * ((CORE + INNER) / 2)
elif ltype == LayerType.OUTER:
    ...
```

**Verdict: BORDERLINE.** This particular case can be data-driven
(`LAYER_RADIUS_FACTOR: dict[LayerType, float]`) and should be. But
state-machines that genuinely run different code paths per state
(rare here) should stay as elif chains.

### 3.6 parser
**What it looks like.** A function whose nesting *mirrors* the
structure of nested input data — typically a save-game deserializer.

**Concrete example** — `game/simulation/battle_state.py::ShipState.to_ship`,
`game/strategy/engine/game_session.py::GameSession.from_dict`. Both
visual depth 5; both walk a save-dict tree.

**Verdict: LEGITIMATE.** Leave alone. The depth is intrinsic to the
data shape; collapsing it would obfuscate the format.

### 3.7 try-ladder
**What it looks like.** `try` block containing another `try` block.
**Verdict: NOT PRESENT.** No site in this codebase. The category is
empty — no project required.

---

## 4. Recommended Follow-Up Projects

Each recommendation is numbered, sized, scoped to specific files, and
explicitly notes overlap with PROJ-309.

### Recommendation 1: UI Event-Router Dispatch-Table Helper
**Size:** Medium (~3-5 days)
**Files (~14 sites):**
- `game/ui/screens/strategy_event_router.py` (`_handle_button_pressed`, `_handle_window_close`)
- `game/ui/screens/workshop_event_router.py` (`_handle_panel_action`, `_handle_button_pressed`)
- `game/ui/screens/strategy_ui_action_router.py` (`handle_ui_action`)
- `game/ui/screens/strategy_fleet_command_router.py` (`handle_fleet_action`, `handle_detail_action`)
- `game/ui/screens/strategy_input_handler.py` (`_handle_button_press`)
- `game/ui/screens/battle_screen.py` (`_handle_keydown`)
- `game/ui/screens/battle_setup/input_handler.py` (`_handle_button`)
- `game/ui/screens/transfer_dialog.py` (`process_event`)
- `game/ui/screens/builder/modifier_row.py` (`handle_event`)
- `game/ui/screens/builder/layer_panel.py` (`handle_item_action`)
- `game/ui/screens/strategy_detail_formatter.py` (`show_detailed_report`)

**New module:** `game/ui/event_dispatch.py` with:
- `ButtonDispatcher` — `{ui_element: handler}` table built lazily after pygame_gui creation, returns True if dispatched
- `ActionDispatcher` — string/enum keyed table

**Outcome:** ~14 functions drop from AST 8-14 / CC 22-37 to
near-trivial (`return self._dispatcher.dispatch(event.ui_element)`).
Cyclomatic complexity halves across the affected files. Each function
collapses from 30-100 LOC to ~5 LOC + a table.

**Overlap with PROJ-309:** Low. PROJ-309 is decomposing god-class
files; the elif chains it inherits from those files become flat tables
*as a side effect* of extraction, but PROJ-309 is not consciously
designing the dispatcher abstraction. PROJ-310 Recommendation 1
defines the abstraction and applies it broadly. **Run after PROJ-309
phase that touches each file** to avoid merge conflicts.

### Recommendation 2: Ability Iteration Helper Module
**Size:** Medium (~3-5 days)
**Files (~10 sites):**
- `game/strategy/services/system_effects_collector.py` (`_collect_effects`)
- `game/strategy/services/combat_modifier_collector.py` (`collect_combat_modifiers`)
- `game/strategy/engine/planet_energy_engine.py` (`_process_planet`, `_compute_activation_drain`)
- `game/strategy/data/build_queue_source.py` (`colony_has_planetary_yard`, `_get_planetary_yard_size_multiplier`)
- `game/simulation/entities/combat_endurance.py` (`calculate_combat_endurance`)
- `game/ui/screens/builder/stat_rows_dynamic.py` (`get_planetary_engineering_rows`, `get_planetary_defense_rows`, `get_strategic_modifier_rows`, `_get_strategic_abilities`, `_get_constant_consumption`)

**New module:** `game/strategy/services/abilities_iter.py` (or extend
existing `ability_extractor.py`) with:
```python
def iter_planet_abilities(planet, ability_name) -> Iterator[PlanetAbilityCtx]: ...
def iter_ship_abilities(ship, ability_name) -> Iterator[ShipAbilityCtx]: ...
def first_ship_ability(ship, ability_name) -> Optional[Tuple[Component, Ability]]: ...
def sum_ship_ability_attr(ship, ability_name, attr) -> float: ...
```

The PlanetAbilityCtx / ShipAbilityCtx are frozen dataclasses bundling
(facility, comp_key, layer_name, comp, entry) so call sites do not
need to know the iteration shape.

**Outcome:** All ~10 sites drop from visual depth 5-7 to 2-3. The
five-fold duplication in `stat_rows_dynamic.py` collapses to one
implementation. Total LOC reduction estimated at 200-300 lines.

**Overlap with PROJ-309:** None. None of these files are in PROJ-309's
top-10. This is genuinely new work.

### Recommendation 3: OrderType Formatter Registry
**Size:** Small (~1 day)
**Files (3 sites):**
- `game/ui/screens/strategy_detail_fmt.py` (`_format_orders`)
- `game/ui/screens/orders_window.py` (`OrdersWindow._get_order_description`)
- `game/strategy/data/order_types.py` (`Order.to_dict`)

**Approach:** Module-level dict `_ORDER_FORMATTERS: dict[OrderType,
Callable[[Order, IFleet], str]]` shared between `_format_orders` and
`_get_order_description` (currently duplicate the same OrderType
ladder). For `Order.to_dict`, a parallel `_ORDER_TARGET_SERIALIZERS`
dict eliminates the accreted PROJ-102/PROJ-207/PROJ-238 markers.

**Outcome:** Three high-AST-depth functions (15, 9, 10) drop to depth
2 each. Removes a real duplication smell (same OrderType list
maintained in two places).

**Overlap with PROJ-309:** None.

### Recommendation 4: Sort-Field Dispatch Tables
**Size:** Small (~1 day)
**Files (3 sites):**
- `game/ui/screens/fleet_report_filters.py` (`sort_ships`, nested `get_sort_key`)
- `game/ui/screens/star_list_filters.py` (`sort_stars`)
- `game/ui/screens/planet_list_filters.py` (`sort_planets`)

**Approach:** Replace each `if sort_field == "x": key = ... elif
sort_field == "y": ...` with a `{sort_field_name: key_func}` table.

**Outcome:** Three functions (each AST 10-14, CC 12-18) collapse to
~10 LOC each.

**Overlap with PROJ-309:** None.

### Recommendation 5: Layer-Panel Rebuild Decomposition
**Size:** Small (~1-2 days)
**Files (1 site, dominant offender):**
- `game/ui/screens/builder/layer_panel.py` (`LayerPanel.rebuild` and
  related `get_range_selection`)

**Approach:** Extract `_rebuild_layer_header(...)`,
`_rebuild_group_item(...)`, `_rebuild_individual_item(...)`, plus a
small `_cache_or_create(key, ctor)` helper that DRYs up the
duplicated cache hit/miss block at every level.

**Outcome:** `LayerPanel.rebuild` drops from 175 LOC / visual depth 7
to ~40 LOC + three small helpers. This is the worst offender in the
visual-depth ranking.

**Overlap with PROJ-309:** Possible. If `layer_panel.py` is on
PROJ-309's list (check), absorb there. **Otherwise standalone.**

### Recommendation 6: format_planet_info Decomposition
**Size:** Small (~1 day)
**Files (1 site):**
- `game/ui/screens/strategy_detail_fmt.py` (`format_planet_info`)

**Approach:** Extract `_format_mass(planet)`,
`_format_population_block(planet, view)`,
`_format_facilities_block(planet)`,
`_format_ability_status_block(planet)`,
`_format_uncolonized_section(planet, empire, race_registry)`. Top-level
becomes a string-concat of helper outputs.

**Outcome:** 156 LOC / visual depth 5 -> ~30 LOC + 5 helpers.

**Overlap with PROJ-309:** Possibly absorbed if `strategy_detail_fmt.py`
is on PROJ-309's list. Otherwise standalone.

### Recommendation 7: race_setup_screen.process_event Decomposition
**Size:** Small (~1 day) — but **absorbed by PROJ-309**.
**Files:** `game/ui/screens/race_setup_screen.py` (`process_event`)

**Approach:** Per-event-type handler split. Already covered by
Recommendation 1's ButtonDispatcher, plus `_handle_dropdown(e)` /
`_handle_slider(e)` / `_handle_text_entry(e)` per-event helpers.

**Overlap with PROJ-309:** YES — `race_setup_screen.py` is in PROJ-309's
top-10. **Do not run as a separate project**; PROJ-309's decomposition
will subsume it.

### Recommendation 8: Defensive-Chain Sweep
**Size:** Small (~1 day)
**Files:** ~8-12 specific sites identified by re-running the AST tool
filtered to `visual_depth >= 4 AND elif_run <= 1 AND
longest_ladder_kind starts with 'if->if'`.

Examples found in this review:
- `game/ui/screens/strategy_colonization.py::on_colonize_click`
- `game/ui/screens/planet_selection_window.py::PlanetSelectionWindow.update`
- `game/ui/screens/builder_selection.py::process_selection_change`

**Approach:** Mechanical: replace nested null-check pyramids with
early-return guards. No new abstractions.

**Outcome:** ~10 functions drop from depth 5-6 to depth 2-3.

**Overlap with PROJ-309:** Low. Some sites may live in files PROJ-309
will touch; check before scheduling. Recommend running this LAST so
it can fix what's left after PROJ-309 + Recommendation 1.

---

## 5. What NOT to Refactor

Future agents reading this review must NOT propose deep-nesting fixes
for the following sites. The depth is intrinsic to the problem.

### `game/simulation/battle_state.py::ShipState.to_ship`
Visual depth 5. Save-game deserializer mirroring the ShipState dict
shape. The nesting follows the persisted format and obfuscation is
the expected outcome of "fixing" it.

### `game/strategy/engine/game_session.py::GameSession.from_dict`
Visual depth 5. Same reasoning — top-level save deserializer. The
shape of the function reflects the shape of the save file.

### `game/ui/screens/planet_list_presets.py::apply_planet_list_state`
Visual depth 5. State-machine over preset categories. Each branch
applies a distinct configuration block to the panel; the structure
mirrors the preset taxonomy and is regular.

### `game/simulation/entities/ship_layer_manager.py::ShipLayerManager.change_class`
Visual depth 5. Domain logic that re-layers components when a ship's
class changes. The nesting reflects the layer-by-layer redistribution
algorithm. Borderline — could marginally benefit from helper extraction
but it is not adding a meaningful clarity win for the risk.

### `game/engine/collision.py::CollisionSystem.process_beam_attack`
Visual depth 5. Hot path for combat. The nesting is target-resolution
guards (target alive? in range? line of sight?). Can be flattened with
early-return but this is performance-sensitive code; **do not touch
without profile data**.

### `game/strategy/data/planet_gen.py::PlanetGenerator._determine_type`
Not in top-30 by visual depth but appears at radon CC 22 — likely a
genuine state-machine dispatching planet types based on stellar
parameters. Treat as state-machine archetype; keep elif chain unless
a clear data-driven equivalent emerges.

### Functions whose ladder is dominated by elif (`elif_run >= visual_depth`)
The 14 dispatch-ladder offenders are flagged for refactor in
Recommendation 1, BUT they are NOT visually nested and do NOT need
"de-nesting" — they need a dispatch table. Future reviewers must not
classify a 12-elif ladder as "deeply nested code that should be
flattened with helper extraction."

---

## 6. Summary of Recommendations

| # | Title                                        | Size  | Sites | Overlap PROJ-309 |
|--:|----------------------------------------------|-------|------:|------------------|
| 1 | UI event-router dispatch-table helper        | M     | ~14   | Run after PROJ-309 file decompositions |
| 2 | Ability iteration helper module              | M     | ~10   | None             |
| 3 | OrderType formatter registry                 | S     | 3     | None             |
| 4 | Sort-field dispatch tables                   | S     | 3     | None             |
| 5 | LayerPanel.rebuild decomposition             | S     | 1     | Check first      |
| 6 | format_planet_info decomposition             | S     | 1     | Possibly         |
| 7 | race_setup_screen.process_event              | -     | 1     | **ABSORBED**     |
| 8 | Defensive-chain sweep                        | S     | ~10   | Low; run last    |

**Recommended ordering (assuming PROJ-309 continues in parallel):**
1. PROJ-309 phases that touch `race_setup_screen.py`, `strategy_detail_fmt.py`,
   `layer_panel.py` (subsumes Recs 5, 6, 7 if the file is on PROJ-309's list)
2. Recommendation 2 (ability iteration helper) — independent of UI
   work, biggest LOC win
3. Recommendation 3 (OrderType formatter registry) — small, removes
   real duplication
4. Recommendation 4 (sort-field dispatch tables) — small
5. Recommendation 1 (event-router dispatcher) — after PROJ-309 stabilizes
   the affected files
6. Recommendation 8 (defensive-chain sweep) — sweep what remains

---

## 7. User Review Annotations

*(To be filled in by user when reviewing this document.)*

| Rec # | Status (ACCEPT / REJECT / DEFER) | Notes |
|------:|----------------------------------|-------|
|     1 |                                  |       |
|     2 |                                  |       |
|     3 |                                  |       |
|     4 |                                  |       |
|     5 |                                  |       |
|     6 |                                  |       |
|     7 |                                  | (already absorbed by PROJ-309) |
|     8 |                                  |       |
