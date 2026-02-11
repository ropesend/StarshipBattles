# PROJ-66: Race Setup Enhancement

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-66` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-66 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Data Layer - RaceConfig Enhancement | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Homeworld Presets Data | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Identity Tab UI | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Environment Tab Enhancement | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Aptitudes Tab & Point-Buy System | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Tab Reorganization & Summary Update | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Validation, Fixtures & Integration | Complete | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Audit Complete - Awaiting User Verification
**Last Action:** Audit cycle 1 passed with no significant issues
**Next Action:** User verification required
**Blockers:** None

## Overview
Enhance the Race Setup screen with comprehensive race identity fields (Faction Name, Government Type, Leader Title, Physical Type, Society Type), homeworld type selection that auto-populates environment sliders, water preference sliders, a point-buy aptitude system with exponential tolerance costs, and reorganize from 5 tabs to 7 tabs (Summary, Identity, Visuals, Ships, Environment, Aptitudes, Descriptions).

## Goals
- Add all identity fields (faction name, government type/org, leader title, physical type, society type, race name plural)
- Add homeworld type selection with auto-populated environment presets (all 11 PlanetTypes are habitable)
- Add water preference sliders (ideal + tolerance)
- Build point-buy aptitude system with shared budget for stats and environmental tolerance
- Reorganize UI into 7 clean tabs
- Maintain backward compatibility with existing saved races
- Full TDD with ~65 new tests

## Scope
**In:**
- RaceConfig data model expansion (new fields, serialization, validation)
- Homeworld preset data file and auto-populate logic
- Identity tab with dropdowns and text inputs
- Water sliders on Environment tab
- Aptitudes tab with point-buy budget system
- Tab reorganization (5 → 7)
- Summary panel updates
- Validator updates
- Test fixtures updates
- All associated unit tests

**Out:**
- Gameplay effects of Government Organization / Society Type (stored only, effects in future project)
- Population growth mechanics (future project)
- Environmental compatibility scoring (future project)
- Colonization preference system (future project)
- Changes to PlayerConfig/Empire/SaveGame (only RaceConfig JSON files affected)

## Key Files
| Component | File Path |
|-----------|-----------|
| RaceConfig dataclass | `game/strategy/data/race_config.py` |
| RaceSetupScreen | `game/ui/screens/race_setup_screen.py` |
| RaceEnvironmentPanel | `game/ui/panels/race_environment_panel.py` |
| RaceSummaryPanel | `game/ui/panels/race_summary_panel.py` |
| RaceValidator | `game/ui/screens/race_validator.py` |
| RaceLibrary | `game/strategy/systems/race_library.py` |
| RaceDescriptionPanel | `game/ui/panels/race_description_panel.py` |
| NewGameSetupScreen | `game/ui/screens/new_game_setup_screen.py` |
| Test RaceConfig | `tests/unit/strategy/data/test_race_config.py` |
| Test RaceValidator | `tests/unit/ui/screens/test_race_validator.py` |
| Test Env Panel | `tests/unit/ui/panels/test_race_environment_panel.py` |
| Test Summary Panel | `tests/unit/ui/panels/test_race_summary_panel.py` |
| Test Fixture 1 | `tests/fixtures/quickstart/races/test_emp1.json` |
| Test Fixture 2 | `tests/fixtures/quickstart/races/test_emp2.json` |
| **NEW** Identity Panel | `game/ui/panels/race_identity_panel.py` |
| **NEW** Aptitudes Panel | `game/ui/panels/race_aptitudes_panel.py` |
| **NEW** Homeworld Presets | `game/data/homeworld_presets.json` |
| **NEW** Point Budget | `game/strategy/data/race_point_budget.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phase 1: Data Layer - RaceConfig Enhancement [Medium]
**Objective:** Add all new fields to RaceConfig with serialization, defaults, and validation
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Summary
- Add constant lists (GOVERNMENT_TYPES, LEADER_TITLES, etc.) to race_config.py
- Add all new fields to RaceConfig dataclass
- Update to_dict() / from_dict() with backward-compatible defaults
- Update validate() for new field ranges
- Write comprehensive tests (TDD)

