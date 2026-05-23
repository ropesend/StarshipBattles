# PROJ-498: ModifierService allow_abilities engineering hardening: rejection logging, reason API, rejection-matrix coverage

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-498` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-498 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. `is_modifier_allowed` reason-bearing API (TDD) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Save-restore path rejection logging (TDD) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Rejection-matrix test coverage (data-driven) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Doc update | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Not Started
**Last Action:** Project created from PROJ-489 audit follow-up. Codex consult `AgentCoordination/Scratchpad/Consult/20260523T120100Z_plan-PROJ-489-blast-radius/response.md` recommended this scope.
**Next Action:** **DO NOT START** until PROJ-497 completes (Phase 1 of PROJ-498's matrix test must encode the final data surface, not today's accidental surface).
**Blockers:** Hard dependency on PROJ-497 closure.

## Overview
PROJ-489 fixed `ModifierManager.add_modifier` to enforce `allow_abilities`. Two production callers — `battle_state.py` (battle save restore) and `ship_serialization.py` (ship save restore) — now silently drop modifiers when allow_abilities rejects them, with no log. Test coverage for the rejection paths is thin: only 7 re-shot snapshots assert rejection, against ~580 theoretical mismatch pairs. This project adds (1) a reason-bearing allowance API, (2) warning logs at the save-restore boundaries, and (3) a data-driven parametrized test that asserts the full rejection matrix from `data/modifiers.json` x `data/components.json`.

## Goals
- `ModifierService.is_modifier_allowed` returns a reason (enum/result object) when rejection occurs, so log messages at boundaries can be diagnostic.
- Save-restore paths in `battle_state.py` and `ship_serialization.py` emit `logger.warning` on allow_abilities rejection (not just unknown-id).
- A single data-driven parametrized test under `tests/regression/modifier_ability_snapshots/` derives the allow/reject matrix from shipped JSON and asserts the canonical behavior, with PROJ-497 outcomes baked in.

## Scope
**In:**
- `game/simulation/services/modifier_service.py` — reason-bearing return.
- `game/simulation/battle_state.py` — warning log on rejection.
- `game/simulation/entities/ship_serialization.py` — warning log on rejection (different from existing unknown-id warning).
- New test file under `tests/regression/modifier_ability_snapshots/` — parametrized matrix.
- `docs/05_ERROR_HANDLING.md` reference update.
- `docs/04_SERVICES.md` (if PROJ-489's Phase 2 didn't already cover ModifierService API).

**Out:**
- Any data edit to `data/modifiers.json` or `data/components.json` — that's PROJ-497.
- Per-rejected-pair snapshot fixtures — codex consult recommended against this; we use one parametrized test instead.
- Snapshot-comparator extra-keys-strict mode — pre-existing, unrelated.
- Save-file migration — explicit anti-pattern per CLAUDE.md "no save-file migrations".

## Key Design Decisions (locked at plan time)
See [decisions.md](decisions.md) for full rationale.

- **Reason API shape.** Add a method `ModifierService.check_allowance(component, modifier) -> AllowanceResult` (or similar) where `AllowanceResult` is a small dataclass / enum-wrapped struct that distinguishes rejection reasons. The reason set is strictly limited to what the **live service actually enforces today** (`game/simulation/services/modifier_service.py:79-106`): `UNKNOWN_MODIFIER_ID`, `TYPE_NOT_ALLOWED`, `TYPE_DENIED`, `ABILITY_NOT_ALLOWED`, `ALLOWED`. **No `ABILITY_DENIED` reason** — the service does NOT enforce `deny_abilities`, and the docs (`docs/guides/modifier_system.md:98,285`) tell authors not to rely on it. Adding `ABILITY_DENIED` here would silently expand semantics; flagged by Codex mid-project review Q5. Keep `is_modifier_allowed()` as a bool-returning convenience that delegates. Rationale: bare bool conflates "unknown id" with "wrong ability", which makes load warnings vague (Codex consult agreement).
- **Logging boundary, not call-site.** Log at save-restore (`battle_state.py`, `ship_serialization.py`), NOT inside `Component.add_modifier()`. Builder/regression rejections are intentional and should not noise the log. Aligns with `docs/05_ERROR_HANDLING.md:137-143,181-184`.
- **Matrix test derives from JSON, doesn't hardcode.** The parametrized test reads `data/modifiers.json` + `data/components.json` at collection time and asserts `is_modifier_allowed` matches a deterministic intersection rule. This makes the test future-proof against PROJ-497's data edits.

## User Decision Points (Phase 1 confirm)
None at plan time. ONE potential user-decision-point during execution:

- **Are there any modifier+component pairs that the user wants the matrix test to mark as "intentionally rejected" via an explicit marker (vs. naturally rejected by ability/type rules)?** Default assumption: no. If the user wants explicit override (e.g., "this WOULD match the rules but we forbid it anyway"), the matrix test grows an override hook.

## Key Files
| Component | File Path |
|-----------|-----------|
| Canonical allowance service | `game/simulation/services/modifier_service.py` |
| Battle save restore | `game/simulation/battle_state.py:274-280` |
| Ship save restore | `game/simulation/entities/ship_serialization.py:223-228` |
| Mandatory-modifier hook (allowed-implies-mandatory) | `game/simulation/entities/ship_component_manager.py:72-80` |
| Modifier registry/loader | `game/core/registry.py` |
| Snapshot regression conftest | `tests/regression/modifier_ability_snapshots/conftest.py` |
| New matrix test (will be created) | `tests/regression/modifier_ability_snapshots/test_allowance_matrix.py` |
| Error handling guide | `docs/05_ERROR_HANDLING.md` |

## Related Documents
- [design.md](design.md) - Reason API shape, log message format, matrix-test data flow
- [decisions.md](decisions.md) - Full decisions log
- [findings/source_review.md](findings/source_review.md) - Static analysis + production caller inventory
- Parent: PROJ-489 audit and consult artifacts
- Sibling: PROJ-497 (data-intent decisions; MUST complete first)

## Verification
- [ ] All phase checklists complete
- [ ] Tests fail before implementation, pass after (TDD)
- [ ] Matrix test reads shipped JSON; no hard-coded rejection pairs
- [ ] Save-restore logs include modifier id + component id + reason
- [ ] No new logger noise in builder/UI test paths
- [ ] `docs/05_ERROR_HANDLING.md` cites the new save-restore log behavior
- [ ] Audit passed
- [ ] User verified
