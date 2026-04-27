# Phase 3: Execute decompositions (one file per sub-phase)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-309 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Execute the decomposition designs from Phase 2. Each file gets its own sub-phase. Sub-phases are independent — they can be sequenced any way that suits scheduling.

**Prerequisites:** Phase 2 complete — design docs exist for all 10 files.

---

## Sub-phase template (apply to each file)

For each file F:
1. Read the decomposition design at `findings/<F>_decomposition.md`
2. Create the new sub-module files with empty/skeleton contents
3. **TDD:** write a contract test asserting the public API surface of the original module is preserved
4. Move code from F into the sub-modules, one cohesive chunk at a time
5. Apply caller-update strategy:
   - **Option A:** F becomes a re-export shim
   - **Option B:** update every caller to import from new locations; delete F
6. Run the file's targeted tests
7. Run full sharded suite
8. Confirm post-split LOC of every resulting module <500
9. Mark sub-phase complete

---

## Sub-phases

### Sub-phase 3.1: `race_setup_screen.py` (1598) [Complex] ✅ COMPLETE 2026-04-27
- [x] Decomposition per `findings/race_setup_screen_decomposition.md` — PROJ-282 MVVM shape (NOT the panel-by-panel sketch, which was already done by PROJ-12/44/66/299)
- [x] All resulting modules <500 lines (controller at 480 — justified per §2.4)
- [x] Targeted tests pass
- [x] Full sharded suite passes
- [ ] Manual smoke: open the race setup screen (deferred — Phase 4.3)

**Notes:** Landed as 9-file `race_setup/` subpackage + Option-A 31-LOC shim at `race_setup_screen.py`. LOC: shim 31, `screen.py` 376, `controller.py` 480, `renderer.py` 234, `ship_preview.py` 163, `panel_factory.py` 177, `input_handler.py` 174, `llm_dialog_service.py` 154, `view_model.py` 88, `__init__.py` (small). All ≤500. Controller at 480 justified by §2.4 single-responsibility (17 mutation methods + save/load + validation).

Optional renderer split applied: `ship_preview.py` carved out per design.

`RaceSetupScreen.__init__` signature unchanged — `app.py:522` and `new_game_setup_screen.py:433` continue to construct it the same way.

**Phase-D Option-B migration applied:** `new_game_setup_screen.py:405` `from game.ui.screens.race_setup_screen import RaceBrowserDialog` → `from game.ui.screens.race_browser_dialog import RaceBrowserDialog`. Shim still re-exports for unmigrated callers.

Contract test at `tests/unit/ui/screens/test_race_setup_screen_public_api.py` (3 tests). PASSED pre-split AND post-split.

**Test patch-path migrations (~17 sites):** existing 1221-LOC test file's patches at `screen._method` retargeted to `screen._controller._method` / `screen._renderer._method` / `LLMDialogService.<fn>` based on where each method moved. Bypass-init helper `_make_race_setup_screen()` now wires `_view_model`, `_renderer`, `_controller`, `_input_handler`, `_llm_service`. Tests assigning `RaceConfig()` to `screen.race_config` mid-test now also assign to `screen._controller.race_config` (the authoritative reference). PROJ-299 `test_kill_*` tests switched from `screen._description_controller = ...` to constructing a mock MVVM controller exposing `controller.description_controller`. No assertion semantics changed — only patch paths and fixture wiring.

Targeted tests: `test_race_setup_screen.py` 57/57, `test_new_game_setup*.py` 33/33, `tests/unit/ui/screens/` 2127/2127, `tests/unit/ui/` 3524/3524.

Full sharded suite: **15544 / 15544 passed, 0 failed, 0 errors** (57.0s wall time).

**Latent items spotted (per Rule 3 — flagged, not silently changed):**
- Pre-existing `unused-variable: content_width` in `new_game_setup_screen.py:210` — unrelated.
- Original triple-duplicated dialog teardown in `_on_save_dialog_cancel` / `_on_overwrite_save` / `_on_save_as_new` was incidentally consolidated into `renderer.close_save_update_dialog()` (semantically identical, single point of truth — clean-sheet improvement during the move).
- `_show_llm_error_popup` button attribute now declared `None` in `__init__` for type clarity (semantics preserved).

---

