# PROJ-485 File Manifest

> Generated during /claude-proj-from-legacy-audit. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/ai/carrier_controller.py` | Production | Delete | Delete `_find_tactical_launch_ability` (lines 358-390, ~30 LOC), `_pop_fighter_cvs` (lines 255-263, ~8 LOC), `_pop_cvs` (lines 265-300, ~45 LOC). ~83 LOC total. |
| `tests/unit/ai/...` | Test | Migrate-callers | TBD by grep during implementation — migrate any test references to `_sum_launch_rate` / `_pop_cvs_within_budget` |
