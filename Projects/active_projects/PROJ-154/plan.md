# PROJ-154: Test Suite Cleanup - Validated Findings

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-154` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-154 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Pure File Deletions | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate then Delete | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Partial File Edits | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. File Relocation | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-16 17:20
**Active Phase:** Planning
**Last Action:** Plan created with 4 phases, all file paths verified by explore agents
**Next Action:** Begin Phase 1 — pure file deletions
**Blockers:** None
**Context for Next Agent:** Baseline is 12,788 passed, 145 pre-existing failures, 2 skipped. The 145 failures are pre-existing and NOT from this project. Monitor for any NEW failures only.

## Overview
Systematic cleanup of ~2,942 lines of dead, duplicate, and trivially obvious test code identified by a code review (v3) and validated through a detailed 28-finding validation review. The validation confirmed 12 findings for removal, disputed 6 (keep as-is), and modified 10 (partial removal with unique test preservation).

## Goals
- Remove dead test files that test nothing real (MagicMock-only, no game code)
- Eliminate duplicate test files where better versions already exist
- Remove trivially obvious tests (assert X > 0 for static constants)
- Relocate misplaced test file to correct directory
- Preserve all unique/valuable tests by migrating before deleting

## Scope
**In:**
- 28 validated findings (14 UI + 14 Strategy) from review v3
- Files confirmed removable after manual validation
- Test migrations needed to preserve unique coverage

**Out:**
- 6 DISPUTED findings (UI-10, UI-12, STR-8, STR-11, STR-12, STR-13) — these are explicitly kept
- Old directory trees (Agent 8 finding — separate project scope)
- Any production code changes
- Any new test development

## Key Files
| Component | File Path | Action |
|-----------|-----------|--------|
| UI dead files | `tests/unit/ui/test_overlay.py` | Delete |
| UI dead files | `tests/unit/ui/test_slider_snap_logic.py` | Delete |
| UI dead mock | `tests/unit/ui/mocks/mock_battle_ui_service.py` | Delete |
| UI duplicate | `tests/unit/ui/test_race_validator.py` | Merge 2 tests → screens version, delete |
| UI flat service | `tests/unit/ui/services/test_battle_ui_service.py` | Migrate 3 tests → subdirectory, delete |
| UI partial edits | `tests/unit/ui/test_config.py` | Remove ~20 trivial tests |
| UI partial edits | `tests/unit/ui/screens/test_battle_screen_edge_cases.py` | Remove 14 duplicate tests |
| UI partial edits | `tests/unit/ui/test_battle_screen_extended.py` | Remove 3 duplicate tests |
| UI partial edits | `tests/unit/ui/test_colors.py` | Remove 6 trivial tests |
| UI partial edits | `tests/unit/ui/test_scene_protocol.py` | Remove TestGameSwitchScene |
| UI partial edits | `tests/unit/ui/renderer/test_game_renderer.py` | Remove 6 constant checks |
| UI partial edits | `tests/unit/ui/screens/test_strategy_detail_formatter.py` | Remove 11 mock-testing tests |
| STR stubs | `tests/unit/strategy/conflict_resolution/test_conflict_core.py` | Delete |
| STR stubs | `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py` | Delete |
| STR stubs | `tests/unit/strategy/data/test_build_queue_source_errors.py` | Delete |
| STR stubs | `tests/unit/strategy/test_ship_display_formatter_edge_cases.py` | Delete |
| STR duplicate | `tests/unit/strategy/test_hex_math.py` | Delete (superset in core/) |
| STR duplicate | `tests/unit/strategy/test_fleet_resource_aggregator.py` | Delete (superset in data/) |
| STR contracts | `tests/unit/strategy/interfaces/test_engines_contracts.py` | Merge 16 tests → interfaces, delete |
| STR data adapter | `tests/unit/strategy/data/test_fleet_battle_adapter.py` | Merge 1 test → root, delete |
| STR partial edit | `tests/unit/strategy/engine/test_production_refactor.py` | Remove test_legacy_cleanup |
| STR relocation | `tests/unit/strategy/test_fleet_report_filters.py` | git mv → ui/screens/ |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-16 | Respect all 6 DISPUTED findings | Validation review made strong arguments for keeping UI-10, UI-12, STR-8, STR-11, STR-12, STR-13 |
| 2026-02-16 | Migrate before delete | Any unique tests must be moved to proper homes before source files are deleted |
| 2026-02-16 | Phase ordering: deletions → migrations → edits → relocation | Simplest/safest first; partial edits need more care; relocation last (standalone) |
| 2026-02-16 | Keep STR-3 root version (real objects) over data/ version (MagicMock) | Root version uses real Fleet/ShipInstance objects — higher quality despite fewer lines |
| 2026-02-16 | Keep STR-2 data/ version (749 lines) over root version (196 lines) | data/ version is strict superset with 50 tests vs 22 |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Source review: `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/`
- Validation findings: `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/findings/`

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (no NEW failures beyond pre-existing 145)
- [ ] `git diff --stat` confirms ~2,942 lines removed
- [ ] User verified
