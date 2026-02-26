# Phase 1: Trivial Guard Removal — Direct Access

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-198 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove ~90 unnecessary `hasattr`/`getattr` guards where the attribute always exists on the target type. Pure subtraction.

---

## Tasks

### Task 1.1: Planet Attribute Guards [Simple]
**File:** `game/ui/screens/planet_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`

- [ ] L185: Remove `hasattr(planet, "image_id")`. Change to `if not planet.image_id:`
- [ ] L189: Replace `getattr(planet, "image_rotation", 0) or 0` with `planet.image_rotation or 0`
- [ ] Verify: tests pass

**Notes:**

### Task 1.2: Planet List Filter Guards [Simple]
**File:** `game/ui/screens/planet_list_filters.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`

- [ ] L70: Replace `getattr(p, 'owner_id', None)` with `p.owner_id`
- [ ] L202: Remove `if hasattr(p, 'surface_gravity'):` — always True. Dedent body.
- [ ] L205: Remove `if hasattr(p, 'surface_temperature'):` — always True. Dedent body.
- [ ] L208: Remove `if hasattr(p, 'mass'):` — always True. Dedent body.
- [ ] L297: Remove `hasattr(planet, 'resources')`. Change to `if resource_name in planet.resources:`
- [ ] Verify: tests pass

**Notes:**

### Task 1.3: Race Asset Loader Guards [Simple]
**File:** `game/ui/screens/race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/screens/ -k race --testmon`

- [ ] L269: Remove `hasattr(empire, 'empire_theme_id')`. Change to `if empire.empire_theme_id:`
- [ ] L274: Remove `hasattr(empire, 'flag_id')`. Change to `if empire.flag_id:`
- [ ] Verify: tests pass

**Notes:**

### Task 1.4: Empire Build Queue Formatter Guards [Simple]
**File:** `game/ui/screens/empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/ -k empire --testmon`

- [ ] L86: Replace `getattr(sys_obj, 'name', '-')` with `sys_obj.name`
- [ ] L88: Replace `getattr(entity, 'location', None)` with `entity.location`
- [ ] L92: Replace `getattr(sys_obj, 'name', '-')` with `sys_obj.name`
- [ ] L107: Replace `getattr(entity, 'location', None)` with `entity.location`
- [ ] Verify: tests pass

**Notes:**

### Task 1.5: Empire Build Queue Window Guard [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k empire --testmon`

- [ ] L328: Replace `getattr(entity, 'location', None)` with `entity.location`
- [ ] Verify: tests pass

**Notes:**

### Task 1.6: Strategy Screen Guards — Always-Exist Properties [Simple]
**Files:** Multiple strategy_*.py files
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [ ] `strategy_click_dispatcher.py` L524: Remove `hasattr(self.scene, 'galaxy')`. Keep `if self.scene.galaxy:`
- [ ] `strategy_colonization.py` L82-83: Replace with `if self.scene.galaxy:` then direct method call
- [ ] `strategy_colonization.py` L196-197: Same pattern
- [ ] `strategy_detail_formatter.py` L208: Remove `hasattr(self.scene, 'current_empire')`. Use `if self.scene.current_empire:`
- [ ] `strategy_event_router.py` L88: Remove `hasattr(self.ui.scene, 'on_ui_selection')`. Call directly.
- [ ] `strategy_event_router.py` L131: Remove `hasattr(...)`. Use `if event.ui_element == self.ui.scene._quit_confirm_dialog:`
- [ ] `strategy_event_router.py` L149: Remove `hasattr(ui.scene, 'on_design_click')`. Call directly.
- [ ] `strategy_event_router.py` L191: Remove `hasattr(ui.scene, 'galaxy')`. Use `if not ui.scene.galaxy:`
- [ ] `strategy_event_router.py` L213: Remove `hasattr(...)`. Call `request_colonize_order` directly.
- [ ] `strategy_event_router.py` L218: Same as L213.
- [ ] `strategy_renderer.py` L122: Replace `getattr(self.scene, 'input_mode', 'SELECT')` with `self.scene.input_mode`
- [ ] `strategy_ui.py` L256: Remove `hasattr(self.scene, '_get_object_asset')`. Call directly.
- [ ] `strategy_ui.py` L285: Remove `hasattr(...)`. Use `if not self.scene.current_empire:`
- [ ] `strategy_window_manager.py` L202: Remove `hasattr(self.scene, "facade")`. Use `self.scene.facade` directly.
- [ ] Verify: tests pass

**Notes:**

### Task 1.7: Strategy Build Queue Manager Guards [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [ ] L63: Replace `getattr(self._screen.session, 'save_path', None)` with `self._screen.session.save_path`
- [ ] L178: Same replacement
- [ ] L221: Same replacement
- [ ] Verify: tests pass

**Notes:**