---

## Phase 2: Homeworld Presets Data [Simple]
**Objective:** Create homeworld presets JSON and loading logic
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Summary
- Create `game/data/homeworld_presets.json` mapping PlanetType → environment defaults
- Create loading utility for presets
- Write tests for preset loading and application

---

## Phase 3: Identity Tab UI [Medium]
**Objective:** Build the new Identity tab panel with dropdowns and text inputs
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

### Summary
- Create `RaceIdentityPanel` class following extracted panel pattern
- Add dropdowns for Government Type, Government Org, Leader Title, Physical Type, Society Type
- Add text inputs for Faction Name (auto-generated), Race Name, Race Name Plural
- Implement update_config() / set_from_config() / update_labels()
- Write panel unit tests

---

## Phase 4: Environment Tab Enhancement [Simple]
**Objective:** Add water sliders and homeworld dropdown to the existing Environment tab
**Status:** Not Started

See [phase_4_checklist.md](phase_4_checklist.md) for detailed tasks.

### Summary
- Add homeworld type dropdown to RaceEnvironmentPanel (at top, sets initial values)
- Add water ideal + tolerance sliders
- Implement homeworld preset auto-populate when dropdown changes
- Update existing tests, write new tests

---

## Phase 5: Aptitudes Tab & Point-Buy System [Complex]
**Objective:** Build the point-buy aptitude system with budget tracking
**Status:** Not Started

See [phase_5_checklist.md](phase_5_checklist.md) for detailed tasks.

### Summary
- Create `RacePointBudget` class for cost calculations (exponential tolerance costs)
- Create `RaceAptitudesPanel` with 9 aptitude sliders + environmental tolerance budget
- Display remaining points prominently
- Implement cost calculation: linear for aptitudes, 2^n for tolerance
- Prevent saving when over budget
- Write comprehensive tests for budget math and UI

---

## Phase 6: Tab Reorganization & Summary Update [Medium]
**Objective:** Restructure RaceSetupScreen from 5 tabs to 7 tabs, update Summary panel
**Status:** Not Started

See [phase_6_checklist.md](phase_6_checklist.md) for detailed tasks.

### Summary
- Update TAB constants and TAB_NAMES in RaceSetupScreen
- Move Race Name from Visuals tab to Identity tab
- Insert Identity tab (index 1) and Aptitudes tab (index 5)
- Update _create_step_panels() to create 7 panels
- Update event routing for new tab types (dropdowns)
- Update RaceSummaryPanel to show all new fields
- Update _populate_ui_from_config() for new panels
- Write/update integration tests

---

## Phase 7: Validation, Fixtures & Integration [Medium]
**Objective:** Update validation, test fixtures, and verify end-to-end flow
**Status:** Not Started

See [phase_7_checklist.md](phase_7_checklist.md) for detailed tasks.

### Summary
- Update RaceValidator for new required/optional fields with tab references
- Update test_emp1.json and test_emp2.json with new fields
- Update QuickstartBuilder if needed
- Update NewGameSetupScreen race display (show faction name/government)
- Run full test suite, fix any regressions
- Manual testing of complete race setup flow

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` - baseline: 6244 passed, 2 unrelated failures

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual test race setup screen if UI changes made
- [ ] Verify existing saved races still load (backward compatibility)

### Final Verification
- [ ] Create a new race with all fields populated
- [ ] Save race, reload race, verify all fields preserved
- [ ] Edit existing race, verify all fields load correctly
- [ ] Create new game with configured race, verify game starts
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Verify point-buy budget enforces limits correctly
- [ ] Verify homeworld preset auto-populates environment sliders

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-02-07 | No significant issues - All 7 phases verified | PASSED |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] All Phase 5 tasks checked off
- [x] All Phase 6 tasks checked off
- [x] All Phase 7 tasks checked off
- [x] All tests passing (6290 passed)
- [x] Regression tests passing
- [x] Audit passed (no significant issues)
- [ ] User verified
