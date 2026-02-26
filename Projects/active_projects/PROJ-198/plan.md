# PROJ-198: UI Layer Duck Typing Elimination - Strategy Screens & Services

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-198` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-198 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Trivial Guard Removal - Direct Access | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Init Declarations & Guard Removal | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Monkey-Patch Elimination | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Bug Fixes & Dead Code Removal | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Type Annotations & Protocol Fixes | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Superweapon Stub Methods & Final Cleanup | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-25
**Current Phase:** Phase 2 Complete
**Last Agent Action:** Phase 2 executed - ~20 init declarations + guard removals across 12 files
**Next Action:** Execute Phase 3 - Monkey-Patch Elimination
**Blockers:** None
**Context for Next Agent:** Phase 2 complete. Added init declarations for: build_queue_screen, crew_onboard/crew_required, id (Ship/Projectile), is_hovered, design_rows, _dropdown_expanded. Removed ~20 hasattr/getattr guards. Deleted 5 obsolete tests. Tests: 12728 passed.

## Overview
Eliminate ~223 remaining actionable `hasattr()`/`getattr()` duck typing instances across the UI layer (strategy screens, services, panels). This is the final phase of the duck typing elimination initiative that began with PROJ-190 (Core Simulation), continued through PROJ-191 (Strategy), PROJ-192 (AI), PROJ-193 (UI Data Binding), and PROJ-194 (Builder/Workshop).

Deep code review revealed that **~70% of instances are unnecessary defensive guards** on attributes that always exist. The plan is organized by fix type (simplest first) rather than by file, maximizing velocity on easy wins before tackling structural changes.

## Goals
- Remove all unnecessary `hasattr`/`getattr` calls in strategy UI screens and services
- Fix 4 discovered bugs/dead code paths masked by duck typing
- Eliminate 3 monkey-patching anti-patterns (replace with dicts/proper init)
- Add `__init__` declarations for dynamically-set attributes
- Add type annotations where they enable guard removal
- Ensure no regressions in 12734-test suite

## Scope
**In Scope:**
- `game/ui/screens/strategy_*.py` — ~80 instances across 14 files
- `game/ui/screens/empire_*.py` — ~10 instances across 2 files
- `game/ui/screens/planet_*.py` — ~20 instances across 3 files
- `game/ui/screens/build_queue_*.py` — ~8 instances across 2 files
- `game/ui/screens/fleet_orders_window.py` — 1 instance
- `game/ui/screens/design_selector_window.py` — ~5 instances
- `game/ui/screens/galaxy_test/` — ~8 instances across 2 files
- `game/ui/screens/race_asset_loader.py` — 2 instances
- `game/ui/screens/builder/` — 6 instances (not covered by PROJ-194)
- `game/ui/screens/builder_selection.py` — 1 instance
- `game/ui/screens/workshop_viewmodel.py` — 1 instance
- `game/ui/services/battle_ui_service.py` — ~25 instances
- `game/ui/services/battle_factories.py` — 1 instance
- `game/ui/services/screenshot_manager.py` — 4 instances
- `game/ui/services/ship_io.py` — 1 instance
- `game/ui/services/input_mapper.py` — 2 instances
- `game/ui/panels/battle_panels.py` — ~20 instances

**Out of Scope (Globally Exempt — Keep As-Is):**
- `keybindings_scene.py` L63-64 — module introspection on `dir(pygame)` (idiomatic)
- `input_mapper.py` L158 — dynamic pygame constant lookup via `getattr(pygame, key_name)` (idiomatic)
- `modifier_row.py` L177 — pygame_gui version compatibility guard (legitimate library compat)
- Generic column traversal in `planet_data_source.py` L160-161 and `planet_list_filters.py` L136-137/163-164 — dotted-path data-binding utility (intentional dynamic dispatch)
- All instances already excluded by PROJ-193/194 global exemptions (self-init guards, pygame event polling, stats_config.py dispatch)

## Key Files Reference
| Component | File Path | Key Info |
|-----------|-----------|----------|
| Strategy Screen | `game/ui/screens/strategy_screen.py` | `galaxy` (prop L132), `current_empire` (prop L157), `input_mode` (prop L172), `facade` (prop L163), `_quit_confirm_dialog` (L110), `on_ui_selection` (method L285), `on_design_click` (method L330), `request_colonize_order` (method L266). Missing: `build_queue_screen` not in `__init__` |
| Strategy UI | `game/ui/screens/strategy_ui.py` | `show_system_picker` (L347), `_has_modal_open` (L321). Missing: `show_confirmation_dialog`, `show_ship_picker` |
| Game Session | `game/strategy/engine/game_session.py` | `save_path` (L78, init=None), `turn_engine` (L85), `empires` (L90) |
| Ship Entity | `game/simulation/entities/ship.py` | Missing: `id`, `crew_onboard`, `crew_required` |
| Projectile Entity | `game/simulation/entities/projectile.py` | Missing: `id`. Has all other attrs in `__init__` |
| Planet | `game/strategy/data/planet.py` | All fields always present: `owner_id`(L232), `image_id`(L249), `image_rotation`(L250), `surface_gravity`(L206), `surface_temperature`(L210), `mass`(L202), `resources`(L237), `location`(L198) |
| Galaxy | `game/strategy/data/galaxy.py` | Does NOT have `empires`. Empires are on GameSession. |
| Star | `game/strategy/data/stars.py` | `color` (L109, required dataclass field) |
| Empire | `game/strategy/data/empire.py` | `empire_theme_id`(L19, default="Federation"), `flag_id`(L21, default="") |
| Fleet | `game/strategy/data/fleet.py` | `location`(L126), `owner_id`(L125), `name`(prop L146), `construction_queue`(L135) |
| Component | `game/simulation/components/component.py` | `status`(L125), `has_ability`(L223), `shots_fired`(L159), `shots_hit`(L160), `get_ui_rows`(exists) |
| BattleScreen | `game/ui/screens/battle_screen.py` | `test_mode`(L110), `is_battle_over`(L527), `ui_service`(prop L192) |
| CombatScenario | `test_framework/scenario.py` | `max_ticks`(L16, default=1000) |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-25 | Organize phases by fix type, not by file | Front-loads easy wins; ~90 trivial deletions in Phase 1 before any structural work |
| 2026-02-25 | Keep keybindings/input_mapper/modifier_row/column-traversal exempt | Legitimate dynamic dispatch / library compat patterns |
| 2026-02-25 | Add `id` to Ship and Projectile via `str(id(self))` | Eliminates `getattr(x, 'id', id(x))` pattern in 3+ locations |
| 2026-02-25 | Init `crew_onboard`/`crew_required` = 0 in Ship.__init__ | Currently set dynamically by ShipStatsCalculator; init to 0 makes safe |
| 2026-02-25 | Init `build_queue_screen = None` in StrategyScreen.__init__ | Single change eliminates 5+ hasattr checks across 3 files |
| 2026-02-25 | Replace monkey-patched UIButton attrs with dict lookups | 3 locations: design_selector_window, build_queue_selector, fleet_orders_window |
| 2026-02-25 | Fix planet_list_filters.get_owner_name to accept empires param | Galaxy has no `empires` — current code is dead |
| 2026-02-25 | Add stub `show_confirmation_dialog` and `show_ship_picker` to StrategyUI | Currently missing methods; hasattr guards always fail |
| 2026-02-25 | fleet_orders_window: filter by key name instead of hasattr | Row dicts have known keys; `order_ref` is the only non-UI value |

## Initial Analysis
Deep code review (3 parallel Explore agents + 2 verification agents) analyzed all 223 instances against their target types.

### Category Breakdown
| Fix Type | Count | Phase |
|----------|-------|-------|
| Delete unnecessary guard (attr always exists) | ~90 | Phase 1 |
| Initialize in `__init__`, then delete guard | ~15 | Phase 2 |
| Replace monkey-patching with dicts | ~6 | Phase 3 |
| Bug fixes / dead code removal | ~4 | Phase 4 |
| Add type annotations to enable removal | ~20 | Phase 5 |
| Add stub methods + final cleanup | ~8 | Phase 6 |
| Keep as-is (legitimate dynamic patterns) | ~10 | Exempt |

### Bugs Discovered
1. **`strategy_detail_formatter.py` L346** — `hasattr(self.scene, 'turn_engine')` always False; `turn_engine` is on `session`, not on `StrategyScreen`. Colonize button validation never executes.
2. **`strategy_input_handler.py` L61** — `hasattr(self.scene.ui, 'planet_list_window')` always False; `planet_list_window` is on `StrategyWindowManager`, not `StrategyUI`. Early-return branch never triggers.
3. **`planet_list_filters.py` L260** — `hasattr(galaxy, 'empires')` always False; Galaxy has no `empires` attribute. Owner name lookup block is dead code.
4. **`empire_build_queue_formatter.py` L112** — `getattr(entity, 'global_hex', None)` always None; Planet has no `global_hex`. Falls through to `location` which gives local (not global) coordinates.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Trivial Guard Removal — Direct Access [Simple]
**Objective:** Remove ~90 unnecessary `hasattr`/`getattr` guards where the attribute always exists on the target type. Pure subtraction — no new code, just deletions.
**Status:** Not Started

#### Task 1.1: Planet Attribute Guards [Simple]
**File:** `game/ui/screens/planet_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`
- [ ] L185: Remove `hasattr(planet, "image_id")` — `Planet.image_id` always exists (L249 planet.py). Change to `if not planet.image_id:`
- [ ] L189: Replace `getattr(planet, "image_rotation", 0) or 0` with `planet.image_rotation or 0`

#### Task 1.2: Planet List Filter Guards [Simple]
**File:** `game/ui/screens/planet_list_filters.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`
- [ ] L70: Replace `getattr(p, 'owner_id', None)` with `p.owner_id`
- [ ] L202: Remove `if hasattr(p, 'surface_gravity'):` — always True. Keep body indented correctly.
- [ ] L205: Remove `if hasattr(p, 'surface_temperature'):` — always True. Keep body.
- [ ] L208: Remove `if hasattr(p, 'mass'):` — always True. Keep body.
- [ ] L297: Remove `hasattr(planet, 'resources')`. Change to `if resource_name in planet.resources:`

#### Task 1.3: Race Asset Loader Guards [Simple]
**File:** `game/ui/screens/race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/screens/ -k race --testmon`
- [ ] L269: Remove `hasattr(empire, 'empire_theme_id')`. Change to `if empire.empire_theme_id:`
- [ ] L274: Remove `hasattr(empire, 'flag_id')`. Change to `if empire.flag_id:`

#### Task 1.4: Empire Build Queue Formatter Guards [Simple]
**File:** `game/ui/screens/empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/ -k empire --testmon`
- [ ] L86: Replace `getattr(sys_obj, 'name', '-')` with `sys_obj.name`
- [ ] L88: Replace `getattr(entity, 'location', None)` with `entity.location`
- [ ] L92: Replace `getattr(sys_obj, 'name', '-')` with `sys_obj.name`
- [ ] L107: Replace `getattr(entity, 'location', None)` with `entity.location`

#### Task 1.5: Empire Build Queue Window Guard [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k empire --testmon`
- [ ] L328: Replace `getattr(entity, 'location', None)` with `entity.location`

