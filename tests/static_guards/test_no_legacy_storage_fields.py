"""PROJ-436 Phase 3f + Phase 4f + Phase 5 + Phase 7 deletion guard.

Locks in the final-state contract for the legacy storage-field
deletions:

* Phase 3f — :class:`ShipInstance` MUST NOT carry ``cargo_contents``
  / ``consumable_levels`` as dataclass fields.
* Phase 4f — :class:`Planet` MUST NOT carry ``stockpile`` /
  ``max_stockpile`` / ``staging_yard`` as dataclass fields.
* Phase 5  — :class:`Empire` MUST NOT carry ``_fleet_resource_pool``
  as an instance attribute. ``Empire.resource_pool`` is now a pure
  aggregation query that walks colony stockpiles only; the fleet-side
  durable storage was always a self-flagged TODO ("temporary storage
  for fleet construction") and is gone.
* Phase 7  — :class:`TransferValidator` MUST NOT carry the legacy
  ``VALID_CARGO_TYPES`` hardcoded whitelist as a class attribute, and
  ``game.ui.screens.transfer_view_model`` / ``transfer_dialog`` MUST
  NOT expose the legacy ``RESOURCE_TYPES`` / ``RESOURCE_DISPLAY_NAMES``
  constants. The unified contract routes through
  ``ResourceCatalog`` + the three categorical sentinels in
  :data:`game.strategy.validation.transfer_validator._CATEGORICAL_CARGO_TYPES`.

For ShipInstance / Planet the public attribute names survive as
backward-compatible ``@property`` accessors over renamed private
dataclass fields. Production callers route through stable manager
APIs (the cargo / consumable manager surfaces for ShipInstance, and
``IPlanetMutator`` / the Planet stockpile-helper methods for Planet).

For Empire the durable field is fully deleted — there is no
``_fleet_resource_pool`` (private or public). ``Empire`` is a regular
class rather than a dataclass, so the guard checks the instance
``__dict__`` (``vars(empire)``) of a freshly-constructed instance.

These tests are explicit ratchets preventing reintroduction of any
of the six seams.

Model: ``tests/unit/strategy/data/test_phase_1f_deletion_guard.py``
(PROJ-431 Phase 1f deletion guard for ``carried_items``).
"""
from __future__ import annotations

from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet
from game.strategy.data.ship_instance import ShipInstance


def test_ship_instance_has_no_cargo_contents_dataclass_field() -> None:
    """``ShipInstance`` must NOT declare ``cargo_contents`` as a dataclass field.

    PROJ-436 Phase 3f deletion guard. Production callers route through
    ``ship._cargo_mgr.set_cargo`` / ``get_all_cargo`` / ``total_cargo_units``
    / ``has_cargo`` (the stable manager API landed in Phase 3b). A
    backward-compatible ``cargo_contents`` property over the cargo
    manager's storage is permitted as a test-fixture compatibility
    shim — the dataclass field is gone.
    """
    fields = getattr(ShipInstance, "__dataclass_fields__", {})
    assert "cargo_contents" not in fields, (
        f"ShipInstance still has a `cargo_contents` dataclass field "
        f"(PROJ-436 Phase 3f deletion guard). The stable cargo-manager "
        f"API is the canonical access path. Found fields: "
        f"{sorted(fields.keys())}"
    )


def test_ship_instance_has_no_consumable_levels_dataclass_field() -> None:
    """``ShipInstance`` must NOT declare ``consumable_levels`` as a dataclass field.

    PROJ-436 Phase 3f deletion guard. Production callers route through
    ``ship._resource_mgr.set_level`` / ``get_all_levels`` /
    ``get_current_resource`` / ``replace_levels`` (the stable manager
    API landed in Phase 3b). A backward-compatible
    ``consumable_levels`` property over the consumable manager's
    storage is permitted as a test-fixture compatibility shim — the
    dataclass field is gone.
    """
    fields = getattr(ShipInstance, "__dataclass_fields__", {})
    assert "consumable_levels" not in fields, (
        f"ShipInstance still has a `consumable_levels` dataclass field "
        f"(PROJ-436 Phase 3f deletion guard). The stable consumable-"
        f"manager API is the canonical access path. Found fields: "
        f"{sorted(fields.keys())}"
    )


