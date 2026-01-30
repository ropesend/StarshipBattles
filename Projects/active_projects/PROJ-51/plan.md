# PROJ-51: Naming Consistency Remediation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-51` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-51 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Validation Consolidation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. UI File Naming | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. InputHandler Rename | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Stats Service Location | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Verification & Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-30
**Active Phase:** Phase 2 Complete - Ready for Phase 3
**Last Action:** Renamed *_scene.py to *_screen.py, *Interface to *UI (19 files updated)
**Next Action:** Begin Phase 3 - InputHandler Rename (input_handler.py -> battle_input_handler.py)
**Blockers:** None

## Overview
Resolve 4 naming consistency issues identified in the 2026-01-30 Naming Verification Review. This project addresses file/class naming mismatches, consolidates validation logic, and standardizes input handler naming patterns.

**Source Review:** [2026-01-30_consistency_naming_verification](../../../Reviews/results/2026-01-30_consistency_naming_verification/report.md)

## Goals
- Move `ship_validator.py` into dedicated `validation/` directory (NCA-008)
- Rename `*_scene.py` files to `*_screen.py` to match class names (UI-006)
- Rename `InputHandler` to `BattleInputHandler` for consistency (NCA-007)
- Move `stats.py` from `systems/` to `services/` directory (NCA-006)

## Scope
**In:**
- NCA-008: Validation module consolidation
- UI-006: UI file naming (scene -> screen)
- NCA-007: InputHandler -> BattleInputHandler rename
- NCA-006: Stats service relocation

**Out:**
- UI-007: Event handling naming (CLOSED - pattern is correct)
- Other review findings not selected
- New feature development

## Key Files
| Component | Current Path | Target Path |
|-----------|--------------|-------------|
| ShipDesignValidator | `game/simulation/ship_validator.py` | `game/simulation/validation/ship_validator.py` |
| BattleScreen | `game/ui/screens/battle_scene.py` | `game/ui/screens/battle_screen.py` |
| StrategyScreen | `game/ui/screens/strategy_scene.py` | `game/ui/screens/strategy_screen.py` |
| TestLabScreen | `game/ui/screens/test_lab_scene.py` | `game/ui/screens/test_lab_screen.py` |
| BattleInterface | `game/ui/screens/battle_screen.py` | `game/ui/screens/battle_ui.py` |
| StrategyInterface | `game/ui/screens/strategy_screen.py` | `game/ui/screens/strategy_ui.py` |
| BattleInputHandler | `game/core/input_handler.py` | `game/ui/screens/battle_input_handler.py` |
| ShipStatsCalculator | `game/simulation/systems/stats.py` | `game/simulation/services/stats.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/`)
- [ ] Manual verification: Battle, Strategy, Test Lab, Ship Design
- [ ] Audit passed
- [ ] User verified
