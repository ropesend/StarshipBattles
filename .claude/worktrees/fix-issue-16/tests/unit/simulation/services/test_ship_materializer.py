"""Tests for the ship materializer service (PROJ-274).

Covers:
- `IShipMaterializer` protocol contract + runtime-checkable isinstance check.
- `InstanceBackedMaterializer` — delegates to `ship_spec.instance_ref.to_ship(...)`.
- `DesignOnlyMaterializer` — loads design JSON via injected loader and builds a Ship.
- `ShipSpec.instance_ref` field is `Optional[Any]` defaulting to None.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock

import pytest

from game.core.math import Vector2
from game.simulation.battle_spec import ShipSpec
from game.simulation.services.ship_materializer import (
    DesignOnlyMaterializer,
    InstanceBackedMaterializer,
    IShipMaterializer,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ship_spec(
    *,
    design_id: str = "test_design",
    instance_id: str = "inst_0",
    instance_ref: object = None,
    position: Vector2 = None,
) -> ShipSpec:
    return ShipSpec(
        instance_id=instance_id,
        design_id=design_id,
        theme_id="test_theme",
        name="Test Ship",
        position=position or Vector2(10.0, 20.0),
        angle=0.0,
        velocity=Vector2(0.0, 0.0),
        components=(),
        instance_ref=instance_ref,
    )


# ---------------------------------------------------------------------------
# ShipSpec.instance_ref field
# ---------------------------------------------------------------------------


def test_ship_spec_instance_ref_defaults_to_none():
    """ShipSpec constructed without instance_ref has None."""
    spec = ShipSpec(
        instance_id="i0",
        design_id="d",
        theme_id="t",
        name="S",
        position=Vector2(0.0, 0.0),
        angle=0.0,
        velocity=Vector2(0.0, 0.0),
        components=(),
    )
    assert spec.instance_ref is None


def test_ship_spec_instance_ref_accepts_any_object():
    """Loose typing: instance_ref accepts any object (duck-typed)."""
    ref = MagicMock()
    spec = _make_ship_spec(instance_ref=ref)
    assert spec.instance_ref is ref


def test_ship_spec_is_still_frozen():
    """Adding instance_ref doesn't break frozen-dataclass contract."""
    spec = _make_ship_spec()
    with pytest.raises(FrozenInstanceError):
        spec.instance_ref = MagicMock()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Protocol contract
# ---------------------------------------------------------------------------


def test_instance_backed_satisfies_protocol():
    """InstanceBackedMaterializer is an IShipMaterializer."""
    assert isinstance(InstanceBackedMaterializer(), IShipMaterializer)


def test_design_only_satisfies_protocol():
    """DesignOnlyMaterializer is an IShipMaterializer."""
    assert isinstance(DesignOnlyMaterializer(), IShipMaterializer)


# ---------------------------------------------------------------------------
# InstanceBackedMaterializer
# ---------------------------------------------------------------------------


def test_instance_backed_calls_to_ship_with_position_and_team_id():
    """materialize forwards (position, team_id, registries) to instance.to_ship."""
    fake_ship = MagicMock()
    fake_instance = MagicMock()
    fake_instance.to_ship.return_value = fake_ship
    registries = MagicMock()

    spec = _make_ship_spec(
        instance_ref=fake_instance,
        position=Vector2(100.0, 200.0),
    )
    materializer = InstanceBackedMaterializer()
    result = materializer.materialize(spec, team_id=1, registries=registries)

    assert result is fake_ship
    # to_ship receives position as a tuple (its signature is
    # `to_ship(position, team_id, *, registries)`).
    call_args = fake_instance.to_ship.call_args
    pos_arg = call_args.args[0]
    assert pos_arg == (100.0, 200.0)
    assert call_args.args[1] == 1
    assert call_args.kwargs.get("registries") is registries


def test_instance_backed_raises_on_missing_instance_ref():
    """Clear error when ship_spec.instance_ref is None."""
    registries = MagicMock()
    spec = _make_ship_spec(design_id="orphan_design", instance_ref=None)
    materializer = InstanceBackedMaterializer()
    with pytest.raises(ValueError) as exc_info:
        materializer.materialize(spec, team_id=0, registries=registries)
    message = str(exc_info.value)
    # Error must mention instance_ref and the design_id so the developer
    # knows WHICH spec is missing the ref.
    assert "instance_ref" in message
    assert "orphan_design" in message


def test_instance_backed_threads_team_id_through():
    """team_id is passed to instance.to_ship (used by ShipInstance.to_ship)."""
    fake_instance = MagicMock()
    fake_ship = MagicMock()
    fake_instance.to_ship.return_value = fake_ship
    registries = MagicMock()
    spec = _make_ship_spec(instance_ref=fake_instance)
    materializer = InstanceBackedMaterializer()
    materializer.materialize(spec, team_id=42, registries=registries)
    assert fake_instance.to_ship.call_args.args[1] == 42


