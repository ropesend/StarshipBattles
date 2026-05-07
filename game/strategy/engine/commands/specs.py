"""Declarative command/order spec registry (PROJ-363).

Single source of truth for the metadata that previously lived scattered
across seven files (DTOs, OrderType frozensets, registry factory,
action-time map, facade dispatch helpers, and superweapon lambdas).
This module declares one ``CommandSpec`` per Command DTO; the runtime
registry, the order-type category frozensets, and the action-time
ability map are all derived from this table at module-import time.

Adding a new command becomes a one-file edit: add a Command DTO + a
handler, append a ``CommandSpec`` row here, done. The registry, the
category sets, the action-time hookup, and the facade dispatch helper
all populate automatically.

Import-order constraint: this module sits at the leaf of the
strategy-engine import graph. It imports DTOs from
``game.strategy.engine.commands`` (the package's ``__init__.py``) and
handler classes from their leaf modules, but **nothing imports back
into here** from the handler/data side at module-load time. Downstream
consumers (``registry_factory``, ``order_types``,
``action_time_resolver``) use deferred (function-local) imports to
avoid cycles.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type

from game.strategy.data.order_types import OrderType

# DTOs (sibling module in the same package — ``commands/__init__.py``).
from game.strategy.engine.commands import (
    AddToConstructionQueueCommand,
    ClearOrdersCommand,
    ClearPlanetOrdersCommand,
    Command,
    DeleteOrderCommand,
    DeletePlanetOrderCommand,
    IssueBuildOrderCommand,
    IssueCloseWarpPointCommand,
    IssueColonizeCommand,
    IssueCreateDysonSphereCommand,
    IssueImplodePlanetCommand,
    IssueInterceptCommand,
    IssueJoinFleetCommand,
    IssueMoveCommand,
    IssueOpenWarpPointCommand,
    IssuePlanetOrderCommand,
    IssueSelfDestructCommand,
    IssueStellerateStarCommand,
    IssueTransferCommand,
    IssueWarpCommand,
    QueueCloseWarpPointMissionCommand,
    QueueColonizeMissionCommand,
    QueueCreateDysonSphereMissionCommand,
    QueueImplodePlanetMissionCommand,
    QueueOpenWarpPointMissionCommand,
    QueueStellerateStarMissionCommand,
    RemoveBuildOrderCommand,
    RemoveFromConstructionQueueCommand,
    ReorderConstructionQueueCommand,
    ReorderOrderCommand,
    SetAtmosphereTargetCommand,
    SetBuildQueuePausedCommand,
    SetGravityTargetCommand,
    SetRadiationShieldTargetCommand,
    SetWaterTargetCommand,
    SplitFleetCommand,
)

# Handler classes — import from their leaf modules (the ``handlers/__init__.py``
# also re-exports most of them, but the ``superweapon_command_handlers`` and
# ``planet_command_handlers`` siblings remain at their original locations
# pending a follow-up move out of PROJ-309's scope).
from game.strategy.engine.handlers.base import ICommandHandler
from game.strategy.engine.handlers.build import (
    BuildOrderCommandHandler,
    RemoveBuildOrderCommandHandler,
)
from game.strategy.engine.handlers.construction_queue import (
    AddToConstructionQueueCommandHandler,
    RemoveFromConstructionQueueCommandHandler,
    ReorderConstructionQueueCommandHandler,
    SetBuildQueuePausedCommandHandler,
)
from game.strategy.engine.handlers.movement import (
    ColonizeCommandHandler,
    InterceptCommandHandler,
    JoinCommandHandler,
    MoveCommandHandler,
    WarpCommandHandler,
)
from game.strategy.engine.handlers.order_queue import (
    ClearOrdersCommandHandler,
    ColonizeMissionCommandHandler,
    DeleteOrderCommandHandler,
    ReorderOrderCommandHandler,
    SplitFleetCommandHandler,
)
from game.strategy.engine.handlers.transfer import TransferCommandHandler
from game.strategy.engine.planet_command_handlers import (
    ClearPlanetOrdersCommandHandler,
    DeletePlanetOrderCommandHandler,
    IssuePlanetOrderCommandHandler,
    SetAtmosphereTargetCommandHandler,
    SetGravityTargetCommandHandler,
    SetRadiationShieldTargetCommandHandler,
    SetWaterTargetCommandHandler,
)
from game.strategy.engine.superweapon_command_handlers import (
    CloseWarpPointCommandHandler,
    CloseWarpPointMissionCommandHandler,
    CreateDysonSphereCommandHandler,
    CreateDysonSphereMissionCommandHandler,
    ImplodePlanetCommandHandler,
    ImplodePlanetMissionCommandHandler,
    OpenWarpPointCommandHandler,
    OpenWarpPointMissionCommandHandler,
    SelfDestructCommandHandler,
    StellerateStarCommandHandler,
    StellerateStarMissionCommandHandler,
)


# Allowed values for the ``category`` and ``execution_model`` fields. Kept
# as plain string literals (rather than enums) so adding a new category in
# a single line of spec data doesn't require touching an enum.
#
# - ``movement``        Fleet routing orders handled by FleetMovementEngine
# - ``action``          Tick-based fleet actions (ActionExecutionEngine)
# - ``superweapon``     Subset of action; PROJ-364 will use this for its
#                       own dispatch table; otherwise behaves like 'action'
# - ``planet``          Planet-targeted orders (ability toggles, env targets)
# - ``build``           Construction-queue / build-order commands
# - ``construction``    Pure queue-management commands (add/remove/reorder)
# - ``fleet_management`` Fleet-queue / split / reorder commands
#
# - ``execution_model='action'``      Tick-based, goes through ActionExecutionEngine
# - ``execution_model='production'``  Persistent, ProductionEngine ticks (BUILD)
# - ``execution_model='instant'``     Resolved on submission (no tick cost)
# - ``execution_model='mission'``     Decomposes into MOVE + ACTION (no own OrderType)
# - ``execution_model='planet'``      Planet ability tick — PlanetActionEngine
ALLOWED_CATEGORIES = frozenset({
    'movement', 'action', 'superweapon', 'planet',
    'build', 'construction', 'fleet_management',
})
ALLOWED_EXECUTION_MODELS = frozenset({
    'action', 'production', 'instant', 'mission', 'planet',
})


@dataclass(frozen=True)
class CommandSpec:
    """Declarative metadata for a single Command DTO.

    Every field that downstream surfaces (registry, frozensets,
    action-time map, facade dispatch helper) need is captured here so
    a new command lands in one place.

    Args:
        command_class: The Command DTO type (e.g. ``IssueMoveCommand``).
        order_type: The OrderType this command emits, or ``None`` for
            mission commands (which decompose into MOVE+ACTION at
            handler-execution time and have no single OrderType).
        handler_class: The handler type registered for this command.
        category: One of ``ALLOWED_CATEGORIES``. Drives the order-type
            frozensets generated in ``order_types.py``.
        subcategories: Free-form tags for cross-cutting groupings
            (e.g. fleet/planet routing for split commands). Reserved for
            future use; empty by default.
        action_ability_name: The component-ability name in
            components.json that supplies ``action_time``. ``None`` for
            commands that don't go through ActionExecutionEngine
            (movement, instant, mission, build, planet ability toggles
            which read the ability name from the order target).
        execution_model: One of ``ALLOWED_EXECUTION_MODELS``. Drives
            the gating logic in resolvers / engines.
        facade_helper_name: The ``dispatch_*_command`` method name on
            ``CommandDispatchSlice`` (post Phase 4 collapse: resolved
            via ``__getattr__``). ``None`` for commands without a UI
            dispatch entry point.
        serializer_codec: Documentation-only tag identifying the
            ``Order.target`` codec used for save serialization (e.g.
            ``'planet_ref'``, ``'hex_coord'``). Commands themselves
            are not persisted; this references the **order**'s codec.
            Reserved for future round-trip contract tests.
    """
    command_class: Type[Command]
    order_type: OrderType | None
    handler_class: Type[ICommandHandler]
    category: str
    subcategories: frozenset[str] = field(default_factory=frozenset)
    action_ability_name: str | None = None
    execution_model: str = 'action'
    facade_helper_name: str | None = None
    serializer_codec: str | None = None

    def __post_init__(self) -> None:
        # Light validation — invariants here are cheap to check and stop
        # typos at module-import time rather than days later in a test.
        if self.category not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"CommandSpec({self.command_class.__name__}): "
                f"category {self.category!r} not in ALLOWED_CATEGORIES."
            )
        if self.execution_model not in ALLOWED_EXECUTION_MODELS:
            raise ValueError(
                f"CommandSpec({self.command_class.__name__}): "
                f"execution_model {self.execution_model!r} not in ALLOWED_EXECUTION_MODELS."
            )


# ---------------------------------------------------------------------------
# COMMAND_SPECS — the table.
# ---------------------------------------------------------------------------
# Order is documentary (matches the existing registry_factory.py grouping)
# but the table is consumed as a tuple by every downstream surface.

COMMAND_SPECS: tuple[CommandSpec, ...] = (
    # ----- Movement (5) -------------------------------------------------
    CommandSpec(
        command_class=IssueMoveCommand,
        order_type=OrderType.MOVE,
        handler_class=MoveCommandHandler,
        category='movement',
        execution_model='action',  # movement engine, but action-time=0 path
        facade_helper_name='dispatch_issue_move',
        serializer_codec='hex_coord',
    ),
    CommandSpec(
        command_class=IssueWarpCommand,
        order_type=OrderType.WARP,
        handler_class=WarpCommandHandler,
        category='movement',
        execution_model='action',
        facade_helper_name='dispatch_issue_warp',
        serializer_codec='hex_coord',
    ),
    CommandSpec(
        command_class=IssueInterceptCommand,
        order_type=OrderType.MOVE_TO_FLEET,
        handler_class=InterceptCommandHandler,
        category='movement',
        execution_model='action',
        facade_helper_name='dispatch_issue_intercept',
        serializer_codec='fleet_ref',
    ),
    CommandSpec(
        command_class=IssueJoinFleetCommand,
        order_type=OrderType.JOIN_FLEET,
        handler_class=JoinCommandHandler,
        category='movement',
        execution_model='instant',
        facade_helper_name='dispatch_issue_join_fleet',
        serializer_codec='fleet_ref',
    ),
    CommandSpec(
        command_class=IssueColonizeCommand,
        order_type=OrderType.COLONIZE,
        handler_class=ColonizeCommandHandler,
        category='action',
        action_ability_name='ColonizePlanet',
        execution_model='action',
        facade_helper_name='dispatch_issue_colonize',
        serializer_codec='planet_ref',
    ),

    # ----- Fleet-action / cargo (1) ------------------------------------
    CommandSpec(
        command_class=IssueTransferCommand,
        order_type=OrderType.TRANSFER,
        handler_class=TransferCommandHandler,
        category='action',
        execution_model='action',
        facade_helper_name='dispatch_issue_transfer',
        serializer_codec='transfer',
    ),

    # ----- Mission decompositions (1 + 5 superweapon variants) ---------
    # No own OrderType; handler decomposes into MOVE + ACTION orders.
    CommandSpec(
        command_class=QueueColonizeMissionCommand,
        order_type=None,
        handler_class=ColonizeMissionCommandHandler,
        category='action',
        execution_model='mission',
        facade_helper_name='dispatch_queue_colonize_mission',
    ),

    # ----- Order-queue management (4) ----------------------------------
    CommandSpec(
        command_class=ClearOrdersCommand,
        order_type=None,
        handler_class=ClearOrdersCommandHandler,
        category='fleet_management',
        execution_model='instant',
        facade_helper_name='dispatch_clear_orders',
    ),
    CommandSpec(
        command_class=SplitFleetCommand,
        order_type=None,
        handler_class=SplitFleetCommandHandler,
        category='fleet_management',
        execution_model='instant',
        facade_helper_name='dispatch_split_fleet',
    ),
    CommandSpec(
        command_class=DeleteOrderCommand,
        order_type=None,
        handler_class=DeleteOrderCommandHandler,
        category='fleet_management',
        execution_model='instant',
        facade_helper_name='dispatch_delete_order',
    ),
    CommandSpec(
        command_class=ReorderOrderCommand,
        order_type=None,
        handler_class=ReorderOrderCommandHandler,
        category='fleet_management',
        execution_model='instant',
        facade_helper_name='dispatch_reorder_order',
    ),

    # ----- Superweapons immediate (6) ----------------------------------
    CommandSpec(
        command_class=IssueImplodePlanetCommand,
        order_type=OrderType.IMPLODE_PLANET,
        handler_class=ImplodePlanetCommandHandler,
        category='superweapon',
        action_ability_name='DestroyPlanet',
        execution_model='action',
        facade_helper_name='dispatch_issue_implode_planet',
        serializer_codec='planet_ref',
    ),
    CommandSpec(
        command_class=IssueStellerateStarCommand,
        order_type=OrderType.STELLERATE_STAR,
        handler_class=StellerateStarCommandHandler,
        category='superweapon',
        action_ability_name='DestroyStar',
        execution_model='action',
        facade_helper_name='dispatch_issue_stellerate_star',
    ),
    CommandSpec(
        command_class=IssueOpenWarpPointCommand,
        order_type=OrderType.OPEN_WARP_POINT,
        handler_class=OpenWarpPointCommandHandler,
        category='superweapon',
        action_ability_name='OpenWarpPoint',
        execution_model='action',
        facade_helper_name='dispatch_issue_open_warp_point',
        serializer_codec='warp_params',
    ),
    CommandSpec(
        command_class=IssueCloseWarpPointCommand,
        order_type=OrderType.CLOSE_WARP_POINT,
        handler_class=CloseWarpPointCommandHandler,
        category='superweapon',
        action_ability_name='CloseWarpPoint',
        execution_model='action',
        facade_helper_name='dispatch_issue_close_warp_point',
        serializer_codec='warp_params',
    ),
    CommandSpec(
        command_class=IssueCreateDysonSphereCommand,
        order_type=OrderType.CREATE_DYSON_SPHERE,
        handler_class=CreateDysonSphereCommandHandler,
        category='superweapon',
        action_ability_name='CreateDysonSphere',
        execution_model='action',
        facade_helper_name='dispatch_issue_create_dyson_sphere',
    ),
    CommandSpec(
        command_class=IssueSelfDestructCommand,
        order_type=OrderType.SELF_DESTRUCT,
        handler_class=SelfDestructCommandHandler,
        category='superweapon',
        action_ability_name='SelfDestruct',
        execution_model='action',
        facade_helper_name='dispatch_issue_self_destruct',
        serializer_codec='ship_id_list',
    ),

    # ----- Superweapon mission variants (5) ----------------------------
    CommandSpec(
        command_class=QueueImplodePlanetMissionCommand,
        order_type=None,
        handler_class=ImplodePlanetMissionCommandHandler,
        category='superweapon',
        execution_model='mission',
        facade_helper_name='dispatch_queue_implode_planet_mission',
    ),
    CommandSpec(
        command_class=QueueStellerateStarMissionCommand,
        order_type=None,
        handler_class=StellerateStarMissionCommandHandler,
        category='superweapon',
        execution_model='mission',
        facade_helper_name='dispatch_queue_stellerate_star_mission',
    ),
    CommandSpec(
        command_class=QueueOpenWarpPointMissionCommand,
        order_type=None,
        handler_class=OpenWarpPointMissionCommandHandler,
        category='superweapon',
        execution_model='mission',
        facade_helper_name='dispatch_queue_open_warp_point_mission',
    ),
    CommandSpec(
        command_class=QueueCloseWarpPointMissionCommand,
        order_type=None,
        handler_class=CloseWarpPointMissionCommandHandler,
        category='superweapon',
        execution_model='mission',
        facade_helper_name='dispatch_queue_close_warp_point_mission',
    ),
    CommandSpec(
        command_class=QueueCreateDysonSphereMissionCommand,
        order_type=None,
        handler_class=CreateDysonSphereMissionCommandHandler,
        category='superweapon',
        execution_model='mission',
        facade_helper_name='dispatch_queue_create_dyson_sphere_mission',
    ),

    # ----- Build orders (2) --------------------------------------------
    CommandSpec(
        command_class=IssueBuildOrderCommand,
        order_type=OrderType.BUILD,
        handler_class=BuildOrderCommandHandler,
        category='build',
        execution_model='production',
        facade_helper_name='dispatch_issue_build_order',
    ),
    CommandSpec(
        command_class=RemoveBuildOrderCommand,
        order_type=None,
        handler_class=RemoveBuildOrderCommandHandler,
        category='build',
        execution_model='instant',
        facade_helper_name='dispatch_remove_build_order',
    ),

    # ----- Construction-queue management (4) ---------------------------
    CommandSpec(
        command_class=AddToConstructionQueueCommand,
        order_type=None,
        handler_class=AddToConstructionQueueCommandHandler,
        category='construction',
        execution_model='instant',
        facade_helper_name='dispatch_add_to_construction_queue',
    ),
    CommandSpec(
        command_class=RemoveFromConstructionQueueCommand,
        order_type=None,
        handler_class=RemoveFromConstructionQueueCommandHandler,
        category='construction',
        execution_model='instant',
        facade_helper_name='dispatch_remove_from_construction_queue',
    ),
    CommandSpec(
        command_class=ReorderConstructionQueueCommand,
        order_type=None,
        handler_class=ReorderConstructionQueueCommandHandler,
        category='construction',
        execution_model='instant',
        facade_helper_name='dispatch_reorder_construction_queue',
    ),
    CommandSpec(
        command_class=SetBuildQueuePausedCommand,
        order_type=None,
        handler_class=SetBuildQueuePausedCommandHandler,
        category='construction',
        execution_model='instant',
        # No facade helper today (FEAT-17 wires through other paths).
        facade_helper_name=None,
    ),

    # ----- Planet orders (7) -------------------------------------------
    CommandSpec(
        command_class=IssuePlanetOrderCommand,
        order_type=None,  # Routes to ACTIVATE/DEACTIVATE_ABILITY at handle time
        handler_class=IssuePlanetOrderCommandHandler,
        category='planet',
        execution_model='planet',
        facade_helper_name='dispatch_issue_planet_order',
    ),
    CommandSpec(
        command_class=ClearPlanetOrdersCommand,
        order_type=None,
        handler_class=ClearPlanetOrdersCommandHandler,
        category='planet',
        execution_model='instant',
        facade_helper_name='dispatch_clear_planet_orders',
    ),
    CommandSpec(
        command_class=DeletePlanetOrderCommand,
        order_type=None,
        handler_class=DeletePlanetOrderCommandHandler,
        category='planet',
        execution_model='instant',
        facade_helper_name='dispatch_delete_planet_order',
    ),
    CommandSpec(
        command_class=SetAtmosphereTargetCommand,
        order_type=None,
        handler_class=SetAtmosphereTargetCommandHandler,
        category='planet',
        execution_model='instant',
        facade_helper_name='dispatch_set_atmosphere_target',
    ),
    CommandSpec(
        command_class=SetGravityTargetCommand,
        order_type=None,
        handler_class=SetGravityTargetCommandHandler,
        category='planet',
        execution_model='instant',
        # No facade helper today.
        facade_helper_name=None,
    ),
    CommandSpec(
        command_class=SetWaterTargetCommand,
        order_type=None,
        handler_class=SetWaterTargetCommandHandler,
        category='planet',
        execution_model='instant',
        facade_helper_name=None,
    ),
    CommandSpec(
        command_class=SetRadiationShieldTargetCommand,
        order_type=None,
        handler_class=SetRadiationShieldTargetCommandHandler,
        category='planet',
        execution_model='instant',
        facade_helper_name=None,
    ),
)


# ---------------------------------------------------------------------------
# Index views — pre-built lookups that downstream consumers re-export.
# ---------------------------------------------------------------------------

def specs_by_command_name() -> dict[str, CommandSpec]:
    """Map ``CommandClass.__name__`` -> CommandSpec. Used by registry."""
    return {s.command_class.__name__: s for s in COMMAND_SPECS}


def specs_by_facade_helper() -> dict[str, CommandSpec]:
    """Map ``facade_helper_name`` -> CommandSpec.

    Excludes specs without a facade helper (None entries).
    """
    return {
        s.facade_helper_name: s
        for s in COMMAND_SPECS
        if s.facade_helper_name is not None
    }


def order_types_for_category(category: str) -> frozenset[OrderType]:
    """All non-None OrderTypes for specs in ``category``.

    Used to derive ``MOVEMENT_ORDER_TYPES`` etc. Mission specs (which
    set ``order_type=None``) are skipped.
    """
    return frozenset(
        s.order_type for s in COMMAND_SPECS
        if s.category == category and s.order_type is not None
    )


# OrderTypes that are *implicitly* action orders even though no Command DTO
# carries them as a primary ``order_type``. These get folded into
# ``ACTION_ORDER_TYPES`` but have their own dispatch path:
# - LOAD_POPULATION / UNLOAD_POPULATION: emitted by IssueTransferCommand
#   handler when direction='load'/'unload' (transfer-based, but
#   classified as their own action order types for engine routing).
# - ACTIVATE_ABILITY / DEACTIVATE_ABILITY: multiplexed by
#   IssuePlanetOrderCommand based on the order_type string field.
IMPLICIT_ACTION_ORDER_TYPES: frozenset[OrderType] = frozenset({
    OrderType.LOAD_POPULATION,
    OrderType.UNLOAD_POPULATION,
    OrderType.ACTIVATE_ABILITY,
    OrderType.DEACTIVATE_ABILITY,
})


def movement_order_types() -> frozenset[OrderType]:
    """Derive the ``MOVEMENT_ORDER_TYPES`` set.

    Movement orders are those routed through ``FleetMovementEngine``.
    Includes only specs in the 'movement' category whose
    ``execution_model`` is 'action' — that excludes JOIN_FLEET
    (instant), which is conceptually movement but doesn't go through
    the movement engine's tick-based path.
    """
    return frozenset(
        s.order_type for s in COMMAND_SPECS
        if s.category == 'movement'
        and s.order_type is not None
        and s.execution_model == 'action'
    )


def action_order_types() -> frozenset[OrderType]:
    """Derive the ``ACTION_ORDER_TYPES`` set.

    Includes specs in 'action' or 'superweapon' categories, plus the
    implicit (non-Command) order types for population transfers and
    ability toggles.
    """
    explicit = frozenset(
        s.order_type for s in COMMAND_SPECS
        if s.category in ('action', 'superweapon')
        and s.order_type is not None
        and s.execution_model == 'action'
    )
    return explicit | IMPLICIT_ACTION_ORDER_TYPES


def planet_action_order_types() -> frozenset[OrderType]:
    """OrderTypes routed through ``PlanetActionEngine``.

    Today this is exactly ``ACTIVATE_ABILITY``/``DEACTIVATE_ABILITY``,
    which don't have their own Command DTOs (``IssuePlanetOrderCommand``
    multiplexes into them at handler-execution time). The set is hard-
    coded here for now and asserted against the existing
    ``PLANET_ACTION_ORDER_TYPES`` frozenset by a contract test.
    """
    return frozenset({OrderType.ACTIVATE_ABILITY, OrderType.DEACTIVATE_ABILITY})


def order_to_ability_map() -> dict[OrderType, str]:
    """Map OrderType -> ability name for action-time lookups.

    Mirrors the existing hand-maintained ``ORDER_TO_ABILITY_MAP``.
    Includes only specs that have both an ``order_type`` and an
    ``action_ability_name``.
    """
    return {
        s.order_type: s.action_ability_name
        for s in COMMAND_SPECS
        if s.order_type is not None and s.action_ability_name is not None
    }


__all__ = [
    'CommandSpec',
    'COMMAND_SPECS',
    'ALLOWED_CATEGORIES',
    'ALLOWED_EXECUTION_MODELS',
    'IMPLICIT_ACTION_ORDER_TYPES',
    'specs_by_command_name',
    'specs_by_facade_helper',
    'order_types_for_category',
    'movement_order_types',
    'action_order_types',
    'planet_action_order_types',
    'order_to_ability_map',
]
