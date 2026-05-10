# Focused Question Review: Registry Consolidation Migration Plan

**Date:** 2026-02-23
**Type:** Focused Question Review
**Question:** What is the complete migration plan to consolidate all registry access onto a single canonical pattern (IRegistryProvider DI), and what would break?
**Agents Used:** CSM (Call Site Mapper), DCA (Dependency Chain Analyzer), TIA (Test Infrastructure Analyst), TAD (Target Architecture Designer), BCA (Breaking Change Analyzer), RCC (Related Cleanup Cataloguer)
**Source Review:** `2026-02-23_160923_general_deliberate-design-debt-audit/`

---

## Direct Answer

**The migration is achievable in 5 phases over ~7-10 hours of focused work.** The codebase is already ~70% migrated — TIER 3 (direct singleton) has only 4 production files, TIER 2 (service locator) has 11 production files, and TIER 1 (DI provider) already covers 7 production files. The biggest effort is in tests (163+ files reference RegistryManager.instance()), but most of those are legitimate infrastructure (conftest fixtures) that should keep singleton access as composition root.

**What would break:** 18 test files use mock/patch on registry patterns. 29 call sites use `get_default_registries()`. 14 call sites use `RegistryManager.instance()` directly. The deepest signature cascade is 4-5 levels (Fleet properties -> strategy calculators -> component inspectors). One import-time risk exists in WorkshopContext.__post_init__().

**Confidence: HIGH** — All agents converge on the same assessment. The migration is well-scoped, low-risk per phase, and follows established patterns already in the codebase.

---

## Executive Summary

### Call Site Inventory

| Pattern | Production Files | Production Call Sites | Test Files | Test Call Sites |
|---------|-----------------|----------------------|------------|-----------------|
| **TIER 3** (RegistryManager.instance()) | 4 | 14 | 45+ | 166+ |
| **TIER 2** (get_default_registries()) | 11 | 15 | 5+ | 12+ |
| **TIER 1** (get_default_registry_provider()) | 7 | 13 | 4 | 9 |
| **Lifecycle** (set/clear/freeze/hydrate) | 3 | 6 | 15+ | 60+ |

### Production TIER 3 Files (Direct Singleton — Must Migrate or Justify)

| File | Call Sites | Purpose | Migration Difficulty |
|------|-----------|---------|---------------------|
| game/app.py | 2 | Composition root startup | **Keep** (legitimate) |
| game/core/registry.py | 8 | Internal + lifecycle helpers | **Keep** internal, migrate helpers |
| game/simulation/entities/ship_loader.py | 3 | Validator + vehicle class loading | Medium |
| game/simulation/services/registry_loader.py | 1 | Registry reload utility | **Keep** (already receives mgr param) |

### Production TIER 2 Files (Service Locator — Must Migrate to TIER 1)

| File | Sites | Current Pattern | Migration |
|------|-------|----------------|-----------|
| game/strategy/data/fleet_capability_calculator.py | 1 | Private utility fn | Easy |
| game/strategy/engine/turn_engine.py | 2 | Constructor fallback | Easy (already has DI param) |
| game/strategy/engine/empire_economy_calculator.py | 1 | Constructor injection | Easy (already has DI param) |
| game/strategy/data/ship_instance.py | 1 | Late init | Medium |
| game/ui/services/ship_factory.py | 2 | Resolution method | Easy |
| game/ui/services/design_loader_adapter.py | 1 | Lazy resolution | Easy |
| game/ui/panels/planet_report_panel.py | 1 | Inline access | Medium |
| game/ui/screens/empire_panel_window.py | 1 | Method call | Medium |
| game/ui/screens/workshop_context.py | 1 | __post_init__ fallback | Medium (import-time risk) |
| game/simulation/entities/ship_stats.py | 1 | Docstring example only | Trivial |

---

## Target Architecture

### Design Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Keep RegistryManager? | **YES — internal only** | Lifecycle management (freeze/clear/hydrate) is valuable. Make private implementation detail, remove from __all__. |
| Keep GameRegistries? | **YES — deprecate gradually** | Some code passes it as parameter. Phase out over time, not in this project. |
| Keep get_default_registries()? | **NO — eliminate** | Service locator pattern replaced by get_default_registry_provider(). Remove all 11 production call sites. |
| Merge DefaultRegistryProvider into RegistryManager? | **NO — keep separate** | Clean separation: lifecycle (RegistryManager) vs. access (DefaultRegistryProvider). |
| How to add resources? | **Add get_resources() to IRegistryProvider** | Complete the protocol. Add to DefaultRegistryProvider and TestRegistryProvider. |

