"""Regression tests for staging yard spawn crashes.

Crash 1: _spawn_to_staging_yard passed empire.id (int) to _load_design(),
which then tried .id on the int again -> AttributeError.

Crash 2: Mass calculation called .get('mass') on a Component object
(returned by registries.components), which has no .get() method.
"""

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
    """Regression: mass calculation must handle Component objects from registry."""

    def test_mass_from_component_object_not_dict(self):
        """When registries.components returns a Component object (not a dict),
        the mass calculation must use attribute access, not .get()."""
        # Create a mock Component object with a mass attribute (not a dict)
        mock_component = MagicMock()
        mock_component.mass = 25.0
        # Ensure .get() is NOT available (like a real Component)
        del mock_component.get

        mock_registries = MagicMock()
        mock_registries.components.get.return_value = mock_component

        spawner = ProductionSpawner(registries=mock_registries)
        empire = _make_empire(empire_id=1)
        planet = _make_planet()
        design_data = {
            'name': 'TestFighter',
            'layers': {
                'weapons': [{'id': 'laser_mk1', 'mass': 10}]
            }
        }
        item = {'design_id': 'fighter_1', 'type': 'fighter',
                'design_data': design_data}

        # This must NOT raise AttributeError: 'Component' object has no attribute 'get'
        spawner._spawn_to_staging_yard(planet, 'fighter_1', item, empire, '/fake/save')

        staging_item = planet.add_to_staging_yard.call_args[0][0]
        assert staging_item['mass'] == 25.0

    def test_mass_fallback_when_component_not_in_registry(self):
        """When a component ID is not in the registry, fall back to the
        inline mass from the design data dict."""
        mock_registries = MagicMock()
        mock_registries.components.get.return_value = None

        spawner = ProductionSpawner(registries=mock_registries)
        empire = _make_empire(empire_id=1)
        planet = _make_planet()
        design_data = {
            'name': 'TestPod',
            'layers': {
                'hull': [{'id': 'unknown_comp', 'mass': 15}]
            }
        }
        item = {'design_id': 'pod_1', 'type': 'drop_pod',
                'design_data': design_data}

        spawner._spawn_to_staging_yard(planet, 'pod_1', item, empire, '/fake/save')

        staging_item = planet.add_to_staging_yard.call_args[0][0]
        assert staging_item['mass'] == 15
