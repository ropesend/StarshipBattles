# PROJ-352: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Starting point for Closeout follow-up - UI cleanup (T6.6 Strategy load dialog modal tracking + T4.7 NewGameSetup builder docstring) |
| 2026-05-04 | T4.7: KEEP builder, fix docstring only | Confirmed `new_game_setup_ui_builder.NewGameSetupUiBuilder.build()` is a one-line passthrough to `screen._create_ui()`. Per Codex r003 consensus: builder is a Pattern §33 test-substitution seam (Mock/Null variants live at `tests/fixtures/new_game_setup_ui_builder.py`) — keep it; rewrite the misleading "owns the widget tree" docstring to state actual relationship and flag incremental widget extraction as out-of-scope follow-up. |
| 2026-05-04 | T6.6: Shape A — migrate `SaveSelectionWindow` to `StrategyModalWindow` | Uniformity with the rest of the strategy-screen modal plumbing (PROJ-313 OR-bridge). The class already implements two-stage construction with a `bypass_init` shell that mirrors `StrategyModalWindow`'s, and `SaveSelectionWindow`'s only production caller (`strategy_screen_lifecycle.show_load_game_dialog`) has direct access to `screen.ui.window_manager`. Shape B (extra slot in `StrategyWindowManager`) was rejected because adding another bespoke slot during the active phase-out (`docstring at strategy_window_manager.py:142-150`: "slot fields above are being phased out") is moving in the wrong direction. |
