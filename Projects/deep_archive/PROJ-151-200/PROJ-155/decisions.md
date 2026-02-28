# PROJ-155: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-16 | Project created from validated review findings | 4 validation reviews confirmed 47 safe removals, disputed 30 items, modified 32 items |
| 2026-02-16 | Only implement CONFIRMED and MODIFIED findings | DISPUTED findings were proven to have real value by validators — do not remove |
| 2026-02-16 | Merge-before-delete for all MODIFIED findings | ~20 unique tests must be preserved in target files before source deletion |
| 2026-02-16 | File-by-file deletion for old directories, not wholesale | Validation review 4 warned old files may use real objects vs new files' MagicMock — verify each pair |
| 2026-02-16 | Include Phase 3 (old directory trees) in this project | User chose full cleanup over deferral |
| 2026-02-16 | Keep Tasks 2.12/2.13 as conditional | Spatial extended + collision system merges not yet verified to exist, execute if present |
| 2026-02-16 | Do NOT delete builder/systems/ai conftest.py files | These have fixture imports; validation claims they're unused but needs verification |
| 2026-02-16 | Do NOT delete reproduce_scaling.py | Validated as legitimate pytest test with real assertions despite misleading name |
| 2026-02-16 | Do NOT delete any repro_*.py files at root | Validators proved claimed replacements test DIFFERENT functionality |
| 2026-02-16 | Phase ordering: delete > merge > old dirs > partial > structural | Safest items first, highest-risk (old dirs) after simpler cleanups established pattern |
| 2026-02-16 | Baseline: 12,790 passed, 143 pre-existing failures | Pre-existing failures unrelated to this project; track to ensure no increase |
| 2026-02-19 | PROJ-157 completed bulk of PROJ-155 scope | PROJ-157 (Test Suite Cleanup v4) was created independently and completed most overlapping work. Updated all checklists to reflect actual state. |
| 2026-02-19 | DROP Tasks 2.4, 2.5: logger merge targets don't exist | PROJ-157 verified `test_logger.py` never existed. `test_events.py` and `test_singleton.py` ARE the canonical files. |
| 2026-02-19 | DROP Tasks 2.9, 2.10, 2.11: AI merge targets don't exist | PROJ-157 verified target files don't exist. Source files (`test_evaluation_rules.py`, `test_evaluation_integration.py`, `test_adapter_basics.py`, `test_adapter_methods.py`) ARE canonical. |
| 2026-02-19 | DROP Task 4.11: TestLayoutConstants classes are legitimate | Found in `test_initialization.py` and `test_empire_treasury_panel.py` — these test actual layout constant values (sidebar width, column spacing), not trivial `assert X > 0` checks. |
| 2026-02-19 | Updated baseline: 12,185 tests collected | Post-PROJ-157 baseline. Delta of -605 tests from original PROJ-155 baseline reflects PROJ-157 cleanup. |
| 2026-02-19 | PROJ-157 deleted builder/systems/ai conftest.py files | PROJ-155 had deferred these (decision 2026-02-16), but PROJ-157 verified fixtures were unused and deleted them. |
| 2026-02-20 | PROJ-154 completed remaining Phase 1 deletions | Deleted mock_battle_ui_service.py, cleaned __init__.py, deleted conflict_core.py, build_queue_source_errors.py, fleet_resource_aggregator.py |
| 2026-02-20 | PROJ-154 completed remaining Phase 2 merges | Merged 16 tests from test_engines_contracts.py → test_engine_interfaces.py; merged test_passes_registries from data/test_fleet_battle_adapter.py → root version |
| 2026-02-20 | PROJ-154 completed remaining Phase 4 partial cleanups | Removed TestGameSwitchScene from test_scene_protocol.py, TestStrategyDetailFormatterWidgetAccessors + TestResizeSupport from test_strategy_detail_formatter.py, 3 duplicates from test_battle_screen_extended.py, test_legacy_cleanup from test_production_refactor.py |
| 2026-02-20 | PROJ-154 completed Phase 5 Task 5.1 | Relocated test_fleet_report_filters.py from strategy/ to ui/screens/ via git mv |
| 2026-02-20 | Phases 2 and 4 now fully complete | All tasks done, dropped, or N/A across both phases |