#### Task 1.6: Strategy Screen Guards — Always-Exist Properties [Simple]
**Files:** Multiple strategy_*.py files
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] `strategy_click_dispatcher.py` L524: Remove `hasattr(self.scene, 'galaxy')`. Keep `if self.scene.galaxy:`
- [ ] `strategy_colonization.py` L82-83: Replace triple-defense with `if self.scene.galaxy:` then direct `self.scene.galaxy.get_zones_at_global_hex`
- [ ] `strategy_colonization.py` L196-197: Same pattern as L82-83
- [ ] `strategy_detail_formatter.py` L208: Remove `hasattr(self.scene, 'current_empire')`. Use `if self.scene.current_empire:`
- [ ] `strategy_event_router.py` L88: Remove `hasattr(self.ui.scene, 'on_ui_selection')`. Call directly.
- [ ] `strategy_event_router.py` L131: Remove `hasattr(self.ui.scene, '_quit_confirm_dialog')`. Use `if event.ui_element == self.ui.scene._quit_confirm_dialog:`
- [ ] `strategy_event_router.py` L149: Remove `hasattr(ui.scene, 'on_design_click')`. Call directly.
- [ ] `strategy_event_router.py` L191: Remove `hasattr(ui.scene, 'galaxy')`. Use `if not ui.scene.galaxy:`
- [ ] `strategy_event_router.py` L213: Remove `hasattr(ui.scene, 'request_colonize_order')`. Call directly.
- [ ] `strategy_event_router.py` L218: Remove `hasattr(ui.scene, 'request_colonize_order')`. Call directly.
- [ ] `strategy_renderer.py` L122: Replace `getattr(self.scene, 'input_mode', 'SELECT')` with `self.scene.input_mode`
- [ ] `strategy_ui.py` L256: Remove `hasattr(self.scene, '_get_object_asset')`. Call directly.
- [ ] `strategy_ui.py` L285: Remove `hasattr(self.scene, 'current_empire')`. Use `if not self.scene.current_empire:`
- [ ] `strategy_window_manager.py` L202: Remove `hasattr(self.scene, "facade")`. Use `self.scene.facade` directly.

