"""
Unit tests for fleet hierarchy DTOs.

Phase 9: TaskForceInfo and SquadronInfo DTOs for UI display.
"""

from unittest.mock import MagicMock


def _make_ship(name, role="line_combatant"):
    ship = MagicMock()
    ship.name = name
    ship.instance_id = f"id_{name}"
    ship.design_id = f"design_{name}"
    ship.effective_role = role
    ship.design_data = {"ship_class": "Cruiser"}
    ship.is_combat_capable.return_value = True
    ship.get_hp_percentage.return_value = 1.0
    return ship


class TestSquadronInfo:
    """Tests for SquadronInfo DTO."""

    def test_squadron_info_from_squadron(self):
        """SquadronInfo.from_squadron creates DTO from domain object."""
        from game.strategy.facade.dto.fleet_hierarchy_dto import SquadronInfo
        from game.strategy.data.squadron import Squadron
        from game.strategy.data.fleet_hierarchy import CombatPolicy, BattleRole

        sq = Squadron(
            name="Battle Line",
            policy=CombatPolicy(targeting="focus_strongest"),
            battle_role=BattleRole.MAIN_BODY,
            spatial_behavior="battle_line",
        )
        s1 = _make_ship("Ship1")
        sq.add_ship(s1)

        dto = SquadronInfo.from_squadron(sq)

        assert dto.name == "Battle Line"
        assert dto.node_id == sq.node_id
        assert dto.ship_count == 1
        assert dto.battle_role == "main_body"
        assert dto.targeting == "focus_strongest"
        assert dto.spatial_behavior == "battle_line"

    def test_squadron_info_is_frozen(self):
        """SquadronInfo is immutable."""
        from game.strategy.facade.dto.fleet_hierarchy_dto import SquadronInfo
        from game.strategy.data.squadron import Squadron

        sq = Squadron(name="Test")
        dto = SquadronInfo.from_squadron(sq)

        import pytest
        with pytest.raises(AttributeError):
            dto.name = "Changed"


class TestTaskForceInfo:
    """Tests for TaskForceInfo DTO."""

    def test_task_force_info_from_task_force(self):
        """TaskForceInfo.from_task_force creates DTO with squadrons."""
        from game.strategy.facade.dto.fleet_hierarchy_dto import TaskForceInfo
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron
        from game.strategy.data.fleet_hierarchy import CombatPolicy, BattleRole

        tf = TaskForce(
            name="Alpha Strike",
            policy=CombatPolicy(targeting="focus_strongest", movement="advance"),
            battle_role=BattleRole.MAIN_BODY,
        )
        sq = Squadron(name="Line", battle_role=BattleRole.MAIN_BODY)
        sq.add_ship(_make_ship("Ship1"))
        sq.add_ship(_make_ship("Ship2"))
        tf.add_squadron(sq)

        dto = TaskForceInfo.from_task_force(tf)

        assert dto.name == "Alpha Strike"
        assert dto.battle_role == "main_body"
        assert dto.targeting == "focus_strongest"
        assert dto.movement == "advance"
        assert len(dto.squadrons) == 1
        assert dto.squadrons[0].name == "Line"
        assert dto.total_ship_count == 2

    def test_task_force_info_includes_lone_ships(self):
        """TaskForceInfo counts lone ships."""
        from game.strategy.facade.dto.fleet_hierarchy_dto import TaskForceInfo
        from game.strategy.data.task_force import TaskForce

        tf = TaskForce(name="Alpha")
        tf.add_lone_ship(_make_ship("Lone"))

        dto = TaskForceInfo.from_task_force(tf)

        assert dto.lone_ship_count == 1
        assert dto.total_ship_count == 1


class TestShipInfoRole:
    """Tests that ShipInfo includes design role."""

    def test_ship_info_includes_effective_role(self):
        """ShipInfo includes the effective_role field."""
        from game.strategy.facade.dto.fleet_hierarchy_dto import ShipInfoExtended

        ship = _make_ship("TestShip", role="carrier")
        dto = ShipInfoExtended.from_ship_instance(ship)

        assert dto.effective_role == "carrier"
