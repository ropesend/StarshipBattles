# PROJ-165: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Module-level function in `game/ui/utils.py` | Consistent with existing utils pattern. No shared base class among consumers. |
| 2026-02-23 | Return UILabel, don't advance y | Callers use 3 different y-advancement values (28, ROW_HEIGHT, ROW_HEIGHT+5). Caller controls spacing. |
| 2026-02-23 | Default x=10, height=25 | 23/24 sites use x=10; 19/24 use height=25. Exceptions pass explicit values. |
| 2026-02-23 | Exclude `── Title ──` decorated headers | Different visual pattern. `ship_detail_panel.py` already has own `_add_section_header()`. |
| 2026-02-23 | Lazy import of pygame_gui | `utils.py` currently only imports `pygame`. Keeps module lightweight. |
| 2026-02-23 | Width is required (no default) | Width varies substantially across sites (200, 300, col_width, content_width, calculated expressions). |
