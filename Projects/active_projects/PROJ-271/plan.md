# PROJ-271: Strategic Modifier Battle-Math Track B

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-271` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-271 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. `SHIELD_BONUS_ADD` additive stat_key + `AbilityStatBinding` | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Spec compiler emits real stat_key for `flat_shield_bonus` | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Suppressor opponent-team routing | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. End-to-end integration tests + manual smoke | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-12 — Scaffold created as successor to PROJ-270 Track A
**Active Phase:** Phase 1 — `SHIELD_BONUS_ADD` stat_key wiring
**Last Action:** Project scaffold written as part of PROJ-270 closure. No implementation yet.
**Next Action:** Begin Phase 1 — add `SHIELD_BONUS_ADD` stat_key + `AbilityStatBinding` for ADD-operation shield bonuses. Write failing unit tests first (TDD Rule 1).
**Blockers:** None — PROJ-270 Track A complete, all pre-requisites met.

## Overview

PROJ-270 Phase 6 (Track A) restored the **multiplier-based** strategic modifiers that silently regressed after PROJ-269 Phase 5.5's "placeholder effects silently skipped" decision: storm `shield_capacity_mult`, fleet `shield_mult`, fleet `damage_mult`. **Track B** is the successor scope: the **additive** shield bonus (`flat_shield_bonus`) and **opponent-team-routed** modifiers (suppressors) that were explicitly deferred per PROJ-270 [decisions.md](../PROJ-270/decisions.md) Decision 1 because they required new architectural wiring (new stat_key for additive ops; cross-team modifier routing).

## Goals

- `flat_shield_bonus` from planet-level `FleetCombatModifiers` applies to ship `max_shields` via a new `SHIELD_BONUS_ADD` additive stat_key. End-to-end: planet spec → `build_strategy_battle_spec` → `ModifierStack` entry → `FleetAuraManager._append_external_from_entry` → `AbilityStatBinding` → ship has the bonus.
- Suppressor effects (opponent-team debuffs — e.g., "enemy ships in this hex have -20% damage") route via `ModifierStack.per_team[opponent_id]` and apply to the right team in `FleetAuraManager`.
- Integration tests (real ships, real battles) prove Track A + Track B modifiers work end-to-end, including the `test_storm_shield_interference.py` test deferred from PROJ-270 Task 6.5.
- No placeholder stat_keys remain in the strategy compiler for these modifier types.

## Scope

**In:**
- New `SHIELD_BONUS_ADD` entry on `StatKey` enum with `operation=ADD`, `target_attribute="max_shields"`, `base_attribute="base_max_shields"`.
- New `AbilityStatBinding` mapping `SHIELD_BONUS_ADD` onto shield components so `FleetAuraManager` pipeline handles the additive op correctly (precedent: existing `accuracy_add` binding).
- Strategy compiler emits `stat_key="shield_bonus_add"` (not placeholder) for `FleetCombatModifiers.flat_shield_bonus`.
- Suppressor effects route via `ModifierStack.per_team[opponent_id]` — compiler collects opponent planets' auras and targets them at the opponent's team_id.
- End-to-end integration tests: `tests/integration/strategy/combat/test_storm_shield_interference.py` (from PROJ-270 Task 6.5), plus new tests for flat shield bonus and suppressors.
- Manual launcher smoke.

**Out:**
- Any new modifier types beyond flat_shield_bonus + suppressors — if the audit agent identified more, scope them to a future project.
- UI changes for modifier visualization (strategy screen sector-panel is out of scope).
- Combat Lab modifier wiring (already works via existing pipeline).

## Key Files

| Component | File Path |
|-----------|-----------|
| StatKey enum | `game/simulation/components/abilities/stat_keys.py` |
| AbilityStatBinding | `game/modifiers/ability_stat_binding.py` |
| Strategy compiler | `game/strategy/combat/spec_compiler.py` |
| FleetAuraManager | `game/simulation/combat/fleet_aura_manager.py` |
| ModifierStack | `game/simulation/combat/modifier_stack.py` |
| New integration tests | `tests/integration/strategy/combat/` |

## Related Documents
- [design.md](design.md) — architectural analysis of flat-shield-bonus + suppressor wiring
- [decisions.md](decisions.md) — scope decisions and architectural choices
- [PROJ-270/decisions.md](../PROJ-270/decisions.md) — parent Track A decisions (especially Decision 1 which deferred this scope)

## Verification
- [ ] All phase checklists complete
- [ ] All unit tests passing
- [ ] Integration tests in `tests/integration/strategy/combat/` pass
- [ ] Grep audit: strategy compiler emits zero `stat_key="placeholder"` entries for flat_shield_bonus + suppressors
- [ ] Combat Lab fast + full green
- [ ] Manual launcher smoke verified
