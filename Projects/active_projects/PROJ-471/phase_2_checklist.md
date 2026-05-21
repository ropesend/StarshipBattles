# Phase 2: Major (singleton-divergence + collection + RNG hygiene)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-471 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Partial — Tasks 2.1, 2.2, 2.8, 2.9, 2.10 DONE; 2.11/2.12 DEFERRED→PROJ-473; 2.3, 2.4, 2.5, 2.6, 2.7, 2.13 NOT DONE
**Objective:** Resolve the MAJOR singleton-divergence findings (missing setters, dual pattern, ctx-bridge migrations), add test-isolation seams to the mutable collections, remove the two global `random.seed()` calls, and encapsulate the `exit_dialog` rect globals. Do not begin until Phase 1's two state-corruption items pass.

---

## Tasks

### Task 2.1: Add `set_default_cache_manager()` and wire it [Medium]
**File:** `game/simulation/components/component_loader.py`
**Tests:** `pytest tests/ -k component_cache`; then `pytest tests/ --testmon`

- [x] Added `set_default_cache_manager()` for `_default_cache_manager` and replaced the raw module-attribute assignment in `create_production()` with the setter (`game/context.py`).
- [x] Routed `reset_component_caches()` through `set_default_cache_manager()` so it cannot create permanent divergence from `ctx.component_cache`.
- [x] Verify: pytest passes (setter + loader + application_context tests green); no new `_default_*` without matching wiring.

**Notes:** TDD via `tests/unit/simulation/components/test_cache_manager_setter.py`.

### Task 2.2: Add `set_default_policy_manager()` and wire it [Medium]
**File:** `game/ai/policy_manager.py`
**Tests:** `pytest tests/ -k policy_manager`; then `pytest tests/ --testmon`

- [x] Added `set_default_policy_manager()` and replaced the raw module-attribute assignment in `create_production()` with the setter.
- [x] Verify: pytest passes; no raw module-attr assignment for this default remains in `create_production()`.

**Notes:** TDD via `tests/unit/ai/test_policy_manager_setter.py`.

### Task 2.3: Resolve the `_default_manager` dual pattern in Core [Complex]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/ -k registry`; then `pytest tests/ --testmon`

- [ ] Resolve the dual-pattern access on `_default_manager` (RegistryManager, `registry.py:284`; auto-create window in `get_default_registry_manager()` line 314). The 8 module-level convenience wrappers (`registry.py:324,336,345,360,382,386,390,394` — `freeze_registry`, `set_validator`, `get_validator`, `clear`, etc.) should route through `ctx.registry_manager` when available, or the dual path should be consciously documented as an accepted bridge. Record the decision in `decisions.md`.
- [ ] Verify: pytest passes; the auto-create divergence window is either closed or documented as intentional.

### Task 2.4: Migrate `_default_ship_theme_manager` UI consumers toward ctx [Complex]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/ -k ship_theme`; then `pytest tests/ --testmon`

- [ ] Migrate the 15 production consumers of `get_default_ship_theme_manager()` (`ship_theme_manager.py:54`; consumers in `fleet_data_source.py:296`, `ship_detail_panel.py:297`, `race_summary_panel.py:641`, `build_queue_portraits.py:123`, `workshop_screen.py:112`, `race_theme_gallery.py:132`, `race_browser_dialog.py:167`, `race_asset_loader.py:237`, `race_setup/ship_preview.py:60`, `design_image_helper.py:75`, `builder/right_panel.py:272`, `game_renderer.py:76`, `design_report_panel.py:178`, et al.) to `ctx.ship_theme_manager`, threading `ctx` through UI component constructors (ScreenRouter already passes ctx to scenes). This is the highest get_default reducer in the UI layer.
- [ ] Verify: pytest passes; consumers no longer call the module-level accessor (or remaining ones documented).

### Task 2.5: Migrate `_default_asset_manager` UI consumers toward ctx [Complex]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/ -k asset_manager`; then `pytest tests/ --testmon`

- [ ] Migrate the 7 production consumers of `get_default_asset_manager()` (`asset_manager.py:14`; consumers in `strategy_renderer.py:89`, `planet_selection_window.py:207`, `strategy_screen_assets.py:47,58`, `star_data_source.py:56`, `planet_data_source.py:84`, `strategy_detail_fmt.py:429`) to `ctx.asset_manager` where ctx is threadable.
- [ ] Verify: pytest passes.

### Task 2.6: Migrate `_default_sprite_manager` consumers + fix lazy-init fallback [Medium]
**File:** `game/ui/renderer/sprites.py`
**Tests:** `pytest tests/ -k sprite_manager`; then `pytest tests/ --testmon`

- [ ] Migrate the 2 consumers of `get_default_sprite_manager()` (`sprites.py:14`): `app_bootstrap.py:265` should use `ctx.sprite_manager` (ctx is already in scope at line 264), and `workshop_screen.py:109` once ctx is threaded.
- [ ] Replace the lazy-init fallback in `get_default_sprite_manager()` (`sprites.py:116-119`, ST-01-005) that creates a fresh `SpriteManager()` when `None` — use a sentinel that raises a descriptive error, or guarantee `set_default_sprite_manager()` runs first, to remove the pre-`create_production()` divergence path.
- [ ] Verify: pytest passes; no silent auto-create fallback remains.

