# PROJ-392: Legacy removal — Misc orphan wrappers + zero-call-site placeholders (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-392` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-392 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical — zero-call-site quick deletions | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major — inline-and-delete + small migrations | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-07_220621_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Catch-all project for orphan legacy wrappers across the codebase that don't belong to any other cluster but together represent ~12 small cleanups. Phase 1 ships zero-call-site deletions in a single PR (no migration needed). Phase 2 handles low-call-site inlines, small renames, and find-and-replace migrations.

## Goals

### Phase 1 (zero-call-site deletions)
- Delete `_priority_sort_key` helper at `ship_stats.py:503` (3 LOC, 0 callers).
- Delete `self.name_input = None` placeholder at `race_setup/screen.py:261` (1 LOC, 0 readers).
- Delete `self.expanded_ships = self._expanded_ids` alias at `battle_panels.py:92` (1 LOC, 0 readers).

### Phase 2 (inline-and-delete + small migrations)
- Inline 3 strategy_renderer image-load wrappers (LEG-01-006).
- Inline 2 quickstart_builder dir wrappers (LEG-01-007).
- Inline `find_path_deep_space` static (LEG-01-009).
- Migrate 1 caller of `priority_sort_key` to `lookup_crew_priority` (LEG-01-010).
- Rename `Game._menu_scene` to public `menu_scene` (LEG-02-015 UNCERTAIN-included).
- Find-and-replace `get_asset_manager()` → `get_default_asset_manager()` (LEG-03-010 INFO-included).
- Inline `_get_sector_text` instance wrapper (LEG-03-014).
- Rename `_get_total_crew_requirement` to public, drop `get_crew_required` wrapper (LEG-03-016 INFO-included).
- Migrate 2 callers of `NewGameSetupScreen.validate_save_name`/`generate_default_save_name` to controller (LEG-04-006).

## Scope
**In:** LEG-01-001, LEG-01-006, LEG-01-007, LEG-01-009, LEG-01-010, LEG-02-007, LEG-02-015 (UNCERTAIN), LEG-03-010 (INFO), LEG-03-014, LEG-03-016 (INFO), LEG-03-025, LEG-04-006.
**Out:** Other clusters (siblings PROJ-383..PROJ-391, PROJ-393); UNCERTAIN items the user excluded (LEG-01-008 `find_metadata`, LEG-03-012 `Ship.to_dict/from_dict`, LEG-03-013 `to_roman`); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md).

## Key Files
| Component | File Path |
|-----------|-----------|
| Phase 1 — `_priority_sort_key` | `game/simulation/entities/ship_stats.py` |
| Phase 1 — `name_input` placeholder | `game/ui/screens/race_setup/screen.py` |
| Phase 1 — `expanded_ships` alias | `game/ui/panels/battle_panels.py` |
| Phase 2 — strategy_renderer wrappers | `game/ui/screens/strategy_renderer.py` |
| Phase 2 — quickstart_builder wrappers | `game/strategy/quickstart_builder.py` |
| Phase 2 — `find_path_deep_space` | `game/strategy/services/galaxy_pathfinding_service.py` |
| Phase 2 — `priority_sort_key` | `game/simulation/entities/stat_contributors/command.py` |
| Phase 2 — `_menu_scene` | `game/app.py` |
| Phase 2 — `get_asset_manager` | `game/assets/asset_manager.py` |
| Phase 2 — `_get_sector_text` | `game/ui/screens/empire_build_queue_window.py` |
| Phase 2 — `get_crew_required` + `_get_total_crew_requirement` | `game/ui/screens/builder/stat_getters.py` |
| Phase 2 — Screen-level static wrappers | `game/ui/screens/new_game_setup_screen.py` |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] User verified
