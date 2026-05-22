# Phase 4: Migrate the COLD broad-property consumers + raw-domain fan-out

> **BEFORE MARKING COMPLETE:** `python Projects/scripts/validate_phase.py PROJ-477 4`; update plan.md.

**Status:** Not Started
**Objective:** Move every COLD consumer of `scene.galaxy`/`empires`/`systems` (and the transitive
raw-domain fan-out) onto either a new facade query (Phase 2) or the `StrategyWorldAccess` handle.
The properties still EXIST after this phase (deleted in Phase 6) — but no COLD path reads them, and
guard #3's allowlist shrinks accordingly. **NOTE:** `StrategyWorldAccess` is introduced in Phase 5;
if a cold consumer needs live raw traversal (e.g. menu builders, list windows, build-queue chain),
either (a) pull the `StrategyWorldAccess` introduction forward to the start of this phase, or (b)
migrate the pure-facade-query cold consumers here and the world-handle cold consumers in Phase 5.
**Recommend (a)** — introduce `scene.world` first (Phase 5 Task 5.1) then do Phases 4+5 together.

> This is the largest phase — the Phase 4/5 boundary is the documented CAP cut line (option B).

---

## Tasks

### Task 4.1: Object→system resolution consumers → `scene.world` (LIVE) [Medium]
**Files:** `strategy_event_router.py:397-411`, `strategy_camera_nav.py:91,160-163`
**Tests:** `pytest tests/ -k "event_router or camera_nav"`

