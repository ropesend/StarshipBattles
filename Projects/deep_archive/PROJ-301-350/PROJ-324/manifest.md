# PROJ-324 File Manifest

> Generated during planning. Used by `/proj-parallel` for conflict detection.
> Updated if implementation discovers additional files.

## Production files (Phases 1-2)

| File | Type | Phase | Change |
|------|------|-------|--------|
| `game/ui/screens/strategy_modal_window.py` | Production | 1 | Add `bypass_init` guard at start of `__init__`. Covers 4 subclasses transitively. |
| `game/ui/screens/race_setup/screen.py` | Production | 1 | Add `bypass_init` guard at start of `__init__`. |
| `game/ui/screens/new_game_setup_screen.py` | Production | 1 | Add `bypass_init` guard at start of `__init__`. |
| `game/ui/screens/build_queue_list_window.py` | Production | 1 | Verify `bypass_init` works transitively from `StrategyModalWindow`; if subclass does explicit parent calls, add own guard. |
| `game/ui/screens/fleet_report_window.py` | Production | 1 | Verify `bypass_init` works transitively. |
| `game/ui/screens/orders_window.py` | Production | 1 | Verify `bypass_init` works transitively. |
| `game/ui/screens/transfer_dialog.py` | Production | 1 | Verify `bypass_init` works transitively. |
| `game/services/llm/background.py` | Production | 2 | Add `_done_event: threading.Event`, set in `_run()` terminal states, expose `wait(timeout)` method. |

## Test infrastructure files (Phases 1-2)

| File | Type | Phase | Change |
|------|------|-------|--------|
| `tests/fixtures/ui_widget_factory.py` | Production (test infra) | 1 | Add `bypass_init(Cls)` context manager. Module already exists from PROJ-322 Phase 5. |
| `tests/fixtures/test_ui_widget_factory.py` | Test | 1 | Add smoke test for `bypass_init` context manager — set/unset cleanup, exception path cleanup, nested-context safety. |

## Test files migrated (Phase 3)

| File | Type | PROJ-322 Task | Notes |
|------|------|---------------|-------|
| `tests/unit/services/llm/test_background.py` | Test | 4.3 | Replace 5-6 polling loops with `call.wait(timeout=2.0)`. |
| `tests/unit/ui/screens/test_fleet_report_window.py` | Test | 5.6 | APC-001 → `make_ui_widget` w/ `bypass_init`. ~457 LOC; expect significant test simplification. |
| `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` | Test | 5.7, 3.20 | APC-001 + APC-003 boundary patching. |
| `tests/unit/ui/screens/test_workshop_screen.py` | Test | 5.10, 5.10a | APC-001. Verify integration tests at `tests/integration/ui/workshop_screen/` exist (PROJ-322 manifest claims they do; confirm before migrating). |
| `tests/unit/ui/screens/test_race_setup_screen.py` | Test | 5.11, 2.17, 3.21 | RaceSetupScreen — provisional; see Decision D-005. May roll to PROJ-325. |
| `tests/unit/ui/screens/test_new_game_setup_extended.py` | Test | 5.12 | APC-001. |
| `tests/unit/ui/screens/test_sub_window_hotkeys.py` | Test | 5.16 | All 4 target classes (OrdersWindow, BuildQueueScreen, TransferDialog, BuildQueueListWindow) inherit StrategyModalWindow (or are standalone for BuildQueueScreen — verify). |
| `tests/unit/ui/screens/test_build_queue_list_window.py` | Test | 5.29, 3.19 | APC-001 + APC-003 boundary. |
| `tests/unit/strategy/test_strategy_modal_window.py` | Test | 3.24 | UIWindow root-cause file. |

## Documentation files (Phase 4)

| File | Type | Change |
|------|------|--------|
| `docs/02_PATTERNS.md` | Doc | Add Pattern 15b "UI Widget Test Factory" entry per design.md suggested content. |
| `docs/known-issues.md` | Doc | Mark UIWindow + LLMBackgroundCall blockers as **Resolved by PROJ-324** (preserve historical context). |
| `Projects/active_projects/PROJ-322/plan.md` | Doc | Update Continuation Guide: 14 deferrals closed by PROJ-324; remaining queued in PROJ-327. |

## Files explicitly NOT touched

These are owned by sibling continuation projects. **Do NOT edit them in PROJ-324:**

| File | Owner | Why excluded |
|------|-------|--------------|
| `tests/unit/strategy/engine/test_command_handlers.py` | PROJ-325 | PROJ-323 Task 3.34 fleet_not_found parametrize. |
| `tests/regression/test_no_dead_test_files.py` (NEW) | PROJ-326 | Linter for zero-game-import test files. |
| `tests/integration/ui/test_system_tree_panel_smoke.py` (NEW) | PROJ-326 | Replacement coverage for the deleted `test_system_tree_panel.py`. |
| `tests/unit/strategy/facade/test_strategy_session_facade_contract.py` (NEW) | PROJ-326 | Restore facade contract guard. |
| `tests/unit/ui/components/test_virtual_table.py` | PROJ-327 | 700-LOC `@patch` decorator sweep (PROJ-322 Task 3.14). |
| Mutable-mock fixture rescope candidates (PROJ-322 Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15) | PROJ-327 | Phase 2 of PROJ-327. |
| `tests/unit/ui/screens/test_strategy_screen.py` (or wherever the 50-test cluster lives) | PROJ-327 | PROJ-322 Task 3.25 strategy-screen refactor (~multi-day, low ROI). |
