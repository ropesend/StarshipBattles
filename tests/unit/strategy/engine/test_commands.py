# -*- coding: utf-8 -*-
"""Unit tests for game/strategy/engine/commands.py

Tests cover:
- Command dataclass instantiation and field validation
- CommandType enum behavior
- Command name property
- All command types with various inputs
"""
import pytest
from game.core.hex_math import HexCoord
from game.strategy.engine.commands import (
    Command,
    CommandType,
    IssueColonizeCommand,
    IssueMoveCommand,
    # NOTE: IssueBuildShipCommand removed in PROJ-208 (dead code)
    IssueInterceptCommand,
    IssueJoinFleetCommand,
    QueueColonizeMissionCommand,
    ClearFleetOrdersCommand,
    IssueTransferCommand,
    IssueImplodePlanetCommand,
    IssueStellerateStarCommand,
    IssueOpenWarpPointCommand,
    IssueCloseWarpPointCommand,
    IssueCreateDysonSphereCommand,
    IssueSelfDestructCommand,
    QueueImplodePlanetMissionCommand,
    QueueStellerateStarMissionCommand,
    QueueOpenWarpPointMissionCommand,
    QueueCloseWarpPointMissionCommand,
    QueueCreateDysonSphereMissionCommand,
    IssueWarpCommand,  # PROJ-187
)


class TestCommandBase:
    """Tests for Command base class."""

    def test_command_name_property(self):
        """Command.name should return the class name."""
        cmd = IssueColonizeCommand(fleet_id=1, planet_id=2)
        assert cmd.name == "IssueColonizeCommand"

class TestIssueColonizeCommand:
    """Tests for IssueColonizeCommand."""

    def test_create_with_specific_planet(self):
        """IssueColonizeCommand should store fleet_id and planet_id."""
        cmd = IssueColonizeCommand(fleet_id=10, planet_id=20)
        assert cmd.fleet_id == 10
        assert cmd.planet_id == 20
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_create_with_any_planet(self):
        """IssueColonizeCommand should allow None planet_id for 'any planet'."""
        cmd = IssueColonizeCommand(fleet_id=5)
        assert cmd.fleet_id == 5
        assert cmd.planet_id is None

    def test_default_planet_id_is_none(self):
        """planet_id should default to None when not provided."""
        cmd = IssueColonizeCommand(fleet_id=1)
        assert cmd.planet_id is None


class TestIssueMoveCommand:
    """Tests for IssueMoveCommand."""

    def test_create_with_target_hex(self):
        """IssueMoveCommand should store fleet_id and target_hex."""
        target = HexCoord(5, -3)
        cmd = IssueMoveCommand(fleet_id=7, target_hex=target)
        assert cmd.fleet_id == 7
        assert cmd.target_hex == target
        assert cmd.type == CommandType.ISSUE_ORDER


# NOTE: TestIssueBuildShipCommand removed in PROJ-208 Phase 2 (dead code).
# Use AddToConstructionQueueCommand instead - see test_construction_queue_command_handlers.py


class TestIssueInterceptCommand:
    """Tests for IssueInterceptCommand."""

    def test_create_intercept_command(self):
        """IssueInterceptCommand should store fleet_id and target_fleet_id."""
        cmd = IssueInterceptCommand(fleet_id=3, target_fleet_id=8)
        assert cmd.fleet_id == 3
        assert cmd.target_fleet_id == 8
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_intercept_self(self):
        """Intercept command should allow same fleet as target (validation elsewhere)."""
        cmd = IssueInterceptCommand(fleet_id=5, target_fleet_id=5)
        assert cmd.fleet_id == cmd.target_fleet_id


class TestIssueJoinFleetCommand:
    """Tests for IssueJoinFleetCommand."""

    def test_create_join_fleet_command(self):
        """IssueJoinFleetCommand should store fleet_id and target_fleet_id."""
        cmd = IssueJoinFleetCommand(fleet_id=2, target_fleet_id=9)
        assert cmd.fleet_id == 2
        assert cmd.target_fleet_id == 9
        assert cmd.type == CommandType.ISSUE_ORDER


