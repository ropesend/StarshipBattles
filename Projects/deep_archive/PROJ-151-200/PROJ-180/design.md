# PROJ-180: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis
Independent code review by 5 parallel agents verified all PROJ-172 audit findings:

1. **Ghost Code Confirmed:** `get_column_visibility_changed()` in `empire_build_queue_sidebar.py:265-276` always returns `False`, has zero callers anywhere in the codebase, and was superseded by synchronous handling in the window's button click handler.

2. **Backward Compat Properties Confirmed:** 14 properties in `build_queue_screen.py:161-234` exist purely as delegation shims to `self.panels.*` or `self.renderer.*`. All external callers are in test code (~50 references across 6 test files). No external production code uses them.

3. **MVVM Violation Confirmed:** `_check_tooltip_hover()` in `weapons_panel.py:316-335` performs 4 geometry calculations (content_rect collision, hit_rect collision, pixel-to-ratio mapping, ratio-to-range mapping) that belong in an InputHandler, not in the drawing layer. No WeaponsInputHandler exists yet.

## Swarm Findings Summary

### Architecture
- All 6 PROJ-172 decomposed classes have **zero circular imports**
- MVVM compliance: TestLabScreen (98%), EmpireBuildQueue (95%), WeaponsPanel (90%), FormationEditor (85%), BuildQueueScreen (70%)
- BattleStateViewer (100%) appropriately remains single-class — thin overlay utility
- BuildQueueScreen's 70% score is entirely due to the backward-compat property layer

### Key Patterns to Reuse
- **FormationInputHandler**: `game/ui/screens/formation/input_handler.py` — precedent for pixel-to-game-unit coordinate mapping in InputHandler class
- **EventBus**: Already in WeaponsViewModel — no new event wiring needed for InputHandler extraction

### Dependencies & Risks
1. **test_sub_window_hotkeys dual-path mocking** — Tests at lines 218/236 set `screen.panels.btn_close = screen.btn_close`, creating dual references. Must carefully update to single-path `screen.panels.*` access.
2. **Test count regression** — ~50 test references need updating. File-by-file approach with test run after each minimizes risk.

### Opportunities Discovered
- BuildQueueScreen MVVM score jumps from 70% to ~90% after property removal
- WeaponsPanel achieves 100% MVVM after InputHandler extraction

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
