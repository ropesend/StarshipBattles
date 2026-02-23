# Phase 2: Mock Data & Panel Registry

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-105 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create deterministic mock data factories and register all 5 panel snapshots

---

## Tasks

### Task 2.1: Create Mock Data Factories [Complex]
**File:** `tests/visual_regression/mock_data.py` (NEW)
**Tests:** `pytest tests/visual_regression/test_mock_data.py` (created in Task 2.3)

- [ ] Create `make_ship_dto(**overrides) -> ShipDTO`
  - Default: `id="ship_001"`, `name="ISS Defiant"`, `team_id=0`, `is_alive=True`, `hp=75.0`, `max_hp=100.0`, `current_shields=50.0`, `max_shields=100.0`, etc.
  - Import `ShipDTO`, `ResourceDTO`, `ComponentDTO` from `game.ui.interfaces.battle_ui`
  - Import `Vector2` from `game.core.math`
  - Include 3 default `ResourceDTO` entries (fuel, energy, ammo)
  - Include 2 default `ComponentDTO` entries (1 weapon, 1 non-weapon)

- [ ] Create `make_rich_ship_mock(**overrides) -> MagicMock` for expanded view
  - Must satisfy ALL attribute accesses in `ship_stats_renderer.py`:
    - `.id` (str), `.name` (str), `.team_id` (int), `.is_alive` (bool), `.is_derelict` (bool)
    - `.source_file` (Optional[str]), `.ai_strategy` (str)
    - `.max_shields` (float), `.current_shields` (float), `.hp` (float), `.max_hp` (float)
    - `.resources.get_all_resources()` → list of mock resources with `.name`, `.current_value`, `.max_value`
    - `.current_speed` (float), `.max_speed` (float), `.total_shots_fired` (int)
    - `.crew_onboard` (int), `.crew_required` (int)
    - `.current_target` = mock with `.is_alive=True`, `.name="Enemy"` (or None)
    - `.secondary_targets` = `[]`
    - `.max_targets` = 1
    - `.layers` = dict mapping `LayerType.OUTER` → mock layer with `.components` list
    - Each mock component: `.name`, `.current_hp`, `.max_hp`, `.is_active`, `.status`, `.has_ability()` (returns bool), `.shots_fired`, `.shots_hit`
    - `.get_all_components()` → flat list of all components across layers
  - Import `LayerType` from `game.core.constants`
  - Import `ComponentStatus` from `game.simulation.components.component_constants`

- [ ] Create `make_projectile_dto(**overrides) -> ProjectileDTO`
  - Default: `id="proj_001"`, `status="active"`, `velocity=Vector2(10, -5)`, `damage=25.0`, `hp=10.0`, `max_hp=10.0`, `endurance=5.0`, `max_endurance=8.0`, `target_name="ISS Defiant"`, `max_speed=20.0`

- [ ] Create `make_battle_scene_mock(ships=None, projectiles=None, test_mode=False, battle_over=False) -> MagicMock`
  - `scene.ui_service.get_ships.return_value = ships` (MUST be a real list, not auto-mock)
  - `scene.test_mode = test_mode`
  - `scene.is_battle_over.return_value = battle_over`
  - `scene.ships = ships` (fallback for `_get_ships()`)
  - Default: 4 ships (2 per team), 1 dead

**Notes:** The `_get_ships()` guard at `battle_panels.py:39` checks `isinstance(ships, list)`. Always return a real list from `get_ships()`.

---

### Task 2.2: Create Panel Registry [Medium]
**File:** `tests/visual_regression/panel_registry.py` (NEW)
**Tests:** Import test in Task 2.3

- [ ] Create `PanelSpec` dataclass: `name` (str), `width` (int), `height` (int), `render_fn` (Callable[[pygame.Surface], None]), `description` (str)
- [ ] Create `PANEL_REGISTRY: Dict[str, PanelSpec] = {}`
- [ ] Create `register(name, width, height, render_fn, description)` function
- [ ] Create `get_all_panels() -> List[Tuple[str, PanelSpec]]`

- [ ] Register `ship_stats_collapsed` (width=`UIConfig.STATS_PANEL_WIDTH`, height=600):
  - Create scene with 4 ShipDTOs via `make_battle_scene_mock()`
  - Create `ShipStatsPanel(scene, 0, 0, w, h)` — no ships expanded
  - Call `panel.draw(screen)`

- [ ] Register `ship_stats_expanded` (width=`UIConfig.STATS_PANEL_WIDTH`, height=900):
  - Create scene with rich ship mocks via `make_rich_ship_mock()`
  - Set `scene.ui_service.get_ships.return_value` to rich mock list
  - Create `ShipStatsPanel(scene, 0, 0, w, h)`
  - Set `panel.expanded_ships.add("ship_001")` to expand first ship
  - Set `panel.scroll_offset = 0` explicitly
  - Call `panel.draw(screen)`

- [ ] Register `seeker_monitor` (width=`UIConfig.SEEKER_PANEL_WIDTH`, height=500):
  - Create scene via `make_battle_scene_mock()`
  - Create `SeekerMonitorPanel(scene, 0, 0, w, h)`
  - Call `panel.add_seeker()` with 4 ProjectileDTOs: active, active, hit, miss
  - Call `panel.draw(screen)` (headless `get_pos()` returns (0,0) → deterministic)

- [ ] Register `battle_control_ongoing` (width=800, height=600):
  - Create scene with `battle_over=False`, `test_mode=False`
  - Create `BattleControlPanel(scene, 0, 0, 800, 600)`
  - Call `panel.draw(screen)`

- [ ] Register `battle_control_victory` (width=800, height=600):
  - Create scene: team 1 alive, team 2 dead, `test_mode=False`
  - Create `BattleControlPanel(scene, 0, 0, 800, 600)`
  - Call `panel.draw(screen)`

**Notes:** Each render function is self-contained — constructs its own panel+mocks. Imports are inside functions to avoid module-level side effects.

---

### Task 2.3: Create Mock Data & Registry Tests [Medium]
**File:** `tests/visual_regression/test_mock_data.py` (NEW)
**Tests:** `pytest tests/visual_regression/test_mock_data.py -v`

- [ ] Test: `make_ship_dto()` returns valid `ShipDTO` with all fields
- [ ] Test: `make_ship_dto(name="Custom")` respects overrides
- [ ] Test: `make_rich_ship_mock()` has all required attributes (non-MagicMock leaf values)
  - Verify `.resources.get_all_resources()` returns a real list
  - Verify `.layers` is a real dict with `LayerType` keys
  - Verify each component's `.has_ability('WeaponAbility')` returns a bool (not MagicMock)
- [ ] Test: `make_projectile_dto()` returns valid `ProjectileDTO`
- [ ] Test: `make_battle_scene_mock()` returns scene where `_get_ships()` works
  - Create a `BattlePanel` subclass, verify `_get_ships()` returns the mock list
- [ ] Test: all 5 registered panels render without exceptions
  - For each panel in `PANEL_REGISTRY`: create surface, call render_fn, verify surface was modified (not all-black)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/visual_regression/test_mock_data.py -v` passes
- [ ] All 5 panel render functions execute without exceptions
- [ ] `pytest tests/ -n 12` still passes (no regressions)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