def test_instance_backed_integration_with_real_ship_instance():
    """Integration: materialize a real ShipInstance through the materializer.

    Uses the `create_test_ship_instance` fixture from `tests/fixtures/strategy_entities.py`
    and the default registry provider (same pattern as existing compiler tests).
    Asserts the Ship round-trip produces a live Ship bound to the correct team.
    """
    from game.core.registry import GameRegistries, get_default_registry_provider
    from tests.fixtures.strategy_entities import create_test_ship_instance

    provider = get_default_registry_provider()
    registries = GameRegistries(
        components=provider.get_components(),
        modifiers=provider.get_modifiers(),
        vehicle_classes=provider.get_vehicle_classes(),
        resources=provider.get_resources(),
        resource_catalog=provider.get_resource_catalog(),
    )
    instance = create_test_ship_instance(registries=registries)
    spec = _make_ship_spec(
        design_id=instance.design_id,
        instance_id=instance.instance_id,
        instance_ref=instance,
        position=Vector2(50.0, 60.0),
    )
    materializer = InstanceBackedMaterializer()
    ship = materializer.materialize(spec, team_id=1, registries=registries)

    # Ship materialized successfully with correct team.
    assert ship is not None
    assert ship.team_id == 1
    # Ship has a name (sourced from design_data; instance.name is the
    # strategy-layer display name which isn't propagated by to_ship).
    assert isinstance(ship.name, str) and ship.name


# ---------------------------------------------------------------------------
# DesignOnlyMaterializer
# ---------------------------------------------------------------------------


def test_design_only_without_loader_raises_runtime_error():
    """No loader configured → construction OK, but materialize fails loudly."""
    registries = MagicMock()
    materializer = DesignOnlyMaterializer()
    spec = _make_ship_spec(design_id="no_loader_test")
    with pytest.raises(RuntimeError) as exc_info:
        materializer.materialize(spec, team_id=0, registries=registries)
    assert "design_loader" in str(exc_info.value).lower()


def test_design_only_accepts_injected_loader():
    """Constructor accepts a loader closure."""
    loader = lambda design_id: {"design": design_id}  # noqa: E731
    materializer = DesignOnlyMaterializer(design_loader=loader)
    # Confirm the loader is stored (private field, but accessible).
    assert materializer._design_loader is loader


def test_design_only_materialize_calls_loader_with_design_id(monkeypatch):
    """materialize calls `design_loader(ship_spec.design_id)` and feeds the
    result through `Ship.from_dict`."""
    captured_design_id: list[str] = []
    fake_ship = MagicMock()
    # Stub Ship.from_dict so we don't need a valid ship JSON.
    import game.simulation.entities.ship as ship_mod

    def fake_from_dict(data, *, registries):
        return fake_ship

    monkeypatch.setattr(ship_mod.Ship, "from_dict", staticmethod(fake_from_dict))

    def loader(design_id):
        captured_design_id.append(design_id)
        return {"dummy": "design"}

    materializer = DesignOnlyMaterializer(design_loader=loader)
    spec = _make_ship_spec(design_id="Test_Ship_A.json")
    registries = MagicMock()
    result = materializer.materialize(spec, team_id=0, registries=registries)

    assert captured_design_id == ["Test_Ship_A.json"]
    assert result is fake_ship
    fake_ship.recalculate_stats.assert_called_once()


def test_design_only_loader_error_propagates(monkeypatch):
    """Loader exceptions bubble up — materializer doesn't swallow them."""
    def raising_loader(design_id):
        raise FileNotFoundError(f"No such design: {design_id}")

    materializer = DesignOnlyMaterializer(design_loader=raising_loader)
    spec = _make_ship_spec(design_id="missing.json")
    registries = MagicMock()
    with pytest.raises(FileNotFoundError):
        materializer.materialize(spec, team_id=0, registries=registries)


# ---------------------------------------------------------------------------
# Context accessors (Phase 4)
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=False)
def _reset_default_materializer():
    """Reset the module-level default materializer between tests to prevent
    cross-test pollution."""
    from game.simulation.services import ship_materializer as mod
    original = mod._default_ship_materializer
    mod._default_ship_materializer = None
    yield
    mod._default_ship_materializer = original


def test_get_default_returns_instance_backed_by_default(_reset_default_materializer):
    """First access returns an InstanceBackedMaterializer (production default)."""
    from game.simulation.services.ship_materializer import (
        get_default_ship_materializer,
    )
    materializer = get_default_ship_materializer()
    assert isinstance(materializer, InstanceBackedMaterializer)


def test_get_default_returns_singleton(_reset_default_materializer):
    """Repeated calls return the same instance."""
    from game.simulation.services.ship_materializer import (
        get_default_ship_materializer,
    )
    first = get_default_ship_materializer()
    second = get_default_ship_materializer()
    assert first is second


def test_set_default_replaces_instance(_reset_default_materializer):
    """set_default_ship_materializer overrides the default."""
    from game.simulation.services.ship_materializer import (
        get_default_ship_materializer,
        set_default_ship_materializer,
    )
    custom = DesignOnlyMaterializer(design_loader=lambda did: {"x": 1})
    set_default_ship_materializer(custom)
    assert get_default_ship_materializer() is custom


def test_set_default_none_triggers_lazy_reinit(_reset_default_materializer):
    """set_default_ship_materializer(None) followed by get_default yields a
    fresh default (InstanceBackedMaterializer)."""
    from game.simulation.services.ship_materializer import (
        get_default_ship_materializer,
        set_default_ship_materializer,
    )
    custom = DesignOnlyMaterializer()
    set_default_ship_materializer(custom)
    set_default_ship_materializer(None)
    materializer = get_default_ship_materializer()
    assert isinstance(materializer, InstanceBackedMaterializer)
    assert materializer is not custom
