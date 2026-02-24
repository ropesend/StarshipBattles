# PROJ-167: Centralize UI Color Palette Constants

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-167` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-167 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Ability Color Hint Constants | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Ability Files Migration | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Test Assertions Update | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Layer Color Consolidation | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Verification & Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Active Phase:** Phase 3 Complete
**Last Action:** Updated 8 test files to use imported ui_colors constants instead of hardcoded hex strings
**Next Action:** Begin Phase 4 — UI layer color consolidation
**Blockers:** None
**Baseline:** 12,016 passed, 1 skipped

## Overview
Centralize all hardcoded color values across the codebase into named constants. This eliminates 51+ inline hex color strings in ability files and 200+ inline RGB tuples in UI panels/renderers. Two central files respect the layer boundary: ability hint colors in the simulation layer, UI rendering colors in the UI layer.

## Goals
- Eliminate all hardcoded color literals from ability `get_ui_rows()` methods
- Eliminate hardcoded color literals from UI panels, renderers, and screens
- Single source of truth for each semantic color value
- No new cross-layer imports; respect existing architecture
- All existing tests continue to pass

## Scope
**In:**
- All `color_hint` hex strings in `game/simulation/components/abilities/*.py` (25 unique, 51 references)
- Hardcoded hex colors in `game/ui/screens/builder/detail_panel.py` (5 colors)
- Hardcoded RGB tuples in UI panels: battle_panels, ship_stats_renderer, ship_detail_panel, design_stats_panel, design_report_panel, planet_report_panel, build_queue_portraits, strategy_widgets
- Hardcoded RGB tuples in renderers: game_renderer, setup_renderer, formation renderer
- Hardcoded colors in research UI: research_renderer, research_controls, research_scene
- Hardcoded colors in test_lab screens
- Hardcoded colors in galaxy_test screens
- Test assertions referencing hardcoded color values (27 color_hint + additional RGB assertions)

**Out:**
- Dynamic/computed colors (color interpolation, alpha blending)
- Colors defined in JSON theme files
- Star color mappings (data-driven, loaded from asset files)
- Player/empire colors (user-configured at runtime)
- `game/ui/colors.py` existing COLORS dict entries (already centralized)
- Electromagnetic spectrum and gas composition colors in strategy_widgets (domain data, not UI theme)

## Key Files
| Component | File Path |
|-----------|-----------|
| **NEW** Ability hint colors | `game/simulation/components/abilities/ui_colors.py` |
| Existing UI colors | `game/ui/colors.py` |
| Ability base class | `game/simulation/components/abilities/base.py` |
| Detail panel (consumer) | `game/ui/screens/builder/detail_panel.py` |
| Weapons abilities | `game/simulation/components/abilities/weapons.py` |
| Defense abilities | `game/simulation/components/abilities/defense.py` |
| Propulsion abilities | `game/simulation/components/abilities/propulsion.py` |
| Crew abilities | `game/simulation/components/abilities/crew.py` |
| Cargo abilities | `game/simulation/components/abilities/cargo.py` |
| Resources abilities | `game/simulation/components/abilities/resources.py` |
| Markers abilities | `game/simulation/components/abilities/markers.py` |
| Harvester abilities | `game/simulation/components/abilities/harvester.py` |
| Superweapons abilities | `game/simulation/components/abilities/superweapons.py` |
| Colonize abilities | `game/simulation/components/abilities/colonize.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis, color palette reference, aliasing table
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Create Ability Color Hint Constants [Simple]
**Objective:** Create `ui_colors.py` with all 25 named constants
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Phase 2: Migrate Ability Files to Constants [Medium]
**Objective:** Replace all 51 inline hex strings in 11 ability files + detail_panel.py with constant imports
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Phase 3: Update Test Assertions [Simple]
**Objective:** Update 27+ test assertions to use imported constants instead of hardcoded hex strings
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

### Phase 4: UI Layer Color Consolidation [Complex]
**Objective:** Add categorized constants to `game/ui/colors.py` and update UI files
**Status:** Not Started

See [phase_4_checklist.md](phase_4_checklist.md) for detailed tasks.

### Phase 5: Verification & Cleanup [Simple]
**Objective:** Full test suite, grep for remaining hardcoded colors, final audit
**Status:** Not Started

See [phase_5_checklist.md](phase_5_checklist.md) for detailed tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` - 11,994 passed, 1 skipped (baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Grep for remaining hardcoded hex colors in modified files

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] `grep -r "color_hint.*'#" game/simulation/` returns only ui_colors.py
- [ ] No new imports crossing the simulation→ui boundary
- [ ] Visual spot-check: open builder, inspect component detail panel colors

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All tests passing (11,994+)
- [ ] Audit passed
- [ ] User verified
