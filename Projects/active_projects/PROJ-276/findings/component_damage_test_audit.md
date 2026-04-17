# `component_damage` Test-site Audit — Phase 1 Task 1.5

**Date:** 2026-04-16

Full list from `grep component_damage tests/` (29 hits across 11
files):

| File | Line | Snippet | Category |
|---|---|---|---|
| `tests/fixtures/strategy_entities.py` | 314 | `component_damage={"laser_1": 5},` | **RENAME** — fixture construction, easy swap to `components=` |
| `tests/integration/strategy/turn_engine/test_components.py` | 304, 311 | `component_damage={}` | **DELETE** — empty-dict defaults, just remove arg |
| `tests/unit/simulation/systems/test_ship_design_stats.py` | 118 | `component_damage={'bridge': 0}` | **REWRITE** — must pass `components` with `ComponentState(..., current_hp=0)` |
| `tests/unit/strategy/test_ship_instance_damage.py` | 47, 266 | `instance.component_damage = {...}` | **REWRITE** — asserts lossy-flatten behavior; must move to per-instance |
| `tests/unit/strategy/test_ship_display_formatter.py` | 28 | `ship.component_damage = {}` | **DELETE** or **RENAME** — sets empty; check whether formatter tests assert anything from the dict |
| `tests/unit/strategy/ship_stats/test_edge_cases.py` | 379, 401, 507 | `component_damage={...}` | **REWRITE** — targets the dead `ShipStatsCalculator` directly; these tests die with the module |
| `tests/unit/strategy/test_fleet_capability_calculator_di.py` | 142 | `'component_damage': {}` | **DELETE** — empty-dict in save-data simulation |
| `tests/integration/save_load/test_roundtrip_ships.py` | 67-70 | `test_component_damage`, `create_test_ship_instance(component_damage=...)` | **REWRITE** — must test `components` round-trip, not `component_damage` |
| `tests/unit/strategy/ship_instance/test_validation.py` | 102 | `assert ship.component_damage == {}` | **DELETE** — asserts field existence; field gone after Phase 6 |
| `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` | 21, 47, 115, 121-122 | `component_damage={'comp_1': 50}` + assertions | **REWRITE** — serializer tests must cover `components` round-trip |
| `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py` | 20, 99-107 | `test_captures_component_damage` + assertions | **REWRITE** — bridge tests must assert per-instance `components` output |
| `tests/unit/strategy/ship_instance/test_cost_queries.py` | 138 | `ship.component_damage['warp_drive'] = 50` | **REWRITE** — cost queries derive from calculated stats; must go via per-instance |
| `tests/integration/resource_system/test_resource_pipeline.py` | 276 | `'component_damage': {'engine_0': 50}` | **REWRITE** — save-data integration |
| `tests/unit/strategy/services/test_ship_stats_pod_storage.py` | 92, 95 | `ShipStatsCalculator.calculate_stats(..., component_damage=...)` | **DELETE** if strategy ShipStatsCalculator deleted, else REWRITE |

### Also: the entire test directory `tests/unit/strategy/ship_stats/`

`tests/unit/strategy/ship_stats/{test_warp,test_toggles,test_resources,...}.py`
exercise the dead strategy `ShipStatsCalculator` directly (37 import
sites). **If the dead module is deleted, this test directory goes
with it.** It's a pure duplicate — coverage of the real code path
(`ship_design_stats.py`) already lives in
`tests/unit/simulation/systems/test_ship_design_stats.py`. Verifying
parity before deletion is part of Phase 2.

## Categories

- **DELETE**: 4 sites — empty-dict args, just remove
- **RENAME**: 1 site — direct field rename to `components={}`
- **REWRITE**: 11 sites — require building `ComponentState` objects
  with correct `instance_index` per `component_id`
- **MODULE-SCOPE DELETE**: `tests/unit/strategy/ship_stats/*` (if dead
  module deleted) — roughly 37 file-level sites become irrelevant

## No tests assert lossy-flatten behavior as a feature

Scanned all 29 occurrences: none assert that two instances of the same
component_id must flatten to one HP value. Every test either uses
single-instance ships or is checking per-id (not per-instance)
semantics that map cleanly to
`components[component_state_key(id, 0)].current_hp`.

This means Phase 7 test migration is mechanical — no behavioral tests
need to be rethought. This is good news.
