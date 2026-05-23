# PROJ-486 File Manifest

> Generated during /claude-proj-from-legacy-audit. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/simulation/battle_controller.py` | Production | Delete | Delete `BattleController.load_state` lines 509-595 (~87 LOC) — refreshed post-merge `67116932d` |
| `tests/unit/simulation/battle_controller/test_state.py` | Test | Migrate-callers | Reconcile 4 test callers at lines 90, 128, 245, 268 — delete or migrate to `save_state`-only assertions |