### Task 1.8: Strategy Game State Manager Guards [Simple]
**File:** `game/ui/screens/strategy_game_state_manager.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [ ] L110: Replace `getattr(self._screen.session, 'turn_engine', None)` with `self._screen.session.turn_engine`
- [ ] L113: Replace `getattr(turn_engine, 'last_scuttle_events', [])` with `turn_engine.last_scuttle_events`
- [ ] Verify: tests pass

**Notes:**

### Task 1.9: Strategy Detail Format Guards [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [ ] L302: Replace `getattr(order.target, 'name', 'Unknown')` with `order.target.name if order.target else 'Unknown'`
- [ ] L305: Replace `getattr(fleet, 'construction_queue', [])` with `fleet.construction_queue`
- [ ] Verify: tests pass

**Notes:**

### Task 1.10: Galaxy Test Screen Guards [Simple]
**File:** `game/ui/screens/galaxy_test/screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k galaxy --testmon`

- [ ] L214-224: Replace all `getattr(..., None)` with direct attribute access (7 replacements)
- [ ] Verify: tests pass

**Notes:**

### Task 1.11: Galaxy Test System Mode Guard [Simple]
**File:** `game/ui/screens/galaxy_test/system_mode.py`
**Tests:** `pytest tests/unit/ui/screens/ -k galaxy --testmon`

- [ ] L520: Replace `star.color if hasattr(star, 'color') else (255, 255, 200)` with `star.color`
- [ ] Verify: tests pass

**Notes:**

### Task 1.12: Battle UI Service — Component Guards [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`

- [ ] L228: Remove `hasattr(comp, 'status') and hasattr(comp.status, 'name')`. Use direct access.
- [ ] L233: Remove `hasattr(comp, 'has_ability')`. Call directly.
- [ ] L244-245: Replace `getattr(comp, 'shots_fired', 0)` / `getattr(comp, 'shots_hit', 0)` with direct access.
- [ ] Verify: tests pass

**Notes:**

### Task 1.13: Battle UI Service — Projectile Guards [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`

- [ ] L259: `getattr(proj, 'target', None)` → `proj.target`
- [ ] L267: `getattr(proj, 'type', None)` → `proj.type`
- [ ] L275: `getattr(proj, 'radius', 4.0)` → `proj.radius`
- [ ] L277: `getattr(proj, 'hp', 0.0)` → `proj.hp`
- [ ] L278: `getattr(proj, 'max_hp', 0.0)` → `proj.max_hp`
- [ ] L279: `getattr(proj, 'status', 'active')` → `proj.status`
- [ ] L280: `getattr(proj, 'endurance', 0.0)` → `proj.endurance`
- [ ] L281: `getattr(proj, 'max_endurance', 0.0)` → `proj.max_endurance`
- [ ] L283: `getattr(proj, 'max_speed', 0.0)` → `proj.max_speed`
- [ ] Verify: tests pass

**Notes:**

### Task 1.14: Battle Panels — Projectile Guards [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`

- [ ] L353: `getattr(proj, 'status', 'active')` → `proj.status`
- [ ] L401: `getattr(proj, 'max_speed', ...)` → `proj.max_speed`
- [ ] L407: `getattr(proj, 'hp', 0)` → `proj.hp`
- [ ] L408: `getattr(proj, 'max_hp', ...)` → `proj.max_hp`
- [ ] L418: `getattr(proj, 'endurance', 0)` → `proj.endurance`
- [ ] L419: `getattr(proj, 'max_endurance', ...)` → `proj.max_endurance`
- [ ] L434: `getattr(proj, 'target', None)` → `proj.target`
- [ ] L435: Remove `hasattr(target, 'name')` — target is always Ship
- [ ] Verify: tests pass

**Notes:**

### Task 1.15: Battle Factories Guard [Simple]
**File:** `game/ui/services/battle_factories.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`

- [ ] L133: Replace `scenario.max_ticks if hasattr(scenario, 'max_ticks') else 100000` with `scenario.max_ticks`
- [ ] Verify: tests pass

**Notes:**

### Task 1.16: Ship IO Guard [Simple]
**File:** `game/ui/services/ship_io.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`

- [ ] L142: Replace `getattr(new_ship, '_loading_warnings', [])` with `new_ship._loading_warnings`
- [ ] Verify: tests pass

**Notes:**

### Task 1.17: Builder/Workshop Remaining Guards [Simple]
**Files:** Multiple builder files
**Tests:** `pytest tests/unit/ui/screens/builder/ --testmon`

- [ ] `builder/left_panel.py` L254: `getattr(self.builder.ship, 'vehicle_type', "Ship")` → `self.builder.ship.vehicle_type`
- [ ] `builder/schematic_view.py` L71: `getattr(ship, 'theme_id', 'Federation')` → `ship.theme_id`
- [ ] `builder/detail_panel.py` L145: Remove `hasattr(comp, 'get_ui_rows')`. Call directly.
- [ ] Verify: tests pass

**Notes:**

### Task 1.18: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 12734 tests pass
- [ ] No new failures introduced

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
