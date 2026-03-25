"""Cross-object reference integrity tests (PROJ-223 Phase 4).

Verifies that colony references, fleet order targets, pursuer trackers,
fleet registration, and galaxy back-references survive save/load.
"""

import pytest

from game.strategy.engine.game_session import GameSession
from game.strategy.data.order_types import OrderType, FleetOrder
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


class TestColonyReferenceIntegrity:
    """Verify colony references are resolved after save/load."""

    def _find_unowned_planet(self, session):
        """Find an unowned planet in the galaxy."""
        for system in session.galaxy.systems.values():
            for planet in system.planets:
                if planet.owner_id is None:
                    return planet
        return None

    def test_colonies_are_planet_objects(self, game_session_with_state):
        session = game_session_with_state
        planet = self._find_unowned_planet(session)
        if planet:
            session.empires[0].add_colony(planet)

        d = session.to_dict()
        restored = GameSession.from_dict(d)

        for empire in restored.empires:
            for colony in empire.colonies:
                # Should be an actual Planet object, not an int ID
                assert hasattr(colony, 'name'), (
                    f"Colony {colony} in empire {empire.id} is not a Planet object"
                )

    def test_colony_owner_id_matches_empire(self, game_session_with_state):
        session = game_session_with_state
        planet = self._find_unowned_planet(session)
        if planet:
            session.empires[0].add_colony(planet)

        d = session.to_dict()
        restored = GameSession.from_dict(d)

        for empire in restored.empires:
            for colony in empire.colonies:
                assert colony.owner_id == empire.id

    def test_colonies_exist_in_galaxy(self, game_session_with_state):
        session = game_session_with_state
        planet = self._find_unowned_planet(session)
        if planet:
            session.empires[0].add_colony(planet)

        d = session.to_dict()
        restored = GameSession.from_dict(d)

        for empire in restored.empires:
            for colony in empire.colonies:
                found = restored.galaxy.get_planet_by_id(colony.id)
                assert found is not None
                assert found.name == colony.name

    def test_colony_count_matches(self, game_session_with_state):
        session = game_session_with_state
        planet = self._find_unowned_planet(session)
        if planet:
            session.empires[0].add_colony(planet)

        original_counts = [len(e.colonies) for e in session.empires]
        d = session.to_dict()
        restored = GameSession.from_dict(d)
        restored_counts = [len(e.colonies) for e in restored.empires]
        assert original_counts == restored_counts


class TestFleetOrderReferenceResolution:
    """Verify fleet/planet order references are resolved after save/load."""

    def test_move_to_fleet_resolved(self, game_session_with_state):
        """MOVE_TO_FLEET target should be a Fleet object after load."""
        session = game_session_with_state
        empire0 = session.empires[0]
        empire1 = session.empires[1]
        if empire0.fleets and empire1.fleets:
            target_fleet = empire1.fleets[0]
            order = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
            empire0.fleets[0].orders.append(order)

            d = session.to_dict()
            restored = GameSession.from_dict(d)

            pursuing_fleet = restored.empires[0].fleets[0]
            # Find the MOVE_TO_FLEET order
            mtf_orders = [o for o in pursuing_fleet.orders if o.type == OrderType.MOVE_TO_FLEET]
            if mtf_orders:
                assert isinstance(mtf_orders[0].target, Fleet), (
                    f"MOVE_TO_FLEET target should be Fleet, got {type(mtf_orders[0].target)}"
                )

    def test_colonize_resolved_to_planet(self, game_session_with_state):
        """COLONIZE target should be a Planet object after load."""
        session = game_session_with_state
        if session.empires[0].fleets and session.galaxy.systems:
            system = list(session.galaxy.systems.values())[0]
            if system.planets:
                planet = system.planets[0]
                order = FleetOrder(OrderType.COLONIZE, planet)
                session.empires[0].fleets[0].orders.append(order)

                d = session.to_dict()
                restored = GameSession.from_dict(d)

                fleet = restored.empires[0].fleets[0]
                col_orders = [o for o in fleet.orders if o.type == OrderType.COLONIZE]
                if col_orders:
                    from game.strategy.data.planet import Planet
                    assert isinstance(col_orders[0].target, Planet)

    def test_unresolvable_fleet_ref_removed(self, game_session_with_state):
        """Order referencing a deleted fleet should be removed with warning."""
        session = game_session_with_state
        if session.empires[0].fleets:
            # Create order targeting a non-existent fleet ID
            order = FleetOrder(OrderType.MOVE_TO_FLEET, None)
            order.target = Fleet(fleet_id=99999, owner_id=99, location=HexCoord(0, 0))
            session.empires[0].fleets[0].orders.append(order)

            d = session.to_dict()
            restored = GameSession.from_dict(d)

            fleet = restored.empires[0].fleets[0]
            # The unresolvable MOVE_TO_FLEET order should have been removed
            mtf_orders = [o for o in fleet.orders if o.type == OrderType.MOVE_TO_FLEET]
            assert len(mtf_orders) == 0


class TestPursuerTrackerRebuild:
    """Verify pursuer tracker is rebuilt after save/load."""

    def test_pursuers_registered_after_load(self, game_session_with_state):
        """After load with MOVE_TO_FLEET, target fleet's pursuer_tracker includes pursuer."""
        session = game_session_with_state
        empire0 = session.empires[0]
        empire1 = session.empires[1]
        if empire0.fleets and empire1.fleets:
            target_fleet = empire1.fleets[0]
            order = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
            empire0.fleets[0].orders.append(order)

            d = session.to_dict()
            restored = GameSession.from_dict(d)

            restored_target = restored.empires[1].fleets[0]
            pursuers = restored_target.pursuer_tracker.pursuers
            # The pursuing fleet should be registered
            assert len(pursuers) >= 1


class TestFleetRegistrationWithGalaxy:
    """Verify fleets are registered with galaxy after save/load."""

    def test_all_fleets_registered(self, game_session_with_state):
        session = game_session_with_state
        d = session.to_dict()
        restored = GameSession.from_dict(d)

        for empire in restored.empires:
            for fleet in empire.fleets:
                found = restored.galaxy.get_fleet_by_id(fleet.id)
                assert found is not None, (
                    f"Fleet {fleet.id} not registered with galaxy"
                )

    def test_fleet_count_matches(self, game_session_with_state):
        session = game_session_with_state
        original_count = sum(len(e.fleets) for e in session.empires)
        d = session.to_dict()
        restored = GameSession.from_dict(d)
        restored_count = sum(len(e.fleets) for e in restored.empires)
        assert original_count == restored_count


class TestGalaxyBackReferences:
    """Verify empire galaxy back-references after save/load."""

    def test_empires_have_galaxy_reference(self, game_session_with_state):
        session = game_session_with_state
        d = session.to_dict()
        restored = GameSession.from_dict(d)

        for empire in restored.empires:
            assert empire._galaxy is not None, (
                f"Empire {empire.id} has no galaxy back-reference"
            )
