# PROJ-217: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Project initialized | Starting point for Standardize Star Measurement to Radius |
| 2026-02-28 | Full rename to `radius_hexes` (not just fix rendering) | User preference: radius is more natural for hex grids. Integer radii map cleanly to ring counts. |
| 2026-02-28 | Integer type (`int`) not float | Hex radii are always whole ring counts. Eliminates the need for `ceil()` everywhere. |
| 2026-02-28 | 1-indexed radius: `radius_hexes=1` = center hex only (1 hex) | Most intuitive: "radius of 1" means just the center hex. Minimum value for any star. |
| 2026-02-28 | Formula: `hex_circle_filled(location, radius_hexes - 1)` | With 1-indexing, we subtract 1 to get the distance parameter for hex_circle_filled. |
| 2026-02-28 | Compact remnants (neutron stars, black holes, white dwarfs) get `radius_hexes=1` | They're sub-hex objects. Occupying just 1 hex is physically accurate. |
| 2026-02-28 | Fix all inconsistencies (companion placement, orbit safe_start, warp distance) | User chose broader scope. The old formulas were inconsistent with each other. |
| 2026-02-28 | No save file migration | Per CLAUDE.md: old saves are disposable. No backward compat shims. |
| 2026-02-28 | Dyson Spheres: `radius_hexes=6` (91 hexes) | Old: `diameter_hexes=11.0` → ceil(11/2)=6 → 127 hexes. New: `radius_hexes=6` → fill(loc,5) → 91 hexes. Slightly smaller zone but cleaner value. |
| 2026-02-28 | Generation formula: `_map_solar_radius_to_hex_radius()` returns int 1-6 | Replaces old `_map_radius_to_hexes()` that returned float 0.5-11.0. Halved coefficient in log formula. |
| 2026-02-28 | Companion min distance: `radius + 2` | Old: `int(diameter * 2) + 2` was semantically wrong. New formula is clear: stay at least 2 hexes outside the star's zone. |
| 2026-02-28 | Warp distance: `base + radius * 3.0` | Old: `15 + diameter * 1.5`. With radius ≈ diameter/2, equivalent is `15 + radius * 3.0`. |
