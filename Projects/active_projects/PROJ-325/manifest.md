# PROJ-325 File Manifest

> Generated during planning. Used by `/proj-parallel` for conflict detection.
> Updated if implementation discovers additional files.

## Phase 1 (PROJ-323 documentation corrections)

| File | Type | Change |
|------|------|--------|
| `Projects/active_projects/PROJ-323/phase_3_checklist.md` | Doc | Re-mark Tasks 3.3 + 3.6 as `_(skipped — upstream project already deleted target file)_`. Resolve Task 3.10 ambiguity (FND-CC-001, FND-CC-005). |
| `Projects/active_projects/PROJ-323/plan.md` | Doc | Reconcile "items" vs "tasks" terminology + LOC delta annotations (FND-CC-002, FND-CC-003). |
| `Projects/active_projects/PROJ-323/design.md` | Doc | Fix line 41 deleted-file reference, line 42 mischaracterization (FND-P2-003, FND-P2-005). |
| `Projects/active_projects/PROJ-323/manifest.md` | Doc | Remove ~42 stale entries for files PROJ-321 deleted (FND-CC-004). Add comment at top documenting the cleanup. |
| `tests/unit/simulation/projectile/test_projectile_manager.py` | Test | Task 5.19 precision mismatch: relax tolerance OR add intermediate values to docstring (FND-P2-001). |

## Phase 2 (PROJ-323 Tasks 3.34 + 3.37 parametrize)

| File | Type | Change |
|------|------|--------|
| `tests/unit/strategy/engine/test_command_handlers.py` | Test | Two-group class-level parametrize over 11 `fleet_not_found` handler tests. ~75 LOC saved. Verify file path (PROJ-323 plan.md says `test_command_handlers.py` — confirm location.) |
| `tests/unit/strategy/data/test_fleet_cargo_resources.py` (or similar) | Test | Parametrize 4 zero/negative cargo amount tests across load/unload. ~10 LOC saved. Identify exact file in Phase 2 Task 2.2. |

## Phase 3 (RaceSetupScreen — conditional on PROJ-324 Phase 3 Task 3.4 outcome)

### GO path (bypass_init suffices)

| File | Type | Change |
|------|------|--------|
| `tests/unit/ui/screens/test_race_setup_screen.py` | Test | Migrate per PROJ-324 pattern: `bypass_init(RaceSetupScreen)` + `make_ui_widget`. ~1464 LOC file; ~150 tests. |

### NO-GO path (production refactor required)

| File | Type | Change |
|------|------|--------|
| `game/ui/screens/race_setup/screen.py` | Production | Extract 8 panel constructions to a `PanelRegistry` protocol passed via `__init__`. Default `RaceSetupPanelFactory` in production; `MockPanelRegistry` in tests. |
| `tests/unit/ui/screens/test_race_setup_screen.py` | Test | Migrate to use `MockPanelRegistry` injection — eliminates need for `bypass_init` for those code paths. |
| (potentially) `game/ui/screens/race_setup/panel_registry.py` (NEW) | Production | Protocol definition + default implementation. |
| (potentially) `tests/fixtures/race_setup_panel_registry.py` (NEW) | Production (test infra) | Mock implementation for tests. |

## Files explicitly NOT touched

These are owned by sibling continuation projects:

| File | Owner | Why excluded |
|------|-------|--------------|
| `game/ui/screens/strategy_modal_window.py`, `game/ui/screens/new_game_setup_screen.py`, `game/services/llm/background.py`, `tests/fixtures/ui_widget_factory.py` | PROJ-324 | bypass_init flag + LLM Event |
| `tests/unit/ui/screens/test_fleet_report_window*.py`, `test_workshop_screen.py`, `test_new_game_setup_extended.py`, `test_sub_window_hotkeys.py`, `test_build_queue_list_window.py`, `test_strategy_modal_window.py` | PROJ-324 Phase 3 | 13 of 14 unblocked PROJ-322 deferrals |
| `Tools/` (linter scripts), `tests/regression/test_no_dead_test_files.py` (NEW), `tests/integration/ui/test_system_tree_panel_smoke.py` (NEW), `tests/unit/strategy/facade/test_strategy_session_facade_contract.py` (NEW) | PROJ-326 | Linter + SystemTreePanel + facade contract |
| `tests/unit/ui/components/test_virtual_table.py` | PROJ-327 | 700-LOC `@patch` decorator sweep (PROJ-322 Task 3.14) |
| Mutable-mock fixture rescope candidates (PROJ-322 Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15) | PROJ-327 | Phase 2 of PROJ-327 |
| `tests/unit/ui/screens/test_strategy_screen.py` (or wherever the 50-test cluster lives) | PROJ-327 | PROJ-322 Task 3.25 strategy_screen refactor |
