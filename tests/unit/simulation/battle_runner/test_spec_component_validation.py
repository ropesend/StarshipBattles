"""PROJ-358: Validation that `_apply_spec_components_to_ship` rejects spec
component entries that do not map to a materialized Ship component.

Replaces the silent-ignore "design drift" path with a typed
`ValidationException` carrying ship_id, component_id, instance_index,
and design_id context.
"""
from __future__ import annotations

import pytest

from game.core.exceptions import ValidationException
from game.core.math import Vector2
from game.simulation.battle_runner import _apply_spec_components_to_ship
from game.simulation.battle_spec import ComponentStateSpec, ShipSpec
from game.simulation.components.component_constants import ComponentStatus


# ---------------------------------------------------------------------------
# Minimal fakes — `_apply_spec_components_to_ship` only touches
# `ship.layers[*].components[*].id / current_hp / take_damage(...)`.
# ---------------------------------------------------------------------------


class _FakeComp:
    def __init__(
        self,
        cid: str,
        current_hp: float,
        max_hp: float = 100.0,
        status: ComponentStatus = ComponentStatus.ACTIVE,
        is_active: bool = True,
    ) -> None:
        self.id = cid
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.status = status
        self.is_active = is_active

    def take_damage(self, dmg: int) -> None:
        self.current_hp = max(0.0, self.current_hp - dmg)


class _FakeLayer:
    def __init__(self, comps: list) -> None:
        self.components = comps


class _FakeShip:
    def __init__(self, layers: dict, instance_id: str = "ship-test") -> None:
        self.layers = layers
        self.instance_id = instance_id


def _ship_with_two_lasers() -> _FakeShip:
    """Materialized ship: bridge#0, laser_cannon#0, laser_cannon#1."""
    return _FakeShip(
        layers={
            "CORE": _FakeLayer([_FakeComp("bridge", 100.0)]),
            "OUTER": _FakeLayer(
                [
                    _FakeComp("laser_cannon", 100.0),
                    _FakeComp("laser_cannon", 100.0),
                ]
            ),
        },
        instance_id="ship-abc",
    )


def _ship_spec(
    *,
    instance_id: str = "ship-abc",
    design_id: str = "Cruiser",
    components: tuple = (),
) -> ShipSpec:
    return ShipSpec(
        instance_id=instance_id,
        design_id=design_id,
        theme_id="Federation",
        name="TestShip",
        position=Vector2(0, 0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=components,
    )


# ---------------------------------------------------------------------------
# Failing tests — these MUST raise after PROJ-358 lands. Pre-fix, the
# silent-ignore path absorbs the bad entries and the tests fail (no raise).
# ---------------------------------------------------------------------------


def test_unmapped_component_id_raises_validation_with_full_context():
    """Spec lists a component_id that does not exist on the Ship.

    Must raise `ValidationException` with ship_id, component_id,
    instance_index, and design_id in the message.
    """
    ship = _ship_with_two_lasers()
    spec = _ship_spec(
        components=(
            ComponentStateSpec(
                component_id="missile_rack",  # Not on the materialized ship
                instance_index=0,
                current_hp=50.0,
                max_hp=100.0,
                status="ACTIVE",
                is_active=True,
            ),
        ),
    )

    with pytest.raises(ValidationException) as excinfo:
        _apply_spec_components_to_ship(spec, ship)

    msg = str(excinfo.value)
    assert "ship-abc" in msg
    assert "missile_rack" in msg
    assert "Cruiser" in msg
    # instance_index appears as the integer 0 — match on a token form
    assert "0" in msg
    # Context dict carries the structured fields (rich error handling).
    ctx = excinfo.value.context
    assert ctx["ship_id"] == "ship-abc"
    assert ctx["component_id"] == "missile_rack"
    assert ctx["instance_index"] == 0
    assert ctx["design_id"] == "Cruiser"


def test_unmapped_instance_index_raises_validation():
    """Spec references laser_cannon#5 but the Ship only has #0 and #1.

    Component id is valid; instance_index drifts. Must raise.
    """
    ship = _ship_with_two_lasers()
    spec = _ship_spec(
        components=(
            ComponentStateSpec(
                component_id="laser_cannon",
                instance_index=5,
                current_hp=20.0,
                max_hp=100.0,
                status="DAMAGED",
                is_active=True,
            ),
        ),
    )

    with pytest.raises(ValidationException) as excinfo:
        _apply_spec_components_to_ship(spec, ship)

    ctx = excinfo.value.context
    assert ctx["component_id"] == "laser_cannon"
    assert ctx["instance_index"] == 5


def test_mixed_valid_and_invalid_spec_raises_on_invalid():
    """A spec with one valid + one invalid entry must raise — the valid
    entry is irrelevant to validation passing."""
    ship = _ship_with_two_lasers()
    spec = _ship_spec(
        components=(
            ComponentStateSpec(
                component_id="laser_cannon",
                instance_index=0,
                current_hp=70.0,
                max_hp=100.0,
                status="DAMAGED",
                is_active=True,
            ),
            ComponentStateSpec(
                component_id="phantom_thruster",  # Drift
                instance_index=0,
                current_hp=10.0,
                max_hp=100.0,
                status="DAMAGED",
                is_active=True,
            ),
        ),
    )

    with pytest.raises(ValidationException) as excinfo:
        _apply_spec_components_to_ship(spec, ship)

    assert excinfo.value.context["component_id"] == "phantom_thruster"


# ---------------------------------------------------------------------------
# Passing tests — valid specs remain accepted with bit-identical results.
# These must pass both before and after PROJ-358.
# ---------------------------------------------------------------------------


def test_valid_spec_applies_hp_to_target_component():
    """Every spec entry maps cleanly; HP lands on the intended instance."""
    ship = _ship_with_two_lasers()
    spec = _ship_spec(
        components=(
            ComponentStateSpec(
                component_id="laser_cannon",
                instance_index=0,
                current_hp=40.0,
                max_hp=100.0,
                status="DAMAGED",
                is_active=True,
            ),
            ComponentStateSpec(
                component_id="laser_cannon",
                instance_index=1,
                current_hp=70.0,
                max_hp=100.0,
                status="DAMAGED",
                is_active=True,
            ),
        ),
    )

    _apply_spec_components_to_ship(spec, ship)

    laser0 = ship.layers["OUTER"].components[0]
    laser1 = ship.layers["OUTER"].components[1]
    bridge = ship.layers["CORE"].components[0]
    assert laser0.current_hp == pytest.approx(40.0)
    assert laser1.current_hp == pytest.approx(70.0)
    # Untouched component (no spec entry) remains at full HP.
    assert bridge.current_hp == pytest.approx(100.0)


def test_empty_components_no_op():
    """`ShipSpec.components` empty → function returns without touching the ship."""
    ship = _ship_with_two_lasers()
    spec = _ship_spec(components=())

    _apply_spec_components_to_ship(spec, ship)

    assert ship.layers["CORE"].components[0].current_hp == 100.0
    assert ship.layers["OUTER"].components[0].current_hp == 100.0
    assert ship.layers["OUTER"].components[1].current_hp == 100.0
