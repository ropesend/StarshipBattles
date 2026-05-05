# PROJ-360: ShipStatsCalculator — Decompose by Stat Domain

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-360` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-360 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Golden output tests for representative ships | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract domain contributors behind current API | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Replace hardcoded ability-name checks with registered contributors | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-05
**Active Phase:** 3
**Last Action:** Phase 2 complete — `ship_stats.py` now 486 LOC (under 500), domain contributors live in `game/simulation/entities/stat_contributors/{movement,defense,weapons,command,launch}.py`. Golden tests bit-identical; sharded suite 17702/17698 passed (+37 new contributor tests).
**Next Action:** Phase 3 — replace hardcoded ability-name string checks with a registered-contributor pattern; add the extension acceptance test.
**Blockers:** None

## Overview

`ShipStatsCalculator.calculate()` (`game/simulation/entities/ship_stats.py:111`)
runs many mutable phases and hardcodes ability-name string checks for
movement, shields, regeneration, launch capacity, multiplex tracking, armor,
command priority, and engine priority. The file is 643 LOC, over the
production 500 LOC convention. Adding a new stat or ability class means
editing a broad single-source-of-truth file that already owns multiple
unrelated concerns.

Decompose by stat domain (movement, defense, weapons, command, launch),
convert hardcoded ability-name checks into registered contributors, and
preserve the current output contract via golden tests written first.

Note: this project consciously sequences AFTER PROJ-359 (typed weapon
contract). Some weapon/defense contributors may want to consume the typed
contract once it lands.

Source: realtime combat tech-debt review finding #5 (P2 maintainability).

## Goals
- `ship_stats.py` drops below 500 LOC by extracting domain contributors
- Hardcoded ability-class string checks replaced with a contributor registry
- A new stat contributor can be added without editing unrelated stat domains
- Output of `ShipStatsCalculator.calculate(ship)` is bit-identical for representative ship designs across the migration

## Scope
**In:**
- `game/simulation/entities/ship_stats.py` — split into domain modules
- New domain contributor modules (e.g., `game/simulation/entities/stat_contributors/`)
- Tests under `tests/unit/simulation/entities/`

**Out:**
- `ship_design_stats.py` (separate calculator with its own complexity score — could be a follow-up project)
- `combat_endurance.py` (separate complexity hotspot — follow-up if warranted)
- Ability-stat registry (`ABILITY_STAT_REGISTRY`) — already centralized by PROJ-273
- Splitting `planetary.py` (related #6 finding — separate / opportunistic)

## Key Files
| Component | File Path |
|-----------|-----------|
| Monolithic calculator | `game/simulation/entities/ship_stats.py` |
| Ability-stat registry (reuse) | `game/simulation/combat/ability_stat_registry.py` |
| Contributor modules (new) | `game/simulation/entities/stat_contributors/*.py` |
| Golden tests (new) | `tests/unit/simulation/entities/test_ship_stats_golden.py` |
| Domain tests (new) | `tests/unit/simulation/entities/stat_contributors/test_*.py` |

## Phasing Notes
Phase 1 establishes a golden snapshot of `calculate()` output for a representative
set of ship designs (small/medium/large, with shields, with hangar, with armor)
to lock current behavior. Phase 2 extracts contributors behind the existing
public API without changing semantics. Phase 3 replaces hardcoded ability-name
branches with registered contributors and verifies golden output still matches.

## Related Documents
- Review report finding #5: `Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/report.md`
- Convention: AGENTS.md § Key Conventions (500 LOC ceiling for `game/`)
- Pattern: `docs/02_PATTERNS.md` § Ability-Stat Registry

## Verification
- [ ] Golden output tests pass on current main (snapshot baseline)
- [ ] After decomposition, golden output still matches bit-for-bit
- [ ] `ship_stats.py` is under 500 LOC
- [ ] A fake test contributor can be added without editing unrelated domains
- [ ] `python Tools/test_sharded/test_sharded.py` passes
