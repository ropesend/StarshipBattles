# PROJ-289: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current layouts (pre-PROJ-289)

**Per-species text** at `game/ui/screens/strategy_detail_fmt.py:117-129`:
```python
if len(populations) > 0:
    for pop in populations:
        # Happiness indicator
        if pop.happiness >= 0.8:
            h_icon = "+"
        elif pop.happiness >= 0.4:
            h_icon = "~"
        else:
            h_icon = "-"
        cnt_str = format_compact_number(pop.count)
        text += f" - {pop.race_id}: {cnt_str} [{h_icon}]<br>"
```
One line per species. No habitability, no growth, no food ratio.

**Per-resource grid** at `game/ui/panels/planet_report_panel.py:314` (`_build_resource_grid`) + `_update_resource_grid` at ~line 437. Today shows a stockpile grid with current/max per resource, 8 resources (metals, organics, vapors, radioactives, exotics, fuel, energy, ammo).

### Target layouts

**Per-species sub-block** (user-confirmed):
```
Humans: 10,000 [Content]
    Habitability: 0.94        Happiness: 1.47
    Growth: +1.2% / turn      Food ratio: 1.00
    Allocation: 1.00×
Voidari: 3,000 [Unhappy]
    Habitability: 0.42        Happiness: 0.21
    Growth: -0.8% / turn      Food ratio: 0.35
    Allocation: 0.50×
```

Each species gets a header line (name, count, category) + 3 metric lines. 4 visual rows per species including the header. Display numbers:
- Habitability: raw [0, 1] to 2 decimals.
- Happiness: raw [0, 3] to 2 decimals.
- Growth: percentage, signed (`+X.X% / turn`, `-X.X% / turn`).
- Food ratio: raw [0, 1+] to 2 decimals (can exceed 1 on over-supply).
- Allocation: slider value as a multiplier (`1.00×`, `2.00×`).

Category label (Content / Unhappy / Starving) is a function of happiness: `happiness >= 1.5 → "Content"`, `0.5 <= x < 1.5 → "Settled"`, `< 0.5 → "Unhappy"`. Bracketed after the count.

**Per-resource grid** (full row, user-confirmed):
```
             Harvest   Upkeep    Yard      Net
Organics     +12.4     -10.0     -1.5      +0.9
Metals       +8.0      -1.0      -4.2      +2.8
Radioactives +2.3      -0.1      0.0       +2.2
Vapors       +5.1      0.0       0.0       +5.1
...
```

- Column headers shown ONCE at the top.
- ROW per resource. Display every resource in `ResourceCatalog` for this planet's `resource_projections` (which is driven by the superset of harvest/upkeep/yard per PROJ-288's projector).
- Signed numbers with `+` / `-` prefix to make gains vs losses scannable.
- Net column color-coded (positive = green, negative = red) — existing text-coloring utilities in `game/ui/colors.py`.

### Data flow

```
facade.get_colony_demographic_view(planet_id) -> ColonyDemographicView (PROJ-288)
       |
       ├── .species (Tuple[SpeciesDemographicView])  ──► strategy_detail_fmt.format_planet_info
       └── .resource_projections (Tuple[ResourceProjection]) ──► planet_report_panel._update_resource_grid
```

One facade call per panel update. No re-projection per-frame.

## Architecture

### `format_planet_info` signature change

Today: `format_planet_info(planet: IPlanet) -> str`. After PROJ-289: `format_planet_info(planet: IPlanet, view: Optional[ColonyDemographicView] = None) -> str`. When `view` is provided, the per-species sub-blocks use the view's richer data; when None (e.g. a test snapshot without a facade), fall back to the legacy minimal line. Backward compat.

### `PlanetReportPanel.update_planet` signature change

Today: `update_planet(planet, registries=None)` — reads planet state directly. After: `update_planet(planet, registries=None, view=None)` where `view` is an optional `ColonyDemographicView`. Callers (strategy screen) pass `view = self._facade.get_colony_demographic_view(planet.id)`. Panel passes `view` through to `format_planet_info` AND uses `view.resource_projections` for the resource grid.

### Resource grid rewrite

Delete the current stockpile-based grid. Build a new grid:
- Header row: 5 cells: (Resource, Harvest, Upkeep, Yard, Net).
- Data rows: one per resource in `view.resource_projections`.
- Cell renderer: `format_signed_float(val, width=7, decimals=1)` → `+12.4` or `-1.50` etc.
- Net cell color: green if > 0, red if < 0, default if == 0.

Stockpile/capacity data moves elsewhere OR stays in a separate row below the projection grid; user design session didn't address what happens to the old "current / max" display. **Design decision**: keep the existing stockpile display as a compact single-row summary BELOW the projection grid (e.g. "Stockpile: Metals 4523/10000, Organics 890/5000, ..."), since losing per-turn stockpile visibility would hurt gameplay signal. Document this decision.

### Species-category label

```python
def _happiness_category(happiness: float) -> str:
    if happiness >= 1.5: return "Content"
    if happiness >= 0.5: return "Settled"
    return "Unhappy"
```

Thresholds chosen to match PROJ-283's `base_happiness` = 0.5 default → "Settled" at baseline, "Content" only on well-fed + habitable planets, "Unhappy" for struggling colonies. Easy to tune.

### Signed-number formatting

Add helper `format_signed_float(value, decimals=1) -> str` in `game/ui/utils/formatters.py`:
```python
def format_signed_float(value: float, decimals: int = 1) -> str:
    if value > 0:
        return f"+{value:.{decimals}f}"
    return f"{value:.{decimals}f}"  # negatives already have their minus
```

## Dependencies & Risks

1. **`format_planet_info` is used elsewhere** — needs a codebase search to ensure the signature change doesn't break callers. The optional `view` kwarg keeps backward compat.

2. **Panel height** — adding 4+ lines per species makes the panel taller. The existing scrollable container handles this, but verify scroll behavior with 3+ species.

3. **ColonyDemographicView return-None case** — uncolonized planets return None. The panel still needs to show basic info (harvest, no upkeep, no yard). Build a fallback projection path — or always materialize the view (with empty species tuple) even for uncolonized planets. PROJ-288 defined "returns None for uncolonized"; revisit that for uncolonized-with-harvester case OR add a second lighter DTO.

4. **Stockpile display retention** — keeping current/max stockpile alongside the new projection grid doubles the resource-display real estate. Users may find it noisy. Acceptable for v1; UX polish can compact in a follow-up.

5. **PROJ-290 overlap** — PROJ-290 adds an uncolonized-habitability list to this same panel. Make sure the layout leaves room, and coordinate visual hierarchy (e.g. habitability list goes ABOVE the resource grid on uncolonized planets, per-species sub-blocks ABOVE the grid on colonized planets).

## Key Patterns to Reuse

- **`format_planet_info` HTML generation** — extend the existing pattern; don't invent a new one.
- **`PlanetReportPanel._build_resource_grid` layout** — replace the cell contents but keep the grid-cell construction idiom.
- **`format_compact_number` + existing formatters** — use for count/stockpile values.
- **UI colors** — existing `game/ui/colors.py` + HTML color hex for signed-number tinting.
- **`ColonyDemographicView` DTO** — the single source of truth for this panel's state.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
