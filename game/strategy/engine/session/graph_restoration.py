"""PROJ-438 Phase 1: canonical post-deserialize graph-wiring steps.

Both restore paths reach the same shape after the entity dicts are
deserialized:

- ``SessionPersistenceAdapter.rehydrate_state()`` (save → load)
- ``TurnStateSnapshot.restore()`` (snapshot → rollback)

Both must perform the same four post-deserialize wiring steps before the
graph is consumable by downstream consumers (auto fleet registration,
capability calculators, order execution, pursuit AI):

1. **Galaxy back-references** — ``empire.set_galaxy(galaxy)`` for every
   empire (PROJ-219 pre-req).
2. **Fleet registration** — ``galaxy.register_fleet(fleet)`` for every
   fleet on every empire; deserialized fleets bypass ``add_fleet()`` and
   must be registered explicitly (PROJ-219).
3. **Order reference resolution** — ``fleet.resolve_order_references(
   galaxy, empires)`` to convert marker dicts in fleet orders into live
   object references (PROJ-207).
4. **Pursuer tracker rebuild** — for every ``MOVE_TO_FLEET`` /
   ``JOIN_FLEET`` order, ``order.target.pursuer_tracker.add_pursuer(
   fleet)`` to re-attach the pursuit relationship (PROJ-222).

PROJ-432 closed the silent asymmetry where the rollback path was missing
steps 1 and 4. PROJ-438 Phase 1 collapses the two now-identical inline
loops into this one canonical collaborator so future regressions cannot
re-introduce the divergence on only one side.

Scope: this module owns ONLY the four shared steps. ``DesignCatalog``
repopulation (save-load only) and ``ProductionEngine`` catalog forwarding
remain in ``persistence_adapter.py`` — see PROJ-438 Phase 1 Task 1.3 for
that asymmetry's disposition.
"""
from __future__ import annotations

from typing import Any

from game.strategy.data.order_types import OrderType


def restore_graph_wiring(galaxy: Any, empires: list[Any]) -> None:
    """Run the four canonical post-deserialize graph-wiring steps.

    Pure side-effect function on the entity graph. No GameSession
    dependency, no service-bag dependency, no ``DesignCatalog`` handling.
    Safe to call on any galaxy/empires pair whose fleets and orders were
    just constructed via ``from_dict``.

    Args:
        galaxy: Galaxy with a ``register_fleet(fleet)`` method.
        empires: List of empires; each must expose ``set_galaxy(galaxy)``,
            ``.fleets`` iterable, and each fleet must expose ``.orders``
            and ``resolve_order_references(galaxy, empires)``.
    """
    # Step 1: galaxy back-references (PROJ-219).
    for empire in empires:
        empire.set_galaxy(galaxy)

    # Step 2: fleet registration (PROJ-219).
    for empire in empires:
        for fleet in empire.fleets:
            galaxy.register_fleet(fleet)

    # Step 3: order reference resolution (PROJ-207).
    for empire in empires:
        for fleet in empire.fleets:
            fleet.resolve_order_references(galaxy, empires)

    # Step 4: pursuer tracker rebuild (PROJ-222).
    for empire in empires:
        for fleet in empire.fleets:
            for order in fleet.orders:
                if order.type in (
                    OrderType.MOVE_TO_FLEET,
                    OrderType.JOIN_FLEET,
                ):
                    if hasattr(order.target, "pursuer_tracker"):
                        order.target.pursuer_tracker.add_pursuer(fleet)
