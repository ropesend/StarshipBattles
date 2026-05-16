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
    def __init__(
        self,
        components: list[object],
        *,
        max_hp_pool: float = 0,
    ) -> None:
        self.components = components
        self.max_hp_pool = max_hp_pool


class FakeComponent:
    def __init__(self, abilities: dict[str, object] | None = None) -> None:
        self._abilities = abilities or {}
        self.ability_instances = list(self._abilities.values())

    def has_ability(self, ability_name: str) -> bool:
        return ability_name in self._abilities

    def get_ability(self, ability_name: str) -> object | None:
        return self._abilities.get(ability_name)


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

    def get_all_components(self) -> list[object]:
        return [
            component
            for layer in self.layers.values()
            for component in layer.components
        ]


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
        get_ability_total=lambda ability: 5 if ability == "RequiresMaintenance" else 0,
    )
    assert stat_getters.mass_validator(ship, 0)[0] is True
    assert stat_getters.crew_validator(ship, 5)[0] is True
    assert stat_getters.crew_validator(ship, 4)[0] is False
    assert stat_getters.life_support_validator(ship, 5)[0] is True
    assert stat_getters.life_support_validator(ship, 4)[0] is False


def test_basic_stat_getters_read_ship_fields_and_ability_totals() -> None:
    ship = SimpleNamespace(
        mass=123.5,
        max_targets=3,
        total_maneuver_points=7,
        fuel_consumption=1.5,
        ammo_consumption=2.5,
        energy_consumption=3.5,
        get_ability_total=lambda ability: {
            "RequiresMaintenance": 9,
            "CrewCapacity": -4,
            "LifeSupportCapacity": 6,
        }.get(ability, 0),
        layers={},
    )

    assert stat_getters.get_mass_display(ship) == 123.5
    assert stat_getters.get_total_crew_requirement(ship) == 9
    assert stat_getters.get_crew_capacity(ship) == 0
    assert stat_getters.get_life_support(ship) == 6
    assert stat_getters.get_max_targets(ship) == 3
    assert stat_getters.get_maneuver_points(ship) == 7
    assert stat_getters.get_fuel_consumption(ship) == 1.5
    assert stat_getters.get_ammo_consumption(ship) == 2.5
    assert stat_getters.get_energy_consumption(ship) == 3.5
    assert stat_getters.get_armor_hp(ship) == 0

    ship.layers[LayerType.ARMOR] = FakeLayer([], max_hp_pool=42)
    assert stat_getters.get_armor_hp(ship) == 42


def test_strategic_speed_handles_zero_values_normal_math_and_cap() -> None:
    normal = SimpleNamespace(mass=100, total_strategic_movement=16)
    capped = SimpleNamespace(mass=100, total_strategic_movement=1000)
    no_mass = SimpleNamespace(mass=0, total_strategic_movement=100)
    no_movement = SimpleNamespace(mass=100, total_strategic_movement=0)

    assert stat_getters.get_strategic_speed(normal) == 4
    assert stat_getters.get_strategic_speed(capped) == 10
    assert stat_getters.get_strategic_speed(no_mass) == 0
    assert stat_getters.get_strategic_speed(no_movement) == 0


def test_resource_getters_return_registry_values_and_positive_time_math() -> None:
    ship = FakeShip(
        resources=FakeResources(
            {"fuel": FakeResource(max_value=120, current_value=40, regen_rate=6)}
        ),
        resource_stats={("fuel", "consumption"): 3.0},
    )

    assert stat_getters.get_resource_storage(ship, "fuel") == 120
    assert stat_getters.get_resource_current(ship, "fuel") == 40
    assert stat_getters.get_resource_generation(ship, "fuel") == 6
    assert stat_getters.get_resource_endurance(ship, "fuel") == 40
    assert stat_getters.get_resource_replenish(ship, "fuel") == 20


def test_resource_max_usage_falls_back_to_direct_consumption_and_zero() -> None:
    ship = FakeShip(resource_stats={("energy", "consumption"): 5.0})

    assert stat_getters.get_resource_max_usage(ship, "energy") == 5.0
    assert stat_getters.get_resource_max_usage(ship, "organics") == 0


def test_weapon_and_combat_summary_getters() -> None:
    weapon = FakeComponent({"WeaponAbility": object()})
    utility = FakeComponent()
    ship = FakeShip(components=[weapon, utility])
    ship.cached_summary = {"dps": 12.5}
    ship.ammo_endurance = 50
    ship.energy_endurance = 30
    ship.max_weapon_range = 900

    assert stat_getters.get_weapon_count(ship) == 1
    assert stat_getters.get_total_dps(ship) == 12.5
    assert stat_getters.get_dps_duration(ship) == 30
    assert stat_getters.get_max_range(ship) == 900

    ship.cached_summary = None
    assert stat_getters.get_total_dps(ship) == 0


