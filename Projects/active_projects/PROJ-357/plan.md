# PROJ-357: Fleet Aura Provider Identity — Bind to Component, Not Class

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-357` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-357 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Characterization tests | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Provider identity rework | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** 1
**Last Action:** Project scaffolded from realtime-combat tech-debt review finding #2 (P1 correctness).
**Next Action:** Run /claude-proj-start PROJ-357 to expand design + checklists.
**Blockers:** None

## Overview

`FleetAuraManager._recalculate` (`game/simulation/combat/fleet_aura_manager.py:308-327`)
keeps an `AuraProvider` entry alive whenever **any** same-class non-self
ability remains operational on the provider's ship. The provider's originally
recorded `value` is reused regardless of whether the originally-providing
component is still alive. With two same-class providers on one ship,
disabling one component leaves the disabled value still being applied.

This is both a correctness bug and a sign of weak provider identity:
provider records key off `(ship, ability_class_name)` rather than the
specific component / ability instance that contributed the value.

Source: realtime combat tech-debt review finding #2 (P1 correctness).

## Goals
- Provider records carry component identity AND ability identity, not just class name
- `_recalculate` reads live `value` from the live ability instance — no stale cached numbers
- Disabling one same-class provider on a ship removes only that contribution
- Stacking semantics (MAX same group / SUM across groups) preserved bit-for-bit

## Scope
**In:**
- `game/simulation/combat/fleet_aura_manager.py` — `AuraProvider`, `_scan_ship`, `_recalculate`, fingerprint
- New + characterization tests under `tests/unit/simulation/combat/`

**Out:**
- External `ModifierEntry` ingestion (already routed via `KNOWN_EXTERNAL_STAT_KEYS` per PROJ-273)
- `ABILITY_STAT_REGISTRY` typed-contribution refactor (separate concern from provider identity)
- UI display rows for active bonuses

## Key Files
| Component | File Path |
|-----------|-----------|
| Provider record + recalc (bug site) | `game/simulation/combat/fleet_aura_manager.py` |
| Aggregator (preserve contract) | `game/simulation/entities/ability_aggregator.py` |
| Existing aura tests | `tests/unit/simulation/combat/test_fleet_aura_*.py` |
| New characterization tests | `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py` |

## Related Documents
- Review report finding #2: `Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/report.md`
- Pattern: `docs/02_PATTERNS.md` § Ability-Stat Registry (KNOWN_EXTERNAL_STAT_KEYS)

## Verification
- [ ] Two same-class providers on one ship: disabling one removes only that value
- [ ] Disabling the provider ship removes all of its provider entries
- [ ] Single-provider behavior unchanged (regression for existing tests)
- [ ] Fingerprint cache still invalidates on per-component operational changes
- [ ] `python Tools/test_sharded/test_sharded.py` passes
