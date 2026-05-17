"""PROJ-431 Phase 3 — FighterWing tests (RED).

Coverage:
- Construction: identity (id, owner_id, location, display_name).
- Ship roster: ``ships: list[ShipInstance]`` lives directly on the wing.
- ``to_dict()`` / ``from_dict()`` round-trip via the polymorphic
  :meth:`DeployedGroup.from_dict` dispatcher.
- DeployedGroup base type (sibling-of-Fleet) discriminates against
  Fleet at compile time — ``isinstance(wing, Fleet) is False``.
- Polymorphic dispatch: ``DeployedGroup.from_dict({"type": "fighter_wing", ...})``
  returns a :class:`FighterWing`.
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.data.deployed_group import DeployedGroup, FighterWing
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance


def _fighter_ship(design_id: str = "fighter_a", owner_id: int = 0) -> ShipInstance:
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
                            "abilities": {"StructuralIntegrity": {"hp": 12}},
                        },
                    ],
                },
            },
        },
    )


class TestFighterWingConstruction:
    def test_minimal_construction_has_identity(self):
        wing = FighterWing(
            group_id=200001,
            owner_id=3,
            location=HexCoord(2, 1),
        )
        assert wing.id == 200001
        assert wing.owner_id == 3
        assert wing.location == HexCoord(2, 1)
        assert wing.display_name == ""
        assert "200001" in wing.name

    def test_explicit_display_name(self):
        wing = FighterWing(
            group_id=5,
            owner_id=0,
            location=HexCoord(0, 0),
            display_name="Alpha Wing",
        )
        assert wing.display_name == "Alpha Wing"
        assert wing.name == "Alpha Wing"

    def test_empty_ships_by_default(self):
        wing = FighterWing(group_id=1, owner_id=0, location=HexCoord(0, 0))
        assert wing.ships == []


class TestFighterWingIsNotFleet:
    def test_fighter_wing_is_not_a_fleet(self):
        wing = FighterWing(group_id=1, owner_id=0, location=HexCoord(0, 0))
        assert not isinstance(wing, Fleet)
        assert isinstance(wing, DeployedGroup)


class TestFighterWingRoster:
    def test_can_append_ships_directly(self):
        wing = FighterWing(group_id=1, owner_id=0, location=HexCoord(0, 0))
        wing.ships.append(_fighter_ship("fa"))
        wing.ships.append(_fighter_ship("fb"))
        assert len(wing.ships) == 2
        assert wing.ships[0].design_id == "fa"
        assert wing.ships[1].design_id == "fb"


class TestFighterWingSerialisation:
    def test_to_dict_records_type_discriminator(self):
        wing = FighterWing(group_id=1, owner_id=0, location=HexCoord(0, 0))
        data = wing.to_dict()
        assert data.get("type") == "fighter_wing"

    def test_to_dict_round_trip_empty(self):
        wing = FighterWing(
            group_id=7,
            owner_id=2,
            location=HexCoord(-1, 3),
            display_name="Outer Wing",
        )
        data = wing.to_dict()
        restored = DeployedGroup.from_dict(data)
        assert isinstance(restored, FighterWing)
        assert restored.id == wing.id
        assert restored.owner_id == wing.owner_id
        assert restored.location == wing.location
        assert restored.display_name == "Outer Wing"
        assert restored.ships == []

    def test_to_dict_round_trip_with_ships(self):
        wing = FighterWing(group_id=8, owner_id=1, location=HexCoord(0, 0))
        wing.ships.append(_fighter_ship("xa", owner_id=1))
        wing.ships.append(_fighter_ship("xb", owner_id=1))

        data = wing.to_dict()
        restored = DeployedGroup.from_dict(data)
        assert isinstance(restored, FighterWing)
        assert len(restored.ships) == 2
        assert {s.design_id for s in restored.ships} == {"xa", "xb"}
