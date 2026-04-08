"""
Tests for per-tick position tracking on TestScenario.

Validates that when track_positions is enabled, ship positions are recorded
each tick and stored in results for post-test analysis.
"""

from unittest.mock import Mock, patch
import pygame


def _create_mock_ship(name, x, y, speed=0.0, angle=0.0):
    """Create a mock ship with position, velocity, angle."""
    ship = Mock()
    ship.name = name
    ship.position = pygame.math.Vector2(x, y)
    ship.velocity = pygame.math.Vector2(speed, 0)
    ship.angle = angle
    ship.is_alive = True
    ship.current_speed = speed
    return ship


def _create_scenario(track=True):
    """Create a TestScenario with tracking configured."""
    from combat_lab.scenarios.base import TestScenario

    with patch.object(TestScenario, "__init__", lambda self: None):
        scenario = TestScenario()
        scenario.results = {}
        scenario.track_positions = track
        scenario._position_log = {}
        scenario._tracking_weapon_range = None
        return scenario


# =============================================================================
# Core tracking behavior
# =============================================================================

class TestPositionTrackingBasic:
    """Core _track_tick functionality."""

    def test_records_attacker_position(self):
        """Attacker position is recorded when tracking is enabled."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)

        scenario._track_tick(tick=0)

        assert "attacker" in scenario._position_log
        assert len(scenario._position_log["attacker"]) == 1
        entry = scenario._position_log["attacker"][0]
        assert entry["tick"] == 0
        assert entry["x"] == 0
        assert entry["y"] == 0

    def test_records_target_position(self):
        """Target position is recorded when tracking is enabled."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)
        scenario.target = _create_mock_ship("Target", 100, 200)

        scenario._track_tick(tick=5)

        assert "target" in scenario._position_log
        entry = scenario._position_log["target"][0]
        assert entry["tick"] == 5
        assert entry["x"] == 100
        assert entry["y"] == 200

    def test_records_speed_and_heading(self):
        """Speed and heading are captured in each entry."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0, speed=15.0, angle=45.0)

        scenario._track_tick(tick=0)

        entry = scenario._position_log["attacker"][0]
        assert entry["speed"] == 15.0
        assert entry["heading"] == 45.0

    def test_records_distance_to_attacker_for_non_attacker_ships(self):
        """Non-attacker ships record distance to the attacker."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)
        scenario.target = _create_mock_ship("Target", 300, 400)

        scenario._track_tick(tick=0)

        entry = scenario._position_log["target"][0]
        assert entry["dist_to_attacker"] == 500.0  # 3-4-5 triangle

    def test_records_in_range_flag(self):
        """in_range flag based on weapon range is recorded."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)
        scenario.target = _create_mock_ship("Target", 500, 0)

        # Provide weapon range
        scenario._tracking_weapon_range = 1000

        scenario._track_tick(tick=0)

        entry = scenario._position_log["target"][0]
        assert entry["in_range"] is True

    def test_out_of_range_flag(self):
        """in_range is False when target exceeds weapon range."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)
        scenario.target = _create_mock_ship("Target", 1500, 0)

        scenario._tracking_weapon_range = 1000

        scenario._track_tick(tick=0)

        entry = scenario._position_log["target"][0]
        assert entry["in_range"] is False

    def test_accumulates_multiple_ticks(self):
        """Multiple _track_tick calls accumulate entries."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)

        for tick in range(10):
            scenario.attacker.position = pygame.math.Vector2(tick * 10, 0)
            scenario._track_tick(tick=tick)

        assert len(scenario._position_log["attacker"]) == 10
        assert scenario._position_log["attacker"][0]["x"] == 0
        assert scenario._position_log["attacker"][9]["x"] == 90


# =============================================================================
# Disabled / edge cases
# =============================================================================

class TestPositionTrackingDisabled:
    """Tracking behavior when disabled."""

    def test_no_tracking_when_disabled(self):
        """No data recorded when track_positions is False."""
        scenario = _create_scenario(track=False)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)

        scenario._track_tick(tick=0)

        assert scenario._position_log == {}

    def test_default_is_disabled(self):
        """track_positions defaults to False on TestScenario."""
        from combat_lab.scenarios.base import TestScenario, TestMetadata

        class DummyScenario(TestScenario):
            metadata = TestMetadata(
                test_id="DUMMY-001", category="Test", subcategory="Test",
                name="Dummy", summary="Dummy", conditions=[], edge_cases=[],
                expected_outcome="", pass_criteria="", max_ticks=10,
            )

        s = DummyScenario()
        assert s.track_positions is False

    def test_no_ships_does_not_crash(self):
        """Tracking with no ships set does not crash."""
        scenario = _create_scenario(track=True)
        # No attacker, target, ship, etc.

        scenario._track_tick(tick=0)  # Should not raise

        assert scenario._position_log == {}


# =============================================================================
# Ship discovery (different template ship attributes)
# =============================================================================

class TestPositionTrackingShipDiscovery:
    """Tracking discovers ships from various template attributes."""

    def test_discovers_ship_attribute(self):
        """PropulsionScenario/ResourceScenario use self.ship."""
        scenario = _create_scenario(track=True)
        scenario.ship = _create_mock_ship("Engine Test Ship", 50, 50)

        scenario._track_tick(tick=0)

        assert "ship" in scenario._position_log

    def test_discovers_ship1_ship2(self):
        """DuelScenario uses self.ship1 and self.ship2."""
        scenario = _create_scenario(track=True)
        scenario.ship1 = _create_mock_ship("Ship1", 0, 0)
        scenario.ship2 = _create_mock_ship("Ship2", 100, 0)

        scenario._track_tick(tick=0)

        assert "ship1" in scenario._position_log
        assert "ship2" in scenario._position_log

    def test_attacker_is_reference_for_distance(self):
        """Distance is computed relative to attacker when present."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)
        scenario.target = _create_mock_ship("Target", 100, 0)

        scenario._track_tick(tick=0)

        assert scenario._position_log["target"][0]["dist_to_attacker"] == 100.0
        # Attacker has no dist_to_attacker (it IS the attacker)
        assert "dist_to_attacker" not in scenario._position_log["attacker"][0]

    def test_ship1_is_reference_when_no_attacker(self):
        """In DuelScenario, ship1 is the reference for distance."""
        scenario = _create_scenario(track=True)
        scenario.ship1 = _create_mock_ship("Ship1", 0, 0)
        scenario.ship2 = _create_mock_ship("Ship2", 200, 0)

        scenario._track_tick(tick=0)

        assert scenario._position_log["ship2"][0]["dist_to_attacker"] == 200.0


