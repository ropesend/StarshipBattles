"""
Unit tests for spatial behavior system.

Phase 4: Spatial behaviors replace the old ShipFormation system.
Each behavior defines how ships position relative to an anchor
(ship, group centroid, or zone).

TDD: Written before implementation.
"""

from unittest.mock import MagicMock
from game.core.math import Vector2


# =============================================================================
# Helpers
# =============================================================================

def _make_ship(x=0, y=0, angle=0, alive=True):
    """Create a mock ship with position, angle, and basic properties."""
    ship = MagicMock()
    ship.position = Vector2(x, y)
    ship.angle = angle
    ship.is_alive = alive
    ship.is_derelict = not alive
    ship.mass = 1000
    ship.max_speed = 10.0
    ship.instance_id = f"ship_{x}_{y}"
    return ship


# =============================================================================
# SpatialBehavior Base Class
# =============================================================================

class TestSpatialBehaviorBase:
    """Tests for the SpatialBehavior abstract base class."""

    def test_base_class_exists(self):
        """SpatialBehavior base class is importable."""
        from game.ai.spatial_behaviors.base import SpatialBehavior

        assert SpatialBehavior is not None

    def test_base_has_compute_target_position(self):
        """SpatialBehavior defines compute_target_position method."""
        from game.ai.spatial_behaviors.base import SpatialBehavior

        assert hasattr(SpatialBehavior, 'compute_target_position')

    def test_base_has_behavior_type(self):
        """SpatialBehavior defines behavior_type class attribute."""
        from game.ai.spatial_behaviors.base import SpatialBehavior

        assert hasattr(SpatialBehavior, 'behavior_type')


# =============================================================================
# FreeManeuver Behavior
# =============================================================================

class TestFreeManeuverBehavior:
    """Tests for FreeManeuver — no spatial constraints."""

    def test_free_maneuver_returns_none(self):
        """FreeManeuver.compute_target_position returns None (no constraint)."""
        from game.ai.spatial_behaviors.free_maneuver import FreeManeuverBehavior

        behavior = FreeManeuverBehavior()
        ship = _make_ship(100, 200)

        result = behavior.compute_target_position(ship, [])
        assert result is None

    def test_free_maneuver_type(self):
        """FreeManeuver has behavior_type 'free_maneuver'."""
        from game.ai.spatial_behaviors.free_maneuver import FreeManeuverBehavior

        assert FreeManeuverBehavior.behavior_type == "free_maneuver"


# =============================================================================
# BattleLine Behavior (Rigid)
# =============================================================================

class TestBattleLineBehavior:
    """Tests for BattleLine — ships hold positions in a line perpendicular to facing."""

    def test_battle_line_type(self):
        """BattleLine has behavior_type 'battle_line'."""
        from game.ai.spatial_behaviors.battle_line import BattleLineBehavior

        assert BattleLineBehavior.behavior_type == "battle_line"

    def test_battle_line_assigns_slots(self):
        """BattleLine assigns slot positions to ships based on count."""
        from game.ai.spatial_behaviors.battle_line import BattleLineBehavior

        behavior = BattleLineBehavior(spacing=2000, shape="line")
        leader = _make_ship(0, 0, angle=0)
        ships = [_make_ship(100, i * 100) for i in range(3)]

        # Each ship gets a target position relative to leader
        for i, ship in enumerate(ships):
            result = behavior.compute_target_position(
                ship, ships, leader=leader, slot_index=i,
            )
            assert result is not None
            assert isinstance(result, Vector2)

    def test_battle_line_ships_spread_perpendicular(self):
        """Battle line ships spread along the perpendicular axis."""
        from game.ai.spatial_behaviors.battle_line import BattleLineBehavior

        behavior = BattleLineBehavior(spacing=2000, shape="line")
        leader = _make_ship(0, 0, angle=0)  # facing right (angle=0)
        ships = [_make_ship(0, 0) for _ in range(3)]

        positions = []
        for i, ship in enumerate(ships):
            pos = behavior.compute_target_position(
                ship, ships, leader=leader, slot_index=i,
            )
            positions.append(pos)

        # With 3 ships in a line, they should be spread along Y axis
        # (perpendicular to angle=0 which faces right along X)
        y_values = [p.y for p in positions]
        # They should be spread out, not all at same Y
        assert max(y_values) - min(y_values) > 0

    def test_battle_line_spacing_respected(self):
        """Ships in battle line are spaced by the configured spacing."""
        from game.ai.spatial_behaviors.battle_line import BattleLineBehavior

        spacing = 3000
        behavior = BattleLineBehavior(spacing=spacing, shape="line")
        leader = _make_ship(0, 0, angle=0)
        ships = [_make_ship(0, 0) for _ in range(2)]

        p0 = behavior.compute_target_position(
            ships[0], ships, leader=leader, slot_index=0,
        )
        p1 = behavior.compute_target_position(
            ships[1], ships, leader=leader, slot_index=1,
        )

        dist = (p1 - p0).length()
        assert abs(dist - spacing) < 1.0  # within 1 unit


# =============================================================================
# Screen Behavior (Loose)
# =============================================================================

