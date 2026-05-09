# PROJ-396: PROJ-382 remediation — review CRITICAL + MAJOR + Task 5.4 deferred

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. CRITICAL — static-guard blind spot + GameSession.from_dict mutators | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. MAJOR — 9 follow-up findings | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Task 5.4 deferred — `superweapon_order_processor.py` 723 LOC decomp | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-09 (PROJ-406 reconciliation)
**Active Phase:** Closeout
**Last Action:** All 3 phases complete. CRIT-001/002 closed; 7 of 9 MAJOR closed (MAJ-008/009 already-fixed by PROJ-383); MAJ-005 Task 5.4 decomp shipped via Option B (state-bag) reducing `superweapon_order_processor.py` from 723 LOC to 487 LOC. 392 superweapon tests green. **Sharded suite baseline (post-Wave-1, 2026-05-09 by remediation orchestrator at commit `db21bf514` and earlier in this branch): 19815 tests | 19811 passed | 0 failed | 0 errors | 4 skipped** — replaces the earlier "19735/19745" claim, which was an unverified estimate.
**Next Action:** Audit complete; awaiting user verification.
**Blockers:** None

## Overview
PROJ-382 (pattern conformance, 21 audit items + 6 user-included uncertain + 5 LOC ceiling files) shipped across 5 phases. OpenCode review flagged 2 CRITICAL + 9 MAJOR. Plus PROJ-382 deferred Task 5.4 (`superweapon_order_processor.py` 723 LOC decomposition — needs registry-restructuring approach).

## Goals
### Phase 1 (CRITICAL)
- **CRIT-001:** Extend AST static-guard at `tests/static_guards/test_facade_bypass_guard.py:58-68` to match `_session.handle_command(...)` (private form), not just `session.handle_command(...)`. After PROJ-382's privatization, the current guard has a syntactic blind spot.
- **CRIT-002:** Restore mutator services in `GameSession.from_dict()` at `game/strategy/engine/game_session.py:475-490`. Currently constructs `TurnEngineConfig.create_default()` without `fleet_mutator`/`planet_mutator`/`empire_mutator`/`ship_mutator`. Any command handler call after deserialization raises `AttributeError`. Mirror `__init__` lines 104-123.

### Phase 2 (MAJOR — 9 items)
See review for full list. Themes: BuildQueuePortraitLoader's `portrait_session=` kwarg may be a re-introduced shim under a new name; Phase 5 file-split fitness; PROJ-381 cross-impact double-check.

### Phase 3 (deferred Task 5.4)
- `game/strategy/engine/superweapon_order_processor.py` — 723 LOC. PROJ-382 deferred decomposition because the 5 `process_*` dispatchers carry `_precheck`/`_effect` closures over `self._get_empire_mutator()` / `self._event_bus` / `self._registries`. The audit's preferred path was "register effect closures on `SuperweaponSpec`" — a registry-restructuring approach. Either implement that, or use a `class _SuperweaponDispatcher` with engine refs as instance fields.

## Scope
**In:** All CRITICAL + MAJOR findings from `Reviews/results/2026-05-08_235750_code_proj-382-pattern-conformance-facade-integrity-even_req-req_20260508_235748_8c0ea0/report.md`. PROJ-382 Task 5.4 deferred decomposition.

**Out:** MINOR (14) + INFO (24) findings. PROJ-394 (already closed via separate project).

## Key Files
| Component | File Path |
|-----------|-----------|
| Static-guard fix | `tests/static_guards/test_facade_bypass_guard.py` |
| `GameSession.from_dict` | `game/strategy/engine/game_session.py` |
| BuildQueuePortraitLoader | `game/ui/screens/build_queue_screen.py` (or wherever PROJ-382 added the `portrait_session=` kwarg) |
| Task 5.4 target | `game/strategy/engine/superweapon_order_processor.py` |

## Verification
- [x] All phase checklists complete
- [x] All tests passing — sharded baseline 19815 tests | 19811 passed | 0 failed | 0 errors | 4 skipped (post-Wave-1 by orchestrator on 2026-05-09 at commit `db21bf514` and earlier in this branch). Earlier "19735/19745 sharded pass" claim corrected.
- [x] Audit passed (`validate_audit_ready.py PROJ-396` PASSED after PROJ-406 reconciliation)
- [ ] User verified

_Source review: `Reviews/results/2026-05-08_235750_code_proj-382-pattern-conformance-facade-integrity-even_req-req_20260508_235748_8c0ea0/`_
