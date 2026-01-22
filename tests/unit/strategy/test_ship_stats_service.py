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
        assert stats['max_fuel'] == 0
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
            abilities={'WarpJump': {'max_tonnage': 5000, 'energy_cost': 500}}
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
            abilities={'WarpJump': {'max_tonnage': 5000, 'energy_cost': 500}}
        )

        design_data = make_design_data({'OUTER': ['warp_drive']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'warp_drive': warp_comp}

            # Undamaged - has warp capability
            stats_ok = ShipStatsService.calculate_stats(design_data, {})
            assert stats_ok['warp_max_tonnage'] == 5000
            assert stats_ok['warp_energy_cost'] == 500

            # Damaged - no warp capability
            stats_damaged = ShipStatsService.calculate_stats(
                design_data, {'warp_drive': 99}
            )
            assert stats_damaged['warp_max_tonnage'] == 0
            assert stats_damaged['warp_energy_cost'] == 0

    def test_multiple_warp_drives_largest_tonnage(self):
        """With multiple warp drives, use largest tonnage."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        warp1 = MockComponent(
            'warp_small', max_hp=100, mass=30,
            abilities={'WarpJump': {'max_tonnage': 2000, 'energy_cost': 200}}
        )
        warp2 = MockComponent(
            'warp_large', max_hp=100, mass=60,
            abilities={'WarpJump': {'max_tonnage': 10000, 'energy_cost': 800}}
        )

        design_data = make_design_data({'OUTER': ['warp_small', 'warp_large']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'warp_small': warp1, 'warp_large': warp2}

            stats = ShipStatsService.calculate_stats(design_data, {})

            # Tonnage = max of drives (10000)
            assert stats['warp_max_tonnage'] == 10000
            # Energy = sum of drives (200 + 800)
            assert stats['warp_energy_cost'] == 1000

    def test_one_damaged_warp_drive_reduces_capability(self):
        """If one of two warp drives is damaged, only undamaged contributes."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        warp1 = MockComponent(
            'warp_small', max_hp=100,
            abilities={'WarpJump': {'max_tonnage': 2000, 'energy_cost': 200}}
        )
        warp2 = MockComponent(
            'warp_large', max_hp=100,
            abilities={'WarpJump': {'max_tonnage': 10000, 'energy_cost': 800}}
        )

        design_data = make_design_data({'OUTER': ['warp_small', 'warp_large']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'warp_small': warp1, 'warp_large': warp2}

            # Large warp damaged - only small works
            stats = ShipStatsService.calculate_stats(
                design_data, {'warp_large': 99}
            )

            assert stats['warp_max_tonnage'] == 2000
            assert stats['warp_energy_cost'] == 200


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
            assert stats['max_fuel'] == 10000

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
            assert stats['strategic_fuel_per_hex'] == 100


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
            abilities={'WarpJump': {'max_tonnage': 2000, 'energy_cost': 500}}
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
            assert stats['max_fuel'] == 50000
            assert stats['strategic_movement'] == 100
            assert stats['strategic_fuel_per_hex'] == 100
            assert stats['warp_max_tonnage'] == 2000
            assert stats['warp_energy_cost'] == 500

    def test_damaged_escort_loses_warp(self):
        """Escort with damaged warp drive loses warp capability."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        warp = MockComponent(
            'warp_drive', mass=40, max_hp=60,
            abilities={'WarpJump': {'max_tonnage': 2000, 'energy_cost': 500}}
        )

        design_data = make_design_data({'OUTER': ['engine', 'warp_drive']})

        with patch('game.strategy.services.ship_stats_service.get_component_registry') as mock_reg:
            mock_reg.return_value = {'engine': engine, 'warp_drive': warp}

            # Warp drive at 99% HP - disabled
            stats = ShipStatsService.calculate_stats(
                design_data, {'warp_drive': 59}  # Just under 100%
            )

            assert stats['warp_max_tonnage'] == 0
            assert stats['warp_energy_cost'] == 0
            # Engine still works (100% HP)
            assert stats['strategic_movement'] == 100
