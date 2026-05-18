"""
PROJ-436 Phase 1: tests for the `Container` ability parser and the
parity helpers that compile the three legacy storage abilities
(`ResourceStorage`, `CargoStorage`, `VehicleBay`) into the equivalent
`(capacity_mass, ContainerPolicy)` view.

No legacy ability is removed in Phase 1. The new parser sits alongside
the old ones; runtime behaviour is unchanged. The parity helpers exist
so Phase 2+ runtime code can read a uniform shape regardless of which
ability the component author used.
"""
from __future__ import annotations

import pytest

from game.simulation.components.abilities import (
    ABILITY_REGISTRY,
    CargoStorage,
    ResourceStorage,
    VehicleBayAbility,
    create_ability,
)
from game.simulation.components.abilities.container import (
    ContainerAbility,
    container_view_from_cargo_storage,
    container_view_from_resource_storage,
    container_view_from_vehicle_bay,
)
from game.strategy.data.containable import ContainableKind
from game.strategy.data.container import ContainerPolicy


# ---------------------------------------------------------------------------
# Container ability registration
# ---------------------------------------------------------------------------


class TestRegistration:
    def test_container_registered(self):
        assert "Container" in ABILITY_REGISTRY
        assert ABILITY_REGISTRY["Container"] is ContainerAbility

    def test_create_ability_returns_container(self):
        data = {
            "capacity_mass": 100.0,
            "allowed_kinds": ["RESOURCE"],
            "allowed_type_ids": ["metals"],
        }
        ability = create_ability("Container", component=None, data=data)
        assert isinstance(ability, ContainerAbility)


# ---------------------------------------------------------------------------
# Container ability parsing
# ---------------------------------------------------------------------------


class TestParsing:
    def test_full_dict_shape(self):
        data = {
            "capacity_mass": 250.0,
            "allowed_kinds": ["ITEM"],
            "allowed_type_ids": ["fighter", "satellite"],
        }
        ability = ContainerAbility(component=None, data=data)
        assert ability.capacity_mass == pytest.approx(250.0)
        assert ability.policy.allowed_kinds == frozenset({ContainableKind.ITEM})
        assert ability.policy.allowed_type_ids == frozenset({"fighter", "satellite"})

    def test_kinds_case_insensitive(self):
        data = {
            "capacity_mass": 50.0,
            "allowed_kinds": ["resource", "ITEM", "Population"],
            "allowed_type_ids": None,
        }
        ability = ContainerAbility(component=None, data=data)
        assert ability.policy.allowed_kinds == frozenset({
            ContainableKind.RESOURCE,
            ContainableKind.ITEM,
            ContainableKind.POPULATION,
        })

    def test_null_allowed_type_ids_means_any(self):
        data = {
            "capacity_mass": 100.0,
            "allowed_kinds": ["RESOURCE"],
            "allowed_type_ids": None,
        }
        ability = ContainerAbility(component=None, data=data)
        assert ability.policy.allowed_type_ids is None

    def test_missing_allowed_type_ids_means_any(self):
        data = {
            "capacity_mass": 100.0,
            "allowed_kinds": ["RESOURCE"],
        }
        ability = ContainerAbility(component=None, data=data)
        assert ability.policy.allowed_type_ids is None

    def test_missing_capacity_mass_is_zero(self):
        data = {
            "allowed_kinds": ["RESOURCE"],
        }
        ability = ContainerAbility(component=None, data=data)
        assert ability.capacity_mass == 0.0

    def test_unknown_kind_rejected(self):
        data = {
            "capacity_mass": 100.0,
            "allowed_kinds": ["NONSENSE"],
        }
        with pytest.raises(ValueError):
            ContainerAbility(component=None, data=data)


# ---------------------------------------------------------------------------
# Parity: ResourceStorage -> Container
# ---------------------------------------------------------------------------


