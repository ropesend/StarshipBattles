"""Contract tests for the command/order spec registry (PROJ-363).

These are characterization tests pinning the **current** behavior of the
command-handler / OrderType / action-time / facade-dispatch surfaces.

Phase 1 deliverable: every test in this file must PASS on current code,
*before* the spec table lands. Phases 2-4 then introduce
``COMMAND_SPECS`` and refactor the three derived surfaces (registry,
category frozensets, ``ORDER_TO_ABILITY_MAP``) plus the facade
``__getattr__`` collapse — and *these* tests must keep passing
unchanged. That's the contract.

A second test file (``test_command_specs_contract.py``) is added in
Phase 2 and asserts the spec-table-shape invariants directly. This
file holds only the surface invariants that must hold whether the spec
table exists or not.

Review finding #4 source: PROJ-363 Phase 1 checklist.
"""
from __future__ import annotations

import pytest

import game.strategy.engine.commands as commands_module
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands.order_metadata_view import order_metadata
from game.strategy.engine.commands.registry import command_registry
from game.strategy.engine.handlers.registry_factory import create_default_registry
# PROJ-429 / TD-07 Phase 4: ``ORDER_TO_TIME_FIELD`` was deleted from
# ``action_time_resolver``. The per-ability action-time field name now
# comes from ``ability_action_time_field`` in the unified
# ``AbilityMetadataRegistry``. The contract test below that pinned the
# empty extension dict is replaced by an existence-and-coverage test
# against the registry.


# ---------------------------------------------------------------------------
# Section 1 — every Command class is registered with a handler
# ---------------------------------------------------------------------------

def _all_command_class_names() -> set[str]:
    """Return the set of declared *Command class names* in commands.py."""
    return {
        name
        for name in dir(commands_module)
        if name.endswith("Command")
        and not name.startswith("_")
        and isinstance(getattr(commands_module, name), type)
    } - {"Command"}


def test_every_declared_command_has_a_registered_handler() -> None:
    """Every concrete Command DTO is dispatchable through the registry.

    Pins the current factory output: registering a new command without
    wiring its handler is a regression both before and after the
    spec-table refactor.
    """
    registry = create_default_registry()
    declared = _all_command_class_names()
    registered = set(registry._handlers.keys())
    missing = declared - registered
    assert not missing, (
        f"Command DTOs declared in commands.py without a registered handler: "
        f"{sorted(missing)}."
    )


def test_no_orphaned_handler_registrations() -> None:
    """Every registry key corresponds to a real Command class.

    Catches stale `register('FooCommand', ...)` after a Command rename
    or removal.
    """
    registry = create_default_registry()
    declared = _all_command_class_names()
    orphans = set(registry._handlers.keys()) - declared
    assert not orphans, (
        f"Registry has handlers for unknown command names: {sorted(orphans)}."
    )


# ---------------------------------------------------------------------------
# Section 2 — OrderType frozenset invariants
# ---------------------------------------------------------------------------

def test_movement_action_order_type_sets_are_disjoint() -> None:
    """movement_order_types and action_order_types never overlap.

    Both engines (FleetMovementEngine, ActionExecutionEngine) gate on
    these sets; any overlap silently double-routes an order.

    PROJ-424 Phase 5: read through ``order_metadata`` (frozensets in
    ``order_types.py`` deleted).
    """
    assert order_metadata.movement_order_types.isdisjoint(
        order_metadata.action_order_types
    )


def test_planet_action_is_subset_of_action() -> None:
    """planet_action_order_types is a subset of action_order_types."""
    assert order_metadata.planet_action_order_types.issubset(
        order_metadata.action_order_types
    )


def test_movement_order_types_contains_expected_members() -> None:
    """Pin movement_order_types contents (used by FleetMovementEngine)."""
    assert order_metadata.movement_order_types == frozenset(
        {OrderType.MOVE, OrderType.MOVE_TO_FLEET, OrderType.WARP}
    )


def test_planet_action_order_types_contains_expected_members() -> None:
    """Pin planet_action_order_types contents (used by PlanetActionEngine)."""
    assert order_metadata.planet_action_order_types == frozenset(
        {OrderType.ACTIVATE_ABILITY, OrderType.DEACTIVATE_ABILITY}
    )


