# PROJ-494: Test polish UI-family (PROJ-480 follow-through)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-494` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-494 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Retarget / prune | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. CAT-9 simplification (UI) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-8 needless complexity (UI) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-10 parametrize (UI) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CAT-11/12 fragile + logic (UI) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Audit remediation (Codex 2026-05-23) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** All 6 phases (Phases 0-5) complete; awaiting user verification.
**Last Action:** Phase 5 audit remediation executed in a single pass. T3.14 winner-determination cluster parametrized into 3-case `test_get_winner_for_team_deaths`; T3.15 directional margin cluster parametrized into 4-case `test_margin_extends_visibility_directional` with symmetric far-outside cases for top/bottom; T4.6 workshop bridge-mass assertion tightened to `mass / (50 * sqrt(2.0)) in [0.9, 1.1]` ratio band. Phase 3 checklist notes updated. Targeted pytest: 67 passed (test_battle_screen_simulation.py + test_research_renderer.py + test_workshop_event_router_select_component.py).
**Next Action:** User verification.
**Blockers:** None.

## Overview
P2 test-review polish carried over from PROJ-480 for **UI-family** tests only. Per Codex's structural advice (consult 2026-05-23), the deferred PROJ-480 backlog is split by **path locality** rather than CAT-number so that same-file work owned by multiple PROJ-480 phases stays in one project. PROJ-495 owns core mechanical (`tests/unit/strategy/**`, `tests/unit/simulation/**`, ...). PROJ-496 owns risky guard/introspection files and non-UI integration.

## Goals
- Apply CAT-8/9/10/11/12 polish to every UI-family test file pending after PROJ-480 stalled
- Resolve same-file collisions (e.g. test_fleet_report_filters.py touches CAT-8 + CAT-10) in a single owner
- Retarget every stale plan path before TDD

## Scope
**In:** Pending PROJ-480 tasks where the target file is under:
- `tests/unit/ui/**`
- `tests/repro_issues/test_bug_04_display.py`
- `tests/unit/research/test_research_renderer.py` (moved from `tests/unit/ui/screens/`)
- `tests/integration/ui/test_build_queue_formatting.py` (moved from `tests/unit/ui/screens/`)
- `tests/integration/ui/test_camera_zoom.py`

**Out:**
- Core mechanical polish (non-UI strategy/simulation/ai/modifiers/regression) → PROJ-495
- Risky files (`test_turn_engine_lazy_properties.py`, `test_persistence_adapter.py`, `test_bug_regressions_2026_01.py`, `test_battle_engine_tick.py`, `test_generation.py` atmosphere, `test_colony_output.py`) + non-UI integration → PROJ-496
- Anything PROJ-480 marked NO-ACTION / verified-acceptable / coordination-only
- Anything PROJ-480 deliberately skipped (Task 1.15, 1.17)

## Key Files
See [manifest.md](manifest.md) for the full file list.

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [findings/source_review.md](findings/source_review.md) — origin (PROJ-480 + Codex consult)
- Source: `Projects/active_projects/PROJ-480/plan.md` (deferred backlog)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
