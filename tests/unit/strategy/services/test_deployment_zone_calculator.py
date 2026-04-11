"""
Unit tests for DeploymentZoneCalculator.

Phase 5: Maps BattleRole to deployment positions on the battlefield.
Each TaskForce/Squadron's battle_role determines where it deploys.

TDD: Written before implementation.
"""

import pytest
from game.core.math import Vector2


# =============================================================================
# Zone Position Calculation
# =============================================================================

class TestDeploymentZonePositions:
    """Tests for battle role -> zone position mapping."""

    def test_main_body_team_0_center(self):
        """MAIN_BODY for team 0 deploys at left-center."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        pos = DeploymentZoneCalculator.get_zone_center(BattleRole.MAIN_BODY, team_id=0)

        assert pos.x == pytest.approx(25000, abs=1000)
        assert pos.y == pytest.approx(50000, abs=1000)

    def test_main_body_team_1_mirrored(self):
        """MAIN_BODY for team 1 deploys at right-center (mirrored)."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        pos = DeploymentZoneCalculator.get_zone_center(BattleRole.MAIN_BODY, team_id=1)

        assert pos.x == pytest.approx(75000, abs=1000)
        assert pos.y == pytest.approx(50000, abs=1000)

    def test_vanguard_closer_to_center(self):
        """VANGUARD deploys closer to the battlefield center than MAIN_BODY."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        vanguard = DeploymentZoneCalculator.get_zone_center(BattleRole.VANGUARD, team_id=0)
        main = DeploymentZoneCalculator.get_zone_center(BattleRole.MAIN_BODY, team_id=0)

        # Vanguard should be further right (closer to center) for team 0
        assert vanguard.x > main.x

    def test_reserve_furthest_from_center(self):
        """RESERVE deploys furthest from the battlefield center."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        reserve = DeploymentZoneCalculator.get_zone_center(BattleRole.RESERVE, team_id=0)
        main = DeploymentZoneCalculator.get_zone_center(BattleRole.MAIN_BODY, team_id=0)

        # Reserve should be further left (away from center) for team 0
        assert reserve.x < main.x

    def test_screen_between_vanguard_and_main(self):
        """SCREEN deploys between VANGUARD and MAIN_BODY."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        screen = DeploymentZoneCalculator.get_zone_center(BattleRole.SCREEN, team_id=0)
        vanguard = DeploymentZoneCalculator.get_zone_center(BattleRole.VANGUARD, team_id=0)
        main = DeploymentZoneCalculator.get_zone_center(BattleRole.MAIN_BODY, team_id=0)

        assert main.x < screen.x < vanguard.x

    def test_flanker_left_y_offset_negative(self):
        """FLANKER_LEFT has negative Y offset (above center)."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        flanker_l = DeploymentZoneCalculator.get_zone_center(BattleRole.FLANKER_LEFT, team_id=0)
        main = DeploymentZoneCalculator.get_zone_center(BattleRole.MAIN_BODY, team_id=0)

        assert flanker_l.y < main.y

    def test_flanker_right_y_offset_positive(self):
        """FLANKER_RIGHT has positive Y offset (below center)."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        flanker_r = DeploymentZoneCalculator.get_zone_center(BattleRole.FLANKER_RIGHT, team_id=0)
        main = DeploymentZoneCalculator.get_zone_center(BattleRole.MAIN_BODY, team_id=0)

        assert flanker_r.y > main.y

    def test_team_1_mirrors_x_but_same_y_logic(self):
        """Team 1 mirrors X positions but flanker Y offsets use same direction."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        # Team 1 vanguard should be closer to center (lower X)
        vanguard_1 = DeploymentZoneCalculator.get_zone_center(BattleRole.VANGUARD, team_id=1)
        main_1 = DeploymentZoneCalculator.get_zone_center(BattleRole.MAIN_BODY, team_id=1)

        assert vanguard_1.x < main_1.x  # opposite of team 0


# =============================================================================
# Ship Position Generation Within Zone
# =============================================================================

class TestShipPositionsInZone:
    """Tests for generating ship positions within a deployment zone."""

    def test_single_ship_at_zone_center(self):
        """A single ship deploys at the zone center."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        positions = DeploymentZoneCalculator.compute_positions(
            ship_count=1,
            battle_role=BattleRole.MAIN_BODY,
            team_id=0,
        )

        assert len(positions) == 1
        zone_center = DeploymentZoneCalculator.get_zone_center(BattleRole.MAIN_BODY, team_id=0)
        assert abs(positions[0][0] - zone_center.x) < 100
        assert abs(positions[0][1] - zone_center.y) < 100

    def test_multiple_ships_spread_vertically(self):
        """Multiple ships spread vertically within the zone."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        positions = DeploymentZoneCalculator.compute_positions(
            ship_count=5,
            battle_role=BattleRole.MAIN_BODY,
            team_id=0,
        )

        assert len(positions) == 5

        y_values = [p[1] for p in positions]
        # All Y values should be different (spread out)
        assert len(set(y_values)) == 5
        # X values should all be close to zone center X
        x_values = [p[0] for p in positions]
        assert max(x_values) - min(x_values) < 100

    def test_positions_are_tuples(self):
        """Positions are returned as (x, y) tuples for compatibility."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        positions = DeploymentZoneCalculator.compute_positions(
            ship_count=3,
            battle_role=BattleRole.MAIN_BODY,
            team_id=0,
        )

        for pos in positions:
            assert isinstance(pos, tuple)
            assert len(pos) == 2

    def test_default_role_is_main_body(self):
        """None role defaults to MAIN_BODY positioning."""
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator
        from game.strategy.data.fleet_hierarchy import BattleRole

        positions_none = DeploymentZoneCalculator.compute_positions(
            ship_count=3, battle_role=None, team_id=0,
        )
        positions_main = DeploymentZoneCalculator.compute_positions(
            ship_count=3, battle_role=BattleRole.MAIN_BODY, team_id=0,
        )

        # Should produce identical positions
        for p1, p2 in zip(positions_none, positions_main):
            assert p1 == p2
