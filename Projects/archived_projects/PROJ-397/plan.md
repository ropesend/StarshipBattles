# PROJ-397: PROJ-393 remediation — review CRITICAL + MAJOR + 3 deferred items

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. CRITICAL — reclaim 4 BattleScreen Combat Lab dead vars | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. MAJOR — 6 follow-up findings | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Deferred items — fleet_id field, view=None branch | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-09 (PROJ-406 reconciliation)
**Active Phase:** Closeout
**Last Action:** All 3 phases complete. Commits: a5ef5e74a (Phase 1 F-01), 6b8ee8c8f (Phase 2 F-02..F-07), 53b621303 (Phase 3 Task 3.2 view=None). Phase 3 Task 3.1 originally framed as "Full `fleet_id` deletion" was implemented as Path B simplification (delete forward-dead `entity_type`; retain `fleet_id` as canonical) — the original deletion-track text contradicted the shipped decision and is now reconciled.
**Next Action:** Audit complete; awaiting user verification.
**Blockers:** None

## Overview
PROJ-393 (test-injection legacy fallbacks + comment cleanups, 16 items across 3 phases) deferred 3 items. The OpenCode review confirmed the LEG-03-023 deferral was a post-hoc rationalization — 4 of 6 BattleScreen Combat Lab vars are actually dead code. Plus 6 MAJOR findings.

## Goals
### Phase 1 (CRITICAL F-01)
- Delete `test_mode`, `test_scenario`, `test_tick_count`, `test_completed`, `headless_start_time` (5 of 6 vars) at `game/ui/screens/battle_screen.py:117-125`. Per OpenCode's review, these are NEVER set to non-default in production. The `is_battle_over()` check at line 490 is a dead branch — live detection is `self._battle_service.is_battle_over()` at line 492. The visual test results capture in `test_lab/screen.py:334-356` is dead.
- Keep `headless_mode` only — that's the single legitimately-active feature.
- Fix `is_battle_over()` (lines 487-492), `print_headless_summary()` (lines 677-687), and `test_lab/screen.py:334-356` to remove dead branches.

### Phase 2 (MAJOR — 6 items)
See review for the full list. Themes likely include test-injection fallback gaps, partial Task 3.2 (`fleet_id` tag-only removal), and additional sweep gaps.

### Phase 3 (deferred items)
- **LEG-02-004 full deletion:** PROJ-393 only removed the `# Kept for backward compat` tag; the field stayed. Either design `entity_id`/`entity_type` or delete `fleet_id` and migrate all callers.
- **LEG-02-006 (`view=None` branch):** `PlanetSelectionWindow` lacks facade access; thread it through, then delete the legacy branch.

## Scope
**In:** All CRIT + MAJ findings from `Reviews/results/2026-05-09_002247_code_proj-393-test-injection-legacy-fallbacks-comment-c_req-req_20260509_002246_bca19e/report.md`. PROJ-393's 3 deferred items.

**Out:** MIN (8) + INFO (4) findings.

## Key Files
| Component | File Path |
|-----------|-----------|
| Combat Lab vars | `game/ui/screens/battle_screen.py` |
| Test results capture (dead) | `game/ui/screens/test_lab/screen.py` |
| `fleet_id` field | `game/strategy/engine/commands/__init__.py` |
| `view=None` branch | `game/ui/screens/strategy_detail_fmt.py` |
| `PlanetSelectionWindow` (facade thread) | (TBD per Phase 3) |

## Verification
- [x] All phase checklists complete
- [x] All tests passing (sharded suite cleared post-Wave-1 by orchestrator)
- [x] Audit passed (`validate_audit_ready.py PROJ-397` PASSED after PROJ-406 reconciliation)
- [ ] User verified
- F-05 follow-up (literal `TypeError`-on-instantiation test) deferred to PROJ-408 C-01 (Wave 4).

_Source review: `Reviews/results/2026-05-09_002247_code_proj-393-test-injection-legacy-fallbacks-comment-c_req-req_20260509_002246_bca19e/`_
