# PROJ-188: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for Strategy Layer List UI Consolidation |
| 2026-02-24 | Single ITableDataSource base class (not split protocols) | One entry point prevents agents from missing interfaces. Required + optional methods with defaults. |
| 2026-02-24 | Pluggable ISelectionStrategy pattern | Most extensible — new modes = new class, not table modification. Table delegates click→selection, renders from state. |
| 2026-02-24 | Always virtual scrolling for all 4 lists | Consistency. Build Queue and Event Log gain performance for large datasets. |
| 2026-02-24 | Unified scroll math: start_percentage | 3 of 4 existing implementations use this. Cleaner API. |
| 2026-02-24 | VirtualTable owns selection highlighting | Selection is a table concern. DataSource's get_row_highlight() is for domain-specific highlights only. |
| 2026-02-24 | Fleet Report migrated first (Phase 2) | Best test coverage (~158 tests) validates architecture handles the hardest case. |
| 2026-02-24 | Migrate Event Log to VirtualTable | Gains virtual scrolling, sortable columns, and consistent architecture. |
| 2026-02-24 | Column value extraction in DataSource, not TableColumnManager | Decouples domain logic from generic component. Each domain adapter knows its data shape. |
| 2026-02-24 | Header sort indicators unified to ▲/▼ | Consistent across all tables. Current Planet ^/v replaced. |
| 2026-02-24 | EventBus preserved for Build Queue | Important for MVVM pattern in EmpireBuildQueueWindow. VirtualTable coexists. |
| 2026-02-24 | Delete old renderers after migration (no backward compat) | System Migration Policy: eradicate old system completely. |
