"""
Unit tests for GroupTargetCoordinator.

Phase 6: Group-level coordination for focus fire, reserve commitment,
and flagship succession.

TDD: Written before implementation.
"""

from unittest.mock import MagicMock
from game.core.math import Vector2


def _make_ship(name="Ship", hp=100, max_hp=100, alive=True, team_id=0, has_cnc=False):
    """Create a mock ship for coordination tests."""
    ship = MagicMock()
    ship.name = name
    ship.instance_id = f"id_{name}"
    ship.position = Vector2(0, 0)
    ship.is_alive = alive
    ship.is_derelict = not alive
    ship.hp = hp
    ship.max_hp = max_hp
    ship.team_id = team_id
    ship.mass = 8000
    ship._has_cnc = has_cnc
    return ship


def _make_enemy(name="Enemy", hp=100, max_hp=100, mass=8000):
    """Create a mock enemy ship."""
    enemy = MagicMock()
    enemy.name = name
    enemy.instance_id = f"id_{name}"
    enemy.position = Vector2(50000, 50000)
    enemy.is_alive = True
    enemy.is_derelict = False
    enemy.hp = hp
    enemy.max_hp = max_hp
    enemy.team_id = 1
    enemy.mass = mass
    return enemy


# =============================================================================
# Focus Fire Coordination
# =============================================================================

class TestFocusFireCoordination:
    """Tests for group focus-fire target selection."""

    def test_focus_fire_returns_single_target(self):
        """Focus fire selects one target for the group."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        coordinator = GroupTargetCoordinator()
        enemies = [_make_enemy("E1"), _make_enemy("E2")]

        target = coordinator.select_focus_target(
            enemies=enemies,
            priority="strongest",
        )

        assert target is not None
        assert target in enemies

    def test_focus_strongest_picks_highest_mass(self):
        """'strongest' priority picks the enemy with highest mass."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        coordinator = GroupTargetCoordinator()
        light = _make_enemy("Light", mass=1000)
        heavy = _make_enemy("Heavy", mass=32000)

        target = coordinator.select_focus_target(
            enemies=[light, heavy],
            priority="strongest",
        )

        assert target == heavy

    def test_focus_weakest_picks_most_damaged(self):
        """'most_damaged' priority picks the enemy with lowest HP ratio."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        coordinator = GroupTargetCoordinator()
        healthy = _make_enemy("Healthy", hp=100, max_hp=100)
        damaged = _make_enemy("Damaged", hp=20, max_hp=100)

        target = coordinator.select_focus_target(
            enemies=[healthy, damaged],
            priority="most_damaged",
        )

        assert target == damaged

    def test_focus_nearest_picks_closest(self):
        """'nearest' priority picks the closest enemy to group centroid."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        coordinator = GroupTargetCoordinator()
        far = _make_enemy("Far")
        far.position = Vector2(80000, 50000)
        near = _make_enemy("Near")
        near.position = Vector2(30000, 50000)

        group_centroid = Vector2(25000, 50000)

        target = coordinator.select_focus_target(
            enemies=[far, near],
            priority="nearest",
            reference_position=group_centroid,
        )

        assert target == near

    def test_empty_enemies_returns_none(self):
        """No enemies returns None."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        coordinator = GroupTargetCoordinator()
        target = coordinator.select_focus_target(enemies=[], priority="strongest")
        assert target is None

    def test_dead_enemies_filtered(self):
        """Dead enemies are not selected."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        coordinator = GroupTargetCoordinator()
        dead = _make_enemy("Dead")
        dead.is_alive = False
        alive = _make_enemy("Alive")

        target = coordinator.select_focus_target(
            enemies=[dead, alive],
            priority="strongest",
        )

        assert target == alive


# =============================================================================
# Group HP Calculation
# =============================================================================

