# PROJ-51: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-30 | Project initialized from review | Review identified 5 unresolved naming consistency issues |
| 2026-01-30 | Include NCA-006 (MINOR) in scope | User requested to include the minor stats.py relocation issue |
| 2026-01-30 | Close UI-007 (Event Handling) | Analysis found dual convention is intentional: `process_event` for pygame_gui elements, `handle_event` for custom screens. This is correct architecture. |
| 2026-01-30 | Rename files not classes (UI-006) | Classes already named `*Screen`, files misnamed `*_scene.py`. Rename files to match. |
| 2026-01-30 | Rename `*Interface` to `*UI` | Avoids file collision when renaming `*_scene.py` to `*_screen.py`. Creates consistent naming. |
| 2026-01-30 | Move InputHandler to `ui/screens/` | Aligns with `StrategyInputHandler` location pattern |