def test_planet_has_no_stockpile_dataclass_field() -> None:
    """``Planet`` must NOT declare ``stockpile`` as a dataclass field.

    PROJ-436 Phase 4f deletion guard. Production writers route through
    ``IPlanetMutator.set_stockpile_amount`` / ``set_max_stockpile`` or
    Planet's own ``add_to_stockpile`` / ``consume_from_stockpile``
    helpers, which write to the private ``_stockpile`` field. A
    backward-compatible ``stockpile`` ``@property`` over the private
    dict is permitted as the read / mutate surface for test fixtures
    and read-only callers — the dataclass field is gone.
    """
    fields = getattr(Planet, "__dataclass_fields__", {})
    assert "stockpile" not in fields, (
        f"Planet still has a `stockpile` dataclass field "
        f"(PROJ-436 Phase 4f deletion guard). The stable Planet "
        f"stockpile-helper / IPlanetMutator API is the canonical "
        f"write path. Found fields: {sorted(fields.keys())}"
    )


def test_planet_has_no_max_stockpile_dataclass_field() -> None:
    """``Planet`` must NOT declare ``max_stockpile`` as a dataclass field.

    PROJ-436 Phase 4f deletion guard. Production writers route through
    ``IPlanetMutator.set_max_stockpile``. A backward-compatible
    ``max_stockpile`` ``@property`` over the private ``_max_stockpile``
    dict is permitted — the dataclass field is gone.
    """
    fields = getattr(Planet, "__dataclass_fields__", {})
    assert "max_stockpile" not in fields, (
        f"Planet still has a `max_stockpile` dataclass field "
        f"(PROJ-436 Phase 4f deletion guard). The stable Planet "
        f"stockpile-helper / IPlanetMutator API is the canonical "
        f"write path. Found fields: {sorted(fields.keys())}"
    )


def test_planet_has_no_staging_yard_dataclass_field() -> None:
    """``Planet`` must NOT declare ``staging_yard`` as a dataclass field.

    PROJ-436 Phase 4f deletion guard. Production writers route through
    ``IPlanetMutator.add_staging_item`` / ``pop_staging_item`` or
    Planet's own ``add_to_staging_yard`` / ``remove_from_staging_yard``
    helpers, which append / pop the private ``_staging_yard`` list. A
    backward-compatible ``staging_yard`` ``@property`` over the
    private list is permitted — the dataclass field is gone.
    """
    fields = getattr(Planet, "__dataclass_fields__", {})
    assert "staging_yard" not in fields, (
        f"Planet still has a `staging_yard` dataclass field "
        f"(PROJ-436 Phase 4f deletion guard). The stable Planet "
        f"staging-helper / IPlanetMutator API is the canonical "
        f"write path. Found fields: {sorted(fields.keys())}"
    )


def test_planet_staging_yard_substrate_is_typed_not_dict() -> None:
    """``Planet._staging_yard`` MUST hold typed ``CarriedVehicle | DropPod``
    entries only; dict entries are forbidden.

    PROJ-450 Phase 5 type-pin guard. The substrate was widened from
    ``List[Dict[str, Any]]`` to ``List[CarriedVehicle | DropPod]``.
    The ``add_to_staging_yard`` method normalises dict inputs to
    typed before appending, so any future regression that re-introduces
    a raw dict (via ``planet._staging_yard.append(legacy_dict)`` or
    similar back-door) is caught here.

    The public ``Planet.staging_yard`` property returns
    ``tuple[CarriedVehicle | DropPod, ...]``; this guard pins the
    underlying storage shape.
    """
    from game.core.hex_math import HexCoord
    from game.strategy.data.bay_inventory import DropPod
    from game.strategy.data.carried_vehicle import CarriedVehicle
    from game.strategy.data.planet import Planet, PlanetType

    planet = Planet(
        name="GuardPlanet",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5514.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.71,
        tectonic_activity=0.6,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
        owner_id=0,
    )

    # Add via the public API — dicts and typed inputs both accepted.
    planet.add_to_staging_yard(
        CarriedVehicle(
            design_id="guard_cv",
            vehicle_type="mine",
            design_data={"name": "Guard CV"},
            mass=1.0,
        )
    )
    planet.add_to_staging_yard(
        {
            "design_id": "guard_pod",
            "design_data": {},
            "mass": 2.0,
            "payload": {"name": "Guard Pod"},
        }
    )

    # The substrate MUST hold typed entries regardless of input shape.
    types = [type(item).__name__ for item in planet._staging_yard]
    assert all(
        isinstance(item, (CarriedVehicle, DropPod))
        for item in planet._staging_yard
    ), (
        f"Planet._staging_yard must hold CarriedVehicle | DropPod "
        f"entries only (PROJ-450 Phase 5 type-pin guard). Got: {types}"
    )


def _fresh_empire() -> Empire:
    """Construct an Empire with no callers — used by the Phase 5 guard."""
    return Empire(empire_id=1, name="Guard", color=(0, 0, 0))


