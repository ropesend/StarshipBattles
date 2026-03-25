"""Registry injection verification tests (PROJ-223 Phase 4).

BUG-107 regression guard: ensures all DI-dependent objects receive
registries after deserialization through GameSession.from_dict().
"""

import json
import pytest

from game.strategy.engine.game_session import GameSession
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance


class TestRegistryInjectionAfterLoad:
    """Verify registry injection through the full deserialization chain."""

    def test_all_ship_instances_have_registries(self, game_session_with_state):
        """After save/load, all ShipInstance objects must have _registries set."""
        session = game_session_with_state
        d = session.to_dict()
        restored = GameSession.from_dict(d)

        for empire in restored.empires:
            for fleet in empire.fleets:
                for ship in fleet.ships:
                    assert ship._registries is not None, (
                        f"Ship {ship.instance_id} in fleet {fleet.id} "
                        f"empire {empire.id} has _registries=None after load"
                    )

    def test_get_calculated_stats_works_after_load(self, game_session_with_state):
        """After save/load, ship stats calculation should work without error."""
        session = game_session_with_state
        d = session.to_dict()
        restored = GameSession.from_dict(d)

        for empire in restored.empires:
            for fleet in empire.fleets:
                for ship in fleet.ships:
                    if ship.design_data:
                        # Should not raise — registries are injected
                        try:
                            stats = ship.get_calculated_stats()
                            # Stats may be None if design_data is minimal, but shouldn't error
                        except Exception as e:
                            pytest.fail(
                                f"get_calculated_stats() failed for ship {ship.instance_id}: {e}"
                            )

    def test_game_session_registries_populated(self, game_session_with_state):
        """GameSession._registries should be populated after from_dict()."""
        session = game_session_with_state
        d = session.to_dict()
        restored = GameSession.from_dict(d)

        assert restored._registries is not None
        assert restored._registries.components is not None
        assert len(restored._registries.components) > 0

    def test_turn_engine_receives_registries(self, game_session_with_state):
        """TurnEngine should have registries after from_dict()."""
        session = game_session_with_state
        d = session.to_dict()
        restored = GameSession.from_dict(d)

        assert restored.turn_engine is not None
        assert restored.turn_engine._registries is not None

    def test_fleet_without_registries_ships_get_none(self):
        """Deliberately omitting registries → ShipInstance gets None."""
        from tests.fixtures.strategy_entities import create_test_fleet
        fleet = create_test_fleet(num_ships=2)
        d = fleet.to_dict()
        # Load without registries
        restored = Fleet.from_dict(d, registries=None)
        for ship in restored.ships:
            assert ship._registries is None