- [ ] Failing tests for each: object centering / event routing works without `scene.galaxy`/`scene.systems`.
- [ ] **POST-FLESH B2:** `strategy_event_router.py:401` `galaxy.get_system_of_object` → `scene.world.system_for_object(obj)` — **NOT** `facade.systems.of_object` (the caller immediately iterates the resolved system's LIVE `.planets` at `:401-411`; `SystemInfo` carries no `planets`/`warp_points`/`stars`, `system_dto.py:118-161`). Use `facade.systems.of_object` only for true summary-only callers.
- [ ] `strategy_camera_nav._resolve_global_hex` (`:91`) and `zoom_to_system` (`:160-163`) `s for s in self.systems if obj in s.planets` → `scene.world.system_for_object(obj)` (live, no DTO).
- [ ] `zoom_to_galaxy` (`:108-113`) `for sys in self.systems` → `scene.world.iter_systems()`.
- [ ] Drop the migrated allowlist entries.

**Notes:** These consumers need the LIVE `StarSystem`, not a `SystemInfo` summary.

---

### Task 4.2: Spatial/hex consumers → `facade.spatial.contents_at_hex` / `scene.world` [Complex]
**Files:** `strategy_colonization.py:83,170,257,270`, `strategy_superweapons.py:109,213,367`, `strategy_click_dispatcher.py:594-595`
**Tests:** `pytest tests/ -k "colonization or superweapon or click_dispatcher"`

- [ ] Failing tests: colonize target detection, superweapon targeting, click picking work without raw `scene.galaxy`.
- [ ] `get_zones_at_global_hex` reads (`colonization:84,171`, `click_dispatcher:595`) → `facade.spatial.contents_at_hex(hex)` (preserves multi-hex zone membership).
- [ ] **POST-FLESH B5 caveat:** `get_planets_at_global_hex` (`superweapons:109-122`) → `scene.world.planets_at_exact_hex(hex)` — **NOT** `contents_at_hex` (this site uses EXACT planet membership; the multi-hex `contents_at_hex` would start matching Dyson-Sphere edge hexes where it does not today).
- [ ] **POST-FLESH B2:** `_pathfinder.get_system_at_hex` (`colonization:257`, `superweapons:367`) → `scene.world.system_at_map_hex(hex, radius=50)` (LIVE) — these callers then read the resolved system's live `.planets` (`colonization:73-80,160-167,246-257`) / `.warp_points` (`superweapons:362-379`). Use `facade.systems.at_map_hex` only for summary-only callers. Either way, radius=50 semantics, NOT `near_hex(max_dist=8)`.
- [ ] full-scan fallbacks `for sys in self.systems` (`colonization:91,270`, `superweapons:213`) → `scene.world.iter_systems()`.
- [ ] `scene.empires` (`click_dispatcher:560`) → `scene.world.iter_empires()`.
- [ ] Drop migrated allowlist entries.

**Notes:** Watch semantic drift (design.md risk 2) — verify zone membership + system-radius behavior unchanged. Live-system callers use `scene.world`, not the summary facade query.

---

### Task 4.3: Menu builders → world/facade handle [Medium]
**Files:** `strategy_ui.py:199,237`, `fleet_menu_items.py:89-142`, `planet_menu_items.py:59-97`
**Tests:** `pytest tests/ -k "menu_items or strategy_ui"`

- [ ] Failing tests: fleet/planet context menus build correctly without raw `scene.galaxy`.
- [ ] Change `build_menu_items` / `build_planet_menu_items` signatures to take a `world` handle (or facade) instead of raw `galaxy`; update their internal `galaxy.get_planets_at_global_hex`/`galaxy.empires`/`galaxy.systems` traversal accordingly.
- [ ] `strategy_ui.py:199,237` pass `self.scene.world` instead of `self.scene.galaxy`.
- [ ] Drop migrated allowlist entries.

**Notes:**

---

### Task 4.4: List windows → world handle [Complex]
**Files:** `strategy_windows/list_windows.py:42-117`, `planet_list_window.py`, `star_list_window.py`, `planet_list_filters.py:38-87`, `star_list_filters.py:20-64`
**Tests:** `pytest tests/ -k "list_window or planet_list or star_list"`

- [ ] Failing tests: Planet/Star list windows open + render owner names + navigate + FILTER without raw `galaxy`/`empires`.
- [ ] `list_windows.py` pass `c.scene.world` (and existing `facade_state` for caches) instead of `c.scene.galaxy`/`c.scene.empires`.
- [ ] `PlanetListWindow`/`StarListWindow` consume the `world` handle for system/owner traversal (they already accept `facade_state`/`facade`). Update `open_for_galaxy` rebind paths.
- [ ] **POST-FLESH B3:** `planet_list_filters.py:38-87` and `star_list_filters.py:20-64` walk `galaxy.systems.values()` — part of the transitive fan-out once the windows stop receiving raw galaxy. Migrate these to the `world` handle (`world.iter_systems()`) too.
- [ ] Drop migrated allowlist entries.

**Notes:** These windows store raw `galaxy`/`empires` as locals — guard #3 must NOT flag those local `self.galaxy` reads (design.md), but the SOURCE read `c.scene.galaxy` is what migrates.

---

### Task 4.5: Build-queue chain → world handle [Complex]
**Files:** `build_queue_windows.py:62`, `strategy_build_queue_manager.py:141-317`, `build_queue_screen.py:111,237,357`, `build_queue_controller.py:456-554`
**Tests:** `pytest tests/ -k "build_queue"`

- [ ] Failing tests: build-queue open + planet-at-hex resolution + live-yard resolution work without raw `galaxy`.
- [ ] Thread `scene.world` through `build_queue_windows`/`strategy_build_queue_manager` into `BuildQueueScreen`/`BuildQueueController` (replacing the raw `galaxy` they store + `get_planets_at_global_hex` calls with `world.planets_at_exact_hex`).
- [ ] **POST-FLESH B3:** `strategy_build_queue_manager._resolve_live_yard()` (`:301-319`) needs a live planet lookup BY ID. Use `scene.world.planet_by_id(id)` (added Phase 5 Task 5.1) OR route to `facade.facade_state.get_planet_by_id(id)` (`_facade_state.py:130-134`, already exists). Pick one and pin it.
- [ ] Drop migrated allowlist entries.

**Notes:** Deepest fan-out; the controller's `self.galaxy` local stays NOT-matched by guard #3.

---

### Task 4.6: Assets / selection / state-manager / fleet-ops / screen-internal [Medium]
**Files:** `strategy_screen_assets.py:34,50`, `strategy_screen_selection.py:34,80`, `strategy_game_state_manager.py:144-146,160-164`, `strategy_fleet_ops.py:66`, `strategy_screen.py:201-210`
**Tests:** `pytest tests/ -k "assets or selection or state_manager or current_empire"`

- [ ] `strategy_screen_assets.py` `screen.systems`/`screen.empires` → `scene.world.iter_systems/iter_empires`.
- [ ] `strategy_screen_selection.py` `screen.systems` → `scene.world`.
- [ ] `strategy_game_state_manager.py` `_screen.empires` → `scene.world.iter_empires`.
- [ ] `strategy_fleet_ops.py:66` wrapper-only `scene.empires` → world (or delete the unused wrapper if no consumer).
- [ ] `strategy_screen.current_empire` (`:201-210`) internal `self.empires` → `self._session.empires` (composition root — the screen owns the only legitimate handle; this is NOT a property bypass).
- [ ] Drop migrated allowlist entries.

**Notes:** `current_empire` rewire to `_session` mirrors how PROJ-475 handles `active_empire_id`.

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] No COLD consumer reads `scene.galaxy`/`empires`/`systems`; guard #3 allowlist shrunk to render-hot only
- [ ] No system/hex SEMANTIC drift (verify targeting/selection behavior pins)
- [ ] Sharded suite green
- [ ] Update status `Complete`; update plan.md table + Current State → Phase 5
