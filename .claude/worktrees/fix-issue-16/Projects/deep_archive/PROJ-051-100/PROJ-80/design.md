# PROJ-80: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Architecture
Two separate implementations of ship stats display:

1. **`BuilderRightPanel`** (`game/ui/screens/builder/right_panel.py`)
   - 750px wide (from `PANEL_WIDTHS.right_panel` in `builder_utils.py`)
   - Top ~210px: Controls area (Name, Theme, Type, Class, AI dropdowns + portrait)
   - Below: Stats in `UIScrollingContainer` with two-column layout
   - Column 1: Main Systems, Maneuvering, Shields, Armor, Layers (dynamic), Targeting
   - Column 2: Logistics (dynamic via `get_logistics_rows()`), Crew Logistics, Fighter Support
   - Bottom: Requirements + Recommendations text boxes
   - Live updates via event bus (SHIP_UPDATED, REGISTRY_RELOADED)
   - Dirty-checking on logistics keys for rebuild triggers
   - Defines `StatRow` helper class (lines 15-56)

2. **`DesignReportPanel`** (`game/ui/panels/design_report_panel.py`)
   - 400px wide (hardcoded in `build_queue_screen.py` line 372)
   - Full-width portrait at top
   - Single-column stats below portrait
   - Uses static `fuel_logistics`/`ammo_logistics`/`energy_logistics` from STATS_CONFIG
   - Also shows `get_construction_rows(ship)` for Build Cost
   - No Requirements/Recommendations
   - One-shot update pattern (not live-editing)
   - Imports `StatRow` from `right_panel.py`

### Shared Data Layer (already unified)
- `STATS_CONFIG` in `stats_config.py` - stat group definitions loaded from `data/stats_layout.json`
- `get_logistics_rows(ship)` - dynamic resource rows (Fuel, Energy, Ammo + others)
- `get_construction_rows(ship)` - build cost rows from `PLANET_RESOURCES`
- `StatDefinition` class with getters, formatters, validators

### Consumers of `DesignReportPanel`
- `build_queue_screen.py` - creates panel at 400px wide
- `build_queue_controller.py` - calls `update_design(ship)` and `show_placeholder()`
- `ship_detail_panel.py` - only references in docstring, does NOT import or use

### Consumers of `StatRow`
- `right_panel.py` - defines it
- `design_report_panel.py` - imports from `right_panel.py`
- Tests reference indirectly via panel instantiation

## Design: Extract-and-Delegate Pattern

### New Widget: `DesignStatsPanel`
**File:** `game/ui/panels/design_stats_panel.py`

A self-contained scrollable two-column stats display widget.

```
┌─────────────────────────────────────────┐
│  ── Main Systems ──  │  ── Logistics ── │
│  Mass: 1000 / 1200   │  Fuel Cap: 500   │
│  HP: 500 HP          │  Fuel Use: 10 /s │
│  ...                 │  ...             │
│  ── Maneuvering ──   │  ── Crew ──      │
│  ...                 │  ...             │
│  ── Shields ──       │  ── Fighter ──   │
│  ...                 │  ...             │
│  ── Armor ──         │  ── Build Cost ──│
│  ...                 │  Metal: 500      │
│  ── Layers ──        │  ...             │
│  ...                 │                  │
│  ── Targeting ──     │                  │
│  ...                 │                  │
├─────────────────────────────────────────┤
│  ── Requirements ──  │  ── Recommend ── │  ← optional
│  (text box)          │  (text box)      │
└─────────────────────────────────────────┘
```

### Integration Points

**BuilderRightPanel** (Design Workshop):
```
┌── Controls (Name, Type, Class, AI) ──────── Portrait ──┐
├─────────────────────────────────────────────────────────┤
│  DesignStatsPanel(show_requirements=True)               │
│  (embeds as scrolling container filling remaining space)│
└─────────────────────────────────────────────────────────┘
```
- Controls section unchanged (top ~210px)
- Stats section delegated to `DesignStatsPanel`
- Event bus updates call `stats_panel.update_stats(ship)` / `stats_panel.rebuild(ship)`

**DesignReportPanel** (Build Queue):
```
┌─────────────────────────────────────────┐
│              Portrait (730x730)          │
├─────────────────────────────────────────┤
│  DesignStatsPanel(show_requirements=False)│
│  (embeds below portrait)                │
└─────────────────────────────────────────┘
```
- Portrait section unchanged (full-width square)
- Stats section delegated to `DesignStatsPanel`
- One-shot `update_design(ship)` creates new `DesignStatsPanel`

### Key Patterns to Reuse
- **`StatRow` class**: `game/ui/screens/builder/right_panel.py:15-56` - moves to `design_stats_panel.py`
- **`build_section()` helper**: `right_panel.py:417-428` - extracted into `DesignStatsPanel._build_section()`
- **Two-column layout calc**: `right_panel.py:397-408` - extracted into `DesignStatsPanel._build_sections()`
- **Stats update loop**: `right_panel.py:558-639` - extracted into `DesignStatsPanel.update_stats()`
- **Logistics dirty-check**: `right_panel.py:96-128` - extracted into `DesignStatsPanel.needs_rebuild()`
- **Layer row display**: `right_panel.py:580-608` - extracted into `DesignStatsPanel.update_stats()`
- **Requirements/Recommendations update**: `right_panel.py:610-639` - conditional in `update_stats()`

### Dependencies & Risks
1. **Build queue panel width at lower resolutions** - At 1280px wide: build queue panel = 1280 - 710 - 750 - 20 = -200px (negative!). Mitigation: The minimum width check `if panel_width < 250: panel_width = 250` already exists. On screens <1480px, the queue panel will overlap or be clamped. This is acceptable as the game targets 1920x1080 minimum.
2. **Test import paths** - `StatRow` moves from `right_panel.py` to `design_stats_panel.py`. Tests that import `BuilderRightPanel` and access `StatRow` indirectly will work fine. Only `design_report_panel.py` directly imports `StatRow` and needs updating.
3. **Dynamic logistics rebuild** - Build queue's one-shot pattern calls `rebuild()` each time. No performance concern since it only happens on design selection click.

### Opportunities Discovered
- Build Queue currently uses static `fuel_logistics`/`ammo_logistics`/`energy_logistics` keys from STATS_CONFIG rather than `get_logistics_rows()`. The unified panel will use the dynamic version, giving Build Queue the same rich logistics display as the workshop (shows all resources dynamically, not just hardcoded fuel/ammo/energy).
- Build Cost section currently only in Build Queue. Workshop will gain it too via the shared panel.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
