"""Tests for dynamic builder stat-row generators."""
from __future__ import annotations

from types import SimpleNamespace

from game.core.constants import LayerType
from game.simulation.components.abilities.resources import ResourceConsumption
from game.ui.screens.builder import stat_rows_dynamic


class FakeResource:
    def __init__(
        self,
        *,
        max_value: float = 0,
        current_value: float = 0,
        regen_rate: float = 0,
    ) -> None:
        self.max_value = max_value
        self.current_value = current_value
        self.regen_rate = regen_rate


class FakeResources:
    def __init__(self, resources: dict[str, FakeResource]) -> None:
        self._resources = resources

    def get_resource_names(self) -> list[str]:
        return list(self._resources)

    def get_resource(self, name: str) -> FakeResource | None:
        return self._resources.get(name)


class FakeLayer:
    def __init__(self, components: list[FakeComponent]) -> None:
        self.components = components


class FakeComponent:
    def __init__(self, ability_map: dict[str, object]) -> None:
        self._ability_map = ability_map
        self.ability_instances = list(ability_map.values())

    def has_ability(self, ability_name: str) -> bool:
        return ability_name in self._ability_map

    def get_ability(self, ability_name: str) -> object | None:
        return self._ability_map.get(ability_name)


class FakeShip:
    def __init__(
        self,
        *,
        resources: FakeResources | None = None,
        components: list[FakeComponent] | None = None,
        resource_stats: dict[tuple[str, str], float] | None = None,
    ) -> None:
        self.resources = resources or FakeResources({})
        self.layers = {LayerType.CORE: FakeLayer(components or [])}
        self.cargo_storage: dict[str, float] = {}
        self.pod_storage_mass = 0
        self._resource_stats = resource_stats or {}

    def get_resource_stat(self, resource_name: str, stat_type: str) -> float:
        return self._resource_stats.get((resource_name, stat_type), 0.0)

    def get_all_components(self) -> list[FakeComponent]:
        return [
            component
            for layer in self.layers.values()
            for component in layer.components
        ]


class ResourceHarvesterAbility:
    def __init__(self, resource_type: str, base_harvest_rate: float) -> None:
        self.resource_type = resource_type
        self.base_harvest_rate = base_harvest_rate


class LocalStorageAbility:
    def __init__(self, resource_type: str, capacity: float) -> None:
        self.resource_type = resource_type
        self.capacity = capacity


class PlanetaryYardAbility:
    pass


class SpaceShipyardAbility:
    def __init__(self) -> None:
        self.construction_speed_bonus = 1.5
        self.max_ship_mass = 5000
        self.production_rates = {"ship": 20}


class StagingYardAbility:
    def __init__(self, capacity_mass: float) -> None:
        self.capacity_mass = capacity_mass


class AtmosphereModifier:
    def __init__(self, modification_rate: float) -> None:
        self.modification_rate = modification_rate


class WaterModifier:
    def __init__(self, modification_rate: float) -> None:
        self.modification_rate = modification_rate


class PlanetaryShield:
    def __init__(self) -> None:
        self.energy_drain_rate = 4.0
        self.activation_time = 12
        self.scope = "system"


def _row_ids(rows: list[object]) -> list[str]:
    return [row.key for row in rows]


def test_logistics_rows_return_empty_for_missing_resource_interface() -> None:
    ship = SimpleNamespace(resources=None, get_resource_stat=lambda *_args: 0)

    assert stat_rows_dynamic.get_logistics_rows(ship) == []


def test_logistics_rows_include_capacity_generation_constant_max_and_endurance() -> None:
    consumption = ResourceConsumption(
        SimpleNamespace(ship=None),
        {"resource": "fuel", "amount": 5.0, "trigger": "constant"},
    )
    ship = FakeShip(
        resources=FakeResources({"fuel": FakeResource(max_value=100, regen_rate=2)}),
        components=[FakeComponent({"ResourceConsumption": consumption})],
        resource_stats={("potential_fuel", "consumption"): 20.0},
    )

    rows = stat_rows_dynamic.get_logistics_rows(ship)

    assert _row_ids(rows) == [
        "max_fuel",
        "fuel_gen",
        "fuel_constant",
        "fuel_max_usage",
        "fuel_endurance",
        "fuel_max_endurance",
    ]
    values = {row.key: row.get_value(ship) for row in rows}
    assert values["fuel_constant"] == 5.0
    assert values["fuel_max_usage"] == 20.0
    assert values["fuel_max_endurance"] == 5.0


def test_logistics_rows_add_recharge_for_generation_only_resource() -> None:
    ship = FakeShip(
        resources=FakeResources({"energy": FakeResource(max_value=120, regen_rate=6)}),
    )

    rows = stat_rows_dynamic.get_logistics_rows(ship)

    assert _row_ids(rows) == ["max_energy", "energy_gen", "energy_recharge"]
    assert rows[-1].get_value(ship) == 20.0


def test_strategic_rows_collect_harvest_storage_yards_and_staging() -> None:
    ship = FakeShip(
        components=[
            FakeComponent(
                {
                    "ResourceHarvester": ResourceHarvesterAbility("metals", 3.5),
                    "LocalStorage": LocalStorageAbility("organics", 80),
                    "PlanetaryYard": PlanetaryYardAbility(),
                    "SpaceShipyard": SpaceShipyardAbility(),
                    "StagingYard": StagingYardAbility(250),
                }
            ),
            FakeComponent(
                {
                    "ResourceHarvester": ResourceHarvesterAbility("metals", 1.5),
                    "LocalStorage": LocalStorageAbility("organics", 20),
                }
            ),
        ]
    )

    rows = stat_rows_dynamic.get_strategic_rows(ship)

    assert _row_ids(rows) == [
        "harvest_metals",
        "storage_organics",
        "planetary_yard",
        "space_shipyard",
        "shipyard_max_mass",
        "staging_capacity",
    ]
    assert rows[0].get_value(ship) == 5.0
    assert rows[1].get_value(ship) == 100.0
    assert rows[2].format_value(rows[2].get_value(ship)) == "Yes"


def test_strategic_ability_helpers_tolerate_missing_layers() -> None:
    ship = SimpleNamespace(layers=None)

    assert stat_rows_dynamic.has_strategic_abilities(ship) is False


def test_planetary_engineering_rows_use_later_nonzero_ability() -> None:
    ship = FakeShip(
        components=[
            FakeComponent({"AtmosphereModifier": AtmosphereModifier(0)}),
            FakeComponent({"AtmosphereModifier": AtmosphereModifier(2.5)}),
            FakeComponent({"WaterModifier": WaterModifier(0.25)}),
        ]
    )

    rows = stat_rows_dynamic.get_planetary_engineering_rows(ship)

    assert _row_ids(rows) == [
        "planetary_atmospheremodifier",
        "planetary_watermodifier",
    ]
    assert rows[0].get_value(ship) == 2.5
    assert rows[1].get_value(ship) == 0.25


def test_planetary_defense_rows_include_scope_drain_and_activation() -> None:
    ship = FakeShip(components=[FakeComponent({"PlanetaryShield": PlanetaryShield()})])

    rows = stat_rows_dynamic.get_planetary_defense_rows(ship)

    assert _row_ids(rows) == [
        "defense_planetaryshield",
        "defense_planetaryshield_time",
    ]
    assert rows[0].label == "Planet Shield (system)"
    assert rows[0].get_value(ship) == 4.0
    assert rows[1].get_value(ship) == 12