def test_dps_duration_finite_when_ammo_endurance_is_finite() -> None:
    """QA Observation 4 regression.

    A fighter armed only with mini_railgun (now consuming ammo per shot) should
    surface a finite DPS-duration in the Builder. Before the data fix,
    ``ammo_endurance`` defaulted to ``float('inf')`` because no
    ResourceConsumption ability was bound, so the Builder displayed "Infinite".
    """
    weapon = FakeComponent({"WeaponAbility": object()})
    ship = FakeShip(components=[weapon])
    ship.cached_summary = {"dps": 5.0}
    ship.ammo_endurance = 400.0  # 200 ammo / 0.5 ammo-per-sec = 400s
    ship.energy_endurance = float("inf")
    ship.max_weapon_range = 1000

    duration = stat_getters.get_dps_duration(ship)
    assert duration != float("inf")
    assert duration == 400.0


def test_warp_and_strategic_range_getters_cover_resource_edges() -> None:
    per_hex = ResourceConsumption(
        SimpleNamespace(ship=None),
        {"resource": "fuel", "amount": 4.0, "trigger": "strategic_per_hex"},
    )
    ship = FakeShip(
        resources=FakeResources(
            {
                "fuel": FakeResource(max_value=100, current_value=100, regen_rate=0),
                "energy": FakeResource(max_value=45, current_value=45, regen_rate=0),
            }
        ),
        components=[SimpleNamespace(ability_instances=[per_hex])],
    )
    ship.warp_max_tonnage = 200
    ship.warp_energy_cost = 15
    ship.warp_resource_costs = {"fuel": 20, "energy": 15}

    assert stat_getters.get_warp_capable(ship) == 1.0
    assert stat_getters.get_warp_tonnage(ship) == 200
    assert stat_getters.get_warp_cost(ship) == 15
    assert stat_getters.get_warp_jumps(ship) == 3
    assert stat_getters.get_fuel_per_hex(ship) == 4.0
    assert stat_getters.get_hex_range(ship) == 25

    no_cost_ship = FakeShip(
        resources=FakeResources(
            {"fuel": FakeResource(max_value=100, current_value=100, regen_rate=0)}
        )
    )
    no_cost_ship.warp_max_tonnage = 0
    no_cost_ship.warp_resource_costs = {}
    assert stat_getters.get_warp_capable(no_cost_ship) == 0.0
    assert stat_getters.get_warp_jumps(no_cost_ship) == 0
    assert stat_getters.get_hex_range(no_cost_ship) == float("inf")

    no_fuel_ship = FakeShip(resources=FakeResources({}))
    assert stat_getters.get_hex_range(no_fuel_ship) == 0


def test_cargo_colony_superweapon_and_command_getters() -> None:
    colonizer = FakeComponent(
        {
            "ColonizePlanet": SimpleNamespace(planet_type="Arid"),
            "DestroyPlanet": object(),
        }
    )
    command = FakeComponent({"CommandAndControl": object()})
    ship = FakeShip(components=[command, colonizer])
    ship.cargo_storage = {"generic": 80, "passengers": 12}
    ship.pod_storage_mass = 25
    ship.repair_rate = 1.5

    assert stat_getters.get_cargo_capacity(ship) == 80
    assert stat_getters.get_cargo_capacity(ship, "ore") == 0
    assert stat_getters.get_passenger_capacity(ship) == 12
    assert stat_getters.get_pod_storage(ship) == 25
    assert stat_getters.get_colony_types(ship) == "Arid"
    assert stat_getters.get_superweapon_summary(ship) == "Planet Imploder x1"
    assert stat_getters.has_superweapons(ship) is True
    assert stat_getters.get_repair_rate(ship) == 1.5
    assert stat_getters.get_command_status(ship) == 1.0

    empty_ship = FakeShip()
    assert stat_getters.get_colony_types(empty_ship) == "None"
    assert stat_getters.get_superweapon_summary(empty_ship) == "None"
    assert stat_getters.has_superweapons(empty_ship) is False
    assert stat_getters.get_command_status(empty_ship) == 0.0


def test_remaining_formatters_and_function_registries() -> None:
    assert stat_getters.fmt_time(0) == "0.0s"
    assert stat_getters.fmt_time(1_000_000) == "Infinite"
    assert stat_getters.fmt_multiply(1.23456) == "1.2346"
    assert stat_getters.fmt_decimal(1.25) == "1.2"
    assert stat_getters.fmt_int(12.9) == "12"
    assert stat_getters.fmt_int(float("inf")) == "\u221e"
    assert stat_getters.fmt_text("Scout") == "Scout"
    assert stat_getters.GETTERS["get_mass_display"] is stat_getters.get_mass_display
    assert stat_getters.FORMATTERS["fmt_int"] is stat_getters.fmt_int
    assert stat_getters.VALIDATORS["mass_validator"] is stat_getters.mass_validator
    assert stat_getters.UNITS["mass_unit"](
        SimpleNamespace(max_mass_budget=100),
        50,
    ) == "/ 100"
