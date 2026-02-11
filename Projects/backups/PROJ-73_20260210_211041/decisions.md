# PROJ-73: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Rotating Warp Point Graphics |
| 2026-02-07 | Rotation speed: 12 degrees/second | Slow enough to be ambient (30 sec full rotation), fast enough to be noticeable. Earth rotation too slow (0.004 deg/sec), loading spinners too fast (180+ deg/sec). |
| 2026-02-07 | Unique offset via `hash(wp) % 360` | Already using `hash(wp)` for image selection. Reusing for rotation offset ensures each warp point starts at different angle. Stable across frames/sessions. |
| 2026-02-07 | Track elapsed time in StrategyRenderer | Keeps animation state local to renderer where it's used. Alternative (pygame.time.get_ticks) introduces global dependency. |
| 2026-02-07 | Use existing `scale_and_rotate_image()` | Utility already exists in `game/ui/utils.py`. Handles scale-then-rotate in correct order. No need to reinvent. |
| 2026-02-07 | Scale before rotate | Scaling changes pixel dimensions (should happen first). Rotation expands bounding box to fit corners. This is the standard order. |
| 2026-02-07 | No data model changes | Rotation is purely visual. WarpPoint class unchanged. No save/load impact. |
