# PROJ-62: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Project initialized | Starting point for Planet List Window Breakdown |
| 2026-02-06 | 4-phase approach: sidebar, data+columns, renderer, cleanup | Each phase is independently testable and reversible |
| 2026-02-06 | Sidebar uses module-level function, not class | Pure UI construction with no ongoing state management |
| 2026-02-06 | Data accessors move to existing `planet_list_filters.py` | They're pure formatting functions; consolidates with existing filter module |
| 2026-02-06 | Column manager is a class (`ColumnManager`) | Maintains column order, sort state, and header widgets - natural class boundary |
| 2026-02-06 | Virtual renderer is a class (`VirtualListRenderer`) | Manages row pool lifecycle, icon cache, scroll state - complex subsystem |
| 2026-02-06 | Keep `process_event()` and `update()` in main window | They're coordination methods that delegate to subsystems; extracting adds indirection without reducing complexity |
| 2026-02-06 | Column definitions stay as list-of-dicts | Existing pattern works well; no need to create Column dataclass for this project |
| 2026-02-06 | Sidebar builder returns plain dict of widget refs | Simpler than dataclass; main window unpacks what it needs |
