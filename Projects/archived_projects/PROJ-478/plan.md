# PROJ-478: Test review P0 dead-trivial cleanup 2026-05-20

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-478` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-478 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. CAT-1 Trivial Pass | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-2 Tests Nothing Real | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-3 Dead Test Code | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Audit remediation (Codex consult 2026-05-23) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** All 4 phases complete
**Last Action:** Executed Phases 1–3 in a single autonomous pass. Targeted test suite (Phase 1 + Phase 2 + Phase 3 affected files) all green: 4 passed + 1 skipped (test_ship_loading), 63 passed (Phase 2 broader run), 9 passed (build_queue lifecycle scope check).
**Next Action:** User review + project close. See per-phase Notes sections for full disposition.
**Blockers:** None.
**Surfaced issues (require user decision):**
1. **Phase 1 Task 1.10** — `test_all_ships_match_expected_stats` was a vacuous-pass test pointing to a nonexistent fixture directory `tests/unit/ships/`. Skipped with detailed reason; logged as discovered issue `DI-2026-05-23-002`. Needs either real-ship fixtures created, or a test redesign that loads test-only components from `tests/unit/data/test_components.json`, or deletion.
2. **Phase 3 Task 3.2** — verification report's premise (PROJ-410 Phase 2 helper not yet implemented) is stale. `VirtualTable.invalidate_widget_caches` exists in production and the 4 affected tests all pass. Did NOT apply skip decorators because doing so would remove legitimate coverage. Recommend closing Task 3.2 as resolved-upstream.

**Manifest path corrections discovered during execution:**
- `test_strategy_widgets.py` lives under `tests/unit/ui/panels/`, not `tests/unit/ui/screens/`.
- `test_galaxy_state_encapsulation.py` lives under `tests/unit/strategy/data/`, not `tests/unit/strategy/`.
- `test_codex_consult_skills.py` source was already at `tests/static_guards/`, not `tests/unit/agent_coordination/`.
- `test_codex_interagent_discussion_skills.py` source was `tests/unit/tools/`, not `tests/unit/agent_coordination/`.
- `test_panel_full_open_benchmark.py` source was `tests/performance/`, not `tests/regression/`.

**Line refs refreshed 2026-05-22 post-merge `67116932d`.**

## Overview
P0 tier of the 2026-05-20 test-review. OpenCode's 16-shard test audit confirmed 322 findings across 13 categories; this project covers the highest-severity findings (CAT-1 Trivial Pass, CAT-2 Tests Nothing Real, CAT-3 Dead Test Code). After Claude's independent third-pass verification, 44 findings entered the plan (~430 LOC reclaimable). The remaining CAT-13 CRITICAL deletion-guard items (10) were correctly reclassified as intentional regression guards during verification and excluded.

## Goals
- Delete or rewrite 24 CAT-1 trivial-pass tests with zero regression value
- Delete or rewrite 18 CAT-2 tests-nothing-real tests (lambda-replaces-prod, phantom methods, `__new__` bypass with no real coverage)
- Remove 2 CAT-3 dead test code locations

## Scope
**In:** CAT-1 (Trivial Pass), CAT-2 (Tests Nothing Real), CAT-3 (Dead Test Code) — findings tagged CRITICAL or MAJOR after verification.
**Out:**
- CAT-4 / 5 / 6 / 7 + APC/DUP/HLP cluster items → see PROJ-479 (P1 project).
- CAT-8 / 9 / 10 / 11 / 12 polish work → see PROJ-480 (P2 project).
- Anything OpenCode tagged DISPUTED or INCONCLUSIVE (already excluded).
- Anything Claude's verification rejected or marked out-of-scope (see [findings/verification_report.md](findings/verification_report.md)).

## Key Files
| Component | File Path |
|-----------|-----------|
| Workshop screen tests | `tests/unit/ui/screens/test_workshop_screen.py` |
| ViewModel public-API tests | `tests/unit/workshop/test_workshop_viewmodel_public_api.py` |
| Strategy widgets imports | `tests/unit/ui/screens/test_strategy_widgets.py` |
| Keybindings scene smoke tests | `tests/unit/ui/screens/test_keybindings_scene.py` |
| Strategy renderer public API | `tests/unit/ui/screens/test_strategy_renderer_public_api.py` |
| Fleet aura cache | `tests/unit/simulation/combat/test_fleet_aura_cache.py` |
| Builder ship loading | `tests/unit/builder/test_ship_loading.py` |
| Consumable conftest | `tests/unit/strategy/consumable_management_engine/conftest.py` |
| Codex tooling tests | `tests/unit/agent_coordination/test_codex_consult_skills.py`, `tests/unit/agent_coordination/test_codex_interagent_discussion_skills.py`, `tests/unit/tools/test_codex_project_config.py` |
| Build queue TDD pending | `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` |

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