class TestGroupHP:
    """Tests for aggregate group HP calculation."""

    def test_group_hp_ratio(self):
        """compute_group_hp_ratio returns aggregate HP/maxHP."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        ships = [
            _make_ship("S1", hp=50, max_hp=100),
            _make_ship("S2", hp=100, max_hp=100),
        ]

        ratio = GroupTargetCoordinator.compute_group_hp_ratio(ships)
        assert ratio == 0.75  # 150/200

    def test_group_hp_ratio_empty(self):
        """Empty group returns 0.0."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        ratio = GroupTargetCoordinator.compute_group_hp_ratio([])
        assert ratio == 0.0

    def test_group_hp_ratio_all_dead(self):
        """All dead ships returns 0.0."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        ships = [_make_ship("S1", hp=0, max_hp=100)]
        ratio = GroupTargetCoordinator.compute_group_hp_ratio(ships)
        assert ratio == 0.0


# =============================================================================
# Reserve Commitment
# =============================================================================

class TestReserveCommitment:
    """Tests for reserve group commitment logic."""

    def test_reserve_not_committed_above_threshold(self):
        """Reserve stays uncommitted when main body HP is above threshold."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        main_body_ships = [_make_ship("M1", hp=80, max_hp=100)]

        committed = GroupTargetCoordinator.should_commit_reserve(
            main_body_ships=main_body_ships,
            threshold=0.50,
        )

        assert committed is False

    def test_reserve_committed_below_threshold(self):
        """Reserve commits when main body HP drops below threshold."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        main_body_ships = [
            _make_ship("M1", hp=20, max_hp=100),
            _make_ship("M2", hp=10, max_hp=100),
        ]

        committed = GroupTargetCoordinator.should_commit_reserve(
            main_body_ships=main_body_ships,
            threshold=0.50,
        )

        assert committed is True

    def test_reserve_committed_at_exact_threshold(self):
        """Reserve commits at exactly the threshold."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        main_body_ships = [_make_ship("M1", hp=50, max_hp=100)]

        committed = GroupTargetCoordinator.should_commit_reserve(
            main_body_ships=main_body_ships,
            threshold=0.50,
        )

        assert committed is True


# =============================================================================
# Flagship Succession
# =============================================================================

class TestFlagshipSuccession:
    """Tests for flagship destruction and succession."""

    def test_find_successor_returns_ship_with_cnc(self):
        """find_flagship_successor returns a ship with CommandAndControl."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        ships = [
            _make_ship("NoCNC1", has_cnc=False),
            _make_ship("HasCNC", has_cnc=True),
            _make_ship("NoCNC2", has_cnc=False),
        ]

        successor = GroupTargetCoordinator.find_flagship_successor(
            ships=ships,
            has_cnc_check=lambda s: s._has_cnc,
        )

        assert successor is not None
        assert successor.name == "HasCNC"

    def test_find_successor_returns_none_when_no_cnc(self):
        """find_flagship_successor returns None when no ship has C&C."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        ships = [
            _make_ship("NoCNC1", has_cnc=False),
            _make_ship("NoCNC2", has_cnc=False),
        ]

        successor = GroupTargetCoordinator.find_flagship_successor(
            ships=ships,
            has_cnc_check=lambda s: s._has_cnc,
        )

        assert successor is None

    def test_find_successor_skips_dead_ships(self):
        """Dead ships are not considered for succession."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        dead_cnc = _make_ship("DeadCNC", has_cnc=True, alive=False)
        alive_cnc = _make_ship("AliveCNC", has_cnc=True)

        successor = GroupTargetCoordinator.find_flagship_successor(
            ships=[dead_cnc, alive_cnc],
            has_cnc_check=lambda s: s._has_cnc,
        )

        assert successor == alive_cnc

    def test_find_successor_prefers_heaviest(self):
        """Among multiple C&C ships, picks the heaviest."""
        from game.ai.group_target_coordinator import GroupTargetCoordinator

        light_cnc = _make_ship("LightCNC", has_cnc=True)
        light_cnc.mass = 4000
        heavy_cnc = _make_ship("HeavyCNC", has_cnc=True)
        heavy_cnc.mass = 32000

        successor = GroupTargetCoordinator.find_flagship_successor(
            ships=[light_cnc, heavy_cnc],
            has_cnc_check=lambda s: s._has_cnc,
        )

        assert successor == heavy_cnc
