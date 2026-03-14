# PROJ-188: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State: 4 Duplicated List Implementations

The Strategy Layer has 4 list/table UIs, each with its own rendering, column management, and scrolling:

1. **Fleet Report** (most complex): `FleetListRenderer` (426 lines) + `ColumnManager` (234 lines) + `FleetListViewModel`
   - Virtual scrolling with row pool, multi-select, image columns (portrait + topdown)
   - `ColumnManager.get_column_value()` extracts display values with late imports for strategy services

2. **Planet List**: `VirtualListRenderer` (227 lines) + `planet_list_columns.ColumnManager` (201 lines)
   - Virtual scrolling with row pool, single select, icon column with rotation
   - Column defs use `func` callables and `attr` dotted paths for value extraction

3. **Empire Build Queue**: Inline label rendering in window (~150 lines) + `BuildQueueFilterManager` (222 lines)
   - NO virtual scrolling (creates UILabel per row), multi-select, EventBus/MVVM
   - Uses `planet_list_columns.ColumnManager` for headers (confusing cross-dependency)

4. **Event Log**: Simple UILabel list (~100 lines) in `EventLogWindow`
   - NO virtual scrolling, no columns, no sorting, no selection
   - Filter tabs only (All/Combat/Production/Colonies)

### Key Duplication Points

| Concern | Fleet | Planet | Build Queue | Event Log |
|---------|-------|--------|-------------|-----------|
| Virtual scrolling | FleetListRenderer | VirtualListRenderer | None | None |
| Column config | ColumnManager | planet_list_columns.ColumnManager | BuildQueueFilterManager | None |
| Header buttons | FleetListRenderer | planet_list_columns.ColumnManager | planet_list_columns.ColumnManager | None |
| Value extraction | ColumnManager.get_column_value | get_column_value() func | ViewModel.get_column_value | Inline |
| Image caching | FleetListRenderer (ShipThemeManager) | VirtualListRenderer (AssetManager) | None | None |
| Selection | set[int] on Window | single planet ref | set[int] on ViewModel | None |
| Sort state | ViewModel | ColumnManager | ColumnManager | Hardcoded |

## Swarm Findings Summary

### Architecture (6 Agents)

**Architecture Analyst:** Identified minimal generic API: VirtualTable needs 6 core methods, TableHeader needs check-press pattern, ITableDataSource needs `get_row_count/get_cell_value/get_columns`. Sorting and filtering stay in domain adapters.

**Dependency Mapper:** All renderers have single reverse dependencies (each used by exactly one window). No circular dependencies except expected late imports in fleet ColumnManager. Two ColumnManager classes with same name but different interfaces is the key naming conflict.

**Test Impact Analyst:** ~1,095 existing tests across 32 files. 59% reusable as-is, 26% need import edits, 15% need rewriting. Critical gap: no tests for VirtualListRenderer or FleetListRenderer rendering logic.

**Pattern Scout:** Established patterns to follow — UIPanel creation, element cleanup via kill(), EventBus for inter-component events, @runtime_checkable Protocol in core/protocols.py, UIConfig constants for layout, COLORS dict for styling.

**Risk Assessor:** Key risks — scroll math differences (scroll_position vs start_percentage), image caching strategy differences, selection model variations, column spacing differences (10px gaps in Build Queue). Migration order: Planet → Fleet → Build Queue → Event Log by risk.

**Data Flow Tracer:** All 4 can use ITableDataSource but implementations vary significantly. Minimum protocol: row_count + cell_value + columns. Optional: images, highlighting, tooltips.

### Key Patterns to Reuse
- **Row Pool Pattern**: `(visible_height / row_height) + 2` pre-created rows — `fleet_list_renderer.py:166-226`
- **Scroll Math**: `start_percentage * total_height` — `planet_list_renderer.py:108-112`
- **Dirty Tracking**: Compare scroll_pct + row_count to skip updates — `planet_list_renderer.py:90-106`
- **Check-Press Pattern**: Header returns action dict, no events — `fleet_list_renderer.py:400-425`
- **Selection Highlighting**: `bg_panel.background_colour = Color(60,80,120)` — `fleet_list_renderer.py:274-288`
- **Image Caching**: Dict cache keyed by item_id — `fleet_list_renderer.py:316-352`
- **Protocol Definition**: `@runtime_checkable class I*(Protocol)` — `game/core/protocols.py`

### Dependencies & Risks
1. **Scroll math inconsistency** — Fleet uses `scroll_position`, Planet uses `start_percentage`. Unified to `start_percentage`.
2. **Two ColumnManager classes** — Same name, different interfaces. Both replaced by `TableColumnManager`.
3. **Late imports in Fleet ColumnManager** — Value extraction logic uses late imports for FleetSpeedCalculator etc. Moved to FleetDataSource.
4. **Empire Build Queue gains virtual scrolling** — Must handle potentially large datasets it wasn't designed for.
5. **Header sort indicators differ** — Fleet: ▲/▼, Planet: ^/v. Unified to ▲/▼.
6. **Column spacing** — Build Queue has 10px gaps, others flush. TableColumnManager should support configurable gap.

### Opportunities Discovered
- Empire Build Queue and Event Log gain virtual scrolling (performance for large empires)
- Event Log gains sortable columns (sort by turn, category)
- Unified image caching across all tables
- All lists gain column reordering and visibility toggles
- Test infrastructure for generic table enables future list UIs to be trivial

## Design Decisions

### ITableDataSource: Base Class with Defaults (Not Pure Protocol)

**Decision:** Single `ITableDataSource` base class with required + optional methods.
**Why:** Prevents agents from missing available interfaces. ONE class name to search for, ONE class to extend. Optional methods have sensible defaults (return None). This is easier to discover than split protocols.

```python
class ITableDataSource:
    # Required (subclass MUST implement)
    def get_row_count(self) -> int: raise NotImplementedError
    def get_cell_value(self, row_index: int, column_id: str) -> str: raise NotImplementedError
    def get_columns(self) -> List[Dict[str, Any]]: raise NotImplementedError

    # Optional (override as needed)
    def get_visible_columns(self) -> List[Dict]: ...  # filters by visible
    def get_cell_image(self, row_index: int, column_id: str) -> Optional[Surface]: return None
    def get_row_highlight(self, row_index: int) -> Optional[Tuple[int,int,int]]: return None
```

### Selection: Pluggable Strategy Pattern

**Decision:** VirtualTable accepts `ISelectionStrategy` (SingleSelect, MultiSelect, NoSelect).
**Why:** Most extensible — adding new selection modes (range, checkbox) means one new class, not modifying the table. Table delegates click→selection, renders from strategy state. Tested independently.

### Virtual Scrolling: Always On

**Decision:** All 4 lists use virtual scrolling after migration.
**Why:** Consistency; Build Queue and Event Log gain performance for large datasets. No "non-virtual" mode needed.

### Scroll Math: start_percentage

**Decision:** Unified to `scroll_bar.start_percentage * total_height`.
**Why:** 3 of 4 existing implementations use this. Cleaner API than Fleet's `scroll_position * max_scroll`.

### VirtualTable Owns Selection Highlighting

**Decision:** VirtualTable applies highlight colors based on its SelectionStrategy, not the DataSource.
**Why:** Selection is a table concern. DataSource's `get_row_highlight()` is for domain-specific highlights (e.g., damaged ships in red).

See [decisions.md](decisions.md) for the full log with rationale.
