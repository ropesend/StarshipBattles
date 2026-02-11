# PROJ-85: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Three module-level globals are defined at import time in the simulation layer:

```python
# component.py:81-82
COMPONENT_REGISTRY = get_default_registry_provider().get_components()
MODIFIER_REGISTRY = get_default_registry_provider().get_modifiers()

# ship.py:27
VEHICLE_CLASSES = get_default_registry_provider().get_vehicle_classes()
```

These call `get_default_registry_provider()` at import time, which:
1. Creates a `DefaultRegistryProvider` singleton (if not already created)
2. Returns mutable dict references to `RegistryManager.instance()` dicts
3. Captures state at the moment the module is first imported

### Why They Existed
PROJ-42 kept these for "UI hot-reload compatibility" — the builder's `_reload_data()` method relied on in-place dict mutation being visible through these module-level references.

### Why They're Now Dead Code
- **PROJ-43** migrated all UI code to `VehicleClassService` and `ComponentService`
- **PROJ-44** refactored `_reload_data()` to use `WorkshopDataLoader`
- **PROJ-50** established strict constructor-based DI throughout

**Grep confirms zero importers** across `game/`, `tests/`, and `simulation_tests/`. The only references in active code are the definitions themselves and historical comments in builder files documenting the PROJ-43 migration.

## Swarm Findings Summary

### Architecture
- The DI system has three tiers: Constructor DI (preferred), Service Locator (`get_default_registries()`), and Direct Singleton (`RegistryManager.instance()`)
- All modern code uses constructor DI or service locator — nobody uses these module-level globals
- The `ComponentCacheManager` singleton is unrelated to these globals despite existing in the same file — it serves the `load_components()`/`load_modifiers()` caching pattern

### Key Patterns to Reuse
- No new patterns needed — this is pure deletion

### Dependencies & Risks
1. **Risk: Dynamic attribute access** — If any code uses `getattr(module, 'COMPONENT_REGISTRY')`, it would break. Grep found no such usage. **Risk: Negligible.**
2. **Risk: Import side effects** — Removing the globals eliminates three `get_default_registry_provider()` calls at import time. This is a positive change — the provider is still created when actually needed by `load_components_data()`, `load_components()`, `load_modifiers()`, and UI services.

### Opportunities Discovered
- The `if TYPE_CHECKING: pass` block in `ship.py:14-15` is dead code from when `GameRegistries` was only imported for type checking. Since `GameRegistries` is now imported directly (line 11), this block does nothing.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
