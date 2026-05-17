"""PROJ-431 Phase 3 — SatelliteConstellation tests (RED).

Mirror of test_fighter_wing.py for the satellite family. Same shape,
same contract, different concrete type.
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.data.deployed_group import DeployedGroup, SatelliteConstellation
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance


def _satellite_ship(design_id: str = "sat_a", owner_id: int = 0) -> ShipInstance:
    return ShipInstance(
        instance_id=f"{design_id}_inst",
        design_id=design_id,
        name=design_id,
        owner_id=owner_id,
        design_data={
            "name": design_id,
            "layers": {
                "CORE": {
                    "components": [
                        {
                            "id": "hull",
                            "abilities": {"StructuralIntegrity": {"hp": 8}},
                        },
                    ],
                },
            },
        },
    )


class TestSatelliteConstellationConstruction:
    def test_minimal_construction_has_identity(self):
        c = SatelliteConstellation(
            group_id=300001,
            owner_id=3,
            location=HexCoord(2, 1),
        )
        assert c.id == 300001
        assert c.owner_id == 3
        assert c.location == HexCoord(2, 1)
        assert c.display_name == ""
        assert "300001" in c.name

    def test_explicit_display_name(self):
        c = SatelliteConstellation(
            group_id=5,
            owner_id=0,
            location=HexCoord(0, 0),
            display_name="Border Sats",
        )
        assert c.display_name == "Border Sats"
        assert c.name == "Border Sats"

    def test_empty_ships_by_default(self):
        c = SatelliteConstellation(group_id=1, owner_id=0, location=HexCoord(0, 0))
        assert c.ships == []


class TestSatelliteConstellationIsNotFleet:
    def test_constellation_is_not_a_fleet(self):
        c = SatelliteConstellation(group_id=1, owner_id=0, location=HexCoord(0, 0))
        assert not isinstance(c, Fleet)
        assert isinstance(c, DeployedGroup)


class TestSatelliteConstellationRoster:
    def test_can_append_ships_directly(self):
        c = SatelliteConstellation(group_id=1, owner_id=0, location=HexCoord(0, 0))
        c.ships.append(_satellite_ship("sa"))
        c.ships.append(_satellite_ship("sb"))
        assert len(c.ships) == 2
        assert c.ships[0].design_id == "sa"
        assert c.ships[1].design_id == "sb"


class TestSatelliteConstellationSerialisation:
    def test_to_dict_records_type_discriminator(self):
        c = SatelliteConstellation(group_id=1, owner_id=0, location=HexCoord(0, 0))
        data = c.to_dict()
        assert data.get("type") == "satellite_constellation"

    def test_to_dict_round_trip_empty(self):
        c = SatelliteConstellation(
            group_id=7,
            owner_id=2,
            location=HexCoord(-1, 3),
            display_name="Outer Sats",
        )
        data = c.to_dict()
        restored = DeployedGroup.from_dict(data)
        assert isinstance(restored, SatelliteConstellation)
        assert restored.id == c.id
        assert restored.owner_id == c.owner_id
        assert restored.location == c.location
        assert restored.display_name == "Outer Sats"
        assert restored.ships == []

    def test_to_dict_round_trip_with_ships(self):
        c = SatelliteConstellation(group_id=8, owner_id=1, location=HexCoord(0, 0))
        c.ships.append(_satellite_ship("xa", owner_id=1))
        c.ships.append(_satellite_ship("xb", owner_id=1))

        data = c.to_dict()
        restored = DeployedGroup.from_dict(data)
        assert isinstance(restored, SatelliteConstellation)
        assert len(restored.ships) == 2
        assert {s.design_id for s in restored.ships} == {"xa", "xb"}