def test_command_registry_planet_fms_action_order_types_derivation() -> None:
    """``CommandRegistry.planet_fms_action_order_types()`` derives from the
    ``subcategories`` tag and matches the planet-FMS member set.

    PROJ-424 Phase 1: registry-side derivation contract. Phase 5: the
    expected set is pinned here rather than against a deleted frozenset.
    """
    from game.strategy.engine.commands.registry import (
        command_registry,
        seed_default_commands,
    )

    if len(command_registry) == 0:
        seed_default_commands(command_registry)
    derived = command_registry.planet_fms_action_order_types()
    assert derived == frozenset({
        OrderType.LAY_MINES,
        OrderType.LAUNCH_FIGHTERS,
        OrderType.LAUNCH_SATELLITES,
        OrderType.RECOVER_FIGHTERS,
        OrderType.RECOVER_SATELLITES,
    })


def test_planet_fms_subcategory_tag_spelling_or_set_size() -> None:
    """PROJ-445 Phase 1 (F-B-020) — typo-and-size ratchet on the
    planet-FMS subcategory tag.

    The :meth:`CommandRegistry.planet_fms_action_order_types` derivation
    keys off the literal string ``"planet_fms"`` in each CommandSpec's
    ``subcategories``. A typo (``"plnaet_fms"``, ``"planet-fms"``,
    ``"planet_fms "``) silently drops that handler from the planet-FMS
    surface, which would manifest only when a player tries to issue
    the order from a planet — i.e., far too late.

    This ratchet asserts:

    - exactly 5 entries are derived (size guard),
    - the derived set equals the expected canonical OrderType set
      (set-equality guard catches drift either way: a typo drops one,
      a spuriously-tagged sixth handler adds one).
    """
    from game.strategy.engine.commands.registry import (
        command_registry,
        seed_default_commands,
    )

    if len(command_registry) == 0:
        seed_default_commands(command_registry)
    derived = command_registry.planet_fms_action_order_types()
    expected = {
        OrderType.LAY_MINES,
        OrderType.LAUNCH_FIGHTERS,
        OrderType.LAUNCH_SATELLITES,
        OrderType.RECOVER_FIGHTERS,
        OrderType.RECOVER_SATELLITES,
    }
    assert len(derived) == 5, (
        f"planet_fms subcategory tag count drift: expected 5, got "
        f"{len(derived)} ({sorted(t.name for t in derived)}). A typo in "
        f"one handler's `subcategories=frozenset({{\"planet_fms\"}})` "
        f"declaration silently drops that handler from the planet-FMS "
        f"dispatch surface."
    )
    assert set(derived) == expected, (
        f"planet_fms subcategory tag set drift: derived "
        f"{sorted(t.name for t in derived)} != expected "
        f"{sorted(t.name for t in expected)}."
    )


def test_action_order_types_contains_all_known_members() -> None:
    """Pin action_order_types contents.

    Excludes BUILD (production-driven) and JOIN_FLEET (instant-only,
    PROJ-207 EP-001).
    """
    assert order_metadata.action_order_types == frozenset({
        OrderType.COLONIZE,
        OrderType.TRANSFER,
        OrderType.LOAD_POPULATION,
        OrderType.UNLOAD_POPULATION,
        OrderType.IMPLODE_PLANET,
        OrderType.STELLERATE_STAR,
        OrderType.OPEN_WARP_POINT,
        OrderType.CLOSE_WARP_POINT,
        OrderType.CREATE_DYSON_SPHERE,
        OrderType.SELF_DESTRUCT,
        OrderType.ACTIVATE_ABILITY,
        OrderType.DEACTIVATE_ABILITY,
        # PROJ-FMS-B Phase 1: strategic mine-laying.
        OrderType.LAY_MINES,
        # PROJ-FMS-C Phase 1+3: strategic fighter launch + recovery.
        OrderType.LAUNCH_FIGHTERS,
        OrderType.RECOVER_FIGHTERS,
        # PROJ-FMS-D Phase 1+2: strategic satellite launch + recovery.
        OrderType.LAUNCH_SATELLITES,
        OrderType.RECOVER_SATELLITES,
    })


# ---------------------------------------------------------------------------
# Section 3 — order_to_ability_map coverage
# ---------------------------------------------------------------------------

