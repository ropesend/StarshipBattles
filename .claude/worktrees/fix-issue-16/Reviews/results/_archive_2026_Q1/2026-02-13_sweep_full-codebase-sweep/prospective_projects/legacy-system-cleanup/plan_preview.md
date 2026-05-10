# Project Plan: Legacy System Cleanup

## Project Metadata

- **Project ID:** PROJ-XXX
- **Title:** Legacy System Cleanup
- **Status:** Planning
- **Created:** 2026-02-13
- **Source:** Sweep 2026-02-13_sweep_full-codebase-sweep

## Overview

This project addresses 20 legacy system findings from the codebase sweep. Following the project's "System Migration Policy", the primary goals are:

1. Remove explicit "legacy behavior" branches
2. Remove backward compatibility code for save files
3. Clean up dead code and unused patterns
4. Modernize legacy patterns to use DI

## Phases

### Phase 1: Strategy Engine Legacy Branches

**Objective:** Remove "legacy behavior" branches in core engine code.

**Tasks:**
- [ ] Update callers to always pass component_registry to FleetOrderProcessor (LEG-STR-001)
- [ ] Update tests to register fleets with Galaxy, remove O(n) fallback (LEG-STR-002)
- [ ] Verify no legacy queue items exist, remove dual code paths (LEG-STR-003)

**Estimated Effort:** 3-4 days

### Phase 2: Save File Compatibility Removal

**Objective:** Remove save file compatibility code per disposal policy.

**Tasks:**
- [ ] Remove backward compat default in Planet.from_dict (LEG-STR-005)
- [ ] Remove old layer format handling in DesignMetadata (LEG-STR-007)
- [ ] Remove sprite_preview compatibility field (LEG-STR-008)
- [ ] Remove module identity fallback (LEG-SIM-006)
- [ ] Remove ability index fallback (LEG-SIM-007)

**Estimated Effort:** 2-3 days

### Phase 3: Dead Code Removal

**Objective:** Remove unused code.

**Tasks:**
- [ ] Remove unused AI_STATE_ERROR ErrorCode (LEG-FND-005)
- [ ] Evaluate ModifierEditorPanel - remove or modernize (LEG-UI2-004)
- [ ] Evaluate TechPresetLoader usage (LEG-SIM-009)

**Estimated Effort:** 1-2 days

### Phase 4: Pattern Modernization

**Objective:** Update legacy patterns to modern approaches.

**Tasks:**
- [ ] Standardize ship adapter access in behaviors.py (LEG-FND-003)
- [ ] Replace excessive getattr() patterns (LEG-UI2-003)
- [ ] Audit singleton patterns for DI conversion (LEG-FND-004)

**Estimated Effort:** 2-3 days

### Phase 5: Cleanup

**Objective:** Address remaining minor items.

**Tasks:**
- [ ] Evaluate if project_path_as_dicts is still needed (LEG-STR-004)
- [ ] Update test mocks to implement interfaces (LEG-STR-009)
- [ ] Evaluate camera hasattr() check (LEG-UI2-006)

**Estimated Effort:** 1 day

## Success Criteria

1. All MAJOR legacy branches removed
2. All backward compatibility code for save files removed
3. No explicit "legacy behavior" comments remaining
4. Dead code removed
5. Test suite passes after all changes

## Dependencies

- May need coordination with test coverage projects if removing code affects test infrastructure

## Risks

- Removing backward compatibility may require updating some tests
- Singleton-to-DI conversion may have broad impact
