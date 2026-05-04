# PROJ-335 — Phase 1 Checklist

Characterization tests for five `game/strategy/data/` files. Per-file
sections; mark items as you go.

---

## Pre-flight: verify existing coverage

- [ ] Read `tests/unit/strategy/data/test_facility_activation.py` end-to-end and list which `PlanetaryFacility` behaviors it pins.
- [ ] Read `tests/unit/strategy/data/test_facility_construction_queue.py`; list pinned behaviors.
- [ ] Read `tests/unit/strategy/data/test_facility_resource_tracking.py`; list pinned behaviors.
- [ ] Read `tests/unit/strategy/data/test_population_model.py` `TestSpeciesPopulation` class; if it covers construction defaults + `from_dict` happy path + missing-key rejection, **skip the species_population test file** and log in `decisions.md`.
- [ ] Read `tests/unit/strategy/data/test_superweapon_orders.py` and `test_fleet_order_resolution.py`; list which `Order` branches are already pinned.
- [ ] Confirm no existing standalone tests for `squadron.py` or `group_policy_registry.py` (expected: none).

---

## `planetary_facility.py` (target ~6–8 new tests)

New file: `tests/unit/strategy/data/test_planetary_facility_characterization.py`.

- [ ] **simple** `to_dict()` → `from_dict()` round-trip preserves all top-level fields including `consumable_levels` and `component_states`.
- [ ] **simple** `from_dict({})` raises `PersistenceException` (via `require_keys`) — covers missing instance_id/design_id/name/design_data.
- [ ] **simple** `is_shipyard` returns False when `is_operational=False` even with a `space_shipyard` component active (short-circuit).
- [ ] **simple** `is_shipyard` returns True when `is_operational=True` and a `space_shipyard` component is active.
- [ ] **medium** Legacy `resource_levels` key in input dict is accepted by `from_dict` as `consumable_levels`.
- [ ] **medium** Legacy `{'active': bool}` dict shape stored in component_states is unwrapped by `get_activation_state` to a plain bool.
- [ ] **simple** `is_component_active` and `set_component_active` pair: set then read returns the value just set.
- [ ] *(optional)* **medium** Round-trip preserves `construction_queue_paused` flag both True and False.

---

## `species_population.py` (target 0–4 new tests; skip likely)

If the pre-flight check shows full coverage in `TestSpeciesPopulation`, skip
this section and log it in `decisions.md`.

If a new file is needed: `tests/unit/strategy/data/test_species_population_characterization.py`.

- [ ] **simple** `from_dict({'race_id': 'human', 'count': 5})` defaults `happiness` to `0.5`.
- [ ] **simple** `from_dict({'race_id': 'human'})` raises `PersistenceException` (missing required `count`).
- [ ] **simple** Construct with explicit `happiness=0.0` and `count=0` — survives without validation error (pin the no-bounds-check behavior).
- [ ] **simple** Construct with `happiness=1.5` — survives (pins out-of-range acceptance).

---

## `squadron.py` (target ~7–9 new tests)

New file: `tests/unit/strategy/data/test_squadron_characterization.py`.

- [ ] **simple** `add_ship(ship)` is idempotent: adding the same ship twice leaves `len(ships) == 1`.
- [ ] **simple** `remove_ship(ship)` returns True when the ship was present, False otherwise.
- [ ] **simple** `all_ships` returns members concatenated with lone ships in that order.
- [ ] **medium** `to_dict()` omits `spatial_behavior` key when `None`; omits `spatial_behavior_params` key when `{}`.
- [ ] **medium** `to_dict()` round-trip via `from_dict` reconstructs equivalent fields (`spatial_behavior_params == {}` after reload when omitted).
- [ ] **simple** `to_dict()` includes `"type": "squadron"` discriminator.
- [ ] **medium** `from_dict` parses `battle_role` enum value from string form.
- [ ] **simple** Default `node_id` is generated when not supplied (UUID-shaped — assert non-empty / unique across two instances).
- [ ] *(optional)* **medium** Round-trip preserves `flagship` and `lone_ships` (parent class fields, but exercised via Squadron round-trip).

---

## `order_types.py` (target ~10–14 new tests)

New file: `tests/unit/strategy/data/test_order_types_characterization.py`.

