# PROJ-130: test-coverage-core-systems

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-130` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-130 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-02-13 06:11
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-13_sweep_full-codebase-sweep. Total findings selected: 31 (Critical: 2, Major: 13, Other: 16).

## Goals
- Address TCG-FND-001: CollisionSystem raycasting edge cases un
- Address TCG-FND-002: ResearchService leaky bucket algorithm e
- Address TCG-FND-003: AIController navigation and avoidance al
- Address TCG-FND-004: TargetEvaluator rule evaluation missing
- Address TCG-FND-005: Behavior classes missing state transitio
- Address TCG-FND-006: TechTree validation methods lack test co
- Address TCG-FND-007: TechRequirement fuzzy resolution edge ca
- Address TCG-FND-009: SpatialGrid query_radius does not filter
- Address TCG-SIM-004: designs.py Lacks Any Test Coverage
- Address TCG-SIM-005: resource_manager.py (ResourceRegistry) M
- ...and 21 more findings

## Scope
**In:**
- Unknown
- game/ai/behaviors.py
- game/ai/controller.py
- game/ai/interfaces/controllabl
- game/ai/target_evaluator.py
- game/core/config.py
- game/core/error_codes.py
- game/core/hex_math.py
- game/core/logger.py
- game/core/profiling.py
- game/engine/collision.py
- game/engine/physics.py
- game/engine/spatial.py
- game/research/data/tech_node.p
- game/research/data/tech_tree.p
- ...and 13 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `Unknown` |
| [TBD] | `game/ai/behaviors.py` |
| [TBD] | `game/ai/controller.py` |
| [TBD] | `game/ai/interfaces/controllabl` |
| [TBD] | `game/ai/target_evaluator.py` |
| [TBD] | `game/core/config.py` |
| [TBD] | `game/core/error_codes.py` |
| [TBD] | `game/core/hex_math.py` |
| [TBD] | `game/core/logger.py` |
| [TBD] | `game/core/profiling.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
