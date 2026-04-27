# PROJ-309 File Manifest

## Files

### EDIT (convention)
| File | Type | Notes |
|------|------|-------|
| `CLAUDE.md` | Instructions | Add 500-LOC rule under Code Quality |
| `docs/03_CONVENTIONS.md` | Docs | Add §File Size section |

### EDIT or DELETE (decomposition targets — per Phase 2 design)
| File | Lines (current) | Fate / Status |
|------|----------------:|---------------|
| `game/ui/screens/race_setup_screen.py` | 1598 | **SHIMMED 2026-04-27 (3.1 ✅)** — Option-A 31-LOC shim; logic in `race_setup/` 9-file MVVM subpackage |
| `game/ui/screens/strategy_renderer.py` | 1208 | **EDITED 2026-04-27 (3.2 ✅)** — slimmed composer (307 LOC); 13-module `strategy_render/` subpackage |
| `game/ui/screens/test_lab/renderer.py` | 1195 | **DELETED 2026-04-27 (3.3 ✅)** — replaced by `game/ui/screens/test_lab/renderer/` 10-file subpackage |
| `game/core/protocols.py` | 1087 | **DELETED 2026-04-27 (3.4 ✅)** — replaced by `game/core/protocols/` 9-file package |
| `game/strategy/engine/command_handlers.py` | 1076 | **SHIMMED 2026-04-27 (3.5 ✅)** — Option-A re-export shim (82 LOC); logic in `handlers/` package |
| `game/ui/screens/test_lab/test_run_details.py` | 960 | **SHIMMED 2026-04-27 (3.6 ✅)** — Option-A 12-LOC shim; logic in `details/` subpackage |
| `game/strategy/facade/strategy_session_facade.py` | 928 | **EDITED 2026-04-27 (3.7 ✅)** — slimmed composer (476 LOC); 8-slice subpackage at `slices/` |
| `game/ui/screens/workshop_viewmodel.py` | 873 | **EDITED 2026-04-27 (3.8 ✅)** — slimmed to 462 LOC; helpers extracted to `workshop_viewmodel_*.py` siblings |
| `game/app.py` | 855 | **EDITED 2026-04-27 (3.9 ✅)** — slimmed to 444 LOC; `app_bootstrap.py`, `screen_router.py`, `run_loop.py` extracted |
| `game/ui/screens/strategy_window_manager.py` | 817 | **EDITED 2026-04-27 (3.10 ✅)** — slimmed composition root (334 LOC); 13-module `strategy_windows/` subpackage |

### NEW (created by decompositions — final shape per Phase 2 designs)
- `game/ui/screens/race_setup/*.py` (sub-modules)
- `game/ui/screens/strategy_render/*.py`
- `game/ui/screens/test_lab/renderer/*.py` (LANDED 2026-04-27 in sub-phase 3.3) — `__init__.py`, `orchestrator.py`, `header_panel.py`, `category_panel.py`, `tag_filter_panel.py`, `test_list_panel.py`, `metadata_panel.py`, `validation_panel.py`, `_draw_helpers.py` (module-level functions, intended for reuse by sub-phase 3.6), `_condition_logic.py` (pure, no pygame).
- `game/core/protocols/*.py` (LANDED 2026-04-27 in sub-phase 3.4) — `__init__.py`, `common.py`, `registry.py`, `strategy_entities.py`, `strategy_domain.py`, `combat.py`, `boundary.py`, `ui.py`, `persistence.py`
- `game/strategy/engine/handlers/*.py` (LANDED 2026-04-27 in sub-phase 3.5) — `__init__.py`, `base.py`, `build.py`, `construction_queue.py`, `movement.py`, `order_queue.py`, `registry_factory.py`, `transfer.py` (8 modules; domain-grouped, not one-per-handler)
- `game/strategy/facade/slices/*.py` (LANDED 2026-04-27 in sub-phase 3.7) — `__init__.py`, `_facade_state.py` (FacadeSessionState shared cache), `command_dispatch_slice.py`, `fleet_slice.py`, `planet_slice.py`, `system_slice.py`, `empire_slice.py`, `economy_slice.py`, `event_slice.py`. Composer in `strategy_session_facade.py` (kept at original path) wires them.
- `game/ui/screens/workshop_viewmodel_*.py` (LANDED 2026-04-27 in sub-phase 3.8) — `workshop_viewmodel_ship_ops.py` (351 LOC), `workshop_viewmodel_layer_ops.py` (261 LOC), `workshop_viewmodel_selection.py` (138 LOC). Note FLAT layout per `docs/03_CONVENTIONS.md` §1.3 — workshop modules are NOT in a `workshop/` subdir.
- `game/<bootstrap_or_runloop>.py` (split out of app.py)
- `game/ui/screens/strategy_windowing/*.py`

