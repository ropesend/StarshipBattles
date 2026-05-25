"""Shared save-restore helper for applying modifiers with rejection logging.

Extracted in PROJ-498 Phase 5 (audit finding F1) to deduplicate the
near-identical 18/19-line blocks in
``game/simulation/battle_state.py`` (``ShipState.to_ship``) and
``game/simulation/entities/ship_serialization.py``
(``ShipSerializer._load_components``).

Both call sites need the same behavior: at the save-restore boundary,
check whether a modifier present in the registry is still allowed for
the target component, and if not, drop it silently while emitting a
diagnostic ``logger.warning``. Logging at the call site (not inside
``Component.add_modifier``) is intentional — builder/UI rejection paths
intentionally probe rejection conditions and would generate noise.

This module is pure code organization. It adds no behavior beyond what
the two call sites already do. Existing tests on the log message format
in
``tests/unit/simulation/test_battle_state_live_object_bridges.py``
(``TestShipStateToShipRejectionLogging``) and
``tests/unit/simulation/entities/test_ship_serialization.py``
(``TestLoadComponentsRejectionLogging``) continue to pass without
edits.
"""
from __future__ import annotations

import logging
from typing import Any

from game.simulation.services.modifier_service import ModifierService

logger = logging.getLogger(__name__)


def apply_modifier_with_rejection_logging(
    *,
    modifier_id: str,
    modifier_value: Any,
    component: Any,
    modifier_registry: dict[str, Any],
    context_label: str,
    target_label: str,
) -> bool:
    """Apply ``modifier_id`` to ``component``; log + skip on rejection.

    Args:
        modifier_id: Modifier ID being restored. MUST already be present
            in ``modifier_registry``; callers do that membership check
            (so the unknown-id branch — distinct messaging in some
            callers — stays at the call site).
        modifier_value: Value to pass through to ``component.add_modifier``.
        component: Live component the modifier is being applied to.
            Must expose ``id``, ``type_str``, ``abilities`` and ``data``
            for ``ModifierService.check_allowance`` to evaluate.
        modifier_registry: Modifier registry to construct the
            ``ModifierService`` against.
        context_label: Short prefix that identifies the call site in the
            warning, e.g. ``"BattleState restore"`` or ``"ShipSerializer"``.
        target_label: Free-form descriptor of the host of ``component`` —
            typically ``f"ship '{ship_id_or_name}'"``. Used verbatim in
            the warning so call sites control whether they print a UUID
            (battle save) or a ship name (ship save).

    Returns:
        True if the modifier passed ``check_allowance`` and was applied
        via ``component.add_modifier``; False if it was rejected (and
        logged).
    """
    allowance = ModifierService(
        modifier_registry=modifier_registry
    ).check_allowance(modifier_id, component)
    if not allowance.allowed:
        logger.warning(
            f"{context_label}: Modifier '{modifier_id}' rejected for "
            f"component '{component.id}' on {target_label}: "
            f"{allowance.reason.name}; skipping"
        )
        return False
    component.add_modifier(modifier_id, modifier_value)
    return True
