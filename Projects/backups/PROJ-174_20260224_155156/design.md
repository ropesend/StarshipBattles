# PROJ-174: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Source:** Focused Question Review `2026-02-23_185804_focused_registry-consolidation-migration`
**Parent Review:** Deliberate Design Debt Audit `2026-02-23_160923_general_deliberate-design-debt-audit`

The codebase has three registry access patterns that evolved over PROJ-27/38/50/58:
- **TIER 3** (Direct Singleton): `RegistryManager.instance().components` — 4 production files, 14 call sites
- **TIER 2** (Service Locator): `get_default_registries().components` — 11 production files, 15 call sites
- **TIER 1** (DI Provider): `get_default_registry_provider().get_components()` — 7 production files, 13 call sites

The codebase is ~70% migrated. This project completes the remaining 30%.

## Swarm Findings Summary
Combined analysis from 6 investigation agents (CSM, DCA, TIA, TAD, BCA, RCC).

### Architecture
- **IRegistryProvider** protocol (`game/core/protocols.py:46`) is the target abstraction
- **DefaultRegistryProvider** delegates to RegistryManager singleton (production)
- **TestRegistryProvider** provides isolated test data
- **RegistryManager** is the internal storage engine — freeze/clear/hydrate lifecycle
- **GameRegistries** is a frozen dataclass bridge — kept for backward compatibility
- **Composition roots:** `game/app.py` (production), `conftest.py` (tests) — legitimately access RegistryManager

### Key Patterns to Reuse
- **Constructor fallback pattern**: `game/strategy/engine/turn_engine.py:101` — accept optional registries param, fall back to global
- **Service lazy resolution**: `game/ui/services/component_service.py:46-50` — `_get_provider()` resolves once and caches
- **TestRegistryProvider isolation**: `tests/unit/core/test_registry_provider.py` — create isolated provider per test

### Dependencies & Risks
1. **WorkshopContext.__post_init__()** (`game/ui/screens/workshop_context.py:66-74`) — accesses registries at instantiation time. Already has try/except safety net. Convert to use provider instead of service locator.
2. **FleetCapabilityCalculator static utility** (`game/strategy/data/fleet_capability_calculator.py:14-17`) — private function wraps service locator. Simple swap to provider.
3. **ship_loader.py validator storage** (`game/simulation/entities/ship_loader.py:22-25`) — validator is stored ON RegistryManager. May need to keep singleton access for validator get/set specifically.
4. **18 test files mock/patch** registry globals — each needs updating to DI patterns after production code migrates.
5. **xdist parallelization** — each worker has isolated singletons. No special handling needed.

### Opportunities Discovered
- **MOD-CORE-006/007** (incomplete protocol) can be fixed as natural Phase 1 step
- **Performance impact is negligible** — ~30-100ns per access overhead, 0.06% of frame budget at 100 accesses/frame

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

### Target Architecture

```
                    IRegistryProvider (Protocol)
                   /                            \
    DefaultRegistryProvider              TestRegistryProvider
    (wraps RegistryManager)              (isolated test data)
           |
    RegistryManager (INTERNAL)
    - freeze() / clear() / hydrate()
    - Lifecycle only, not in __all__
```

### End-State registry.py Public API

```python
__all__ = [
    'DefaultRegistryProvider', 'TestRegistryProvider',
    'get_default_registry_provider',
    'freeze_registry', 'clear_registry', 'set_validator',
    'GameRegistries', 'set_default_registries',  # deprecated bridge
]
```

### Consumer Pattern (Post-Migration)

```python
# Best: Constructor DI
class MyService:
    def __init__(self, registry: IRegistryProvider):
        self._registry = registry

# Acceptable: Lazy resolution
def some_function():
    provider = get_default_registry_provider()
    components = provider.get_components()
```
