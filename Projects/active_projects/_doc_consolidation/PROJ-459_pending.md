# PROJ-459 — Pending doc consolidation

Cross-group doc edits staged here per `Projects/active_projects/PROJ-459/plan.md`
"Doc consolidation rule (cross-group, three-project)". PROJ-457 / PROJ-459 /
PROJ-460 each stage their intended `docs/01_ARCHITECTURE.md` and
`docs/02_PATTERNS.md` edits as a single block here; the last of the three to
finish applies all three pending blocks as one consolidated commit.

---

## docs/01_ARCHITECTURE.md

### Anchor: `### game/strategy/` package map, `data/` bullet (currently line 154)
### Operation: insert-into-list
### Source: PROJ-459 Phase 1 — F-A-008 fleet_serde extraction

The `data/` bullet currently enumerates `planet_serde.py` among the data-layer
modules. Add `fleet_serde.py` alongside it (PROJ-459 Phase 1 lifted the
`Fleet.to_dict` / `Fleet.from_dict` bodies into the sibling module, mirroring
the planet_serde pattern from PROJ-372).

Suggested in-place edit, current text:

> `data/`: domain entities and delegates, including `Fleet`, `ShipInstance`,
> `Empire`, `Galaxy`, `GalaxyState`, `Planet`, `StarSystem`, `WarpPoint`,
> `stars.py`, `spectrum.py`, `planet_serde.py`, pathfinding, physics, fleet/ship
> delegates, hierarchy (`task_force.py`, `squadron.py`, `fleet_hierarchy.py`),
> role/policy registries, and generation config modules. […]

→

> `data/`: domain entities and delegates, including `Fleet`, `ShipInstance`,
> `Empire`, `Galaxy`, `GalaxyState`, `Planet`, `StarSystem`, `WarpPoint`,
> `stars.py`, `spectrum.py`, `planet_serde.py`, `fleet_serde.py`, pathfinding,
> physics, fleet/ship delegates, hierarchy (`task_force.py`, `squadron.py`,
> `fleet_hierarchy.py`), role/policy registries, and generation config
> modules. […]

---

## docs/systems/strategy_layer.md

### Anchor: line 847 — the existing `planet_serde.py` mention
### Operation: append-to-sentence
### Source: PROJ-459 Phase 1 — F-A-008 fleet_serde extraction

Current text (single sentence at end of paragraph):

> `Planet` query-style behavior routes through `PlanetQueryService`;
> habitability multiplier lookup routes through context-injectable
> `PlanetHabitabilityService`; serde lives in `planet_serde.py`.

→

> `Planet` query-style behavior routes through `PlanetQueryService`;
> habitability multiplier lookup routes through context-injectable
> `PlanetHabitabilityService`; serde lives in `planet_serde.py`. Fleet
> save/load follows the same sibling-module pattern at
> `game/strategy/data/fleet_serde.py` (PROJ-459 Phase 1) — `Fleet.to_dict`
> / `Fleet.from_dict` are 1-line facades delegating to
> `fleet_to_dict(fleet)` / `fleet_from_dict_kwargs(data, registries)` +
> `_deserialize_fleet_ships` / `_deserialize_fleet_orders`.

---

## docs/02_PATTERNS.md

### Anchor: not strictly needed — no pattern currently cites planet_serde as a "single instance"
### Operation: optional — only edit if a reviewer judges a "sibling-module serde" entry is now warranted given two instances
### Source: PROJ-459 Phase 1

Search of `docs/02_PATTERNS.md` for `planet_serde` returns no matches; the
file already describes serde extraction generically (the AST guard at line
164 has "lifecycle/serde allowlists" without naming files). No edit required
unless the consolidator decides to add an explicit pattern entry for
"Sibling-module serde extraction" now that there are two precedents
(`planet_serde.py`, `fleet_serde.py`). If added, suggested placement: after
the existing facade-pattern entries; pattern name "Sibling-module serde
helpers".
