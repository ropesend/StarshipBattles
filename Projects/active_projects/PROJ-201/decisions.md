# PROJ-201: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-27 | Project initialized | Starting point for Reduce complexity: FleetDataSource._get_column_value (CC 29) |
| 2026-02-27 | PROCEED with refactoring | Multi-agent review: 30 tests, pure function, clear extraction path |
| 2026-02-27 | Use handler method extraction | Late imports prevent simple dispatch; methods can contain imports |
| 2026-02-27 | Consolidate capability columns | 5 columns share identical pattern; single handler with SPECIAL_CAPABILITY_COLUMNS |
| 2026-02-27 | 3-phase approach | Extract complex handlers first for early CC wins; dispatch last |

---

## Detailed Decisions

### Decision 1: Proceed with Refactoring

**Date:** 2026-02-27
**Status:** DECIDED

**Context:** `_get_column_value` has CC=29, well above the threshold of 20. Need to determine if refactoring is warranted or if the function should be skipped.

**Analysis:**
- Multi-agent review completed (structure, dependency, safety)
- Function has 30 tests covering all 19 column types
- Function is pure (no side effects)
- Single internal caller (private method)
- Clear extraction path via handler methods

**Decision:** PROCEED WITH REFACTORING

---

### Decision 2: Handler Extraction over Dispatch Table

**Date:** 2026-02-27
**Status:** DECIDED

**Context:** Two main approaches considered:
1. Pure dispatch table with lambdas/functions
2. Handler method extraction with method dict

**Decision:** USE HANDLER METHOD EXTRACTION

Extract each column's logic to a `_format_X(ship)` method, then create a dispatch dict mapping column IDs to bound methods.

Benefits:
- Handlers can contain late imports
- Each handler is independently readable
- Methods can be tested in isolation if needed
- Cleaner than inline lambdas

---

### Decision 3: Consolidate Capability Columns

**Date:** 2026-02-27
**Status:** DECIDED

**Context:** Five columns (`can_destroy_planet`, `can_open_warp`, `can_close_warp`, `can_destroy_star`, `can_create_sphere`) all follow identical pattern.

**Decision:** CREATE SINGLE `_format_capability(ship, col_id)` HANDLER

This handler will:
1. Perform the late import once
2. Look up ability name from existing SPECIAL_CAPABILITY_COLUMNS dict
3. Return Yes/No based on capability check

---

### Decision 4: Phase Structure

**Date:** 2026-02-27
**Status:** DECIDED

**Decision:** 3-PHASE APPROACH

1. **Phase 1: Extract Complex Handlers** - status, resources (highest CC impact)
2. **Phase 2: Extract Remaining Handlers** - simple and service handlers
3. **Phase 3: Implement Dispatch & Verify** - replace if-elif chain

Rationale: Test coverage is strong, so no test fortification needed first.
