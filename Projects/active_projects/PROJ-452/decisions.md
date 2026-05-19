# PROJ-452: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-18 | Project initialized | Starting point for Catalog-driven resource surfaces (DI-003/004/005 + LABEL_ABBREV) |
| 2026-05-18 | F-C-015 closed in PROJ-452 Phase 3 alongside DI-004 (same two `LABEL_ABBREV` dicts at `stat_rows_dynamic.py:178-181` and `:251-254`, labels-side framing) | Single PR retires the abbreviation map across `get_construction_rows` and `get_strategic_rows`; both call sites route through `_label_for(resource_id)` → `ResourceCatalog.from_json().get(rid).name`. Closure scope is appropriate because DI-004 (IDs side) and F-C-015 (labels side) describe the same two duplicated dicts through different lenses, and the IDs side was already catalog-driven at `:177` before this project. |
| 2026-05-18 | Adopt catalog `ResourceDefinition.name` (`Radioactives`) over the legacy abbreviation (`Radact`) | F-C-015's directive: catalog is the canonical source of truth for display labels. The 4 other planetary resources (`metals`, `organics`, `vapors`, `exotics`) coincidentally match between the legacy abbreviation map and the catalog `name`. The single user-visible change is `radioactives` row label going from `Radact` → `Radioactives`. No existing tests or production code reference the literal `"Radact"`. |
