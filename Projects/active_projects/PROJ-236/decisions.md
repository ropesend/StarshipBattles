# PROJ-236: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Proceed with refactoring | Function is NOT irreducibly complex; complexity from repeated patterns |
| 2026-02-26 | Test-first approach | Add 6 safety tests before any code changes |
| 2026-02-26 | Use private helper functions | `_` prefix, same file, good testability |
| 2026-02-26 | Preserve late import pattern | Circular import risk still exists at module level |
| 2026-02-26 | Extract status first, then capabilities | Highest CC reduction first, enables subsequent extractions |

---

## Decision Details

### Decision 1: Proceed with Refactoring
**Date:** 2026-02-26
**Status:** Approved

**Context:** The `filter_ships` function has CC 36. Multi-agent review found strong test coverage (~25 tests), pure function semantics, and clear extraction patterns.

**Decision:** Proceed with refactoring. The function is NOT irreducibly complex.

**Rationale:**
- Complexity comes from repeated patterns, not inherent problem complexity
- The binary filter pattern appears 5 times - clear extraction candidate
- The status cascade is a simple priority classifier, not a state machine
- Test coverage is sufficient to catch regressions

---

### Decision 2: Test-First Approach
**Date:** 2026-02-26
**Status:** Approved

**Context:** Safety analysis identified 6 missing test cases for edge conditions.

**Decision:** Add safety tests in Phase 1 BEFORE any code changes.

**Tests to add:**
1. Empty ships list
2. Partial filter state (empty dict)
3. All filters disabled
4. Derelict priority over damaged
5. Order preservation
6. Combined filter categories

**Rationale:** These tests document expected behavior and catch regressions during refactoring.

---

### Decision 3: Helper Function Structure
**Date:** 2026-02-26
**Status:** Approved

**Context:** Multiple approaches possible for extracting helpers.

**Decision:** Use module-private functions (prefixed with `_`) in the same file.

**Alternatives considered:**
- Filter class hierarchy - Overkill for this use case
- Separate filter module - Adds indirection without benefit
- Lambda functions inline - Reduces readability

**Rationale:** Private functions provide good testability while keeping related code together.

---

### Decision 4: Preserve Late Import Pattern
**Date:** 2026-02-26
**Status:** Approved

**Context:** `FleetCapabilityCalculator` is imported inside conditionals to avoid circular imports.

**Decision:** Keep the late import pattern, but move it outside the per-ship loop into the helper functions.

**Rationale:**
- Circular import issue still exists at module level
- Moving import to helper function top reduces per-ship import overhead
- Full resolution of circular import is out of scope

---

### Decision 5: Extraction Order
**Date:** 2026-02-26
**Status:** Approved

**Context:** Multiple helpers need extraction. Order matters for incremental verification.

**Decision:** Extract in this order:
1. Status classifier (`_get_ship_status`)
2. Status filter (`_passes_status_filter`)
3. Binary filter helper (`_passes_binary_filter`)
4. Capability filters (`_passes_capability_filters`)
5. Special capability filters (`_passes_special_capability_filters`)

**Rationale:**
- Start with status (most complex, highest CC contribution)
- Binary filter helper enables subsequent capability extractions
- Each step reduces CC incrementally