# =============================================================================
# Results integration
# =============================================================================

class TestPositionTrackingResults:
    """Tracking data integration with results dict."""

    def test_finalize_stores_in_results(self):
        """_finalize_tracking stores position_tracks in results."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)
        scenario.target = _create_mock_ship("Target", 500, 0)
        scenario._tracking_weapon_range = 1000

        for tick in range(5):
            scenario._track_tick(tick=tick)

        scenario._finalize_tracking()

        assert "position_tracks" in scenario.results
        assert "attacker" in scenario.results["position_tracks"]
        assert "target" in scenario.results["position_tracks"]

    def test_finalize_stores_summary(self):
        """_finalize_tracking stores per-ship summary stats."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)
        scenario.target = _create_mock_ship("Target", 500, 0)
        scenario._tracking_weapon_range = 1000

        for tick in range(10):
            scenario._track_tick(tick=tick)

        scenario._finalize_tracking()

        summary = scenario.results["tracking_summary"]
        assert "target" in summary
        assert summary["target"]["ticks_tracked"] == 10
        assert summary["target"]["ticks_in_range"] == 10

    def test_finalize_counts_out_of_range_ticks(self):
        """Summary correctly counts in-range vs out-of-range ticks."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)
        scenario.target = _create_mock_ship("Target", 0, 0)
        scenario._tracking_weapon_range = 100

        # 5 ticks in range, 5 ticks out of range
        for tick in range(10):
            scenario.target.position = pygame.math.Vector2(tick * 20, 0)
            scenario._track_tick(tick=tick)

        scenario._finalize_tracking()

        summary = scenario.results["tracking_summary"]["target"]
        assert summary["ticks_tracked"] == 10
        assert summary["ticks_in_range"] == 6  # 0,20,40,60,80,100 are <=100
        assert summary["ticks_out_of_range"] == 4  # 120,140,160,180 are >100

    def test_finalize_noop_when_disabled(self):
        """_finalize_tracking is a no-op when tracking is disabled."""
        scenario = _create_scenario(track=False)

        scenario._finalize_tracking()

        assert "position_tracks" not in scenario.results

    def test_finalize_stores_min_max_distance(self):
        """Summary includes min and max distance to attacker."""
        scenario = _create_scenario(track=True)
        scenario.attacker = _create_mock_ship("Attacker", 0, 0)
        scenario.target = _create_mock_ship("Target", 0, 0)
        scenario._tracking_weapon_range = 1000

        distances = [500, 200, 800, 100, 600]
        for tick, d in enumerate(distances):
            scenario.target.position = pygame.math.Vector2(d, 0)
            scenario._track_tick(tick=tick)

        scenario._finalize_tracking()

        summary = scenario.results["tracking_summary"]["target"]
        assert summary["min_distance"] == 100.0
        assert summary["max_distance"] == 800.0