#### Task 1.7: Strategy Build Queue Manager Guards [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] L63: Replace `getattr(self._screen.session, 'save_path', None)` with `self._screen.session.save_path`
- [ ] L178: Replace `getattr(self._screen.session, 'save_path', None)` with `self._screen.session.save_path`
- [ ] L221: Replace `getattr(self._screen.session, 'save_path', None)` with `self._screen.session.save_path`

#### Task 1.8: Strategy Game State Manager Guards [Simple]
**File:** `game/ui/screens/strategy_game_state_manager.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] L110: Replace `getattr(self._screen.session, 'turn_engine', None)` with `self._screen.session.turn_engine`
- [ ] L113: Replace `getattr(turn_engine, 'last_scuttle_events', [])` with `turn_engine.last_scuttle_events`

#### Task 1.9: Strategy Detail Format Guards [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] L302: Replace `getattr(order.target, 'name', 'Unknown')` with `order.target.name if order.target else 'Unknown'`
- [ ] L305: Replace `getattr(fleet, 'construction_queue', [])` with `fleet.construction_queue`

#### Task 1.10: Galaxy Test Screen Guards [Simple]
**File:** `game/ui/screens/galaxy_test/screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k galaxy --testmon`
- [ ] L214-224: Replace all `getattr(..., None)` with direct attribute access:
  - `getattr(self, 'btn_galaxy', None)` → `self.btn_galaxy`
  - `getattr(self, 'btn_system', None)` → `self.btn_system`
  - `getattr(self, 'btn_close', None)` → `self.btn_close`
  - `getattr(self.system_helper, 'btn_back', None)` → `self.system_helper.btn_back`
  - `getattr(self.galaxy_helper, 'btn_back', None)` → `self.galaxy_helper.btn_back`
  - `getattr(self.galaxy_helper, 'btn_generate', None)` → `self.galaxy_helper.btn_generate`
  - `getattr(self.system_helper, 'btn_generate_system', None)` → `self.system_helper.btn_generate_system`

#### Task 1.11: Galaxy Test System Mode Guard [Simple]
**File:** `game/ui/screens/galaxy_test/system_mode.py`
**Tests:** `pytest tests/unit/ui/screens/ -k galaxy --testmon`
- [ ] L520: Replace `star.color if hasattr(star, 'color') else (255, 255, 200)` with `star.color`

#### Task 1.12: Battle UI Service — Component Guards [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`
- [ ] L228: Remove `hasattr(comp, 'status') and hasattr(comp.status, 'name')`. Use `comp.status.name.lower()` directly.
- [ ] L233: Remove `hasattr(comp, 'has_ability')`. Call `comp.has_ability(...)` directly.
- [ ] L244-245: Replace `getattr(comp, 'shots_fired', 0)` and `getattr(comp, 'shots_hit', 0)` with direct access.

