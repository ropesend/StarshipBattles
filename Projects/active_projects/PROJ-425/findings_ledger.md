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