# The action-time resolver looks up ability names per OrderType. Movement
# orders bypass it (return 0). Generic ability toggles read the ability
# name from the order's target dict, not from the static map.
_ABILITY_LOOKUP_EXEMPT = order_metadata.movement_order_types | {
    OrderType.ACTIVATE_ABILITY,
    OrderType.DEACTIVATE_ABILITY,
    OrderType.JOIN_FLEET,   # instant path; never hits action-time resolver
    OrderType.BUILD,        # production engine, not action engine
    OrderType.TRANSFER,     # falls through to default action_time=1
    OrderType.LOAD_POPULATION,
    OrderType.UNLOAD_POPULATION,
    # PROJ-FMS-B Phase 1: LAY_MINES uses StrategicMineLayerAbility on the
    # carrier ship, but the action_time lookup is data-only here; falls
    # through to default action_time. The ability-name resolver is not
    # the gate.
    OrderType.LAY_MINES,
    # PROJ-FMS-C audit Fix (inline risk): LAUNCH_FIGHTERS / RECOVER_FIGHTERS
    # are NO LONGER exempt — the command specs declare
    # ``action_ability_name='StrategicFighterLaunch'`` and
    # ``'RecoverFighters'`` respectively, so the ability-lookup resolver
    # gates them via the carrier ship's mounted abilities. Adding either
    # back to this exempt set is a deliberate regression and must surface
    # in this test.
}


def test_action_orders_have_ability_map_entry() -> None:
    """Every action OrderType that needs a static ability lookup has one.

    Pins the live ``order_metadata.order_to_ability_map`` for the 7
    superweapon-style actions plus COLONIZE.

    PROJ-424 Phase 3: read through the lazy view rather than the deleted
    import-time ``ORDER_TO_ABILITY_MAP`` snapshot.
    """
    expected_keys = set(order_metadata.action_order_types) - _ABILITY_LOOKUP_EXEMPT
    actual_keys = set(order_metadata.order_to_ability_map.keys())
    assert expected_keys == actual_keys, (
        f"order_to_ability_map coverage drift. Missing: {expected_keys - actual_keys}. "
        f"Unexpected: {actual_keys - expected_keys}."
    )


def test_order_to_ability_map_values_are_known_abilities() -> None:
    """Pin the ability-name strings (catches accidental rename).

    These names must match component ability dicts in components.json.

    PROJ-424 Phase 3: read through ``order_metadata.order_to_ability_map``.
    """
    assert order_metadata.order_to_ability_map == {
        OrderType.COLONIZE: 'ColonizePlanet',
        OrderType.IMPLODE_PLANET: 'DestroyPlanet',
        OrderType.STELLERATE_STAR: 'DestroyStar',
        OrderType.OPEN_WARP_POINT: 'OpenWarpPoint',
        OrderType.CLOSE_WARP_POINT: 'CloseWarpPoint',
        OrderType.CREATE_DYSON_SPHERE: 'CreateDysonSphere',
        OrderType.SELF_DESTRUCT: 'SelfDestruct',
        # PROJ-FMS-C audit Fix (inline risk): ability-lookup gating for
        # the fighter launch + recovery flows. Ability names match the
        # component ability dicts in ``data/components.json``.
        OrderType.LAUNCH_FIGHTERS: 'StrategicFighterLaunch',
        OrderType.RECOVER_FIGHTERS: 'RecoverFighters',
        # PROJ-FMS-D Phase 1+2: ability-lookup gating for satellite
        # launch + recovery. Closes the same loophole the fighter
        # equivalents closed.
        OrderType.LAUNCH_SATELLITES: 'StrategicSatelliteLaunch',
        OrderType.RECOVER_SATELLITES: 'RecoverSatellites',
    }


def test_action_time_field_resolves_through_unified_registry() -> None:
    """PROJ-429 / TD-07 Phase 4: the empty ``ORDER_TO_TIME_FIELD``
    extension point is replaced by per-ability metadata in
    ``AbilityMetadataRegistry``.

    Pins the current state: every action-ability registered in a
    ``CommandSpec`` resolves to a non-empty time-field name through
    ``ability_action_time_field``. The default is ``'action_time'``.
    """
    from game.strategy.services.ability_metadata import ability_action_time_field

    seen: set[str] = set()
    for spec in command_registry.all():
        name = spec.action_ability_name
        if name is None:
            continue
        seen.add(name)
        field_name = ability_action_time_field(name)
        assert field_name, (
            f"ability_action_time_field({name!r}) returned empty"
        )
    assert seen, "command_registry has no action_ability_name entries — unexpected"


# ---------------------------------------------------------------------------
# Section 4 — facade dispatch surface (every existing helper still callable)
# ---------------------------------------------------------------------------

