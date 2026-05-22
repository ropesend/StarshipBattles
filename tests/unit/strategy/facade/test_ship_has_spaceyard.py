"""PROJ-475 Phase 1 Task 1.4 — ``ShipInfo.has_spaceyard`` projection.

``ShipInfo.has_spaceyard`` equals
``FleetCapabilityCalculator.ship_has_spaceyard(ship)`` for the source ship,
computed once at projection time in the facade layer. The fleet-report consumer
bridge is Phase 2 Task 2.6 — this task only adds the DTO field.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.facade.dto.fleet_dto import FleetInfo, ShipInfo


class TestShipInfoHasSpaceyardField:
    def test_field_exists(self) -> None:
        assert "has_spaceyard" in ShipInfo.__dataclass_fields__

    @pytest.fixture
    def make_ship_with_yard(self, fresh_registries):
        def _make(name="Yard Ship"):
            mock = MagicMock()
            mock.name = name
            mock.instance_id = f"inst_{name}"
            mock.design_id = "construction_ship"
            mock.is_combat_capable.return_value = True
            mock.get_hp_percentage.return_value = 1.0
            mock.get_calculated_stats.return_value = {"mass": 5000}
            mock._registries = fresh_registries
            mock.design_data = {
                "name": name,
                "ship_class": "Support",
                "vehicle_type": "Ship",
                "layers": {
                    "core": [{"id": "space_shipyard", "name": "Fleet Space Yard"}]
                },
            }
            return mock
        return _make

    @pytest.fixture
    def make_regular_ship(self, fresh_registries):
        def _make(name="Scout"):
            mock = MagicMock()
            mock.name = name
            mock.instance_id = f"inst_{name}"
            mock.design_id = "scout"
            mock.is_combat_capable.return_value = True
            mock.get_hp_percentage.return_value = 1.0
            mock.get_calculated_stats.return_value = {"mass": 2000}
            mock._registries = fresh_registries
            mock.design_data = {
                "name": name,
                "ship_class": "Scout",
                "vehicle_type": "Ship",
                "layers": {"core": [{"id": "engine"}]},
            }
            return mock
        return _make

    def test_has_spaceyard_true_for_yard_ship(self, make_ship_with_yard) -> None:
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_ship_with_yard())

        info = FleetInfo.from_fleet(fleet)

        assert info.ships[0].has_spaceyard is True

    def test_has_spaceyard_false_for_regular_ship(self, make_regular_ship) -> None:
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_regular_ship())

        info = FleetInfo.from_fleet(fleet)

        assert info.ships[0].has_spaceyard is False

    def test_degrades_to_false_when_calculator_raises(self, monkeypatch) -> None:
        """PROJ-475 Phase 5 (audit Finding 3b): the per-ship projection catches
        ``(ValidationException, AttributeError)`` from the capability calculator
        (atypical fixtures lacking a component registry) and degrades to ``False``
        instead of propagating into projection."""
        from game.core.exceptions import ValidationException
        from game.strategy.data.fleet_capability_calculator import (
            FleetCapabilityCalculator,
        )

        def _boom(ship):
            raise ValidationException("no component registry")

        monkeypatch.setattr(
            FleetCapabilityCalculator, "ship_has_spaceyard", staticmethod(_boom)
        )

        assert FleetInfo._ship_has_spaceyard(MagicMock()) is False
