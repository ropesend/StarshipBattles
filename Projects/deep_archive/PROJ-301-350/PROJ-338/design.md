# PROJ-338 — Design / Architecture Context

For each panel: what the panel is, who calls it, what it reads, what it
writes, what's mockable, and what the test seam looks like.

---

## 1. `BuildQueueDragHandler`

**File:** `game/ui/panels/build_queue_drag_handler.py` (350 LOC)

- **Owner:** instantiated by `BuildQueueScreen` (build-queue scene), held as
  `self._drag_handler`.
- **Inputs:** `portrait_loader`, `design_library`, four callbacks
  (add-to-queue, refresh-queue, refresh-design-report, optional
  remove-from-queue).
- **Reads:** pygame events + container/scrollable element rects + a
  list-of-dicts construction queue + a `VirtualTable` (PROJ-221).
- **Writes:** callbacks fire add/remove/refresh; mutates `dragged_item`,
  `drag_start_pos`, `_pending_queue_index`, `selected_design`.
- **Test seam:** pure constructor injection — no facade, no scene reach.
  Easiest of the five to characterise. Just synthesize `pygame.event.Event`
  and stub the scrollable/virtual_table.

---

## 2. `BuildQueueController`

**File:** `game/ui/panels/build_queue_controller.py` (652 LOC)

- **Owner:** instantiated by `BuildQueueScreen` controllers initialiser; holds
  business logic for the queue.
- **Inputs:** `build_context` (`Planet|Fleet|BuildContext`), `design_library`,
  `design_loader`, `design_report` panel, `on_queue_changed` callback,
  optional galaxy/empire/hex_coord/planet-selection callback,
  `add_to_queue_callback` (PROJ-208), `registries`.
- **Reads:** `design_library.scan_designs()` /
  `load_design_data()`, `design_loader.load_ship_from_design_data()`,
  `galaxy.get_planets_at_global_hex()`,
  `source.context_type`/`can_build_ships`/`can_build_complexes`/
  `queue_id`/`owner_entity`.
- **Writes:** dispatches to `add_to_queue_callback`, calls
  `on_queue_changed`, calls `design_report.update_design` /
  `show_placeholder`.
- **Test seam:** existing tests use `MagicMock` `build_context` +
  `entity_registry` + `_make_add_callback` simulation — same pattern
  continues for the gap tests.

---

## 3. `SystemTreePanel`

**File:** `game/ui/panels/system_tree_panel.py` (719 LOC)

- **Owner:** held by `system_panel` and `sector_panel` in strategy screen.
- **Inputs:** `relative_rect`, `pygame_gui.UIManager`, container; later
  `set_items(contents, scene_interface, flat_view, system_obj, hex_coord)`.
- **Reads:** `scene_interface._get_label_for_obj`,
  `scene_interface._get_object_asset`,
  `scene_interface.scene.session.active_empire.id`,
  `scene_interface.scene.session.registries`; `collect_system_effects` /
  `collect_sector_effects` / `format_intrinsic_ability_magnitude`.
- **Writes:** builds `SystemTreeItem` widgets (UIButton/UILabel/UIImage
  children); `expanded_groups` set; `on_selection_callback` invocation.
- **Test seam:** existing smoke test uses live pygame_gui UIManager via
  `_init_uimanager` fixture. Characterization tests reuse that fixture.
  For internal helpers (`_format_effect_value`, `_format_provider_value`)
  — pure functions, no pygame needed.

---

## 4. `PlanetReportPanel`

**File:** `game/ui/panels/planet_report_panel.py` (673 LOC)

- **Owner:** held by strategy-screen detail areas + build-queue planet
  display.
- **Inputs:** `manager`, `rect`, `planet`, `container`, `portrait_surface`,
  `show_complexes`, `production_rates`, `view`, `empire`, `race_registry`.
- **Reads:** `format_planet_info(planet, view, empire, race_registry)` (heavy
  facade reach in helper), `Paths.RESOURCE_PORTRAITS_DIR`,
  `planet.deposits` / `stockpile` / `max_stockpile` / `facilities` /
  `atmosphere` / `planet_type` / `name`, `view.resource_projections`.
- **Writes:** `UIPanel` / `UIImage` / `UITextBox` / `UIScrollingContainer` /
  `UILabel` widgets; resource icons cache; `complex_items` list.
- **Test seam:** existing tests use `__new__` / `MagicMock` manager pattern.
  Characterization tests reuse — no architectural change. Pure helpers
  (`_projection_grid_rows` etc.) need no pygame at all.

---

## 5. `battle_panels.py` — `ShipStatsPanel`, `SeekerMonitorPanel`, `BattleControlPanel` (+ bases)

**File:** `game/ui/panels/battle_panels.py` (563 LOC)

- **Owner:** held by `BattleScreen` (combat scene).
- **Inputs:** scene reference + `(x, y, w, h)`. Scene must expose
  `ui_service.get_ships()`, `is_battle_over()`, `engine.aura_manager`.
- **Reads:** ship/projectile DTOs (`.id`, `.team_id`, `.is_alive`,
  `.is_derelict`, `.status`, `.velocity.length()`, etc.); pygame keys
  (`pygame.key.get_pressed()`); pygame mouse (`pygame.mouse.get_pos()`).
- **Writes:** blits to passed-in `screen` surface; mutates `_expanded_ids` /
  `tracked_seekers`; sets `battle_end_button_rect` /
  `end_battle_early_rect` / `clear_btn_rect` / `_ship_banner_rects`.
- **Test seam:** established mocked-pygame substitution from
  `test_battle_panels.py` — `MockRect` +
  `patch.dict(sys.modules, {'pygame': mock_pygame})`. Reuse verbatim.

---

## Testability blockers (cross-reference for `decisions.md`)

1. **`PlanetReportPanel.__init__` reaches into the filesystem**
   (`pygame.image.load(path)` for resource portraits). Tests need `__new__`
   bypass OR fixture catalog with on-disk icons. D-002 picks bypass; matches
   existing `test_planet_report_panel.py` shape.
2. **`SystemTreePanel._add_system_effects` /  `_add_sector_effects` reach
   `scene_interface.scene.session.active_empire.id` and
   `.session.registries`.** Stub `scene_interface` chain in the
   characterization tests; live pygame_gui UIManager via existing fixture.
3. **`BuildQueueController` needs `BuildQueueSource` instances** for the
   multi/single-queue paths — already solved in existing test file via
   MagicMock with `context_type` / `display_name` / `can_build_ships` /
   `can_build_complexes` / `queue_id` / `owner_entity` / `planet_id`. Reuse.
4. **Drag handler is the cleanest** — pure constructor injection, no facade.
   Direct unit-test target, not a blocker.
5. **Battle panels are coupled to `pygame.key.get_pressed()` and
   `pygame.mouse.get_pos()`** — the existing test file already solves this
   via `patch.dict(sys.modules, {'pygame': mock_pygame})`. Reuse verbatim,
   including `mock_pygame.key.get_pressed.return_value = ...` for shift-click
   semantics. Not a blocker — it's the established pattern.
