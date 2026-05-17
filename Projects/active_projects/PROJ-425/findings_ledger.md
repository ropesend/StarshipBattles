# PROJ-425 — Findings Ledger

## Phase 0 — Characterization (2026-05-17)

### Live manager / accessor names on `ShipInstance` (Task 0.1)

Grep of `game/strategy/data/ship_instance.py`:

- `self._resource_mgr` — set in `__post_init__` to `ShipConsumableManager(self)` (line 179)
- `self._cargo_mgr` — set in `__post_init__` to `ShipCargoManager(self)` (line 180)
- `self._display_fmt` — set in `__post_init__` to `ShipDisplayFormatter(self)` (line 181)
- `self._bridge` — set in `__post_init__` to `ShipInstanceBridge(self)` (line 182)

Grep of `game/strategy/services/ship_instance_write_service.py`:

- `set_cargo_amount` queries `getattr(instance, "_cargo_manager", None)` (line 67)
- `set_consumable_level` queries `getattr(instance, "_consumable_manager", None)` (line 76)

### Divergence — Phase 4 standardization input

The write service queries **`_cargo_manager` / `_consumable_manager`**, but the entity initializes **`_cargo_mgr` / `_resource_mgr`**. These getattr lookups in `ShipInstanceWriteService.set_cargo_amount` / `set_consumable_level` therefore always return `None` today and the code path always falls through to the direct-dict assignment. The "manager exists" branch is dead code.

**Phase 4 prep must reconcile these names** — rename entity fields to `_cargo_manager` / `_consumable_manager` to match the write service expectation (the write-service naming is the "manager" suffix used by docs). The display/bridge delegates are `_display_fmt` / `_bridge` and the write service does not reference those, so they stay.

### Baseline test pass counts (Task 0.7)

Run on `proj/PROJ-425/main` HEAD (= `proj/PROJ-424/main` tip `70c1f4b70`):

- `pytest tests/unit/strategy/ship_instance/` → **122 passed**
- `pytest tests/unit/strategy/services/test_ship_instance_write_service.py tests/unit/strategy/fleets/test_ship_instance_roundtrip.py tests/unit/strategy/fleets/test_ship_instance_components.py` → **21 passed**
- Combined focused suite → **143 passed**

No pre-existing failures.

### Baseline LOC

`game/strategy/data/ship_instance.py` → **845 LOC** (matches the design.md baseline).

### Existing test coverage audit (Tasks 0.2 - 0.6)

The existing tests in `tests/unit/strategy/ship_instance/` already cover all required characterization surfaces:

- **`create(...)` factory** (Task 0.2): `test_registries_di.py::TestShipInstanceCreateWithRegistries`.
- **Stats-cache hit/miss/invalidate** (Task 0.3): `test_component_toggles.py::TestCacheInvalidation` and `test_registries_di.py::TestGetCalculatedStatsWithRegistries::test_raises_when_registries_none`.
- **Component-toggle invalidation** (Task 0.4): `test_component_toggles.py::TestSetComponentEnabled::test_set_component_enabled_invalidates_cache`.
- **Bridge / serializer round-trip** (Task 0.5): `test_ship_instance_bridge.py`, `test_ship_instance_serializer.py`, `test_serialization.py::TestFromDictSerialization::test_from_dict_then_to_dict_round_trip`, `test_serialization.py::TestClonePreservation`.
- **Convenience-method coverage** (Task 0.6): `test_convenience_methods.py`, `test_capacity_levels.py`.

**No new characterization tests needed** — coverage is already sufficient. Phase 0 is a read-only confirmation phase. Phases 1-5 will add their own TDD anchor tests.

## Phase 1 — Stats-calculation extraction (2026-05-17)

Created `game/strategy/data/ship_stats_cache.py` (66 LOC) with `ShipStatsCache.calculate` / `get_or_compute` / `invalidate`. `ShipInstance.get_calculated_stats` and `invalidate_stats_cache` now delegate to the helper. `_cached_stats` storage stays on the entity (Guardrail #2).

- New test file: `tests/unit/strategy/ship_instance/test_ship_stats_cache.py` (6 tests).
- Focused suite: **149 passed** (143 baseline + 6 new).
- `ship_instance.py` LOC: 830 (down from 845; -15).

## Phase 2 — Component/layer inspection extraction (2026-05-17)

Added to `game/strategy/services/component_inspector.py`:

- `iter_components_by_layer(ship)` — extracted from `ShipInstance.iter_all_components_by_layer`.
- `damaged_components_by_layer(ship)` — extracted from `ShipInstance.get_damaged_components_by_layer`.
- `count_damaged_components(ship)` — extracted from `ShipInstance.get_damaged_component_count`.
- `lookup_design_max_hp(ship, comp_id)` — extracted from `ShipInstance._lookup_design_max_hp` (private helper, no production callers).

`ShipInstance` methods now delegate. The entity drops ~96 LOC of inspection logic.

- New test file: `tests/unit/strategy/services/test_component_inspector_layers.py` (6 tests, all green).
- Focused suite: **155 passed**.
- `ship_instance.py` LOC: **722** (was 830; -108 this phase, -123 cumulative).
- `component_inspector.py` LOC: 537 (was 391; +146). Above the 500-LOC guideline but already-shared infrastructure module — split deferred as the additions are cohesive ship-introspection helpers; revisit if it grows further.

## Phase 3 — Factory extraction (2026-05-17)

Created `game/strategy/services/ship_instance_factory.py` (166 LOC):

- `ShipInstanceFactory.create(...)` — extracted body of `ShipInstance.create(...)`.
- `build_full_hp_components_from_design(...)` — extracted from the module-level `_build_full_hp_components_from_design` helper in `ship_instance.py`.

`ShipInstance.create(...)` retained as a thin shim per TD-06 Guardrail #1.

Grep gate `rg -n "ShipInstance\.create\(" game tests` → 33 occurrences across 16 files. Shim must remain.

Fixed one broken import: `tests/unit/strategy/test_ship_instance_damage.py` had `from game.strategy.data.ship_instance import _build_full_hp_components_from_design`; redirected to `ship_instance_factory` as `build_full_hp_components_from_design`.

- New test file: `tests/unit/strategy/services/test_ship_instance_factory.py` (7 tests).
- `tests/unit/strategy/` → **4557 passed**.
- `ship_instance.py` LOC: **629** (was 722; -93 this phase, -216 cumulative).