#### Task 1.13: Battle UI Service — Projectile Guards [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`
- [ ] L259: Replace `getattr(proj, 'target', None)` with `proj.target`
- [ ] L267: Replace `getattr(proj, 'type', None)` with `proj.type`
- [ ] L275: Replace `getattr(proj, 'radius', 4.0)` with `proj.radius`
- [ ] L277: Replace `getattr(proj, 'hp', 0.0)` with `proj.hp`
- [ ] L278: Replace `getattr(proj, 'max_hp', 0.0)` with `proj.max_hp`
- [ ] L279: Replace `getattr(proj, 'status', 'active')` with `proj.status`
- [ ] L280: Replace `getattr(proj, 'endurance', 0.0)` with `proj.endurance`
- [ ] L281: Replace `getattr(proj, 'max_endurance', 0.0)` with `proj.max_endurance`
- [ ] L283: Replace `getattr(proj, 'max_speed', 0.0)` with `proj.max_speed`

#### Task 1.14: Battle Panels — Projectile Guards [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`
- [ ] L353: Replace `getattr(proj, 'status', 'active')` with `proj.status`
- [ ] L401: Replace `getattr(proj, 'max_speed', p_vel_len)` with `proj.max_speed`
- [ ] L407: Replace `getattr(proj, 'hp', 0)` with `proj.hp`
- [ ] L408: Replace `getattr(proj, 'max_hp', hp)` with `proj.max_hp`
- [ ] L418: Replace `getattr(proj, 'endurance', 0)` with `proj.endurance`
- [ ] L419: Replace `getattr(proj, 'max_endurance', ...)` with `proj.max_endurance`
- [ ] L434: Replace `getattr(proj, 'target', None)` with `proj.target`
- [ ] L435: Remove `hasattr(target, 'name')` guard. Target is always a Ship.

