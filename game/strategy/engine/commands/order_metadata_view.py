"""Live, lazy, cycle-safe read facade over ``command_registry``
(PROJ-424 Phase 2 / TD-03).

Why this module exists
----------------------
Five truth surfaces previously encoded overlapping order metadata:

1. The 41-DTO Command catalog in ``commands/__init__.py``.
2. The ``CommandSpec`` registry in ``commands/registry.py``.
3. Four hardcoded ``frozenset``s in ``game/strategy/data/order_types.py``
   (``MOVEMENT_ORDER_TYPES``, ``ACTION_ORDER_TYPES``,
   ``PLANET_ACTION_ORDER_TYPES``, ``PLANET_FMS_ACTION_ORDER_TYPES``).
4. The import-time-frozen ``ORDER_TO_ABILITY_MAP`` snapshot at
   ``action_time_resolver.py``.
5. ``fleet.py`` re-exports of two of the frozensets.

The frozensets in ``order_types.py`` were pinned hardcoded because
runtime derivation from ``command_registry`` would trigger the cycle::

    order_types.py
        -> commands/registry.py
            -> seed_default_commands()
                -> handlers.{movement, transfer, lay_mines, ...}
                    -> order_types.py  (Order, OrderType)

``OrderMetadataView`` breaks the cycle by importing ``command_registry``
LAZILY inside :meth:`_registry` rather than at module load. Because the
handler modules import only ``Order`` / ``OrderType`` from
``order_types.py`` (not the now-removed frozensets), reading through
the view never re-triggers the cycle.

Cycle-safety invariant (pinned by ``test_view_is_lazy_at_import_time``)
----------------------------------------------------------------------
Importing ``game.strategy.engine.commands.order_metadata_view`` must
NOT cause ``game.strategy.engine.commands.registry`` to be pulled into
``sys.modules``. Any future "optimisation" that hoists the import to
module top will reintroduce the cycle.

No caching, no invalidation
---------------------------
The view is deliberately not cached: ``command_registry.register(...,
replace=True)`` is supported for mod overlays, and a cached snapshot
would silently fail to reflect the overlay (the exact bug that motivated
deleting the import-time ``ORDER_TO_ABILITY_MAP`` snapshot). Every
property read calls back into the registry. The work is cheap because
the registry stores its specs in a plain ``dict``.

PROJ-429 (TD-07) will mirror this lazy-view pattern for ability
metadata convergence.
"""
from __future__ import annotations

# IMPORTANT: do NOT import anything from
# ``game.strategy.engine.commands.registry`` at module top. The lazy
# import lives inside :meth:`OrderMetadataView._registry`.
#
# ``OrderType`` is imported from the data layer (not the registry) so
# this module remains independent of registry init at module load.
from typing import TYPE_CHECKING

from game.strategy.data.order_types import OrderType

if TYPE_CHECKING:
    from game.strategy.engine.commands.registry import CommandRegistry


class OrderMetadataView:
    """Live, lazy, cycle-safe read facade over ``command_registry``.

    Import-time invariant: importing this module must NOT import
    ``game.strategy.engine.commands.registry``. All registry access
    happens inside :meth:`_registry`, which is called only when a
    property is read.

    Read invariant: each property returns the registry's current
    derivation result — no caching, no snapshot. A ``replace=True``
    overlay is visible immediately.
    """

    @staticmethod
    def _registry() -> "CommandRegistry":
        """Return the seeded ``command_registry`` (lazy import).

        The deferred import is the single linchpin that keeps the
        ``order_types -> registry -> handlers -> order_types`` cycle
        broken. Do not hoist it.

        Seeds the registry on first read when it is empty, so callers
        that import the view without going through the production
        bootstrap (tests, isolated tools) still see all 40 specs.
        """
        from game.strategy.engine.commands.registry import (
            command_registry,
            seed_default_commands,
        )

        if len(command_registry) == 0:
            seed_default_commands(command_registry)
        return command_registry

    # ------------------------------------------------------------------
    # Read-only views.
    # ------------------------------------------------------------------

    @property
    def movement_order_types(self) -> frozenset[OrderType]:
        return self._registry().movement_order_types()

    @property
    def action_order_types(self) -> frozenset[OrderType]:
        return self._registry().action_order_types()

    @property
    def planet_action_order_types(self) -> frozenset[OrderType]:
        return self._registry().planet_action_order_types()

    @property
    def planet_fms_action_order_types(self) -> frozenset[OrderType]:
        return self._registry().planet_fms_action_order_types()

    @property
    def order_to_ability_map(self) -> dict[OrderType, str]:
        return self._registry().order_to_ability_map()

    def serializer_codec_for(self, order_type: OrderType) -> str | None:
        """PROJ-438 Phase 7: expose the per-OrderType serializer codec
        through the live view. Future projects can route
        ``Order.to_dict()`` and ``OrderSerializer._deserialize_target``
        through this lookup to reduce the inline target-shape branching."""
        return self._registry().serializer_codec_for(order_type)


# Canonical singleton — consumers ``from ... import order_metadata``
# rather than constructing their own.
order_metadata = OrderMetadataView()


__all__ = ["OrderMetadataView", "order_metadata"]
