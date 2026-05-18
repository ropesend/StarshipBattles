"""Integration tests for command flow through StrategySessionFacade.

These tests verify full command execution through the facade with real
GameSession instances. Fleets are manually created since GameSession
doesn't generate starting fleets.

PROJ-55: Updated to create fleets with colony pods for colonization tests.
"""
from unittest.mock import MagicMock

import pytest
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig
from game.strategy.facade.strategy_session_facade import StrategySessionFacade
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.ship_instance import ShipInstance


def _ensure_uncolonized_planet(session, *, distant_from: HexCoord = None):
    """F-A-028: deterministic helper — return an uncolonized planet,
    creating one by unclaiming if procedural generation produced none.

    If ``distant_from`` is passed, prefer a planet in a system whose
    ``global_location`` differs from that hex. Returns
    ``(planet, target_hex)``.
    """
    candidate = None
    candidate_hex = None
    # First pass: prefer naturally uncolonized planets.
    for sys in session.systems:
        if distant_from is not None and sys.global_location == distant_from:
            continue
        for planet in sys.planets:
            if planet.owner_id is None:
                return planet, sys.global_location + planet.location
            if candidate is None:
                candidate = planet
                candidate_hex = sys.global_location + planet.location
    # Fallback: unclaim a candidate to force a deterministic uncolonized planet.
    if candidate is not None:
        candidate.owner_id = None
        return candidate, candidate_hex
    raise AssertionError(
        "Galaxy fixture has no planets at all — config/system_count is too small."
    )


def _ensure_enemy_fleet(session, *, location: HexCoord):
    """F-A-028: deterministic helper — return an enemy empire's fleet,
    creating one if none exists. Returns the fleet."""
    if len(session.empires) < 2:
        raise AssertionError(
            "Galaxy fixture has fewer than 2 empires; "
            "test requires a second empire for intercept/enemy targeting."
        )
    enemy_empire = session.empires[1]
    fleet = Fleet(
        fleet_id=900_000 + enemy_empire.id,
        owner_id=enemy_empire.id,
        location=location,
    )
    enemy_empire.fleets.append(fleet)
    session.galaxy.register_fleet(fleet)
    return fleet


def make_colony_ship_for_planet(planet, owner_id: int) -> ShipInstance:
    """Create a ship with a drop pod in carried_items."""
    planet_type_str = planet.planet_type.name

    ship = ShipInstance(
        instance_id=f"colony-ship-{planet_type_str.lower()}-{id(planet)}",
        design_id=f"{planet_type_str}_colony_ship",
        name=f"Colony Ship ({planet_type_str})",
        owner_id=owner_id,
        design_data={
            'name': f"Colony Ship ({planet_type_str})",
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'layers': {
                'HULL': [{'id': 'colony_pod_bay'}]
            }
        },
    )
    # PROJ-436 Phase 9: typed DropPod into bay_inventory.pods.
    from game.strategy.data.bay_inventory import DropPod
    ship.bay_inventory.pods.append(DropPod(
        design_id=f"{planet_type_str.lower()}_drop_pod",
        design_data={"layers": {"CORE": []}},
        mass=500.0,
        payload={
            "name": f"Drop Pod ({planet_type_str})",
            "vehicle_type": "drop_pod",
        },
    ))
    return ship


