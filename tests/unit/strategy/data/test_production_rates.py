"""Tests for production_rates.json loading and validation."""

import json
from pathlib import Path

import pytest

from game.core.json_utils import load_json


class TestProductionRatesJson:
    """Tests for the production_rates.json data file."""

    @pytest.fixture
    def production_rates(self) -> dict:
        """Load production_rates.json."""
        return load_json("data/production_rates.json")

    def test_load_production_rates_succeeds(self, production_rates: dict) -> None:
        """Verify production_rates.json loads without error."""
        assert production_rates is not None
        assert isinstance(production_rates, dict)

    def test_all_three_yard_types_present(self, production_rates: dict) -> None:
        """Verify all three yard types are defined."""
        expected_yards = {"planetary_yard", "space_shipyard", "fleet_space_yard"}
        assert set(production_rates.keys()) == expected_yards

    def test_planetary_yard_has_all_resources(self, production_rates: dict) -> None:
        """Verify planetary_yard has all 5 resource types."""
        expected_resources = {"metals", "organics", "radioactives", "vapors", "exotics"}
        assert set(production_rates["planetary_yard"].keys()) == expected_resources

    def test_space_shipyard_has_all_resources(self, production_rates: dict) -> None:
        """Verify space_shipyard has all 5 resource types."""
        expected_resources = {"metals", "organics", "radioactives", "vapors", "exotics"}
        assert set(production_rates["space_shipyard"].keys()) == expected_resources

    def test_fleet_space_yard_has_all_resources(self, production_rates: dict) -> None:
        """Verify fleet_space_yard has all 5 resource types."""
        expected_resources = {"metals", "organics", "radioactives", "vapors", "exotics"}
        assert set(production_rates["fleet_space_yard"].keys()) == expected_resources

    def test_planetary_yard_default_rate_is_2000(self, production_rates: dict) -> None:
        """Verify planetary_yard has 2000/turn for all resources."""
        for resource, rate in production_rates["planetary_yard"].items():
            assert rate == 2000, f"Expected 2000 for {resource}, got {rate}"

    def test_space_shipyard_default_rate_is_3000(self, production_rates: dict) -> None:
        """Verify space_shipyard has 3000/turn for all resources."""
        for resource, rate in production_rates["space_shipyard"].items():
            assert rate == 3000, f"Expected 3000 for {resource}, got {rate}"

    def test_fleet_space_yard_default_rate_is_3000(self, production_rates: dict) -> None:
        """Verify fleet_space_yard has 3000/turn for all resources."""
        for resource, rate in production_rates["fleet_space_yard"].items():
            assert rate == 3000, f"Expected 3000 for {resource}, got {rate}"

    def test_all_rates_are_positive_numbers(self, production_rates: dict) -> None:
        """Verify all rates are positive numeric values."""
        for yard_type, resources in production_rates.items():
            for resource, rate in resources.items():
                assert isinstance(rate, (int, float)), f"{yard_type}.{resource} is not a number"
                assert rate > 0, f"{yard_type}.{resource} is not positive"
