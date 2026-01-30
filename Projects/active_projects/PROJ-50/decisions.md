# PROJ-50: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-30 | Project initialized | Starting point for Strict Dependency Injection Refactor |
| 2026-01-30 | Keep `DefaultRegistryProvider` and `get_default_registry_provider()` | Required for module-level constants (COMPONENT_REGISTRY, MODIFIER_REGISTRY, VEHICLE_CLASSES) used in hot-reload. Removing would break builder UX. |
| 2026-01-30 | Keep `get_default_registries()` for app.py | Composition root needs a way to set/get default registries. Mark as internal-use-only in docs. |
| 2026-01-30 | VehicleClassService: strict DI enforced | Converted to require `registry_provider` parameter. Fallback patterns in legacy UI create provider from composition root. |
| 2026-01-30 | `_get_registries_fallback` removed | Anti-pattern eliminated. All code now uses explicit DI or documented module-level constants. |
