# PROJ-480: Test review P2 opportunistic polish 2026-05-20

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-480` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-480 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. CAT-9 Simplification | Partial (high-value tasks done) | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-8 Needless Complexity | Partial (subsumed/no-action only) | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-10 Parametrize | Partial (5 done) | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CAT-11 Fragile Assertion | Partial (4 done) | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. CAT-12 Logic-Heavy | Partial (no-action only) | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Audit remediation (Codex consult 2026-05-23) | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-22 (autonomous session)
**Active Phase:** Phase 1 (CAT-9 Simplification) — mid-phase stop per protocol 03a §3
**Last Action:** Completed 18 tasks across all 5 phases. Phase 1: 1.1, 1.2, 1.4, 1.6, 1.8, 1.9, 1.10, 1.12, 1.13, 1.18, 1.19, 1.20, 1.22, 1.23, 1.24, 1.25, 1.26, 1.27, 1.28 (all complete-or-no-action). Phase 2: 2.1, 2.24, 2.25, 2.26, 2.27 (no-action only — others pending). Phase 3: 3.5, 3.10, 3.20, 3.32, 3.33, 3.34, 3.40, 3.43, 3.51. Phase 4: 4.2, 4.4, 4.10. Phase 5: 5.10, 5.14, 5.18 (all coordination/no-action).
**Next Action:** Resume Phase 1 with remaining tasks: 1.3 (fleet_menu_items helpers, 40 LOC), 1.5 (HLP-005 coord — already done if PROJ-479 ran), 1.7 (MockPlanetType, 30 LOC), 1.11 (3 mode-test classes, 230 LOC — LARGEST remaining Phase 1), 1.14 (race_setup mocks, 40 LOC), 1.15 (_make_strategy_screen → fixture, see Watchouts), 1.16 (_make_ship_mock factory, 90 LOC), 1.17 (scope=module UIManager — see Watchouts), 1.21 (mock_ship factory usage, 30 LOC).
**Blockers:** None. Context budget limited single-session completion of 138 tasks; mid-phase stop is legitimate per protocol.
**Tests:** 630 tests across 20 touched files pass.

### Watchouts for the next agent
- **Plan line refs are STALE.** Many files moved or were edited by PROJ-478/PROJ-479. Always re-grep before editing. Examples encountered: `test_physics_constants.py` is under `simulation/` not `strategy/`; `test_planet_specific_colonization.py` is under `integration/colonization/` not `unit/strategy/engine/`; `test_superweapons.py` is under `simulation/components/abilities/`; `test_caption_schemas_validate.py` is under `regression/`; `test_naming.py` (with `to_roman`) is under `unit/strategy/data/`; `test_list_data_source_base.py` is under `unit/ui/screens/`. Plan undercounts of occurrences are common (e.g., Task 4.4 said ~4, was 10; Task 1.23 said 3, was 4; Task 3.10 said 7, was 14).
- **Some files referenced by the plan no longer exist** (e.g., `test_fleet_order_transfer.py` for Task 1.13). Treat their cleanup as already absorbed.
- **Conftest already populated** (per the prompt). `tests/conftest.py` has `_make_mock_fleet`, `_assert_roundtrip_property`, `make_mock_ship_instance(has_yard=...)`. `tests/unit/strategy/engine/conftest.py` has `make_mock_empire` + `mock_empire_factory`. Use these before adding duplicates.
- **Task 1.15** (_make_strategy_screen → fixture) was deliberately skipped. The function is a one-liner already; converting to a fixture forces every test-method signature change but yields no real LOC win because callers still unpack `(screen, scene_callback, ui_mock)`. Either accept the noise to gain pytest fixture-discoverability, or document the conscious skip.
- **Task 1.17** (`scope=module` + `MagicMock` UIManager for `test_transfer_dialog.py` / `test_cargo_quick_dialog.py`) was skipped. These tests use a real `pygame_gui.UIManager` and the behaviour is exercised. Switching to MagicMock has nontrivial risk; only do this if you're prepared to fix any tests that depend on real `UIManager` behaviour.
- **Phase 2 / Phase 5 are essentially untouched** for active rewrites — only coordination/no-action items have been checked off.
- Task 5.14 was wrongly marked done via PROJ-479 subsume claim; now correctly pending (Codex audit, Phase 6).

**Line refs refreshed 2026-05-22 post-merge `67116932d`.**

## Overview
P2 tier of the 2026-05-20 test-review. Lowest-priority polish work — readability and maintainability improvements that don't change test fidelity. Dominated by **CAT-10 parametrization (88 verified findings, ~3,000 LOC reducible)**: clusters of structurally identical tests where the per-test setup is genuinely redundant. After verification, ~145 items entered the plan (~1,900 LOC reclaimable). This project is sequenced lowest-risk first (simplification, then complexity reduction, then parametrize, then assertion/logic polish).

## Goals
- Replace ~28 CAT-9 repeated-pattern setups with shared fixtures or in-module helpers
- Flatten ~30 CAT-8 deeply-nested patch / oversized helper sites
- Parametrize ~55 CAT-10 structurally-identical test clusters (≥3 members each)
- Replace ~12 CAT-11 brittle exact-value assertions with tolerance / property checks
- Replace ~20 CAT-12 logic-heavy test bodies with reference values + extracted helpers

## Scope
**In:** CAT-8 Needless Complexity, CAT-9 Simplification, CAT-10 Parametrize, CAT-11 Fragile Assertion, CAT-12 Logic-Heavy — verified items only.
**Out:**
- CAT-1 / 2 / 3 dead-trivial cleanup → see PROJ-478 (P0 project).
- CAT-4 / 5 / 6 / 7 brittle-bloated remediation + cluster items → see PROJ-479 (P1 project).
- Anything OpenCode tagged DISPUTED or INCONCLUSIVE (already excluded).
- Anything Claude's verification rejected or marked out-of-scope (see [findings/verification_report.md](findings/verification_report.md)).

## Key Files
| Component | File Path |
|-----------|-----------|
| Engine validation classes (12) | `tests/unit/strategy/engine/test_engine_validation.py` |
| Superweapon parametrize matrix | `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py` |
| Strategy input handler hotkeys | `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py` |
| Strategy input handler transfer | `tests/unit/ui/screens/test_strategy_input_handler_transfer.py` |
| Camera tests (13 patch blocks) | `tests/unit/ui/test_camera.py` |
| Fleet menu items (10+ FMS rows) | `tests/unit/ui/screens/test_fleet_menu_items.py` |
| Ship serialization roundtrips | `tests/unit/simulation/entities/test_ship_serialization.py` |
| Turn engine lazy properties (18 tests) | `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` |
| Race browser dialog (12 patch.object) | `tests/unit/ui/test_race_browser_dialog.py` (also Phase 3 of PROJ-479) |
| Naming Roman numeral cluster (16 tests) | `tests/unit/strategy/utility/test_naming.py` |

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
