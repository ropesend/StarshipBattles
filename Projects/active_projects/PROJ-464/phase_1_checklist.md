# Phase 1: Major (UI Any narrowing + ignores + missing returns)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-464 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow the verified MAJOR presentation `-> Any` returns to concrete types, resolve the StrategyRenderer scene seam via a Protocol, remove the two UI type-ignores, and add missing UI/top-level public return types. (No CRITICAL findings in this layer.)

---

## Tasks

### Task 1.1: Narrow StrategyScreen delegate properties [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/ui/screens/strategy_screen.py`

- [ ] Narrow the 15 `-> Any` properties (e.g. `galaxy` line 161, `empires`, `systems`, `active_empire`, `facade`, `session`) to concrete types: `Galaxy`, `list[Empire]`, `list[StarSystem]`, `StrategySessionFacade`, `GameSession`
- [ ] Verify: pytest passes; `mypy game/ui/screens/strategy_screen.py` shows no new errors

### Task 1.2: Resolve StrategyRenderer scene seam via Protocol [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py tests/unit/ui/screens/test_strategy_renderer_public_api.py` and `mypy game/ui/screens/strategy_renderer.py`

- [ ] Introduce a minimal renderer-scene Protocol describing the scene surface the renderer reads, and annotate the 13 delegating properties (lines 115-157: `camera`, `galaxy`, `systems`, `empires`, `hex_size`, `screen_width/height`, `SIDEBAR_WIDTH`, `TOP_BAR_HEIGHT`, `empire_assets`, ...) against it
- [ ] DO NOT hard-narrow to `StrategyScreen` — the tests instantiate the renderer with `MagicMock` scenes and assert property delegations directly; a Protocol seam keeps those passing
- [ ] Verify: the two renderer tests pass; `mypy game/ui/screens/strategy_renderer.py` shows no new errors

### Task 1.3: Narrow BattleScreen delegate properties [Medium]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/ui/screens/battle_screen.py`

- [ ] Narrow `engine` (line 172) → `BattleEngine | None`; `show_overlay`/`stats_panel_width`/`ships`/`projectiles`/`ai_controllers` (199,207,211,215,219) → `bool`/`int`/`list[Ship]`/`list[Projectile]`/`list[AIController]`; `is_battle_over`/`get_winner` (481,485) → `bool`/`int | None`
- [ ] Verify: pytest passes; `mypy game/ui/screens/battle_screen.py` shows no new errors

### Task 1.4: Narrow planet/star list filter functions [Medium]
**File:** `game/ui/screens/planet_list_filters.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/ui/screens/planet_list_filters.py game/ui/screens/star_list_filters.py`

- [ ] Narrow planet_list_filters.py public functions (lines 38,174,215,252,280,333,348): `gather_planets`/`filter_planets`/`sort_planets` → `list[PlanetInfo]`; `get_column_value` → `str`; `compute_planet_ranges` → `dict[str, tuple]`; `get_system_name`/`get_owner_name` → `str`
- [ ] Narrow star_list_filters.py public functions (lines 20,67,121,163,203,217): `gather_stars`/`filter_stars`/`sort_stars` → `list[StarInfo]`, etc.
- [ ] Verify: pytest passes; mypy shows no new errors on both files

### Task 1.5: Narrow builder viewmodel + column manager returns [Simple]
**File:** `game/ui/screens/builder/weapons_viewmodel.py`
**Tests:** `pytest tests/ --testmon` and `mypy <touched files>`

- [ ] Narrow `builder/left_panel.py:453` get_add_count → `int`; `builder/modifier_logic.py:150` calculate_snap_value → `float`; `builder/weapons_viewmodel.py:110` hovered_weapon → `Component | None`, `:392` calc_damage_at_range → `float`
- [ ] Narrow `components/table/column_manager.py:79,137`: tighten `_columns` value type so `toggle_column` → `Optional[bool]` and `is_column_visible` → `bool` stop returning `Any`
- [ ] Verify: pytest passes; mypy shows no new errors on the touched files

### Task 1.6: Remove UI type-ignores [Simple]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/ --testmon` and `mypy <touched files>`

- [ ] Type `expected` as `tuple[int, int] | None` so the `# type: ignore[index]` at `ship_theme_manager.py:254` becomes unnecessary, then remove it
- [ ] Resolve the genuine override return-type mismatch at `race_theme_gallery.py:118` (`_discover_assets` returns `Dict[str, Surface]` vs base `List[Tuple[str, Surface]]`) — align the override shape and remove `# type: ignore[override]`
- [ ] Verify: pytest passes; mypy shows no new errors on the touched files

### Task 1.7: Add missing UI/top-level public return types [Simple]
**File:** `game/app_bootstrap.py`
**Tests:** `pytest tests/ --testmon` and `mypy <touched files>`

- [ ] Add `-> Ship` to `_replay_combat_lab_fallback` (app_bootstrap.py:310)
- [ ] Add return types to UI `_button_handlers` methods: `atmosphere_target_editor.py:223` (`-> None` or dict), `radiation_shield_editor.py:176`, `water_target_editor.py:173`
- [ ] Add `-> tuple[int,int,int]` to `test_lab/details/validation.py:39` `_phase_color`; add `-> ResourceCatalog` to `transfer_mass_preview.py:189` `_get_catalog`
- [ ] Verify: pytest passes; mypy shows no new errors on the touched files

### Task 1.8: Fix top-level/UI implicit-Optional violations [Simple]
**File:** `game/core/profiling.py` (+ UI siblings)
**Tests:** `pytest tests/ --testmon` and `mypy <touched files>`

- [ ] Fix `Type = None` → `Type | None = None` at `profiling.py:90` (`save_history`), `resources.py:85`, `ui/renderer/sprites.py:33`
- [ ] Verify: pytest passes; mypy shows no new errors on the touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-19_223900_type-audit/`. See `findings/source_audit.md` for the link._
