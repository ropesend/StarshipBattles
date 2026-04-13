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
| 1. `SHIELD_BONUS_ADD` additive stat_key + ship-level plumbing | **Complete** | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Both spec compilers emit real stat_keys for all placeholder entries | **Complete** | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Suppressor opponent-team routing | **Complete** | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. End-to-end integration tests + manual smoke | **Complete (pending manual smoke)** | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Evaluate + eliminate legacy `capture_battle_state` | **Complete — Option C (retain + harden)** | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Fix Phase 5 hardening live-path miss (audit C1) | **Complete** | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. FleetAuraManager stack_group respect | **Complete** | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Modifier Visibility in UI | **Complete** | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Resolve `_entries_from_modifier_source` | **Complete (deleted)** | [phase_9_checklist.md](phase_9_checklist.md) |
| 10. Documentation sync (Rule 2) | **Complete** | [phase_10_checklist.md](phase_10_checklist.md) |
| 11. Test hardening | **Complete** | [phase_11_checklist.md](phase_11_checklist.md) |
| 12. Misc cleanup + semantic fixes | **Complete** | [phase_12_checklist.md](phase_12_checklist.md) |

## Current State
**Last Updated:** 2026-04-13 — **ALL 12 PHASES COMPLETE**; only user manual launcher smoke remains
**Active Phase:** Closeout — ready for user's manual smoke + protocol 05 archival
**Last Action:** Phases 6-12 executed in same session as original Phases 1-5 after 4-agent skeptic audit. Findings addressed: C1 Phase 5 live-path miss → Phase 6 (class method narrowed). H1 stack_group ignored → Phase 7 (two-phase MAX/SUM for external entries, 4 new tests incl. integration). H2 UI hides modifiers → Phase 8 (Results shields row + Battle HUD active-modifier labels, 6 new tests). H4 dead-with-landmine → Phase 9 (deleted `_entries_from_modifier_source` + 3 obsolete tests, new compiler-wide placeholder guard). Docs sync → Phase 10 (PROJ-270 Phase 9 bridge documented in `adding_abilities.md` + `02_PATTERNS.md`; 3 new pattern entries; SHIELD_BONUS_ADD in ability reference; "pending PROJ-271" cleared; stale `BattleFactories` ref fixed). Test hardening → Phase 11 (glob survey, whitelist meta-assertion, save/load leak guard, recalculate_stats invocation test). Semantic fix → Phase 12 (flat bonus now scaled by BOTH `capacity_mult` AND `shield_capacity_mult`; dead code deleted). Total across audit follow-up: 20+ new tests.
**Next Action:** User runs manual launcher smoke per original Phase 4.4 script. After smoke confirmation, archive via protocol 05.
**Blockers:** Only user-led manual smoke remains.

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
- Ship-level plumbing: `Ship.recalculate_stats` (or `_compute_max_shields`) reads `ship.external_stats.get('shield_bonus_add', 0.0)` and adds it to max_shields ONCE, not per shield component. Pipeline ordering `(base + flat) × mult` locked by [decisions.md](decisions.md).
- Strategy compiler emits `stat_key="shield_bonus_add"` (not placeholder) for `FleetCombatModifiers.flat_shield_bonus`.
- Battle Setup compiler `_complex_entries`: parse complex design JSON, walk components, extract non-SELF-scoped abilities (`ShieldModifier`, `DamageModifier`, `ShieldProjection`), map ability class → stat_key, route by scope (`enemy_*` → opponent team, else → owner team).
- Scope-driven team routing applies to both compilers. Strategy path already works (via collector); Battle Setup path needs implementation.
- End-to-end integration tests: `test_storm_shield_interference.py` (exists from PROJ-270 Phase 9, verify still green), `test_flat_shield_bonus.py`, `test_suppressor_effects.py`.
- `capture_battle_state` audit + Option B refactor (likely) — 1 live caller in `test_executor.py`; decide retain-refactor vs delete after Task 5.1 audit.
- Manual launcher smoke.

**Out:**
- Any modifier types beyond flat_shield_bonus + scope-driven boosters/suppressors.
- UI changes for modifier visualization (strategy screen sector-panel out of scope).
- Combat Lab modifier wiring (already works via existing pipeline).
- PROJ-270 deferred items (Task 12.3 ComponentStateSpec.is_active, Task 12.4 BoundaryRegion type-split) — separate cleanup projects.

## Key Files

| Component | File Path |
|-----------|-----------|
| StatKey enum + AbilityStatBinding | `game/simulation/components/abilities/stat_keys.py` |
| Ability composition layer (get_effective_stat) | `game/simulation/components/abilities/base.py` |
| Ship stat recalculation | `game/simulation/entities/ship.py` |
| FleetAuraManager (external_stats bridge) | `game/simulation/combat/fleet_aura_manager.py` |
| Strategy compiler | `game/strategy/combat/spec_compiler.py` |
| Battle Setup compiler | `game/ui/screens/battle_setup/spec_compiler.py` |
| Combat modifier collector | `game/strategy/services/combat_modifier_collector.py` |
| ModifierStack | `game/simulation/combat/modifier_stack.py` |
| Regression guards | `tests/unit/simulation/test_unified_entry_guard.py` |
| Integration tests | `tests/integration/strategy/combat/` |
| capture_battle_state (Phase 5) | `combat_lab/battle_state_capture.py` |

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
