# Legacy Code Cleanup Project

**Project Start:** 2026-01-25
**Status:** Planning Complete - Ready for Execution

---

## Overview

This project systematically cleans up legacy code, enforces architectural boundaries, and standardizes patterns across the Starship Battles codebase.

**Key Decisions Made:**
- **Type Safety:** Use Protocols/ABCs for core entities
- **Registry Access:** Tiered approach (utility functions + domain services)
- **Layer Boundaries:** Strict enforcement with dependency inversion
- **UI Framework:** Stay with pygame_gui, migrate legacy Button class
- **Save Games:** No backward compatibility required

---

## Phase Summary

| Phase | Name | Risk | Document |
|-------|------|------|----------|
| 1 | Delete Dead Code | Very Low | [PHASE_1_DELETE_DEAD_CODE.md](PHASE_1_DELETE_DEAD_CODE.md) |
| 2 | Remove Shims & Aliases | Medium | [PHASE_2_REMOVE_SHIMS_ALIASES.md](PHASE_2_REMOVE_SHIMS_ALIASES.md) |
| 3 | Consolidate Re-exports | Medium | [PHASE_3_CONSOLIDATE_REEXPORTS.md](PHASE_3_CONSOLIDATE_REEXPORTS.md) |
| 4 | Enforce Layer Boundaries | High | [PHASE_4_ENFORCE_LAYER_BOUNDARIES.md](PHASE_4_ENFORCE_LAYER_BOUNDARIES.md) |
| 5 | Standardize Registry Access | Medium | [PHASE_5_STANDARDIZE_REGISTRY_ACCESS.md](PHASE_5_STANDARDIZE_REGISTRY_ACCESS.md) |
| 6 | Type Safety via Protocols | High | [PHASE_6_TYPE_SAFETY_PROTOCOLS.md](PHASE_6_TYPE_SAFETY_PROTOCOLS.md) |
| 7 | Standardize Data Formats | Medium | [PHASE_7_STANDARDIZE_DATA_FORMATS.md](PHASE_7_STANDARDIZE_DATA_FORMATS.md) |
| 8 | Clean Up Tests & Patterns | Low | [PHASE_8_CLEANUP_TESTS_PATTERNS.md](PHASE_8_CLEANUP_TESTS_PATTERNS.md) |

---

## Execution Instructions

### For Each Phase:

1. **Read the phase document** - Understand objectives and detailed tasks
2. **Complete all tasks** in the phase document
3. **Run verification checklist** at the end of each phase
4. **Ensure all tests pass** before moving to next phase
5. **Commit changes** with descriptive message

### Between Phases:

- All unit tests must pass
- All integration tests must pass
- Application must launch and run correctly
- No circular imports
- No deprecation warnings

---

## Target Architecture

```
┌─────────────────────────────────────┐
│    UI Layer (game/ui/)              │  Depends on: Strategy, Simulation, AI, Core
└──────────────┬──────────────────────┘
┌──────────────▼──────────────────────┐
│  Strategy Layer (game/strategy/)    │  Depends on: Simulation (via interface), Core
└──────────────┬──────────────────────┘
┌──────────────▼──────────────────────┐
│  Simulation Layer (game/simulation/)│  Depends on: Core ONLY (no pygame!)
└──────────────┬──────────────────────┘
┌──────────────▼──────────────────────┐
│  AI Layer (game/ai/)                │  Depends on: Simulation interfaces, Core
└──────────────┬──────────────────────┘
┌──────────────▼──────────────────────┐
│  Core Layer (game/core/)            │  Depends on: Nothing
└─────────────────────────────────────┘
```

---

## Key Metrics

### Before Cleanup:
- Files marked for deletion: 11 + 45MB directory
- Deprecated shim files: 5
- Method/property aliases: 30+
- hasattr/getattr patterns: 500+
- Legacy data format locations: 60+
- Duplicate classes: 3 (ValidationResult)

### Target After Cleanup:
- Dead files: 0
- Shim files: 0
- Aliases: 0
- hasattr patterns: <100 (legitimate uses only)
- Legacy formats: 0
- Duplicate classes: 0

---

## Related Documents

- [legacy_code_audit.md](../../legacy_code_audit.md) - Original comprehensive audit
- [legacy_cleanup_stages.md](../../legacy_cleanup_stages.md) - Alternative staging document

---

*End of README*
