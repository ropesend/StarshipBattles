# PROJ-290: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Treasury panel

- `game/ui/panels/empire_treasury_panel.py` renders an `EmpireEconomySnapshot` DTO.
- The snapshot (from `game/strategy/engine/empire_economy_calculator.py`) already aggregates per-turn production and expenses by resource — the treasury panel uses `EmpireEconomySnapshot.expenses` + `.production` dicts.
- Current expenses likely include: construction drain, fleet upkeep (fuel?), maybe environmental costs. Need to confirm during Phase A exploration.
- Adding "Population upkeep" = one more entry in the expenses dict, labeled consistently.

### Current uncolonized-planet rendering

- `format_planet_info` shows physical stats (mass, gravity, pressure, etc.) for any planet. For uncolonized planets it skips the "Colony Status: Owned" branch and doesn't emit population / complexes sections.
- Nothing in the panel currently considers the VIEWING empire's species when rendering a non-owned planet.

### Data we need

For Section 3 (Treasury):
- Total per-resource population upkeep across the empire = `sum(colony_view.total_upkeep[res] for colony in empire.colonies for res in config.population_consumption)`.
- Equivalent to: `sum(PlanetEconomyProjector.project(colony)[res].upkeep for colony in empire.colonies for res in ...)`.
- Best location: add `total_population_upkeep: Dict[str, float]` to `EmpireEconomySnapshot`, computed during the existing aggregation walk.

For Section 4 (Uncolonized habitability):
- Input: `planet` (uncolonized), `empire.resident_species() -> Set[str]`, `race_registry` to resolve.
- For each race_id: `race_config = race_registry.get_race(race_id)`; `score = int(round(score_planet_for_race(planet, race_config) * 100))`.
- Sort list by score descending.
- Skip races whose `race_registry.get_race(id)` returns None.

## Architecture

### Section 3 (Treasury populace upkeep)

**Add** `EmpireEconomySnapshot.total_population_upkeep: Dict[str, float]` (empty dict if no populations). Compute in the existing `EmpireEconomyCalculator` pass:

```python
# In EmpireEconomyCalculator.compute or similar:
population_upkeep: Dict[str, float] = defaultdict(float)
for colony in empire.colonies:
    # Option A: re-use PlanetEconomyProjector (PROJ-288)
    projections = self._projector.project(colony)
    for res_id, proj in projections.items():
        population_upkeep[res_id] += proj.upkeep
```

Alternative Option B: compute upkeep inline from `economy.population_consumption` + `colony.populations` — duplicates math from the projector. Prefer Option A (shared projector).

**Update** `EmpireTreasuryPanel` to render one row labeled "Population Upkeep" with one signed cell per resource:
- Row pulled from `snapshot.total_population_upkeep`.
- Values rendered via the same signed-float helper (negative, since it's a drain).
- Row placed in the "Expenses" section alongside existing expense categories.

### Section 4 (Uncolonized habitability)

New rendering branch in `format_planet_info` (or a new helper `format_uncolonized_habitability_for_empire`):

```python
def format_uncolonized_habitability_for_empire(
    planet: 'Planet',
    empire: 'Empire',
    race_registry: IRaceRegistry,
) -> str:
    """Return an HTML snippet showing 0-100 habitability for each
    resident species of the empire on this uncolonized planet.
    Empty string if the empire has no resident species."""
    species_ids = sorted(empire.resident_species())
    scored = []
    for race_id in species_ids:
        race = race_registry.get_race(race_id)
        if race is None:
            continue
        score = int(round(score_planet_for_race(planet, race) * 100))
        race_name = getattr(race, "race_name", None) or getattr(race, "name", None) or race_id
        scored.append((score, race_name, race_id))
    if not scored:
        return ""
    scored.sort(reverse=True)  # largest score first
    lines = "<br>".join(f" - {name}: {score}/100" for score, name, _ in scored)
    return f"<br><b>Habitability for your species:</b><br>{lines}<br>"
```

Called from `format_planet_info` when `planet.owner_id is None` AND an empire + race_registry are available (via new kwargs).

### Signature threading

Following PROJ-289's pattern, `format_planet_info` gains two more optional kwargs:
```python
def format_planet_info(
    planet: IPlanet,
    view: Optional[ColonyDemographicView] = None,
    empire: Optional[Empire] = None,
    race_registry: Optional[IRaceRegistry] = None,
) -> str:
```

When all three are None → legacy rendering. When `planet.owner_id is None` AND `empire + race_registry` are present → render the uncolonized habitability section. Clean backward compat.

`PlanetReportPanel.update_planet` similarly accepts `empire` + `race_registry` OR grabs them from a newly-threaded facade reference.

### Signed-float formatting for treasury

`format_signed_float` (added in PROJ-289) is reused here — negative for expenses, consistent with other expense rows.

## Key Patterns to Reuse

- **`EmpireEconomySnapshot` DTO pattern** (existing) — add a new field; UI reads.
- **`format_planet_info` conditional rendering** — extend the optional-kwarg pattern PROJ-289 introduces.
- **`PlanetEconomyProjector`** (PROJ-288) — reused by `EmpireEconomyCalculator` to avoid duplicating upkeep math.
- **`IRaceRegistry`** (PROJ-287) — resolve race names for display.

## Dependencies & Risks

1. **Treasury layout overflow** — adding one row to the expenses section may push other rows out of the viewport. `empire_treasury_panel.py` uses `UIScrollingContainer`; verify scroll works after addition.

2. **Race display names** — race_configs may have both `race_name` (species name) and `name` (faction name). Prefer `race_name` for the UI list; fall back to `name` then `race_id` if both are empty.

3. **Zero-upkeep empire** — a new game with no populations yet may have `total_population_upkeep == {}`. Treasury should gracefully omit the row (or show it with all zeros; user preference). Decision: hide the row when all values are zero — avoids noise for fresh games.

4. **Score precision** — rounding 0.94 to 94 is lossy. Agreed with user design session: "calculated value from 0 to 100" — integer is the display format. If the raw [0, 1] float is ever useful, it's still accessible via `score_planet_for_race` directly.

5. **Order of operations when a race file doesn't exist** — `race_registry.get_race(id)` returns None; skip that species silently. Same save-drift defense as PROJ-285.

6. **Large empires** — a 50-colony empire means Section 3 sums 50 projections. Each projection is O(species + resources + queues). Total: thousands of operations per treasury refresh. Acceptable for UI refresh rate but monitor. Can cache in `EmpireEconomySnapshot` (already cached per turn by the existing calculator).

## Key Patterns to Reuse

- `EmpireEconomySnapshot` at `game/strategy/engine/empire_economy_calculator.py` — existing DTO pattern for empire-wide aggregations; add a new field.
- `PlanetEconomyProjector` — reuse for per-colony upkeep computation.
- `format_planet_info` conditional rendering — extend.
- `format_signed_float` (PROJ-289) — reuse.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
