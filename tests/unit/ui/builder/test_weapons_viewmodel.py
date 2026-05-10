"""
Tests for WeaponsViewModel - pure data/calculation layer for weapons panel.
"""
import pytest
import math
from unittest.mock import Mock, MagicMock, PropertyMock


class TestWeaponsViewModelImports:
    """Test that WeaponsViewModel can be imported without pygame dependencies."""

    def test_import_weapons_viewmodel(self):
        """WeaponsViewModel should import cleanly without pygame."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        assert WeaponsViewModel is not None

    def test_import_weapons_events(self):
        """WeaponsEvents should be importable."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsEvents
        assert WeaponsEvents is not None


class TestWeaponsEvents:
    """Test event constants."""

    def test_event_constants_defined(self):
        """All expected event constants should be defined."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsEvents

        assert hasattr(WeaponsEvents, 'WEAPONS_UPDATED')
        assert hasattr(WeaponsEvents, 'FILTER_CHANGED')
        assert hasattr(WeaponsEvents, 'TARGET_CHANGED')
        assert hasattr(WeaponsEvents, 'HOVER_CHANGED')


class TestWeaponsViewModelInit:
    """Test WeaponsViewModel initialization."""

    def test_init_with_event_bus(self):
        """ViewModel should initialize with event bus."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        bus = WorkshopEventBus()
        vm = WeaponsViewModel(bus)

        assert vm.event_bus is bus
        assert vm.weapon_groups == []
        assert vm.max_range == 0

    def test_init_default_filter_states(self):
        """ViewModel should have all filters enabled by default."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())

        assert vm.filter_states['projectile'] is True
        assert vm.filter_states['beam'] is True
        assert vm.filter_states['seeker'] is True


class TestWeaponsViewModelFiltering:
    """Test weapon filtering functionality."""

    def test_toggle_filter_emits_event(self):
        """Toggling a filter should emit FILTER_CHANGED event."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel, WeaponsEvents
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        bus = WorkshopEventBus()
        vm = WeaponsViewModel(bus)

        received = []
        bus.subscribe(WeaponsEvents.FILTER_CHANGED, lambda d: received.append(d))

        vm.toggle_filter('projectile')

        assert len(received) == 1
        assert received[0]['projectile'] is False

    def test_toggle_filter_changes_state(self):
        """Toggling a filter should change its state."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())

        assert vm.filter_states['beam'] is True
        vm.toggle_filter('beam')
        assert vm.filter_states['beam'] is False
        vm.toggle_filter('beam')
        assert vm.filter_states['beam'] is True

    def test_enable_all_filters(self):
        """enable_all_filters should set all filters to True."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())
        vm.filter_states['projectile'] = False
        vm.filter_states['beam'] = False

        vm.enable_all_filters()

        assert vm.filter_states['projectile'] is True
        assert vm.filter_states['beam'] is True
        assert vm.filter_states['seeker'] is True


class TestWeaponsViewModelTarget:
    """Test target management."""

    def test_set_target_stores_values(self):
        """Setting target should store name and defense mod."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())

        target_ship = Mock()
        target_ship.name = "Enemy Ship"
        target_ship.total_defense_score = 2.5

        vm.set_target(target_ship)

        assert vm.target_name == "Enemy Ship"
        assert vm.target_defense_mod == 2.5

    def test_set_target_emits_event(self):
        """Setting target should emit TARGET_CHANGED event."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel, WeaponsEvents
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        bus = WorkshopEventBus()
        vm = WeaponsViewModel(bus)

        received = []
        bus.subscribe(WeaponsEvents.TARGET_CHANGED, lambda d: received.append(d))

        target_ship = Mock()
        target_ship.name = "Enemy"
        target_ship.total_defense_score = 1.0
        vm.set_target(target_ship)

        assert len(received) == 1

    def test_clear_target(self):
        """clear_target should reset target values."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())

        target = Mock()
        target.name = "Target"
        target.total_defense_score = 1.0
        vm.set_target(target)

        vm.clear_target()

        assert vm.target_name is None
        assert vm.target_defense_mod == 0.0


class TestWeaponsViewModelGrouping:
    """Test weapon grouping logic."""

    def _make_mock_weapon(self, weapon_id, name, facing=0, arc=360, modifiers=None):
        """Create a mock weapon component."""
        weapon = Mock()
        weapon.id = weapon_id
        weapon.name = name
        weapon.modifiers = modifiers or []

        ability = Mock()
        ability.facing_angle = facing
        ability.firing_arc = arc

        weapon.get_ability.return_value = ability
        weapon.has_ability.side_effect = lambda t: t == 'WeaponAbility'

        return weapon

    def test_group_identical_weapons(self):
        """Identical weapons should be grouped with count."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())

        w1 = self._make_mock_weapon("laser_1", "Laser Cannon")
        w2 = self._make_mock_weapon("laser_1", "Laser Cannon")
        w3 = self._make_mock_weapon("laser_1", "Laser Cannon")

        groups = vm.group_weapons([w1, w2, w3])

        assert len(groups) == 1
        assert groups[0]['count'] == 3
        assert groups[0]['weapon'].name == "Laser Cannon"

    def test_different_weapons_not_grouped(self):
        """Different weapons should not be grouped."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())

        w1 = self._make_mock_weapon("laser_1", "Laser Cannon")
        w2 = self._make_mock_weapon("missile_1", "Missile Launcher")

        groups = vm.group_weapons([w1, w2])

        assert len(groups) == 2

    def test_same_id_different_facing_not_grouped(self):
        """Same weapon ID with different facing should not be grouped."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())

        w1 = self._make_mock_weapon("laser_1", "Laser", facing=0)
        w2 = self._make_mock_weapon("laser_1", "Laser", facing=90)

        groups = vm.group_weapons([w1, w2])

        assert len(groups) == 2


