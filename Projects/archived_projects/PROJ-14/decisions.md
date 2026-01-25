# PROJ-14: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Project initialized | Starting point for Legacy Cleanup Phase 1 - Delete Dead Code |
| 2026-01-25 | Skip `Debugging/Marked_for_Deletion_2026-01-20/` | Directory doesn't exist - already cleaned up |
| 2026-01-25 | DO NOT delete `Tools/formation_editor.py` | Production dependency - imported by game/app.py line 24 |
| 2026-01-25 | Replace traceback imports with logger.exception() | Maintains proper debug info while removing inline imports |
| 2026-01-25 | Keep Button migration in Phase 1 | Foundational cleanup - prevents future confusion about legacy vs modern UI |
| 2026-01-25 | Leave Tool scripts (component_manager, component_graphic_picker) with legacy Button | User decision - dev tools work fine, not worth migration effort |
| 2026-01-25 | Skip logger.py line 38 cleanup | Commented code doesn't exist - false report from original audit |
| 2026-01-25 | Delete tests/unit/ui/test_ui_widgets.py entirely | Tests only legacy Button/Label/Slider classes that will be deleted |
| 2026-01-25 | Store button callbacks with `btn._callback` pattern | Simple attribute storage avoids need for separate callback mapping dictionary |
| 2026-01-25 | Add ui_manager parameter to JSONPopup and ConfirmationDialog | Enables pygame_gui button integration while maintaining dialog encapsulation |
| 2026-01-25 | Project completed | All 4 phases done - dead code deleted, Button migrated to pygame_gui, legacy components removed |
