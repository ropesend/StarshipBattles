# PROJ-214: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Project initialized | Starting point for Hex Highlights for Objects and Ownership |
| 2026-02-28 | Zoom threshold: >= 0.5 | User specified "when planets become visible" - planets render at zoom >= 0.5 |
| 2026-02-28 | Dual concentric outlines for mixed hexes | User chose split/dual over player-wins or enemy-wins for mixed ownership |
| 2026-02-28 | All object types get outlines | User chose all objects (stars, storms, warp points, planets, fleets) not just strategic ones |
| 2026-02-28 | Render order: after grid, before warp lanes | Outlines act as "floor highlights" behind all objects |
| 2026-02-28 | Turn-based cache invalidation | Galaxy data + fleet positions only change during turn processing |
| 2026-02-28 | Scale factors: 0.88 single, 0.90/0.80 dual | Provides visible gap between hex edge and outline, dual is visually distinct |
| 2026-02-28 | Muted red (200,60,60) and off-white (220,220,220) | Avoids visual clash with other bright indicators |
| 2026-02-28 | Reuse Galaxy spatial indexes | No new data structures needed - O(1) lookups via _global_hex_planets, _global_hex_zones, _global_hex_warp_points |
