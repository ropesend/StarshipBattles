"""
Integration tests for strategic layer abilities.

Tests end-to-end integration of:
- StrategicMovement ability with fleet speed calculation
- WarpJump ability validation and constraints
- Component data loading with new abilities
"""

import pytest
import os
import json
import tempfile
from unittest.mock import MagicMock

from game.simulation.components.abilities.propulsion import StrategicMovement, WarpJump
from game.simulation.components.abilities.base import AbilityLayer, AbilityScope
from game.strategy.services.fleet_mobility_service import FleetMobilityService


class TestStrategicMovementIntegration:
    """Integration tests for StrategicMovement ability with fleet systems."""

    def test_engine_component_has_strategic_movement(self):
        """Verify standard_engine in components.json includes StrategicMovement."""
        components_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'components.json'
        )

        with open(components_path, 'r') as f:
            data = json.load(f)

        components = data.get('components', [])
        standard_engine = next(
            (c for c in components if c['id'] == 'standard_engine'), None
        )

        assert standard_engine is not None, "standard_engine not found in components.json"
        assert 'StrategicMovement' in standard_engine['abilities'], \
            "standard_engine missing StrategicMovement ability"
        assert standard_engine['abilities']['StrategicMovement'] == 100

    def test_fighter_engine_no_strategic_movement(self):
        """Verify fighter engine (mini_engine) does NOT have StrategicMovement."""
        components_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'components.json'
        )

        with open(components_path, 'r') as f:
            data = json.load(f)

        components = data.get('components', [])
        mini_engine = next(
            (c for c in components if c['id'] == 'mini_engine'), None
        )

        assert mini_engine is not None, "mini_engine not found in components.json"
        # Fighters are carrier-based, no independent strategic movement
        assert 'StrategicMovement' not in mini_engine['abilities'], \
            "mini_engine should NOT have StrategicMovement (fighters are carrier-based)"

    def test_fleet_speed_calculation_with_design_data(self):
        """Test fleet speed calculation using design data with StrategicMovement."""
        from game.strategy.services.fleet_mobility_service import K_STRATEGIC

        # Create mock ship instance with design data containing strategic movement
        mock_ship = MagicMock()
        stats = {'mass': 1000, 'strategic_movement': 100}  # 1000 kg ship, 100 movement points
        mock_ship.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        mock_ship.get_calculated_stats.return_value = stats
        mock_ship.is_combat_capable.return_value = True

        # Calculate speed: floor((100 * 25) / 1000) = floor(2500/1000) = floor(2.5) = 2
        speed = FleetMobilityService.calculate_ship_speed(mock_ship)
        expected = int((100 * K_STRATEGIC) / 1000)
        assert speed == expected

    def test_fleet_speed_with_multiple_ships(self):
        """Test fleet uses slowest ship speed."""
        # Fast ship
        fast_stats = {'mass': 100, 'strategic_movement': 200}
        fast_ship = MagicMock()
        fast_ship.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': fast_stats
        }
        fast_ship.get_calculated_stats.return_value = fast_stats
        fast_ship.is_combat_capable.return_value = True

        # Slow ship (heavy cruiser)
        slow_stats = {'mass': 5000, 'strategic_movement': 100}
        slow_ship = MagicMock()
        slow_ship.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': slow_stats
        }
        slow_ship.get_calculated_stats.return_value = slow_stats
        slow_ship.is_combat_capable.return_value = True

        # Create mock fleet
        mock_fleet = MagicMock()
        mock_fleet.get_ship_instances.return_value = [fast_ship, slow_ship]

        fleet_speed = FleetMobilityService.calculate_fleet_speed(mock_fleet)

        # Fast ship: floor((200 * 25) / 100) = floor(50) = clamped to 10
        # Slow ship: floor((100 * 25) / 5000) = floor(0.5) = 0
        # Fleet speed = min(10, 0) = 0
        assert fleet_speed == 0.0

    def test_planetary_complex_has_zero_speed(self):
        """Planetary complexes should have 0 strategic movement (stationary)."""
        mock_ship = MagicMock()
        mock_ship.design_data = {
            'vehicle_type': 'Planetary Complex',
            'expected_stats': {
                'mass': 10000,
                'strategic_movement': 100  # Even with movement points
            }
        }
        mock_ship.is_combat_capable.return_value = True

        speed = FleetMobilityService.calculate_ship_speed(mock_ship)
        assert speed == 0


