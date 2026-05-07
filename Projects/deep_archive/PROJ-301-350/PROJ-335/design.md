# PROJ-335 — Design Notes

Per-file context for the test author. Read this before writing tests so you
don't have to re-derive shapes from source.

---

## `planetary_facility.py`

### What it models

A constructed facility instance on a planet. Distinct from the design
template — one design can have many instances. Carries operational state
(active, paused), per-component activation states, consumable inventory
(fuel), and a per-instance construction queue.

### Persistence contract

`to_dict()` emits all fields. `from_dict()` requires
`instance_id`, `design_id`, `name`, `design_data` — missing any of those
raises `PersistenceException` via `require_keys`.

Two legacy fallback paths to be aware of:

1. `from_dict` accepts a top-level `resource_levels` key as a synonym for
   `consumable_levels` (older save format).
2. `get_activation_state(key)` accepts a stored `{'active': bool}` dict
   shape and converts it on read.

### `is_shipyard` property

Returns `True` iff `is_operational` is True **and** any active component is a
`space_shipyard`. Short-circuits to `False` whenever `is_operational` is
False, regardless of components. Pin the short-circuit.

---

## `species_population.py`

### What it models

A single race's presence on a planet: race id, headcount, happiness scalar.
**No growth math here** — growth lives in the population manager / planet
update loop. The class docstring suggests otherwise; ignore it.

### Persistence contract

`from_dict({race_id, count})` defaults `happiness` to `0.5`. Missing
`race_id` or `count` raises `PersistenceException`. No bounds validation:
negative counts or out-of-range happiness are accepted silently.

---

## `squadron.py`

### What it models

A grouping of ships within a fleet. Inherits `FleetHierarchyNode` (which
contributes `combat_policy`, `battle_role`, `flagship`, `lone_ships`). Adds
its own ships list and a pair of spatial-behavior fields used by the combat
positioning system.

### Persistence contract

`to_dict()` emits `"type": "squadron"` as a discriminator. Two
serialization asymmetries:

- `spatial_behavior` key omitted when `None`.
- `spatial_behavior_params` key omitted when `{}`.

`from_dict` accepts both omissions and reconstructs with `None` and `{}`
respectively. Round-trip equivalence is therefore field-by-field, not
dict-by-dict.

`add_ship` is idempotent — adding the same ship twice does not duplicate.
`remove_ship` returns a `bool` indicating whether removal occurred.

### `all_ships` property

Returns `members + lone_ships` in that order. Order is part of the contract.

---

## `order_types.py`

### `OrderType` enum

17 variants, `auto()`-numbered. Values are positional and **not** stable for
save format — save code references variant names as strings.

### Three categorization frozensets

- `MOVEMENT_ORDER_TYPES` (3 variants).
- `ACTION_ORDER_TYPES` (12 variants).
- `PLANET_ACTION_ORDER_TYPES` (2 variants — strict subset of action).

Disjointness: movement and action are disjoint; planet-action is a subset of
action.

### `Order.to_dict` 10-branch matrix

The dispatch ladder — matches in order, first match wins:

| # | Predicate | Emitted shape |
|---|---|---|
| 1 | type ∈ {TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION} | `{type: 'transfer', value: dict}` |
| 2 | type == IMPLODE_PLANET and target is Planet | `{type: 'planet_ref', id}` |
| 3 | type == SELF_DESTRUCT and target is list | `{type: 'ship_id_list', value: list}` |
| 4 | type ∈ {OPEN_WARP_POINT, CLOSE_WARP_POINT} and target is dict | `{type: 'warp_params', value: dict}` |
| 5 | target is HexCoord | `{q, r}` — **no `type` key** |
| 6 | target is Planet | `{type: 'planet_ref', id}` |
| 7 | target is Fleet | `{type: 'fleet_ref', id}` |
| 8 | type == COLONIZE and target is dict | `{type: 'colonize_params', planet_id, population, cargo}` |
| 9 | target is dict (catch-all) | `{type: 'dict', value: dict}` |
| 10 | else | `{type: 'raw', value: str(target)}` |

`execution_progress` is serialized only when `> 0` (clean-saves invariant).

### `Order.from_dict`

The "simple" path. Unwraps `{type: 'dict', value: …}`. HexCoord, Planet, and
Fleet branches require `OrderSerializer` for reference resolution; they do
**not** round-trip via `from_dict` alone. Tests pin the simple round-trip and
explicitly assert that the HexCoord branch does not.

### `__repr__`

Two forms: with `execution_progress` (when > 0) and without. Pin both.

---

## `group_policy_registry.py`

### What it models

In-memory cache of group-combat policies, partitioned into three axes:
`targeting`, `movement`, `retreat`. Loaded from a JSON file with the
top-level shape:

```json
{
  "targeting": { "<id>": { ...policy fields... } },
  "movement":  { "<id>": { ... } },
  "retreat":   { "<id>": { ... } }
}
```

### `load(file_path=None)`

Defaults to `Paths.GROUP_POLICIES_FILE`. Uses `load_json(default={})`, so a
missing file silently produces empty axes (no exception). Sets `_loaded =
True` regardless of file presence. Logs counts.

### `validate_policy(CombatPolicy) → list[str]`

Per-axis validation. **`None` on an axis means "inherit", not invalid** —
None axes are skipped. Returns ordered error messages with literal text
`"Invalid {axis} policy: '{id}'"`. Pin the exact format.

### `is_valid_*` and `get_*`

Three pairs, one per axis. `is_valid_*` returns False until `load` runs.
`get_*` returns `None` for unknown ids.
