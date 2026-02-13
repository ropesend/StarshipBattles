"""Tests for build_queue_helpers module - formatting functions for build queue display."""

import pytest
from unittest.mock import MagicMock

from game.ui.screens.build_queue_helpers import (
    RESOURCE_ABBREVS,
    RESOURCE_ABBREVS_SHORT,
    format_empire_resources,
    format_resource_cost,
)


class TestResourceAbbreviations:
    """Tests for resource abbreviation constants."""

    def test_all_resources_have_abbrevs(self):
        """Verify all planet resources have abbreviations."""
        from game.core.constants import PLANET_RESOURCES

        for res in PLANET_RESOURCES:
            assert res in RESOURCE_ABBREVS, f"{res} missing from RESOURCE_ABBREVS"
            assert res in RESOURCE_ABBREVS_SHORT, f"{res} missing from RESOURCE_ABBREVS_SHORT"

    def test_short_abbrevs_are_single_char(self):
        """Verify short abbreviations are single characters."""
        for res, abbr in RESOURCE_ABBREVS_SHORT.items():
            assert len(abbr) == 1, f"{res} has multi-char short abbrev: {abbr}"

    def test_abbrevs_are_unique(self):
        """Verify abbreviations are unique."""
        abbrevs = list(RESOURCE_ABBREVS.values())
        assert len(abbrevs) == len(set(abbrevs)), "Duplicate abbreviations found"

        short_abbrevs = list(RESOURCE_ABBREVS_SHORT.values())
        assert len(short_abbrevs) == len(set(short_abbrevs)), "Duplicate short abbreviations"


class TestFormatEmpireResources:
    """Tests for format_empire_resources function."""

    def test_formats_resources_with_capacity(self):
        """Verify resources with capacity are formatted as current/cap."""
        empire = MagicMock()
        empire.resource_pool = {"Metals": 500.0, "Organics": 200.0}
        empire.max_storage = {"Metals": 1000.0, "Organics": 500.0}

        result = format_empire_resources(empire)

        assert "Met: 500/1000" in result
        assert "Org: 200/500" in result

    def test_formats_resources_without_capacity(self):
        """Verify resources without capacity show only current."""
        empire = MagicMock()
        empire.resource_pool = {"Metals": 100.0, "Organics": 50.0}
        empire.max_storage = {"Metals": 0.0, "Organics": 0.0}

        result = format_empire_resources(empire)

        assert "Met: 100" in result
        assert "Org: 50" in result
        assert "/" not in result  # No capacity shown

    def test_uses_pipe_separator(self):
        """Verify parts are separated by pipe characters."""
        empire = MagicMock()
        empire.resource_pool = {"Metals": 100.0, "Organics": 50.0}
        empire.max_storage = {"Metals": 200.0, "Organics": 100.0}

        result = format_empire_resources(empire)

        assert "  |  " in result

    def test_empty_empire_returns_no_resources(self):
        """Verify empty resource pool returns 'No resources'."""
        empire = MagicMock()
        empire.resource_pool = {}
        empire.max_storage = {}

        result = format_empire_resources(empire)

        assert result == "No resources"

    def test_zero_values_not_shown(self):
        """Verify zero-value resources are not shown."""
        empire = MagicMock()
        empire.resource_pool = {"Metals": 0.0, "Organics": 0.0}
        empire.max_storage = {"Metals": 0.0, "Organics": 0.0}

        result = format_empire_resources(empire)

        assert result == "No resources"

    def test_truncates_to_integers(self):
        """Verify float values are truncated to integers."""
        empire = MagicMock()
        empire.resource_pool = {"Metals": 123.7}
        empire.max_storage = {"Metals": 456.9}

        result = format_empire_resources(empire)

        assert "Met: 123/456" in result

    def test_handles_missing_resource_gracefully(self):
        """Verify missing resources return 0."""
        empire = MagicMock()
        empire.resource_pool = MagicMock()
        empire.resource_pool.get = MagicMock(return_value=0.0)
        empire.max_storage = MagicMock()
        empire.max_storage.get = MagicMock(return_value=0.0)

        result = format_empire_resources(empire)

        assert result == "No resources"


class TestFormatResourceCost:
    """Tests for format_resource_cost function."""

    def test_formats_single_resource(self):
        """Verify single resource cost is formatted."""
        cost = {"Metals": 100}

        result = format_resource_cost(cost)

        assert result == "M:100"

    def test_formats_multiple_resources(self):
        """Verify multiple resource costs are formatted."""
        cost = {"Metals": 100, "Organics": 50, "Vapors": 25}

        result = format_resource_cost(cost)

        assert "M:100" in result
        assert "O:50" in result
        assert "V:25" in result

    def test_skips_zero_cost_resources(self):
        """Verify zero-cost resources are not shown."""
        cost = {"Metals": 100, "Organics": 0, "Vapors": 25}

        result = format_resource_cost(cost)

        assert "M:100" in result
        assert "V:25" in result
        assert "O:" not in result

    def test_empty_cost_returns_empty_string(self):
        """Verify empty cost dict returns empty string."""
        cost = {}

        result = format_resource_cost(cost)

        assert result == ""

    def test_all_zero_costs_returns_empty_string(self):
        """Verify all-zero costs return empty string."""
        cost = {"Metals": 0, "Organics": 0, "Vapors": 0}

        result = format_resource_cost(cost)

        assert result == ""

    def test_truncates_to_integers(self):
        """Verify float values are truncated to integers."""
        cost = {"Metals": 99.9}

        result = format_resource_cost(cost)

        assert result == "M:99"

    def test_uses_space_separator(self):
        """Verify parts are separated by spaces."""
        cost = {"Metals": 100, "Organics": 50}

        result = format_resource_cost(cost)

        assert " " in result
        parts = result.split(" ")
        assert len(parts) == 2

    def test_respects_planet_resources_order(self):
        """Verify resources are ordered according to PLANET_RESOURCES."""
        from game.core.constants import PLANET_RESOURCES

        # Create cost with all resources
        cost = {res: (i + 1) * 10 for i, res in enumerate(PLANET_RESOURCES)}

        result = format_resource_cost(cost)

        # Extract order from result
        parts = result.split(" ")
        result_abbrevs = [p.split(":")[0] for p in parts]

        # Expected order based on PLANET_RESOURCES
        expected_abbrevs = [RESOURCE_ABBREVS_SHORT[res] for res in PLANET_RESOURCES]

        assert result_abbrevs == expected_abbrevs
