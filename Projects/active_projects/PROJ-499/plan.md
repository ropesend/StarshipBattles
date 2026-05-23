# PROJ-499: Regression-snapshot harness — symmetric key comparison + baseline cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-499` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-499 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Pre-flight survey + baseline-drift census | Not Started | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Strict-TDD failing test for symmetric comparator | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Tighten `compare_snapshots()` to symmetric key equality | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Re-baseline all 65 modifier-ability snapshots | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Negative-test guard (deliberately broken snapshot must fail) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Survey + document other regression harnesses (no propagation needed) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Planning (scaffolding only — no execution yet)
**Last Action:** Project created from PROJ-489 F4 informational finding. Two Codex consults landed: planning consult at `AgentCoordination/Scratchpad/Consult/20260523T125809Z_plan-snapshot-harness-fix/response.md` (recommended symmetric set-equality, opened contract-scope question) and mid-project-review audit at `AgentCoordination/Scratchpad/Consult/20260523T131241Z_audit-PROJ-499/response.md` (confirmed 58-of-65 stale prediction, no missed harnesses, no writer hardening; four actionable refinements applied — see decisions.md row 2026-05-23 mid-project audit).
**Next Action:** Phase 0 — confirm Codex's inference that ALL 65 baselines are stale, not just the 7 PROJ-489 reshots. Prototype symmetric comparator and run the modifier-snapshot suite once to count actual failures.
**Blockers:** None.
**Context for Next Agent:** PROJ-489 closed without addressing this — F4 was flagged INFORMATIONAL with "No action — harness masks; pre-existing schema-drift behavior unrelated to PROJ-489" (PROJ-489 audit_verification.md). This project is the follow-up. The Codex planning consult, decisions.md, and design.md are the binding artifacts; do not re-litigate the strategy choice without explicit cause.

## Overview
The modifier-ability snapshot harness at `tests/regression/modifier_ability_snapshots/conftest.py:147-173` has an asymmetric comparator that only iterates expected-JSON keys. Extra keys in actual output are silently dropped. PROJ-489's 7 re-shot baselines picked up 4 new `StatKey` enum members (`launch_rate_mult`, `recovery_rate_mult`, `bay_capacity_mult`, `shield_bonus_add`) that the unchanged 58 sibling baselines still lack — yet the suite is green. This project hardens the comparator and brings all 65 baselines back to the current schema.

## Goals
- Make `compare_snapshots()` symmetric: extra keys in actual must produce a diff just like missing keys in actual.
- Re-shoot all 65 baselines under `tests/regression/snapshots/` so the live schema matches the on-disk contract.
- Add a negative-test guard so a deliberately-broken snapshot is proven to fail (prevent regression of the harness itself).
- Confirm no other regression-snapshot harnesses share the gap (Codex survey says no; document the survey).

## Scope

**In:**
- `tests/regression/modifier_ability_snapshots/conftest.py` — symmetric comparator
- `tests/regression/snapshots/*.json` — re-shoot all 65 files (one-time cleanup)
- New negative-test guard for `compare_snapshots()`
- Survey documentation under `findings/harness_survey.md`

**Out:**
- Changes to `snapshot_full_component()` / writer-side code (Codex confirmed not needed for compare-only hardening)
- `tests/infrastructure/deep_compare.py` (already symmetric per Codex finding 1)
- Save/load roundtrip harnesses (already strict per Codex finding 2)
- Golden-fixture harnesses (already strict per Codex finding 2)
- Schema-versioning metadata (rejected — see decisions.md)
- Per-snapshot allowlists (rejected — see decisions.md)
- Narrowed-projection snapshot contract (rejected — see decisions.md)
- Fixing the underlying `efficient_engines` modifier data bug (PROJ-489 DI; out-of-scope here)

## Key Files
| Component | File Path |
|-----------|-----------|
| Comparator (the gap) | `tests/regression/modifier_ability_snapshots/conftest.py:139-173` |
| Snapshot writer (untouched) | `tests/regression/modifier_ability_snapshots/conftest.py:127-135` |
| Snapshot baselines (65 files, all need re-shoot) | `tests/regression/snapshots/*.json` |
| Consumer tests | `tests/regression/modifier_ability_snapshots/test_utility_modifiers.py`, `test_weapon_modifiers.py` |
| StatKey enum (source of the 4 new keys) | `game/simulation/components/abilities/stat_keys.py:53-70,109-114` |
| Default stats dict generator | `game/simulation/components/abilities/stat_keys.py:103-114` |

## Related Documents
- [design.md](design.md) — fix strategy rationale (symmetric vs allowlist vs schema-versioned vs hybrid)
- [decisions.md](decisions.md) — full decisions log
- [findings/source_review.md](findings/source_review.md) — Phase 0 baseline-drift census
- [findings/harness_survey.md](findings/harness_survey.md) — confirmation that other harnesses are clean
- Codex planning consult — `AgentCoordination/Scratchpad/Consult/20260523T125809Z_plan-snapshot-harness-fix/response.md`
- Origin: PROJ-489 F4 — `Projects/active_projects/PROJ-489/findings/audit_verification.md`

## Verification
- [ ] All phase checklists complete
- [ ] Symmetric comparator pinned by passing TDD test
- [ ] All 65 baselines re-shot, diff inspected, committed
- [ ] Negative-test guard pins comparator strictness (extra key in actual → fail)
- [ ] Sharded suite green at project end
- [ ] User verified
