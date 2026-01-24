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