### Sub-phase 3.2: `strategy_renderer.py` (1208) [Complex] ✅ COMPLETE 2026-04-27
- [x] Decomposition per `findings/strategy_renderer_decomposition.md`
- [x] All resulting modules <500 lines
- [x] Targeted tests pass
- [ ] Manual smoke: open strategy screen, verify every render layer (deferred — Phase 4.3)

**Notes:** Landed as 13-module `strategy_render/` subpackage + composer kept at `strategy_renderer.py`. Composer landed at 307 LOC (vs design's 120 estimate — overhead from instance-attribute monkey-patch compatibility shims, see test-edit note below). All 14 files <500. Largest layer module: `systems.py` 307.

`StrategyRenderer` class kept on the original module path. `BackgroundLayer` and `HexOutlineLayer` instance state owned by composer. `update()` increments `_elapsed_time`; `draw()` orchestrates layer-function calls.

**Latent bugs preserved verbatim (per design instruction; Rule-3 follow-ups captured):**
1. `screen_diameter` NameError in Dyson Sphere owner-flag path — now in `strategy_render/dyson_spheres.py` L 81/89/90 with `# noqa: F821 — preserved latent bug` comments. Triggers only when colonized Dyson Sphere has empire with no `'colony'` asset.
2. `_temp_screen_pos` / `_temp_draw_r` smeared onto planet domain objects — now in `strategy_render/systems.py` (multi-planet branch). Inline `PRESERVED CODE SMELL` comment.
3. Polar-angle table duplicated with `strategy_click_dispatcher.py:448` — flagged in `strategy_render/planets.py` module docstring; deferred per design.

**Test-monkey-patch compatibility:** Existing tests use INSTANCE-attribute monkey-patches (`renderer._draw_grid = MagicMock()`), not class-level `patch.object`. To preserve those, `_draw_*` methods kept on the composer as thin delegators; layer modules dispatch cross-layer hops through `r._draw_X(...)` to allow monkey-patching to intercept. Documented with `NOTE: dispatch through renderer wrapper` comments. Trade-off: ~80 LOC of wrapper boilerplate; tests untouched.

`_bg_*` and `_hex_outline_cache*` instance attributes exposed via @property forwarders on the composer for tests that read them. `WARP_POINT_ROTATION_SPEED` lives in `strategy_render/systems.py` with a re-export from `strategy_renderer.py` for the test_strategy_renderer_animation.py import.

Contract test at `tests/unit/ui/screens/test_strategy_renderer_public_api.py` (7 tests). PASSED pre-split AND post-split.

Targeted tests: `test_strategy_renderer.py` 66/66, `test_strategy_renderer_animation.py` 2/2, broader `tests/unit/ui/screens/` 2099/2099. Zero test edits required.

Full sharded suite: **15516 / 15516 passed, 0 failed, 0 errors** (53.6s wall time).

**Follow-ups captured:**
- (a) BUG ticket: fix the `screen_diameter` NameError in `dyson_spheres.py`.
- (b) Refactor: thread per-planet draw layout via a local `dict[planet_id, (pos, radius)]` instead of mutating domain models.
- (c) If test contract relaxes (instance-monkey-patches replaced with module-function patches), the wrapper boilerplate in the composer can be dropped (~80 LOC reclaim).

---

### Sub-phase 3.3: `test_lab/renderer.py` (1195) [Complex] ✅ COMPLETE 2026-04-27
- [x] Decomposition per `findings/test_lab_renderer_decomposition.md`
- [x] All resulting modules <500 lines
- [x] Targeted tests pass
- [ ] Manual smoke: open Combat Lab, verify scenario rendering (deferred — Phase 4.3)

**Notes:** Landed as 10-file `renderer/` subpackage (Option A — package replaces the file at the same import path). All files <500 LOC. Largest is `validation_panel.py` at 230. `__init__.py` re-exports `TestLabRenderer` so `from game.ui.screens.test_lab.renderer import TestLabRenderer` keeps working unchanged.

`TestLabRenderer._format_check_pair` and `._is_condition_verified` preserved as class-attribute aliases (staticmethod / thin instance-method delegators) so existing patches in `tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py` (19 tests) work without modification. The orchestrator wires panels in `__init__`; `CategoryPanel.draw(...)` returns `terminal_y` for the orchestrator to thread to the next panel — replaces a previous direct cross-panel call.

`_draw_helpers.py` (module-level functions) and `_condition_logic.py` (pure, no pygame) are exported for sub-phase 3.6 (`test_run_details`) to reuse — cross-review fix #3.

Contract test at `tests/unit/test_lab/test_renderer_public_api.py` (4 tests). PASSED pre-split AND post-split.

Targeted tests: 380 passed in `tests/unit/test_lab/`, `tests/unit/combat_lab/`, `tests/unit/ui/screens/test_lab/`. Subagent reported 18 failures in `combat_lab/services/test_test_execution_service.py` confirmed pre-existing on `main` HEAD via git-stash check (unrelated to PROJ-309). Broader `tests/unit/ui/`: 3470 passed.

Full sharded suite: **15497 / 15497 passed, 0 failed, 0 errors** (57.2s wall time). The 18 failures the subagent saw are excluded or path-filtered from the sharded runner.

**Viewmodel rect-attribute contract preserved** (cross-module write-side: panels write, `screen_input_handler.py` reads): `seed_mode_rects`, `seed_input_rect`, `group_header_rects`, `category_rects`, `tag_filter_rects`, `tag_clear_rect`, `test_list_panel_rect`, `run_all_tests_btn_rect`, `run_test_btn_rect`, `run_headless_btn_rect`, `run_baseline_btn_rect`, `update_expected_button_rect`, `update_expected_button_visible`, `scroll_offset`. Each write site moved with its panel.

---

### Sub-phase 3.4: `core/protocols.py` (1087) [Complex] ✅ COMPLETE 2026-04-27
- [x] Package layout per `findings/core_protocols_decomposition.md`
- [x] `game/core/protocols/__init__.py` re-exports all symbols (Option A mandatory)
- [x] All sub-files <500 lines
- [x] Targeted tests pass
- [x] Critical: import from `from game.core.protocols import X` works exactly as before for X in every protocol

**Notes:** Landed as a 9-file package. LOC per file: `__init__.py` 147, `boundary.py` 126, `combat.py` 133, `common.py` 46, `persistence.py` 27, `registry.py` 38, `strategy_domain.py` 194, `strategy_entities.py` 401, `ui.py` 112 — every file well under 500. Original 1087-LOC monolith deleted.

Contract test at `tests/unit/core/test_protocols_public_api.py` (46 tests, parametrized over 43 public symbols + 1 private-but-public `_has_attrs` + 2 metadata tests). Test PASSED against the monolith pre-split AND the package post-split, proving the public API was preserved exactly.

Full sharded suite: **15454 / 15454 passed, 0 failed, 0 errors** (51.7s wall time). Baseline (15405) + 46 new contract tests + 3 parametrized variants = 15454. Zero regressions.

`game/core/__init__.py` continues to do `from game.core.protocols import (...)` unchanged — Python resolves `protocols` as either a module or a package by name. No call-site edits required anywhere in the codebase (132 import statements across 80 files, all preserved).

The cross-review's pre-split decision (commit upfront to `strategy_entities.py` + `strategy_domain.py` rather than land borderline at ~520) was validated: `strategy_entities.py` measured 401 LOC actual (vs ~340 estimate); `strategy_domain.py` measured 194 (vs ~180 estimate). Both well under cap.

Open question #2 from design doc resolved: `_has_attrs` kept underscored, re-exported from `__init__.py` (no rename, no caller churn).
Open question #4 resolved: package replaces file (`game/core/protocols.py` deleted; `game/core/protocols/` package directory created at the same import path).

---

### Sub-phase 3.5: `command_handlers.py` (1076) [Complex] ✅ COMPLETE 2026-04-27
- [x] Domain-grouped handlers under `game/strategy/engine/handlers/` (8 modules, NOT one-per-handler — see design doc)
- [x] `command_handlers.py` becomes a re-export shim (Option A)
- [x] All resulting modules <500 lines
- [x] Targeted tests pass

**Notes:** Landed as 8 new files in `game/strategy/engine/handlers/` + Option-A shim. LOC: `__init__.py` 72, `base.py` 302, `build.py` 66, `construction_queue.py` 226, `movement.py` 214, `order_queue.py` 212, `registry_factory.py` 123, `transfer.py` 90, plus `command_handlers.py` shim 82 — every file well under 500. Original 1076-LOC monolith replaced.

Contract test at `tests/unit/strategy/engine/test_command_handlers_public_api.py` (23 tests over 21 public symbols + dispatch-completeness check). PASSED against the monolith pre-split AND post-split.

Full sharded suite: **15477 / 15477 passed, 0 failed, 0 errors** (55.5s wall time). Final result was clean; intermittent runs showed 1-4 flakes in unrelated tests (`test_collect_movements_respects_speed`, `test_fleet_fuel_consumed_during_movement`) that pass when run alone — consistent with the documented test-isolation flake pattern (cf. `test_colony_owner_id_matches_empire`). Pre-PROJ-309 baseline ALSO showed 15477/15477 green via git-stash verification, confirming these flakes are not regressions from this PROJ.

**Test patch-target migration (Rule-3 follow-through):** The original monolith imported `find_hybrid_path` at module level, so tests patched `game.strategy.engine.command_handlers.find_hybrid_path`. After decomposition, `add_move_order_if_needed` lives in `handlers/base.py` and references `find_hybrid_path` from THAT module's namespace. Patches at the shim level no longer intercept the actual call site. 5 test files updated to patch `game.strategy.engine.handlers.base.find_hybrid_path`: `tests/integration/strategy/test_command_handlers.py`, `tests/unit/strategy/test_command_handlers.py`, `tests/unit/strategy/engine/test_superweapon_command_handlers.py`, `tests/unit/strategy/engine/test_superweapon_edge_cases.py`, `tests/unit/strategy/engine/test_superweapon_handler_validation.py`. This is correct migration — adding a fake `find_hybrid_path` attribute on the shim would create an illegitimate API surface and wouldn't intercept the real call anyway.

**Open questions resolved:**
- Q1 (`superweapon_command_handlers` / `planet_command_handlers` migration into `handlers/`): kept where they are; out of scope per design. They now import `BaseCommandHandler` from `game.strategy.engine.handlers.base` (verified post-split).
- Q2 (shim deletion timeline): captured in shim docstring + System Migration Policy — schedule a follow-up PROJ once external callers migrate.
- Q3 (`BaseCommandHandler` mixin → module-level functions): out of scope; flagged for follow-up in design doc.

**Latent items NOT addressed (deferred):**
- `planet_command_handlers.py` 7× deferred imports of `BaseCommandHandler` — design doc risk #4. The cycle (if any) would still go through the same import target since the module path is preserved through the shim. Investigation is a separate follow-up; this PROJ is about size, not import architecture.

---

### Sub-phase 3.6: `test_run_details.py` (960) [Complex] ✅ COMPLETE 2026-04-27
- [x] Decomposition per design doc
- [x] All resulting modules <500 lines
- [x] Targeted tests pass
- [ ] Manual smoke: Combat Lab → run a test → open the details panel (deferred — Phase 4.3)

**Notes:** Landed as a 7-file `details/` subpackage + Option-A shim at the original path. LOC: shim 12, `panel.py` 216, `chrome.py` 244, `validation.py` 253, `resource_outcomes.py` 294, `propulsion_outcomes.py` 229, `draw_context.py` 62, `__init__.py` 17. Every file <500.

Cross-review fix #3 evaluated and intentionally NOT applied: the renderer's `_draw_helpers.py` (3.3) primitives are wrapping/bulleted-section helpers; `details/` uses two-column row layouts instead. Forcing reuse would be cosmetic — the two layout vocabularies don't overlap. Subagent kept `details/` self-contained around its own `DetailsDrawContext` + `OutcomePalette`. Documented decision; if a future need to share emerges, it can be addressed then.

UI-contract zone preserved verbatim: V/X/! glyphs, color-coded check names, Expected/Actual/Difference/p-value/Detail rows, phase headers (DATA/PRECONDITION/OUTCOME), big PASSED/FAILED badge, EXACT MATCH formatting, `0 (depleted)` / `Within tolerance` / `(Hits not tracked - seekers in flight)` strings — character-for-character. Theme color lookup remained late-bound (`_phase_color()`) for test compatibility.

Action-button rect contract preserved: `chrome.draw_action_buttons` returns an `ActionButtonRects` dataclass; `panel.draw` mirrors the three rects onto the same `self.view_states_button_rect` / `self.use_seed_button_rect` / `self.copy_results_button_rect` attributes so `handle_event`'s hit-test reads the same surface as before.

Contract test at `tests/unit/test_lab/test_test_run_details_public_api.py` (12 tests). PASSED pre-split AND post-split.

Targeted tests: 392 passed in `tests/unit/test_lab/`, `tests/unit/combat_lab/`, `tests/unit/ui/screens/test_lab/`. 18 pre-existing failures in `combat_lab/services/test_test_execution_service.py` (verified pre-existing in 3.3 closeout) were ignored as instructed. Zero PROJ-309-3.6 regressions.

Full sharded suite: **15508 / 15509 passed, 1 failed** — the failure is the documented test-isolation flake `test_colony_owner_id_matches_empire` (per MEMORY.md and CLAUDE.md), not introduced by this sub-phase.

---

### Sub-phase 3.7: `strategy_session_facade.py` (928) [Complex] ✅ COMPLETE 2026-04-27
- [x] Per-domain facade slices
- [x] All resulting modules <500 lines
- [x] Targeted tests pass

**Notes:** Landed as composer + 8-slice subpackage `game/strategy/facade/slices/`. LOC: composer 476, `_facade_state.py` 98, `command_dispatch_slice.py` 219, `economy_slice.py` 174, `fleet_slice.py` 138, `system_slice.py` 131, `planet_slice.py` 105, `empire_slice.py` 97, `event_slice.py` 64, `__init__.py` 7 — every file under 500. Composer landed higher than the design's ~280 estimate due to ~50 LOC of legacy cache-attribute property forwarders (`_planet_index`, `_fleets_by_hex_cache`, `_all_stars_cache`, `_race_registry`, plus turn-stamp companions) that backward-compat tests read+write directly.

`FacadeSessionState` dataclass (in `slices/_facade_state.py`) owns the shared `_get_X_by_id` helpers + caches. Slices reach state via `state`, never into each other.

Contract test at `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` (5 tests). PASSED pre-split AND post-split.

Targeted scope: 869 tests passed across `tests/unit/strategy/facade/`, `tests/integration/strategy/`, `tests/integration/colonization/`, `tests/integration/ui/`, plus projector/treasury/planet-list tests. Zero test edits required.

Full sharded suite: **15493 / 15493 passed, 0 failed, 0 errors** (56.3s wall time).

**Test-mock compatibility detail:** `test_facade_dispatch.py` patches `facade.handle_command = MagicMock(...)` and asserts the mock is called. Solution: dispatch slice receives `handle_command` as a callable resolving `self.handle_command` at call time (`lambda cmd: self.handle_command(cmd)`), so monkey-patching the composer's instance attribute still intercepts dispatch.

**Documentation follow-up:** design doc open question #6 noted that `docs/02_PATTERNS.md` and `docs/systems/strategy_layer.md` could document the slice composition pattern. Captured as a Phase 4 follow-up to bundle with other doc updates from PROJ-309.

---

### Sub-phase 3.8: `workshop_viewmodel.py` (873) [Complex] ✅ COMPLETE 2026-04-27
- [x] Decomposition per design doc
- [x] All resulting modules <500 lines
- [x] Targeted tests pass
- [ ] Manual smoke: open Workshop, exercise all tabs (deferred — Phase 4.3 manual smoke step)

**Notes:** Landed as 4 files, all <500 LOC: `workshop_viewmodel.py` (slimmed core, 462 LOC), `workshop_viewmodel_ship_ops.py` (351 LOC), `workshop_viewmodel_layer_ops.py` (261 LOC), `workshop_viewmodel_selection.py` (138 LOC). Public `WorkshopViewModel` class kept on the same module path; helpers are private composition (`self._ship_ops`, `self._layer_ops`) following the existing `WorkshopShipIO` precedent. Selection state remains owned by the viewmodel; selection helpers are stateless module-level functions.

Contract test at `tests/unit/workshop/test_workshop_viewmodel_public_api.py` (11 tests) asserts every public method/property on `WorkshopViewModel` survives the refactor. PASSED pre-split AND post-split.

Targeted tests: 191 passed across `tests/unit/workshop/`, `tests/unit/ui/screens/test_workshop_*`, and `tests/unit/builder/`. Zero test edits required.

Full sharded suite: **15488 / 15488 passed, 0 failed, 0 errors** (51.6s wall time).

**Behavioral fix flagged by implementing agent:** in `apply_append_selection`, the original monolith mutated `self._selected_components` mid-loop in toggle mode without recomputing the membership set, leaving an inconsistent state if `incoming` contained the same component twice. The new code keeps `result` and `current_objs` in sync. The edge case is not exercised by any test (all 15488 still pass); the fix is documented inline. Per Rule 3 (clean-sheet design), accepted.

**Open questions resolved:**
- Q1 (`validate_design` placement): moved to `WorkshopShipOps` per design proposal; viewmodel keeps a one-line forwarder.
- Q4 (layer-ops constructor): receives `registries` directly, keeping helper independently testable without a full viewmodel.

---

### Sub-phase 3.9: `app.py` (855) [Complex] ✅ COMPLETE 2026-04-27
- [x] Bootstrap / run-loop / screen-router as separate modules
- [x] All resulting modules <500 lines
- [x] Targeted tests pass
- [ ] Manual smoke: launch the game (deferred — Phase 4.3, MANDATORY)

**Notes:** Landed as 4-file split: `app.py` 444 LOC (slim `Game` shell + `_SCREEN_TRANSITIONS` + `main()` + crash handler), `app_bootstrap.py` 202 LOC (pure init + `BootstrapResult` + `configure_logging` + `parse_args`), `screen_router.py` 496 LOC (`ScreenRouter` + `SceneCallbacks` + scene lifecycle), `run_loop.py` 211 LOC. All <500.

`Game.__init__(self, args=None)` signature unchanged. `from game.app import Game, main` still works. All 5 callers (1 production: `launcher.py`; 4 test files) work without edits.

**6 initialization-order invariants preserved verbatim and locked by new test:**
1. `pygame.init()` before `pygame.display.Info()` / `set_mode()` / pygame_gui.
2. `pygame.font.init()` before any `get_font()` call.
3. `ApplicationContext.create_production()` before `get_default_registry_provider()`.
4. `load_components` / `load_modifiers` before `initialize_ship_data`.
5. `SpriteManager.load_sprites` after registries but before scene constructors.
6. `MenuScene` constructor before any overlay-dialog code path.

`tests/unit/test_app_bootstrap_invariants.py` (6 tests) locks call ordering via mock patches.

**`ResourceCatalog.from_json()` deduplicated:** original `app.py:160` + `app.py:182` double call eliminated. Bootstrap loads once into local `catalog`, hydrates `ctx.registry_manager.resources` AND passes the same instance into `GameRegistries(...resource_catalog=catalog)`.

**Test compatibility preserved:** Scene-attribute properties (`battle_scene`, `strategy_scene`, etc.) use `_route_get`/`_route_set` delegating to `_router` when present, falling back to `__dict__` for `Game.__new__`-bypass tests. `_handle_*_action` / `_return_to` methods kept on `Game` (router doesn't duplicate); scene callbacks via `SceneCallbacks` dataclass with bound methods so `game._handle_strategy_action = MagicMock()` mocks intercept correctly.

Contract test at `tests/unit/test_app_public_api.py` (32 tests). PASSED pre-split AND post-split.

Targeted tests: 89 passed across `test_app_public_api.py`, `test_app_bootstrap_invariants.py`, `test_app_integration.py`, `test_main_integration.py`. Broader: `tests/unit/` 14337 passed, `tests/integration/` 1069 passed + 2 skipped, `tests/regression/` 110 passed.

Full sharded suite: **15582 / 15582 passed, 0 failed, 0 errors** (54.9s wall time).

**Latent items flagged (preserve-and-flag):**
- `BootstrapResult` is frozen dataclass; `RunLoop._handle_resize` uses `object.__setattr__` to update display state (necessary because pygame `set_mode` returns a new surface). Future cleaner design: split mutable display state into separate dataclass.
- `start_builder(return_to=...)` and `on_builder_return(custom_ship=...)` parameters preserved as unused (per source). Cleanup deferred.
- 5 property forwarders on `Game` (`battle_scene`, `strategy_scene`, etc.) cost ~50 LOC. Once tests migrate to `game._router.battle_scene`, these can be deleted (follow-up).

**Mandatory manual smoke required at Phase 4.3:** launch the game; main menu → strategy → battle → return. No automated test can fully verify the entry point's runtime behavior.

**REGRESSION SURFACED + FIXED 2026-04-27** (during user manual smoke):
- **Symptom:** `AttributeError: 'ScreenRouter' object has no attribute '_create_workshop_context'` when clicking "Design" on the Strategy screen (path: `_handle_strategy_action("open_builder")` → `_create_workshop_context(...)` → broken delegation).
- **Cause:** Sub-phase 3.9 implementing agent's report claimed `_create_workshop_context` had moved to `ScreenRouter`, but only the docstring reference was added — the method itself was never copied. The original `Game._create_workshop_context` body was a self-contained 30-LOC builder reading `self.registries` with zero router-state dependency, so it never had business living on the router.
- **Fix:** Restored the original method body inline in `Game._create_workshop_context` (uses `self.registries` directly); removed `_create_workshop_context` from `screen_router.py`'s module docstring and added a clarifying note that the method intentionally stays on `Game`.
- **Regression test:** `tests/unit/test_app_create_workshop_context.py` (4 tests) covers the empire-missing / session-missing / valid-inputs / no-save-path branches via bypass-init `Game.__new__(Game)`. Pre-fix all 4 raised the AttributeError; post-fix all 4 pass.
- **Suite:** 15586/15586 (was 15582 + 4 new regression tests).
- **Lesson for future agent-driven decompositions:** subagent reports describe what the agent *intended*; verify what *actually* landed. The mandatory manual-smoke gate caught this — exactly the case the design called out as "no automated test can fully verify the entry point's runtime behavior."

---

### Sub-phase 3.10: `strategy_window_manager.py` (817) [Complex] ✅ COMPLETE 2026-04-27
- [x] Per-window-family registrars + composition root
- [x] All resulting modules <500 lines
- [x] Targeted tests pass
- [ ] Manual smoke: open and close every sub-window on the strategy screen (deferred — Phase 4.3)

**Notes:** Landed as 13-module `strategy_windows/` subpackage + composition root kept at `strategy_window_manager.py`. Composer landed at 334 LOC (vs design's 180 estimate; extra 150 LOC is legacy `_on_*_closed` delegations called by `StrategyEventRouter._handle_window_close` and existing tests). Largest registrar: `dispatch.py` 129. All 14 files <500.

`StrategyWindowManager` class kept on the original module path. The 14 (now 15) window-slot attributes preserved as direct instance attributes for `StrategyEventRouter.has_modal_open()` to read.

**Latent bug FIXED (authorized clean-sheet fix):** `planet_abilities_window` slot now `None`-initialized in `__init__` AND included in `StrategyEventRouter.has_modal_open()` (now 15-slot scan) and `_is_blocking_ui_element_at()`. Contract test reflects 15 slots.

**Closure-capture risks resolved:** `open_orders_window` (3 command closures) and `open_fleet_report_window` (split-fleet closure) refactored to capture `facade` / `owner_id` as explicit local bindings, making them resilient to future `self.scene.facade` rebinding.

**Local-import preservation:** All 6 method-scope imports kept intact (`OrdersWindow`, `SettingsWindow`, `TransferDialog`+`CargoQuickDialog`, `PlanetAbilitiesWindow`+`StrategyEventRouter`+`get_default_registry_provider`, `pygame_gui.windows`) per design risk #5. Independent cycle verification deferred to follow-up.

Contract test at `tests/unit/ui/screens/test_strategy_window_manager_public_api.py` (25 tests). PASSED pre-split AND post-split.

**Test patch-target migrations (Rule-3 follow-through):** `test_strategy_window_manager.py` patched 24 `@patch('strategy_window_manager.<Class>')` decorators to the registrar paths (e.g. `strategy_windows.list_windows`, `strategy_windows.build_queue_windows`) since registrars now import the window classes themselves. `test_sub_window_hotkeys.py` updated similarly. 4 fixture files (`test_strategy_event_router.py`, `test_click_gate_integration.py`, `test_event_log_window.py`, `test_strategy_ui_menu.py`) added `wm.planet_abilities_window = None` to MagicMock fixtures since `has_modal_open` now scans that slot.

Targeted tests: 114 (contract+window_manager+event_router+sub_window_hotkeys), 2124 in `tests/unit/ui/screens/`, 3521 in `tests/unit/ui/`. All green.

Full sharded suite: **15541 / 15541 passed, 0 failed, 0 errors** (54.4s wall time).

**Follow-up captured:** legacy `_on_*_closed` delegations (~150 LOC) could be deleted once `StrategyEventRouter._handle_window_close` and existing tests migrate to call `wm._<registrar>._on_closed()` directly.

---

## Phase Completion Checklist
- [x] All 10 sub-phases complete
- [x] No file in `game/` newly introduced by this project exceeds 500 LOC (controllers at 480, routers at 496 — within cap, justified)
- [x] No re-export shim is permanently load-bearing without justification (each shim's Notes entry covers why it's there)
- [x] Full sharded suite at 15389+ baseline maintained (final: **15582/15582**)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 4)
