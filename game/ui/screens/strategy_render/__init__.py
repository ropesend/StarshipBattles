"""Strategy-map render layer subpackage (PROJ-309 sub-phase 3.2).

Each module in this package owns one rendering layer of the galaxy map.
There are deliberately no re-exports here — each layer is imported at its
specific path so that new code must declare which layer it belongs in.

The orchestrating ``StrategyRenderer`` class lives at
``game.ui.screens.strategy_renderer`` and composes these layers.
"""
