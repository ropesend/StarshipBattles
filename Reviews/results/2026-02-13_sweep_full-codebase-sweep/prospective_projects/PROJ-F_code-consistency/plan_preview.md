# PROJ-F: Code Consistency and Duplication Cleanup

## Project Overview

**Goal:** Establish and apply consistent coding conventions across the codebase, and consolidate duplicate code patterns.

**Context:** The codebase has accumulated inconsistencies in naming, patterns, and duplicate code. While individually minor, these issues increase cognitive load.

## Current State

- Mixed naming conventions (Screen vs Scene, Service vs Manager)
- Multiple docstring formats
- Duplicate utility patterns (clamp, font creation, directory creation)
- Magic numbers scattered in code
- Inconsistent import organization

## Target State

- Documented naming conventions
- Single docstring format (Google style)
- Consolidated utility functions
- Magic numbers extracted to constants
- Consistent import organization

## Phases

### Phase 1: Documentation and Standards
**Estimated Duration:** 2 days

#### 1.1 Naming Conventions
- [ ] Document class naming: Manager (stateful) vs Service (stateless) vs System (ECS)
- [ ] Document parameter naming: entity (generic) vs ship (specific) vs target (context)
- [ ] Document method naming: get_ (cached) vs load_ (from disk) vs fetch_ (async)
- [ ] Add to CLAUDE.md

#### 1.2 Code Style
- [ ] Choose docstring format: Google style
- [ ] Choose import organization: stdlib / third-party / local
- [ ] Choose `__all__` placement: after imports
- [ ] Add to CLAUDE.md

#### 1.3 Code Review Checklist
- [ ] Create checklist for PRs
- [ ] Include naming checks
- [ ] Include style checks

### Phase 2: Naming Cleanup
**Estimated Duration:** 3 days

#### 2.1 Class Naming
- [ ] Audit Manager vs Service vs System usage
- [ ] Document intentional exceptions
- [ ] Update misleading names (with care)

#### 2.2 Parameter Naming
- [ ] Audit entity vs ship vs obj usage
- [ ] Standardize in high-traffic modules
- [ ] Document conventions for new code

#### 2.3 Method Naming
- [ ] Audit is_alive() vs is_alive property
- [ ] Standardize boolean access patterns
- [ ] Update interfaces where needed

### Phase 3: Duplication Consolidation
**Estimated Duration:** 4 days

#### 3.1 Utility Functions
- [ ] Review clamp function duplication
- [ ] Create shared clamp in game/core/math.py
- [ ] Update all callers

#### 3.2 UI Patterns
- [ ] Consolidate font creation to FontManager
- [ ] Consolidate directory creation to PathUtils
- [ ] Consolidate placeholder surface creation

#### 3.3 Serialization Patterns
- [ ] Review to_dict/from_dict patterns
- [ ] Consider dataclass-based serialization
- [ ] Document chosen pattern

### Phase 4: Pattern Cleanup
**Estimated Duration:** 3 days

#### 4.1 Docstrings
- [ ] Convert reST docstrings to Google style
- [ ] Add missing docstrings to public APIs
- [ ] Verify consistency

#### 4.2 Error Handling
- [ ] Replace broad except with specific
- [ ] Add logging to silent handlers
- [ ] Document error handling convention

#### 4.3 Magic Numbers
- [ ] Extract magic numbers from AI layer
- [ ] Extract magic numbers from renderer
- [ ] Add to appropriate config classes

#### 4.4 Import Organization
- [ ] Organize imports per PEP 8
- [ ] Remove unused imports
- [ ] Standardize TYPE_CHECKING usage

## Validation

### During Development
- Run linters to verify style
- Run tests after each change
- Review changes in small batches

### Completion Criteria
- [ ] All Major findings addressed (20/20)
- [ ] Conventions documented in CLAUDE.md
- [ ] Code review checklist created
- [ ] Full test suite passes

## Notes

- This is a polish project - lower priority than tests/architecture
- Can be done incrementally over time
- Focus on high-impact, low-risk changes
- Some consistency issues may be intentional
