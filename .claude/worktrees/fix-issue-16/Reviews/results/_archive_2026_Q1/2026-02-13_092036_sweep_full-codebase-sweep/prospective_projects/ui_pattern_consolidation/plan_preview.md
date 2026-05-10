# [PROJ-XXX] UI Pattern Consolidation

## Status: Planning
## Created: 2026-02-13
## Source: Sweep 2026-02-13_092036_sweep_full-codebase-sweep

---

## Overview

Extract duplicated UI patterns into reusable components to reduce maintenance burden and ensure consistent behavior across the UI layer.

### Problem Statement
Multiple UI windows implement similar patterns independently:
- 4 windows have nearly identical virtual scrolling implementations (~60 lines each)
- 3+ windows duplicate filter toggle button patterns
- Number formatting uses inconsistent 'k' vs 'K' suffixes
- Placeholder surface creation is implemented 3 times

### Goals
1. Create reusable VirtualScrollableList component
2. Create ToggleFilterButton and FilterSidebarBuilder utilities
3. Consolidate number formatting into single utility
4. Extract other duplicated patterns to shared utilities

### Success Criteria
- Virtual scrolling implemented in one place, used by 4 windows
- Filter toggle behavior consistent across all windows
- Number formatting uses consistent suffix style
- No pattern duplicated more than twice
- All existing tests pass

---

## Design Decisions

### DD-001: Virtual Scrolling Implementation
**Decision:** Create VirtualScrollableList as a mixin class
**Rationale:** Windows have different base classes; mixin allows flexible composition
**Alternatives considered:** Base class (rejected - inheritance conflicts)

### DD-002: Number Formatting Location
**Decision:** Add format_compact_number() to game/ui/utils.py
**Rationale:** Centralized utility module, already exists for other utilities
**Alternatives considered:** New formatting module (rejected - overkill for one function)

### DD-003: Filter Toggle Widget
**Decision:** Create ToggleFilterButton as standalone widget class
**Rationale:** Encapsulates state management and visual updates
**Alternatives considered:** Helper function (rejected - doesn't manage state)

---

## Phases

### Phase 1: Utility Functions
**Target:** DUP-UI1-001, DUP-UI1-004, DUP-UI2-003, DUP-FND-006
**Scope:** Simple utility function extractions
**Tests Required:** Unit tests for each utility

- [ ] Add format_compact_number(value, lowercase=False) to utils.py
- [ ] Add create_placeholder_surface(size, style='default') to utils.py
- [ ] Extract scale_image() utility with None handling
- [ ] Extract flee_direction_calculation() utility
- [ ] Update all call sites to use new utilities
- [ ] Add unit tests for utilities

### Phase 2: Virtual Scrolling Component
**Target:** DUP-UI1-002
**Scope:** VirtualScrollableList mixin
**Tests Required:** Component tests, integration tests

- [ ] Design VirtualScrollableList interface
- [ ] Implement scrollbar setup and management
- [ ] Implement mouse wheel handling
- [ ] Implement visible percentage calculation
- [ ] Refactor planet_list_window to use mixin
- [ ] Refactor fleet_report_window to use mixin
- [ ] Refactor empire_build_queue_window to use mixin
- [ ] Refactor event_log_window to use mixin

### Phase 3: Filter Components
**Target:** DUP-UI1-003, DUP-UI1-005, DUP-UI1-007, CON-UI1-010
**Scope:** Filter toggle and sidebar builder
**Tests Required:** Widget tests

- [ ] Create ToggleFilterButton widget class
- [ ] Create FilterSidebarBuilder helper class
- [ ] Move column toggle handling into ColumnManager
- [ ] Consolidate duplicate ColumnManager classes
- [ ] Refactor fleet_report_window filters
- [ ] Refactor planet_list_window filters
- [ ] Refactor empire_build_queue_window filters

### Phase 4: Service Layer Cleanup
**Target:** DUP-UI2-001, DUP-UI2-002, DUP-UI2-006
**Scope:** Service pattern consolidation
**Tests Required:** Service tests

- [ ] Extract Tkinter root initialization to utility
- [ ] Standardize registry provider lazy resolution
- [ ] Consolidate clipboard copy implementation

### Phase 5: Foundation and Strategy Patterns
**Target:** DUP-FND-001, DUP-FND-002, DUP-FND-003, DUP-STR-*
**Scope:** Cross-layer pattern consolidation
**Tests Required:** Unit tests for utilities

- [ ] Evaluate IControllable/IShip consolidation
- [ ] Consolidate research tracker duplication
- [ ] Extract distance calculation utility
- [ ] Address strategy layer command handler pattern
- [ ] Address strategy layer facility iteration pattern
- [ ] Address strategy layer resource cost pattern

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking window behavior | High | Test each window after refactoring |
| Mixin complexity | Medium | Keep interface simple and focused |
| Performance regression | Low | Profile before and after |

---

## Notes

- The BaseGallery extraction (DUP-UI1-009) is a positive example to follow
- Consider using Protocol for VirtualScrollableList interface
- Filter components should maintain backward compatibility during transition
