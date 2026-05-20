# PROJ-460 — Pending doc consolidation

Cross-group doc edits staged here per `Projects/active_projects/PROJ-460/plan.md`
"Doc consolidation rule (cross-group)". PROJ-457 / PROJ-459 / PROJ-460 each
stage their intended `docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md` edits
as a single block here; the last of the three to finish applies all three
pending blocks as one consolidated commit.

PROJ-460 extracts three simulation-layer LOC reductions. Entries are appended
per phase.

---

## docs/01_ARCHITECTURE.md

### Anchor: `game/simulation/` package map (the serialization / save-load bullet)
### Operation: insert-into-list
### Source: PROJ-460 Phase 1 — F-D-028 battle_state serde extraction

The `game/simulation/` package map should note that `BattleState` save/load
serde now follows the sibling-module pattern (mirroring `planet_serde.py` /
`fleet_serde.py` in the strategy data layer). Add a mention of
`battle_state_serde.py` alongside `battle_state.py`:

> `battle_state.py` carries the `BattleState` / `ShipState` / `ProjectileState`
> / `ComponentState` / `BattleResults` dataclasses and their live-object
> constructors (`from_ship`, `to_ship`, `capture_from_engine`, etc.); the
> save/load serde (the 10 `to_dict` / `from_dict` pairs) lives in the sibling
> `battle_state_serde.py` (PROJ-460 Phase 1, F-D-028) — the dataclass methods
> are 1-line facades delegating to `component_state_to_dict(state)` /
> `component_state_from_dict(data)` and the parallel functions for the other 4
> dataclasses. Same sibling-module serde pattern as
> `game/strategy/data/planet_serde.py` (PROJ-372) and `fleet_serde.py`
> (PROJ-459).

(If the architecture doc has no explicit `game/simulation/` package-map
section yet, add the `battle_state_serde.py` note wherever simulation save/load
is described; the consolidator picks the anchor.)

---

## docs/02_PATTERNS.md

### Anchor: the "sibling-module serde" pattern (if PROJ-459's consolidation added one) OR none
### Operation: extend-or-noop
### Source: PROJ-460 Phase 1 — F-D-028

If the consolidated edit adds a "Sibling-module serde helpers" pattern entry
(PROJ-459's pending block proposes this, now that there are 2+ precedents),
add `battle_state_serde.py` as the third concrete instance — and note it is the
**multi-class** variant (5 dataclasses in one serde module, vs the single-class
`planet_serde.py` / `fleet_serde.py`). If no such pattern entry is added, no
edit is required here (the existing AST-guard "lifecycle/serde allowlists"
wording already covers it generically).