#### Task 1.15: Battle Factories Guard [Simple]
**File:** `game/ui/services/battle_factories.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`
- [ ] L133: Replace `scenario.max_ticks if hasattr(scenario, 'max_ticks') else 100000` with `scenario.max_ticks`

#### Task 1.16: Ship IO Guard [Simple]
**File:** `game/ui/services/ship_io.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`
- [ ] L142: Replace `getattr(new_ship, '_loading_warnings', [])` with `new_ship._loading_warnings`

#### Task 1.17: Builder/Workshop Remaining Guards [Simple]
**Files:** Multiple builder files
**Tests:** `pytest tests/unit/ui/screens/builder/ --testmon`
- [ ] `builder/left_panel.py` L254: Replace `getattr(self.builder.ship, 'vehicle_type', "Ship")` with `self.builder.ship.vehicle_type`
- [ ] `builder/schematic_view.py` L71: Replace `getattr(ship, 'theme_id', 'Federation')` with `ship.theme_id`
- [ ] `builder/detail_panel.py` L145: Remove `hasattr(comp, 'get_ui_rows')`. Call `comp.get_ui_rows()` directly.

#### Task 1.18: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12734 tests pass
**Notes:**

---

### Phase 2: Init Declarations & Guard Removal [Simple]
**Objective:** Add missing `__init__` declarations for dynamically-set attributes, then remove the hasattr guards that check for them.
**Status:** Not Started

#### Task 2.1: StrategyScreen — build_queue_screen Init [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] Add `self.build_queue_screen = None` in `__init__` (near L110 where other UI attrs are initialized)
- [ ] `strategy_event_router.py` L58: Remove `hasattr(...)`. Change to `if self.ui.scene.build_queue_screen is not None:`
- [ ] `strategy_input_handler.py` L56: Remove `hasattr(...)`. Change to `if self.scene.build_queue_screen is not None:`
- [ ] `strategy_build_queue_manager.py` L44: Remove `hasattr(...)`. Change to `if self._screen.build_queue_screen is not None:`
- [ ] `strategy_build_queue_manager.py` L155: Same pattern
- [ ] `strategy_build_queue_manager.py` L202: Same pattern
- [ ] `screenshot_manager.py` L155: Remove `hasattr(...)`. Change to `if scene.build_queue_screen:`

#### Task 2.2: Ship — crew_onboard / crew_required Init [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ --testmon`
- [ ] Add `self.crew_onboard: int = 0` in `__init__` (near other status attrs)
- [ ] Add `self.crew_required: int = 0` in `__init__`
- [ ] `battle_ui_service.py` L205-206: Replace `getattr(ship, 'crew_onboard', 0)` / `getattr(ship, 'crew_required', 0)` with direct access