(Exact paths decided in Phase 2 per-file design docs.)

### NEW (project artifacts) — Phase 2 deliverables (LANDED 2026-04-27)
- `Projects/active_projects/PROJ-309/findings/race_setup_screen_decomposition.md`
- `Projects/active_projects/PROJ-309/findings/strategy_renderer_decomposition.md`
- `Projects/active_projects/PROJ-309/findings/test_lab_renderer_decomposition.md`
- `Projects/active_projects/PROJ-309/findings/core_protocols_decomposition.md`
- `Projects/active_projects/PROJ-309/findings/command_handlers_decomposition.md`
- `Projects/active_projects/PROJ-309/findings/test_run_details_decomposition.md`
- `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md`
- `Projects/active_projects/PROJ-309/findings/workshop_viewmodel_decomposition.md`
- `Projects/active_projects/PROJ-309/findings/app_decomposition.md`
- `Projects/active_projects/PROJ-309/findings/strategy_window_manager_decomposition.md`
- `Projects/active_projects/PROJ-309/findings/_cross_design_review.md` — Phase 2.11 cross-design review (APPROVE WITH FIXES)
- `Tools/check_file_size.py` (LANDED 2026-04-27 in Phase 4.4) — walks `game/`, fails if any production file >500 LOC. Run via `python Tools/check_file_size.py [--max N] [--quiet]`. Currently reports 52 OUT-OF-SCOPE violations; PROJ-309's 10 targets all clear.

### NEW (tests)
- Per sub-phase: TDD contract tests for the public API surface preservation. Paths under `tests/unit/`
- `tests/unit/core/test_protocols_public_api.py` (LANDED 2026-04-27 in sub-phase 3.4) — 46 tests parametrized over 43 public symbols + `_has_attrs` + 2 metadata tests. Asserts every symbol remains importable from `game.core.protocols` post-decomposition.
- `tests/unit/strategy/engine/test_command_handlers_public_api.py` (LANDED 2026-04-27 in sub-phase 3.5) — 23 tests parametrized over 21 public symbols + dispatch-completeness check. Asserts every symbol remains importable from `game.strategy.engine.command_handlers` (the shim).
- `tests/unit/workshop/test_workshop_viewmodel_public_api.py` (LANDED 2026-04-27 in sub-phase 3.8) — 11 tests asserting every public method/property on `WorkshopViewModel` survives the helper-extraction refactor.
- `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` (LANDED 2026-04-27 in sub-phase 3.7) — 5 tests asserting every public symbol on `StrategySessionFacade` (including `_planet_index`, `_get_fleet_by_id`, etc. that tests reach into) survives the slice extraction.
- `tests/unit/test_lab/test_renderer_public_api.py` (LANDED 2026-04-27 in sub-phase 3.3) — 4 tests asserting `TestLabRenderer` and class-attribute aliases (`_format_check_pair`, `_is_condition_verified`) remain importable from `game.ui.screens.test_lab.renderer`.

### EDIT (test patch-target migration, sub-phase 3.5)
- `tests/integration/strategy/test_command_handlers.py`
- `tests/unit/strategy/test_command_handlers.py`
- `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
- `tests/unit/strategy/engine/test_superweapon_edge_cases.py`
- `tests/unit/strategy/engine/test_superweapon_handler_validation.py`
  Updated patch targets from `game.strategy.engine.command_handlers.find_hybrid_path` to `game.strategy.engine.handlers.base.find_hybrid_path` — the function is now imported at the new module's call site, so patches must follow.

### EXPLICITLY EXCLUDED
- The other 52 files >500 LOC
- Test files (long test files often legitimate)
- Files where the public API surface intentionally changes (out of scope)