def test_empire_has_no_fleet_resource_pool_attribute() -> None:
    """``Empire`` must NOT carry ``_fleet_resource_pool`` on a fresh instance.

    PROJ-436 Phase 5 deletion guard. The empire's fleet-side resource
    pool was always a self-flagged TODO ("temporary storage for fleet
    construction") and is fully deleted in Phase 5 — fleet
    construction resources draw from the build-location's container
    (``Planet.stockpile`` for planet construction, fleet cargo for
    fleet construction). ``Empire.resource_pool`` is now a pure
    aggregation query that walks ``self.colonies`` only; there is no
    fleet-side durable summand.

    Empire is a regular class (not a dataclass), so the guard checks
    the instance ``__dict__`` of a freshly-constructed Empire.
    """
    empire = _fresh_empire()
    instance_attrs = sorted(vars(empire).keys())
    assert "_fleet_resource_pool" not in vars(empire), (
        f"Empire still initialises `_fleet_resource_pool` on a fresh "
        f"instance (PROJ-436 Phase 5 deletion guard). The fleet-side "
        f"durable pool is gone; `resource_pool` is a pure aggregation "
        f"of `self.colonies[*].stockpile`. Found instance attrs: "
        f"{instance_attrs}"
    )


def test_empire_resource_pool_is_pure_aggregation_with_no_colonies() -> None:
    """A freshly-constructed empire with no colonies has an empty resource_pool.

    PROJ-436 Phase 5 deletion guard. Before Phase 5 a freshly-
    constructed empire could carry resources via ``_fleet_resource_pool``;
    after Phase 5, ``resource_pool`` is a pure aggregation over
    ``self.colonies[*].stockpile`` and is empty for an empire with no
    colonies. This pins the new contract from the read-side.
    """
    empire = _fresh_empire()
    assert empire.resource_pool == {}, (
        "Empire.resource_pool should aggregate colony stockpiles only; "
        "an empire with no colonies must return an empty dict. Got: "
        f"{empire.resource_pool}"
    )


# ---------------------------------------------------------------------------
# Phase 7 deletion guards
# ---------------------------------------------------------------------------


def test_transfer_validator_has_no_valid_cargo_types_attribute() -> None:
    """``TransferValidator`` must NOT carry the legacy ``VALID_CARGO_TYPES``.

    PROJ-436 Phase 7 deletion guard. The hardcoded whitelist is gone.
    Cargo-type validation now consults
    :class:`game.core.resources.ResourceCatalog` plus three categorical
    sentinels (``passengers`` / ``drop_pod`` / ``vehicle``) in
    :mod:`game.strategy.validation.transfer_validator`. Adding a new
    resource to ``data/resources.json`` makes it transferrable; no
    validator change required.
    """
    from game.strategy.validation.transfer_validator import TransferValidator

    assert not hasattr(TransferValidator, "VALID_CARGO_TYPES"), (
        "TransferValidator still exposes a `VALID_CARGO_TYPES` class "
        "attribute (PROJ-436 Phase 7 deletion guard). Cargo-type "
        "validation must route through ResourceCatalog + categorical "
        "sentinels, not a hardcoded whitelist."
    )


def test_transfer_view_model_has_no_resource_types_constant() -> None:
    """``transfer_view_model`` MUST NOT expose ``RESOURCE_TYPES``.

    PROJ-436 Phase 7 deletion guard. The UI iterates
    ``ResourceCatalog.all_ids()`` (Core-layer single source of truth)
    in display order; the previous hardcoded ordered list is gone.
    """
    import game.ui.screens.transfer_view_model as vm

    assert not hasattr(vm, "RESOURCE_TYPES"), (
        "transfer_view_model still exposes a `RESOURCE_TYPES` "
        "module-level constant (PROJ-436 Phase 7 deletion guard). UI "
        "iteration must consult ResourceCatalog.all_ids()."
    )


def test_transfer_view_model_has_no_resource_display_names_constant() -> None:
    """``transfer_view_model`` MUST NOT expose ``RESOURCE_DISPLAY_NAMES``.

    PROJ-436 Phase 7 deletion guard. The UI looks up display labels
    via ``ResourceDefinition.name`` from the same catalog; the previous
    hardcoded mapping is gone.
    """
    import game.ui.screens.transfer_view_model as vm

    assert not hasattr(vm, "RESOURCE_DISPLAY_NAMES"), (
        "transfer_view_model still exposes a `RESOURCE_DISPLAY_NAMES` "
        "module-level constant (PROJ-436 Phase 7 deletion guard). "
        "Display labels must come from ResourceDefinition.name."
    )


