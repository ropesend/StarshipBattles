# PROJ-497: ModifierService data-intent decisions: efficient_engines and seeker/beam allowance review

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-497` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-497 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. User-decision gating (block until decisions captured) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Apply approved data edits (TDD) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Doc + decisions update | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Audit remediation (Codex consult 2026-05-23) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Done — all phases complete, audit remediated, awaiting user verification
**Last Action:** Phase 4 audit remediation complete. Task 4.1: TDD-applied endurance reduction (3.0 -> 0.05) at `data/components.json:1079`, yielding effective range = 240 (per user: "close to 200"); 2 new tests in `TestMiniCapitalMissileEffectiveRange`. Task 4.2: `Projects/projects_index.md:8` PROJ-497 status updated `Planning` -> `Awaiting Verification`. Task 4.3: DI-2026-05-23-007 logged for `docs/systems/ability_reference.md:287` (stale "seekers ignore firing arc" claim). Task 4.4: DI-2026-05-23-008 logged for inert `"Weapon"` tokens in `data/modifiers.json:58, 284` (turret_mount, rapid_fire). Full sharded suite stable: **24659 / 24658 passed / 0 failed / 0 errors / 1 skipped**. All four `validate_phase.py` checks PASSED; `validate_close_ready.py` PASSED.
**Next Action:** Project ready for user verification. After user-verified label applied, run archive workflow.
**Blockers:** None.

## Overview
PROJ-489 consolidated ModifierService into one canonical implementation and fixed a long-standing bug where `ModifierManager.add_modifier` silently bypassed the `allow_abilities` check. The fix surfaced latent data smells in `data/modifiers.json` that were previously masked. This project captures user decisions on those smells and (only after sign-off) applies the data edits. Engineering hardening — rejection logging, reason-bearing API, rejection-matrix test coverage — is the sibling project PROJ-498 and depends on the data surface chosen here.

## Goals
- Surface every `allow_abilities`/`allow_types`/`deny_types` row in `data/modifiers.json` whose validity is now visibly broken or visibly questionable.
- Capture an explicit user decision on each before any edit.
- Apply only the edits the user approves, via TDD against snapshot/regression tests.
- Leave a decisions trail so future agents understand what is intentional narrow targeting vs. what was a bug.

## Scope
**In:**
- `efficient_engines` modifier (allowed nowhere today; broken allow_abilities namespace AND broken effect shape — see findings).
- `mini_capital_missile` component type classification (currently `BeamWeaponAbility`; conceptually a missile).
- `facing` and `turret_mount` allow lists that include `SeekerWeaponAbility` despite seekers ignoring firing arc.
- `data/modifiers.json`, `data/components.json`, and any affected snapshot files under `tests/regression/modifier_ability_snapshots/`.

**Out:**
- Rejection logging at save-restore paths — that is PROJ-498.
- `is_modifier_allowed` reason API — that is PROJ-498.
- Rejection-matrix parametrized test coverage — that is PROJ-498.
- Any modifier the user marks "intentional, leave alone" — record decision and stop.

## User Decision Points (Phase 1 blocker)
These MUST be answered before Phase 2. Each is a real user choice, not a foregone conclusion.

1. **`efficient_engines` disposition.** Today the row's `allow_abilities` are `Engine/Generator/Weapon/Thruster` — names that do not exist in the component ability key namespace (`CombatPropulsion/ResourceGeneration/ManeuveringThruster/...`). The row also encodes `consumption_mult` as a bare `-0.2` against the default `multiply` operation, which would drive consumption negative if the row ever became reachable. Options:
   - **(a) Delete the modifier.** Lowest regression risk. Codex's recommended option. No design references it elsewhere.
   - **(b) Redesign with concrete current ability keys + corrected effect shape.** User must specify intended targets AND effect formula. Note: `get_mandatory_modifiers()` returns every *allowed* modifier and `ShipComponentManager.ensure_mandatory_modifiers()` auto-applies them on add — broadening the allow list also broadens auto-application surface.
   - **(c) Keep inert (do nothing).** Documents the row as known-broken. Worst from a code-clarity standpoint; arguably acceptable if user wants to revisit later.

2. **`mini_capital_missile` type classification.** Currently `type: "BeamWeaponAbility"` in `data/components.json:1057-1083`. Its name suggests a seeker missile. Retyping affects valid-pair counts for `seeker_*`, `range_mount`, `precision_mount`, `facing`, and `turret_mount`. Options:
   - **(a) Keep as `BeamWeaponAbility`.** Current behavior. No edits needed.
   - **(b) Retype to `SeekerWeaponAbility`.** Aligns name with type. Cascades into the seeker modifier valid-target list (currently 1, would become 2).
   - **(c) Defer.** Mark as "intentional pre-existing quirk" and stop.

3. **`facing` / `turret_mount` seeker allowance.** Both include `SeekerWeaponAbility` in `allow_abilities`, but seeker weapons ignore firing arc per `docs/systems/ability_reference.md:287`. Options:
   - **(a) Remove `SeekerWeaponAbility` from both.** Cleans dead allowance branch. Could affect any UI that allows users to add `facing`/`turret_mount` on a seeker (today: no such component except `capital_missile`, so impact is small).
   - **(b) Keep, document as intentional in `decisions.md`.** Forward-compat if seekers ever gain arc semantics.
   - **(c) Defer.**

## Key Files
| Component | File Path |
|-----------|-----------|
| Modifier definitions | `data/modifiers.json` |
| Component definitions | `data/components.json` |
| Canonical allowance service | `game/simulation/services/modifier_service.py` |
| Snapshot regression conftest | `tests/regression/modifier_ability_snapshots/conftest.py` |
| Snapshot fixtures (allowed pairs) | `tests/regression/snapshots/` |
| Auto-mandatory hook | `game/simulation/entities/ship_component_manager.py:72-80` |

## Related Documents
- [design.md](design.md) - Static analysis, mandatory-modifier coupling, decision space
- [decisions.md](decisions.md) - Full decisions log
- [findings/source_review.md](findings/source_review.md) - Static scan + PROJ-489 pointers
- Parent audit: `Projects/active_projects/PROJ-489/findings/audit_verification.md`
- Codex audit: `AgentCoordination/Scratchpad/Consult/20260523T120008Z_audit-PROJ-489/response.md`
- Codex plan consult: `AgentCoordination/Scratchpad/Consult/20260523T120100Z_plan-PROJ-489-blast-radius/response.md`
- Related DI: `DI-2026-05-23-004` (efficient_engines namespace mismatch)
- Sibling project: PROJ-498 (engineering hardening; depends on data surface chosen here)

## Verification
- [ ] All phase checklists complete
- [ ] All user decisions captured in `decisions.md` with rationale
- [ ] All tests passing (focused + targeted snapshot suite)
- [ ] No silent data re-broadening (a previously-rejected pair is now accepted only if user explicitly approved it)
- [ ] Audit passed
- [ ] User verified
