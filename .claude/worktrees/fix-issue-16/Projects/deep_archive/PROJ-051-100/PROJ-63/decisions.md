# PROJ-63: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Project initialized | Starting point for Break Down build_queue_screen.py |
| 2026-02-06 | Extract 3 modules (not 2 or 4+) | Balances reduction (945 to ~450) vs complexity. Gets under 500 without over-fragmenting. |
| 2026-02-06 | Place extracted files in `game/ui/panels/` | Follows existing convention — `PlanetReportPanel` and `DesignReportPanel` already live here. |
| 2026-02-06 | Portrait loader extracted first | Zero coupling to other extractions — simplest, lowest risk. Other modules depend on it. |
| 2026-02-06 | Drag handler owns all drag state | Cleaner than sharing state between screen and handler. Screen delegates all mouse events. |
| 2026-02-06 | Controller takes callbacks, not parent reference | Avoids tight coupling. Controller calls `on_queue_changed()` callback rather than accessing screen directly. |
| 2026-02-06 | Keep `_refresh_items_list` and `_refresh_queue_display` in main screen | These methods create UI elements in the screen's scrollable containers — too tightly coupled to layout to extract cleanly. |
