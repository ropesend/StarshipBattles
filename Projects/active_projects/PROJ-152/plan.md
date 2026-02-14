# PROJ-152: test_coverage_ui_battle

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-152` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-152 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. UI-Framework | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. UI-Screens | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-02-14 04:04
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-14_031258_sweep_full-codebase-sweep. Total findings selected: 11 (Critical: 0, Major: 7, Other: 4).

## Goals
- Address TCG-UI2-001: Missing Tests for Validation Service Err
- Address TCG-UI1-001: BattleScreen has minimal functional test
- Address TCG-UI1-002: BattleUI panel rendering has no test fil
- Address TCG-UI2-002: BattleUIService Missing Tests for Edge-C
- Address TCG-UI2-003: GameRenderer Missing Tests for Component
- Address TCG-UI1-005: FleetOrdersWindow has no tests
- Address TCG-UI1-007: PlanetListWindow has no direct test file
- Address TCG-UI1-008: EmpirePanelWindow has no tests
- Address TCG-UI1-010: StrategyEventRouter has no tests
- Address TCG-UI1-015: RaceBrowserDialog tests are minimal - on
- ...and 1 more findings

## Scope
**In:**
- game/ui/renderer/game_renderer
- game/ui/screens/battle_screen.
- game/ui/screens/battle_ui.py
- game/ui/screens/empire_panel_w
- game/ui/screens/fleet_orders_w
- game/ui/screens/planet_list_wi
- game/ui/screens/strategy_event
- game/ui/screens/system_selecti
- game/ui/services/battle_ui_ser
- game/ui/services/validation_se
- tests/unit/ui/test_race_browse

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `game/ui/renderer/game_renderer` |
| [TBD] | `game/ui/screens/battle_screen.` |
| [TBD] | `game/ui/screens/battle_ui.py` |
| [TBD] | `game/ui/screens/empire_panel_w` |
| [TBD] | `game/ui/screens/fleet_orders_w` |
| [TBD] | `game/ui/screens/planet_list_wi` |
| [TBD] | `game/ui/screens/strategy_event` |
| [TBD] | `game/ui/screens/system_selecti` |
| [TBD] | `game/ui/services/battle_ui_ser` |
| [TBD] | `game/ui/services/validation_se` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
