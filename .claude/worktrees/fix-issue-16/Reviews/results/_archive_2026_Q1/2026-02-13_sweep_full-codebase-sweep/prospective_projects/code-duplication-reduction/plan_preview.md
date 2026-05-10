# Project Plan: Code Duplication Reduction

## Project Metadata

- **Project ID:** PROJ-XXX
- **Title:** Code Duplication Reduction
- **Status:** Planning
- **Created:** 2026-02-13
- **Source:** Sweep 2026-02-13_sweep_full-codebase-sweep

## Overview

This project addresses 36 duplication findings (30 DUP + 6 UNK) from the codebase sweep. The primary goals are:

1. Consolidate repeated serialization patterns
2. Extract common iteration helpers
3. Centralize calculation utilities
4. Reduce copy-paste code patterns

## Phases

### Phase 1: Serialization Consolidation

**Objective:** Create reusable serialization infrastructure.

**Tasks:**
- [ ] Design SerializableMixin or base class for to_dict/from_dict (DUP-STR-004)
- [ ] Apply to battle_state.py (DUP-SIM-001)
- [ ] Apply to research_tracker.py (DUP-FND-006)
- [ ] Standardize field handling patterns

**Estimated Effort:** 3-4 days

### Phase 2: Iterator Pattern Extraction

**Objective:** Create reusable iteration helpers.

**Tasks:**
- [ ] Extract team iteration helper (DUP-SIM-003)
- [ ] Extract colony pod iteration helper (DUP-STR-006)
- [ ] Extract component layer iteration pattern (DUP-STR-007)

**Estimated Effort:** 2-3 days

### Phase 3: Calculation Utilities

**Objective:** Centralize repeated calculations.

**Tasks:**
- [ ] Extract flee direction calculator (DUP-FND-004)
- [ ] Extract gaussian factor utility (DUP-STR-008)
- [ ] Consolidate Vector2 conversion (DUP-SIM-004)

**Estimated Effort:** 1-2 days

### Phase 4: UI Utilities Consolidation

**Objective:** Centralize scattered UI helpers.

**Tasks:**
- [ ] Consolidate image transform operations (DUP-UI2-004)
- [ ] Consolidate camera coordinate transforms (DUP-UI2-006)
- [ ] Consolidate number formatting (UNK-08)
- [ ] Consolidate dropdown recreation utility (UNK-11)

**Estimated Effort:** 2-3 days

### Phase 5: Domain Helper Extraction

**Objective:** Extract repeated domain-specific patterns.

**Tasks:**
- [ ] Consolidate build queue source collection (DUP-STR-001)
- [ ] Consolidate shipyard detection (DUP-STR-002)
- [ ] Extract fleet resolution helper (DUP-STR-005)
- [ ] Consolidate resource ability logic (DUP-SIM-002)

**Estimated Effort:** 2-3 days

## Success Criteria

1. All MAJOR duplication issues resolved
2. Serialization base class/mixin available and documented
3. Common iterator helpers extracted
4. No significant copy-paste patterns remaining
5. Code deduplication reduces total LOC by 500+

## Dependencies

- None (self-contained)

## Risks

- Some consolidation may require interface changes
- Tests may need updating to use new helpers