#### Task 2.3: Ship & Projectile — id Attribute [Simple]
**File:** `game/simulation/entities/ship.py`, `game/simulation/entities/projectile.py`
**Tests:** `pytest tests/unit/simulation/ --testmon`
- [ ] Add `self.id: str = str(id(self))` in `Ship.__init__`
- [ ] Add `self.id: str = str(id(self))` in `Projectile.__init__`
- [ ] `battle_ui_service.py` L180: Replace `getattr(ship, 'id', id(ship))` with `ship.id`
- [ ] `battle_ui_service.py` L264: Replace `getattr(proj, 'id', id(proj))` with `proj.id`
- [ ] `battle_panels.py` L71-79: Simplify `_get_ship_id` to use `ship.id` (handle DTO and domain)
- [ ] `battle_panels.py` L275-279: Simplify `_get_projectile_id` to use `proj.id`

#### Task 2.4: ComponentListItem — is_hovered Init [Simple]
**File:** `game/ui/screens/builder/components.py`
**Tests:** `pytest tests/unit/ui/screens/builder/ --testmon`
- [ ] Add `self.is_hovered: bool = False` in `ComponentListItem.__init__`
- [ ] `builder/left_panel.py` L352: Replace `getattr(item, 'is_hovered', False)` with `item.is_hovered`

#### Task 2.5: DesignSelectorWindow — design_rows Init [Simple]
**File:** `game/ui/screens/design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k design --testmon`
- [ ] Add `self.design_rows = []` in `__init__` before the call to `_refresh_designs()`
- [ ] L285: Remove `hasattr(self, 'design_rows')` guard. Keep the for-loop body.

#### Task 2.6: BuilderLeftPanel — _dropdown_expanded Init [Simple]
**File:** `game/ui/screens/builder/left_panel.py`
**Tests:** `pytest tests/unit/ui/screens/builder/ --testmon`
- [ ] Add `self._dropdown_expanded: bool = False` in `__init__`
- [ ] L214: Replace `getattr(self, '_dropdown_expanded', False)` with `self._dropdown_expanded`

#### Task 2.7: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12734 tests pass
**Notes:**

---

### Phase 3: Monkey-Patch Elimination [Medium]
**Objective:** Replace 3 monkey-patching anti-patterns (stamping attributes on library UIButton objects) with proper dict lookups.
**Status:** Not Started

#### Task 3.1: DesignSelectorWindow — Button Identification [Medium]
**File:** `game/ui/screens/design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k design --testmon`
- [ ] Add `self._button_design_map: Dict[UIButton, str] = {}` in `__init__`
- [ ] Add `self._obsolete_buttons: Set[UIButton] = set()` in `__init__`
- [ ] Add `self._obsolete_state_map: Dict[UIButton, bool] = {}` in `__init__`
- [ ] L403-405: Replace monkey-patches with dict entries:
  ```python
  self._button_design_map[obsolete_btn] = design.design_id
  self._obsolete_buttons.add(obsolete_btn)
  self._obsolete_state_map[obsolete_btn] = design.is_obsolete
  ```
- [ ] L417: Replace `select_btn.design_id = ...` with `self._button_design_map[select_btn] = design.design_id`
- [ ] L459: Replace `hasattr(event.ui_element, 'is_obsolete_button')` with `event.ui_element in self._obsolete_buttons`
- [ ] L464: Replace `hasattr(event.ui_element, 'design_id')` with `event.ui_element in self._button_design_map`; access via `self._button_design_map[event.ui_element]`
- [ ] Clear all three dicts/sets at top of `_rebuild_design_list()` before rebuilding
- [ ] Update any other references to `current_obsolete_state` to use the map

#### Task 3.2: BuildQueueSelector — Button Index [Medium]
**File:** `game/ui/screens/build_queue_selector.py`
**Tests:** `pytest tests/unit/ui/screens/ -k build_queue --testmon`
- [ ] Add `self._button_index_map: Dict[UIButton, int] = {}` in `__init__`
- [ ] L117: Replace `btn.queue_source_index = idx` with `self._button_index_map[btn] = idx`
- [ ] L140: Replace `hasattr(button, 'queue_source_index')` with `button in self._button_index_map`
- [ ] Replace all `button.queue_source_index` access with `self._button_index_map[button]`
- [ ] Clear dict when rebuilding buttons

