# PROJ-238: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Proceed with refactoring | Multi-agent review confirmed function is refactorable - pure function, single caller, comprehensive tests |
| 2026-02-26 | Add edge case tests first | Safety analysis found gaps: empty filter_state, all-filters-false, destroyed+derelict precedence |
| 2026-02-26 | Extract generic binary filter helper | Pattern repeats 4 times - DRY violation to eliminate |
| 2026-02-26 | Move late imports to function scope | Avoid circular imports but stop repeating import inside loops |
| 2026-02-26 | Use list comprehension in final form | Replace 10 continue statements with clean predicate composition |
| 2026-02-26 | Preserve status check order | Critical invariant: destroyed → derelict → damaged → undamaged |

## Detailed Decisions

### Decision 1: Proceed with Refactoring
**Date:** 2026-02-26
**Status:** Approved

**Context:** The `filter_ships` function has CC 36, well above the threshold of 20.

**Analysis:**
- Multi-agent review confirmed the function is refactorable
- Comprehensive test coverage exists (20+ test methods)
- Function is pure with no side effects
- Single production caller allows safe refactoring

**Decision:** Proceed with phased refactoring approach.

---

### Decision 2: Add Edge Case Tests Before Refactoring
**Date:** 2026-02-26
**Status:** Approved

**Context:** Safety analysis identified test coverage gaps that could mask regression bugs.

**Gaps identified:**
- Empty `filter_state` dict
- All filters set to False
- Destroyed + derelict ship precedence

**Decision:** Phase 1 will add these tests before any code changes.

---

### Decision 3: Extract Generic Binary Filter Helper
**Date:** 2026-02-26
**Status:** Approved

**Context:** The binary capability filter pattern repeats 4 times with identical structure.

**Current pattern (repeated):**
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_not_X', True)
if not show_has or not show_not:
    has_capability = check_capability(ship)
    if has_capability and not show_has:
        continue
    if not has_capability and not show_not:
        continue
```

**Decision:** Extract `_passes_binary_filter(has_cap, show_has, show_not) -> bool` to eliminate duplication.

---

### Decision 4: Move Late Imports to Function Scope
**Date:** 2026-02-26
**Status:** Approved

**Context:** `FleetCapabilityCalculator` is imported inside the loop, inside conditionals (up to 6 times per ship).

**Decision:** Move import to the start of helper functions. Do NOT move to module level to avoid circular import issues (the existing late imports are intentional for this reason).

---

### Decision 5: Use List Comprehension in Final Form
**Date:** 2026-02-26
**Status:** Approved

**Context:** The current function uses explicit loop with `result.append()` and multiple `continue` statements.

**Decision:** Final refactored form will use list comprehension with predicate functions for clarity and reduced complexity.

---

### Decision 6: Preserve Status Check Order
**Date:** 2026-02-26
**Status:** Approved

**Context:** Status checks have specific precedence: destroyed → derelict → damaged → undamaged.

**Decision:** The `_get_ship_status()` helper must preserve this exact order. Tests will verify precedence.
