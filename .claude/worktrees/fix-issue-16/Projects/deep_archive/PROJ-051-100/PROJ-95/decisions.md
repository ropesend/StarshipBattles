# PROJ-95: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Resource API Consistency and Clean-Sheet Conventions |
| 2026-02-10 | Accept dual resource systems as-is (Finding #1) | ShipInstance exists in strategy layer without simulation Ship; cannot delegate to ResourceRegistry. Architecturally justified. |
| 2026-02-10 | Full rename is_destroyed to is_alive (not convenience property) | Clean-sheet approach per CLAUDE.md. Eliminates double-negation bugs. Save files are disposable. |
| 2026-02-10 | Eliminate None-means-full convention | Clean-sheet: always store actual values. Aligns with simulation layer. Removes ambiguity and simplifies getters. |
| 2026-02-10 | One project, 4 phases | Three changes are low-coupling cleanups. Constants first (pure addition), then rename (semantic), then convention change (behavioral). |
| 2026-02-10 | ResourceType as class with string constants, not Enum | Values used extensively as dict keys. Enum would require .value everywhere. Class constants are simpler. |
| 2026-02-10 | Use new serialization key 'is_alive' (break old saves) | Per CLAUDE.md: save files are disposable. No backward compatibility shims. |
| 2026-02-10 | PROJ-94 should complete before PROJ-95 | Removes dead code that would otherwise need updating here |
