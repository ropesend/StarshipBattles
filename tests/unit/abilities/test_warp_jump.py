"""
Tests for WarpJump ability.

TDD Phase 3, Step 3.1: Tests for the WarpJump ability class.
"""

import pytest
from unittest.mock import MagicMock


class TestWarpJumpAbility:
    """Tests for the WarpJump ability class."""

    @pytest.fixture
    def mock_component(self):
        mock = MagicMock()
        mock.ship = MagicMock()
        mock.stats = {}
        return mock

    def test_warp_jump_layer_is_strategic(self):
        """WarpJump should have STRATEGIC layer."""
        from game.simulation.components.abilities.propulsion import WarpJump
        from game.simulation.components.abilities.base import AbilityLayer

        assert WarpJump.layer == AbilityLayer.STRATEGIC

    def test_warp_jump_allowed_scopes_only_self(self):
        """WarpJump should only allow SELF scope (affects only the ship it's on)."""
        from game.simulation.components.abilities.propulsion import WarpJump
        from game.simulation.components.abilities.base import AbilityScope

        assert WarpJump.allowed_scopes == [AbilityScope.SELF]
        assert WarpJump.default_scope == AbilityScope.SELF

    def test_warp_jump_max_tonnage_from_simple_data(self, mock_component):
        """WarpJump should read max_tonnage from primitive data."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(mock_component, 5000)

        assert ab.max_tonnage == 5000

    def test_warp_jump_max_tonnage_from_dict(self, mock_component):
        """WarpJump should read max_tonnage from dict data."""
        from game.simulation.components.abilities.propulsion import WarpJump

        data = {'max_tonnage': 10000}
        ab = WarpJump(mock_component, data)

        assert ab.max_tonnage == 10000

    def test_warp_jump_can_jump_under_limit(self, mock_component):
        """can_jump() should return True when ship mass <= max_tonnage."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(mock_component, {'max_tonnage': 5000})

        assert ab.can_jump(4000) is True  # Under limit
        assert ab.can_jump(5000) is True  # At limit

    def test_warp_jump_cannot_jump_over_limit(self, mock_component):
        """can_jump() should return False when ship mass > max_tonnage."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(mock_component, {'max_tonnage': 5000})

        assert ab.can_jump(5001) is False  # Over limit
        assert ab.can_jump(10000) is False  # Way over

    def test_warp_jump_ui_rows(self, mock_component):
        """WarpJump should provide UI rows showing capability and limits."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(mock_component, {'max_tonnage': 5000})
        rows = ab.get_ui_rows()

        assert len(rows) >= 1

        # Should indicate warp capability
        labels = [r['label'] for r in rows]
        assert any('Warp' in label for label in labels)

    def test_warp_jump_get_primary_value(self, mock_component):
        """WarpJump.get_primary_value() should return max_tonnage."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(mock_component, 7500)

        assert ab.get_primary_value() == 7500

    def test_warp_jump_does_not_apply_to_combat(self, mock_component):
        """WarpJump should NOT apply to COMBAT layer."""
        from game.simulation.components.abilities.propulsion import WarpJump
        from game.simulation.components.abilities.base import AbilityLayer

        ab = WarpJump(mock_component, 5000)

        assert ab.applies_to_layer(AbilityLayer.COMBAT) is False
        assert ab.applies_to_layer(AbilityLayer.STRATEGIC) is True

    def test_warp_jump_rejects_system_scope(self, mock_component):
        """WarpJump should reject non-SELF scopes."""
        from game.simulation.components.abilities.propulsion import WarpJump

        data = {'max_tonnage': 5000, 'scope': 'system'}

        with pytest.raises(ValueError):
            WarpJump(mock_component, data)


class TestWarpJumpEnergyCost:
    """Tests for WarpJump energy cost functionality."""

    @pytest.fixture
    def mock_component(self):
        mock = MagicMock()
        mock.ship = MagicMock()
        mock.stats = {}
        return mock

    def test_energy_cost_default_zero(self, mock_component):
        """WarpJump should default energy_cost to 0 when not specified."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(mock_component, 5000)  # Primitive shortcut
        assert ab.energy_cost == 0.0

    def test_energy_cost_from_dict(self, mock_component):
        """WarpJump should read energy_cost from dict data."""
        from game.simulation.components.abilities.propulsion import WarpJump

        data = {'max_tonnage': 5000, 'energy_cost': 100}
        ab = WarpJump(mock_component, data)

        assert ab.energy_cost == 100.0

    def test_energy_cost_default_when_omitted_from_dict(self, mock_component):
        """WarpJump should default energy_cost to 0 when dict omits it."""
        from game.simulation.components.abilities.propulsion import WarpJump

        data = {'max_tonnage': 5000}  # energy_cost omitted
        ab = WarpJump(mock_component, data)

        assert ab.energy_cost == 0.0

    def test_ui_rows_show_energy_cost_when_positive(self, mock_component):
        """WarpJump should show energy cost in UI when energy_cost > 0."""
        from game.simulation.components.abilities.propulsion import WarpJump

        data = {'max_tonnage': 5000, 'energy_cost': 150}
        ab = WarpJump(mock_component, data)
        rows = ab.get_ui_rows()

        labels = [r['label'] for r in rows]
        assert 'Warp Energy' in labels

    def test_ui_rows_hide_energy_cost_when_zero(self, mock_component):
        """WarpJump should NOT show energy cost in UI when energy_cost is 0."""
        from game.simulation.components.abilities.propulsion import WarpJump

        data = {'max_tonnage': 5000, 'energy_cost': 0}
        ab = WarpJump(mock_component, data)
        rows = ab.get_ui_rows()

        labels = [r['label'] for r in rows]
        assert 'Warp Energy' not in labels

    def test_can_jump_boundary_exact_mass(self, mock_component):
        """can_jump() boundary test: exact mass equals max_tonnage."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(mock_component, {'max_tonnage': 5000})

        assert ab.can_jump(5000.0) is True
        assert ab.can_jump(5000.001) is False

    def test_can_jump_zero_mass(self, mock_component):
        """can_jump() edge case: zero mass always succeeds."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(mock_component, {'max_tonnage': 5000})
        assert ab.can_jump(0) is True

    def test_can_jump_zero_tonnage_drive(self, mock_component):
        """can_jump() edge case: zero max_tonnage drive only allows zero mass."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(mock_component, {'max_tonnage': 0})
        assert ab.can_jump(0) is True
        assert ab.can_jump(1) is False


class TestWarpJumpRegistration:
    """Tests for WarpJump registration in ability system."""

    def test_warp_jump_in_registry(self):
        """WarpJump should be registered in ABILITY_REGISTRY."""
        from game.simulation.components.abilities import ABILITY_REGISTRY

        assert 'WarpJump' in ABILITY_REGISTRY

    def test_create_warp_jump_via_factory(self):
        """Should be able to create WarpJump via create_ability()."""
        from game.simulation.components.abilities import create_ability
        from game.simulation.components.abilities.propulsion import WarpJump

        mock_component = MagicMock()
        ab = create_ability('WarpJump', mock_component, {'max_tonnage': 8000})

        assert isinstance(ab, WarpJump)
        assert ab.max_tonnage == 8000
