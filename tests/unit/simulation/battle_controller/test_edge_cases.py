"""BattleController edge-case tests — substantially DELETED in PROJ-269 Phase 6.

This file previously tested:
  - `apply_results_to_fleets` (deleted with the strategy adapter rewrite)
  - `mode_handler` property + per-mode handler swap on reconfigure
  - Mode-handler-driven retreat / reinforcement defaults
  - `BattleMode` enum-based config validation

Phase 6 deleted `BattleMode`, `BattleModeHandler`, and the `mode_handler`
property. The retreat / reinforcement defaults are now config-flag driven
only — covered by `test_retreat_priority.py` (also slimmed). The empty
stub is retained so test discovery / git history references resolve.
"""