class TestQueueColonizeMissionCommand:
    """Tests for QueueColonizeMissionCommand."""

    def test_create_with_specific_planet(self):
        """QueueColonizeMissionCommand should store all fields."""
        target = HexCoord(10, -5)
        cmd = QueueColonizeMissionCommand(fleet_id=4, target_hex=target, planet_id=25)
        assert cmd.fleet_id == 4
        assert cmd.target_hex == target
        assert cmd.planet_id == 25
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_create_with_any_planet(self):
        """QueueColonizeMissionCommand should allow None planet_id."""
        target = HexCoord(3, 2)
        cmd = QueueColonizeMissionCommand(fleet_id=6, target_hex=target)
        assert cmd.planet_id is None

    def test_default_planet_id(self):
        """planet_id should default to None."""
        cmd = QueueColonizeMissionCommand(fleet_id=1, target_hex=HexCoord(0, 0))
        assert cmd.planet_id is None


class TestClearFleetOrdersCommand:
    """Tests for ClearFleetOrdersCommand."""

    def test_create_clear_orders_command(self):
        """ClearFleetOrdersCommand should store fleet_id."""
        cmd = ClearFleetOrdersCommand(fleet_id=11)
        assert cmd.fleet_id == 11
        assert cmd.type == CommandType.ISSUE_ORDER


class TestIssueTransferCommand:
    """Tests for IssueTransferCommand."""

    def test_create_load_command(self):
        """IssueTransferCommand should support load direction."""
        cmd = IssueTransferCommand(
            fleet_id=1,
            planet_id=2,
            cargo_type="passengers",
            direction="load",
            amount=100
        )
        assert cmd.fleet_id == 1
        assert cmd.planet_id == 2
        assert cmd.cargo_type == "passengers"
        assert cmd.direction == "load"
        assert cmd.amount == 100
        assert cmd.species_id is None
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_create_unload_command(self):
        """IssueTransferCommand should support unload direction."""
        cmd = IssueTransferCommand(
            fleet_id=3,
            planet_id=4,
            cargo_type="passengers",
            direction="unload",
            amount=50
        )
        assert cmd.direction == "unload"
        assert cmd.amount == 50

    def test_transfer_all_with_zero_amount(self):
        """Amount of 0 should mean 'transfer all'."""
        cmd = IssueTransferCommand(
            fleet_id=1,
            planet_id=2,
            cargo_type="passengers",
            direction="load",
            amount=0
        )
        assert cmd.amount == 0

    def test_default_amount_is_zero(self):
        """Amount should default to 0 (transfer all)."""
        cmd = IssueTransferCommand(
            fleet_id=1,
            planet_id=2,
            cargo_type="passengers",
            direction="load"
        )
        assert cmd.amount == 0

    def test_with_species_id(self):
        """IssueTransferCommand should support species_id for population transfers."""
        cmd = IssueTransferCommand(
            fleet_id=1,
            planet_id=2,
            cargo_type="passengers",
            direction="load",
            amount=10,
            species_id="human_01"
        )
        assert cmd.species_id == "human_01"


class TestSuperweaponCommands:
    """Tests for superweapon commands."""

    def test_implode_planet_command(self):
        """IssueImplodePlanetCommand should store fleet_id and planet_id."""
        cmd = IssueImplodePlanetCommand(fleet_id=5, planet_id=12)
        assert cmd.fleet_id == 5
        assert cmd.planet_id == 12
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_stellerate_star_command(self):
        """IssueStellerateStarCommand should store fleet_id."""
        cmd = IssueStellerateStarCommand(fleet_id=7)
        assert cmd.fleet_id == 7
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_open_warp_point_command(self):
        """IssueOpenWarpPointCommand should store all fields."""
        target = HexCoord(15, 8)
        cmd = IssueOpenWarpPointCommand(
            fleet_id=9,
            target_hex=target,
            target_system_name="Alpha Centauri"
        )
        assert cmd.fleet_id == 9
        assert cmd.target_hex == target
        assert cmd.target_system_name == "Alpha Centauri"
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_close_warp_point_command(self):
        """IssueCloseWarpPointCommand should store fleet_id and destination_id."""
        cmd = IssueCloseWarpPointCommand(
            fleet_id=3,
            warp_point_destination_id="system_beta_warp"
        )
        assert cmd.fleet_id == 3
        assert cmd.warp_point_destination_id == "system_beta_warp"
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_create_dyson_sphere_command(self):
        """IssueCreateDysonSphereCommand should store fleet_id."""
        cmd = IssueCreateDysonSphereCommand(fleet_id=14)
        assert cmd.fleet_id == 14
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_self_destruct_command(self):
        """IssueSelfDestructCommand should store fleet_id and ship_ids."""
        cmd = IssueSelfDestructCommand(fleet_id=8, ship_ids=[101, 102, 103])
        assert cmd.fleet_id == 8
        assert cmd.ship_ids == [101, 102, 103]
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_self_destruct_empty_list(self):
        """IssueSelfDestructCommand should allow empty ship_ids list."""
        cmd = IssueSelfDestructCommand(fleet_id=1, ship_ids=[])
        assert cmd.ship_ids == []


