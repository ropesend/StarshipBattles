# PROJ-86: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Project initialized | Starting point for Critical God Class Decomposition - UI Tier |
| 2026-02-09 | Extract in order of least coupling: data first, executor last | Data extraction has zero UI dependencies and can be tested independently. Validation depends on data extraction. Panel creation depends on data. Test executor depends on all three plus has render callbacks. This ordering minimizes merge conflicts between phases. |
| 2026-02-09 | TestLabScreen extractions go into existing `game/ui/screens/test_lab/` subdirectory | The package structure already exists with `dialogs.py`, `ship_panels.py`, etc. Adding `data_extractor.py`, `validation_manager.py`, `panel_manager.py`, `test_executor.py` follows the established pattern. |
| 2026-02-09 | StrategyUI extractions go alongside in `game/ui/screens/` | StrategyUI is not in a package -- it is a single file `strategy_ui.py` alongside `strategy_detail_fmt.py`, `strategy_renderer.py`, etc. New extractions (`strategy_detail_formatter.py`, `strategy_window_manager.py`, `strategy_panel_manager.py`, `strategy_event_router.py`) follow this flat naming convention. |
| 2026-02-09 | Facade pattern: original classes remain the public API | No call sites outside the three target files should change. `TestLabScreen`, `StrategyUI`, and `BuildQueueScreen` keep all their public methods. Internally, they delegate to extracted helpers. This ensures zero blast radius. |
| 2026-02-09 | Phase 4 TestExecutor needs render callback for progress overlay | `_on_run_headless` and `_run_next_batch_test` draw progress overlays via `self.game.screen`, `self.header_font`, `self.body_font`, and `self.small_font`. Rather than passing all of these, pass a single `render_progress(title, subtitle, detail)` callback that the screen implements. The executor calls this callback; the screen handles the actual rendering. |
| 2026-02-09 | Phase 5: Move `show_detailed_report` near existing `strategy_detail_fmt.py` functions | `show_detailed_report` is the primary consumer of the formatting functions in `strategy_detail_fmt.py`. Moving it into a new `strategy_detail_formatter.py` class (which imports from `strategy_detail_fmt.py`) keeps related code together. We do NOT merge into `strategy_detail_fmt.py` itself because `show_detailed_report` needs pygame_gui widget references. |
| 2026-02-09 | Phase 8 starts with analysis before defining extractions | BuildQueueScreen grew from 603 to 1185 lines through multiple feature additions. The exact decomposition cannot be predetermined without analyzing what was added. Phase 8 begins with a method-by-method analysis task before defining extraction targets. |