class TestResourceStorageParity:
    def test_fuel_storage_compiles(self):
        # fuel_tank example: 50000 units of fuel.
        ability = ResourceStorage(component=None, data={"resource": "fuel", "amount": 50000.0})
        capacity_mass, policy = container_view_from_resource_storage(ability)
        # 50000 * 0.0001 mass/unit = 5.0 tons.
        assert capacity_mass == pytest.approx(5.0)
        assert policy.allowed_kinds == frozenset({ContainableKind.RESOURCE})
        assert policy.allowed_type_ids == frozenset({"fuel"})

    def test_metals_storage_compiles(self):
        ability = ResourceStorage(component=None, data={"resource": "metals", "amount": 10000.0})
        capacity_mass, policy = container_view_from_resource_storage(ability)
        assert capacity_mass == pytest.approx(100.0)  # 10000 * 0.01
        assert policy.allowed_type_ids == frozenset({"metals"})

    def test_energy_storage_compiles(self):
        # Per user directive: 1 unit of energy = 1 ton.
        ability = ResourceStorage(component=None, data={"resource": "energy", "amount": 250.0})
        capacity_mass, policy = container_view_from_resource_storage(ability)
        assert capacity_mass == pytest.approx(250.0)


# ---------------------------------------------------------------------------
# Parity: CargoStorage -> Container
# ---------------------------------------------------------------------------


class TestCargoStorageParity:
    def test_passenger_quarters_compiles_to_population(self):
        # passenger_quarters: cargo_type="passengers", capacity=5000.
        ability = CargoStorage(component=None, data={"cargo_type": "passengers", "capacity": 5000.0})
        capacity_mass, policy = container_view_from_cargo_storage(ability)
        # 5000 passengers * 0.1 tons each = 500 tons of mass.
        assert capacity_mass == pytest.approx(500.0)
        assert policy.allowed_kinds == frozenset({ContainableKind.POPULATION})
        assert policy.allowed_type_ids is None  # any species

    def test_generic_cargo_compiles_to_any(self):
        ability = CargoStorage(component=None, data={"cargo_type": "generic", "capacity": 100.0})
        capacity_mass, policy = container_view_from_cargo_storage(ability)
        assert capacity_mass == pytest.approx(100.0)
        assert policy.allowed_kinds == frozenset({
            ContainableKind.RESOURCE,
            ContainableKind.ITEM,
            ContainableKind.POPULATION,
        })
        assert policy.allowed_type_ids is None


# ---------------------------------------------------------------------------
# Parity: VehicleBay -> Container
# ---------------------------------------------------------------------------


class TestVehicleBayParity:
    def test_fighter_only_bay_compiles(self):
        ability = VehicleBayAbility(component=None, data={"capacity_mass": 250, "allowed_types": ["fighter"]})
        capacity_mass, policy = container_view_from_vehicle_bay(ability)
        assert capacity_mass == pytest.approx(250.0)
        assert policy.allowed_kinds == frozenset({ContainableKind.ITEM})
        assert policy.allowed_type_ids == frozenset({"fighter"})

    def test_mixed_vehicle_bay_compiles(self):
        ability = VehicleBayAbility(
            component=None,
            data={"capacity_mass": 250, "allowed_types": ["mine", "fighter", "satellite"]},
        )
        capacity_mass, policy = container_view_from_vehicle_bay(ability)
        assert policy.allowed_type_ids == frozenset({"mine", "fighter", "satellite"})

    def test_default_vehicle_bay_compiles(self):
        # Scalar input — VehicleBayAbility defaults allowed_types to all three.
        ability = VehicleBayAbility(component=None, data=200)
        capacity_mass, policy = container_view_from_vehicle_bay(ability)
        assert capacity_mass == pytest.approx(200.0)
        assert policy.allowed_type_ids == frozenset({"mine", "fighter", "satellite"})


# ---------------------------------------------------------------------------
# ContainerAbility round-trip with policy
# ---------------------------------------------------------------------------


class TestPolicyConstruction:
    def test_policy_attribute_is_container_policy(self):
        data = {
            "capacity_mass": 50.0,
            "allowed_kinds": ["RESOURCE"],
            "allowed_type_ids": ["fuel"],
        }
        ability = ContainerAbility(component=None, data=data)
        assert isinstance(ability.policy, ContainerPolicy)

    def test_get_primary_value_returns_capacity_mass(self):
        data = {"capacity_mass": 123.4, "allowed_kinds": ["RESOURCE"]}
        ability = ContainerAbility(component=None, data=data)
        assert ability.get_primary_value() == pytest.approx(123.4)