class TestSuperweaponMissionCommands:
    """Tests for superweapon mission commands (move + action)."""

    def test_queue_implode_planet_mission(self):
        """QueueImplodePlanetMissionCommand should store all fields."""
        target = HexCoord(20, -10)
        cmd = QueueImplodePlanetMissionCommand(
            fleet_id=6,
            target_hex=target,
            planet_id=33
        )
        assert cmd.fleet_id == 6
        assert cmd.target_hex == target
        assert cmd.planet_id == 33
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_queue_stellerate_star_mission(self):
        """QueueStellerateStarMissionCommand should store fleet_id and target_hex."""
        target = HexCoord(-5, 12)
        cmd = QueueStellerateStarMissionCommand(fleet_id=4, target_hex=target)
        assert cmd.fleet_id == 4
        assert cmd.target_hex == target
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_queue_open_warp_point_mission(self):
        """QueueOpenWarpPointMissionCommand should store all fields."""
        target = HexCoord(8, 8)
        cmd = QueueOpenWarpPointMissionCommand(
            fleet_id=11,
            target_hex=target,
            target_system_name="Proxima"
        )
        assert cmd.fleet_id == 11
        assert cmd.target_hex == target
        assert cmd.target_system_name == "Proxima"
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_queue_close_warp_point_mission(self):
        """QueueCloseWarpPointMissionCommand should store all fields."""
        target = HexCoord(0, -15)
        cmd = QueueCloseWarpPointMissionCommand(
            fleet_id=2,
            target_hex=target,
            warp_point_destination_id="old_warp_link"
        )
        assert cmd.fleet_id == 2
        assert cmd.target_hex == target
        assert cmd.warp_point_destination_id == "old_warp_link"
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_queue_create_dyson_sphere_mission(self):
        """QueueCreateDysonSphereMissionCommand should store fleet_id and target_hex."""
        target = HexCoord(25, 25)
        cmd = QueueCreateDysonSphereMissionCommand(fleet_id=16, target_hex=target)
        assert cmd.fleet_id == 16
        assert cmd.target_hex == target
        assert cmd.type == CommandType.ISSUE_ORDER


class TestIssueWarpCommand:
    """Tests for IssueWarpCommand (PROJ-187)."""

    def test_create_warp_command(self):
        """IssueWarpCommand should store fleet_id and warp_point_hex."""
        warp_hex = HexCoord(10, 5)
        cmd = IssueWarpCommand(fleet_id=7, warp_point_hex=warp_hex)
        assert cmd.fleet_id == 7
        assert cmd.warp_point_hex == warp_hex
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_warp_command_name(self):
        """IssueWarpCommand should have correct name property."""
        cmd = IssueWarpCommand(fleet_id=1, warp_point_hex=HexCoord(0, 0))
        assert cmd.name == "IssueWarpCommand"


class TestCommandEquality:
    """Tests for command equality behavior (dataclass default)."""

    def test_same_commands_are_equal(self):
        """Commands with same values should be equal."""
        cmd1 = IssueMoveCommand(fleet_id=1, target_hex=HexCoord(5, 5))
        cmd2 = IssueMoveCommand(fleet_id=1, target_hex=HexCoord(5, 5))
        assert cmd1 == cmd2

    def test_different_values_not_equal(self):
        """Commands with different values should not be equal."""
        cmd1 = IssueMoveCommand(fleet_id=1, target_hex=HexCoord(5, 5))
        cmd2 = IssueMoveCommand(fleet_id=2, target_hex=HexCoord(5, 5))
        assert cmd1 != cmd2

    def test_different_command_types_not_equal(self):
        """Different command classes should not be equal."""
        cmd1 = IssueColonizeCommand(fleet_id=1, planet_id=2)
        cmd2 = IssueInterceptCommand(fleet_id=1, target_fleet_id=2)
        assert cmd1 != cmd2
