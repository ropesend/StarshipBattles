# PROJ-27: Core Foundation: Registry Singleton Refactoring

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-27` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-27 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major Issues | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Audit Fixes (Cycle 1) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-01-27
**Active Phase:** Audit complete
**Last Action:** Audit cycle 2 passed with no significant issues
**Next Action:** User verification required
**Blockers:** None
**Context for Next Agent:** Project is audit-complete. User needs to verify and close.

## Overview
Systematic remediation of findings from review: 2026-01-27_general_self-contained-systems. Total findings selected: 2 (Critical: 1, Major: 1, Other: 0).

## Goals
- Address CORE-01: Singleton anti-pattern
- Address CORE-03: No abstraction between services and registries

## Scope
**In:**
- Complex
- Medium

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| IRegistryProvider Protocol | `game/core/protocols.py` |
| DefaultRegistryProvider | `game/core/registry.py` |
| TestRegistryProvider | `game/core/registry.py` |
| ShipStatsService injection | `game/strategy/services/ship_stats_service.py` |
| ModifierService injection | `game/simulation/services/modifier_service.py` |
| VehicleDesignService injection | `game/simulation/services/vehicle_design_service.py` |
| Registry provider tests | `tests/unit/core/test_registry_provider.py` |
| Service injection tests | `tests/unit/core/test_service_injection.py` |

## Implementation Summary

### CORE-01: Singleton Anti-Pattern Fix
Created an abstraction layer for registry access via the IRegistryProvider protocol:
- `IRegistryProvider`: Runtime-checkable protocol with `get_components()`, `get_modifiers()`, `get_vehicle_classes()`
- `DefaultRegistryProvider`: Production implementation backed by singleton
- `TestRegistryProvider`: Isolated implementation for testing
- `get_default_registry_provider()`: Factory function for singleton provider

### CORE-03: Service Registry Abstraction
Added optional `registry` parameter to key services:
- `ShipStatsService.calculate_stats(registry=...)`
- `ModifierService.is_modifier_allowed(registry=...)` (and all other methods)
- `VehicleDesignService(registry=...)` (constructor)

Key design decision: Falls back to original module-level functions when `registry=None` to maintain backward compatibility with 62 existing tests that patch those functions.

### Test Results
- Baseline: 4613 passed
- After Phase 2: 4693 passed (+38 new tests)
- After Phase 3: 4697 passed (+4 new behavioral tests)
- 24 tests for IRegistryProvider protocol and providers
- 18 tests for service injection (14 original + 4 new behavioral tests)

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [x] All tests passing
- [x] Audit passed
- [ ] User verified

---

## Audit Log

| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-27 | 2 major, 2 minor issues | Added Phase 3 for fixes |
| 2 | 2026-01-27 | No significant issues | PASSED |

---

## Audit Cycle 1 - 2026-01-27

### Confirmed Issues

| Task | Issue | Severity | Fix Required |
|------|-------|----------|--------------|
| 2.1 | VehicleDesignService.get_available_components() bypasses injected registry | Major | Use self._registry.get_components() |
| 2.1 | VehicleDesignService.validate_design() doesn't use stored registry | Major | Document limitation OR implement injection |
| 2.1 | Service injection tests are mostly signature checks, not behavior tests | Minor | Add behavioral verification tests |
| 1.1 | get_default_registry_provider() factory has no thread safety | Minor | Acceptable for single-threaded game |

### Resolved Concerns (False Positives)

| Task | Original Concern | Resolution |
|------|------------------|------------|
| 1.1 | Protocol tests might be trivial | Tests do verify actual isinstance behavior, would catch real bugs |
| 2.1 | Backward compatibility might break | Fallback to singleton is correctly implemented in all cases |

### Items Requiring User Decision

None - all concerns have clear fixes or are acceptable as-is.

---

## Audit Cycle 2 - 2026-01-27

### Summary
Re-audit after Phase 3 fixes. All Cycle 1 issues verified as resolved.

### Verification Checklist

| Check | Task 3.1 | Task 3.2 | Task 3.3 |
|-------|----------|----------|----------|
| Completion | ✓ | ✓ | ✓ |
| Tests Exist | ✓ test_get_available_components_uses_injected_registry | N/A (docs) | ✓ 4 behavioral tests |
| Tests Pass | ✓ | ✓ | ✓ |
| Code Matches Intent | ✓ Line 360 uses self._registry | ✓ Docstring clear | ✓ Tests verify actual behavior |
| No Shortcuts | ✓ | ✓ | ✓ |

### Investigated Concerns

| Concern | Investigation Perspective | Finding | Verdict |
|---------|--------------------------|---------|---------|
| VehicleDesignService.get_available_components() line 360 | Code Review | Correctly uses self._registry.get_components() | ✓ Resolved |
| create_component() on line 363 still uses singleton | Integration Check | Out-of-scope for PROJ-27 - factory function not service | ✓ Acceptable |
| validate_design() singleton limitation | Quality Review | Docstring clearly documents limitation and workaround | ✓ Acceptable |
| Behavioral tests adequate | Test Verification | 4 new tests prove injected registry values are used | ✓ Resolved |

### Resolved Concerns

All Phase 3 fixes verified as correctly implemented:
1. `get_available_components()` now uses `self._registry.get_components()` (line 360)
2. `validate_design()` has clear docstring explaining singleton limitation
3. 4 new behavioral tests prove services use injected registry values

### Notes on Architectural Decisions

The `create_component()` factory function (called on line 363) still uses the singleton directly. This is **acceptable** because:
- PROJ-27 focused on service-level injection, not standalone factory functions
- The behavioral test `test_get_available_components_uses_injected_registry` passes, proving the key requirement is met
- The service correctly iterates over the injected registry's component IDs
- Refactoring `create_component()` would be a separate project

### Result: PASSED

All tasks verified complete. No significant issues found. Ready for user verification.
