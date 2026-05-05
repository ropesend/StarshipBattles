# PROJ-343: Closeout Sprint 1 - Production behavior bug fixes from PROJ-321..341 review

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-343` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-343 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Failing API tests (TDD) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. T1.1 fleet-to-fleet TransferDialog fix | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. T1.2 snapshot-capture failure surfacing | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. T1.2 end-of-turn engines wrapped in `_time_phase` | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. T1.3 owned sector effects empire_id propagation | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. T1.4 TransferDialog selective-close on abort | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. T1.5 CargoQuickDialog teardown guarantee | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Verification + fresh OpenCode review | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning (awaiting implementation kickoff)
**Last Action:** Project scaffolded from master arc plan at `~/.claude/plans/you-are-picking-up-vivid-spindle.md`
**Next Action:** Begin Phase 1 — write 6 failing API tests (one per defect)
**Blockers:** None
**Context for Next Agent:** Five production-behavior defects firsthand-verified by the planning instance. All Tier-1 evidence is captured in [design.md](design.md). Several tests written by the prior arc (PROJ-329C / PROJ-333) currently pin the buggy behavior as required — those tests must be UPDATED or DELETED alongside the production fix, not preserved. Per-bug commit discipline applies; commit messages are pre-suggested in each phase checklist. PROJ-342 is in flight on another machine but has zero file overlap.

## Overview

Fix five user-visible production defects discovered by the post-arc review streams (Codex × 1 + Claude subagents × 6 + OpenCode × 6). Each defect was firsthand-verified by the planning instance against the live source. The new characterization tests written by the prior arc currently pin some of these bugs as required behavior; those pinning tests must be updated alongside the production fix. This is the only project in the closeout arc that **changes production behavior**; PROJ-344..349 preserve observed behavior.

## Goals

- Fleet-to-fleet TransferDialog dispatch succeeds against the production handler (not just a mocked facade) — `IssueTransferCommand(fleet_id=A, target_fleet_id=B)` resolves to a queued TRANSFER order on fleet A targeting fleet B.
- Snapshot-capture failure no longer silently disables turn rollback — capture errors propagate or escalate so rollback safety isn't quietly bypassed.
- End-of-turn engines (organics_consumption, happiness, population, quality, atmosphere, water) wrap their work in `_time_phase` so they raise `EnginePhaseError` and the existing rollback site catches them.
- Owned sector effects (EnvironmentalDamage, FuelDrain, etc.) project only onto the owning empire's fleets at the same hex — passing the querying empire's `empire_id` activates the collector's owner filter.
- TransferDialog stays open on input-validation aborts (no source/target, both endpoints non-fleet) so the user can correct.
- CargoQuickDialog window guarantees teardown on facade-dispatch exception via `try/finally`.

## Scope

**In:**
- `game/strategy/engine/handlers/transfer.py` (T1.1)
- `game/strategy/engine/commands.py` (T1.1: confirm `target_fleet_id` carries through if order persistence change is needed)
- `game/strategy/data/order_types.py` (T1.1: only if `target_fleet_id` needs to be a recognized order param)
- `game/strategy/engine/turn_engine.py` (T1.2-snapshot, T1.2-engines)
- `game/strategy/engine/environmental_hazard_engine.py` (T1.3)
- `game/strategy/engine/conflict_resolution_engine.py` (T1.3)
- `game/ui/screens/transfer_dialog.py` (T1.4)
- `game/ui/screens/cargo_quick_dialog.py` (T1.5)
- New API-level failing tests (one per defect, written first)
- Update or delete pinning tests in:
  - `tests/unit/ui/screens/test_transfer_dialog_characterization.py:418-432` and the four tests using `patch.object(dialog, "kill")` (locate via grep)
  - `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py:168-172`
  - `tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py:130-160`
  - `tests/unit/ui/screens/test_cargo_quick_dialog*.py` no-finally pins (locate via grep)
  - `tests/unit/strategy/engine/test_environmental_hazard_engine*.py` and conflict_resolution_engine tests pinning the cross-team leak
- `Projects/active_projects/PROJ-328/phase_C_checklist.md` Note 3 — update misdocumentation of T1.4

**Out:**
- The wider Tier-2..7 cleanup (separate projects PROJ-344..349).
- Any rewrite of the "queued transfer order" persistence shape beyond what's strictly required for `target_fleet_id` to round-trip (defer to a follow-up if the order-EXECUTION path also needs updates — Phase 2 task list calls this out for the implementer to decide).
- Any non-Tier-1 finding from the review streams.

## Key Files

| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| T1.1 handler | `game/strategy/engine/handlers/transfer.py` | `TransferCommandHandler.execute` (lines 28-90) |
| T1.1 command type | `game/strategy/engine/commands.py` | `IssueTransferCommand` (lines 106-129) |
| T1.1 controller | `game/ui/screens/transfer_controller.py` | `_resolve_endpoints` (166-184), `confirm_pending` (200-280) |
| T1.2 turn engine | `game/strategy/engine/turn_engine.py` | `process_turn` (lines 514-589) |
| T1.3 hazard engine | `game/strategy/engine/environmental_hazard_engine.py` | `_process_environmental_tick` (lines 95-124) |
| T1.3 combat | `game/strategy/engine/conflict_resolution_engine.py` | sector-effects lookup (508-511) |
| T1.3 collector | `game/strategy/services/system_effects_collector.py` | `_aggregate` owner filter (293-299) |
| T1.4 dialog | `game/ui/screens/transfer_dialog.py` | `_on_confirm` (372-378) |
| T1.5 dialog | `game/ui/screens/cargo_quick_dialog.py` | `_issue_orders` (300-306) |
| Reusable helper | `game/strategy/engine/handlers/base.py` | `_resolve_player_fleet` |
| Reusable helper | `game/strategy/engine/turn_engine.py` | `_time_phase` (existing wrapper used by tick-loop sub-engines) |
| PROJ-328 misdoc | `Projects/active_projects/PROJ-328/phase_C_checklist.md` | Note 3 |

## Related Documents

- [design.md](design.md) — firsthand verification of each defect with line numbers
- [decisions.md](decisions.md) — decisions log
- [manifest.md](manifest.md) — file manifest for parallel-execution conflict detection
- Master arc plan: `C:\Users\rossr\.claude\plans\you-are-picking-up-vivid-spindle.md`
- Source synthesis: `AgentCoordination/Scratchpad/plans/proj321_341_unified_remediation_plan.md` (gitignored)
- Source Codex review: `AgentCoordination/Scratchpad/tmp/codex_fresh_eyes_PROJ321_341_2026-05-04.md` (gitignored)

## Verification

- [ ] All phase checklists complete
- [ ] Targeted: `pytest tests/unit/strategy/engine/handlers tests/unit/strategy/turn_engine tests/unit/ui/screens -x -q` — all pass
- [ ] Targeted: `pytest tests/unit/strategy/engine/test_environmental_hazard_engine* tests/unit/strategy/engine/test_conflict_resolution_engine* -x -q` — all pass
- [ ] Full unit suite: `python -m pytest tests/unit/ -q` — 15,708+ pass / 0 fail / 2 skip (small delta acceptable)
- [ ] Lint: `python Tools/lint_test_files.py` — 0 violations
- [ ] Fresh OpenCode review dispatched via `claude-delegate-review` skill, returned with no CRITICAL findings on the Phase 2-7 fixes
- [ ] Audit passed (no significant issues)
- [ ] User verified
