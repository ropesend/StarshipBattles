# PROJ-488 File Manifest

> Generated during /claude-proj-from-legacy-audit. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/data/planet_physics.py` | Production | Delete | Delete `MASS_EARTH = EARTH_MASS` alias at line 25 and the `# Backward-compatible alias` comment |
| (~25 caller files; enumerate during Phase 1 Task 1.1) | Production / Test / Tool | Migrate-callers | Replace `MASS_EARTH` with `EARTH_MASS` from canonical module |
