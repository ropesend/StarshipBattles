"""
Tests for ShipStatsService - dynamic stat calculation from components.

PROJ-07: Strategy Layer Stats Calculation Refactor
"""

import pytest
from unittest.mock import MagicMock, patch


class MockComponent:
    """Mock component for testing without full registry."""

    def __init__(
        self,
        comp_id: str,
        mass: float = 100,
        max_hp: float = 100,
        abilities: dict = None,
        type_str: str = 'Generic',
        damage_threshold: float = 0.3
    ):
        self.id = comp_id
        self.mass = mass
        self.max_hp = max_hp
        self.abilities = abilities or {}
        self.type_str = type_str
        self.damage_threshold = damage_threshold


def make_design_data(components_by_layer: dict) -> dict:
    """Helper to create design_data structure for testing."""
    layers = {}
    for layer_name, comp_ids in components_by_layer.items():
        layers[layer_name] = [{'id': cid} for cid in comp_ids]
    return {'layers': layers}


class TestShipStatsServiceBasics:
    """Basic functionality tests."""

    def test_empty_design_returns_zeros(self):
        """Empty design should return zero stats."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        design_data = {'layers': {}}
        stats = ShipStatsService.calculate_stats(design_data)

        assert stats['max_hp'] == 0
        assert stats['mass'] == 0
        assert stats['resource_storage'].get('fuel', 0) == 0
        assert stats['strategic_movement'] == 0
        assert stats['warp_max_tonnage'] == 0

    def test_undamaged_component_full_effectiveness(self):
        """Undamaged components should have full effectiveness."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent('test_comp', mass=100, max_hp=200)
        effectiveness = ShipStatsService.get_component_effectiveness(
            'test_comp', comp, {}
        )

        assert effectiveness == 1.0

    def test_missing_component_skipped(self):
        """Components not in registry should be skipped with warning."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        design_data = make_design_data({'CORE': ['nonexistent_component']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {}  # Empty registry
            stats = ShipStatsService.calculate_stats(design_data)

        assert stats['max_hp'] == 0
        assert stats['mass'] == 0


class TestDamageEffectiveness:
    """Tests for damage effectiveness calculation."""

    def test_full_hp_full_effectiveness(self):
        """100% HP = 100% effectiveness."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent('engine', max_hp=100)
        eff = ShipStatsService.get_component_effectiveness('engine', comp, {})
        assert eff == 1.0

    def test_below_threshold_zero_effectiveness(self):
        """Below 30% HP = 0% effectiveness (inactive)."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent('engine', max_hp=100, damage_threshold=0.3)
        # At 25% HP (below 30% threshold)
        eff = ShipStatsService.get_component_effectiveness(
            'engine', comp, {'engine': 25}
        )
        assert eff == 0.0

    def test_at_threshold_zero_effectiveness(self):
        """At exactly 30% HP = 0% effectiveness."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent('engine', max_hp=100, damage_threshold=0.3)
        eff = ShipStatsService.get_component_effectiveness(
            'engine', comp, {'engine': 30}
        )
        assert eff == 0.0

    def test_gradual_degradation(self):
        """Between 30% and 100% HP = gradual degradation."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent('engine', max_hp=100, damage_threshold=0.3)

        # At 65% HP: (0.65 - 0.3) / (1.0 - 0.3) = 0.35 / 0.7 = 0.5
        eff = ShipStatsService.get_component_effectiveness(
            'engine', comp, {'engine': 65}
        )
        assert abs(eff - 0.5) < 0.01

        # At 100% HP = full
        eff_full = ShipStatsService.get_component_effectiveness(
            'engine', comp, {'engine': 100}
        )
        assert eff_full == 1.0

    def test_armor_never_degrades(self):
        """Armor should always be 100% effective regardless of damage."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        # Test by type
        armor_by_type = MockComponent('armor', max_hp=100, type_str='Armor')
        eff = ShipStatsService.get_component_effectiveness(
            'armor', armor_by_type, {'armor': 1}  # 1% HP
        )
        assert eff == 1.0

        # Test by ability marker
        armor_by_ability = MockComponent(
            'armor2', max_hp=100, type_str='Generic',
            abilities={'Armor': True}
        )
        eff2 = ShipStatsService.get_component_effectiveness(
            'armor2', armor_by_ability, {'armor2': 1}
        )
        assert eff2 == 1.0


