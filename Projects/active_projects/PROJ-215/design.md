# PROJ-215: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Event Log Architecture
- **EventLogWindow** (`game/ui/screens/event_log_window.py`) — UIWindow with filter tabs and VirtualTable
- **EventLogDataSource** (`game/ui/screens/event_log_data_source.py`) — ITableDataSource providing cell values
- **EVENT_LOG_COLUMNS** — 4 columns: category, turn, location, message
- Events stored as dicts with `details` dict carrying arbitrary structured data

### Location Data Flow
1. Events created in strategy engines (production, combat, fleet orders)
2. `log_event()` called with kwargs → remaining kwargs become `Event.details` dict
3. Events serialized to dicts via `Event.to_dict()`
4. Facade returns event dicts to UI via `get_all_events()`
5. DataSource extracts `details.location_name` and `details.location_hex` for display

### Current Location Fields in Event Details
| Field | Set By | Description |
|-------|--------|-------------|
| `location_name` | Production, Colony events | Planet name (e.g., "Lincoln I") |
| `location_hex` | All location events | `[q, r]` global hex coords |
| *(missing)* | — | System name not stored |
| *(missing)* | — | Local hex (planet-relative) not stored |
| *(missing)* | — | Storm info not stored |

### Navigation Wiring
- Double-click detection in `EventLogWindow.process_event()` lines 253-273
- `_handle_row_navigate()` extracts `location_hex`, calls `on_navigate_callback([q, r])`
- `StrategyWindowManager._on_event_log_navigate()` receives callback, creates HexCoord, calls `_camera_nav.center_on_hex()`

## Swarm Findings Summary

### Architecture
- **Column toggle infrastructure exists**: `TableColumnManager.toggle_column()`, `get_toggleable_columns()`, `get_visible_columns()` all tested and functional
- **Sidebar pattern established**: FleetReportSidebar (lines 347-375) and PlanetListSidebar (lines 194-209) both implement `[x]/[ ]` column toggle buttons
- **VirtualTable supports dynamic rebuilds**: `rebuild_row_pool()` + `rebuild_headers()` + `force_update()` handles visibility changes
- **Facade already has system lookup**: `get_system_at_hex()` and `get_system_near_hex()` return SystemInfo DTOs

### Key Patterns to Reuse
- **Column toggle sidebar**: `fleet_report_sidebar.py:347-375` — `_build_column_section()` with `get_toggleable_columns()`, `btn.col_ref = col`, `object_id=f"#column_{col_id}"`
- **VirtualTable rebuild sequence**: `rebuild_headers()` → `rebuild_row_pool()` → `force_update()` → `update_visible_rows()`
- **System resolution from hex**: `galaxy.get_system_at_location(hex_coord)` → StarSystem with `.name`
- **Storm query**: `AreaEffectManager.get_effects_at_global_hex(galaxy, hex)` → EnvironmentalEffects with `.storm_names`

### Dependencies & Risks
1. **Event enrichment changes engine signatures** — Adding `system_name` and `local_hex` to `log_event()` is non-breaking (kwargs go to `details` dict) but tests may need updates
2. **Storm data injection scope** — ConflictResolutionEngine already has `_area_effect_manager`; ProductionEngine and FleetOrderProcessor do not. Two approaches: inject into all engines, or do lazy UI-time lookup
3. **Double-click coordinate space** — `event.pos` from MOUSEBUTTONDOWN is screen-space; `find_clicked_row()` may expect container-relative coordinates. This is the likely navigation bug.

### Opportunities Discovered
- Column reordering (drag headers) is already built into TableHeader — comes free with the new sidebar
- Storm column could later link to a storm detail popup

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## Column Architecture

### New EVENT_LOG_COLUMNS (8 total)
```python
EVENT_LOG_COLUMNS = [
    {"id": "category",   "width": 90,  "title": "Category",   "visible": True,  "sortable": True},
    {"id": "turn",       "width": 60,  "title": "Turn",       "visible": True,  "sortable": True},
    {"id": "system",     "width": 120, "title": "System",     "visible": True,  "sortable": True},
    {"id": "planet",     "width": 120, "title": "Planet",     "visible": True,  "sortable": True},
    {"id": "local_hex",  "width": 80,  "title": "Local Hex",  "visible": False, "sortable": True},
    {"id": "galaxy_hex", "width": 80,  "title": "Galaxy Hex", "visible": False, "sortable": True},
    {"id": "storm",      "width": 120, "title": "Storm",      "visible": False, "sortable": True},
    {"id": "message",    "width": 500, "title": "Message",    "visible": True,  "sortable": True},
]
```

### Event Details Fields (after enrichment)
| Field | Type | Source | Column |
|-------|------|--------|--------|
| `system_name` | `str` | Galaxy lookup at creation | System |
| `location_name` | `str` | Planet name (existing) | Planet |
| `local_hex` | `[q, r]` or None | Planet local coords | Local Hex |
| `location_hex` | `[q, r]` | Global hex (existing) | Galaxy Hex |
| `storm_names` | `List[str]` or None | AreaEffectManager query | Storm |

### Sidebar Layout
```
┌─ Event Log ─────────────────────────────────┐
│ [All] [Combat] [Production] [Colonies]      │
│┌──────────┐┌───────────────────────────────┐│
││ COLUMNS  ││ Category│Turn│System│...│Msg  ││
││[x] Cat   ││  [Prod] │  1 │Lincoln│...│... ││
││[x] Turn  ││  [Prod] │  1 │Lincoln│...│... ││
││[x] System││         │    │       │   │    ││
││[x] Planet││         │    │       │   │    ││
││[ ] Loc Hx││         │    │       │   │    ││
││[ ] Gal Hx││         │    │       │   │    ││
││[ ] Storm ││         │    │       │   │    ││
││[x] Msg   ││         │    │       │   │    ││
│└──────────┘└───────────────────────────────┘│
└─────────────────────────────────────────────┘
```
