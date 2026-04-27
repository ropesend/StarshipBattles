"""Strategy window registrar subpackage (PROJ-309 sub-phase 3.10).

Each module owns the lifecycle of one window family on the strategy screen.
The orchestrating ``StrategyWindowManager`` lives at
``game.ui.screens.strategy_window_manager`` and composes these registrars.

There are deliberately no re-exports here — each registrar is imported at its
specific path so that new code must declare which family it belongs to.
"""