class TestWarpCapability:
    """Tests for warp drive special handling."""

    def test_warp_requires_full_hp(self):
        """Warp drives must be at 100% HP to function."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent(
            'warp_drive', max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 5000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}]
            }
        )

        # Full HP - warp works
        eff = ShipStatsService._get_warp_effectiveness('warp_drive', comp, {})
        assert eff == 1.0

        # 99% HP - warp disabled
        eff_damaged = ShipStatsService._get_warp_effectiveness(
            'warp_drive', comp, {'warp_drive': 99}
        )
        assert eff_damaged == 0.0

    def test_damaged_warp_drive_zero_tonnage(self):
        """Damaged warp drive should contribute 0 to warp_max_tonnage."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        warp_comp = MockComponent(
            'warp_drive', max_hp=100, mass=50,
            abilities={
                'WarpJump': {'max_tonnage': 5000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}]
            }
        )

        design_data = make_design_data({'OUTER': ['warp_drive']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'warp_drive': warp_comp}

            # Undamaged - has warp capability
            stats_ok = ShipStatsService.calculate_stats(design_data, {})
            assert stats_ok['warp_max_tonnage'] == 5000
            assert stats_ok['warp_resource_costs'].get('energy', 0) == 500

            # Damaged - no warp capability
            stats_damaged = ShipStatsService.calculate_stats(
                design_data, {'warp_drive': 99}
            )
            assert stats_damaged['warp_max_tonnage'] == 0
            assert stats_damaged['warp_resource_costs'].get('energy', 0) == 0

    def test_multiple_warp_drives_largest_tonnage(self):
        """With multiple warp drives, use largest tonnage."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        warp1 = MockComponent(
            'warp_small', max_hp=100, mass=30,
            abilities={
                'WarpJump': {'max_tonnage': 2000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 200, 'trigger': 'warp_jump'}]
            }
        )
        warp2 = MockComponent(
            'warp_large', max_hp=100, mass=60,
            abilities={
                'WarpJump': {'max_tonnage': 10000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 800, 'trigger': 'warp_jump'}]
            }
        )

        design_data = make_design_data({'OUTER': ['warp_small', 'warp_large']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'warp_small': warp1, 'warp_large': warp2}

            stats = ShipStatsService.calculate_stats(design_data, {})

            # Tonnage = max of drives (10000)
            assert stats['warp_max_tonnage'] == 10000
            # Energy = sum of drives (200 + 800)
            assert stats['warp_resource_costs'].get('energy', 0) == 1000

    def test_one_damaged_warp_drive_reduces_capability(self):
        """If one of two warp drives is damaged, only undamaged contributes."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        warp1 = MockComponent(
            'warp_small', max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 2000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 200, 'trigger': 'warp_jump'}]
            }
        )
        warp2 = MockComponent(
            'warp_large', max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 10000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 800, 'trigger': 'warp_jump'}]
            }
        )

        design_data = make_design_data({'OUTER': ['warp_small', 'warp_large']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'warp_small': warp1, 'warp_large': warp2}

            # Large warp damaged - only small works
            stats = ShipStatsService.calculate_stats(
                design_data, {'warp_large': 99}
            )

            assert stats['warp_max_tonnage'] == 2000
            assert stats['warp_resource_costs'].get('energy', 0) == 200


class TestStatAggregation:
    """Tests for stat aggregation from components."""

    def test_mass_does_not_degrade(self):
        """Mass should be full regardless of damage."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent('heavy_part', mass=500, max_hp=100)
        design_data = make_design_data({'CORE': ['heavy_part']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'heavy_part': comp}

            # Even with damaged component
            stats = ShipStatsService.calculate_stats(
                design_data, {'heavy_part': 1}  # 1% HP
            )

            assert stats['mass'] == 500  # Full mass

    def test_hp_degrades_with_damage(self):
        """HP contribution should degrade with damage."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent('hull', mass=100, max_hp=200, damage_threshold=0.3)
        design_data = make_design_data({'CORE': ['hull']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'hull': comp}

            # Full HP
            stats_full = ShipStatsService.calculate_stats(design_data, {})
            assert stats_full['max_hp'] == 200

            # At 130 current HP out of 200 = 65% HP
            # effectiveness = (0.65 - 0.3) / (1.0 - 0.3) = 0.35/0.7 = 0.5
            # HP contribution = 200 * 0.5 = 100
            stats_half = ShipStatsService.calculate_stats(
                design_data, {'hull': 130}  # 130/200 = 65% HP
            )
            assert stats_half['max_hp'] == 100

    def test_strategic_movement_aggregation(self):
        """Strategic movement should sum across engines, degraded by damage."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        design_data = make_design_data({'OUTER': ['engine']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'engine': engine}

            # Full HP
            stats = ShipStatsService.calculate_stats(design_data, {})
            assert stats['strategic_movement'] == 100

            # Damaged (65% HP = 50% effectiveness)
            stats_damaged = ShipStatsService.calculate_stats(
                design_data, {'engine': 65}
            )
            assert abs(stats_damaged['strategic_movement'] - 50) < 1

    def test_fuel_storage_aggregation(self):
        """Fuel storage should sum, degraded by damage."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        tank = MockComponent(
            'fuel_tank', mass=20, max_hp=50,
            abilities={'FuelStorage': 10000}
        )
        design_data = make_design_data({'OUTER': ['fuel_tank']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'fuel_tank': tank}

            stats = ShipStatsService.calculate_stats(design_data, {})
            assert stats['resource_storage']['fuel'] == 10000

    def test_strategic_fuel_consumption(self):
        """Strategic fuel per hex should sum across engines."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['engine']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'engine': engine}

            stats = ShipStatsService.calculate_stats(design_data, {})
            assert stats['resource_consumption_per_hex']['fuel'] == 100


class TestComponentIdMatching:
    """Tests for component ID matching with damage dict."""

    def test_indexed_component_id(self):
        """Should match indexed component IDs (e.g., 'engine_0')."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent('engine', max_hp=100)

        # Damage dict uses indexed ID
        current_hp = ShipStatsService._get_current_hp('engine', 100, {'engine_0': 50})
        assert current_hp == 50

    def test_base_id_takes_precedence(self):
        """Base ID should match before indexed forms."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent('engine', max_hp=100)

        # Both base and indexed exist - base wins
        current_hp = ShipStatsService._get_current_hp(
            'engine', 100, {'engine': 30, 'engine_0': 50}
        )
        assert current_hp == 30

    def test_no_damage_returns_max_hp(self):
        """No damage entry should return max HP."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        current_hp = ShipStatsService._get_current_hp('engine', 100, {})
        assert current_hp == 100


class TestIntegrationScenarios:
    """Integration tests with realistic ship configurations."""

    def test_escort_with_warp_drive(self):
        """Test escort ship with engine and warp drive."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        bridge = MockComponent(
            'bridge', mass=50, max_hp=200,
            abilities={'CommandAndControl': True}
        )
        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={
                'StrategicMovement': 100,
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        warp = MockComponent(
            'warp_drive', mass=40, max_hp=60,
            abilities={
                'WarpJump': {'max_tonnage': 2000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}]
            }
        )
        tank = MockComponent(
            'fuel_tank', mass=30, max_hp=50,
            abilities={'FuelStorage': 50000}
        )

        design_data = make_design_data({
            'CORE': ['bridge'],
            'OUTER': ['engine', 'warp_drive', 'fuel_tank']
        })

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {
                'bridge': bridge,
                'engine': engine,
                'warp_drive': warp,
                'fuel_tank': tank
            }

            stats = ShipStatsService.calculate_stats(design_data, {})

            assert stats['mass'] == 50 + 80 + 40 + 30  # 200
            assert stats['max_hp'] == 200 + 100 + 60 + 50  # 410
            assert stats['resource_storage']['fuel'] == 50000
            assert stats['strategic_movement'] == 100
            assert stats['resource_consumption_per_hex']['fuel'] == 100
            assert stats['warp_max_tonnage'] == 2000
            assert stats['warp_resource_costs'].get('energy', 0) == 500

    def test_damaged_escort_loses_warp(self):
        """Escort with damaged warp drive loses warp capability."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        warp = MockComponent(
            'warp_drive', mass=40, max_hp=60,
            abilities={
                'WarpJump': {'max_tonnage': 2000},
                'ResourceConsumption': [{'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}]
            }
        )

        design_data = make_design_data({'OUTER': ['engine', 'warp_drive']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'engine': engine, 'warp_drive': warp}

            # Warp drive at 99% HP - disabled
            stats = ShipStatsService.calculate_stats(
                design_data, {'warp_drive': 59}  # Just under 100%
            )

            assert stats['warp_max_tonnage'] == 0
            assert stats['warp_resource_costs'].get('energy', 0) == 0
            # Engine still works (100% HP)
            assert stats['strategic_movement'] == 100


# =============================================================================
# PROJ-08: Data-Driven Resource System Tests
# =============================================================================


class TestGenericDictAccumulators:
    """Tests for generic dict accumulator fields (PROJ-08)."""

    def test_resource_storage_generic_dict_structure(self):
        """resource_storage should be a dict with resource types as keys."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        tank = MockComponent(
            'multi_tank', mass=50, max_hp=100,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'max_amount': 5000},
                    {'resource': 'water', 'max_amount': 1000}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['multi_tank']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'multi_tank': tank}
            stats = ShipStatsService.calculate_stats(design_data, {})

        assert isinstance(stats['resource_storage'], dict)
        assert stats['resource_storage']['fuel'] == 5000
        assert stats['resource_storage']['water'] == 1000

    def test_resource_consumption_per_hex_generic_dict(self):
        """resource_consumption_per_hex should be a dict with resource types."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine = MockComponent(
            'advanced_engine', mass=80, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'},
                    {'resource': 'coolant', 'amount': 10, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['advanced_engine']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'advanced_engine': engine}
            stats = ShipStatsService.calculate_stats(design_data, {})

        assert isinstance(stats['resource_consumption_per_hex'], dict)
        assert stats['resource_consumption_per_hex']['fuel'] == 100
        assert stats['resource_consumption_per_hex']['coolant'] == 10

    def test_resource_consumption_per_turn_generic_dict(self):
        """resource_consumption_per_turn should be a dict with resource types."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        life_support = MockComponent(
            'life_support', mass=30, max_hp=50,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'oxygen', 'amount': 5, 'trigger': 'per_turn'},
                    {'resource': 'food', 'amount': 2, 'trigger': 'per_turn'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['life_support']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'life_support': life_support}
            stats = ShipStatsService.calculate_stats(design_data, {})

        assert isinstance(stats['resource_consumption_per_turn'], dict)
        assert stats['resource_consumption_per_turn']['oxygen'] == 5
        assert stats['resource_consumption_per_turn']['food'] == 2

    def test_warp_resource_costs_generic_dict(self):
        """warp_resource_costs should be a dict with resource types."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        warp_drive = MockComponent(
            'warp_drive', mass=100, max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 5000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'},
                    {'resource': 'antimatter', 'amount': 10, 'trigger': 'warp_jump'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['warp_drive']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'warp_drive': warp_drive}
            stats = ShipStatsService.calculate_stats(design_data, {})

        assert isinstance(stats['warp_resource_costs'], dict)
        assert stats['warp_resource_costs']['energy'] == 500
        assert stats['warp_resource_costs']['antimatter'] == 10

    def test_multiple_custom_resources_accumulate(self):
        """Multiple components should accumulate custom resources in same dict."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        tank1 = MockComponent(
            'fuel_tank', mass=20, max_hp=50,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'max_amount': 3000}
                ]
            }
        )
        tank2 = MockComponent(
            'fuel_tank_2', mass=20, max_hp=50,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'max_amount': 2000}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['fuel_tank', 'fuel_tank_2']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'fuel_tank': tank1, 'fuel_tank_2': tank2}
            stats = ShipStatsService.calculate_stats(design_data, {})

        # Should accumulate: 3000 + 2000 = 5000
        assert stats['resource_storage']['fuel'] == 5000


class TestComponentToggles:
    """Tests for component toggle functionality (PROJ-08)."""

    def test_toggled_off_component_mass_still_counted(self):
        """Toggled off components should still contribute mass."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine = MockComponent(
            'engine', mass=200, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        design_data = make_design_data({'OUTER': ['engine']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'engine': engine}
            stats = ShipStatsService.calculate_stats(
                design_data, {}, component_toggles={'engine': False}
            )

        assert stats['mass'] == 200  # Mass still counted

    def test_toggled_off_component_no_hp_contribution(self):
        """Toggled off components should not contribute HP."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        hull = MockComponent('hull', mass=100, max_hp=500)
        design_data = make_design_data({'CORE': ['hull']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'hull': hull}

            # Enabled
            stats_on = ShipStatsService.calculate_stats(design_data, {})
            assert stats_on['max_hp'] == 500

            # Disabled
            stats_off = ShipStatsService.calculate_stats(
                design_data, {}, component_toggles={'hull': False}
            )
            assert stats_off['max_hp'] == 0

    def test_toggled_off_component_no_strategic_movement(self):
        """Toggled off engines should not contribute strategic movement."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 150}
        )
        design_data = make_design_data({'OUTER': ['engine']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'engine': engine}

            stats_on = ShipStatsService.calculate_stats(design_data, {})
            assert stats_on['strategic_movement'] == 150

            stats_off = ShipStatsService.calculate_stats(
                design_data, {}, component_toggles={'engine': False}
            )
            assert stats_off['strategic_movement'] == 0

    def test_toggled_off_warp_drive_no_warp_capability(self):
        """Toggled off warp drive should contribute no warp capability."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        warp = MockComponent(
            'warp_drive', mass=60, max_hp=100,
            abilities={'WarpJump': {'max_tonnage': 8000, 'energy_cost': 600}}
        )
        design_data = make_design_data({'OUTER': ['warp_drive']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'warp_drive': warp}

            stats_on = ShipStatsService.calculate_stats(design_data, {})
            assert stats_on['warp_max_tonnage'] == 8000

            stats_off = ShipStatsService.calculate_stats(
                design_data, {}, component_toggles={'warp_drive': False}
            )
            assert stats_off['warp_max_tonnage'] == 0

    def test_toggled_off_resource_storage_not_counted(self):
        """Toggled off storage components should not contribute storage capacity."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        tank = MockComponent(
            'fuel_tank', mass=30, max_hp=50,
            abilities={'FuelStorage': 10000}
        )
        design_data = make_design_data({'OUTER': ['fuel_tank']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'fuel_tank': tank}

            stats_on = ShipStatsService.calculate_stats(design_data, {})
            assert stats_on['resource_storage']['fuel'] == 10000

            stats_off = ShipStatsService.calculate_stats(
                design_data, {}, component_toggles={'fuel_tank': False}
            )
            assert stats_off['resource_storage'].get('fuel', 0) == 0

    def test_mixed_enabled_disabled_components(self):
        """Mix of enabled and disabled components should calculate correctly."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine1 = MockComponent(
            'engine_a', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        engine2 = MockComponent(
            'engine_b', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        design_data = make_design_data({'OUTER': ['engine_a', 'engine_b']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'engine_a': engine1, 'engine_b': engine2}

            stats = ShipStatsService.calculate_stats(
                design_data, {},
                component_toggles={'engine_a': True, 'engine_b': False}
            )

        # Mass from both (80 + 80 = 160)
        assert stats['mass'] == 160
        # Movement only from enabled engine
        assert stats['strategic_movement'] == 100
        # HP only from enabled engine
        assert stats['max_hp'] == 100

    def test_missing_toggle_defaults_to_enabled(self):
        """Components not in toggle dict should default to enabled."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        design_data = make_design_data({'OUTER': ['engine']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'engine': engine}

            # Pass empty toggle dict - should default to enabled
            stats = ShipStatsService.calculate_stats(
                design_data, {}, component_toggles={}
            )

        assert stats['strategic_movement'] == 100
        assert stats['max_hp'] == 100

    def test_toggled_off_custom_resource_consumption_not_counted(self):
        """Toggled off components should not contribute resource consumption."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine = MockComponent(
            'advanced_engine', mass=100, max_hp=100,
            abilities={
                'StrategicMovement': 200,
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 200, 'trigger': 'strategic_per_hex'},
                    {'resource': 'coolant', 'amount': 50, 'trigger': 'per_turn'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['advanced_engine']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'advanced_engine': engine}

            stats_on = ShipStatsService.calculate_stats(design_data, {})
            assert stats_on['resource_consumption_per_hex']['fuel'] == 200
            assert stats_on['resource_consumption_per_turn']['coolant'] == 50

            stats_off = ShipStatsService.calculate_stats(
                design_data, {}, component_toggles={'advanced_engine': False}
            )
            # Should be empty dicts or not have the keys
            assert stats_off['resource_consumption_per_hex'].get('fuel', 0) == 0
            assert stats_off['resource_consumption_per_turn'].get('coolant', 0) == 0


class TestTriggerTypes:
    """Tests for ResourceConsumption trigger types (PROJ-08)."""

    def test_trigger_strategic_per_hex_accumulates_correctly(self):
        """strategic_per_hex trigger should accumulate in resource_consumption_per_hex."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine1 = MockComponent(
            'engine_1', mass=50, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 75, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        engine2 = MockComponent(
            'engine_2', mass=50, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 25, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['engine_1', 'engine_2']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'engine_1': engine1, 'engine_2': engine2}
            stats = ShipStatsService.calculate_stats(design_data, {})

        assert stats['resource_consumption_per_hex']['fuel'] == 100

    def test_trigger_per_turn_accumulates_correctly(self):
        """per_turn trigger should accumulate in resource_consumption_per_turn."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        life_support_1 = MockComponent(
            'ls_1', mass=20, max_hp=50,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'oxygen', 'amount': 10, 'trigger': 'per_turn'}
                ]
            }
        )
        life_support_2 = MockComponent(
            'ls_2', mass=20, max_hp=50,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'oxygen', 'amount': 15, 'trigger': 'per_turn'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['ls_1', 'ls_2']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'ls_1': life_support_1, 'ls_2': life_support_2}
            stats = ShipStatsService.calculate_stats(design_data, {})

        assert stats['resource_consumption_per_turn']['oxygen'] == 25

    def test_trigger_warp_jump_accumulates_correctly(self):
        """warp_jump trigger should accumulate in warp_resource_costs."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        warp1 = MockComponent(
            'warp_1', mass=60, max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 5000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 300, 'trigger': 'warp_jump'}
                ]
            }
        )
        warp2 = MockComponent(
            'warp_2', mass=60, max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 3000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 200, 'trigger': 'warp_jump'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['warp_1', 'warp_2']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'warp_1': warp1, 'warp_2': warp2}
            stats = ShipStatsService.calculate_stats(design_data, {})

        # Energy costs accumulate
        assert stats['warp_resource_costs']['energy'] == 500

    def test_different_triggers_dont_cross_buckets(self):
        """Different trigger types should go into separate buckets."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        multi_consumer = MockComponent(
            'multi', mass=100, max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 5000},  # Required for warp_jump trigger to work
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'},
                    {'resource': 'fuel', 'amount': 50, 'trigger': 'per_turn'},
                    {'resource': 'fuel', 'amount': 200, 'trigger': 'warp_jump'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['multi']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'multi': multi_consumer}
            stats = ShipStatsService.calculate_stats(design_data, {})

        # Each should be in its own bucket, not mixed
        assert stats['resource_consumption_per_hex']['fuel'] == 100
        assert stats['resource_consumption_per_turn']['fuel'] == 50
        assert stats['warp_resource_costs']['fuel'] == 200

    def test_trigger_per_turn_degrades_with_damage(self):
        """per_turn consumption should degrade with component damage."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        life_support = MockComponent(
            'life_support', mass=30, max_hp=100, damage_threshold=0.3,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'oxygen', 'amount': 100, 'trigger': 'per_turn'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['life_support']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'life_support': life_support}

            # Full HP
            stats_full = ShipStatsService.calculate_stats(design_data, {})
            assert stats_full['resource_consumption_per_turn']['oxygen'] == 100

            # At 65% HP (50% effectiveness)
            stats_damaged = ShipStatsService.calculate_stats(
                design_data, {'life_support': 65}
            )
            assert abs(stats_damaged['resource_consumption_per_turn']['oxygen'] - 50) < 1

    def test_trigger_warp_jump_requires_full_hp(self):
        """warp_jump consumption requires full HP (warp resource costs are 0 if damaged)."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        # warp_jump trigger now uses warp effectiveness: either 0 (damaged) or 1 (100% HP)
        # If warp drive is damaged, warp_resource_costs should be 0 (no warp possible)
        warp = MockComponent(
            'warp', mass=60, max_hp=100, damage_threshold=0.3,
            abilities={
                'WarpJump': {'max_tonnage': 5000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['warp']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'warp': warp}

            # Full HP - warp works
            stats_full = ShipStatsService.calculate_stats(design_data, {})
            assert stats_full['warp_max_tonnage'] == 5000
            assert stats_full['warp_resource_costs']['energy'] == 500

            # 99% HP - warp drive disabled (0 tonnage)
            # warp_resource_costs should also be 0 (no warp = no cost)
            stats_damaged = ShipStatsService.calculate_stats(
                design_data, {'warp': 99}
            )
            assert stats_damaged['warp_max_tonnage'] == 0
            # When warp is disabled, warp_resource_costs should be empty or 0
            assert stats_damaged['warp_resource_costs'].get('energy', 0) == 0

    def test_trigger_unknown_type_ignored(self):
        """Unknown trigger types should be ignored (no error)."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        comp = MockComponent(
            'strange', mass=50, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'mystery', 'amount': 999, 'trigger': 'unknown_trigger_type'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['strange']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'strange': comp}
            stats = ShipStatsService.calculate_stats(design_data, {})

        # Should not appear in any bucket
        assert stats['resource_consumption_per_hex'].get('mystery', 0) == 0
        assert stats['resource_consumption_per_turn'].get('mystery', 0) == 0
        assert stats['warp_resource_costs'].get('mystery', 0) == 0


