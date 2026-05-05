"""Tests for builder stat getter helper functions."""
from __future__ import annotations

from types import SimpleNamespace

from game.core.constants import LayerType
from game.simulation.components.abilities.resources import ResourceConsumption
from game.ui.screens.builder import stat_getters


class FakeResource:
    def __init__(self, *, max_value: float, current_value: float, regen_rate: float) -> None:
        self.max_value = max_value
        self.current_value = current_value
        self.regen_rate = regen_rate


class FakeResources:
    def __init__(self, resources: dict[str, FakeResource]) -> None:
        self._resources = resources

    def get_resource(self, name: str) -> FakeResource | None:
        return self._resources.get(name)


class FakeLayer:
    def __init__(self, components: list[object]) -> None:
        self.components = components


class FakeShip:
    def __init__(
        self,
        *,
        resources: FakeResources | None = None,
        components: list[object] | None = None,
        resource_stats: dict[tuple[str, str], float] | None = None,
    ) -> None:
        self.resources = resources
        self.layers = {LayerType.CORE: FakeLayer(components or [])}
        self._resource_stats = resource_stats or {}

    def get_resource_stat(self, resource_name: str, stat_type: str) -> float:
        return self._resource_stats.get((resource_name, stat_type), 0.0)


def test_resource_getters_return_zero_when_resource_registry_missing() -> None:
    ship = SimpleNamespace(resources=None)

    assert stat_getters.get_resource_storage(ship, "fuel") == 0
    assert stat_getters.get_resource_current(ship, "fuel") == 0
    assert stat_getters.get_resource_generation(ship, "fuel") == 0


def test_resource_consumption_prefers_ship_stat_and_falls_back_to_constant_ability() -> None:
    constant_consumption = ResourceConsumption(
        SimpleNamespace(ship=None),
        {"resource": "fuel", "amount": 3.0, "trigger": "constant"},
    )
    activation_consumption = ResourceConsumption(
        SimpleNamespace(ship=None),
        {"resource": "fuel", "amount": 20.0, "trigger": "activation"},
    )
    component = SimpleNamespace(
        ability_instances=[constant_consumption, activation_consumption]
    )

    fallback_ship = FakeShip(components=[component])
    stat_ship = FakeShip(
        components=[component],
        resource_stats={("fuel", "consumption"): 9.0},
    )

    assert stat_getters.get_resource_consumption(stat_ship, "fuel") == 9.0
    assert stat_getters.get_resource_consumption(fallback_ship, "fuel") == 3.0


def test_resource_endurance_and_replenish_handle_empty_rates() -> None:
    ship = FakeShip(
        resources=FakeResources(
            {"fuel": FakeResource(max_value=50, current_value=25, regen_rate=0)}
        )
    )

    assert stat_getters.get_resource_endurance(ship, "fuel") == float("inf")
    assert stat_getters.get_resource_replenish(ship, "fuel") == float("inf")


def test_resource_max_usage_prefers_potential_resource_stat() -> None:
    ship = FakeShip(
        resource_stats={
            ("fuel", "consumption"): 2.0,
            ("potential_fuel", "consumption"): 8.0,
        }
    )

    assert stat_getters.get_resource_max_usage(ship, "fuel") == 8.0


def test_formatters_and_validators_cover_boundary_values() -> None:
    assert stat_getters.fmt_time(float("inf")) == "Infinite"
    assert stat_getters.fmt_time(3660) == "1.0h"
    assert stat_getters.fmt_time(90) == "1.5m"
    assert stat_getters.fmt_time(12.25) == "12.2s"
    assert stat_getters.fmt_score(3) == "+3.0"
    assert stat_getters.fmt_score(-1) == "-1.0"
    assert stat_getters.fmt_targeting(1) == "Single"
    assert stat_getters.fmt_targeting(3) == "Multi (3)"
    assert stat_getters.fmt_yes_no(1) == "Yes"
    assert stat_getters.fmt_yes_no(0) == "No"
    assert stat_getters.fmt_text("") == "None"

    ship = SimpleNamespace(
        mass_limits_ok=True,
        get_ability_total=lambda ability: 5 if ability == "CrewRequired" else 0,
    )
    assert stat_getters.mass_validator(ship, 0)[0] is True
    assert stat_getters.crew_validator(ship, 5)[0] is True
    assert stat_getters.crew_validator(ship, 4)[0] is False
    assert stat_getters.life_support_validator(ship, 5)[0] is True
    assert stat_getters.life_support_validator(ship, 4)[0] is False
