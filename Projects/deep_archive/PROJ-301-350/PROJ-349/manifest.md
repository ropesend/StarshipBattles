# PROJ-349 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/planetary_facility.py` | Production (delete + tests) | T6.1 — user-confirmed deletion of legacy `resource_levels` fallback |
| `tests/unit/strategy/data/test_planetary_facility_characterization.py` | Test (update) | T6.1 — update tests at lines 95-108 (currently pin the legacy alias) |
| `game/ui/panels/race_environment_panel.py` | Production (annotation) | T6.2 — annotate broad catch at lines 322-333 |
| `game/strategy/engine/action_execution_engine.py` | Production (refactor) | T6.3 — use injected `action_time_resolver` at line 165-168 (or remove DI parameter) |
| `tests/unit/strategy/engine/test_action_execution_engine_gaps.py` | Test (rewrite) | T6.3 — rewrite line 128-156 to assert injected resolver IS consulted |
| `game/ui/screens/planet_abilities_controller.py` | Production (refactor) | T6.4 — replace hardcoded ability lists at lines 29-48 with registry scan |
| `game/services/llm/errors.py` | Production (add) | T6.5 — add `LLMUnexpectedError` to ErrorCode taxonomy |
| `game/ui/screens/strategy_screen_lifecycle.py` | Production (refactor) | T6.6 — track load dialog as blocking modal |
| `game/ui/screens/strategy_window_manager.py` | Production (refactor) | T6.6 — add load/save selection slot |
| `docs/05_ERROR_HANDLING.md` | Doc (timestamp) | T6.7 — bump "Last verified" |
| `Tools/lint_test_files.py` | Tool (possible add) | T6.8 — facade `_session` enforcement decision |
| `game/services/llm/background.py` | Production (refactor) | T7 — fix `_done_event` race (set after `_active_workers` cleanup) |
| `tests/unit/strategy/engine/test_production_spawner.py` | Test (tighten) | T7 — `assert_called_once` → `assert_called_once_with(...)` per dispatch test |
| `tests/unit/strategy/turn_engine/test_*team_modifiers*.py` | Test (rewrite) | T7 — replace brittle import patch |
| `tests/unit/...` (multiple) | Tests (annotate or rewrite) | T7 — dead-branch pins, factory tests, from_dict gaps, vacuous constants, font quantize, format_value, shortage flags |
| `tests/unit/...` (PROJ-321 rewrite) | Test (NEW) | T7 — recover deleted `test_start_battle_ship_builder_*` from history; rewrite |
| `tests/unit/...` (TestRegisterOnConstruction) | Test (rewrite) | T7 — actually test construction-registration |
| `tests/fixtures/ui_widget_factory.py` (`bypass_init`) | Tool (possible refactor) | T7 — MRO leak risk under pytest-xdist parallel |
| `Projects/active_projects/PROJ-349/plan.md` | Project artifact | Updates per phase |
| `Projects/projects_index.md` | Project index | Final status update at end of Phase 3 |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 (Tier 6) | `pytest tests/unit/ -q` then `python Tools/lint_test_files.py` |
| 2 (Tier 7) | same |
| 3 (closeout) | `python Tools/test_sharded/test_sharded.py` from repo root |
