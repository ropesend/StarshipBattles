# Phase 2: Major (singleton-divergence + collection + RNG hygiene)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-471 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete — Tasks 2.1, 2.2, 2.6, 2.8, 2.9, 2.10, 2.13 DONE; 2.3 RESOLVED (documented bridge); 2.4/2.5/2.7 DROPPED (moot for state-hygiene, see decisions.md 2026-05-21); 2.11/2.12 DEFERRED→PROJ-473
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

### Task 2.3: Resolve the `_default_manager` dual pattern in Core [Complex] — RESOLVED (documented bridge)
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/ -k registry`; then `pytest tests/ --testmon`

- [x] RESOLVED: the dual pattern is a documented, accepted bridge. Re-verified `registry.py:284-360`: the 8 convenience wrappers all route through the single `get_default_registry_manager()` getter; production primes it once via `set_default_registry_manager()` in `create_production()` (`context.py:175`), so all wrappers share one manager. The `_default_manager is None` auto-create is the test-time convenience (registry tests need no full ApplicationContext); the only divergence window (touch a wrapper before bootstrap in production) never occurs because bootstrap runs first. Decision recorded in `decisions.md` (2026-05-21). No behavior change.
- [x] Verify: existing registry tests stay green; divergence window documented as intentional.

### Task 2.4: Migrate `_default_ship_theme_manager` UI consumers toward ctx [Complex] — DROPPED (moot for state-hygiene)
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/ -k ship_theme`; then `pytest tests/ --testmon`

- [x] DROPPED. Re-verified: `set_default_ship_theme_manager()` is called exactly once, in `create_production()` (`context.py:181`); nothing re-sets it mid-run, so `get_default_ship_theme_manager() is ctx.ship_theme_manager` always holds in production — there is NO singleton-divergence bug here, only an accessor-style preference. Migrating the 15 consumers requires threading `ApplicationContext` through many UI constructors that carry no ctx today — a cross-cutting UI-DI refactor disproportionate to the task and with zero state-hygiene payoff. Dropped per CLAUDE.md root-cause/no-gold-plating. Decision in `decisions.md` (2026-05-21).

### Task 2.5: Migrate `_default_asset_manager` UI consumers toward ctx [Complex] — DROPPED (moot for state-hygiene)
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/ -k asset_manager`; then `pytest tests/ --testmon`

- [x] DROPPED for the same reason as 2.4: `set_default_asset_manager()` is a single startup call (`context.py:179`), no mid-run re-set, so no divergence exists in production. Consumer migration is a UI-DI refactor with no state-hygiene benefit. Decision in `decisions.md` (2026-05-21).

### Task 2.6: Migrate `_default_sprite_manager` consumers + fix lazy-init fallback [Medium]
**File:** `game/ui/renderer/sprites.py`
**Tests:** `pytest tests/ -k sprite_manager`; then `pytest tests/ --testmon`

- [x] Migrated `app_bootstrap.py:265` to `ctx.sprite_manager` (ctx in scope) and removed the now-unused module import. `workshop_screen.py:109` keeps the accessor: it takes a `WorkshopContext`, not an `ApplicationContext`, so no ctx is threadable there without a separate UI-DI change; production always primes the default at startup so no divergence results. Documented in `decisions.md` (2026-05-21).
- [x] Replaced the lazy-init fallback in `get_default_sprite_manager()` (the genuine ST-01-005 state bug): the accessor now raises a descriptive `RuntimeError` when `_default_sprite_manager` is `None` instead of silently creating a fresh, unloaded, divergent manager. `create_production()` primes it at startup; tests prime it explicitly.
- [x] Verify: pytest passes (`tests/unit/ui/test_sprite_default_no_autocreate.py` + existing `test_sprites.py`/`test_sprite_loading.py` green); no silent auto-create fallback remains.

**Notes:** TDD via `tests/unit/ui/test_sprite_default_no_autocreate.py`.

### Task 2.7: Migrate `_default_llm_provider` sole consumer to ctx [Simple] — DROPPED (moot for state-hygiene)
**File:** `game/services/llm/defaults.py`
**Tests:** `pytest tests/ -k llm_provider`; then `pytest tests/ --testmon`

- [x] DROPPED. `set_default_llm_provider()` is a single startup call (`context.py:183`); `get_default_llm_provider() is ctx.llm_provider` always holds — no divergence. The sole consumer (`panel_factory.create_descriptions_panel`) sits at the bottom of a ctx-less UI chain (`new_game_setup_controller` → `RaceSetupScreen` → `panel_factory`); threading ctx down four constructor layers is disproportionate to a "Simple" task and yields no state-hygiene benefit. Bridge kept as the intentional module-level hook. Decision in `decisions.md` (2026-05-21). (Task 3.3 dropped with it.)

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

- [x] Encapsulated the rects in an `ExitDialog` class (`game/exit_dialog.py`): per-instance `_yes_rect`/`_no_rect`, methods `draw`/`handle_click`/`handle_cancel`. Removed the module-level `_exit_yes_rect`/`_exit_no_rect` globals and the `global` reassignment. `RunLoop` (`game/run_loop.py`) owns one `ExitDialog` instance; updated its imports + the three call sites; updated `tests/unit/test_run_loop.py` monkeypatches accordingly.
- [x] Verify: pytest passes; no module-level mutable rect globals remain (test asserts `not hasattr(exit_dialog, "_exit_yes_rect")`).

**Notes:** TDD via `tests/unit/test_exit_dialog.py` (rewritten for the instance class + per-instance isolation).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (done / resolved / dropped-with-reason)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_082533_state-audit/`. See `findings/source_audit.md` for the link._
