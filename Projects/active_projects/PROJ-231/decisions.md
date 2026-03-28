# PROJ-231: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-28 | Project initialized | Starting point for Star List Panel |
| 2026-03-28 | Mirror planet list architecture exactly (6 files) | Consistent patterns, proven design, easy for agents to follow |
| 2026-03-28 | No star detail panel on right side | Stars don't have the rich detail that planets do (no colonies, production, population). Table gets full width after sidebar. |
| 2026-03-28 | No owner filter | Stars have no owner, unlike planets |
| 2026-03-28 | Spectrum columns hidden by default | 9 extra columns would overwhelm the default view; users can toggle them on via sidebar |
| 2026-03-28 | No spectrum range filters initially | Spectrum filtering adds complexity for minimal user value. Columns exist for display; filters can be added later. |
| 2026-03-28 | Flatten spectrum into StarInfo DTO (9 individual fields) | Frozen dataclasses can't cleanly hold nested mutable objects; flattening keeps serialization trivial |
| 2026-03-28 | Subclass PresetManager for star presets | Separate preset file (`star_ui_presets.json`) avoids collision with planet presets |
| 2026-03-28 | Navigate callback closes window and centers camera | Follows event log navigation pattern; user wants to see the star on the map |
| 2026-03-28 | Add Stars button after Planets in top bar | Logical grouping: Planets and Stars are related celestial object lists |
| 2026-03-28 | Work with domain Star objects in filter/sort (not DTOs) | Planet list already does this — `gather_planets()` works with Planet domain objects directly, attaching cached values. DTOs are for facade queries; list window receives `galaxy` directly. |
| 2026-03-28 | No InputAction/keyboard shortcut initially | Can be added later; keeps scope focused |
