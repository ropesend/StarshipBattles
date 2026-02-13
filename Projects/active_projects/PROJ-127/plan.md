# PROJ-127: code-duplication-reduction

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-127` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-127 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strategy | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI-Framework | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Other | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-13 06:11
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-13_sweep_full-codebase-sweep. Total findings selected: 36 (Critical: 0, Major: 11, Other: 25).

## Goals
- Address DUP-FND-001: Entity Position/State Access Patterns in
- Address DUP-SIM-001: Serialization to_dict/from_dict Pattern
- Address DUP-SIM-002: Resource Ability Classes Share Identical
- Address DUP-SIM-003: Team Iteration Pattern Duplicated in Bat
- Address DUP-STR-001: Build Queue Source Collection - Near-Ide
- Address DUP-STR-002: Facility Shipyard Detection - Duplicated
- Address DUP-STR-003: Mission Command Handler Duplication
- Address DUP-STR-004: `to_dict` / `from_dict` Boilerplate Patt
- Address DUP-STR-005: Fleet Resolution Pattern in Command Hand
- Address DUP-STR-006: ColonizeValidator Colony Pod Iteration P
- ...and 26 more findings

## Scope
**In:**
- Unknown
- game/ai/behaviors.py
- game/ai/combat_utils.py
- game/research/data/research_tr
- game/research/data/tech_tree.p
- game/simulation/battle_state.p
- game/simulation/components/abi
- game/simulation/components/mod
- game/simulation/managers/retre
- game/simulation/projectile_man
- game/simulation/systems/battle
- game/strategy/data/build_queue
- game/strategy/engine/superweap
- game/strategy/formulas/habitab
- game/strategy/services/compone
- ...and 6 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `Unknown` |
| [TBD] | `game/ai/behaviors.py` |
| [TBD] | `game/ai/combat_utils.py` |
| [TBD] | `game/research/data/research_tr` |
| [TBD] | `game/research/data/tech_tree.p` |
| [TBD] | `game/simulation/battle_state.p` |
| [TBD] | `game/simulation/components/abi` |
| [TBD] | `game/simulation/components/mod` |
| [TBD] | `game/simulation/managers/retre` |
| [TBD] | `game/simulation/projectile_man` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
