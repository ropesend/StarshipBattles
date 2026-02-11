"""Tests for superweapon input actions and key bindings (Phase 7)."""

import pytest
from game.core.input_actions import (
    InputAction,
    ACTION_DISPLAY_NAMES,
    ACTION_GROUPS,
)


class TestSuperweaponInputActions:
    """Tests for superweapon InputAction enum values."""

    def test_fleet_implode_planet_exists(self):
        """FLEET_IMPLODE_PLANET enum value exists."""
        assert InputAction.FLEET_IMPLODE_PLANET == "fleet.implode_planet"

    def test_fleet_stellerate_star_exists(self):
        """FLEET_STELLERATE_STAR enum value exists."""
        assert InputAction.FLEET_STELLERATE_STAR == "fleet.stellerate_star"

    def test_fleet_open_warp_point_exists(self):
        """FLEET_OPEN_WARP_POINT enum value exists."""
        assert InputAction.FLEET_OPEN_WARP_POINT == "fleet.open_warp_point"

    def test_fleet_close_warp_point_exists(self):
        """FLEET_CLOSE_WARP_POINT enum value exists."""
        assert InputAction.FLEET_CLOSE_WARP_POINT == "fleet.close_warp_point"

    def test_fleet_create_dyson_sphere_exists(self):
        """FLEET_CREATE_DYSON_SPHERE enum value exists."""
        assert InputAction.FLEET_CREATE_DYSON_SPHERE == "fleet.create_dyson_sphere"

    def test_fleet_self_destruct_exists(self):
        """FLEET_SELF_DESTRUCT enum value exists."""
        assert InputAction.FLEET_SELF_DESTRUCT == "fleet.self_destruct"


class TestSuperweaponDisplayNames:
    """Tests for superweapon display names."""

    def test_implode_planet_display_name(self):
        """FLEET_IMPLODE_PLANET has correct display name."""
        assert ACTION_DISPLAY_NAMES[InputAction.FLEET_IMPLODE_PLANET] == "Destroy Planet"

    def test_stellerate_star_display_name(self):
        """FLEET_STELLERATE_STAR has correct display name."""
        assert ACTION_DISPLAY_NAMES[InputAction.FLEET_STELLERATE_STAR] == "Destroy Star"

    def test_open_warp_point_display_name(self):
        """FLEET_OPEN_WARP_POINT has correct display name."""
        assert ACTION_DISPLAY_NAMES[InputAction.FLEET_OPEN_WARP_POINT] == "Open Warp Point"

    def test_close_warp_point_display_name(self):
        """FLEET_CLOSE_WARP_POINT has correct display name."""
        assert ACTION_DISPLAY_NAMES[InputAction.FLEET_CLOSE_WARP_POINT] == "Close Warp Point"

    def test_create_dyson_sphere_display_name(self):
        """FLEET_CREATE_DYSON_SPHERE has correct display name."""
        assert ACTION_DISPLAY_NAMES[InputAction.FLEET_CREATE_DYSON_SPHERE] == "Create Dyson Sphere"

    def test_self_destruct_display_name(self):
        """FLEET_SELF_DESTRUCT has correct display name."""
        assert ACTION_DISPLAY_NAMES[InputAction.FLEET_SELF_DESTRUCT] == "Self-Destruct"


class TestSuperweaponActionGroups:
    """Tests for superweapon actions in Fleet Commands group."""

    def test_implode_planet_in_fleet_commands(self):
        """FLEET_IMPLODE_PLANET is in Fleet Commands group."""
        assert InputAction.FLEET_IMPLODE_PLANET in ACTION_GROUPS["Fleet Commands"]

    def test_stellerate_star_in_fleet_commands(self):
        """FLEET_STELLERATE_STAR is in Fleet Commands group."""
        assert InputAction.FLEET_STELLERATE_STAR in ACTION_GROUPS["Fleet Commands"]

    def test_open_warp_point_in_fleet_commands(self):
        """FLEET_OPEN_WARP_POINT is in Fleet Commands group."""
        assert InputAction.FLEET_OPEN_WARP_POINT in ACTION_GROUPS["Fleet Commands"]

    def test_close_warp_point_in_fleet_commands(self):
        """FLEET_CLOSE_WARP_POINT is in Fleet Commands group."""
        assert InputAction.FLEET_CLOSE_WARP_POINT in ACTION_GROUPS["Fleet Commands"]

    def test_create_dyson_sphere_in_fleet_commands(self):
        """FLEET_CREATE_DYSON_SPHERE is in Fleet Commands group."""
        assert InputAction.FLEET_CREATE_DYSON_SPHERE in ACTION_GROUPS["Fleet Commands"]

    def test_self_destruct_in_fleet_commands(self):
        """FLEET_SELF_DESTRUCT is in Fleet Commands group."""
        assert InputAction.FLEET_SELF_DESTRUCT in ACTION_GROUPS["Fleet Commands"]