class TestScreenBehavior:
    """Tests for Screen — ships orbit/patrol around an anchor."""

    def test_screen_type(self):
        """Screen has behavior_type 'screen'."""
        from game.ai.spatial_behaviors.screen import ScreenBehavior

        assert ScreenBehavior.behavior_type == "screen"

    def test_screen_distributes_around_anchor(self):
        """Screen positions ships evenly around the anchor point."""
        from game.ai.spatial_behaviors.screen import ScreenBehavior

        anchor_pos = Vector2(5000, 5000)
        behavior = ScreenBehavior(radius=2000)
        ships = [_make_ship(0, 0) for _ in range(4)]

        positions = []
        for i, ship in enumerate(ships):
            pos = behavior.compute_target_position(
                ship, ships, anchor_position=anchor_pos, slot_index=i,
            )
            positions.append(pos)

        # All positions should be approximately radius distance from anchor
        for pos in positions:
            dist = (pos - anchor_pos).length()
            assert abs(dist - 2000) < 1.0

        # Positions should be spread around (not clumped)
        # Check that angles are roughly evenly spaced (90 degrees apart for 4 ships)
        import math
        angles = []
        for pos in positions:
            dx = pos.x - anchor_pos.x
            dy = pos.y - anchor_pos.y
            angles.append(math.atan2(dy, dx))
        angles.sort()

        # Consecutive angle differences should be roughly pi/2 (90 degrees)
        for i in range(len(angles) - 1):
            diff = angles[i + 1] - angles[i]
            assert abs(diff - math.pi / 2) < 0.1

    def test_screen_positions_at_radius(self):
        """Screen positions are at the configured radius from anchor."""
        from game.ai.spatial_behaviors.screen import ScreenBehavior

        anchor_pos = Vector2(0, 0)
        radius = 3000
        behavior = ScreenBehavior(radius=radius)
        ship = _make_ship(100, 200)

        pos = behavior.compute_target_position(
            ship, [ship], anchor_position=anchor_pos, slot_index=0,
        )

        dist = (pos - anchor_pos).length()
        assert abs(dist - radius) < 1.0


# =============================================================================
# Escort Behavior (Loose)
# =============================================================================

class TestEscortBehavior:
    """Tests for Escort — ships stay close to anchor ship."""

    def test_escort_type(self):
        """Escort has behavior_type 'escort'."""
        from game.ai.spatial_behaviors.escort import EscortBehavior

        assert EscortBehavior.behavior_type == "escort"

    def test_escort_positions_near_anchor(self):
        """Escort positions ships near the anchor ship."""
        from game.ai.spatial_behaviors.escort import EscortBehavior

        anchor_ship = _make_ship(5000, 5000, angle=90)
        behavior = EscortBehavior(distance=1000)
        ship = _make_ship(0, 0)

        pos = behavior.compute_target_position(
            ship, [ship], anchor_ship=anchor_ship, slot_index=0,
        )

        dist = (pos - anchor_ship.position).length()
        assert abs(dist - 1000) < 1.0


# =============================================================================
# Column Behavior (Rigid)
# =============================================================================

class TestColumnBehavior:
    """Tests for Column — ships follow leader in single file."""

    def test_column_type(self):
        """Column has behavior_type 'column'."""
        from game.ai.spatial_behaviors.column import ColumnBehavior

        assert ColumnBehavior.behavior_type == "column"

    def test_column_positions_behind_leader(self):
        """Column positions ships behind the leader along the leader's facing."""
        from game.ai.spatial_behaviors.column import ColumnBehavior

        leader = _make_ship(5000, 5000, angle=0)  # facing right
        behavior = ColumnBehavior(follow_distance=1500)
        ships = [_make_ship(0, 0) for _ in range(3)]

        positions = []
        for i, ship in enumerate(ships):
            pos = behavior.compute_target_position(
                ship, ships, leader=leader, slot_index=i,
            )
            positions.append(pos)

        # Ships should be progressively further behind the leader (lower X for angle=0)
        for i in range(len(positions) - 1):
            assert positions[i].x > positions[i + 1].x


# =============================================================================
# PatrolZone Behavior (Loose)
# =============================================================================

class TestPatrolZoneBehavior:
    """Tests for PatrolZone — ships move within a defined area."""

    def test_patrol_zone_type(self):
        """PatrolZone has behavior_type 'patrol_zone'."""
        from game.ai.spatial_behaviors.patrol_zone import PatrolZoneBehavior

        assert PatrolZoneBehavior.behavior_type == "patrol_zone"

    def test_patrol_zone_positions_within_zone(self):
        """PatrolZone positions are within the zone radius."""
        from game.ai.spatial_behaviors.patrol_zone import PatrolZoneBehavior

        zone_center = Vector2(10000, 10000)
        zone_radius = 5000
        behavior = PatrolZoneBehavior(zone_center=zone_center, zone_radius=zone_radius)
        ship = _make_ship(0, 0)

        pos = behavior.compute_target_position(
            ship, [ship], slot_index=0,
        )

        dist = (pos - zone_center).length()
        assert dist <= zone_radius


# =============================================================================
# Behavior Registry
# =============================================================================

class TestSpatialBehaviorRegistry:
    """Tests for looking up spatial behaviors by type string."""

    def test_create_behavior_by_type(self):
        """create_spatial_behavior creates the correct behavior class."""
        from game.ai.spatial_behaviors import create_spatial_behavior

        behavior = create_spatial_behavior("free_maneuver")
        assert behavior.behavior_type == "free_maneuver"

    def test_create_battle_line(self):
        """create_spatial_behavior creates BattleLine."""
        from game.ai.spatial_behaviors import create_spatial_behavior

        behavior = create_spatial_behavior("battle_line", spacing=2000)
        assert behavior.behavior_type == "battle_line"

    def test_create_screen(self):
        """create_spatial_behavior creates Screen."""
        from game.ai.spatial_behaviors import create_spatial_behavior

        behavior = create_spatial_behavior("screen", radius=3000)
        assert behavior.behavior_type == "screen"

    def test_create_unknown_returns_free_maneuver(self):
        """Unknown behavior type defaults to FreeManeuver."""
        from game.ai.spatial_behaviors import create_spatial_behavior

        behavior = create_spatial_behavior("nonexistent_behavior")
        assert behavior.behavior_type == "free_maneuver"
