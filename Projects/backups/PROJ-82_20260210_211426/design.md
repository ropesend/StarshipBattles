# PROJ-82: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Planet Report Panel Layout
**File:** `game/ui/panels/planet_report_panel.py`

The PlanetReportPanel is a reusable widget displaying comprehensive planet info:
- **Portrait** (150x150 at 10,10)
- **Info text** (UITextBox at 170,10 — scrollable HTML with planet stats, colony info, AND resources)
- **Atmosphere graph** (150px wide below portrait at 10,170)
- **Complexes list** (optional, right side, 200px wide, scrollable)

Strategy UI creates it at `game/ui/screens/strategy_ui.py:646` with `show_complexes=False`, rect `(10, 10, 580, panel_max_height)`.

### Current Resource Display
**File:** `game/ui/screens/strategy_detail_fmt.py:147-159`

Resources displayed as inline HTML text within `format_planet_info()`:
```
Resources:
 Metals: 250k (Q:85)
 Organics: 120k (Q:72)
 ...
```

### Resource Data Available
- `planet.resources`: `Dict[str, dict]` → `{name: {'quantity': int, 'quality': float}}`
- 5 resources: `PLANET_RESOURCES = ["Metals", "Organics", "Vapors", "Radioactives", "Exotics"]` (`game/core/constants.py`)
- Production computed by `HarvestingEngine`: `harvest = base_harvest_rate * planet_quality` (per facility per turn)

### Existing Resource Icon Infrastructure
**File:** `game/ui/panels/build_queue_portraits.py`

Already has:
- `RESOURCE_PORTRAIT_FILES` — maps resource name to filename
- `RESOURCE_FALLBACK_COLORS` — maps resource name to RGB tuple
- `load_resource_icons(icon_size)` method on `BuildQueuePortraitLoader` class
- Icons in `assets/Images/Resource Portraits/` (5 PNG files, ~700-800KB each)

## New Layout Design

```
+------ PlanetReportPanel (full rect) ---------+
| [Portrait 150x150] | [Info UITextBox]   |[Cx]|
|                     | (SHORTER height    |[li]|
|                     |  no resource info) |[st]|
| [Atmosphere Graph]  |                    |    |
|                     |                    |    |
|---------------------------------------------- |
| [Resource Grid Panel - full width, ~100px]    |
|        [Met] [Org] [Vap] [Rad] [Exo]  ← icons|
| Qty:   250k  120k  80k   45k   12k           |
| Qual:   85    72    91    43    67            |
| Prod:  1.2k  800   0     520   0             |
+-----------------------------------------------+
```

### Layout Calculations
- **Resource panel height:** `RESOURCE_PANEL_HEIGHT = 100` (icon row ~30px + 3 data rows ~20px each + padding)
- **Resource panel position:** `(10, rect.height - RESOURCE_PANEL_HEIGHT - 10, rect.width - 20, RESOURCE_PANEL_HEIGHT)`
- **Info text height reduction:** `text_h = rect.height - 20 - RESOURCE_PANEL_HEIGHT` (was `rect.height - 20`)
- **Atmosphere graph height reduction:** `graph_h = rect.height - 180 - RESOURCE_PANEL_HEIGHT` (was `rect.height - 180`)

### Grid Column Layout
- Row labels column: ~60px wide (left side)
- 5 resource columns: remaining width divided equally
- Each column: icon centered, values centered below
- Column width estimate: `(panel_width - 60) / 5` ≈ 100px per column

## Key Patterns to Reuse

- **Resource icon loading**: Reuse `RESOURCE_PORTRAIT_FILES` and `RESOURCE_FALLBACK_COLORS` from `build_queue_portraits.py` (import constants, replicate loading pattern without needing `BuildQueuePortraitLoader` class)
- **UILabel for grid cells**: Same pattern as complexes list — `UILabel` elements in a container
- **Compact number formatting**: Same pattern as `format_planet_info()` lines 151-156 (`qty >= 1000000` → "1.2M", `qty >= 1000` → "250k")
- **UIPanel as container**: Same pattern as main panel and complexes container

## Dependencies & Risks

1. **Atmosphere graph height** — reducing panel space means the graph gets shorter. Min height check already exists (`if graph_h < 50: graph_h = 50`). May need to adjust minimum panel height from 350 to 450.
2. **Complexes list overlap** — when `show_complexes=True`, the resource panel spans full width including the complexes area. The complexes container height also needs to be reduced by `RESOURCE_PANEL_HEIGHT`.
3. **Production computation in strategy_ui** — strategy_ui.py will need a helper to scan facilities for ResourceHarvester abilities. This mirrors HarvestingEngine logic but is read-only (no mutation).

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
