# PROJ-42: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Source Document
All issues originate from: `findings_03_backward_compatibility_legacy.md`

### Issue Summary
| Category | Critical | Major | Minor | Info | Total |
|----------|----------|-------|-------|------|-------|
| Dual Registry System (BCD-001, LPH-001) | 2 | 1 | - | - | 3 |
| Deprecated Modules (LPH-002, STR-001) | 2 | - | - | - | 2 |
| Static/Instance Patterns (LPH-003, BCD-003) | 2 | - | - | - | 2 |
| Backward Compat Layers (LPH-006, BCD-004, BCD-005) | 1 | 3 | 3 | - | 7 |
| Proxy/Lazy Init Patterns (LPH-004, LPH-008, LPH-010) | 1 | 2 | - | - | 3 |
| Serialization Legacy Formats (BCD-006-010, LPH-005, LPH-007, STR-002) | 1 | 2 | 5 | - | 8 |
| BattleEngine Legacy Paths (LPH-009, SIM-007) | 1 | 1 | - | - | 2 |
| Scattered Compat Code (STR-005, BCD-007, BCD-008) | - | 1 | 3 | - | 4 |
| Minor Legacy Patterns (LPH-011-020) | - | - | 10 | 3 | 13 |
| **TOTAL** | **10** | **10** | **21** | **3** | **44** |

### Baseline Test Results
- **5199 tests passed**, 3 skipped
- **28,319 deprecation warnings** emitted during test run
- Key warnings from: `get_component_registry()`, `get_modifier_registry()`, `get_vehicle_classes()`

---

## Swarm Findings Summary

### 1. Dual Registry System Analysis (Agent 1)

**Current State:**
- **121 deprecated function calls** across 42+ files
- **Two parallel DI patterns**: IRegistryProvider (legacy) vs GameRegistries (modern)
- **5 services** have try/except fallback chains

**Distribution:**
| Pattern | Files | Percentage |
|---------|-------|------------|
| Deprecated functions only | 31 | 73.8% |
| IRegistryProvider | 9 | 21.4% |
| GameRegistries | 24 | 57.1% |
| Both patterns | 3 | 7.1% |

**Critical Files (Priority Order):**
1. `game/strategy/services/ship_stats_service.py` - 20+ deprecated calls
2. `game/simulation/services/modifier_service.py` - 4+ deprecated calls
3. `game/simulation/entities/ship.py` - 8+ deprecated calls
4. `game/simulation/components/component.py` - 5+ deprecated calls
5. `game/simulation/services/vehicle_design_service.py` - dual support

**Migration Path:** Constructor DI → Method-level DI → Remove fallbacks

### 2. FleetMovementSimulator Analysis (Agent 2)

**Status: SAFE TO REMOVE**
- No active instantiations in production code
- No imports in production code
- All functionality migrated to `FleetNavigationService`
- 0 tests directly depend on it

**Removal Steps:**
1. Delete `game/strategy/engine/fleet_movement.py` (331 LOC)
2. Update any documentation references
3. Verify tests pass

### 3. Static/Instance Method Patterns (Agent 3)

**Current State:**
- **32 static callers** in production code
- **0 instance callers** in production code
- Two services affected: ShipStatsService, ModifierService

**Recommendation:** Keep instance pattern as canonical, deprecate static

**Methods Affected:**
| Service | Method | Static Calls |
|---------|--------|--------------|
| ShipStatsService | calculate_stats() | 6 |
| ModifierService | is_modifier_allowed() | 6 |
| ModifierService | ensure_mandatory_modifiers() | 4 |
| ModifierService | get_mandatory_modifiers() | 8 |
| ModifierService | get_initial_value() | 5 |
| ModifierService | is_modifier_mandatory() | 3 |

### 4. Backward Compatibility Layers (Agent 4)

**Keep (Cannot Remove Safely):**
- `constants.py` WIDTH/HEIGHT re-export (64 files depend on it)
- `validation.py` ValidationResult dual patterns (21+ files)
- `save_game_service.py` MIGRATABLE_VERSIONS (player data compatibility)

**Can Remove After Migration:**
- `component_constants.py` LayerType re-export (10-15 files to update)
- `legacy_components.py` ModifierEditorPanel (if standalone builder deprecated)

**Remove Immediately:**
- `app.py` GameState aliases (lines 49-58) - simple find/replace

### 5. Proxy/Lazy Init Patterns (Agent 5)

**Keep (Necessary):**
- `_ValidatorProxy` in ship.py - prevents circular imports
- `_ProfilerProxy` in profiling.py - thread-safe lazy init

