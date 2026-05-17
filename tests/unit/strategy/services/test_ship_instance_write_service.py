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
    # PROJ-425 Phase 4: entity attributes are ``_cargo_mgr`` /
    # ``_resource_mgr`` (write service was previously querying the
    # never-existing ``_cargo_manager`` / ``_consumable_manager``).
    inst._cargo_mgr = None
    inst._resource_mgr = None
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


# PROJ-431 Phase 1f: ``add_carried_item`` / ``pop_carried_item`` removed
# from :class:`ShipInstanceWriteService`. Carried-inventory mutation now
# goes through the typed :class:`BayInventory` surface
# (``ShipCargoManager.load_vehicle`` / ``unload_vehicle``) or
# :meth:`ShipInstance.set_bay_inventory` directly; the old service
# methods had no production callers.


def test_set_cargo_amount_direct_write_when_no_manager(
    service: ShipInstanceWriteService, instance: MagicMock
) -> None:
    instance._cargo_mgr = None
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


# ---------------------------------------------------------------------------
# PROJ-425 Phase 4: write service owns toggle + repair (cache invalidation
# centralized here, not split across entity + service).
# ---------------------------------------------------------------------------


class TestSetComponentEnabledWrite:
    """`set_component_enabled(...)` toggles + invalidates the stats cache."""

    def test_enable_writes_toggle_and_invalidates_cache(
        self, service: ShipInstanceWriteService, instance: MagicMock,
    ) -> None:
        service.set_component_enabled(instance, "engine", True)
        assert instance.component_toggles["engine"] is True
        instance.invalidate_stats_cache.assert_called_once()

    def test_disable_writes_toggle_and_invalidates_cache(
        self, service: ShipInstanceWriteService, instance: MagicMock,
    ) -> None:
        service.set_component_enabled(instance, "engine", False)
        assert instance.component_toggles["engine"] is False
        instance.invalidate_stats_cache.assert_called_once()


class TestRepairWrite:
    """`repair(...)` returns delta + invalidates the stats cache."""

    def test_repair_returns_zero_when_already_full(
        self, service: ShipInstanceWriteService, instance: MagicMock,
    ) -> None:
        instance.current_hp = None  # full health
        result = service.repair(instance, 50)
        assert result == 0
        # No invalidation needed when nothing changed
        instance.invalidate_stats_cache.assert_not_called()

    def test_repair_partial(
        self, service: ShipInstanceWriteService, instance: MagicMock,
    ) -> None:
        instance.current_hp = 30
        instance.get_calculated_stats = MagicMock(return_value={"max_hp": 100})
        instance.components = {}
        result = service.repair(instance, 20)
        assert instance.current_hp == 50
        assert result == 20
        instance.invalidate_stats_cache.assert_called_once()

    def test_repair_full_restores_components_and_clears_hp(
        self, service: ShipInstanceWriteService, instance: MagicMock,
    ) -> None:
        instance.current_hp = 80
        instance.get_calculated_stats = MagicMock(return_value={"max_hp": 100})
        # Two damaged components
        cs_a = MagicMock(current_hp=20, max_hp=40)
        cs_b = MagicMock(current_hp=10, max_hp=10)
        instance.components = {"a#0": cs_a, "b#0": cs_b}

        result = service.repair(instance, 100)

        # Hp set to None (full health)
        assert instance.current_hp is None
        # Components restored
        assert cs_a.current_hp == 40
        assert cs_b.current_hp == 10
        # Returned delta uses max_hp - old_hp when fully repaired
        assert result == 20
        instance.invalidate_stats_cache.assert_called_once()
