# PROJ-96: Species Setup Ships View Layout Redesign

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-96` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-96 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Restructure RaceThemeGallery | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Restructure Ships Panel Layout | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Redesign Ship Preview Grid | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Cleanup & Final Testing | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Phase 2 - Restructure Ships Panel Layout
**Last Action:** Phase 1 complete - RaceThemeGallery converted to UIScrollingContainer with height parameter
**Next Action:** Begin Phase 2 - Side-by-side layout in ships panel
**Blockers:** None
**Context for Next Agent:** Phase 1 complete. RaceThemeGallery now accepts height parameter and uses UIScrollingContainer. Preview label/panel removed. Call site updated. 12 tests passing (was 14, removed 2 obsolete). 7593 tests passing overall.

## Overview
Redesign the Ships tab in the Species Setup screen to improve layout and information density. Move theme names from horizontal buttons on top to a scrollable list on the left side. Expand the ship preview grid from 2 columns / 6 ships to 3 columns / 9 ships. Make top-down images larger by using visible-bounding-rect scaling. Tighten spacing throughout.

## Goals
- Move theme selector to a vertical scrollable list on the left side of the panel
- Display 9 representative ship designs in a 3-column grid (up from 6 in 2 columns)
- Make top-down ship images larger by scaling based on visible pixels, not full image dimensions
- Center design labels above image pairs (top-down + portrait)
- Reduce spacing between elements for a tighter, more polished layout
- Clean up duplicate portrait loading code

## Scope
**In:**
- `RaceThemeGallery` layout restructure (vertical scrollable list)
- `_create_ships_panel_content` layout change (side-by-side)
- `_refresh_ship_preview` grid redesign (3 cols, 9 ships, smart scaling)
- Delete duplicate `_load_ship_portrait` method
- Unit test updates for gallery changes

**Out:**
- Adding new ship themes or ship classes
- Changes to `ShipThemeManager` internals
- Changes to other Species Setup tabs (Summary, Identity, Visuals, etc.)
- Portrait image file additions or modifications

## Key Files
| Component | File Path |
|-----------|-----------|
| Theme Gallery | `game/ui/panels/race_theme_gallery.py` |
| Ships Panel | `game/ui/screens/race_setup_screen.py` (lines 332-508) |
| Theme Manager | `game/ui/assets/ship_theme_manager.py` (API reference) |
| Gallery Tests | `tests/unit/ui/test_race_theme_gallery.py` |
| Pattern Reference | `game/ui/panels/race_portrait_gallery.py` (scrollable gallery) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Visual verification: theme list on left, 3x3 grid on right, correct sizing
- [ ] Audit passed
- [ ] User verified