class TestWarpJumpIntegration:
    """Integration tests for WarpJump ability with component data."""

    def test_warp_drive_components_exist(self):
        """Verify warp drive components exist in components.json."""
        components_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'components.json'
        )

        with open(components_path, 'r') as f:
            data = json.load(f)

        components = data.get('components', [])
        warp_drives = [c for c in components if 'WarpJump' in c.get('abilities', {})]

        assert len(warp_drives) >= 2, "Should have at least 2 warp drive tiers"

        # Verify warp drives have expected properties
        for wd in warp_drives:
            assert wd['allowed_vehicle_types'] == ['Ship'], \
                f"Warp drive {wd['id']} should only be for Ships"
            assert isinstance(wd['abilities']['WarpJump'], (int, float, dict)), \
                f"WarpJump ability should have max_tonnage value"

    def test_warp_drive_tiered_tonnage(self):
        """Verify warp drives have increasing tonnage limits."""
        components_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'components.json'
        )

        with open(components_path, 'r') as f:
            data = json.load(f)

        components = data.get('components', [])
        warp_drives = [c for c in components if 'WarpJump' in c.get('abilities', {})]

        # Sort by tonnage to verify tiering
        def get_tonnage(c):
            wj = c['abilities']['WarpJump']
            if isinstance(wj, dict):
                return wj.get('max_tonnage', 0)
            return wj

        tonnages = sorted([get_tonnage(wd) for wd in warp_drives])

        # Verify increasing tonnage limits
        for i in range(1, len(tonnages)):
            assert tonnages[i] > tonnages[i-1], \
                f"Warp drives should have increasing tonnage: {tonnages}"

    def test_warp_jump_ability_from_component_data(self):
        """Test creating WarpJump ability from component data."""
        mock_component = MagicMock()
        mock_component.stats = {}

        # Test simple data format (just tonnage value)
        ability = WarpJump(mock_component, 5000)
        assert ability.max_tonnage == 5000
        assert ability.layer == AbilityLayer.STRATEGIC
        assert ability.scope == AbilityScope.SELF

        # Test dict format
        ability2 = WarpJump(mock_component, {'max_tonnage': 10000})
        assert ability2.max_tonnage == 10000

    def test_warp_capability_check(self):
        """Test can_jump() method with various ship masses."""
        mock_component = MagicMock()
        mock_component.stats = {}

        # Standard warp drive: 5000 kg limit
        ability = WarpJump(mock_component, 5000)

        # Under limit
        assert ability.can_jump(4000) is True
        assert ability.can_jump(4999) is True

        # At limit
        assert ability.can_jump(5000) is True

        # Over limit
        assert ability.can_jump(5001) is False
        assert ability.can_jump(10000) is False


class TestAbilityLayerIntegration:
    """Integration tests for ability layer filtering."""

    def test_strategic_movement_layer_filtering(self):
        """StrategicMovement should only apply to STRATEGIC layer."""
        mock_component = MagicMock()
        mock_component.stats = {}

        ability = StrategicMovement(mock_component, 100)

        assert ability.applies_to_layer(AbilityLayer.STRATEGIC) is True
        assert ability.applies_to_layer(AbilityLayer.COMBAT) is False
        assert ability.applies_to_layer(AbilityLayer.BOTH) is True

    def test_warp_jump_layer_filtering(self):
        """WarpJump should only apply to STRATEGIC layer."""
        mock_component = MagicMock()
        mock_component.stats = {}

        ability = WarpJump(mock_component, 5000)

        assert ability.applies_to_layer(AbilityLayer.STRATEGIC) is True
        assert ability.applies_to_layer(AbilityLayer.COMBAT) is False
        assert ability.applies_to_layer(AbilityLayer.BOTH) is True


class TestAbilityScopeIntegration:
    """Integration tests for ability scope configuration."""

    def test_strategic_movement_scope_from_json(self):
        """Test StrategicMovement scope can be configured via JSON."""
        mock_component = MagicMock()
        mock_component.stats = {}

        # Default scope (SELF)
        ability_self = StrategicMovement(mock_component, 100)
        assert ability_self.scope == AbilityScope.SELF

        # Allied sector scope (for tugs)
        ability_sector = StrategicMovement(mock_component, {
            'value': 50,
            'scope': 'allied_sector'
        })
        assert ability_sector.scope == AbilityScope.ALLIED_SECTOR

        # Allied system scope (for orbital complexes)
        ability_system = StrategicMovement(mock_component, {
            'value': 25,
            'scope': 'allied_system'
        })
        assert ability_system.scope == AbilityScope.ALLIED_SYSTEM

    def test_warp_jump_rejects_non_self_scope(self):
        """WarpJump should reject any scope other than SELF."""
        mock_component = MagicMock()
        mock_component.stats = {}

        # Attempting to use system scope should fail
        with pytest.raises(ValueError) as exc_info:
            WarpJump(mock_component, {'max_tonnage': 5000, 'scope': 'system'})

        assert 'does not support scope' in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
