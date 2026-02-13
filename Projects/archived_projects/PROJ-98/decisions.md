# PROJ-98: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Empire Build Yards Screen Enhancement |
| 2026-02-10 | Resource columns show construction cost rates (cost_per_tick * 100 and total_cost) | User chose this over planet harvesting rates or resource deposits. Shows what each queue is consuming to build its current item. |
| 2026-02-10 | All 10 resource columns visible by default | User preference - wants data immediately visible rather than hidden behind toggles |
| 2026-02-10 | Fix event handling with `pygame_gui.UI_BUTTON_PRESSED` | Root cause of issues #1 and #3. Matches pattern used by 27+ other working files in codebase. The string comparison against `'ui_button_pressed'` never matches. |
| 2026-02-10 | Reuse ColumnManager from planet_list_columns.py directly | Proven pattern with sort indicators (^ v) and reorder arrows (< >). Uses check_pressed() in update() loop. No need to reinvent. |
| 2026-02-10 | Add sort_sources() to BuildQueueFilterManager | Follows the sort_planets() pattern from planet_list_filters.py. Keeps filter manager as the single owner of column-related logic. |
| 2026-02-10 | Sidebar height overflow is accepted limitation | With 18 columns + filters, sidebar content may exceed window height on smaller screens. Can be addressed in a follow-up with sidebar scrolling. |
| 2026-02-10 | PROJ-97 independence confirmed | Resource columns read from queue item dicts (cost_per_tick, total_cost), not from BuildQueueSource.build_rate. No conflict. |
