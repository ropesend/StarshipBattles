# PROJ-72: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Strategy Menu Button |
| 2026-02-07 | Menu button replaces Save Game at same position | Keeps button count identical, no layout changes needed. Save Game moves into dropdown. User confirmed. |
| 2026-02-07 | Use UIPanel (not UIWindow) for dropdown | UIWindow adds title bar/decorations not wanted for a dropdown menu. UIPanel is lightweight and matches existing UI. |
| 2026-02-07 | Route quit/load through scene_callback | Follows existing "open_builder" pattern. Keeps App.py as sole orchestrator of scene transitions. |
| 2026-02-07 | Quit to Main Menu shows confirmation dialog | User preference. Uses UIConfirmationDialog pattern already used in save deletion. |
| 2026-02-07 | Quit Game does NOT show confirmation | Alt+X already exists for confirmed exit. Menu quit is an explicit user action. |
| 2026-02-07 | Load Game opens SaveSelectionWindow in strategy UI manager | Reuses existing component. Creates window in strategy's manager so it renders in the strategy view. |
| 2026-02-07 | Settings/Controls are "Coming Soon" placeholders | User requested dummy buttons for now. Uses UIMessageWindow. |
