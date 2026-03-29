# PROJ-231: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Star Data Model (`game/strategy/data/stars.py`)
The `Star` dataclass has 10 direct attributes + 1 derived property:
- `name` (str), `mass` (float, solar masses), `radius_hexes` (int, 1-6)
- `temperature` (float, Kelvin), `luminosity` (float, solar luminosity)
- `spectrum` (Spectrum with 9 bands), `star_type` (StarType enum, 8 types)
- `color` (RGB tuple), `age` (float, years), `location` (HexCoord)
- `occupied_hexes` (FrozenSet[HexCoord], derived property)

### StarType Enum (8 values)
MAIN_SEQUENCE, RED_GIANT, BLUE_GIANT, WHITE_DWARF, RED_DWARF, NEUTRON_STAR, BLACK_HOLE, BROWN_DWARF

### Spectrum Bands (9)
gamma_ray, xray, ultraviolet, blue, green, red, infrared, microwave, radio

### Current StarInfo DTO (`game/strategy/facade/dto/system_dto.py`)
Very sparse — only `name`, `star_type`, `color`, `location`. Needs enrichment with all star attributes plus system context (system_name, system_global_location, planet_count, companion_star_count).

### Planet List Architecture (template to mirror)
The planet list uses 6 files with clean separation:
1. **Window** (`planet_list_window.py`) — UIWindow subclass, layout, event coordination
2. **Filters** (`planet_list_filters.py`) — Pure functions: gather, filter, sort, compute_ranges
3. **Filter Manager** (`planet_list_filter_manager.py`) — State class for filter values
4. **Sidebar** (`planet_list_sidebar.py`) — `build_sidebar()` factory creating all filter UI elements
5. **Data Source** (`planet_data_source.py`) — `ITableDataSource` implementation
6. **Presets** (`planet_list_presets.py`) — `PresetManager` with capture/apply functions

All reuse the `VirtualTable` + `TableColumnManager` + `SingleSelect` from `game/ui/components/table/`.

### Strategy Screen Integration Pattern
- Button added in `strategy_panel_manager.py` (StrategyWidgets dataclass + top bar creation)
- Button unpacked in `strategy_ui.py` with delegation method
- Window opened in `strategy_window_manager.py` with close/navigate callbacks
- Button routed in `strategy_event_router.py` with modal/blocking checks

### Navigation Pattern
Camera navigation uses `scene._camera_nav.center_on_hex(hex_coord)` — already used by event log window navigation callback.

## Key Patterns to Reuse
- **VirtualTable**: `game/ui/components/table/virtual_table.py` — sortable, reorderable, virtual-scrolling table
- **TableColumnManager**: `game/ui/components/table/column_manager.py` — column state management
- **ITableDataSource**: `game/ui/components/table/data_source.py` — data provider interface
- **SingleSelect**: `game/ui/components/table/selection.py` — single row selection strategy
- **UIScrollingContainer**: pygame_gui built-in, used by planet sidebar for tall filter content
- **PresetManager**: `game/ui/screens/planet_list_presets.py` — subclass with different filename
- **CQRS-lite DTO pattern**: Frozen dataclass DTOs from facade, never expose domain objects

## Dependencies & Risks
1. **Top bar button overflow** — Adding a 10th button to the top bar. At 100px width + 10px gap, 10 buttons = ~1090px. Should fit on 2560px+ screens (target resolution). If it overflows, reduce `btn_w` or abbreviate labels.
2. **StarInfo DTO backward compatibility** — Adding new fields with defaults to `StarInfo.from_star()` preserves the existing call in `SystemInfo.from_star_system()` which passes only `star`.
3. **No detail panel** — Unlike planet list, star list has no detail panel on the right. This simplifies layout but means the table gets more horizontal space.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

### Column Plan (19 columns)

**Visible by default (10):**
| ID | Title | Width | Source |
|----|-------|-------|--------|
| name | Name | 150 | `star.name` |
| type | Type | 120 | `star.star_type.name` formatted |
| system | System | 120 | cached system name |
| mass | Mass (Sol) | 100 | `star.mass` |
| radius | Radius | 80 | `star.radius_hexes` |
| temp | Temp (K) | 100 | `star.temperature` |
| luminosity | Lumin (Sol) | 100 | `star.luminosity` |
| age | Age (Gyr) | 110 | `star.age / 1e9` |
| planets | Planets | 70 | cached planet count |
| companions | Companions | 90 | cached companion count |

**Hidden by default (9 spectrum bands):**
| ID | Title | Width | Source |
|----|-------|-------|--------|
| spec_gamma | Gamma Ray | 90 | `star.spectrum.gamma_ray` |
| spec_xray | X-Ray | 90 | `star.spectrum.xray` |
| spec_uv | UV | 90 | `star.spectrum.ultraviolet` |
| spec_blue | Blue | 90 | `star.spectrum.blue` |
| spec_green | Green | 90 | `star.spectrum.green` |
| spec_red | Red | 90 | `star.spectrum.red` |
| spec_ir | Infrared | 90 | `star.spectrum.infrared` |
| spec_micro | Microwave | 90 | `star.spectrum.microwave` |
| spec_radio | Radio | 90 | `star.spectrum.radio` |

### Filter Plan

| Filter | Type | Default |
|--------|------|---------|
| Name search | Text entry | Empty |
| Star type | 8 checkboxes + All/None | All enabled |
| Mass | Range slider (min/max) | Full range from data |
| Temperature | Range slider (min/max) | Full range from data |
| Luminosity | Range slider (min/max) | Full range from data |
| Age | Range slider (min/max) | Full range from data |
| Radius hexes | Range slider (min/max) | Full range from data |
