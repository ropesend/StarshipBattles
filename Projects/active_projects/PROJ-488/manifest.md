# PROJ-488 File Manifest

> Generated during /claude-proj-from-legacy-audit. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/data/planet_physics.py` | Production | Delete | Delete `MASS_EARTH = EARTH_MASS` alias at line 25 and the `# Backward-compatible alias` comment |
| (~67 references across 12 files; enumerate during Phase 1 Task 1.1) | Production / Test / Tool | Migrate-callers | Replace `MASS_EARTH` with `EARTH_MASS` from canonical module. Production `game/` callers: `planet_atmosphere.py`, `planet_gen_surface.py`, `ui/screens/galaxy_test/system_mode.py` |
| `tests/static_guards/test_facade_read_path_imports_guard.py` | Test (static-guard fixture) | Edit | Line 208 enshrines `MASS_EARTH` as the canonical import for `system_mode.py` — update to `EARTH_MASS`. Added 2026-05-22 post-merge audit. |