class TestWeaponsViewModelPointsOfInterest:
    """Test points of interest calculation."""

    def _make_projectile_weapon(self, weapon_range=1000, damage=50):
        """Create a mock projectile weapon."""
        weapon = Mock()
        weapon.name = "Test Projectile"

        ability = Mock()
        ability.range = weapon_range
        ability.damage = damage
        ability.get_damage = Mock(side_effect=lambda r: damage)  # Constant damage

        weapon.get_ability.return_value = ability
        weapon.has_ability.side_effect = lambda t: t in ['WeaponAbility', 'ProjectileWeaponAbility']

        return weapon

    def _make_beam_weapon(self, weapon_range=800, damage=30, base_accuracy=2.0, falloff=0.002):
        """Create a mock beam weapon."""
        weapon = Mock()
        weapon.name = "Test Beam"

        ability = Mock()
        ability.range = weapon_range
        ability.damage = damage
        ability.base_accuracy = base_accuracy
        ability.accuracy_falloff = falloff
        ability.get_damage = Mock(side_effect=lambda r: damage)

        weapon.get_ability.return_value = ability
        weapon.has_ability.side_effect = lambda t: t in ['WeaponAbility', 'BeamWeaponAbility']

        return weapon

    def _make_mock_ship(self, sensor_score=0.0):
        """Create a mock ship with sensor score."""
        ship = Mock()
        ship.get_total_sensor_score = Mock(return_value=sensor_score)
        return ship

    def test_projectile_poi_has_range_breakpoints(self):
        """Projectile weapons should have range percentage breakpoints."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())
        weapon = self._make_projectile_weapon(weapon_range=1000)
        ship = self._make_mock_ship()

        points = vm.get_points_of_interest(weapon, ship)

        # Should have points at 0%, 20%, 40%, 60%, 80%, 100% of range
        range_values = [p['range'] for p in points]
        assert 0 in range_values
        assert 200 in range_values
        assert 1000 in range_values

    def test_projectile_poi_no_accuracy(self):
        """Projectile weapons should have None accuracy."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())
        weapon = self._make_projectile_weapon()
        ship = self._make_mock_ship()

        points = vm.get_points_of_interest(weapon, ship)

        for point in points:
            assert point['accuracy'] is None

    def test_beam_poi_has_accuracy_values(self):
        """Beam weapons should have accuracy calculated at each point."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())
        weapon = self._make_beam_weapon()
        ship = self._make_mock_ship()

        points = vm.get_points_of_interest(weapon, ship)

        # At least some points should have accuracy
        accuracy_points = [p for p in points if p['accuracy'] is not None]
        assert len(accuracy_points) > 0

    def test_poi_sorted_by_range(self):
        """Points of interest should be sorted by range."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())
        weapon = self._make_beam_weapon()
        ship = self._make_mock_ship()

        points = vm.get_points_of_interest(weapon, ship)

        ranges = [p['range'] for p in points]
        assert ranges == sorted(ranges)


class TestWeaponsViewModelThresholdCalculation:
    """Test threshold range calculation for beam weapons."""

    def _make_beam_weapon(self, weapon_range=1000, base_accuracy=3.0, falloff=0.003):
        """Create a mock beam weapon with configurable parameters."""
        weapon = Mock()
        ability = Mock()
        ability.range = weapon_range
        ability.damage = 50
        ability.base_accuracy = base_accuracy
        ability.accuracy_falloff = falloff
        weapon.get_ability.return_value = ability
        weapon.has_ability.side_effect = lambda t: t in ['WeaponAbility', 'BeamWeaponAbility']
        return weapon

    def _make_mock_ship(self, sensor_score=1.0):
        """Create a mock ship."""
        ship = Mock()
        ship.get_total_sensor_score = Mock(return_value=sensor_score)
        return ship

    def test_threshold_ranges_returns_list(self):
        """calculate_threshold_ranges should return a list of tuples."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())
        weapon = self._make_beam_weapon()
        ship = self._make_mock_ship()

        results = vm.calculate_threshold_ranges(weapon, ship)

        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, tuple) for r in results)

    def test_threshold_ranges_format(self):
        """Each threshold result should be (threshold, range, damage)."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())
        weapon = self._make_beam_weapon()
        ship = self._make_mock_ship()

        results = vm.calculate_threshold_ranges(weapon, ship)

        for threshold, range_val, damage in results:
            assert 0 < threshold <= 1
            assert damage is not None


