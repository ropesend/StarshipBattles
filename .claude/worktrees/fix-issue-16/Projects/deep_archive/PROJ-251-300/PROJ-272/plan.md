# PROJ-272: Strategic Modifier System Cleanup + Round-2 Audit Fixes

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-272` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-272 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix `_extract_scope()` default (CRITICAL) | **Complete** | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Reconcile Phase 7 stack_group claim | **Complete** | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. TargetEvaluator projectile guards | **Complete** | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Consecutive-battle external_stats reset | **Complete** | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Delete BattleScreen.start legacy bypass | **Complete** | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Remove capacity_mult time-bomb read | **Complete** | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Remove vestigial strategy compiler kwargs | **Complete** | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Fix `_apply_bonuses` zero-value filter | **Complete** | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Documentation pass (delete duplicate Pattern 26, canonicalize formula, doc UI) | **Complete** | [phase_9_checklist.md](phase_9_checklist.md) |
| 10. Test hardening (3+ teams, destroyed-ship clearing) | **Complete** | [phase_10_checklist.md](phase_10_checklist.md) |
| 11. UX polish (HUD sign-format, non-numeric guard) | **Complete** | [phase_11_checklist.md](phase_11_checklist.md) |

## Current State
**Last Updated:** 2026-04-13 — **ALL 11 PHASES COMPLETE**
**Active Phase:** Closeout — ready for user manual smoke + protocol 05 archival
**Last Action:** 11 phases executed in one continuous session from round-2 audit findings. Phase 1 fixed compiler/runtime scope default disagreement (shared `get_ability_default_scope` helper). Phase 2 reconciled Phase 7 stack_group claim — threaded `stack_group` through strategy compiler (storm + fleet mults now have explicit groups), documented within-source-only limitation. Phase 3 added `is_combat_ship` guards to `TargetEvaluator._eval_has_weapons_rule` + `_eval_least_armor_rule` (projectile crash class eliminated). Phase 4 locked consecutive-battle + destroyed-ship `external_stats` lifecycle. Phase 5 deleted `BattleScreen.start(team0, team1)` + `_build_fallback_outcome` + migrated 2 legacy tests. Phase 6 reverted `capacity_mult` time-bomb read. Phase 7 removed vestigial `sector`/`system` kwargs from strategy compiler. Phase 8 narrowed zero-value filter. Phase 9 deleted duplicate Pattern 26 + canonicalized shield formula + documented Phase 8 UI + multi-team limits. Phase 10 made 2-team assumption LOUD (NotImplementedError). Phase 11 improved HUD sign-format + non-numeric guard. 30+ new tests.
**Next Action:** User-led manual launcher smoke re-verification (Phase 1 + Phase 3 touch live code paths). After smoke confirmation, archive via protocol 05.
**Blockers:** Only user-led manual smoke remains.

## Overview

Round-2 skeptical audit of PROJ-269/270/271 (conducted post-archival on 2026-04-13) surfaced 1 CRITICAL + 6 HIGH + 6 MEDIUM + 3 LOW findings. Issues fall into three buckets: (a) **bugs introduced by PROJ-271 Phase 6-12 fixes themselves** (stack_group unification claim overstated; `capacity_mult` time-bomb), (b) **pre-existing bugs surfaced by deeper inspection** (TargetEvaluator projectile crashes; scope-default silent no-op; BattleScreen legacy bypass), (c) **doc/test hardening gaps** (3+ team behavior; consecutive-battle external_stats leak; documentation holes).

## Goals

- Every CRITICAL + HIGH finding from round-2 audit resolved.
- MEDIUM + LOW findings either resolved or deliberately deferred with documented rationale.
- Phase 7 stack_group claim in `FleetAuraManager` either delivered fully OR documented as within-source-only.
- TargetEvaluator survives mixed ship/projectile candidate lists without silent-drop.
- External_stats lifecycle locked: reset between battles + cleared on destruction + never serialized.
- Docs reflect reality: no duplicate patterns, one canonical shield formula, Phase 8 UI additions documented.

## Scope

**In:**
- Fix C-1 scope-default mismatch in Battle Setup compiler + CombatModifierCollector.
- Fix H1/H3 stack_group propagation (strategy compiler currently hardcodes None; decide on cross-source composition).
- Fix H2 TargetEvaluator projectile-candidate crashes (add `is_combat_ship` guards).
- Add consecutive-battle `external_stats` reset + test.
- Delete `BattleScreen.start(team0, team1)` + `_build_fallback_outcome` (Rule 3 cleanup).
- Remove `capacity_mult` read from ship_stats flat-bonus scaling (time-bomb).
- Remove vestigial `sector`/`system`/`empires` kwargs from `build_strategy_battle_spec`.
- Fix `if v` filter in `_apply_bonuses` (drops legitimate 0.0 entries).
- Doc cleanup: delete duplicate Pattern 26, canonicalize shield formula, document Phase 8 UI + 3+ team behavior.
- Test hardening: 3+ team routing lock, destroyed-ship external_stats guard.
- UX: HUD multiplier sign-format, non-numeric label guard.

**Out:**
- Any new modifier types beyond what PROJ-269/270/271 established.
- Mid-battle destruction of external modifier sources (architectural limitation — Battle Setup complexes aren't ships).
- New Protocol definitions or major refactors beyond what the findings require.

## Key Files

| Component | File Path |
|-----------|-----------|
| Battle Setup compiler | `game/ui/screens/battle_setup/spec_compiler.py` |
| CombatModifierCollector | `game/strategy/services/combat_modifier_collector.py` |
| Strategy compiler | `game/strategy/combat/spec_compiler.py` |
| FleetAuraManager | `game/simulation/combat/fleet_aura_manager.py` |
| Ship stats aggregator | `game/simulation/entities/ship_stats.py` |
| TargetEvaluator | `game/ai/target_evaluator.py` |
| BattleScreen | `game/ui/screens/battle_screen.py` |
| 02_PATTERNS.md | `docs/02_PATTERNS.md` |
| ability_reference.md | `docs/systems/ability_reference.md` |
| Findings reports | `Projects/active_projects/PROJ-272/findings/*_round2.md` |

## Related Documents
- [design.md](design.md) — architectural context for round-2 findings
- [decisions.md](decisions.md) — decisions log
- [findings/code_round2.md](findings/code_round2.md) — code/architecture skeptic report
- [findings/tests_round2.md](findings/tests_round2.md) — test coverage skeptic report
- [findings/docs_round2.md](findings/docs_round2.md) — documentation skeptic report
- [findings/e2e_goals_round2.md](findings/e2e_goals_round2.md) — user-facing goals skeptic report

## Verification
- [ ] All 11 phase checklists complete
- [ ] `pytest tests/` — no net regression vs PROJ-271 baseline of 14698
- [ ] `python -m combat_lab.run_tests --fast --no-history` 162/162 + full 170/170
- [ ] Grep audit: duplicate Pattern 26 removed; single canonical shield formula
- [ ] Manual launcher smoke (re-verify after Phase 1 + Phase 3 fixes — these touch live code paths)
