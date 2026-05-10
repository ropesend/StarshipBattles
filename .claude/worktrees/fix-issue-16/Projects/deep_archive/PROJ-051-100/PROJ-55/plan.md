# PROJ-55: Data-Driven Planet-Specific Colonization System

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-55` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-55 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create ColonizePlanet Ability & Components | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Enhance Validation Layer | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Enhance Execution Layer | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Enhance UI Layer | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Integration & Testing | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-01
**Active Phase:** Phase 5 - Integration & Testing (COMPLETE)
**Last Action:** Fixed critical production code issue where component_registry wasn't passed.
**Next Action:** User re-test to verify colony pod validation now enforced in gameplay.
**Blockers:** None - awaiting user verification

**Context for Next Agent:**

### CRITICAL FIX (This Session)

User testing revealed that validation was NOT being enforced in gameplay despite all
tests passing. Root cause: Production code paths never passed `component_registry` to
validation/execution methods.

**Files Fixed:**
- `game/strategy/engine/turn_engine.py`:
  - `validate_colonize_order()`: Now passes `self._registries.components`
  - `_process_end_turn_orders()`: Now passes `component_registry` to order processor
- `game/strategy/engine/fleet_order_processor.py`:
  - `process_end_turn_orders()`: Updated signature to accept `component_registry`
- `game/strategy/interfaces/engines.py`:
  - `IOrderProcessor`: Updated interface signature
- `tests/unit/strategy/turn_engine/conftest.py`:
  - `mock_fleet`: Added `remove_ship` side_effect to modify ships list
  - Added colony pod data to mock_ship.design_data
- `tests/unit/strategy/mocks/mock_engines.py`:
  - `MockOrderProcessor`: Updated to track component_registry argument

### Test Summary
- Total tests: 6244 passed, 5 skipped
- All tests pass after production fix
- Backward compatibility maintained via `component_registry=None` default

### User Verification Required
**User should re-test colonization in gameplay:**
1. Try to colonize WITHOUT colony pod → Should fail with "No matching colony pod" error
2. Try to colonize with WRONG pod type → Should fail with validation error
3. Colonize with CORRECT pod type → Should succeed, only colony ship removed

## Overview

Transform the colonization system from a simple "any fleet can colonize any planet" mechanic to a sophisticated, data-driven system where ships require planet-type-specific colony components. The system validates colonization chains against available pod inventory and consumes individual colony ships (not entire fleets) on colonization.

## Goals
- Enable planet-type-specific colonization requirements (11 planet types)
- Implement colony pod components as ship components (designed in workshop)
- Support colonization chain queueing with validation against available pods
- Consume individual colony ships on colonization (not entire fleet)
- Make system fully data-driven via components.json for easy modding
- Maintain comprehensive test coverage

## Scope
**In Scope:**
- New `ColonizePlanet` ability with planet_type parameter
- 11 new colony pod components in components.json (one per planet type)
- Enhanced validation: check for matching colony pod, track pod inventory for chains
- Enhanced execution: remove specific ship with pod (not entire fleet)
- UI enhancements: filter planets by available pods, show planet types
- Comprehensive test coverage for new behavior
- Documentation updates

**Out of Scope:**
- Research/tech tree for unlocking colony pods (future enhancement)
- Habitability scoring system (future enhancement)
- Resource specialization by planet type (future enhancement)
- Multi-component requirements (e.g., pod + life support) (future enhancement)
- Colony upgrade/tier system (future enhancement)
- Planetary facility restrictions by planet type (future enhancement)

## Key Files
| Component | File Path |
|-----------|-----------|
| **New Ability** | `game/simulation/components/abilities/colonize.py` |
| **Ability Registry** | `game/simulation/components/abilities/__init__.py` |
| **Components Data** | `data/components.json` |
| **Validation** | `game/strategy/validation/colonize_validator.py` |
| **Execution** | `game/strategy/engine/fleet_order_processor.py` |
| **Fleet Data** | `game/strategy/data/fleet.py` |
| **UI** | `game/ui/screens/strategy_colonization.py` |
| **Planet Data** | `game/strategy/data/planet.py` |
| **Commands** | `game/strategy/engine/commands.py` |

---

## Phases

### Phase 1: Create ColonizePlanet Ability & Components [Simple]
**Objective:** Implement the colony pod ability and define all 11 components in JSON
**Status:** Complete
**Checklist:** [phase_1_checklist.md](phase_1_checklist.md)

**Tasks:**
1. Create `ColonizePlanet` ability class
2. Register ability in ability registry
3. Add 11 colony pod components to components.json
4. Write unit tests for ability

**Estimated Complexity:** Simple - Follows existing ability patterns exactly

### Phase 2: Enhance Validation Layer [Medium]
**Objective:** Add pod detection and chain validation to colonization validator
**Status:** Complete
**Checklist:** [phase_2_checklist.md](phase_2_checklist.md)

**Tasks:**
1. Add pod detection methods to `ColonizeValidator`
2. Add pod inventory tracking methods
3. Modify `validate()` to check for matching pods
4. Modify `validate()` to enforce chain limits
5. Update validation tests

**Estimated Complexity:** Medium - Multiple new methods with logic

### Phase 3: Enhance Execution Layer [Medium]
**Objective:** Change colonization to remove individual ship instead of entire fleet
**Status:** Complete
**Checklist:** [phase_3_checklist.md](phase_3_checklist.md)

**Tasks:**
1. Modify `process_colonize()` to find specific ship with pod
2. Remove individual ship instead of entire fleet
3. Add `Fleet.remove_ship()` method if needed
4. Handle fleet removal if last ship consumed
5. Update execution tests

**Estimated Complexity:** Medium - Core logic change with edge cases

### Phase 4: Enhance UI Layer [Medium]
**Objective:** Filter planet selection by available pods and improve UX
**Status:** Complete
**Checklist:** [phase_4_checklist.md](phase_4_checklist.md)

**Tasks:**
1. Modify `on_colonize_click()` to filter planets by pods
2. Account for committed pods in chain orders
3. Add helpful error messages when no valid targets
4. Display planet types in selection UI
5. Update UI tests

**Estimated Complexity:** Medium - UI logic with multiple states

### Phase 5: Integration & Testing [Simple]
**Objective:** End-to-end testing and regression verification
**Status:** Complete
**Checklist:** [phase_5_checklist.md](phase_5_checklist.md)

**Tasks:**
1. Create comprehensive integration tests
2. Run full test suite (regression check)
3. Manual testing scenarios
4. Fix any discovered issues
5. Update documentation

**Estimated Complexity:** Simple - Testing and verification

---

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - establish baseline

### After Each Phase
- [x] Run `pytest tests/ --testmon` - all affected tests pass
- [x] Manual spot check relevant functionality
- [x] Update Current State section

### Final Verification
- [x] All phase checklists complete (Phases 1-4, Phase 5 in progress)
- [x] All tests passing (full suite, NOT --testmon) - 6244 passed, 5 skipped
- [ ] Manual test: Design colony ship in workshop (USER REQUIRED)
- [x] Manual test: Queue multiple colonizations with validation (AUTOMATED)
- [x] Manual test: Verify only colony ship consumed (AUTOMATED)
- [x] Manual test: UI shows correct planet filtering (AUTOMATED)
- [ ] Audit passed
- [ ] User verified