#### Task 3.3: FleetOrdersWindow — Row Cleanup [Simple]
**File:** `game/ui/screens/fleet_orders_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k fleet --testmon`
- [ ] L93-95: Replace `hasattr(element, 'kill')` with explicit key exclusion:
  ```python
  for key, element in row.items():
      if key != 'order_ref':
          element.kill()
  ```

#### Task 3.4: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12734 tests pass
**Notes:**

---

### Phase 4: Bug Fixes & Dead Code Removal [Medium]
**Objective:** Fix 4 discovered bugs/dead code paths that were masked by duck typing.
**Status:** Not Started

#### Task 4.1: Fix strategy_detail_formatter.py — turn_engine Path [Medium]
**File:** `game/ui/screens/strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] L346: `hasattr(self.scene, 'turn_engine')` always False. `turn_engine` lives on `self.scene.session`.
  - Fix to `self.scene.session.turn_engine` or remove block if truly unnecessary
- [ ] Investigate what the colonize button validation inside the block does
- [ ] Add a test verifying the corrected behavior
**Notes:** Dead code — colonize button validation never ran.

#### Task 4.2: Fix strategy_input_handler.py — planet_list_window Path [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] L61: `hasattr(self.scene.ui, 'planet_list_window')` always False. `planet_list_window` lives on `StrategyWindowManager`.
  - Fix to correct path through window_manager, or use `self.scene.ui._has_modal_open()` if intent is modal check
- [ ] Investigate what early-return behavior was intended
- [ ] Add a test verifying the corrected behavior
**Notes:** Dead code — planet list window event routing never triggered.

#### Task 4.3: Fix planet_list_filters.py — empires Lookup [Medium]
**File:** `game/ui/screens/planet_list_filters.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`
- [ ] L260: `hasattr(galaxy, 'empires')` always False. Galaxy has no `empires`.
- [ ] Change `get_owner_name()` to accept an `empires` list parameter
- [ ] Update caller in `planet_list_window.py` L83 to pass empires from session
- [ ] Remove the dead `hasattr` guard
- [ ] Also remove `_temp_system_ref` monkey-patch (L27) — use lookup dict `{planet_id: system_name}` instead
- [ ] Update `get_system_name()` (L240) to use the dict
- [ ] Add/update tests
**Notes:** The `_temp_system_ref` monkey-patch on Planet dataclass is a secondary issue worth fixing here.

#### Task 4.4: Fix empire_build_queue_formatter.py — Dead Code [Medium]
**File:** `game/ui/screens/empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/ -k empire --testmon`
- [ ] L79: Remove dead `getattr(entity, 'system_name', None)` block — Planet has no `system_name`
- [ ] L112: Remove dead `getattr(entity, 'global_hex', None)` — Planet has no `global_hex`
  - Determine if global coords are needed; if so, use `galaxy.get_planet_global_hex()`
  - If local coords are sufficient, simplify to `entity.location`
- [ ] Add tests for correct behavior
**Notes:** Line 112 may be a semantic bug — code wants global coordinates but gets local.

#### Task 4.5: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All tests pass
**Notes:**

---

### Phase 5: Type Annotations & Protocol Fixes [Medium]
**Objective:** Add type annotations to untyped parameters to enable removing remaining hasattr/getattr guards.
**Status:** Not Started

#### Task 5.1: Battle UI Service — Type Parameters [Medium]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`
- [ ] Add TYPE_CHECKING imports for Ship, Component, Projectile, ICombatShip
- [ ] Type conversion method parameters
- [ ] L170, L176: Replace `hasattr(target, 'name')` with `isinstance` check or typed access
- [ ] L260: Same pattern for projectile target

#### Task 5.2: Battle Panels — Scene Typing [Medium]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`
- [ ] Add TYPE_CHECKING import for `BattleScreen`
- [ ] Type `self.scene` as `BattleScreen`
- [ ] L38, L49: Remove `getattr(self.scene, 'ui_service', None)` fallback
- [ ] L496-498: Remove `hasattr(self.scene, 'test_mode')` and `hasattr(self.scene, 'is_battle_over')`

