# PROJ-231: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Proceed with refactoring | Multi-agent analysis confirms function is NOT irreducibly complex |
| 2026-02-26 | Add edge case tests first (Phase 1) | Safety analysis found coverage gaps that must be filled before refactoring |
| 2026-02-26 | Extract 5 helper functions | Individual helpers (warp, spaceyard, cargo, special, status) are clearer than generic abstraction |
| 2026-02-26 | Preserve late imports | FleetCapabilityCalculator imports must stay inside functions to avoid circular imports |
| 2026-02-26 | Preserve short-circuit optimization | Don't call expensive capability checks unless filter is active |

---

## Detailed Decisions

### Decision 1: Proceed with Refactoring

**Status:** APPROVED

**Context:** `filter_ships` has CC 36, well above the threshold of 20.

**Analysis:**
- Multi-agent review completed (structure, dependency, safety)
- Function is NOT irreducibly complex
- Clear extraction patterns identified
- Good test coverage exists (~20 tests)
- Single production caller allows safe refactoring

**Decision:** Proceed with refactoring via helper function extraction.

---

### Decision 2: Add Edge Case Tests First

**Status:** APPROVED

**Gaps Found:**
- Empty filter_state dict
- Combined filter interactions
- All status filters disabled simultaneously

**Decision:** Phase 1 will add tests for these edge cases BEFORE any code changes.

**Rationale:** Establishes regression safety net and documents expected behavior.

---

### Decision 3: Extract Five Helpers

**Status:** APPROVED

**Options Considered:**
1. Single `_passes_all_filters()` helper - Moves complexity but doesn't reduce it
2. Generic binary filter helper - Reusable but adds abstraction overhead
3. Individual helpers per filter type - Clear, testable, moderate CC each ← CHOSEN

**Helpers to extract:**
- `_passes_warp_filter()`
- `_passes_spaceyard_filter()`
- `_passes_cargo_filter()`
- `_passes_special_capability_filters()`
- `_passes_status_filter()`

---

### Decision 4: Preserve Critical Invariants

**Status:** APPROVED

**Invariants:**
1. Status filter order: destroyed → derelict → damaged → undamaged
2. Default to True (show all) for missing filter keys
3. Short-circuit optimization for binary filters
4. Special capability key derivation (`can_X` → `no_X`)
5. Late imports for FleetCapabilityCalculator

**Rationale:** These are intentional design choices that must survive refactoring.