### End-State Public API (registry.py)

```python
__all__ = [
    # DI Providers (PRIMARY API)
    'DefaultRegistryProvider',
    'TestRegistryProvider',
    'get_default_registry_provider',
    # Lifecycle helpers (composition roots only)
    'freeze_registry',
    'clear_registry',
    'set_validator',
    # Bridge (deprecated, phase out separately)
    'GameRegistries',
    'set_default_registries',  # kept for conftest compatibility
]
# RegistryManager NOT exported — internal only
```

### End-State IRegistryProvider Protocol

```python
@runtime_checkable
class IRegistryProvider(Protocol):
    def get_components(self) -> Dict[str, Any]: ...
    def get_modifiers(self) -> Dict[str, Any]: ...
    def get_vehicle_classes(self) -> Dict[str, Any]: ...
    def get_resources(self) -> Dict[str, Any]: ...    # NEW
```

---

## Phased Migration Plan

### Phase 1: Complete IRegistryProvider Protocol
**Goal:** Fix incomplete protocol, add resources support
**Risk:** LOW | **Effort:** ~30 min

**Changes:**

| File | Change |
|------|--------|
| game/core/protocols.py | Add `get_resources() -> Dict[str, Any]` to IRegistryProvider |
| game/core/registry.py | Add `get_resources()` to DefaultRegistryProvider |
| game/core/registry.py | Add `resources` param to TestRegistryProvider.__init__() |
| game/core/registry.py | Add `get_resources()` to TestRegistryProvider |
| tests/unit/core/test_registry_provider.py | Add tests for get_resources() |

**Verification:** `pytest tests/unit/core/test_registry_provider.py tests/unit/core/test_protocols_boundary.py -v` then `pytest tests/ -n 12`

**Definition of Done:**
- [ ] IRegistryProvider has get_resources() method
- [ ] DefaultRegistryProvider.get_resources() delegates to RegistryManager
- [ ] TestRegistryProvider accepts resources parameter, has get_resources()
- [ ] All 7353+ tests pass

---

### Phase 2: Make RegistryManager Internal
**Goal:** Remove RegistryManager from public API
**Risk:** LOW | **Effort:** ~1 hour

**Changes:**

| File | Change |
|------|--------|
| game/core/registry.py | Remove RegistryManager from __all__ |
| game/core/registry.py | Update module docstring — single TIER 1 pattern only |

**Note:** Keep RegistryManager in same file (no separate _registry_impl.py needed). Just remove from __all__. Composition roots (app.py, conftest.py) import it directly by name — this still works even when not in __all__.

**Legitimate RegistryManager users (keep access):**
- game/app.py — composition root
- conftest.py / simulation_tests/conftest.py — test composition root
- game/simulation/services/registry_loader.py — receives mgr as parameter
- game/core/registry.py — internal implementation

**Verification:** `pytest tests/ -n 12`

**Definition of Done:**
- [ ] RegistryManager not in __all__
- [ ] Module docstring shows only TIER 1 pattern
- [ ] All tests pass

---

### Phase 3: Migrate TIER 2 Production Code to TIER 1
**Goal:** Replace all `get_default_registries()` calls in game/ with provider pattern
**Risk:** MEDIUM | **Effort:** ~2-3 hours

**Migration per file:**

| File | Current | Target | Notes |
|------|---------|--------|-------|
| fleet_capability_calculator.py | `get_default_registries().components` | Accept `registry: IRegistryProvider` or use `get_default_registry_provider()` | Easy — utility fn |
| turn_engine.py | `get_default_registries()` fallback | `get_default_registry_provider()` fallback | Easy — already DI |
| empire_economy_calculator.py | Already DI, uses registries param | May need provider pattern for the static factory | Easy |
| ship_instance.py | `get_default_registries()` late init | `get_default_registry_provider()` | Easy |
| ship_factory.py | `get_default_registries()` in resolver | `get_default_registry_provider()` | Easy |
| design_loader_adapter.py | `get_default_registries()` lazy | `get_default_registry_provider()` | Easy |
| planet_report_panel.py | `get_default_registries()` inline | Add provider param or use `get_default_registry_provider()` | Medium |
| empire_panel_window.py | `get_default_registries()` in method | Use provider | Medium |
| workshop_context.py | `get_default_registries()` in __post_init__ | Lazy property with provider | Medium — import-time risk |
| ship_stats.py | Docstring example only | Update docstring | Trivial |

