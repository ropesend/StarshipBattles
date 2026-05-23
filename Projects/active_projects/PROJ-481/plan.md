# PROJ-481: Type cleanup — UI per-finding (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-481` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-481 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical UI narrowings | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major UI narrowings | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Minor UI narrowings + ignore cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-22 17:30
**Active Phase:** Phase 1
**Last Action:** Project created from `Reviews/results/2026-05-20_210540_type-audit/` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Type-safety cleanup for the `game/ui/` layer driven by the 2026-05-20 type audit (`Reviews/results/2026-05-20_210540_type-audit/`). After independent third-pass skeptical re-verification, ~79 UI-layer findings survived and are bundled here. Covers narrowable `-> Any` returns, missing return types, and two unjustified `# type: ignore[assignment]` sites. Heavy mypy `--strict` adoption for UI (2,571 strict errors) is **deferred** to a future dedicated project.

## Goals
- Phase 1: Add `-> bool` to the pygame_gui `UIWindow.check_clicked_inside_or_blocking` override (CRITICAL — cross-layer pygame_gui contract).
- Phase 2: Narrow `~40` MAJOR `-> Any` returns across list filter modules, list window properties, strategy_renderer/strategy_screen/strategy_superweapons delegation property clusters, battle_screen properties, and the planet/star/setup public-API surface.
- Phase 3: Narrow `~38` MINOR `-> Any` returns in colonization, click dispatcher, event router, camera_nav, workshop, builder, and test_lab helpers; replace 2 unjustified `# type: ignore[assignment]` in defeat_dialog/turn_failed_dialog with explicit `Optional[UIButton]` declarations; narrow `expected` parameter in ship_theme_manager to remove its `# type: ignore[index]`.

## Scope
**In:**
- All `-> Any` narrowings, missing returns, and removable `# type: ignore` sites in `game/ui/`.
- Two strategy-related test-bypass dialogs (`defeat_dialog.py`, `turn_failed_dialog.py`) that are UI-layer files.

**Out:**
- Strategy/Core/Sim/AI per-finding cleanup — see sibling [PROJ-482](../PROJ-482/plan.md) and [PROJ-483](../PROJ-483/plan.md).
- mypy `--strict` adoption for `game/ui/` (2,571 errors per verifier) — deferred. See `decisions.md`.
- REJECTED, OUT_OF_SCOPE, and user-deferred findings — see [findings/verification_report.md](findings/verification_report.md).
- `stat_getters.py` 47 `-> Any` functions (audit's INFO — data-driven dispatch via JSON config, narrowing requires registry refactor).
- pygame_gui boundary `-> Any` callbacks where `Any` is the upstream contract.

## Key Files
| Component | File Path | Items |
|-----------|-----------|-------|
| Strategy renderer/screen delegation props | `game/ui/screens/strategy_renderer.py`, `strategy_screen.py`, `strategy_superweapons.py`, `strategy_fleet_ops.py` | ~30 |
| Battle screen | `game/ui/screens/battle_screen.py` | 8 |
| Planet/Star list modules | `game/ui/screens/planet_list_filters.py`, `planet_list_window.py`, `star_list_filters.py`, `star_list_window.py` | 21 |
| Battle setup data + screens | `game/ui/screens/setup_data_io.py`, `setup_renderer.py`, `setup_screen.py`, `battle_setup/controller.py` | 8 |
| Workshop + builder | `game/ui/screens/workshop_screen.py`, `workshop_viewmodel.py`, `workshop_viewmodel_ship_ops.py`, `workshop_ship_io.py`, `builder/left_panel.py`, `builder/modifier_logic.py`, `builder/modifier_row.py`, `builder/weapons_viewmodel.py` | 14 |
| Test lab | `game/ui/screens/test_lab/component_dropdown.py`, `test_executor.py`, `details/validation.py`, `test_run_card.py`, `ship_panels.py` | 6 |
| Camera nav + colonization + event router | `game/ui/screens/strategy_camera_nav.py`, `strategy_colonization.py`, `strategy_event_router.py`, `strategy_click_dispatcher.py` | 14 |
| Misc UI helpers | `game/ui/screens/defeat_dialog.py`, `turn_failed_dialog.py`, `transfer_view_model.py`, `transfer_mass_preview.py`, `atmosphere_target_editor.py`, `radiation_shield_editor.py`, `gravity_target_editor.py`, `water_target_editor.py`, `pygame_gui_patch.py`, `fleet_report_window.py`, `fleet_report_filters.py`, `build_queue_list_window.py`, `battle_results_screen.py`, `battle_ui.py`, `builder_selection.py`, `strategy_input_handler.py`, `species_selector_mixin.py`, `workshop_event_router.py`, `galaxy_test/galaxy_mode.py`, `strategy_game_state_manager.py`, `design_selector_window.py`, `strategy_modal_window.py`, `strategy_render/dyson_spheres.py`, `assets/ship_theme_manager.py` | ~30 |

## Related Documents
- [design.md](design.md) — Source audit, bundle counts, layer coverage
- [decisions.md](decisions.md) — Decision log including bundling rationale
- [findings/verification_report.md](findings/verification_report.md) — VERIFIED / REJECTED / UNCERTAIN / OUT_OF_SCOPE per item
- [findings/source_audit.md](findings/source_audit.md) — Pointer to originating type-audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] mypy checks clean on touched files
- [ ] User verified
