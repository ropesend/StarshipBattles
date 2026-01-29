# Phase 7: UI Layer Remediation

**Status:** SUPERSEDED - Moved to Phase 12
**Estimated Effort:** N/A (see Phase 12)
**Priority:** N/A

---

## Overview

> **IMPORTANT:** This phase has been superseded by Phase 12.
>
> All UI layer remediation tasks have been consolidated into [phase_12_checklist.md](phase_12_checklist.md), which includes:
> - All UI → Internal layer violations (37 files, 124 imports)
> - All code quality tasks from this phase
> - Structured remediation by difficulty tier

---

## Migrated Tasks

The following tasks from this phase were moved to Phase 12:

| Original Task | New Location |
|---------------|--------------|
| 7.2 FormationEditor Type Hints (NEW-UI-005) | Phase 12.11 |
| 7.3 Bare Exception Fixes (NEW-UI-008) | Phase 12.12 |
| 7.4 Fragile Path Construction (NEW-UI-009) | Phase 12.13 |
| 7.6 tkinter Exception Handling (NEW-UI-011) | Phase 12.14 |
| 7.7 UI Layout Constants (NEW-UI-012) | Phase 12.15 |
| 7.8 RaceSetupScreen Planning (NEW-UI-014) | Phase 12.16 |
| 7.9 ComponentRef Pattern (NEW-UI-015) | Phase 12.17 |
| 7.10 Schematic Cache Key (NEW-UI-016) | Phase 12.18 |

---

## Removed Tasks (Audit Verification)

### ~~7.1 Consolidate CrewCapacity Logic (NEW-UI-004)~~
**Status:** REMOVED - ALREADY COMPLETE
**Reason:** CrewCapacity is now properly centralized with helper functions:
- `_get_legacy_crew_requirement()` - handles legacy negative values
- `_get_total_crew_requirement()` - combines CrewRequired + legacy
- `get_crew_capacity()` - safe with `max(0, ...)` pattern

### ~~7.5 Fix Module-level Logger (NEW-UI-010)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** Uses proper `logging.getLogger(__name__)` pattern.

---

## Action Required

**Do not work on this phase.** Proceed directly to Phase 12 after completing Phases 1-6 and 8-11.

See [phase_12_checklist.md](phase_12_checklist.md) for the consolidated UI layer remediation plan.