**Key Pattern:**
```python
# BEFORE (TIER 2):
registries = get_default_registries()
components = registries.components

# AFTER (TIER 1 — lazy resolution):
provider = get_default_registry_provider()
components = provider.get_components()

# BEST (constructor DI):
class MyService:
    def __init__(self, registry: IRegistryProvider = None):
        self._registry = registry or get_default_registry_provider()
```

**Verification:** `pytest tests/ -n 12` + grep confirms zero production callers of get_default_registries()

**Definition of Done:**
- [ ] Zero calls to get_default_registries() in game/ (except registry.py definition)
- [ ] All migrated files use get_default_registry_provider() or constructor DI
- [ ] All tests pass

---

### Phase 4: Migrate TIER 3 Non-Composition-Root Code
**Goal:** Remove direct RegistryManager.instance() calls from non-composition-root code
**Risk:** MEDIUM | **Effort:** ~1-2 hours

**Changes:**

| File | Current | Target |
|------|---------|--------|
| game/simulation/entities/ship_loader.py:22 | `RegistryManager.instance().get_validator()` | Accept validator param or use provider |
| game/simulation/entities/ship_loader.py:25 | `mgr = RegistryManager.instance()` | Accept registry param |
| game/simulation/entities/ship_loader.py:124 | `RegistryManager.instance().vehicle_classes` | Accept registry param |

**Note:** registry_loader.py already receives registry_manager as parameter — no change needed.

**Verification:** `pytest tests/unit/simulation/ -v` then `pytest tests/ -n 12`

**Definition of Done:**
- [ ] Only app.py, conftest.py, and registry.py reference RegistryManager.instance()
- [ ] ship_loader.py uses DI or provider
- [ ] All tests pass

---

### Phase 5: Update Test Mocks and Deprecate Old API
**Goal:** Update test patches, mark deprecated functions, clean up
**Risk:** MEDIUM | **Effort:** ~2-3 hours

**Test files requiring mock/patch updates:**

| File | Current Pattern | New Pattern |
|------|----------------|-------------|
| test_builder_data_loader.py | `patch.object(RM.instance(), 'clear')` | Fixture-based setup |
| test_builder_warning_logic.py (2x) | `patch.object(RM.instance(), 'vehicle_classes')` | TestRegistryProvider |
| test_ship_loader.py (10x) | `patch('...ship_loader.RegistryManager')` | Inject mock provider |
| test_workshop_data_loader.py | `patch.object(RM.instance(), 'clear')` | Fixture-based setup |
| test_compute_planet_production.py | `patch('...get_default_registries')` | Pass registries param |
| test_planet_production_display.py (2x) | `patch('...get_default_registries')` | Pass registries param |
| test_strategy_detail_formatter.py (2x) | `patch('...get_default_registries')` | Pass registries param |

**Deprecation:** Add DeprecationWarning to get_default_registries() and set_default_registries()

**Verification:** `pytest tests/ -n 12` — all pass with zero deprecation warnings from production code

**Definition of Done:**
- [ ] All test mock/patch patterns use DI instead of patching globals
- [ ] get_default_registries() marked deprecated with warning
- [ ] All 7353+ tests pass
- [ ] Zero deprecation warnings from game/ code in test output

---

## Related Cleanup Items

### Include During Migration

| ID | Issue | Phase | Effort | Change |
|----|-------|-------|--------|--------|
| MOD-CORE-007 | IRegistryProvider missing get_resources() | Phase 1 | ~6 lines | Add method to protocol + implementations |
| MOD-CORE-006 | TestRegistryProvider lacks resources | Phase 1 | ~5 lines | Add resources param + get_resources() |
| MOD-CORE-005 | Module-level globals alongside singleton | Phase 5 | ~30 lines | Move _default_registries into RegistryManager class |

### Fix After Migration (Quick Separate PR)

| ID | Issue | Effort | Change |
|----|-------|--------|--------|
| MOD-CORE-002 | GameRegistries frozen=True with mutable dicts | 1 line | Remove frozen=True |
| MOD-CORE-004 | Inconsistent frozen state management | ~5 lines | Document limitation, fix misleading comment |

### Defer to Future Project

| ID | Issue | Effort | Rationale |
|----|-------|--------|-----------|
| AR-005 | RegistryManager singleton removal | 3-5 days | 180+ call sites. Not blocking; wait for DI migration to stabilize. |

---

## Risk Assessment

### Per-Phase Risk Matrix

