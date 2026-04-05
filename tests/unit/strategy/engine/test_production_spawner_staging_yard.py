"""Regression tests for staging yard spawn crashes.

Crash 1: _spawn_to_staging_yard passed empire.id (int) to _load_design(),
which then tried .id on the int again -> AttributeError.

Crash 2: Mass calculation called .get('mass') on a Component object
(returned by registries.components), which has no .get() method.
"""

import pytest
from unittest.mock import MagicMock, patch
from game.strategy.engine.production_spawner import ProductionSpawner


def _make_empire(empire_id: int = 1) -> MagicMock:
    empire = MagicMock()
    empire.id = empire_id
    return empire


def _make_planet() -> MagicMock:
    planet = MagicMock()
    planet.name = "TestPlanet"
    planet.add_to_staging_yard = MagicMock(return_value=True)
    return planet


class TestSpawnToStagingYardEmpireParam:
    """Regression: _spawn_to_staging_yard must pass Empire object to _load_design."""

    def test_load_design_receives_empire_object_not_int(self):
        """When design_data is not cached in the item, _load_design must
        receive the Empire object (not empire.id) so it can access .id itself."""
        spawner = ProductionSpawner(registries=None)
        empire = _make_empire(empire_id=42)
        planet = _make_planet()
        item = {'design_id': 'fighter_mk1', 'type': 'fighter'}

        with patch.object(spawner, '_load_design', return_value={'name': 'Fighter'}) as mock_load:
            spawner._spawn_to_staging_yard(planet, 'fighter_mk1', item, empire, '/fake/save')

        # The critical assertion: _load_design receives the Empire object, not an int
        mock_load.assert_called_once_with('fighter_mk1', empire, '/fake/save')

    def test_spawn_to_staging_yard_no_crash_with_real_empire(self):
        """End-to-end: calling _spawn_to_staging_yard with an Empire object
        must not raise AttributeError on empire.id."""
        spawner = ProductionSpawner(registries=None)
        empire = _make_empire(empire_id=7)
        planet = _make_planet()
        item = {'design_id': 'drop_pod_1', 'type': 'drop_pod',
                'design_data': {'name': 'DropPod', 'components': []}}

        # Should not raise - design_data is in the item so _load_design is skipped
        spawner._spawn_to_staging_yard(planet, 'drop_pod_1', item, empire, '/fake/save')
        planet.add_to_staging_yard.assert_called_once()

    def test_spawn_to_staging_yard_uses_empire_id_for_owner(self):
        """The staging_item dict should contain owner_id from empire.id."""
        spawner = ProductionSpawner(registries=None)
        empire = _make_empire(empire_id=99)
        planet = _make_planet()
        item = {'design_id': 'fighter_x', 'type': 'fighter',
                'design_data': {'name': 'FighterX'}}

        spawner._spawn_to_staging_yard(planet, 'fighter_x', item, empire, '/fake/save')

        staging_item = planet.add_to_staging_yard.call_args[0][0]
        assert staging_item['owner_id'] == 99


class TestSpawnToStagingYardMassCalculation:
    """Mass calculation uses ShipStatsCalculator (single source of truth)."""

    def test_mass_calculated_via_stats_calculator(self):
        """Mass should be calculated by ShipStatsCalculator with modifiers applied."""
        from game.core.registry import GameRegistries
        from game.simulation.components.component import load_components_data, load_modifiers_data
        from game.simulation.entities.ship_loader import load_vehicle_classes_data

        minimal = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
        registries = GameRegistries(
            components=load_components_data(registries=minimal),
            modifiers=load_modifiers_data(),
            vehicle_classes=load_vehicle_classes_data(),
            resources={}
        )

        spawner = ProductionSpawner(registries=registries)
        empire = _make_empire(empire_id=1)
        planet = _make_planet()
        # Design with a real component and size modifier (0.5 = half mass)
        design_data = {
            'name': 'TestPod',
            'ship_class': 'Drop Pod (Small)',
            'layers': {
                'CORE': [{'id': 'crew_quarters', 'modifiers': [
                    {'id': 'simple_size_mount', 'value': 0.5}
                ]}]
            }
        }
        item = {'design_id': 'pod_1', 'type': 'drop_pod',
                'design_data': design_data}

        spawner._spawn_to_staging_yard(planet, 'pod_1', item, empire, '/fake/save')

        staging_item = planet.add_to_staging_yard.call_args[0][0]
        # crew_quarters base mass=30, with 0.5 size modifier = 15
        assert staging_item['mass'] == pytest.approx(15.0, abs=1.0)
