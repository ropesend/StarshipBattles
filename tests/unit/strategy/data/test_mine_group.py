"""PROJ-431 Phase 2 — MineGroup tests (RED).

Coverage:
- Construction: identity (id, owner_id, location, display_name).
- Mine inventory: ``mines: list[CarriedVehicle]`` lives directly on the
  group; no synthetic carrier ShipInstance.
- Sensitivity / threshold defaults + setter behaviour.
- Mine positions + scatter seed round-trip.
- ``to_dict()`` / ``from_dict()`` round-trip.
- DeployedGroup base type (sibling-of-Fleet) discriminates against
  Fleet at compile time — ``isinstance(mg, Fleet) is False``.
"""
from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.deployed_group import DeployedGroup, MineGroup
from game.strategy.data.fleet import Fleet


def _mine_cv(design_id: str = "mine_small", damage: float = 50.0) -> CarriedVehicle:
    return CarriedVehicle(
        design_id=design_id,
        design_data={
            "name": design_id,
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "hull", "abilities": {"StructuralIntegrity": {"hp": 30}}},
                        {"id": "warhead", "abilities": {"Warhead": {"damage": damage}}},
                    ],
                },
            },
        },
        vehicle_type="mine",
        mass=5.0,
        current_hp=30,
    )


class TestMineGroupConstruction:
    def test_minimal_construction_has_identity(self):
        mg = MineGroup(
            group_id=100001,
            owner_id=3,
            location=HexCoord(2, 1),
        )
        assert mg.id == 100001
        assert mg.owner_id == 3
        assert mg.location == HexCoord(2, 1)
        assert mg.display_name == ""
        # Defaulted name still resolves a fallback label.
        assert "100001" in mg.name

    def test_explicit_display_name(self):
        mg = MineGroup(
            group_id=5,
            owner_id=0,
            location=HexCoord(0, 0),
            display_name="Border Field",
        )
        assert mg.display_name == "Border Field"
        assert mg.name == "Border Field"

    def test_empty_mines_by_default(self):
        mg = MineGroup(group_id=1, owner_id=0, location=HexCoord(0, 0))
        assert mg.mines == []

    def test_sensitivity_threshold_defaults(self):
        mg = MineGroup(group_id=1, owner_id=0, location=HexCoord(0, 0))
        assert mg.sensitivity == "MED"
        assert mg.expected_hit_chance_threshold == pytest.approx(0.30)

    def test_mine_positions_and_scatter_seed_defaults(self):
        mg = MineGroup(group_id=1, owner_id=0, location=HexCoord(0, 0))
        assert mg.mine_positions == []
        assert mg.scatter_seed is None


class TestMineGroupIsNotFleet:
    def test_mine_group_is_not_a_fleet(self):
        """``DeployedGroup`` is a sibling of ``Fleet``, not a subclass."""
        mg = MineGroup(group_id=1, owner_id=0, location=HexCoord(0, 0))
        assert not isinstance(mg, Fleet)
        assert isinstance(mg, DeployedGroup)


class TestMineGroupInventory:
    def test_can_load_mines_directly(self):
        mg = MineGroup(group_id=1, owner_id=0, location=HexCoord(0, 0))
        mg.mines.append(_mine_cv("mine_a"))
        mg.mines.append(_mine_cv("mine_b"))
        assert len(mg.mines) == 2
        assert mg.mines[0].design_id == "mine_a"
        assert mg.mines[1].design_id == "mine_b"


class TestMineGroupSerialisation:
    def test_to_dict_round_trip_empty(self):
        mg = MineGroup(
            group_id=7,
            owner_id=2,
            location=HexCoord(-1, 3),
            display_name="Outer Ring",
        )
        data = mg.to_dict()
        restored = MineGroup.from_dict(data)
        assert restored.id == mg.id
        assert restored.owner_id == mg.owner_id
        assert restored.location == mg.location
        assert restored.display_name == "Outer Ring"
        assert restored.sensitivity == "MED"
        assert restored.expected_hit_chance_threshold == pytest.approx(0.30)
        assert restored.mines == []
        assert restored.mine_positions == []
        assert restored.scatter_seed is None

    def test_to_dict_round_trip_with_mines(self):
        mg = MineGroup(group_id=8, owner_id=1, location=HexCoord(0, 0))
        mg.mines.append(_mine_cv("a"))
        mg.mines.append(_mine_cv("b"))
        mg.sensitivity = "HIGH"
        mg.expected_hit_chance_threshold = 0.55
        mg.mine_positions = [(1.0, 2.0), (3.0, 4.0)]
        mg.scatter_seed = 1234

        data = mg.to_dict()
        restored = MineGroup.from_dict(data)
        assert len(restored.mines) == 2
        assert {m.design_id for m in restored.mines} == {"a", "b"}
        assert restored.sensitivity == "HIGH"
        assert restored.expected_hit_chance_threshold == pytest.approx(0.55)
        assert restored.mine_positions == [(1.0, 2.0), (3.0, 4.0)]
        assert restored.scatter_seed == 1234

    def test_to_dict_records_type_discriminator(self):
        """``to_dict()`` records a ``type`` field so an Empire-level
        polymorphic deserialiser can pick the correct DeployedGroup
        subclass.
        """
        mg = MineGroup(group_id=1, owner_id=0, location=HexCoord(0, 0))
        data = mg.to_dict()
        assert data.get("type") == "mine_group"
