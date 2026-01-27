# PROJ-37: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Project initialized | Starting point for Fragile Asset Loading Refactor |
| 2026-01-27 | Star colors stored in asset_manifest.json | Centralized config, easier to tune without code changes, follows existing manifest pattern |
| 2026-01-27 | Extend RaceAssetLoader (not create new class) | Reuse existing flag loading logic with resolution hierarchy (1024 > 512 > 256 > root) |
| 2026-01-27 | Add get_star_color_key() to AssetManager | Keeps color lookup logic with manifest data where it belongs |
| 2026-01-27 | Add tests BEFORE refactoring (Phase 1) | Zero test coverage for star color logic - need safety net before changes |
| 2026-01-27 | Preserve empire_assets dict structure | StrategyRenderer depends on exact keys: 'colony', 'fleet', 'fleet_flag' |
