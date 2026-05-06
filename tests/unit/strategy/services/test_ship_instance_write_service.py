"""Unit tests for ShipInstanceWriteService (PROJ-370 Phase 5)."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.protocols import IShipInstanceMutator
from game.strategy.services.ship_instance_write_service import (
    ShipInstanceWriteService,
)


@pytest.fixture
def service() -> ShipInstanceWriteService:
    return ShipInstanceWriteService()


@pytest.fixture
def instance() -> MagicMock:
    """Fake ShipInstance — only the attributes the mutator touches."""
    inst = MagicMock()
    inst.is_alive = True
    inst.is_derelict = False
    inst.current_hp = None
    inst.components = {}
    inst.cargo_contents = {}
    inst.consumable_levels = {}
    inst.carried_items = []
    inst.component_toggles = {}
    inst.activation_states = {}
    inst.battles_survived = 0
    inst.experience = 0.0
    inst.kills = 0
    inst._cargo_manager = None
    inst._consumable_manager = None
    inst.invalidate_stats_cache = MagicMock()
    return inst


def test_ship_instance_write_service_satisfies_protocol(
    service: ShipInstanceWriteService,
) -> None:
    assert isinstance(service, IShipInstanceMutator)


def test_set_is_alive(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    service.set_is_alive(instance, False)
    assert instance.is_alive is False


def test_set_is_derelict(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    service.set_is_derelict(instance, True)
    assert instance.is_derelict is True


def test_set_current_hp_value(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    service.set_current_hp(instance, 42.0)
    assert instance.current_hp == 42.0


def test_set_current_hp_none(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    instance.current_hp = 50
    service.set_current_hp(instance, None)
    assert instance.current_hp is None


def test_replace_components_invalidates_stats_cache(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    new_components = {"a": object(), "b": object()}
    service.replace_components(instance, new_components)
    assert instance.components == new_components
    instance.invalidate_stats_cache.assert_called_once()


def test_increment_battles_survived(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    service.increment_battles_survived(instance)
    service.increment_battles_survived(instance)
    assert instance.battles_survived == 2


def test_add_carried_item(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    item = {"id": 1}
    service.add_carried_item(instance, item)
    assert instance.carried_items == [item]


def test_pop_carried_item(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    a, b = {"id": 1}, {"id": 2}
    instance.carried_items.extend([a, b])
    popped = service.pop_carried_item(instance, 0)
    assert popped is a
    assert instance.carried_items == [b]


def test_set_cargo_amount_direct_write_when_no_manager(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    instance._cargo_manager = None
    service.set_cargo_amount(instance, "metals", 50.0)
    assert instance.cargo_contents["metals"] == 50.0


def test_add_experience(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    service.add_experience(instance, 5.0)
    service.add_experience(instance, 7.5)
    assert instance.experience == 12.5


def test_add_kill(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    service.add_kill(instance)
    service.add_kill(instance)
    assert instance.kills == 2