- [ ] **simple** `MOVEMENT_ORDER_TYPES` and `ACTION_ORDER_TYPES` are disjoint.
- [ ] **simple** `PLANET_ACTION_ORDER_TYPES ⊆ ACTION_ORDER_TYPES`.
- [ ] **medium** `Order(MOVE, HexCoord(1, 2)).to_dict()['target'] == {'q': 1, 'r': 2}` — pins missing `type` key (asymmetric branch).
- [ ] **medium** `Order(IMPLODE_PLANET, planet_stub).to_dict()['target'] == {'type': 'planet_ref', 'id': 'p1'}`.
- [ ] **medium** `Order(SELF_DESTRUCT, ['s1', 's2']).to_dict()['target'] == {'type': 'ship_id_list', 'value': ['s1', 's2']}`.
- [ ] **medium** `Order(OPEN_WARP_POINT, {...}).to_dict()['target'] == {'type': 'warp_params', 'value': {...}}`.
- [ ] **medium** `Order(MOVE, planet_stub).to_dict()['target'] == {'type': 'planet_ref', 'id': 'p1'}` — generic Planet branch.
- [ ] **medium** `Order(MOVE, fleet_stub).to_dict()['target'] == {'type': 'fleet_ref', 'id': 'f1'}` — generic Fleet branch.
- [ ] **medium** `Order(COLONIZE, {planet_id, population, cargo}).to_dict()['target'] == {'type': 'colonize_params', planet_id, population, cargo}`.
- [ ] **medium** `Order(MOVE, {'arbitrary': 'dict'}).to_dict()['target'] == {'type': 'dict', 'value': {'arbitrary': 'dict'}}` — catch-all dict branch.
- [ ] **medium** `Order(MOVE, 42).to_dict()['target'] == {'type': 'raw', 'value': '42'}` — else branch stringifies.
- [ ] **simple** `execution_progress=0` is omitted from `to_dict()`; `execution_progress=5` is included.
- [ ] **medium** `Order.from_dict({'type': 'COLONIZE', 'target': {'type': 'dict', 'value': {'foo': 'bar'}}})` unwraps to `target == {'foo': 'bar'}`; default `execution_progress == 0`.
- [ ] **medium** `Order.from_dict` does NOT round-trip a HexCoord-emitted dict alone (assert what it does emit / raise — document with a docstring).
- [ ] **simple** `__repr__` has two forms: with and without `execution_progress`.

---

## `group_policy_registry.py` (target ~8–10 new tests)

New file: `tests/unit/strategy/data/test_group_policy_registry_characterization.py`.

- [ ] **simple** Fresh registry: `is_valid_targeting/movement/retreat` all return False; `_loaded` is False.
- [ ] **simple** `validate_policy(CombatPolicy())` (all axes None) returns `[]` — None means inherit, not invalid.
- [ ] **medium** `load(tmp_path / 'policies.json')` with a real JSON file populates all three axes; `_loaded` becomes True.
- [ ] **medium** `load(tmp_path / 'missing.json')` (file does not exist) does not raise; sets `_loaded=True` with empty axes (load_json default fallback).
- [ ] **medium** After loading, `is_valid_targeting('known_id')` is True; `is_valid_targeting('unknown')` is False.
- [ ] **medium** After loading, `get_targeting('known_id')` returns the policy dict; `get_targeting('unknown')` returns `None`.
- [ ] **medium** `validate_policy(CombatPolicy(targeting='bogus'))` against a loaded registry returns exactly `["Invalid targeting policy: 'bogus'"]` (pin exact string).
- [ ] **medium** `validate_policy(CombatPolicy(targeting='bogus', movement='also_bogus'))` returns two messages in axis order: targeting first, then movement.
- [ ] *(optional)* **simple** Repeat for `is_valid_movement` / `is_valid_retreat` parametrized.

---

## Verification

- [ ] Run each new test file in isolation: `pytest tests/unit/strategy/data/test_<file>_characterization.py -v`.
- [ ] Run the strategy data folder: `pytest tests/unit/strategy/data/ -v`.
- [ ] Run the full sharded suite: `python Tools/test_sharded/test_sharded.py`.
- [ ] Lint clean on all touched test files.
- [ ] No production file in `game/strategy/data/` is modified.

---

## Phase Completion (commits)

One commit per production-file/test-file pair (D-006). Suggested order:

- [ ] Commit 1: `test: characterize species_population.py` (or skip-and-log in decisions.md if not needed).
- [ ] Commit 2: `test: characterize planetary_facility.py round-trip and is_shipyard`.
- [ ] Commit 3: `test: characterize squadron.py add/remove and round-trip`.
- [ ] Commit 4: `test: characterize order_types.py to_dict matrix`.
- [ ] Commit 5: `test: characterize group_policy_registry.py load and validate`.

- [ ] Append any newly-discovered quirks to `decisions.md` D-007 list.
- [ ] Move project state to "complete" or hand off per arc master plan.
