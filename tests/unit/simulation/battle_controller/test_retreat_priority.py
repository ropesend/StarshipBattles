"""Retreat-priority tests — DELETED in PROJ-269 Phase 6.

This file tested the OR-based priority between `BattleModeHandler` and
`BattleConfig.allow_retreat` / `allow_reinforcements`. Phase 6 deleted
the mode-handler dispatch entirely; both flags are now read from the
config directly (see `BattleController._retreat_allowed()` and
`BattleController._reinforcements_allowed()`). The remaining behavior
is trivial — covered by `test_mechanics.py` integration tests.

This empty stub is retained so test discovery / git history references
resolve.
"""
