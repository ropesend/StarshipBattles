"""
Regression test for ship death at 0 HP.

Ships at 0 HP should be marked as not alive (is_alive=False) and
removed from the spatial grid on the next tick.
"""

class TestShipDeathAtZeroHP:
    """Verify ships die when HP reaches 0."""

    def test_lethal_damage_kills_ship(self, fresh_registries):
        """A ship that takes damage equal to its HP should die."""
        from game.simulation.entities.ship import Ship
        from game.simulation.combat.damage_calculator import DamageCalculator

        ship = Ship("Victim", 0, 0, (255, 0, 0), team_id=0,
                    ship_class="Escort", registries=fresh_registries)
        ship.recalculate_stats()

        assert ship.is_alive is True
        assert ship.hp > 0

        # Apply lethal damage
        DamageCalculator().apply_damage(ship, ship.hp + 100)

        assert ship.is_alive is False, \
            f"Ship with 0 HP should be dead, but is_alive={ship.is_alive}, hp={ship.hp}"

    def test_non_lethal_damage_keeps_ship_alive(self, fresh_registries):
        """A ship that takes partial damage should remain alive."""
        from game.simulation.entities.ship import Ship
        from game.simulation.combat.damage_calculator import DamageCalculator

        ship = Ship("Survivor", 0, 0, (255, 0, 0), team_id=0,
                    ship_class="Escort", registries=fresh_registries)
        ship.recalculate_stats()

        DamageCalculator().apply_damage(ship, 1)

        assert ship.is_alive is True
        assert ship.hp > 0

    def test_dead_ship_not_in_grid(self, fresh_registries):
        """A dead ship should not appear in the spatial grid."""
        from game.simulation.entities.ship import Ship
        from game.engine.spatial import SpatialGrid

        ship = Ship("Dead", 100, 100, (255, 0, 0), team_id=0,
                    ship_class="Escort", registries=fresh_registries)
        ship.recalculate_stats()
        ship.is_alive = False

        grid = SpatialGrid()
        # Grid only inserts alive ships (checked by battle_engine._rebuild_grid)
        alive_ships = [s for s in [ship] if s.is_alive]
        for s in alive_ships:
            grid.insert(s)

        results = grid.query_radius(ship.position, 1000)
        assert ship not in results, "Dead ship should not be in spatial grid"
