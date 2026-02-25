# PROJ-194: Builder & Workshop Duck Typing Elimination

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-194` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-194 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Direct Attribute Access (Ship Properties) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Weapon & Ability Duck Typing | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Workshop Init-Order & Self-Checks | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Resource Accessor Method | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Remaining Scattered Instances | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-25
**Active Phase:** Phase 3 - Workshop Init-Order & Self-Checks
**Last Action:** Phase 2 complete. Replaced ~10 getattr/hasattr on weapon abilities with direct access. Changed hasattr(ab, 'base_accuracy') → has_ability('BeamWeaponAbility'). Removed ability_instances hasattr checks.
**Next Action:** Begin Phase 3
**Blockers:** None

## Overview
Eliminate ~87 hasattr()/getattr() duck typing instances across 21 builder/workshop files.
Most are unnecessary defensive checks where the attribute always exists. Replace with direct
attribute access, proper init declarations, and typed accessor methods where needed.

## Goals
- Remove all unnecessary hasattr/getattr calls in builder/workshop UI code
- Declare all instance attributes in __init__ (no dynamic setattr for button creation)
- Add typed `get_resource_stat()` accessor on Ship for dynamic resource attributes
- Make code portable to statically-typed languages (C#/C++/Rust)

## Scope
**In:**
- `game/ui/screens/builder/` — 12 files, ~57 instances
- `game/ui/screens/workshop_*.py` — 5 files, ~18 instances
- `game/ui/panels/` (builder-related) — 3 files, ~12 instances
- `game/simulation/entities/ship.py` — Add resource accessor method

**Out:**
- Pygame event hasattr checks (`hasattr(event, 'ui_element')`) — framework boundary
- `StatDefinition.get_value()` generic getattr dispatch (lines 29-30) — intentional design
- Non-builder files outside the scope area

## Key Files
| Component | File Path |
|-----------|-----------|
| Stats display | `game/ui/screens/builder/stats_config.py` (20 instances) |
| Weapons ViewModel | `game/ui/screens/builder/weapons_viewmodel.py` (11 instances) |
| Event router | `game/ui/screens/workshop_event_router.py` (9 instances) |
| Right panel | `game/ui/screens/builder/right_panel.py` (7 instances) |
| Design report | `game/ui/panels/design_report_panel.py` (7 instances) |
| Workshop screen | `game/ui/screens/workshop_screen.py` (5 instances) |
| Component palette | `game/ui/screens/builder/components.py` (5 instances) |
| Modifier grid | `game/ui/panels/modifier_impact_grid.py` (3 instances) |
| Layer panel | `game/ui/screens/builder/layer_panel.py` (2 instances) |
| Interaction ctrl | `game/ui/screens/builder/interaction_controller.py` (2 instances) |
| Grouping strategies | `game/ui/screens/builder/grouping_strategies.py` (1 instance) |
| Structure items | `game/ui/screens/builder/structure_list_items.py` (1 instance) |
| Workshop ship IO | `game/ui/screens/workshop_ship_io.py` (1 instance) |
| Ship entity | `game/simulation/entities/ship.py` (add accessor method) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
