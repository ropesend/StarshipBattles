"""Tests for ShipInstanceBridge - extracted simulation bridge logic."""

import pytest
from unittest.mock import MagicMock, patch

from game.core.component_state import ComponentState, component_state_key
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.ship_instance_bridge import ShipInstanceBridge


@pytest.fixture
def ship():
    """ShipInstance with damage/resource state for bridge testing."""
    s = ShipInstance(
        instance_id='bridge-test-1',
        design_id='TestDesign',
        name='Test Ship',
        owner_id=1,
        design_data={'name': 'TestDesign', 'layers': {}},
        current_hp=80,
        components={
            component_state_key('comp_1', 0): ComponentState(
                component_id='comp_1', instance_index=0, current_hp=50.0,
                max_hp=100.0,
            ),
        },
        _consumable_levels={'fuel': 75.0},
    )
    return s


@pytest.fixture
def bridge(ship):
    """ShipInstanceBridge wrapping a test ship."""
    return ShipInstanceBridge(ship)


def _make_mock_post_battle_ship(
    hp=80, max_hp=100, is_alive=True, is_derelict=False,
    components=None, resources=None,
):
    """Create a mock IPostBattleShip."""
    mock_ship = MagicMock()
    mock_ship.hp = hp
    mock_ship.max_hp = max_hp
    mock_ship.is_alive = is_alive
    mock_ship.is_derelict = is_derelict

    # Layers with components
    if components is None:
        components = []
    mock_layer = MagicMock()
    mock_layer.components = components
    mock_ship.layers = {'CORE': mock_layer}

    # Resources
    if resources is not None:
        mock_ship.resources = MagicMock()
        mock_ship.resources.get_resource_names.return_value = list(resources.keys())
        mock_ship.resources.get_value = lambda name: resources[name]
    else:
        mock_ship.resources = None

    return mock_ship


class TestCaptureResourceLevels:
    def test_extracts_resource_values(self):
        """Captures all resource values from a ship."""
        mock_ship = _make_mock_post_battle_ship(
            resources={'fuel': 50.0, 'energy': 25.0}
        )
        result = ShipInstanceBridge._capture_resource_levels(mock_ship)
        assert result == {'fuel': 50.0, 'energy': 25.0}

    def test_returns_empty_dict_when_no_resources(self):
        """Returns empty dict if ship has no resource registry."""
        mock_ship = _make_mock_post_battle_ship(resources=None)
        mock_ship.resources = None
        result = ShipInstanceBridge._capture_resource_levels(mock_ship)
        assert result == {}


class TestUpdateFromShip:
    def test_updates_hp_when_damaged(self, bridge, ship):
        """Updates current_hp when ship is alive but damaged."""
        mock_ship = _make_mock_post_battle_ship(hp=60, max_hp=100, is_alive=True)
        bridge.update_from_ship(mock_ship)
        assert ship.current_hp == 60
        assert ship.is_alive is True

    def test_clears_hp_when_full_health(self, bridge, ship):
        """Clears current_hp when ship is at full health."""
        mock_ship = _make_mock_post_battle_ship(hp=100, max_hp=100, is_alive=True)
        bridge.update_from_ship(mock_ship)
        assert ship.current_hp is None

    def test_updates_hp_when_dead(self, bridge, ship):
        """Sets is_alive=False and current_hp=0 when ship destroyed."""
        mock_ship = _make_mock_post_battle_ship(hp=0, max_hp=100, is_alive=False)
        bridge.update_from_ship(mock_ship)
        assert ship.is_alive is False
        assert ship.current_hp == 0

    def test_captures_per_instance_component_state(self, bridge, ship):
        """Captures per-instance HP into the authoritative `components` dict."""
        comp = MagicMock()
        comp.id = 'engine_0'
        comp.current_hp = 30
        comp.max_hp = 50
        comp.is_active = True
        mock_ship = _make_mock_post_battle_ship(components=[comp])
        bridge.update_from_ship(mock_ship)
        # PROJ-276 Phase 3: legacy `component_damage` mirror is no longer
        # written by the bridge; `components` is the sole source of truth.
        key = component_state_key('engine_0', 0)
        assert key in ship.components
        assert ship.components[key].current_hp == 30.0
        assert ship.components[key].instance_index == 0

    def test_increments_battles_survived(self, bridge, ship):
        """Increments battles_survived counter."""
        original = ship.battles_survived
        mock_ship = _make_mock_post_battle_ship()
        bridge.update_from_ship(mock_ship)
        assert ship.battles_survived == original + 1

    def test_invalidates_stats_cache(self, bridge, ship):
        """Invalidates the stats cache after update."""
        ship._cached_stats = {'some': 'data'}
        mock_ship = _make_mock_post_battle_ship()
        bridge.update_from_ship(mock_ship)
        assert ship._cached_stats is None

    def test_sets_derelict_status(self, bridge, ship):
        """Updates is_derelict from post-battle ship."""
        mock_ship = _make_mock_post_battle_ship(
            is_alive=True, is_derelict=True, hp=0, max_hp=100
        )
        bridge.update_from_ship(mock_ship)
        assert ship.is_derelict is True