class TestCustomResources:
    """Tests for custom resource type support (PROJ-08)."""

    def test_custom_resource_type_in_storage(self):
        """Custom resource types should work in ResourceStorage."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        tank = MockComponent(
            'plasma_tank', mass=40, max_hp=80,
            abilities={
                'ResourceStorage': [
                    {'resource': 'plasma', 'max_amount': 2500}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['plasma_tank']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'plasma_tank': tank}
            stats = ShipStatsService.calculate_stats(design_data, {})

        assert stats['resource_storage']['plasma'] == 2500

    def test_custom_resource_per_hex_consumption(self):
        """Custom resource types should work in per-hex consumption."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        drive = MockComponent(
            'plasma_drive', mass=100, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'plasma', 'amount': 75, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['plasma_drive']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'plasma_drive': drive}
            stats = ShipStatsService.calculate_stats(design_data, {})

        assert stats['resource_consumption_per_hex']['plasma'] == 75

    def test_custom_resource_per_turn_consumption(self):
        """Custom resource types should work in per-turn consumption."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        reactor = MockComponent(
            'fusion_reactor', mass=80, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'deuterium', 'amount': 5, 'trigger': 'per_turn'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['fusion_reactor']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'fusion_reactor': reactor}
            stats = ShipStatsService.calculate_stats(design_data, {})

        assert stats['resource_consumption_per_turn']['deuterium'] == 5

    def test_custom_resource_warp_costs(self):
        """Custom resource types should work in warp costs."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        warp = MockComponent(
            'exotic_warp', mass=100, max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 10000},
                'ResourceConsumption': [
                    {'resource': 'exotic_matter', 'amount': 50, 'trigger': 'warp_jump'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['exotic_warp']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'exotic_warp': warp}
            stats = ShipStatsService.calculate_stats(design_data, {})

        assert stats['warp_resource_costs']['exotic_matter'] == 50

    def test_many_different_custom_resources_coexist(self):
        """Many different custom resources should coexist without conflict."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        multi_tank = MockComponent(
            'multi_resource', mass=100, max_hp=100,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'max_amount': 1000},
                    {'resource': 'water', 'max_amount': 500},
                    {'resource': 'oxygen', 'max_amount': 300},
                    {'resource': 'food', 'max_amount': 200},
                    {'resource': 'spare_parts', 'max_amount': 100}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['multi_resource']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'multi_resource': multi_tank}
            stats = ShipStatsService.calculate_stats(design_data, {})

        storage = stats['resource_storage']
        assert storage['fuel'] == 1000
        assert storage['water'] == 500
        assert storage['oxygen'] == 300
        assert storage['food'] == 200
        assert storage['spare_parts'] == 100


class TestBugDocumentation:
    """Tests documenting edge cases and bugs (PROJ-08)."""

    def test_empty_resource_type_creates_empty_string_key_bug(self):
        """
        BUG DOC: Empty resource type creates '' key in storage dict.

        When a component has an empty string as resource type, it creates
        an empty string key in the resource dict. This is documented behavior.
        """
        from game.strategy.services.ship_stats_service import ShipStatsService

        buggy_tank = MockComponent(
            'buggy_tank', mass=50, max_hp=100,
            abilities={
                'ResourceStorage': [
                    {'resource': '', 'max_amount': 1000}  # Empty resource type
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['buggy_tank']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'buggy_tank': buggy_tank}
            stats = ShipStatsService.calculate_stats(design_data, {})

        # BUG: Empty string creates '' key - this documents current behavior
        # The service does check `if resource_type:` so empty should NOT be added
        assert '' not in stats['resource_storage']

    def test_empty_resource_type_in_consumption_ignored(self):
        """Empty resource type in consumption should be handled (not create '' key)."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        buggy_engine = MockComponent(
            'buggy_engine', mass=80, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': '', 'amount': 100, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['buggy_engine']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'buggy_engine': buggy_engine}
            stats = ShipStatsService.calculate_stats(design_data, {})

        # Empty string key will be created (current behavior - no validation)
        # This test documents the actual behavior and verifies the value is correct
        assert '' in stats['resource_consumption_per_hex'], \
            "Empty string key created for empty resource type (current behavior)"
        assert stats['resource_consumption_per_hex'][''] == 100

    def test_none_resource_type_handled_safely(self):
        """None as resource type should be handled without errors."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        # Component with None resource (missing 'resource' key)
        bad_tank = MockComponent(
            'bad_tank', mass=50, max_hp=100,
            abilities={
                'ResourceStorage': [
                    {'max_amount': 1000}  # Missing 'resource' key
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['bad_tank']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'bad_tank': bad_tank}
            # Should not raise an exception
            stats = ShipStatsService.calculate_stats(design_data, {})

        # Missing resource key defaults to '' via .get('resource', '')
        # The `if resource_type:` check prevents adding to dict
        assert '' not in stats['resource_storage']


class TestIntegrationProj08:
    """Integration tests for PROJ-08 features."""

    def test_damaged_toggled_component_full_mass_partial_stats(self):
        """Damaged then toggled component: full mass from toggle, no stats."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine = MockComponent(
            'engine', mass=100, max_hp=100, damage_threshold=0.3,
            abilities={
                'StrategicMovement': 100,
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['engine']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'engine': engine}

            # Damaged engine at 50% HP (about 29% effectiveness)
            # But then toggled off - should get mass but no stats
            stats = ShipStatsService.calculate_stats(
                design_data,
                {'engine': 50},  # Damaged
                component_toggles={'engine': False}  # Toggled off
            )

        # Mass still counts (toggle off still contributes mass)
        assert stats['mass'] == 100
        # No movement (toggled off)
        assert stats['strategic_movement'] == 0
        # No fuel consumption (toggled off)
        assert stats['resource_consumption_per_hex'].get('fuel', 0) == 0

    def test_all_resource_types_in_one_component(self):
        """Component with storage, per-hex, per-turn, and warp costs."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        super_component = MockComponent(
            'super', mass=200, max_hp=200,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'max_amount': 10000},
                    {'resource': 'energy', 'max_amount': 5000}
                ],
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'},
                    {'resource': 'energy', 'amount': 10, 'trigger': 'per_turn'},
                    {'resource': 'fuel', 'amount': 500, 'trigger': 'warp_jump'}
                ],
                'WarpJump': {'max_tonnage': 8000},
                'StrategicMovement': 150
            }
        )
        design_data = make_design_data({'CORE': ['super']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'super': super_component}
            stats = ShipStatsService.calculate_stats(design_data, {})

        # Verify all fields populated correctly
        assert stats['resource_storage']['fuel'] == 10000
        assert stats['resource_storage']['energy'] == 5000
        assert stats['resource_consumption_per_hex']['fuel'] == 100
        assert stats['resource_consumption_per_turn']['energy'] == 10
        assert stats['warp_resource_costs']['fuel'] == 500
        assert stats['warp_max_tonnage'] == 8000
        assert stats['strategic_movement'] == 150

    def test_fallback_handles_new_generic_fields(self):
        """Fallback to expected_stats should include new generic fields."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        # Design with no layers, just expected_stats (fallback path)
        design_data = {
            'layers': {},
            'expected_stats': {
                'max_hp': 500,
                'mass': 200,
                'resource_storage': {'fuel': 8000, 'special_gas': 100},
                'resource_consumption_per_hex': {'fuel': 80},
                'resource_consumption_per_turn': {'oxygen': 5},
                'warp_resource_costs': {'energy': 400, 'exotic': 10},
                'strategic_movement': 120,
                'warp_max_tonnage': 6000
            }
        }

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {}  # Empty registry forces fallback
            stats = ShipStatsService.calculate_stats(design_data, {})

        # Should use expected_stats values
        assert stats['max_hp'] == 500
        assert stats['mass'] == 200
        assert stats['resource_storage']['fuel'] == 8000
        assert stats['resource_storage']['special_gas'] == 100
        assert stats['resource_consumption_per_hex']['fuel'] == 80
        assert stats['resource_consumption_per_turn']['oxygen'] == 5
        assert stats['warp_resource_costs']['energy'] == 400
        assert stats['warp_resource_costs']['exotic'] == 10
        assert stats['strategic_movement'] == 120
        assert stats['warp_max_tonnage'] == 6000


# =============================================================================
# PROJ-11: has_warp_capability Tests (Phase 3 - Strategy-UI Separation)
# =============================================================================


class TestHasWarpCapability:
    """
    Tests for has_warp_capability function in ShipStatsService.

    PROJ-11 Phase 3: This function was moved from game.ui.screens.fleet_report_filters
    to game.strategy.services.ship_stats_service to eliminate strategy->UI dependency.

    A ship is warp-capable if:
    1. warp_max_tonnage >= ship's mass
    2. warp drive is undamaged (100% HP)
    3. Ship has enough resource storage capacity for at least one warp jump
    """

    def test_ship_without_warp_drive_not_capable(self):
        """Ship without warp drive should not be warp capable."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 0,  # No warp drive
            'warp_resource_costs': {'energy': 0, 'fuel': 0},
            'resource_storage': {'energy': 500, 'fuel': 5000},
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is False

    def test_ship_with_sufficient_warp_drive_capable(self):
        """Ship with warp drive exceeding mass should be warp capable."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,  # Exceeds mass
            'warp_resource_costs': {'energy': 500, 'fuel': 0},
            'resource_storage': {'energy': 1000, 'fuel': 5000},  # Enough for warp
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is True

    def test_ship_with_equal_warp_tonnage_capable(self):
        """Ship with warp tonnage equal to mass should be warp capable."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1000,  # Exactly equal
            'warp_resource_costs': {'energy': 500, 'fuel': 0},
            'resource_storage': {'energy': 1000, 'fuel': 5000},
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is True

    def test_ship_with_insufficient_warp_tonnage_not_capable(self):
        """Ship with warp tonnage less than mass should not be warp capable."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 500,  # Less than mass
            'warp_resource_costs': {'energy': 500, 'fuel': 0},
            'resource_storage': {'energy': 1000, 'fuel': 5000},
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is False

    def test_ship_with_zero_mass_not_capable(self):
        """Ship with zero mass should not be warp capable (edge case)."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 0,  # Zero mass
            'warp_max_tonnage': 1000,
            'warp_resource_costs': {'energy': 500, 'fuel': 0},
            'resource_storage': {'energy': 1000, 'fuel': 5000},
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is False

    def test_insufficient_energy_storage_not_capable(self):
        """Ship with insufficient energy storage for warp should not be capable."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,
            'warp_resource_costs': {'energy': 500, 'fuel': 0},  # Needs 500 energy
            'resource_storage': {'energy': 300, 'fuel': 5000},  # Only has 300 energy capacity
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is False

    def test_insufficient_fuel_storage_not_capable(self):
        """Ship with insufficient fuel storage for warp should not be capable."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,
            'warp_resource_costs': {'energy': 0, 'fuel': 1000},  # Needs 1000 fuel
            'resource_storage': {'energy': 500, 'fuel': 500},  # Only has 500 fuel capacity
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is False

    def test_exactly_sufficient_storage_capable(self):
        """Ship with exactly enough storage for warp should be capable."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,
            'warp_resource_costs': {'energy': 500, 'fuel': 200},
            'resource_storage': {'energy': 500, 'fuel': 200},  # Exactly enough
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is True

    def test_no_warp_cost_no_storage_check(self):
        """If warp has no resource cost, storage check should pass."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,
            'warp_resource_costs': {'energy': 0, 'fuel': 0},  # No resource costs
            'resource_storage': {'energy': 0, 'fuel': 0},  # No storage
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is True

    def test_damaged_warp_drive_returns_zero_tonnage(self):
        """
        When warp drive is damaged, warp_max_tonnage from get_calculated_stats
        should already be 0 (handled by ShipStatsService.calculate_stats).
        """
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 0,  # Damaged warp drive = 0 tonnage
            'warp_resource_costs': {'energy': 0, 'fuel': 0},
            'resource_storage': {'energy': 1000, 'fuel': 5000},
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is False

    def test_multiple_resource_requirements_all_must_be_met(self):
        """If warp costs both energy and fuel, ship must have enough of both."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            'warp_max_tonnage': 1500,
            'warp_resource_costs': {'energy': 500, 'fuel': 1000},
            'resource_storage': {'energy': 600, 'fuel': 500},  # Enough energy but NOT enough fuel
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is False

    def test_missing_stats_default_to_zero(self):
        """Missing stats should default to zero without crashing."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        ship = MagicMock()
        ship.get_calculated_stats.return_value = {
            'mass': 1000,
            # Missing warp_max_tonnage - should default to 0
        }

        result = ShipStatsService.has_warp_capability(ship)
        assert result is False  # No warp capability without warp_max_tonnage


class TestModifierApplication:
    """Tests for PROJ-23: modifier application in ShipStatsService."""

    def test_scaled_battery_energy_capacity(self):
        """Battery with size modifier should have scaled energy capacity.

        PROJ-23 regression test: Ensures modifiers from design are applied.
        """
        from game.strategy.services.ship_stats_service import ShipStatsService
        from game.simulation.components.component_constants import Modifier

        # Create mock battery component
        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'EnergyStorage': 2000}
        )

        # Create size modifier that scales capacity
        size_modifier = Modifier({
            'id': 'simple_size_mount',
            'name': 'Size Mount',
            'effects': [
                {'stat': 'capacity_mult', 'formula': 'param'},
                {'stat': 'mass_mult', 'formula': 'param'},
                {'stat': 'hp_mult', 'formula': 'param'}
            ]
        })

        # Design with size 20 modifier
        design_data = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [{
                    'id': 'battery',
                    'modifiers': [{'id': 'simple_size_mount', 'value': 20.0}]
                }]
            }
        }

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_comp_reg, \
             patch('game.strategy.services.ship_stats_service.get_modifier_registry') as mock_mod_reg:
            mock_comp_reg.return_value = {'battery': battery}
            mock_mod_reg.return_value = {'simple_size_mount': size_modifier}

            stats = ShipStatsService.calculate_stats(design_data, {})

        # Base battery: 2000 energy, size 20 = 40000 energy
        assert stats['resource_storage'].get('energy', 0) == 40000.0

    def test_multiple_small_vs_one_large_battery(self):
        """10 size-1 batteries should equal 1 size-10 battery.

        This validates that modifier scaling is applied consistently.
        """
        from game.strategy.services.ship_stats_service import ShipStatsService
        from game.simulation.components.component_constants import Modifier

        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'EnergyStorage': 2000}
        )

        size_modifier = Modifier({
            'id': 'simple_size_mount',
            'name': 'Size Mount',
            'effects': [
                {'stat': 'capacity_mult', 'formula': 'param'},
                {'stat': 'mass_mult', 'formula': 'param'}
            ]
        })

        # Design with 10 size-1 batteries
        design_small = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [
                    {'id': 'battery', 'modifiers': [{'id': 'simple_size_mount', 'value': 1.0}]}
                    for _ in range(10)
                ]
            }
        }

        # Design with 1 size-10 battery
        design_large = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [{
                    'id': 'battery',
                    'modifiers': [{'id': 'simple_size_mount', 'value': 10.0}]
                }]
            }
        }

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_comp_reg, \
             patch('game.strategy.services.ship_stats_service.get_modifier_registry') as mock_mod_reg:
            mock_comp_reg.return_value = {'battery': battery}
            mock_mod_reg.return_value = {'simple_size_mount': size_modifier}

            stats_small = ShipStatsService.calculate_stats(design_small, {})
            stats_large = ShipStatsService.calculate_stats(design_large, {})

        # 10 × 2000 × 1 = 20000
        # 1 × 2000 × 10 = 20000
        assert stats_small['resource_storage']['energy'] == stats_large['resource_storage']['energy']
        assert stats_small['resource_storage']['energy'] == 20000.0

    def test_warp_capability_with_scaled_battery(self):
        """Ship with scaled battery should have warp capability.

        PROJ-23 regression test: CRU_1 design with 1 large battery should work.
        """
        from game.strategy.services.ship_stats_service import ShipStatsService
        from game.simulation.components.component_constants import Modifier

        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'EnergyStorage': 2000}
        )

        warp_drive = MockComponent(
            'warp_drive',
            mass=250,
            max_hp=250,
            abilities={
                'WarpJump': {'max_tonnage': 16000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 3175, 'trigger': 'warp_jump'}
                ]
            }
        )

        size_modifier = Modifier({
            'id': 'simple_size_mount',
            'name': 'Size Mount',
            'effects': [
                {'stat': 'capacity_mult', 'formula': 'param'},
                {'stat': 'mass_mult', 'formula': 'param'}
            ]
        })

        design_data = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [
                    {
                        'id': 'battery',
                        'modifiers': [{'id': 'simple_size_mount', 'value': 20.0}]
                    },
                    {
                        'id': 'warp_drive',
                        'modifiers': [{'id': 'simple_size_mount', 'value': 1.0}]
                    }
                ]
            }
        }

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_comp_reg, \
             patch('game.strategy.services.ship_stats_service.get_modifier_registry') as mock_mod_reg:
            mock_comp_reg.return_value = {'battery': battery, 'warp_drive': warp_drive}
            mock_mod_reg.return_value = {'simple_size_mount': size_modifier}

            stats = ShipStatsService.calculate_stats(design_data, {})

        # Warp energy cost: 3175
        # Scaled battery: 2000 * 20 = 40000 energy
        # Should have warp capability
        energy_capacity = stats['resource_storage'].get('energy', 0)
        warp_cost = stats['warp_resource_costs'].get('energy', 0)

        assert energy_capacity >= warp_cost, (
            f"Energy capacity {energy_capacity} should be >= warp cost {warp_cost}"
        )
        assert energy_capacity == 40000.0
        assert warp_cost == 3175

    def test_no_modifiers_uses_base_values(self):
        """Component without modifiers should use base ability values."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'EnergyStorage': 2000}
        )

        design_data = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [{'id': 'battery'}]  # No modifiers
            }
        }

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_comp_reg, \
             patch('game.strategy.services.ship_stats_service.get_modifier_registry') as mock_mod_reg:
            mock_comp_reg.return_value = {'battery': battery}
            mock_mod_reg.return_value = {}

            stats = ShipStatsService.calculate_stats(design_data, {})

        # Base battery: 2000 energy, no modifiers
        assert stats['resource_storage'].get('energy', 0) == 2000.0
        assert stats['mass'] == 30.0

    def test_mass_modifier_applied(self):
        """Mass modifier should be applied to component mass."""
        from game.strategy.services.ship_stats_service import ShipStatsService
        from game.simulation.components.component_constants import Modifier

        component = MockComponent(
            'test_comp',
            mass=100,
            max_hp=50,
            abilities={}
        )

        size_modifier = Modifier({
            'id': 'simple_size_mount',
            'name': 'Size Mount',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param'}
            ]
        })

        design_data = {
            'layers': {
                'OUTER': [{
                    'id': 'test_comp',
                    'modifiers': [{'id': 'simple_size_mount', 'value': 5.0}]
                }]
            }
        }

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_comp_reg, \
             patch('game.strategy.services.ship_stats_service.get_modifier_registry') as mock_mod_reg:
            mock_comp_reg.return_value = {'test_comp': component}
            mock_mod_reg.return_value = {'simple_size_mount': size_modifier}

            stats = ShipStatsService.calculate_stats(design_data, {})

        # Base mass: 100, size 5 = 500 mass
        assert stats['mass'] == 500.0
