"""Unit tests for simulation ability Protocols and TypeGuard helpers."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from game.simulation.interfaces.ability_protocols import (
    IAbility,
    IBeamWeaponAbility,
    IProjectileWeaponAbility,
    IResourceConsumptionAbility,
    IResourceGenerationAbility,
    IResourceStorageAbility,
    ISeekerWeaponAbility,
    IWarpJumpAbility,
    IWeaponAbility,
    is_ability,
    is_beam_weapon,
    is_projectile_weapon,
    is_resource_consumption,
    is_resource_generation,
    is_resource_storage,
    is_seeker_weapon,
    is_warp_jump,
    is_weapon,
)


class AbilityDouble:
    stack_group: str | None = "primary"
    tags: set[str] = {"test"}

    def get_ui_rows(self) -> list[dict[str, str]]:
        return []

    def get_effect_summary(self) -> list[dict[str, Any]]:
        return []

    def sync_data(self, data: Any) -> None:
        self.last_synced_data = data


class ResourceConsumptionDouble(AbilityDouble):
    trigger = "activation"
    resource_type = "energy"
    amount = 5.0

    def check_available(self, resources: Any = None) -> bool:
        return True


class ResourceStorageDouble(AbilityDouble):
    resource_type = "fuel"
    max_amount = 100.0


class ResourceGenerationDouble(AbilityDouble):
    resource_type = "energy"
    rate = 2.5


class WeaponDouble(AbilityDouble):
    damage = 20.0
    range = 500.0
    reload_time = 1.5
    firing_arc = 90.0

    def get_damage(self, range_to_target: float = 0) -> float:
        return self.damage


class BeamWeaponDouble(WeaponDouble):
    base_accuracy = 0.8
    accuracy_falloff = 0.01


class SeekerWeaponDouble(WeaponDouble):
    projectile_speed = 300.0
    endurance = 8.0
    turn_rate = 45.0
    projectile_damage = 12.0
    projectile_hp = 4.0


class ProjectileWeaponDouble(WeaponDouble):
    projectile_speed = 700.0


class WarpJumpDouble(AbilityDouble):
    max_tonnage = 2000.0
    energy_cost = 25.0


@pytest.mark.parametrize(
    ("protocol", "guard", "ability"),
    [
        (IAbility, is_ability, AbilityDouble()),
        (IResourceConsumptionAbility, is_resource_consumption, ResourceConsumptionDouble()),
        (IResourceStorageAbility, is_resource_storage, ResourceStorageDouble()),
        (IResourceGenerationAbility, is_resource_generation, ResourceGenerationDouble()),
        (IWeaponAbility, is_weapon, WeaponDouble()),
        (IBeamWeaponAbility, is_beam_weapon, BeamWeaponDouble()),
        (ISeekerWeaponAbility, is_seeker_weapon, SeekerWeaponDouble()),
        (IProjectileWeaponAbility, is_projectile_weapon, ProjectileWeaponDouble()),
        (IWarpJumpAbility, is_warp_jump, WarpJumpDouble()),
    ],
)
def test_valid_ability_doubles_satisfy_protocol_and_typeguard(
    protocol: type[Any],
    guard: Any,
    ability: object,
) -> None:
    """Complete structural doubles should satisfy runtime protocols and guards."""
    assert isinstance(ability, protocol)
    assert guard(ability)


@pytest.mark.parametrize(
    ("guard", "valid_obj", "invalid_obj"),
    [
        (is_ability, SimpleNamespace(stack_group=None, tags=set()), SimpleNamespace(tags=set())),
        (
            is_resource_consumption,
            SimpleNamespace(
                trigger="constant",
                resource_type="fuel",
                amount=1.0,
                check_available=lambda resources=None: True,
            ),
            SimpleNamespace(trigger="constant", resource_type="fuel", amount=1.0),
        ),
        (
            is_resource_storage,
            SimpleNamespace(resource_type="fuel", max_amount=10.0),
            SimpleNamespace(resource_type="fuel"),
        ),
        (
            is_resource_generation,
            SimpleNamespace(resource_type="energy", rate=3.0),
            SimpleNamespace(resource_type="energy"),
        ),
        (
            is_weapon,
            SimpleNamespace(damage=1.0, range=100.0, reload_time=2.0),
            SimpleNamespace(damage=1.0, range=100.0),
        ),
        (
            is_beam_weapon,
            SimpleNamespace(
                damage=1.0,
                range=100.0,
                base_accuracy=0.9,
                accuracy_falloff=0.01,
            ),
            SimpleNamespace(damage=1.0, range=100.0, base_accuracy=0.9),
        ),
        (
            is_seeker_weapon,
            SimpleNamespace(damage=1.0, range=100.0, endurance=5.0, turn_rate=30.0),
            SimpleNamespace(damage=1.0, range=100.0, endurance=5.0),
        ),
        (
            is_projectile_weapon,
            SimpleNamespace(damage=1.0, range=100.0, projectile_speed=500.0),
            SimpleNamespace(damage=1.0, range=100.0),
        ),
        (
            is_warp_jump,
            SimpleNamespace(max_tonnage=1000.0, energy_cost=10.0),
            SimpleNamespace(max_tonnage=1000.0),
        ),
    ],
)
def test_typeguards_accept_minimal_duck_shape_and_reject_missing_attrs(
    guard: Any,
    valid_obj: object,
    invalid_obj: object,
) -> None:
    """Each TypeGuard checks the minimal distinguishing attribute set."""
    assert guard(valid_obj)
    assert not guard(invalid_obj)
    assert not guard(None)


def test_projectile_weapon_typeguard_excludes_seekers_by_turn_rate() -> None:
    """Seeker weapons also carry projectile_speed, so turn_rate disambiguates them."""
    seeker_shape = SimpleNamespace(
        damage=1.0,
        range=100.0,
        projectile_speed=500.0,
        endurance=5.0,
        turn_rate=30.0,
    )

    assert is_seeker_weapon(seeker_shape)
    assert not is_projectile_weapon(seeker_shape)
