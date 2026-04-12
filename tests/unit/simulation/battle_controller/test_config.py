"""BattleController mode-handler tests — DELETED in PROJ-269 Phase 6.

This file previously tested:
  - `BattleMode` enum values
  - `BattleConfig.mode` field defaults
  - `BattleController.configure()` selecting a mode handler
  - Mode-handler retreat/reinforcement defaults

All of that machinery was deleted in Phase 6 — variance moved to
`BattleSpec` + `run_battle`, and the residual `BattleController` is a
plain visual-mode driver with no mode dispatch. The empty stub is
retained so test discovery / git history references resolve.
"""