### Task 2.7: Migrate `_default_llm_provider` sole consumer to ctx [Simple]
**File:** `game/services/llm/defaults.py`
**Tests:** `pytest tests/ -k llm_provider`; then `pytest tests/ --testmon`

- [ ] Migrate the sole consumer of `get_default_llm_provider()` (`defaults.py:17`) at `game/ui/screens/race_setup/panel_factory.py:167` to `ctx.llm_provider`. (Bridge removal itself is deferred to Phase 3 once this consumer is migrated.)
- [ ] Verify: pytest passes; `panel_factory.py:167` uses ctx.

### Task 2.8: Move `_next_fleet_id` to instance state [Medium]
**File:** `game/ui/screens/battle_setup_state.py`
**Tests:** `pytest tests/ -k battle_setup`; then `pytest tests/ --testmon`

- [x] Replaced the module-level `_next_fleet_id` counter (and `_generate_fleet_id()` global mutation) with a per-`BattleSetupState` `itertools.count` allocator injected into each `BattleSetupSide`; standalone sides fall back to their own local counter. Wired through `__init__`, `add_side`, `clear`, and `from_dict`. Resets per state; no unbounded process-global growth / cross-test leak.
- [x] Verify: pytest passes; no module-level mutable counter remains (`_FLEET_ID_BASE` constant only).

**Notes:** TDD via `tests/unit/ui/screens/test_battle_setup_fleet_id_isolation.py`. Ids remain unique across both sides of one state.

### Task 2.9: Add `_SERIALIZABLE_REGISTRY` test-isolation seam [Simple]
**File:** `game/core/json_utils.py`
**Tests:** `pytest tests/ -k serializable`; then `pytest tests/ --testmon`

- [x] Added `clear_serializable_registry(restore=None)` to `game/core/json_utils.py` (mutates the dict in place; empties by default or restores a `get_serializable_registry()` snapshot). Not wired into the autouse conftest fixture: registrations happen at import time and forcing a reset every test would drop legitimately-imported types — the seam is provided for tests that opt in.
- [x] Verify: pytest passes; a reset seam exists.

**Notes:** TDD via `tests/unit/core/test_serializable_registry_seam.py`.

### Task 2.10: Add `_catalog` invalidation hook [Simple]
**File:** `game/ui/screens/transfer_mass_preview.py`
**Tests:** `pytest tests/ -k transfer_mass`; then `pytest tests/ --testmon`

- [x] Added `_clear_catalog()` to `game/ui/screens/transfer_mass_preview.py` that resets the lazy `_catalog` cache so the next `_get_catalog()` reloads (removes stale-data-in-tests risk); updated the docstring.
- [x] Verify: pytest passes; a clear hook exists.

**Notes:** TDD via `tests/unit/ui/screens/test_transfer_mass_preview_catalog_seam.py`.

### Task 2.11: ~~Remove global `random.seed()` calls~~ — DEFERRED to PROJ-473
**Status:** DEFERRED per scope revision 2026-05-20 via Protocol 07 (see decisions.md + PROJ-473).

The global `random.seed(galaxy_seed)` at `game_initializer.py` is LOAD-BEARING:
`star_generator.py` and planet/atmosphere/naming generation use bare global `random.*`,
and placement strategies fall back to global random when `rng` is None. Deleting the seed
without first threading an explicit `rng` through generation breaks galaxy reproducibility
(determinism regression). PROJ-473 owns the rng-threading prerequisite work. No change here.

### Task 2.12: ~~Remove global `random.seed()` in galaxy test tool~~ — DEFERRED to PROJ-473
**Status:** DEFERRED per scope revision 2026-05-20 via Protocol 07 (see decisions.md + PROJ-473).

`galaxy_mode.py`'s `random.seed(self.galaxy_seed)` feeds the same global-random galaxy
generation path as Task 2.11; it is deferred together. No change here.

### Task 2.13: Encapsulate `exit_dialog` rect globals [Medium]
**File:** `game/exit_dialog.py`
**Tests:** `pytest tests/ -k exit_dialog`; then `pytest tests/ --testmon`

- [ ] Encapsulate `_exit_yes_rect` / `_exit_no_rect` (`exit_dialog.py:11-12`; reassigned every frame via `global` at line 24, read by `handle_exit_dialog_click()` line 86 and `handle_exit_dialog_cancel()` line 101) in a small dialog-state class so the module-level mutable globals are removed. (Audit verifier downgraded CRITICAL→MAJOR: derived values, modal, no corruption — this is a maintainability/coupling fix. Lowest-priority MAJOR; drop first if scope must be trimmed.)
- [ ] Verify: pytest passes; no module-level mutable rect globals remain.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_082533_state-audit/`. See `findings/source_audit.md` for the link._
