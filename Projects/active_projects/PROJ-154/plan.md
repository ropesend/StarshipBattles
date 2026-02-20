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
| 1. Pure File Deletions | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate then Delete | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Partial File Edits | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. File Relocation | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-19
**Active Phase:** All phases complete - ready for audit
**Last Action:** Phase 4 complete - relocated test_fleet_report_filters.py from strategy/ to ui/screens/ (932 lines)
**Next Action:** Trigger audit (Protocol 04)
**Blockers:** None
**Context for Next Agent:** All 4 phases complete. Test count: 11984 passed, 144 pre-existing failures. No NEW failures introduced.

### PROJ-157 Overlap Summary
PROJ-157 completed these PROJ-154 items:
- **Phase 1:** Deleted 5 of 8 files (test_overlay, test_slider_snap_logic, test_simulation_adapter_edge_cases, test_ship_display_formatter_edge_cases, test_hex_math)
- **Phase 2:** Completed 2 of 4 merge tasks (UI-2 race_validator, UI-8 battle_ui_service)
- **Phase 3:** Completed 4 of 8 partial edits (test_config, test_battle_screen_edge_cases, test_colors, test_game_renderer)

### Remaining Work (~10 tasks)
- **Phase 1:** Delete mock_battle_ui_service.py, test_conflict_core.py, test_build_queue_source_errors.py, test_fleet_resource_aggregator.py + __init__ cleanup
- **Phase 2:** Merge test_engines_contracts.py (16 tests) → test_engine_interfaces.py; merge test_fleet_battle_adapter.py data/ (1 test) → root
- **Phase 3:** Remove 3 duplicates from test_battle_screen_extended.py; remove TestGameSwitchScene from test_scene_protocol.py; remove 11 mock-testing tests from test_strategy_detail_formatter.py; remove test_legacy_cleanup from test_production_refactor.py
- **Phase 4:** git mv test_fleet_report_filters.py strategy/ → ui/screens/

## Overview
Systematic cleanup of dead, duplicate, and trivially obvious test code identified by a code review (v3) and validated through a detailed 28-finding validation review. The validation confirmed 12 findings for removal, disputed 6 (keep as-is), and modified 10 (partial removal with unique test preservation).

**Original scope:** ~2,942 lines. **Remaining after PROJ-157:** ~1,438 lines to remove + 932 lines to relocate.

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
- Old directory trees (Agent 8 finding — separate project scope, handled by PROJ-157 Phase 4)
- Any production code changes
- Any new test development

## Key Files (Remaining Only)
| Component | File Path | Action |
|-----------|-----------|--------|
| UI dead mock | `tests/unit/ui/mocks/mock_battle_ui_service.py` | Delete |
| UI partial edits | `tests/unit/ui/test_battle_screen_extended.py` | Remove 3 duplicate tests |
| UI partial edits | `tests/unit/ui/test_scene_protocol.py` | Remove TestGameSwitchScene |
| UI partial edits | `tests/unit/ui/screens/test_strategy_detail_formatter.py` | Remove 11 mock-testing tests |
| STR stubs | `tests/unit/strategy/conflict_resolution/test_conflict_core.py` | Delete |
| STR stubs | `tests/unit/strategy/data/test_build_queue_source_errors.py` | Delete |
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
| 2026-02-19 | Updated checklists after PROJ-157 overlap review | PROJ-157 completed ~60% of PROJ-154 scope; all checklists updated to reflect remaining work |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Source review: `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/`
- Validation findings: `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/findings/`

## Verification
- [x] All phase checklists complete
- [x] All tests passing (no NEW failures beyond pre-existing 144)
- [x] `git diff --stat` confirms remaining ~1,438 lines removed
- [ ] User verified
