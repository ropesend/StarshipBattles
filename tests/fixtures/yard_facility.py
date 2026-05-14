"""Shared factories for yard-bearing entities in tests.

PROJ-322 Task 6.6 (HLP-003): consolidates the yard-related test
helpers from:

* `tests/unit/strategy/engine/test_planetary_yard_requirement.py`
  (`_make_yard_facility(is_operational)`)
* `tests/unit/strategy/production_engine/test_tick_consumption.py`
  (`_make_planetary_yard_facility()`)
* `tests/unit/strategy/fleet/test_space_yard.py`
  (`make_ship_with_yard(name, has_yard, is_combat_capable)`)

into shared factories under `tests.fixtures.yard_facility`.

The two `_make_*_facility` helpers were structurally identical (both
build a `PlanetaryFacility` whose CORE layer carries the
`PlanetaryYard` ability); the consolidated `make_planetary_yard_facility`
exposes the operational flag both callers needed. `make_ship_with_yard`
remains the ship-side helper for the space-yard / fleet-construction tests.

Usage
-----

::

    from tests.fixtures.yard_facility import (
        make_planetary_yard_facility,
        make_ship_with_yard,
    )

    facility = make_planetary_yard_facility(is_operational=True)
    ship = make_ship_with_yard(fresh_registries, name="Carrier")
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from game.strategy.data.planetary_facility import PlanetaryFacility


def make_planetary_yard_facility(
    *,
    instance_id: str = "yard_1",
    design_id: str = "colony_hub",
    name: str = "Colony Hub",
    is_operational: bool = True,
    yard_id: str = "hub",
) -> PlanetaryFacility:
    """Build a `PlanetaryFacility` whose CORE layer carries the
    `PlanetaryYard` ability.

    Arguments
    ---------
    instance_id, design_id, name
        Facility identification — defaults match the historical helper.
    is_operational
        Whether the facility reports as operational. Tests that exercise
        the queue-disabled-when-yard-broken path pass ``False``.
    yard_id
        ID for the yard component inside the CORE layer (some tests want
        a distinct ID to disambiguate vs. other facilities in fixtures).

    Returns
    -------
    A real `PlanetaryFacility` instance ready to drop into
    `colony.facilities` for production-engine / queue tests.
    """

    return PlanetaryFacility(
        instance_id=instance_id,
        design_id=design_id,
        name=name,
        design_data={
            "layers": {
                "CORE": [{"id": yard_id, "abilities": {"PlanetaryYard": True}}]
            }
        },
        is_operational=is_operational,
    )


def make_ship_with_yard(
    fresh_registries: Any,
    *,
    name: str = "Yard Ship",
    has_yard: bool = True,
    is_combat_capable: bool = True,
) -> Any:
    """Build a mock `ShipInstance` with a `space_shipyard` component.

    Mirrors the original module-level fixture from
    `tests/unit/strategy/fleet/test_space_yard.py` (PROJ-322 Task 1.15 /
    S09-CAT4-004 / HLP-003).

    Arguments
    ---------
    fresh_registries
        The PROJ-211 fresh-registries fixture; attached to
        `mock._registries` for DI compliance.
    name
        Ship name visible to the production code.
    has_yard
        Whether the ship's `design_data` carries the `space_shipyard`
        component. Pass ``False`` for the negative-control case.
    is_combat_capable
        Mirrored on the mock's `is_combat_capable.return_value`.
    """

    from game.strategy.data.ship_instance import ShipInstance

    mock = MagicMock(spec=ShipInstance)
    mock.name = name
    mock.is_combat_capable.return_value = is_combat_capable
    mock._registries = fresh_registries  # PROJ-211: DI compliance

    if has_yard:
        mock.design_data = {
            'name': name,
            'vehicle_type': 'Ship',
            'layers': {
                'core': [
                    {'id': 'space_shipyard', 'name': 'Fleet Space Yard'}
                ]
            },
        }
    else:
        mock.design_data = {
            'name': name,
            'vehicle_type': 'Ship',
            'layers': {'core': []},
        }
    return mock


__all__ = ["make_planetary_yard_facility", "make_ship_with_yard"]
