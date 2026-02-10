# PROJ-94: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Resource API Cleanup and Protocol Wiring |
| 2026-02-10 | PROJ-94 before PROJ-95 | Deletes dead code first so PROJ-95 doesn't waste time adding constants to methods about to be deleted |
| 2026-02-10 | Add get_all_resources() to ResourceRegistry | ship_stats_renderer needs ResourceState objects (for .name, .current_value, .max_value), not just names |
| 2026-02-10 | Extract _capture_resource_levels() as static method | Duplicate code in from_ship() and update_from_ship() -- DRY it up |
| 2026-02-10 | Remove getattr for is_derelict | IPostBattleShip declares is_derelict as required property -- getattr is unnecessary defensive code |
| 2026-02-10 | Do NOT delete ResourceState.has_sufficient() | Dead Code Hunter false positive -- it IS used at resources.py:106 |