class TestWeaponsViewModelLoadWeapons:
    """Test loading weapons from a ship."""

    def _make_mock_ship_with_weapons(self, weapons):
        """Create a ship with specified weapons in layers."""
        ship = Mock()
        ship.get_total_sensor_score = Mock(return_value=0.0)

        layer_data = Mock()
        layer_data.components = weapons

        ship.layers = {'main': layer_data}
        return ship

    def _make_weapon_component(self, name, weapon_type='projectile'):
        """Create a mock weapon component."""
        weapon = Mock()
        weapon.id = f"{weapon_type}_{name}"
        weapon.name = name
        weapon.modifiers = []
        weapon.sprite_index = 1

        ability = Mock()
        ability.range = 500
        ability.damage = 25
        ability.facing_angle = 0
        ability.firing_arc = 360

        weapon.get_ability.return_value = ability

        type_abilities = ['WeaponAbility']
        if weapon_type == 'projectile':
            type_abilities.append('ProjectileWeaponAbility')
        elif weapon_type == 'beam':
            type_abilities.append('BeamWeaponAbility')
        elif weapon_type == 'seeker':
            type_abilities.append('SeekerWeaponAbility')

        weapon.has_ability.side_effect = lambda t: t in type_abilities
        return weapon

    def test_load_weapons_updates_cache(self):
        """load_weapons should update weapon_groups."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())

        w1 = self._make_weapon_component("Laser 1")
        w2 = self._make_weapon_component("Laser 2")
        ship = self._make_mock_ship_with_weapons([w1, w2])

        vm.load_weapons(ship)

        assert len(vm.weapon_groups) == 2

    def test_load_weapons_calculates_max_range(self):
        """load_weapons should calculate max_range from all weapons."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())

        w1 = self._make_weapon_component("Short Range")
        w1.get_ability.return_value.range = 400

        w2 = self._make_weapon_component("Long Range")
        w2.get_ability.return_value.range = 1200

        ship = self._make_mock_ship_with_weapons([w1, w2])

        vm.load_weapons(ship)

        assert vm.max_range == 1200

    def test_load_weapons_emits_event(self):
        """load_weapons should emit WEAPONS_UPDATED event."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel, WeaponsEvents
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        bus = WorkshopEventBus()
        vm = WeaponsViewModel(bus)

        received = []
        bus.subscribe(WeaponsEvents.WEAPONS_UPDATED, lambda d: received.append(d))

        ship = self._make_mock_ship_with_weapons([])
        vm.load_weapons(ship)

        assert len(received) == 1

    def test_load_weapons_respects_filters(self):
        """load_weapons should filter based on current filter state."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())

        w1 = self._make_weapon_component("Projectile", 'projectile')
        w2 = self._make_weapon_component("Beam", 'beam')
        w3 = self._make_weapon_component("Seeker", 'seeker')

        ship = self._make_mock_ship_with_weapons([w1, w2, w3])

        # Disable beam filter
        vm.filter_states['beam'] = False
        vm.load_weapons(ship)

        # Should only have projectile and seeker
        names = [g['weapon'].name for g in vm.weapon_groups]
        assert 'Projectile' in names
        assert 'Seeker' in names
        assert 'Beam' not in names


class TestWeaponsViewModelHover:
    """Test hover state management."""

    def test_set_hovered_weapon(self):
        """Setting hovered weapon should store it."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())
        weapon = Mock()

        vm.set_hovered_weapon(weapon)

        assert vm.hovered_weapon is weapon

    def test_set_hovered_weapon_emits_event(self):
        """Setting hovered weapon should emit HOVER_CHANGED event."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel, WeaponsEvents
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        bus = WorkshopEventBus()
        vm = WeaponsViewModel(bus)

        received = []
        bus.subscribe(WeaponsEvents.HOVER_CHANGED, lambda d: received.append(d))

        weapon = Mock()
        vm.set_hovered_weapon(weapon)

        assert len(received) == 1

    def test_clear_hovered_weapon(self):
        """Clearing hovered weapon should set it to None."""
        from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel
        from game.ui.screens.builder.event_bus import WorkshopEventBus

        vm = WeaponsViewModel(WorkshopEventBus())
        vm.set_hovered_weapon(Mock())

        vm.set_hovered_weapon(None)

        assert vm.hovered_weapon is None