EXISTING_FACADE_DISPATCH_HELPERS = (
    "dispatch_issue_colonize",
    "dispatch_issue_move",
    "dispatch_issue_intercept",
    "dispatch_issue_join_fleet",
    "dispatch_clear_orders",
    "dispatch_issue_transfer",
    "dispatch_issue_warp",
    "dispatch_split_fleet",
    "dispatch_delete_order",
    "dispatch_reorder_order",
    "dispatch_issue_self_destruct",
    "dispatch_queue_colonize_mission",
    "dispatch_queue_implode_planet_mission",
    "dispatch_queue_stellerate_star_mission",
    "dispatch_queue_open_warp_point_mission",
    "dispatch_queue_close_warp_point_mission",
    "dispatch_queue_create_dyson_sphere_mission",
    "dispatch_issue_implode_planet",
    "dispatch_issue_stellerate_star",
    "dispatch_issue_open_warp_point",
    "dispatch_issue_close_warp_point",
    "dispatch_issue_create_dyson_sphere",
    "dispatch_issue_build_order",
    "dispatch_remove_build_order",
    "dispatch_add_to_construction_queue",
    "dispatch_remove_from_construction_queue",
    "dispatch_reorder_construction_queue",
    "dispatch_activate_planet_ability",
    "dispatch_deactivate_planet_ability",
    "dispatch_clear_planet_orders",
    "dispatch_delete_planet_order",
    "dispatch_set_atmosphere_target",
)


@pytest.mark.parametrize("helper_name", EXISTING_FACADE_DISPATCH_HELPERS)
def test_facade_dispatch_helper_exists_on_slice_class(helper_name: str) -> None:
    """Every legacy ``dispatch_*`` helper resolves on the slice class.

    Pins the public facade-slice surface. After the Phase 4
    ``__getattr__`` collapse the helpers must still be reachable —
    either as real methods or via the resolver.
    """
    from game.strategy.facade.slices.command_dispatch_slice import (
        CommandDispatchSlice,
    )

    # We don't instantiate the slice (it requires session state); we just
    # check that attribute access resolves to *something* callable. Methods
    # defined on the class are always reachable via class-attribute lookup;
    # the Phase 4 ``__getattr__`` resolver is instance-level and is
    # exercised by the dedicated facade-resolution test.
    obj = CommandDispatchSlice.__dict__.get(helper_name)
    if obj is None:
        # Phase 4 path: helper resolved through __getattr__ on the
        # instance. Fall back to instance-level lookup using a stub.
        slice_inst = object.__new__(CommandDispatchSlice)
        # Set __slots__ so __getattr__ has the dependencies it needs.
        try:
            slice_inst._state = None  # type: ignore[attr-defined]
            slice_inst._handle_command = lambda cmd: None  # type: ignore[attr-defined]
        except AttributeError:
            pass
        resolved = getattr(slice_inst, helper_name, None)
        assert callable(resolved), (
            f"Facade dispatch helper {helper_name!r} is no longer reachable "
            f"on CommandDispatchSlice."
        )
    else:
        assert callable(obj), (
            f"{helper_name!r} resolves on CommandDispatchSlice but is not callable."
        )


# ---------------------------------------------------------------------------
# Section 5 — OrderType ↔ Command class one-way coverage
# ---------------------------------------------------------------------------

