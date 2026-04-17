"""Tests for create_ability silently skipping unevaluated formula data.

Background: components are loaded into the registry without a ship reference,
so formula-driven ability data (e.g. `=ship_class_mass`) cannot be evaluated
to numbers. Previously create_ability tried to instantiate these abilities
anyway, caught the resulting ValueError, and emitted a WARNING log line for
every formula-bearing ability at every startup. The warnings were misleading
because the abilities ARE later instantiated correctly when components attach
to a ship and formulas resolve.

Fix: detect formula strings in the data and skip silently. The ability will
be instantiated lazily when the component is recalculated with proper context.
"""
import logging
from unittest.mock import MagicMock

import pytest

from game.simulation.components.abilities import create_ability


@pytest.fixture
def warning_capture(caplog):
    """Capture WARNING-level logs from the abilities module."""
    caplog.set_level(logging.WARNING, logger='game.simulation.components.abilities')
    return caplog


@pytest.fixture
def mock_component():
    component = MagicMock()
    component.ship = None
    component.stats = {}
    component.ability_stats = {}
    return component


class TestCreateAbilitySkipsFormulaData:
    """create_ability must NOT log a warning when data contains an unevaluated formula."""

    def test_dict_with_formula_value_skipped_silently(self, warning_capture, mock_component):
        """`{'max_tonnage': '=ship_class_mass'}` should return None with no warning."""
        result = create_ability('WarpJump', mock_component, {'max_tonnage': '=ship_class_mass'})
        assert result is None
        assert not any(
            'Failed to create ability' in r.message for r in warning_capture.records
        ), f"Unexpected warning: {[r.message for r in warning_capture.records]}"

    def test_string_formula_does_not_warn(self, warning_capture, mock_component):
        """`'=8 * ship_class_mass'` (raw formula string as data) must not log a warning.

        Whether the ability constructs (with a default value) or returns None
        is an ability-specific detail; what matters is that no misleading
        'Failed to create ability' warning is emitted.
        """
        create_ability('EmissiveArmor', mock_component, '=8 * (ship_class_mass / 1000)**(1/3)')
        assert not any(
            'Failed to create ability' in r.message for r in warning_capture.records
        ), f"Unexpected warning: {[r.message for r in warning_capture.records]}"

    def test_nested_list_with_formula_value_does_not_warn(self, warning_capture, mock_component):
        """ResourceConsumption with formula amount must not warn (skip or succeed silently)."""
        data = [{'resource': 'energy', 'amount': '=5 * (ship_class_mass ** (2/3))', 'trigger': 'warp_jump'}]
        create_ability('ResourceConsumption', mock_component, data)
        assert not any(
            'Failed to create ability' in r.message for r in warning_capture.records
        ), f"Unexpected warning: {[r.message for r in warning_capture.records]}"

    def test_non_formula_data_still_creates_ability(self, mock_component):
        """Numeric data should still construct successfully — fix must not break the happy path."""
        result = create_ability('WarpJump', mock_component, {'max_tonnage': 5000})
        assert result is not None
        assert result.max_tonnage == 5000.0

    def test_real_failures_still_warn(self, warning_capture, mock_component):
        """Genuine errors (not formula-string-related) must still log a warning so
        actual misconfiguration is visible."""
        # QualityImprovement does not allow scope='system' — that's a real config error
        result = create_ability(
            'QualityImprovement', mock_component,
            {'resource_type': 'metals', 'improvement_rate': 0.5, 'scope': 'system'}
        )
        assert result is None
        assert any(
            'Failed to create ability' in r.message for r in warning_capture.records
        ), "Genuine config errors must still emit a warning"


class TestRegistryLoadEmitsNoFormulaWarnings:
    """End-to-end: loading components.json must not emit Failed-to-create warnings
    for formula-bearing abilities (WarpJump, EmissiveArmor, ShieldRegeneratingArmor)."""

    def test_load_components_data_emits_no_formula_failure_warnings(self, caplog):
        """Loading the production components.json must not produce 'Failed to create
        ability' warnings for the three formula-bearing abilities."""
        from game.core.registry import GameRegistries
        from game.simulation.components.component_loader import (
            load_components_data, load_modifiers_data
        )
        from game.simulation.entities.ship_loader import load_vehicle_classes_data

        caplog.set_level(logging.WARNING, logger='game.simulation.components.abilities')

        minimal = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
        load_components_data(registries=minimal)

        offending = [
            r.message for r in caplog.records
            if "Failed to create ability 'WarpJump'" in r.message
            or "Failed to create ability 'EmissiveArmor'" in r.message
            or "Failed to create ability 'ShieldRegeneratingArmor'" in r.message
        ]
        assert not offending, (
            f"Registry load emitted warnings for formula-bearing abilities: {offending}"
        )
