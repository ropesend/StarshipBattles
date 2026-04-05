"""
Tests for superweapon stabilizer check deduplication.

PROJ-239 Task 3.1: CQ-003 - The three stabilizer check methods should
be unified into a single parameterized _is_stabilized method.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestUnifiedStabilizerCheck:
    """Test that _is_stabilized works for all stabilizer types."""

    def _make_processor(self):
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor
        return SuperweaponOrderProcessor()

    def test_planet_stabilized_by_geologic_stabilizer(self):
        """GeologicStabilizer at planet scope protects the planet."""
        proc = self._make_processor()
        planet = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()

        with patch('game.strategy.services.strategic_ability_scanner.find_abilities_in_scope') as mock_scan:
            mock_scan.return_value = [{"ability": "GeologicStabilizer"}]
            result = proc._is_stabilized(
                "GeologicStabilizer", ["planet", "sector", "system"],
                planet, galaxy, [empire]
            )
        assert result is True

    def test_not_stabilized_when_no_abilities_found(self):
        """Returns False when no stabilizer abilities found at any scope."""
        proc = self._make_processor()
        planet = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()

        with patch('game.strategy.services.strategic_ability_scanner.find_abilities_in_scope') as mock_scan:
            mock_scan.return_value = []
            result = proc._is_stabilized(
                "GeologicStabilizer", ["planet", "sector", "system"],
                planet, galaxy, [empire]
            )
        assert result is False

    def test_stellar_stabilizer_with_ref_planet_lookup(self):
        """StellarStabilizer uses reference planet for system-scope scanning."""
        proc = self._make_processor()
        fleet_location = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()
        ref_planet = MagicMock()

        with patch.object(proc, '_get_reference_planet', return_value=ref_planet):
            with patch('game.strategy.services.strategic_ability_scanner.find_abilities_in_scope') as mock_scan:
                mock_scan.return_value = [{"ability": "StellarStabilizer"}]
                result = proc._is_system_stellar_stabilized(fleet_location, galaxy, [empire])
        assert result is True

    def test_warp_stabilizer_returns_false_when_no_ref_planet(self):
        """Returns False when no reference planet found in system."""
        proc = self._make_processor()
        fleet_location = MagicMock()
        galaxy = MagicMock()

        with patch.object(proc, '_get_reference_planet', return_value=None):
            result = proc._is_system_warp_stabilized(fleet_location, galaxy, [])
        assert result is False

    def test_has_unified_is_stabilized_method(self):
        """SuperweaponOrderProcessor has a unified _is_stabilized method."""
        proc = self._make_processor()
        assert hasattr(proc, '_is_stabilized'), (
            "Expected _is_stabilized unified method on SuperweaponOrderProcessor"
        )