**Phase Out:**
- WorkshopScreen proxy properties (after MVVM migration complete)

**Refactor:**
- `hasattr` lazy init patterns (use getattr with defaults instead)

### 6. Serialization Legacy Formats (Agent 6)

**Active Formats (Keep):**
- Ship dict format with modifiers (all modern ships)
- V2 modifier format (array-based)
- ShipInstance class (fleet/strategy layer)

**Unused/Defensive Code (Can Remove):**
- Ship string format parser (no saves in this format)
- V1 modifier format detection (already rejected at validation)
- Formation list format (auto-converts on load/save)

**Needs Migration:**
- String ship references in Fleet (blocks battle conversion)

### 7. BattleEngine Legacy Paths (Agent 7)

**Dual Paths Found:**
- Controller creation: Legacy (lines 227-241) vs PROJ-17 (lines 217-225)
- Reinforcements: Legacy (lines 284-289) vs New (lines 280-282)
- Ship init: Legacy fallback vs PROJ-38 DI

**Bug Found:** `ship.py:467` - `create_component()` called without `registries` parameter

**Recommendation:** Make PROJ-38 DI the only path, remove fallbacks

### 8. Scattered Compat Code (Agent 8)

**Can Centralize:**
- PathSegment legacy 'hex' field
- `_ChaserProxy` adapter class
- Fleet order format deserializer (4 formats!)
- Legacy crew requirement pattern

**Remove Immediately:**
- Scene state aliases in app.py (9 aliases, simple find/replace)

### 9. Test Impact Analysis (Agent 9)

**Tests Affected by Removal:**
| Pattern | Tests Affected | Risk |
|---------|---------------|------|
| IRegistryProvider | 80+ | CRITICAL |
| Deprecated functions | 34 files | HIGH |
| Dual static methods | 5-15 | MEDIUM |
| FleetMovementSimulator | 0 | LOW |

**New Tests Needed:**
- Registry removal impact tests
- Static method removal tests
- Save game migration E2E tests
- Deprecated imports removed verification

---

## Key Patterns to Reuse

### GameRegistries DI Pattern
**File:** `game/core/registry.py:15-25`
```python
@dataclass(frozen=True)
class GameRegistries:
    components: Dict[str, Any]
    modifiers: Dict[str, Any]
    vehicle_classes: Dict[str, Any]
    resources: Dict[str, Any]
```
Use this as the single injection point for all registry access.

### Service Constructor Pattern
**File:** `game/strategy/services/ship_stats_service.py:63-84`
```python
def __init__(self, registries: Optional[GameRegistries] = None):
    if registries is not None:
        self._registries = registries
    else:
        self._registries = get_default_registries()
```

### Test Registry Fixture Pattern
**File:** `tests/conftest.py`
Use `@pytest.fixture` with `GameRegistries` for consistent test setup.

---

## Dependencies & Risks

### 1. Circular Import Risk
**Risk:** Removing proxy patterns may reintroduce circular imports
**Mitigation:** Keep _ValidatorProxy and _ProfilerProxy; they solve real problems

### 2. Player Save Data Risk
**Risk:** Removing save format support breaks existing player saves
**Mitigation:** Keep MIGRATABLE_VERSIONS for announced deprecation period

### 3. Test Suite Stability Risk
**Risk:** 80+ tests depend on IRegistryProvider; removing breaks CI
**Mitigation:** Phase test updates before code removal; never remove both simultaneously

### 4. UI Layer Coupling Risk
**Risk:** Standalone builder uses legacy_components.py; removal breaks it
**Mitigation:** Treat as separate decision - only remove if builder deprecated

### 5. Registry Initialization Order Risk
**Risk:** Some code runs before registries initialized
**Mitigation:** Ensure `set_default_registries()` called early in app.py startup

---

## Opportunities Discovered

1. **28,319 deprecation warnings** can be eliminated (cleaner test output)
2. **331 LOC** can be deleted (FleetMovementSimulator)
3. **189 LOC** potentially removable (legacy_components.py)
4. **121 deprecated function calls** can become type-safe DI
5. **~30% code path reduction** in services (remove dual patterns)

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Key Decisions Made

1. **Complete PROJ-38 GameRegistries migration** - All services will use DI
2. **Remove FleetMovementSimulator immediately** - No dependencies found
3. **Keep proxy patterns** - They solve real circular import issues
4. **Keep save format compatibility** - Player data protection
5. **Phase test updates before code removal** - Maintain CI stability
6. **Centralize compatibility code** - Create `legacy_compatibility.py` module
