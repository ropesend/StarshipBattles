# Project Proposal: Code Consistency and Duplication Cleanup

## Summary

**Project ID:** PROJ-F (Prospective)
**Theme:** Consistency Violations and Code Duplication
**Priority:** Low-Medium
**Estimated Effort:** Medium
**Findings Count:** 108

## Problem Statement

The codebase has accumulated inconsistencies in naming conventions, coding patterns, and duplicate code patterns. While these issues are individually minor, collectively they increase cognitive load and maintenance burden.

Categories of issues:
1. **Naming inconsistencies**: Mixed Screen/Scene terminology, inconsistent parameter names
2. **Pattern inconsistencies**: Different docstring formats, mixed error handling
3. **Code duplication**: Repeated patterns that could be consolidated
4. **Magic numbers**: Hardcoded values that should be constants

## Scope

This project consolidates findings from:
- Consistency Violations (CON) across all shards
- Duplication & Fragmentation (DUP) across all shards
- Various Unknown (UNK) minor findings related to consistency

### Key Areas

**Naming Consistency:**
- Class naming suffixes (Service vs Manager vs System)
- Parameter naming (entity vs ship vs obj)
- Method naming (is_alive() vs is_alive property)

**Pattern Consistency:**
- Docstring format (Google vs reST)
- Error handling (broad except vs specific)
- Import organization
- `__all__` export patterns

**Code Duplication:**
- Clamp function duplication
- Entity position access patterns
- Serialization to_dict/from_dict patterns
- Font creation throughout UI
- Directory creation patterns

## Findings Included

### Consistency Findings (38)
| ID Range | Count | Theme |
|----------|-------|-------|
| CON-FND-* | 18 | Foundation consistency |
| CON-UI2-* | 18 | UI Framework consistency |
| CON-SIM-* | N/A | (Covered in other projects) |
| CON-STR-* | N/A | (Covered in other projects) |

### Duplication Findings (26)
| ID Range | Count | Theme |
|----------|-------|-------|
| DUP-FND-* | 8 | Foundation duplication |
| DUP-STR-* | 11 | Strategy duplication |
| DUP-UI2-* | 12 | UI Framework duplication |

### Other Consistency Findings (44)
| ID Range | Count | Theme |
|----------|-------|-------|
| NC-* | 3 | Naming conventions |
| SP-* | 3 | Structure patterns |
| API-* | 3 | API consistency |
| PP-* | 5 | Programming patterns |
| MOD-* | 4 | Module organization |
| Various UNK | ~25 | Miscellaneous |

## Overlap Analysis

No direct overlap with existing projects. This is a polish/cleanup project that can run independently.

## Success Criteria

1. Consistent naming conventions documented and applied
2. Single docstring format adopted
3. Major duplication patterns consolidated
4. Magic numbers extracted to named constants
5. Code review checklist created for future PRs

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Large scope with many small changes | Batch by theme, not severity |
| Breaking changes from renames | Use IDE refactoring tools |
| Low ROI for effort | Focus on highest-impact items |

## Recommended Phases

### Phase 1: Documentation and Standards (Days 1-2)
- Document naming conventions in CLAUDE.md
- Choose docstring format (Google style)
- Define return semantics convention
- Create code review checklist

### Phase 2: Naming Cleanup (Days 3-5)
- Standardize class suffixes where agreed
- Standardize parameter names in new code
- Document existing exceptions

### Phase 3: Duplication Consolidation (Days 6-9)
- Create shared clamp utility
- Consolidate font creation
- Consolidate directory creation
- Create serialization helpers

### Phase 4: Pattern Cleanup (Days 10-12)
- Standardize docstring format
- Add specific exception handling
- Organize imports consistently
- Extract magic numbers

## Dependencies

- Should run after other projects to avoid churn
- Can be done incrementally over time
- Low priority compared to test coverage and architecture