| Phase | Risk | Impact if Failed | Mitigation |
|-------|------|-----------------|------------|
| Phase 1 | LOW | Protocol incomplete | Pure additions, easy rollback |
| Phase 2 | LOW | Import errors | Only changes __all__, easy rollback |
| Phase 3 | MEDIUM | 11 files break | Migrate one file at a time, test after each |
| Phase 4 | MEDIUM | ship_loader breaks | Well-tested code, clear patterns |
| Phase 5 | MEDIUM | 18 test files break | Update one test at a time, run suite after each |

### Critical Risks

1. **WorkshopContext.__post_init__()** — Import-time access to get_default_registries(). Must convert to lazy property before removing the function.

2. **FleetCapabilityCalculator static methods** — Properties/static methods can't easily accept registries parameter. May need to convert to instance methods or store provider on the class.

3. **Test infrastructure (conftest.py)** — 7353+ tests depend on reset_game_state fixture. The fixture legitimately uses RegistryManager.instance() for hydrate/clear — this is the composition root pattern and should stay.

4. **xdist parallelization** — Each worker has isolated singletons (separate processes). No special handling needed, but verify with `-n 12` after each phase.

### Performance Impact

**Negligible.** DI method call overhead is ~30-100ns per access vs ~20-70ns for direct attribute access. At 100 registry accesses per frame (60 FPS), total overhead is 10us (0.06% of frame budget). No optimization needed.

---

## Test Strategy

```bash
# After each phase:
pytest tests/ -n 12                         # Full suite (7353+ pass, 0 fail)
pytest tests/unit/core/ -v                   # Core registry tests (detailed)

# Phase-specific:
pytest tests/unit/core/test_registry_provider.py -v   # Phase 1
pytest tests/unit/strategy/ -v                         # Phase 3
pytest tests/unit/ui/ -v                               # Phase 3
pytest tests/unit/simulation/ -v                       # Phase 4
pytest tests/unit/builder/ -v                          # Phase 5
```

### Key Regression Tests

| Test | Why It Matters |
|------|---------------|
| test_registry_features.py | Tests get_default_registries/set_default_registries |
| test_registry_provider.py | Tests DefaultRegistryProvider and TestRegistryProvider |
| test_singleton_and_thread.py | Tests RegistryManager singleton behavior |
| test_protocols_boundary.py | Tests IRegistryProvider compliance |
| test_deprecated_code_removed.py | Asserts deprecated patterns are gone |
| test_service_injection.py | Tests DI patterns |

---

## Estimated Effort

| Phase | Effort | Production Files | Test Files |
|-------|--------|-----------------|------------|
| Phase 1: Complete Protocol | 30 min | 2 | 1 |
| Phase 2: Internalize RegistryManager | 1 hour | 1 | 0 |
| Phase 3: Migrate TIER 2 | 2-3 hours | 10 | 0-3 |
| Phase 4: Migrate TIER 3 | 1-2 hours | 1 | 5-10 |
| Phase 5: Update Tests + Deprecate | 2-3 hours | 1 | 18 |
| **Total** | **~7-10 hours** | **~15** | **~22** |

---

## Definition of "Done"

The migration is complete when:

1. **IRegistryProvider** has `get_components()`, `get_modifiers()`, `get_vehicle_classes()`, `get_resources()`
2. **DefaultRegistryProvider** implements all 4 methods
3. **TestRegistryProvider** accepts and returns all 4 registries
4. **RegistryManager** is not in `__all__` — internal implementation detail
5. **get_default_registries()** has deprecation warning, zero production callers
6. **get_default_registry_provider()** is the single recommended entry point
7. **All production code** uses either constructor DI or `get_default_registry_provider()`
8. **All test mocks** use DI (TestRegistryProvider or fixture injection) instead of patching globals
9. **7353+ tests pass**, 0 failures
10. **Module docstring** updated to show single recommended pattern (TIER 1 only)

### Final registry.py Module Docstring

```python
"""
Registry Access Pattern
=======================

Dependency Injection [RECOMMENDED]:
    from game.core.registry import get_default_registry_provider

    # Production - uses the shared singleton-backed provider
    provider = get_default_registry_provider()
    components = provider.get_components()

    # Or receive via constructor (best):
    def __init__(self, registry: IRegistryProvider):
        self._registry = registry

    # Test - uses isolated data
    from game.core.registry import TestRegistryProvider
    provider = TestRegistryProvider(
        components={"test_laser": {...}},
        modifiers={},
        resources={}
    )
"""
```