def test_transfer_dialog_has_no_resource_types_re_export() -> None:
    """``transfer_dialog`` MUST NOT re-export the deleted UI constants.

    PROJ-436 Phase 7 deletion guard. The re-export at
    ``transfer_dialog.py:39-43`` (the legacy convenience shim for
    importers that wrote ``from game.ui.screens.transfer_dialog import
    RESOURCE_TYPES``) is gone.
    """
    import game.ui.screens.transfer_dialog as td

    assert not hasattr(td, "RESOURCE_TYPES"), (
        "transfer_dialog still re-exports `RESOURCE_TYPES` "
        "(PROJ-436 Phase 7 deletion guard)."
    )
    assert not hasattr(td, "RESOURCE_DISPLAY_NAMES"), (
        "transfer_dialog still re-exports `RESOURCE_DISPLAY_NAMES` "
        "(PROJ-436 Phase 7 deletion guard)."
    )


def test_production_engine_has_no_context_type_storage_dispatch() -> None:
    """``production_engine.py`` MUST NOT read ``context_type`` for storage routing.

    PROJ-436 Phase 8 deletion guard. The three storage-typed branch
    sites in ``ProductionEngine._check_affordability`` /
    ``_log_resource_shortage`` / ``_apply_resource_consumption``
    previously dispatched on
    ``getattr(colony_or_fleet, 'context_type', None) == 'planet' /
    'fleet'`` to pick between
    ``has_stockpile`` / ``has_cargo_resources`` etc. Phase 8 collapses
    the dispatch via a unified ``IProductionResourceSource`` protocol
    satisfied by both Planet and Fleet through
    ``production_has_resources`` / ``production_get_resource`` /
    ``production_consume_resource`` methods. The engine reads through
    the protocol; ``context_type`` is no longer a storage routing
    signal.

    This guard reads ``production_engine.py`` as text and asserts the
    pattern ``getattr(colony_or_fleet, 'context_type'`` does not
    appear. UI ``context_type`` reads in
    ``build_queue_controller.py`` / ``build_queue_source.py`` etc.
    remain — they are entity-routing, not storage-typed (PROJ-436
    Phase 6a audit).
    """
    from pathlib import Path

    engine_path = (
        Path(__file__).parent.parent.parent
        / "game" / "strategy" / "engine" / "production_engine.py"
    )
    source = engine_path.read_text(encoding="utf-8")
    forbidden = "getattr(colony_or_fleet, 'context_type'"
    assert forbidden not in source, (
        f"production_engine.py still reads colony_or_fleet.context_type "
        f"for storage routing (PROJ-436 Phase 8 deletion guard). "
        f"Production code must route storage through the unified "
        f"``production_has_resources`` / ``production_get_resource`` "
        f"/ ``production_consume_resource`` methods on the resource-"
        f"source entity. Found {forbidden!r} in the engine source."
    )


def test_planet_has_production_resource_source_methods() -> None:
    """``Planet`` MUST expose the unified production-resource-source API.

    PROJ-436 Phase 8 substrate. Planet satisfies the
    ``IProductionResourceSource`` protocol by exposing
    ``production_has_resources(costs)`` /
    ``production_get_resource(resource_type)`` /
    ``production_consume_resource(resource_type, amount)``. These are
    thin polymorphic delegators over the existing
    ``has_stockpile`` / ``get_stockpile`` / ``consume_from_stockpile``
    stockpile API — the existing methods stay because non-engine
    callers (``transfer_branches.py``, the ``IStockpileHolder``
    protocol) target the stockpile-specific names.
    """
    for method_name in (
        "production_has_resources",
        "production_get_resource",
        "production_consume_resource",
    ):
        assert hasattr(Planet, method_name), (
            f"Planet missing `{method_name}` "
            f"(PROJ-436 Phase 8 substrate). The production-engine "
            f"contract requires unified resource-source methods on "
            f"both Planet and Fleet."
        )


def test_fleet_has_production_resource_source_methods() -> None:
    """``Fleet`` MUST expose the unified production-resource-source API.

    PROJ-436 Phase 8 substrate. Fleet satisfies the
    ``IProductionResourceSource`` protocol by exposing
    ``production_has_resources(costs)`` /
    ``production_get_resource(resource_type)`` /
    ``production_consume_resource(resource_type, amount)``. Thin
    delegators over the existing
    ``has_cargo_resources`` / ``get_cargo_resource`` /
    ``consume_cargo_resource`` fleet-cargo API.
    """
    from game.strategy.data.fleet import Fleet

    for method_name in (
        "production_has_resources",
        "production_get_resource",
        "production_consume_resource",
    ):
        assert hasattr(Fleet, method_name), (
            f"Fleet missing `{method_name}` "
            f"(PROJ-436 Phase 8 substrate). The production-engine "
            f"contract requires unified resource-source methods on "
            f"both Planet and Fleet."
        )
