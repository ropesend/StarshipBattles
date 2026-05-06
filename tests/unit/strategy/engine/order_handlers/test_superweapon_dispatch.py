"""Per-handler tests for `SuperweaponHandlerAdapter` (PROJ-368 Phase 4)."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.data.order_types import OrderType
from game.strategy.engine.order_handlers.superweapons import (
    SuperweaponHandlerAdapter,
    build_superweapon_handlers,
)
from game.strategy.services.superweapon_registry import (
    SuperweaponSpec,
    SUPERWEAPONS,
)


def _make_processor(method_name: str, return_value):
    p = MagicMock()
    getattr(p, method_name).return_value = return_value
    return p


def test_adapter_supported_order_types_matches_spec():
    spec = SUPERWEAPONS[0]  # IMPLODE_PLANET
    adapter = SuperweaponHandlerAdapter(spec=spec, processor=MagicMock())
    assert adapter.supported_order_types == (spec.order_type,)


@pytest.mark.parametrize("spec", list(SUPERWEAPONS))
def test_adapter_dispatches_to_correct_method(spec: SuperweaponSpec):
    method_name = f"process_{spec.order_type.name.lower()}"
    fake_result = MagicMock(success=True, fleet_consumed=False, message="ok")
    processor = _make_processor(method_name, fake_result)
    adapter = SuperweaponHandlerAdapter(spec=spec, processor=processor)

    fleet = MagicMock()
    empire = MagicMock()
    galaxy = MagicMock()
    component_registry = {"ALPHA": object()}
    empires = [empire]

    result = adapter.execute_action_order(
        fleet, empire, galaxy,
        component_registry=component_registry,
        empires=empires,
    )
    getattr(processor, method_name).assert_called_once_with(
        fleet, empire, galaxy, empires, component_registry
    )
    assert result.success is True


def test_adapter_reshapes_superweapon_result_to_order_execution_result():
    spec = SUPERWEAPONS[0]
    fake_result = MagicMock(success=True, fleet_consumed=True, message="boom")
    processor = _make_processor(f"process_{spec.order_type.name.lower()}", fake_result)
    adapter = SuperweaponHandlerAdapter(spec=spec, processor=processor)
    result = adapter.execute_action_order(MagicMock(), MagicMock(), MagicMock())
    assert result.success is True
    assert result.fleet_consumed is True
    assert result.message == "boom"


def test_adapter_passes_empty_list_when_empires_is_none():
    spec = SUPERWEAPONS[0]
    fake_result = MagicMock(success=True, fleet_consumed=False, message="")
    processor = _make_processor(f"process_{spec.order_type.name.lower()}", fake_result)
    adapter = SuperweaponHandlerAdapter(spec=spec, processor=processor)
    adapter.execute_action_order(MagicMock(), MagicMock(), MagicMock(), empires=None)
    args, _ = getattr(processor, f"process_{spec.order_type.name.lower()}").call_args
    # signature: (fleet, empire, galaxy, empires, component_registry)
    assert args[3] == []


def test_build_superweapon_handlers_yields_5_adapters():
    """Count check: 5 adapters, no SELF_DESTRUCT (handled by SelfDestructHandler)."""
    processor = MagicMock()
    adapters = build_superweapon_handlers(processor)
    assert len(adapters) == 5
    order_types = {a.supported_order_types[0] for a in adapters}
    assert OrderType.SELF_DESTRUCT not in order_types
    expected = {
        OrderType.IMPLODE_PLANET,
        OrderType.STELLERATE_STAR,
        OrderType.OPEN_WARP_POINT,
        OrderType.CLOSE_WARP_POINT,
        OrderType.CREATE_DYSON_SPHERE,
    }
    assert order_types == expected
