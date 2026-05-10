"""
BUG-107: Verify that GameSession.from_dict() propagates registries to all ships.

Loading a save must pass registries through the deserialization chain:
  GameSession -> Empire -> Fleet -> ShipInstance

Without this, ShipInstance.get_calculated_stats() raises ValueError on turn advance.
"""
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig


class TestSaveLoadRegistryPropagation:
    """Registries must survive a save/load round-trip."""

    def test_loaded_ships_have_registries(self):
        """BUG-107: Ships loaded via from_dict() must have _registries set."""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10,
        )

        original = GameSession(config=config)

        # Find an empire with fleets that have ships
        # (initial game state may or may not have ships; add one if needed)
        empire = original.empires[0]
        if not empire.fleets or not any(f.ships for f in empire.fleets):
            from game.strategy.data.ship_instance import ShipInstance
            from game.strategy.data.fleet import Fleet
            ship = ShipInstance(
                instance_id="test-ship-001",
                design_id="escort_a",
                name="Test Ship",
                owner_id=empire.id,
                design_data={"name": "Escort A", "ship_class": "Escort"},
            )
            ship._registries = original._registries
            if not empire.fleets:
                fleet = Fleet(
                    fleet_id=9999,
                    owner_id=empire.id,
                    location=empire.colonies[0].location if empire.colonies else None,
                )
                empire.fleets.append(fleet)
            empire.fleets[0].ships.append(ship)

        # Round-trip
        data = original.to_dict()
        restored = GameSession.from_dict(data)

        # Every ship in every fleet must have registries set
        for emp in restored.empires:
            for fleet in emp.fleets:
                for ship in fleet.ships:
                    assert ship._registries is not None, (
                        f"Ship '{ship.name}' in fleet {fleet.fleet_id} of empire "
                        f"'{emp.name}' has _registries=None after load. "
                        f"GameSession.from_dict() must pass registries to Empire.from_dict()."
                    )

    def test_loaded_ships_can_calculate_stats(self):
        """BUG-107: Ships loaded via from_dict() must be able to calculate stats without error."""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10,
        )

        original = GameSession(config=config)

        # Ensure at least one ship exists
        empire = original.empires[0]
        if not empire.fleets or not any(f.ships for f in empire.fleets):
            from game.strategy.data.ship_instance import ShipInstance
            from game.strategy.data.fleet import Fleet
            ship = ShipInstance(
                instance_id="test-ship-002",
                design_id="escort_a",
                name="Test Ship 2",
                owner_id=empire.id,
                design_data={"name": "Escort A", "ship_class": "Escort"},
            )
            ship._registries = original._registries
            if not empire.fleets:
                fleet = Fleet(
                    fleet_id=9998,
                    owner_id=empire.id,
                    location=empire.colonies[0].location if empire.colonies else None,
                )
                empire.fleets.append(fleet)
            empire.fleets[0].ships.append(ship)

        # Round-trip
        data = original.to_dict()
        restored = GameSession.from_dict(data)

        # Stats calculation must not raise
        for emp in restored.empires:
            for fleet in emp.fleets:
                for ship in fleet.ships:
                    # This would raise ValueError if _registries is None
                    stats = ship.get_calculated_stats()
                    assert isinstance(stats, dict)
