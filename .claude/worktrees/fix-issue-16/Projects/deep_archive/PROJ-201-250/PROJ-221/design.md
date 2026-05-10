# PROJ-221: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Per-Planet Build Queue (BuildQueueScreen)
- Full-screen modal with MVVM delegation (PROJ-172 Phase 4)
- **Hardcoded columns** in `BuildQueuePanelFactory` at fixed pixel positions (X=10, 465, 515, 570, 625, 680, 735)
- `BuildQueueRenderer.refresh_queue_display()` creates per-row UIPanel elements with manual label positioning
- Displays: item name, turns remaining, 5× remaining resource cost
- Does NOT use `TableColumnManager`, `VirtualTable`, or `TableHeader`
- `BuildQueueViewModel` exists but is NOT integrated into the screen

### Shared Table Column System
- `TableColumnManager` + `TableHeader` + `VirtualTable` + `ITableDataSource` — well-architected system
- Used by: PlanetListWindow, EmpireBuildQueueWindow, EventLogWindow, FleetReportWindow
- Column swap bug: Only in `EmpireBuildQueueWindow` (detects swap event but never calls `swap_column()`)
- PlanetListWindow handles swap correctly — serves as the gold standard pattern

### Per-Turn Spend Data Flow
- `cost_per_tick` field is NOT populated on queue items by any code path
- `EmpireBuildQueueFormatter.get_resource_rate_text()` reads `cost_per_tick` but always gets None → returns "-"
- The proportional spend formula EXISTS in `ProductionEngine._calculate_tick_expenditure()` but is not exposed to UI
- Per-turn spend must be calculated dynamically from `total_cost`, `resources_consumed`, and `build_rate`

## Swarm Findings Summary

### Architecture
- VirtualTable can be embedded in the existing build queue panel area by replacing the header labels + scrollable container
- VirtualTable creates its own internal panels (header, list viewport, scrollbar) inside a provided container UIPanel
- `BuildQueuePanels` dataclass will lose 3 fields (queue_header_text, queue_scrollable, queue_column_positions) and gain virtual_table + column_manager
- All 5 existing VirtualTable consumers follow identical integration pattern

### Key Patterns to Reuse
- **PlanetListWindow column integration**: `planet_list_window.py:81-101` — column definition, `295-304` — swap handling
- **ITableDataSource**: `game/ui/components/table/data_source.py` — interface with get_row_count, get_cell_value, get_cell_image
- **EmpireBuildQueueDataSource**: `empire_build_queue_data_source.py` — data source pattern for build queues
- **SingleSelect strategy**: `game/ui/components/table/selection.py` — matches build queue single-item selection

### Dependencies & Risks
1. **Drag-and-drop conflict (HIGH)**: DragHandler uses UIPanel references and hardcoded 65px row height. Must refactor to use data-layer indices and query VirtualTable for row positions.
2. **Selection model conflict (MEDIUM)**: BuildQueueScreen maintains separate `selected_queue_index`. Must route all selection through VirtualTable's SingleSelect strategy.
3. **Queue mutation stability (MEDIUM)**: DataSource must read live queue data. Must call `force_update()` after mutations.
4. **Portrait/icon rendering (MEDIUM)**: VirtualTable supports `type: 'image'` columns. DataSource must implement `get_cell_image()`.
5. **Multi-queue switching (LOW-MEDIUM)**: Must reset scroll position and clear selection when switching queues.

### Opportunities Discovered
- Existing `BuildQueueDataSource` (for empire window) already implements ITableDataSource — can serve as reference
- `BuildQueueViewModel` exists but isn't wired — could be integrated as part of this work
- Per-turn spend calculation can be shared between per-planet and empire-wide views

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