# Every OrderType must be reachable from at least one Command (directly or
# via mission decomposition). This pins the dispatch graph so a new
# OrderType can't ship without at least one command path.
ORDER_TYPES_REACHABLE_VIA_COMMAND = {
    OrderType.MOVE,                    # IssueMoveCommand + auto-queued by missions
    OrderType.WARP,                    # IssueWarpCommand
    OrderType.COLONIZE,                # IssueColonizeCommand
    OrderType.MOVE_TO_FLEET,           # IssueInterceptCommand
    OrderType.JOIN_FLEET,              # IssueJoinFleetCommand
    OrderType.BUILD,                   # IssueBuildOrderCommand
    OrderType.TRANSFER,                # IssueTransferCommand
    OrderType.IMPLODE_PLANET,          # IssueImplodePlanetCommand
    OrderType.STELLERATE_STAR,         # IssueStellerateStarCommand
    OrderType.OPEN_WARP_POINT,         # IssueOpenWarpPointCommand
    OrderType.CLOSE_WARP_POINT,        # IssueCloseWarpPointCommand
    OrderType.CREATE_DYSON_SPHERE,     # IssueCreateDysonSphereCommand
    OrderType.SELF_DESTRUCT,           # IssueSelfDestructCommand
    OrderType.LOAD_POPULATION,         # IssueTransferCommand (direction=LOAD)
    OrderType.UNLOAD_POPULATION,       # IssueTransferCommand (direction=UNLOAD)
    OrderType.ACTIVATE_ABILITY,        # ActivatePlanetAbilityCommand (PROJ-438 Phase 5)
    OrderType.DEACTIVATE_ABILITY,      # DeactivatePlanetAbilityCommand (PROJ-438 Phase 5)
    OrderType.LAY_MINES,               # PROJ-FMS-B Phase 1: IssueLayMinesCommand
    OrderType.LAUNCH_FIGHTERS,         # PROJ-FMS-C Phase 1: IssueLaunchFightersCommand
    OrderType.RECOVER_FIGHTERS,        # PROJ-FMS-C Phase 3: IssueRecoverFightersCommand
    OrderType.LAUNCH_SATELLITES,       # PROJ-FMS-D Phase 1: IssueLaunchSatellitesCommand
    OrderType.RECOVER_SATELLITES,      # PROJ-FMS-D Phase 2: IssueRecoverSatellitesCommand
}


# PROJ-FMS-A Phase 5 reserved enum values. These intentionally have no
# command/handler path in PROJ-FMS-A — they are wired in PROJ-FMS-B/C/D.
# PROJ-FMS-B Phase 1 moved LAY_MINES into ORDER_TYPES_REACHABLE_VIA_COMMAND.
# PROJ-FMS-C Phase 1+3 moved LAUNCH_FIGHTERS / RECOVER_FIGHTERS.
# PROJ-FMS-D Phase 1+2 moved LAUNCH_SATELLITES / RECOVER_SATELLITES.
ORDER_TYPES_RESERVED_NO_COMMAND_YET: set = set()


def test_every_order_type_is_reachable_via_command() -> None:
    """Pin the 1:N OrderType-to-Command coverage.

    Adding a new OrderType without any command path is almost always a
    bug: there's no way for the UI or AI to issue the order. PROJ-FMS-A
    Phase 5 reserved five enum values for future PROJ-FMS-B/C/D wiring
    — those are tracked in ``ORDER_TYPES_RESERVED_NO_COMMAND_YET`` and
    excluded from the strict coverage assertion here.
    """
    actual = set(OrderType)
    extra = actual - ORDER_TYPES_REACHABLE_VIA_COMMAND - ORDER_TYPES_RESERVED_NO_COMMAND_YET
    missing = ORDER_TYPES_REACHABLE_VIA_COMMAND - actual
    assert not extra, (
        f"New OrderType members without a documented command path: {sorted(e.name for e in extra)}."
    )
    assert not missing, (
        f"OrderType members removed but still listed in coverage map: "
        f"{sorted(m.name for m in missing)}."
    )


# ---------------------------------------------------------------------------
# Section 6 — serializer round-trip coverage
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "order_type,target",
    [
        (OrderType.MOVE, None),
        (OrderType.WARP, None),
        (OrderType.COLONIZE, None),
        (OrderType.MOVE_TO_FLEET, None),
        (OrderType.JOIN_FLEET, None),
        (OrderType.BUILD, None),
        (OrderType.TRANSFER, {'direction': 'load', 'cargo_type': 'passengers', 'amount': 0}),
        (OrderType.LOAD_POPULATION, {'direction': 'load', 'amount': 0}),
        (OrderType.UNLOAD_POPULATION, {'direction': 'unload', 'amount': 0}),
        (OrderType.SELF_DESTRUCT, None),
        (OrderType.ACTIVATE_ABILITY, {'ability_name': 'PlanetaryShield'}),
        (OrderType.DEACTIVATE_ABILITY, {'ability_name': 'PlanetaryShield'}),
    ],
)
def test_order_serializer_round_trip_dict_targets(order_type: OrderType, target) -> None:
    """to_dict / from_dict round-trips preserve OrderType for these targets.

    Pins the Order serialization invariant for the simple-target subset.
    Reference targets (Planet/Fleet/HexCoord) are covered by the existing
    ``test_order_serializer.py`` round-trip tests.
    """
    order = Order(order_type, target=target)
    payload = order.to_dict()
    restored = Order.from_dict(payload)
    assert restored.type == order.type
