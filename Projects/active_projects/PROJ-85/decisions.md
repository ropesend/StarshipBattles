# PROJ-85: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Project initialized | Starting point for Eradicate Module-Level Mutable Global State |
| 2026-02-09 | Single phase — pure deletion | All three globals are dead code with zero importers. No migration needed, no consumer updates. |
| 2026-02-09 | Keep `get_default_registry_provider()` import in `component.py` | Still used by `load_components_data()` (line 544), `load_components()` (line 600), `load_modifiers()` (line 693) |
| 2026-02-09 | Remove `get_default_registry_provider` import from `ship.py` | Only usage was the deleted `VEHICLE_CLASSES` global; no other callers in this file |
| 2026-02-09 | Remove dead `if TYPE_CHECKING: pass` block in `ship.py` | `GameRegistries` is imported directly on line 11; the TYPE_CHECKING guard is vestigial |
| 2026-02-09 | Do NOT touch `ComponentCacheManager` or `reset_component_caches()` | Still actively used by conftest and load functions; unrelated to the globals despite proximity |
| 2026-02-09 | Do NOT modify documentation/archive files | Historical records accurately describe what existed when they were written |
