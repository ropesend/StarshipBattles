# PROJ-46: Naming Consistency Standardization

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-46` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-46 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quick Wins | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Validator Consolidation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Parameter Naming | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Service Renaming | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Asset Manager Methods | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. UI Directory Consolidation | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Screen Naming | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-01-28 18:45
**Active Phase:** Planning Complete - Ready for Implementation
**Last Action:** Created comprehensive plan with 7 phases
**Next Action:** Begin Phase 1: Quick Wins
**Blockers:** None
**Context for Next Agent:** All 30+ naming issues from findings_05_naming_consistency.md are addressed. User confirmed: (1) Address ALL issues, (2) Consolidate ui/ into game/ui/, (3) Use "Screen" naming convention.

## Overview
This project addresses ALL 30+ naming inconsistencies identified in `findings_05_naming_consistency.md`, consolidates the dual UI directory structure (`ui/` into `game/ui/`), and standardizes UI class naming to "Screen" convention.

## Goals
- Eliminate duplicate ShipDesignValidator classes (NCA-001)
- Standardize `filepath` → `file_path` parameter naming (NCA-002)
- Fix method prefix inconsistencies: `get_*` for I/O → `load_*` (NCA-003)
- Rename calculator-pattern services appropriately (NCA-006, STR-003)
- Consolidate dual UI directory structure (NS-01)
- Standardize UI class naming to "Screen" convention (UI-006)
- Fix boolean method prefixes (NCA-010)
- Standardize type hints to `Optional[T]` style (CORE-007)

## Scope
**In Scope:**
- All Critical issues (NCA-001, NCA-002, NCA-003, NS-01, UI-006)
- All Major issues (NCA-004 through NCA-010, SIM-004, SIM-005, STR-003, UI-007)
- Minor issues (CORE-007, NCA-011)

**Out of Scope:**
- NS-02: Multi-Class Files (test_lab_scene.py has 11 classes - too disruptive)
- NS-03/NS-04: Import Order (use isort tool separately)
- Service Directory Moves (SaveGameService, ResearchService location)
- NCA-012 through NCA-024 (very minor issues, defer)

## Key Files
| Component | File Path |
|-----------|-----------|
| Canonical Validator | `game/simulation/ship_validator.py` |
| Legacy Validator (DELETE) | `game/simulation/systems/validator.py` |
| JSON Utils | `game/core/json_utils.py` |
| Resources | `game/core/resources.py` |
| FleetMobilityService | `game/strategy/services/fleet_mobility_service.py` |
| ShipStatsService | `game/strategy/services/ship_stats_service.py` |
| AssetManager | `game/assets/asset_manager.py` |
| Workshop Screen | `game/ui/screens/workshop_screen.py` |
| Builder Widgets | `game/ui/panels/builder_widgets.py` |
| Resource Manager | `game/simulation/systems/resource_manager.py` |
| Design Library | `game/strategy/systems/design_library.py` |
| Battle Controller | `game/simulation/battle_controller.py` |

## Test Baseline
- **5199 passed, 3 skipped** (established 2026-01-28)
- 1 collection error in test_ship_factory.py (pre-existing, passes in isolation)
- Test impact: ~45 test files, ~330 test methods affected across all phases

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log
- [findings/](findings/) - Swarm agent reports

---

## Phase Summary

### Phase 1: Quick Wins [Simple] - Est. 1-2 hours
Low-risk, immediate-value fixes: type hints, boolean prefixes, backward compat alias.

### Phase 2: Validator Consolidation [Medium] - Est. 1-2 hours
Remove duplicate ShipDesignValidator, update 3 imports, delete legacy file.

### Phase 3: Parameter Naming [Medium] - Est. 2-3 hours
Standardize `filepath` → `file_path` across 14 files, 127 occurrences.

### Phase 4: Service Renaming [Complex] - Est. 2-3 hours
FleetMobilityService → FleetSpeedCalculator, ShipStatsService → ShipStatsCalculator.

### Phase 5: Asset Manager Methods [Simple] - Est. 1 hour
`get_image()` → `load_image()`, `get_group()` → `load_group()`.

### Phase 6: UI Directory Consolidation [Complex] - Est. 3-4 hours
Merge `ui/` into `game/ui/`, update ~40 import statements.

### Phase 7: Screen Naming [Medium] - Est. 2-3 hours
Standardize Scene/Interface/GUI → Screen for all UI classes.

**Total Estimated Effort:** 12-18 hours

---

## Verification Checklist

### Project Start (COMPLETED)
- [x] Run full test suite: `pytest tests/` - baseline established (5199 passed)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Verify no import errors in modified files
- [ ] Update phase status in this document

### Final Verification
- [ ] Run full test suite: `pytest tests/` (NOT --testmon)
- [ ] Manual smoke test: Launch game, use ship builder
- [ ] Manual smoke test: Load/save ship designs
- [ ] Manual smoke test: Run a test battle
- [ ] Manual smoke test: Open strategy map

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-28 | Planning complete | 7 phases defined |

## Completion Checklist
- [ ] Phase 1 complete
- [ ] Phase 2 complete
- [ ] Phase 3 complete
- [ ] Phase 4 complete
- [ ] Phase 5 complete
- [ ] Phase 6 complete
- [ ] Phase 7 complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
