# Plan: Consistency Standardization

## Project Information
- **Project ID:** TBD (will be assigned on creation)
- **Created:** 2026-02-14
- **Source:** Sweep 2026-02-14_031258

## Objective

Establish and enforce consistent coding conventions across the codebase.

## Current State

- Mixed return conventions for not-found cases
- Inconsistent method verb prefixes
- Mixed docstring styles
- Magic numbers scattered throughout UI
- Inconsistent boolean naming
- Mixed singleton vs DI patterns

## Target State

- Documented conventions for all patterns
- Consistent return types (None vs raise vs Optional documented)
- Standard method verb prefixes (get_, load_, fetch_ defined)
- Single docstring format
- Magic numbers extracted to constants
- Boolean names use is_/has_/can_ prefixes

## Phases

### Phase 1: Document Conventions
**Deliverable:** CONVENTIONS.md in docs/

**Contents:**
- Return type conventions for not-found
- Method verb prefix meanings
- Boolean naming requirements
- Docstring format specification
- Import organization rules
- Error handling patterns

### Phase 2: Critical Return Type Fixes
**Files to modify:**
- `game/simulation/services/` - standardize not-found returns
- `game/strategy/services/` - standardize not-found returns

**Rule:** Methods that may not find items should:
- Return `Optional[T]` and return `None`
- OR raise `NotFoundError` (document which)

### Phase 3: Method Verb Standardization
**Focus areas:**
- `get_` - retrieve from cache/memory
- `load_` - retrieve from disk/external
- `fetch_` - retrieve from network (if used)
- `find_` - search with possible failure

**Files to audit:**
- game/strategy/ loading methods
- game/simulation/ query methods

### Phase 4: Boolean Naming
**Focus areas:**
- Rename boolean parameters to is_/has_/can_ prefix
- Rename boolean attributes consistently
- Update all call sites

### Phase 5: UI Magic Numbers
**Files to modify:**
- Extract magic numbers to UIConfig
- game/ui/renderer/ constants
- game/ui/screens/ layout values
- game/strategy/formulas/ magic numbers

### Phase 6: Docstring Standardization
**Choose and enforce:**
- Google style OR NumPy style
- Add to linting rules
- Update existing docstrings incrementally

## Checklist

### Phase 1: Documentation
- [ ] Create docs/CONVENTIONS.md
- [ ] Document return type rules
- [ ] Document verb prefix meanings
- [ ] Document boolean naming
- [ ] Document docstring format

### Phase 2: Return Types
- [ ] Audit simulation services
- [ ] Audit strategy services
- [ ] Add type hints where missing
- [ ] Standardize return patterns

### Phase 3: Verb Prefixes
- [ ] Create inventory of methods
- [ ] Categorize by intended meaning
- [ ] Rename inconsistent methods
- [ ] Update callers

### Phase 4: Boolean Names
- [ ] Find boolean parameters without prefix
- [ ] Rename with is_/has_/can_
- [ ] Update call sites

### Phase 5: Magic Numbers
- [ ] Identify UI magic numbers
- [ ] Add to UIConfig
- [ ] Replace inline values
- [ ] Identify strategy magic numbers
- [ ] Extract to constants

### Phase 6: Docstrings
- [ ] Choose style
- [ ] Update linting config
- [ ] Update high-priority files
- [ ] Document incremental approach

## Dependencies

- None - can run independently but large scope

## Risks

- Large scope may require phasing
- Some inconsistencies may be intentional
- API changes may affect many callers