#### Task 5.3: Screenshot Manager — Scene Typing [Simple]
**File:** `game/ui/services/screenshot_manager.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`
- [ ] Add TYPE_CHECKING import for `StrategyScreen`
- [ ] Type the scene parameter
- [ ] L149: Remove `hasattr(scene, 'ui')`. Use `if scene.ui:` directly.
- [ ] L161-162: Replace `getattr(scene, 'SIDEBAR_WIDTH', 300)` / `getattr(scene, 'TOP_BAR_HEIGHT', 40)` with direct access

#### Task 5.4: Strategy Input Handler — Modal Check [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] L163: Remove double `hasattr`. Call `self.scene.ui._has_modal_open()` directly.

#### Task 5.5: Builder Type Discrimination [Simple]
**Files:** `game/ui/screens/builder/detail_panel.py`, `builder_selection.py`, `workshop_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/builder/ --testmon`
- [ ] `detail_panel.py` L95: Replace `hasattr(selection_data, 'id')` with `isinstance(selection_data, Component)`
- [ ] `builder_selection.py` L22: Replace `hasattr(item, 'id')` with `isinstance(item, Component)`
- [ ] `workshop_viewmodel.py` L166: Replace `hasattr(item, 'id')` with `isinstance(item, Component)`
- [ ] Add TYPE_CHECKING import for Component where needed

#### Task 5.6: Build Queue Screen — Type Validation [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k build_queue --testmon`
- [ ] L177, L183: Replace `hasattr(build_context, 'owner_id')` / `hasattr(build_context, 'name')` with isinstance check against Planet/Fleet or a typed union
- [ ] L179: Keep `getattr(build_context, 'name', 'unknown')` in error path (acceptable)

#### Task 5.7: Strategy Build Queue Manager — queue_sources [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] L97: Replace `getattr(self._screen.build_queue_screen, 'queue_sources', [])` with direct `self._screen.build_queue_screen.queue_sources`

#### Task 5.8: Input Mapper — Event Typing [Simple]
**File:** `game/ui/services/input_mapper.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`
- [ ] L204: Replace `getattr(event, "type", None)` with `event.type`. Type parameter as `pygame.event.Event`.

#### Task 5.9: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All tests pass
**Notes:**

---

### Phase 6: Superweapon Stub Methods & Final Cleanup [Medium]
**Objective:** Add missing UI methods that superweapons module expects, handle remaining edge cases, and do final audit.
**Status:** Not Started

#### Task 6.1: StrategyUI — Add Missing Methods [Medium]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] Add `show_confirmation_dialog(title, message, on_confirm, is_warning=False)` method
  - Implement using existing pygame_gui confirmation dialog pattern
- [ ] Add `show_ship_picker(ships, ability_name, on_selected)` method
  - Implement minimal ship selection dialog
- [ ] `strategy_superweapons.py` L374: Remove `hasattr`. Call `self.scene.ui.show_confirmation_dialog(...)` directly.
- [ ] `strategy_superweapons.py` L390: Remove `hasattr`. Call `self.scene.ui.show_system_picker(...)` directly.
- [ ] `strategy_superweapons.py` L407: Remove `hasattr`. Call `self.scene.ui.show_ship_picker(...)` directly.
- [ ] Remove all fallback else-branches in superweapons (L377-379, L394-396, L410-412)

#### Task 6.2: Battle Panels — Ship/Projectile ID Cleanup [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`
- [ ] Verify `_get_ship_id` and `_get_projectile_id` work with both DTO and domain objects after Phase 2 changes
- [ ] Simplify if both ShipDTO and Ship now have `.id`

#### Task 6.3: Final Audit [Simple]
**Tests:** Full suite
- [ ] Run grep for remaining `hasattr`/`getattr` in `game/ui/` and verify all are in exempt list
- [ ] Document remaining instances with justification
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` — 12734 passed, 1 skipped (baseline 2026-02-25)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Run `pytest tests/ -n 12` — full suite passes

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Grep audit: all remaining hasattr/getattr in game/ui/ are documented exempt
- [ ] Manual test: strategy screen, battle screen, builder — no crashes

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 complete (trivial guard removal)
- [ ] Phase 2 complete (init declarations)
- [ ] Phase 3 complete (monkey-patch elimination)
- [ ] Phase 4 complete (bug fixes)
- [ ] Phase 5 complete (type annotations)
- [ ] Phase 6 complete (stub methods & cleanup)
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
