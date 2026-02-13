# PROJ-118: Test Coverage -- Core and Simulation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-118` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-118 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-02-12 18:39
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-11_sweep_full-codebase-sweep. Total findings selected: 51 (Critical: 8, Major: 22, Other: 21).

## Goals
- Address TCG-FND-001: PhysicsBody.apply_force() and forward_ve
- Address TCG-FND-002: AIController.update() Integration Path N
- Address TCG-FND-003: CollisionSystem.process_beam_attack() Hi
- Address TCG-SIM-001: BattleService has no unit tests
- Address TCG-SIM-002: ProjectileManager has no unit tests
- Address TCG-SIM-003: AbilityAggregator has no unit tests
- Address TCG-SIM-004: ShipPhysicsMixin has no unit tests
- Address TCG-SIM-005: ShipFormation has no unit tests
- Address TCG-FND-004: SpatialGrid.query_radius() Boundary and
- Address TCG-FND-005: AIController._handle_formation_master()
- ...and 41 more findings

## Scope
**In:**
- game/ai/behaviors.py
- game/ai/combat_utils.py
- game/ai/controller.py
- game/ai/strategy_manager.py
- game/ai/target_evaluator.py
- game/core/hex_math.py
- game/core/registry.py
- game/core/strategy_metadata.py
- game/engine/collision.py
- game/engine/physics.py
- game/engine/spatial.py
- game/research/data/research_tr
- game/research/data/tech_node.p
- game/research/systems/research
- game/research/ui/research_cont
- ...and 20 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `game/ai/behaviors.py` |
| [TBD] | `game/ai/combat_utils.py` |
| [TBD] | `game/ai/controller.py` |
| [TBD] | `game/ai/strategy_manager.py` |
| [TBD] | `game/ai/target_evaluator.py` |
| [TBD] | `game/core/hex_math.py` |
| [TBD] | `game/core/registry.py` |
| [TBD] | `game/core/strategy_metadata.py` |
| [TBD] | `game/engine/collision.py` |
| [TBD] | `game/engine/physics.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