class TestToShip:
    @patch('game.simulation.entities.ship_serialization.ShipSerializer')
    def test_creates_ship_with_position_and_team(self, mock_serializer_cls, bridge, ship):
        """to_ship creates Ship with correct position and team_id."""
        mock_sim_ship = MagicMock()
        mock_sim_ship.max_hp = 100
        mock_sim_ship.resources = None
        mock_sim_ship.layers = {}
        mock_serializer_cls.from_dict.return_value = mock_sim_ship
        mock_registries = MagicMock()

        result = bridge.to_ship((1000, 2000), team_id=1, registries=mock_registries)

        assert mock_sim_ship.x == 1000
        assert mock_sim_ship.y == 2000
        assert mock_sim_ship.team_id == 1
        mock_sim_ship.recalculate_stats.assert_called_once()
        assert result is mock_sim_ship

    @patch('game.simulation.entities.ship_serialization.ShipSerializer')
    def test_applies_hp_damage(self, mock_serializer_cls, bridge, ship):
        """to_ship applies HP damage when current_hp is set."""
        mock_sim_ship = MagicMock()
        mock_sim_ship.max_hp = 100
        mock_sim_ship.resources = None
        mock_sim_ship.layers = {}
        mock_serializer_cls.from_dict.return_value = mock_sim_ship
        ship.current_hp = 70  # 30 damage

        bridge.to_ship((0, 0), team_id=0, registries=MagicMock())

        mock_sim_ship.combat_engine.take_damage.assert_called_once_with(30)

    @patch('game.simulation.entities.ship_serialization.ShipSerializer')
    def test_applies_consumable_levels(self, mock_serializer_cls, bridge, ship):
        """to_ship applies resource levels to the simulation ship."""
        mock_resources = MagicMock()
        mock_sim_ship = MagicMock()
        mock_sim_ship.max_hp = 100
        mock_sim_ship.resources = mock_resources
        mock_sim_ship.layers = {}
        mock_serializer_cls.from_dict.return_value = mock_sim_ship
        ship.current_hp = None
        ship._consumable_levels = {'fuel': 50.0}

        bridge.to_ship((0, 0), team_id=0, registries=MagicMock())

        mock_resources.set_value.assert_called_once_with('fuel', 50.0)


class TestToShipPerInstanceDamage:
    """PROJ-276: per-instance damage must be applied from `components`,
    and the legacy `component_damage` dict must NOT be consulted."""

    @patch('game.simulation.entities.ship_serialization.ShipSerializer')
    def test_per_instance_damage_only_targets_matching_instance(
        self, mock_serializer_cls
    ):
        """A ship with 3 identical components and damage on instance #1
        only should produce a Ship where only that specific instance
        takes damage — the other two stay at full HP."""
        # Three identical laser_cannon components on the simulation side.
        comp0, comp1, comp2 = MagicMock(), MagicMock(), MagicMock()
        for c in (comp0, comp1, comp2):
            c.id = 'laser_cannon'
            c.current_hp = 40
            c.max_hp = 40
        mock_layer = MagicMock()
        mock_layer.components = [comp0, comp1, comp2]

        mock_sim_ship = MagicMock()
        mock_sim_ship.max_hp = 100
        mock_sim_ship.resources = None
        mock_sim_ship.layers = {'OUTER': mock_layer}
        mock_serializer_cls.from_dict.return_value = mock_sim_ship

        instance = ShipInstance(
            instance_id='multi-1',
            design_id='Tri-Laser',
            name='Tri',
            owner_id=0,
            design_data={'layers': {}},
        )
        # Instance #1 damaged to 20 HP; #0 and #2 at full 40.
        instance.components = {
            component_state_key('laser_cannon', 0): ComponentState(
                'laser_cannon', 0, current_hp=40
            ),
            component_state_key('laser_cannon', 1): ComponentState(
                'laser_cannon', 1, current_hp=20
            ),
            component_state_key('laser_cannon', 2): ComponentState(
                'laser_cannon', 2, current_hp=40
            ),
        }
        bridge = ShipInstanceBridge(instance)

        bridge.to_ship((0, 0), team_id=0, registries=MagicMock())

        # Only instance #1 takes damage (40 - 20 = 20 HP).
        comp0.take_damage.assert_not_called()
        comp1.take_damage.assert_called_once_with(20)
        comp2.take_damage.assert_not_called()

    @patch('game.simulation.entities.ship_serialization.ShipSerializer')
    def test_ship_with_empty_components_applies_no_damage(
        self, mock_serializer_cls
    ):
        """After PROJ-276 the bridge only reads `components`. A ship
        with no per-instance state attached leaves every component at
        full HP — no damage is applied."""
        # Three laser_cannons on the simulation side, all full HP.
        comp0, comp1, comp2 = MagicMock(), MagicMock(), MagicMock()
        for c in (comp0, comp1, comp2):
            c.id = 'laser_cannon'
            c.current_hp = 40
            c.max_hp = 40
        mock_layer = MagicMock()
        mock_layer.components = [comp0, comp1, comp2]

        mock_sim_ship = MagicMock()
        mock_sim_ship.max_hp = 100
        mock_sim_ship.resources = None
        mock_sim_ship.layers = {'OUTER': mock_layer}
        mock_serializer_cls.from_dict.return_value = mock_sim_ship

        instance = ShipInstance(
            instance_id='no-state-1',
            design_id='Tri-Laser',
            name='Tri',
            owner_id=0,
            design_data={'layers': {}},
            # `components` intentionally empty.
        )
        assert instance.components == {}
        bridge = ShipInstanceBridge(instance)

        bridge.to_ship((0, 0), team_id=0, registries=MagicMock())

        comp0.take_damage.assert_not_called()
        comp1.take_damage.assert_not_called()
        comp2.take_damage.assert_not_called()
