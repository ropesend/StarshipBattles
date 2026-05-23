# PROJ-479: Test review P1 brittle-bloated remediation 2026-05-20

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-479` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-479 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. CAT-4 Duplicate Testing | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-5 Fixture Bloat | Partial (6/18) | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-6 Mocking Brittleness (+ Task 3.34: post-merge bypass_init verification, 6 files) | Partial (7/34) | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CAT-7 Sleep/Latency | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. DUP cluster consolidation | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. HLP helper consolidation | Partial (4/6) | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Audit remediation — status honesty (Codex consult 2026-05-23) | Complete | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Phases 1/4/5/7 Complete; Phases 2/3/6 Partial — see deferred handoff list
**Last Action:** Phase 7 status-honesty remediation per Codex consult 2026-05-23
**Next Action:** User verification + PROJ-480 (P2 tier) can proceed
**Deferred work (requires user decision):**
- Phase 2: 12 CAT-5 tasks marked NEEDS_REWORK — mutation-isolation rationale (Codex sampled 3 deferrals and found them credible: `test_theme_discovery.py`, `test_ai.py`, `test_combat.py` all mutate live state)
- Phase 3: 27 CAT-6 tasks marked NEEDS_REWORK — heavy DI-introduction rationale **EXCEPT** Task 3.32 (ActionExecutionEngine) which was wrongly deferred (DI seam already exists in production — see DI-2026-05-23-003)
- Phase 4 Task 4.2: 5 sleeps reclassified as polling micro-yields / absence-assertions
- Phase 6 Task 6.2: HLP-002 nested copies (12+ method-local copies of MockPlanetType)
- Phase 6 Task 6.4: HLP-004 full 43-file _make_fleet sweep
- Phase 6 Task 6.5: HLP-005 setup_tmpdir — needs strategy decision

**Audit findings:** `findings/audit_verification.md` — Codex mid-project audit; F1 (status hygiene) addressed in Phase 7; F2 (Task 3.32 wrongly deferred) logged as DI-2026-05-23-003; F3 (make_mock_empire byte-identity claim) informational, no action.
**Session summary:**
- Phase 1 (CAT-4): 21/21 tasks fully done. Net consolidation: ~700 LOC reclaimed, ~30 test files touched.
- Phase 2 (CAT-5): 6/18 fully done, 12/18 NEEDS_REWORK (mutation-safety; missing prereq fixtures). All tests verified passing.
- Phase 3 (CAT-6): 7/34 fully done, 27/34 NEEDS_REWORK (heavy DI introduction / real-construction refactors deferred). All tests verified passing.
- Phase 4 (CAT-7): 2/3 fully done; Task 4.2 NEEDS_REWORK (sleeps were correctly classified as polling micro-yields or absence-assertions).
- Phase 5 (DUP cluster): 5/5 tasks addressed. New fixtures: `tests/fixtures/battle_panels.py`, `tests/fixtures/modifier_stubs.py`, helpers added to `tests/conftest.py` and `tests/unit/strategy/engine/conftest.py`.
- Phase 6 (HLP cluster): 4/6 tasks fully done, 2/6 partial (HLP-002 module-level migrations done, nested copies deferred; HLP-004 full 43-file sweep deferred — canonical helper in place). New fixture: `tests/fixtures/colonization_fixtures.py`.

## Overview
P1 tier of the 2026-05-20 test-review. Covers MAJOR-severity findings that aren't dead-trivial cleanup but still actively harm the test suite: duplicate tests (CAT-4), function-scoped heavy fixtures (CAT-5), brittle mocks coupling to private APIs (CAT-6), `time.sleep` for nondeterministic state (CAT-7), plus the 11 cross-shard cluster items (DUP-001/002/003/005/006 + HLP-001..006). After verification, ~95 items entered the plan (~2,200 LOC reclaimable).

## Goals
- Consolidate 21 duplicate-test pairs (CAT-4) via deletion, parametrization, or merge
- Rescope or restructure 18 expensive fixtures (CAT-5) — module/class scope where mutation safe, restructure where not
- Replace 35 brittle mock patterns (CAT-6) with public-boundary or behavioral assertions
- Replace 3 `time.sleep` clusters (CAT-7) with `threading.Event` / `_wait_until` deterministic waits
- Extract 5 DUP cluster patterns into shared fixtures/factories
- Extract 6 HLP helper duplications into canonical conftest locations

## Scope
**In:** CAT-4, CAT-5, CAT-6, CAT-7 individual findings + DUP-001/002/003/005/006 + HLP-001..HLP-006 cluster items.
**Out:**
- CAT-1 / 2 / 3 → see PROJ-478 (P0 project).
- CAT-8 / 9 / 10 / 11 / 12 polish → see PROJ-480 (P2 project).
- DUP-004 (REJECTED — different contract layers, no consolidation).
- Anything OpenCode tagged DISPUTED or INCONCLUSIVE (already excluded).
- Anything Claude's verification rejected or marked out-of-scope (see [findings/verification_report.md](findings/verification_report.md)).

## Key Files
| Component | File Path |
|-----------|-----------|
| Race browser dialog bypass-init | `tests/unit/ui/test_race_browser_dialog.py` |
| Ship detail panel cluster (23 tests) | `tests/unit/ui/panels/test_ship_detail_panel.py` |
| Engine state-manager mocks | `tests/unit/ui/screens/test_strategy_game_state_manager.py` |
| Turn engine lazy properties | `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` |
| Save game service conftest (HLP-001/005 canonical) | `tests/unit/strategy/save_game_service/conftest.py` |
| Engine helpers conftest (DUP-005, HLP-006 target) | `tests/unit/strategy/engine/conftest.py` |
| Root conftest (HLP-003, HLP-004 target) | `tests/conftest.py` |
| Battle panels mocks (DUP-002 target) | `tests/fixtures/battle_panels.py` (new) |
| Colonization fixtures (HLP-002 target) | `tests/fixtures/colonization_fixtures.py` (new or extend) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Claude's independent re-verification
- [findings/source_review.md](findings/source_review.md) - Pointer to source OpenCode review

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
