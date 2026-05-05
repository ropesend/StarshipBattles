# PROJ-342 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/test_lab/screen.py` | Production (refactor) | New constructor signature; drop `self.game`; add `_require_display_surface()` helper; replace 12 `self.game.*` accesses; absorb `BattleStateViewer` sizing fix and resize forwarding |
| `game/screen_router.py` | Production (refactor) | Update `TestLabScreen` construction at lines 123-127 to new signature; remove legacy `# NB:` comment |
| `combat_lab/services/test_lab_controller.py` | Production (refactor) | Drop `game` param from `__init__`; delete `handle_run_visual` and `handle_run_headless`; remove `TestExecutionService`/`TestResultsService` imports and instantiations |
| `combat_lab/services/test_execution_service.py` | Production (DELETE) | Orphan service — no production callers after Phase 4 |
| `combat_lab/services/test_results_service.py` | Production (DELETE) | Orphan service — no production callers after Phase 4 |
| `combat_lab/services/__init__.py` | Production (update) | Remove `TestExecutionService` and `TestResultsService` exports |
| `combat_lab/services/scenario_run_helper.py` | Production (docstring update) | Lines 4 and 68 reference deleted service in comments/docstrings |
| `combat_lab/runner.py` | Production (docstring update) | Lines 62-64 and 88-90 docstrings reference `TestExecutionService` — update to `TestLabExecutor` |
| `combat_lab/COMBAT_LAB_DOCUMENTATION.md` | Documentation (update) | Sections at lines 73-74, 161-162, 222-226, 259 describe deleted services and old run-flow |
| `game/simulation/battle_controller.py` | Production (docstring update) | Lines 113-116 and 254-260 docstrings reference `test_execution_service.py` |
| `tests/unit/test_lab/test_render_progress_no_game_handle.py` | Test (NEW) | Phase 1 regression tests pinning current crash + new constructor contract |
| `tests/unit/test_lab/test_handle_resize_forwards_to_viewer.py` | Test (NEW) | Phase 5 regression test for `BattleStateViewer.handle_resize` forwarding |
| `tests/unit/test_lab/test_visual_run.py` | Test (update) | Replace `mock_game` fixture with `mock_battle_scene`; update construction and assertion call sites |
| `tests/unit/combat_lab/services/test_test_execution_service.py` | Test (DELETE) | Tests for deleted service |
| `tests/unit/combat_lab/services/test_controller_execution.py` | Test (update or DELETE) | All tests calling `controller.handle_run_headless()` are removed; if file becomes empty, delete it |
| `tests/unit/combat_lab/services/test_controller_init_events.py` | Test (update) | Remove tests calling `controller.handle_run_visual()` (lines 148-200); update remaining controller construction to drop `game=` |
| `tests/unit/combat_lab/services/conftest.py` | Test (update) | Remove `mock_game` fixture if used only by deleted tests |
| `Projects/active_projects/PROJ-342/plan.md` | Project artifact | Updated as phases progress |
| `Projects/active_projects/PROJ-342/phase_*_checklist.md` | Project artifact | Tasks checked off as completed |
| `Projects/projects_index.md` | Project index | Status updates per phase |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 | `pytest tests/unit/test_lab/test_render_progress_no_game_handle.py -x` (must FAIL on current code) |
| 2 | `pytest tests/unit/test_lab/test_render_progress_no_game_handle.py -x` (must PASS) |
| 3 | `pytest tests/unit/ui -x` |
| 4 | `pytest tests/unit/combat_lab/services -x` |
| 5 | `pytest tests/unit/test_lab tests/unit/combat_lab/services -x` |
| 6 | Manual: `git grep -nE "TestExecutionService\|TestResultsService\|handle_run_(visual\|headless)" -- combat_lab game docs` returns 0 |
| 7 | `python Tools/test_sharded/test_sharded.py` + manual `python launcher.py` smoke |

## Baseline reference

**Pre-PROJ-342 sharded suite (recorded 2026-05-04):**
- Total: 17,202 tests
- Passed: 17,198
- Failed: 0
- Errors: 0
- Skipped: 4
- Wall time: 53.1s (16 shards)
