# [PROJ-XXX] Consistency Standardization

## Status: Planning
## Created: 2026-02-13
## Source: Sweep 2026-02-13_092036_sweep_full-codebase-sweep

---

## Overview

Standardize coding patterns, naming conventions, and code organization across the codebase to improve readability and reduce cognitive load.

### Problem Statement
The codebase has accumulated inconsistencies over time:
- Mixed naming conventions (is_ vs has_, get_ vs fetch_ vs retrieve_)
- Inconsistent return types for similar operations (None vs empty vs exception)
- Mixed DI patterns (constructor injection vs method injection vs global fallback)
- Varying docstring formats and type hint coverage
- Inconsistent module organization and exports

### Goals
1. Establish and document coding standards
2. Apply consistent naming conventions
3. Standardize return patterns and error handling
4. Improve type hint coverage
5. Standardize module organization

### Success Criteria
- Naming conventions documented and followed
- Return patterns consistent within each layer
- Type hints on all public methods
- Docstrings on all public APIs
- __init__.py exports follow consistent pattern

---

## Design Decisions

### DD-001: Boolean Property Naming
**Decision:** Use `is_` for state, `has_` for possession, `can_` for capability
**Rationale:** Follows Python conventions and improves readability
**Examples:** is_alive, has_weapons, can_move

### DD-002: Method Verb Standardization
**Decision:** Use `get_` for simple retrieval, `find_` for search, `calculate_` for computation
**Rationale:** Consistent verbs communicate intent
**Examples:** get_ship(id), find_ships_by_type(type), calculate_damage()

### DD-003: Return Type for "Not Found"
**Decision:** Return None for single item lookups, empty collection for multi-item lookups
**Rationale:** Matches Python idioms and typing conventions
**Examples:** get_ship(id) -> Optional[Ship], find_ships() -> List[Ship]

### DD-004: Type Hint Style
**Decision:** Use Optional[X] instead of Union[X, None], use | syntax for Python 3.10+
**Rationale:** More readable, follows modern Python conventions
**Examples:** def foo(x: int | None) -> str:

---

## Phases

### Phase 1: Naming Conventions
**Target:** Boolean naming, method verbs, parameter naming, class naming
**Scope:** Establish and apply naming standards
**Tests Required:** None (pure refactoring)

- [ ] Document naming conventions in CLAUDE.md or ARCHITECTURE.md
- [ ] Standardize boolean property names (is_/has_/can_)
- [ ] Standardize method verb prefixes (get_/find_/calculate_)
- [ ] Standardize parameter naming (registry, component, ship_id)
- [ ] Standardize class naming suffixes (Screen, Window, Panel, Manager)

### Phase 2: Return Type Consistency
**Target:** CON-STR-001, CON-SIM-001, CON-UI1-005
**Scope:** Standardize return patterns
**Tests Required:** Update tests for changed signatures

- [ ] Document return type conventions
- [ ] Standardize "not found" returns (None vs empty)
- [ ] Standardize error handling (Result objects vs exceptions)
- [ ] Standardize event handler return types

### Phase 3: Type Hints and Documentation
**Target:** Type hint and docstring findings
**Scope:** Add missing annotations
**Tests Required:** mypy validation

- [ ] Add type hints to singleton classes
- [ ] Add missing return type hints
- [ ] Standardize docstring format (Google style recommended)
- [ ] Add docstrings to undocumented public APIs

### Phase 4: Pattern Standardization
**Target:** DI patterns, initialization, facade patterns
**Scope:** Apply consistent patterns
**Tests Required:** Integration tests

- [ ] Document DI pattern standard (constructor injection)
- [ ] Standardize engine initialization patterns
- [ ] Apply facade pattern consistently in Ship
- [ ] Standardize path construction (pathlib)

### Phase 5: Code Organization
**Target:** Module structure, exports, imports
**Scope:** Standardize organization
**Tests Required:** Import tests

- [ ] Standardize __init__.py export patterns
- [ ] Standardize import organization (stdlib, third-party, local)
- [ ] Extract magic numbers to named constants
- [ ] Remove module-level side effects

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking API changes | Medium | Document changes, deprecate gradually |
| Merge conflicts | Medium | Coordinate with other projects |
| Scope creep | High | Focus on Major findings first |

---

## Notes

- This is a lower-priority project that can be done incrementally
- Many findings are Info-level and can be deferred
- Document standards before enforcing them
- Consider using automated linting (pylint, ruff) to enforce standards
- Some consistency findings (CON-FND-006, CON-FND-013) are marked N/A effort as they're subjective or Python-version dependent
