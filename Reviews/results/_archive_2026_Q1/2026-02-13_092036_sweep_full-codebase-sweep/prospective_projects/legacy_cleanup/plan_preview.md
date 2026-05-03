# [PROJ-XXX] Legacy Code Cleanup

## Status: Planning
## Created: 2026-02-13
## Source: Sweep 2026-02-13_092036_sweep_full-codebase-sweep

---

## Overview

Remove dead code, complete incomplete migrations, and eliminate defensive patterns from old systems following the project policy of "eradicating old systems completely."

### Problem Statement
The codebase contains various legacy holdovers:
- Empty factory module kept "for potential future use" (violates policy)
- Incomplete migration stubs that don't actually do anything
- getattr/hasattr defensive patterns on attributes that should always exist
- Global registry fallback patterns that mask DI failures
- Stale comments referencing completed projects

### Goals
1. Delete all clearly dead code (empty modules, unused methods)
2. Complete or properly document incomplete migration stubs
3. Remove defensive patterns, ensuring attributes always exist
4. Remove global registry fallbacks, require proper DI
5. Remove stale comments and outdated documentation

### Success Criteria
- No empty modules or packages
- No defensive getattr on known attributes
- No global registry fallbacks (all DI explicit)
- No stale project references in comments
- All existing tests pass

---

## Design Decisions

### DD-001: Defensive Pattern Removal Strategy
**Decision:** Verify attribute always exists, then remove getattr; don't add fallback values
**Rationale:** If attribute should exist, masking its absence hides bugs
**Alternatives considered:** Keep defensive patterns (rejected - per CLAUDE.md policy)

### DD-002: Registry Fallback Removal
**Decision:** Remove fallbacks and require explicit DI
**Rationale:** Fallbacks mask misconfiguration; explicit DI is more maintainable
**Alternatives considered:** Keep as safety net (rejected - per CLAUDE.md policy)

### DD-003: Incomplete Migration Handling
**Decision:** Either complete implementation or document as intentional no-op
**Rationale:** Stub methods that do nothing are confusing
**Alternatives considered:** Leave as-is (rejected - creates false expectations)

---

## Phases

### Phase 1: Dead Code Removal
**Target:** LEG-SIM-001, LEG-UI2-003, LEG-UI2-004, LEG-UI1-005, stale comments
**Scope:** Remove clearly unused code
**Tests Required:** Verify removal doesn't break tests

- [ ] Delete game/simulation/factories/ directory
- [ ] Remove unused IBattleUI import
- [ ] Remove unused get_ships_folder method
- [ ] Address stub methods with pass statements
- [ ] Remove stale PROJ-106 comments
- [ ] Remove stale PROJ-40 comments
- [ ] Remove "legacy dispatch" comments
- [ ] Update stale docstrings

### Phase 2: Defensive Pattern Cleanup - Simulation
**Target:** LEG-SIM-003, LEG-SIM-004, LEG-SIM-005, LEG-SIM-006
**Scope:** Clean simulation layer defensive patterns
**Tests Required:** Add tests for edge cases before removing patterns

- [ ] Audit getattr usage on Ship attributes
- [ ] Remove hasattr checks for ability_instances
- [ ] Verify no V1 modifiers exist, remove V1 check
- [ ] Audit Projectile callers for string type usage
- [ ] Add assertions for required attributes

### Phase 3: Defensive Pattern Cleanup - UI
**Target:** LEG-FND-002, LEG-UI2-006, LEG-UI2-007, LEG-UI1-010
**Scope:** Clean UI layer defensive patterns
**Tests Required:** Verify attribute presence before removing patterns

- [ ] Refactor combat_utils defensive patterns
- [ ] Clean battle_ui_service getattr patterns
- [ ] Clean battle_ui_service hasattr patterns
- [ ] Clean empire_panel_window getattr patterns
- [ ] Remove mock detection hasattr if not needed

### Phase 4: Registry Fallback Removal
**Target:** LEG-UI2-001, LEG-UI2-002, LEG-UI2-005
**Scope:** Remove global registry fallback patterns
**Tests Required:** Verify all callers provide registry

- [ ] Remove fallback in ShipFactory
- [ ] Remove fallback in ComponentService
- [ ] Remove fallback in DesignLoaderAdapter
- [ ] Update all callers to provide registry
- [ ] Verify test fixtures provide registry

### Phase 5: Incomplete Migrations
**Target:** LEG-SIM-002, LEG-UI1-001, LEG-UI1-002, LEG-UI1-003, LEG-UI1-008
**Scope:** Complete or document incomplete migrations
**Tests Required:** Tests for new implementations

- [ ] Complete or document apply_results() stub
- [ ] Remove legacy single-selection fields
- [ ] Remove backward compatibility property
- [ ] Remove legacy API method
- [ ] Remove fallback chains in workshop

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Removing used "dead" code | High | Search for all usages before deletion |
| Breaking edge cases with pattern removal | Medium | Add tests before removing patterns |
| Registry issues after fallback removal | Medium | Update all call sites systematically |

---

## Notes

- Some complex items (LEG-FND-003 singleton pattern, LEG-UI1-006/007 hasattr checks) are deferred as project-wide changes
- LEG-UI1-011 (dual-path Ship/DTO) is blocked by PROJ-41
- LEG-UI1-012 (build queue fallback) may be intentional - needs investigation
- Coordinate with other projects that may depend on fallback patterns