class TestMoveCommandIntegration:
    """Integration tests for move command flow through facade."""

    @pytest.fixture
    def game_setup(self):
        """Create a real game session with facade and inject fleets."""
        config = GameConfig(galaxy_radius=5000, system_count=10)
        session = GameSession(config=config)

        # Inject a fleet for the player empire at their home system
        player_empire = session.empires[0]
        home_location = session.systems[0].global_location if session.systems else HexCoord(0, 0)
        fleet = Fleet(fleet_id=101, owner_id=player_empire.id, location=home_location)
        player_empire.fleets.append(fleet)
        session.galaxy.register_fleet(fleet)

        facade = StrategySessionFacade(session)
        return session, facade, fleet

    def test_move_command_through_facade(self, game_setup):
        """Move command through facade adds order to fleet and sets path."""
        session, facade, fleet = game_setup

        # Find a valid destination (different system)
        destination = None
        for sys in session.systems:
            if sys.global_location != fleet.location:
                destination = sys.global_location
                break

        assert destination is not None, "Need at least 2 systems for move test"

        # Execute move through facade
        from game.strategy.engine.commands import IssueMoveCommand
        cmd = IssueMoveCommand(fleet.id, destination)
        result = facade.handle_command(cmd)

        # Verify command succeeded
        assert result.is_valid, f"Move should succeed: {result.message}"

        # Verify fleet has move order
        assert len(fleet.orders) > 0
        assert fleet.orders[0].type == OrderType.MOVE

        # Verify path was set
        assert fleet.path is not None
        assert len(fleet.path) > 0

    def test_move_with_invalid_fleet_fails(self, game_setup):
        """Move command with invalid fleet ID returns error."""
        session, facade, fleet = game_setup

        # Try to move with non-existent fleet ID
        invalid_fleet_id = 999999
        destination = session.systems[1].global_location if len(session.systems) > 1 else HexCoord(100, 100)

        from game.strategy.engine.commands import IssueMoveCommand
        cmd = IssueMoveCommand(invalid_fleet_id, destination)
        result = facade.handle_command(cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message


class TestColonizeCommandIntegration:
    """Integration tests for colonize command flow through facade."""

    @pytest.fixture
    def game_setup(self):
        """Create a real game session with facade and fleet at uncolonized planet.

        F-A-028: an uncolonized planet is now deterministic — if procedural
        generation didn't produce one, ``_ensure_uncolonized_planet``
        unclaims a candidate so the test runs against guaranteed state.
        """
        config = GameConfig(galaxy_radius=5000, system_count=10)
        session = GameSession(config=config)

        uncolonized_planet, target_hex = _ensure_uncolonized_planet(session)

        # Ensure the player has at least one colony so
        # test_colonize_already_owned_fails has a target. GameSession's
        # default setup gives every empire one, but assert it explicitly
        # so the test stops gambling on procedural state.
        player_empire = session.empires[0]
        assert player_empire.colonies, (
            "Game setup invariant: player empire must have a home colony."
        )

        fleet = Fleet(fleet_id=102, owner_id=player_empire.id, location=target_hex)
        fleet.ships = [make_colony_ship_for_planet(uncolonized_planet, player_empire.id)]
        player_empire.fleets.append(fleet)
        session.galaxy.register_fleet(fleet)

        facade = StrategySessionFacade(session)
        return session, facade, fleet, uncolonized_planet

    def test_colonize_command_through_facade(self, game_setup):
        """Colonize command through facade adds colonize order to fleet."""
        session, facade, fleet, planet = game_setup

        # Execute colonize through facade
        from game.strategy.engine.commands import IssueColonizeCommand
        cmd = IssueColonizeCommand(fleet.id, planet.id)
        result = facade.handle_command(cmd)

        # Verify command succeeded
        assert result.is_valid, f"Colonize should succeed: {result.message}"

        # Order queue is now just COLONIZE (no LOAD_POPULATION)
        assert len(fleet.orders) >= 1
        assert fleet.orders[-1].type == OrderType.COLONIZE
        # No LOAD_POPULATION order should be present
        order_types = [o.type for o in fleet.orders]
        assert OrderType.LOAD_POPULATION not in order_types

    def test_colonize_already_owned_fails(self, game_setup):
        """Colonize command fails for already owned planet."""
        session, facade, fleet, _ = game_setup

        player_empire = session.empires[0]
        home_colony = player_empire.colonies[0]  # Guaranteed by fixture assertion.

        from game.strategy.engine.commands import IssueColonizeCommand
        cmd = IssueColonizeCommand(fleet.id, home_colony.id)
        result = facade.handle_command(cmd)

        assert not result.is_valid


class TestInterceptCommandIntegration:
    """Integration tests for intercept command flow through facade."""

    @pytest.fixture
    def game_setup(self):
        """Create a game session with fleets for both empires.

        F-A-028: enemy fleet is now deterministic — the helper asserts
        a second empire exists (default config has 2) and explicitly
        creates a fleet for them.
        """
        config = GameConfig(galaxy_radius=5000, system_count=10)
        session = GameSession(config=config)

        player_empire = session.empires[0]
        assert session.systems, "Game setup invariant: at least one system."
        player_location = session.systems[0].global_location
        player_fleet = Fleet(
            fleet_id=103, owner_id=player_empire.id, location=player_location,
        )
        player_empire.fleets.append(player_fleet)
        session.galaxy.register_fleet(player_fleet)

        enemy_location = session.systems[-1].global_location
        enemy_fleet = _ensure_enemy_fleet(session, location=enemy_location)

        facade = StrategySessionFacade(session)
        return session, facade, player_fleet, enemy_fleet

    def test_intercept_command_through_facade(self, game_setup):
        """Intercept command through facade adds intercept order to fleet."""
        session, facade, player_fleet, enemy_fleet = game_setup

        # Execute intercept through facade
        from game.strategy.engine.commands import IssueInterceptCommand
        cmd = IssueInterceptCommand(player_fleet.id, enemy_fleet.id)
        result = facade.handle_command(cmd)

        # Verify command succeeded
        assert result.is_valid, f"Intercept should succeed: {result.message}"

        # Verify fleet has intercept order
        assert len(player_fleet.orders) > 0
        assert player_fleet.orders[0].type == OrderType.MOVE_TO_FLEET


class TestJoinCommandIntegration:
    """Integration tests for join fleet command flow through facade."""

    @pytest.fixture
    def game_setup(self):
        """Create a game session with two player fleets."""
        config = GameConfig(galaxy_radius=5000, system_count=10)
        session = GameSession(config=config)

        # Inject two fleets for the player
        player_empire = session.empires[0]
        location = session.systems[0].global_location if session.systems else HexCoord(0, 0)

        fleet1 = Fleet(fleet_id=105, owner_id=player_empire.id, location=location)
        fleet2 = Fleet(fleet_id=106, owner_id=player_empire.id, location=HexCoord(location.q + 5, location.r + 5))

        player_empire.fleets.extend([fleet1, fleet2])
        session.galaxy.register_fleet(fleet1)
        session.galaxy.register_fleet(fleet2)

        facade = StrategySessionFacade(session)
        return session, facade, fleet1, fleet2

    def test_join_command_through_facade(self, game_setup):
        """Join command through facade adds join orders to fleet."""
        session, facade, fleet1, fleet2 = game_setup

        # Execute join through facade
        from game.strategy.engine.commands import IssueJoinFleetCommand
        cmd = IssueJoinFleetCommand(fleet1.id, fleet2.id)
        result = facade.handle_command(cmd)

        # Verify command succeeded
        assert result.is_valid, f"Join should succeed: {result.message}"

        # Verify fleet has orders
        assert len(fleet1.orders) > 0
        # Should have at least MOVE_TO_FLEET order
        order_types = [o.type for o in fleet1.orders]
        assert OrderType.MOVE_TO_FLEET in order_types or OrderType.JOIN_FLEET in order_types


class TestColonizeMissionIntegration:
    """Integration tests for colonize mission command flow through facade."""

    @pytest.fixture
    def game_setup(self):
        """Create a real game session with facade.

        F-A-028: a distant uncolonized planet is deterministic — the
        helper unclaims a candidate if no naturally uncolonized planet
        exists outside the fleet's home system.
        """
        config = GameConfig(galaxy_radius=5000, system_count=10)
        session = GameSession(config=config)

        player_empire = session.empires[0]
        assert session.systems, "Game setup invariant: at least one system."
        start_location = session.systems[0].global_location
        fleet = Fleet(
            fleet_id=107, owner_id=player_empire.id, location=start_location,
        )
        player_empire.fleets.append(fleet)
        session.galaxy.register_fleet(fleet)

        uncolonized_planet, target_hex = _ensure_uncolonized_planet(
            session, distant_from=start_location,
        )
        fleet.ships = [make_colony_ship_for_planet(uncolonized_planet, player_empire.id)]

        facade = StrategySessionFacade(session)
        return session, facade, fleet, uncolonized_planet, target_hex

    def test_colonize_mission_through_facade(self, game_setup):
        """Colonize mission command queues move + colonize orders."""
        session, facade, fleet, planet, target_hex = game_setup

        # Execute colonize mission through facade
        from game.strategy.engine.commands import QueueColonizeMissionCommand
        cmd = QueueColonizeMissionCommand(fleet.id, target_hex, planet.id)
        result = facade.handle_command(cmd)

        # Verify command succeeded
        assert result.is_valid, f"Colonize mission should succeed: {result.message}"

        # Verify fleet has orders queued
        assert len(fleet.orders) > 0

        # Should have path set (for movement)
        assert fleet.path is not None

    def test_colonize_mission_with_none_planet_through_facade(self, game_setup):
        """Colonize mission with planet_id=None queues move + colonize any orders."""
        session, facade, fleet, _, target_hex = game_setup

        # Execute colonize mission through facade with planet_id=None
        from game.strategy.engine.commands import QueueColonizeMissionCommand
        cmd = QueueColonizeMissionCommand(fleet.id, target_hex, None)  # None = "any planet"
        result = facade.handle_command(cmd)

        # Verify command succeeded
        assert result.is_valid, f"Colonize mission (any planet) should succeed: {result.message}"

        # Verify fleet has orders queued
        assert len(fleet.orders) > 0

        # Should have path set (for movement)
        assert fleet.path is not None

        # Verify the colonize order has target=None (any planet)
        colonize_order = [o for o in fleet.orders if o.type == OrderType.COLONIZE]
        assert len(colonize_order) > 0
        assert colonize_order[0].target is None  # Should be "any planet"


class TestFacadeProcessTurn:
    """Integration tests for turn processing through facade."""

    @pytest.fixture
    def game_setup(self):
        """Create a real game session with facade.

        PROJ-369 Phase 3: combat raises clearly when no ``ai_factory`` is
        provided (the silent ``_NullBattleResolver`` warn path was
        deleted). Pass ``ai_factory=MagicMock()`` so the
        SimulationBattleResolver is wired and combat resolves.
        """
        config = GameConfig(galaxy_radius=5000, system_count=5)
        session = GameSession(config=config, ai_factory=MagicMock())
        facade = StrategySessionFacade(session)
        return session, facade

    def test_process_turn_through_facade(self, game_setup):
        """process_turn through facade advances game state."""
        session, facade = game_setup

        initial_turn = session.turn_number

        # Process turn through facade
        facade.process_turn()

        # Verify turn advanced
        assert session.turn_number == initial_turn + 1

    def test_multiple_turns_through_facade(self, game_setup):
        """Multiple turns can be processed through facade."""
        session, facade = game_setup

        initial_turn = session.turn_number

        # Process 3 turns
        for _ in range(3):
            facade.process_turn()

        assert session.turn_number == initial_turn + 3
