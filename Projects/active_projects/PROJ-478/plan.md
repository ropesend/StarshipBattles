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
| 1. CAT-1 Trivial Pass | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-2 Tests Nothing Real | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-3 Dead Test Code | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Phase 1 (CAT-1 Trivial Pass)
**Last Action:** Project created from `2026-05-20_210550_test-review` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

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
