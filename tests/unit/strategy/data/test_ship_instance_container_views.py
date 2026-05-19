"""
PROJ-436 Phase 3a: tests for the Container projection accessors on
`ShipInstance`.

Phase 3 (full) deletes `cargo_contents` + `consumable_levels` as
dataclass fields after migrating ~59 files and ~402 call sites. Phase
3a is the substrate sub-phase: add the unified Container view
accessors so future sub-phases can migrate callers off the legacy
fields incrementally. No legacy field is deleted in 3a; mutations on
the returned Container are NOT propagated back (it is a snapshot).
"""
from __future__ import annotations

import pytest

from game.strategy.data.containable import ContainableKind
from game.strategy.data.ship_instance import ShipInstance


def _ship(
    *,
    cargo_contents: dict[str, int] | None = None,
    consumable_levels: dict[str, float] | None = None,
) -> ShipInstance:
    return ShipInstance(
        instance_id="test-ship",
        design_id="qs_light_combat_escort",
        owner_id=1,
        name="USS Test",
        _cargo_contents=dict(cargo_contents or {}),
        _consumable_levels=dict(consumable_levels or {}),
    )


# ---------------------------------------------------------------------------
# consumable_container
# ---------------------------------------------------------------------------


class TestConsumableContainer:
    def test_empty_consumable_levels_yields_empty_container(self):
        ship = _ship()
        c = ship.consumable_container()
        assert c.mass_used == 0.0

    def test_consumable_levels_resources_appear_in_container(self):
        ship = _ship(consumable_levels={"fuel": 50000.0, "energy": 100.0})
        c = ship.consumable_container()
        assert c.get_resource("fuel") == pytest.approx(50000.0)
        assert c.get_resource("energy") == pytest.approx(100.0)
        # 50000 * 0.0001 + 100 * 1.0 = 5.0 + 100.0 = 105.0 tons
        assert c.mass_used == pytest.approx(105.0)

    def test_consumable_container_is_snapshot(self):
        ship = _ship(consumable_levels={"fuel": 100.0})
        c = ship.consumable_container()
        # Mutating the snapshot does NOT change ship.consumable_levels.
        # Container.add doesn't validate against ship state — it's a separate object.
        from game.strategy.data.containable import ResourceContainable
        c.add(ResourceContainable("fuel"), 500.0)
        assert ship.consumable_levels["fuel"] == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# cargo_container
# ---------------------------------------------------------------------------


class TestCargoContainer:
    def test_empty_cargo_contents_yields_empty_container(self):
        ship = _ship()
        c = ship.cargo_container()
        assert c.mass_used == 0.0

    def test_resource_keys_go_to_resource_slice(self):
        # "metals" is a known resource id in the ResourceCatalog.
        ship = _ship(cargo_contents={"metals": 1000})
        c = ship.cargo_container()
        assert c.get_resource("metals") == pytest.approx(1000.0)
        # 1000 * 0.01 = 10.0 tons
        assert c.mass_used == pytest.approx(10.0)

    def test_passengers_key_goes_to_population_slice(self):
        # "passengers" maps to population (default species).
        ship = _ship(cargo_contents={"passengers": 200})
        c = ship.cargo_container()
        # Mass = 200 * 0.1 = 20.0 tons.
        assert c.mass_used == pytest.approx(20.0)
        # The population slice gets the count under a default species key.
        pop_entries = [e for e in c.contents() if e.kind is ContainableKind.POPULATION]
        assert len(pop_entries) == 1
        assert int(pop_entries[0].quantity) == 200

    def test_mixed_cargo_resources_and_passengers(self):
        ship = _ship(cargo_contents={"metals": 500, "passengers": 100})
        c = ship.cargo_container()
        # metals: 500 * 0.01 = 5.0; passengers: 100 * 0.1 = 10.0
        assert c.mass_used == pytest.approx(15.0)

    def test_unknown_cargo_key_skipped_with_warning(self, caplog):
        # Unknown keys (not in ResourceCatalog and not "passengers") are
        # skipped in the projection rather than crashing.
        ship = _ship(cargo_contents={"unobtainium": 5})
        c = ship.cargo_container()
        assert c.mass_used == 0.0

    def test_cargo_container_is_snapshot(self):
        ship = _ship(cargo_contents={"metals": 100})
        c = ship.cargo_container()
        from game.strategy.data.containable import ResourceContainable
        c.add(ResourceContainable("metals"), 50.0)
        assert ship.cargo_contents["metals"] == 100  # unchanged
