# PROJ-464: Type cleanup — presentation (UI + top-level) (2026-05-19)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-464` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-464 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Major (UI Any narrowing + ignores + missing returns) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Minor (bulk UI display narrowing) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strict-mode migration (unknown/top-level, ui) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-19 23:16
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-19_223900_type-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** Foundation baseline (PROJ-462) should land first — core-protocol/Vector2 fixes feed types into the UI properties narrowed here. UI strict-mode (Phase 3) is the largest layer (~1,084 errors, majority from untyped `pygame_gui`) and should run last.

## Overview
This project bundles the presentation-layer findings (UI screens/panels/widgets + top-level app modules) from the type-safety audit at `Reviews/results/2026-05-19_223900_type-audit/`, after an independent third-pass re-verification against live source. It holds 12 verified findings (including TYP-SR, framed as a renderer-scene Protocol seam cleanup) plus the ui and top-level strict-mode migration items. There were no CRITICAL findings in this layer, so Phase 1 begins at MAJOR.

## Goals
- Narrow the StrategyScreen / BattleScreen / planet+star list filter / builder viewmodel `-> Any` returns to concrete types (Phase 1).
- Resolve the StrategyRenderer scene-delegation `Any` via a minimal renderer-scene Protocol — NOT a hard narrow to `StrategyScreen` (Phase 1).
- Remove the two UI type-ignores (`ship_theme_manager` index, `race_theme_gallery` override) and add missing UI public/boundary return types (Phase 1).
- Bulk-narrow the UI display getter/formatter functions (`stat_getters`, `stat_rows_dynamic`) and `_to_tuple` (Phase 2).
- Migrate the top-level/app and ui layers toward `mypy --strict` (Phase 3).

## Scope
**In:** ui layer + top-level/app findings — `narrowable_any`, `type_ignore`, `missing_return`, `implicit_optional`, `strict_migration` within those layers. TYP-SR included as a Protocol-seam task.
**Out:**
- Foundation-layer findings (core/services/engine/research/assets) — see sibling [PROJ-462](../PROJ-462/plan.md) (prerequisite).
- Domain-layer findings (simulation/strategy/ai) — see sibling [PROJ-463](../PROJ-463/plan.md).
- REJECTED item TYP-APP (Game scene accessors stay `-> Any` — intentionally loose for tests) — see `findings/verification_report.md`.

## Key Files
| Component | File Path |
|-----------|-----------|
| StrategyScreen properties | `game/ui/screens/strategy_screen.py` |
| StrategyRenderer (Protocol seam) | `game/ui/screens/strategy_renderer.py` |
| BattleScreen delegates | `game/ui/screens/battle_screen.py` |
| Planet/star list filters | `game/ui/screens/planet_list_filters.py`, `game/ui/screens/star_list_filters.py` |
| Builder viewmodels | `game/ui/screens/builder/left_panel.py`, `modifier_logic.py`, `weapons_viewmodel.py` |
| Column manager | `game/ui/components/table/column_manager.py` |
| UI display getters | `game/ui/screens/builder/stat_getters.py`, `stat_rows_dynamic.py` |
| pygame_gui patch helper | `game/ui/pygame_gui_patch.py` |
| Replay/combat-lab fallback | `game/app_bootstrap.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Independent re-verification of the audit's claims
- [findings/source_audit.md](findings/source_audit.md) - Pointer to the source type-audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) - How findings were bundled across the 3 projects

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
