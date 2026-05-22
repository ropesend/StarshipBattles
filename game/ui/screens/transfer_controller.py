"""Controller for ``TransferDialog`` (PROJ-328 Phase C).

Owns the side-effecting boundaries:

* Facade queries (``get_fleets_at_hex``, ``get_planets_at_hex``,
  ``get_fleet``, ``get_planet``).
* Drop-pod design discovery via ``DesignLibrary``.
* ``IssueTransferCommand`` construction + dispatch through
  ``facade.handle_command``.

The view model holds state; the controller bridges state ↔ engine.
The dialog owns widgets; the controller does not touch pygame_gui.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``)
TransferDialog is "command-heavy. Add focused tests around
pending-transfer math and IssueTransferCommand emission BEFORE moving
UI code." Those characterization tests live at
``tests/unit/ui/screens/test_transfer_dialog_characterization.py``.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from game.strategy.engine.commands import IssueTransferCommand


@dataclass
class ConfirmResult:
    """Result of `TransferController.confirm_pending`.

    PROJ-343 T1.4: prior to this fix the controller returned a plain int
    (orders_issued count). The dialog used `try/finally: self.kill()` and
    closed regardless of the return — including on validation aborts where
    the user wanted to correct input. This richer result lets the dialog
    distinguish "user-correctable abort" from "successful issue or
    catastrophic dispatch failure".

    Attributes:
        orders_issued: How many TRANSFER orders the facade accepted.
        aborted_for_correction: True when the controller short-circuited on
            input-validation grounds (no source/target, both endpoints
            non-fleet, all pending zero) and the dialog should stay open.
        rejection_message: First rejection message captured when EVERY
            dispatched command was rejected by the facade (QA Obs 5
            follow-up, 2026-05-16). The dialog surfaces this via
            ``scene.ui.show_error_message`` so the user sees why
            "Confirm All" appeared to do nothing. ``None`` for input-
            validation aborts (no commands dispatched) and for mixed-
            accept paths.
    """
    orders_issued: int
    aborted_for_correction: bool = False
    rejection_message: Optional[str] = None

if TYPE_CHECKING:
    from game.ui.screens.transfer_view_model import TransferViewModel

logger = logging.getLogger(__name__)


class TransferController:
    """Side-effect boundary for the transfer dialog.

    Holds references to the facade and the view model. Methods that
    touch the engine (queries + command emission) live here.
    """

    def __init__(self, facade, view_model: "TransferViewModel") -> None:
        self.facade = facade
        self.view_model = view_model

    # ------------------------------------------------------------------
    # Facade queries — sources/targets at the hex
    # ------------------------------------------------------------------

    def collect_sources_and_targets(
            self, source_fleet, hex_coord) -> List[dict]:
        """Find fleets and planets at ``hex_coord`` (or the fleet's
        projected position if no planets at the primary hex), build
        the available-sources list, and return it.

        The returned list is a list of ``{label, type, id}`` dicts.
        ``source_fleet`` is always included even if the facade
        doesn't list it at the hex.
        """
        fleets = list(self.facade.fleets.at_hex(hex_coord))
        planets = list(self.facade.planets.at_hex(hex_coord))

        # If no planets at primary hex, check fleet's projected
        # position (queued MOVE/WARP orders).
        if not planets and source_fleet is not None:
            from game.strategy.services.cargo_transfer_service import (
                project_fleet_position,
            )
            projected = project_fleet_position(source_fleet)
            if projected != hex_coord:
                planets = list(self.facade.planets.at_hex(projected))

        sources: List[dict] = []

        if source_fleet is not None:
            fleet_in_list = any(
                getattr(f, "fleet_id", None) == source_fleet.id for f in fleets
            )
            if not fleet_in_list:
                sources.append({
                    "label": source_fleet.name,
                    "type": "fleet",
                    "id": source_fleet.id,
                })

        for f in fleets:
            sources.append({
                "label": f.name,
                "type": "fleet",
                "id": f.fleet_id,
            })

        for p in planets:
            if p.owner_id is not None:
                sources.append({
                    "label": f"Colony: {p.name}",
                    "type": "colony",
                    "id": p.planet_id,
                })
            else:
                sources.append({
                    "label": f"Planet: {p.name}",
                    "type": "planet",
                    "id": p.planet_id,
                })

        # PROJ-437 Phase 1b: attach the per-entity Container snapshots so
        # downstream phases (view-model row data, mass-remaining preview,
        # mixed-content display) can read storage state through the
        # unified Container API without re-querying the facade. Field is
        # additive — existing consumers that only read `label`/`type`/`id`
        # are unaffected.
        for entry in sources:
            if entry["type"] == "fleet":
                entry["containers"] = self.facade.fleets.get_containers(entry["id"])
            else:
                entry["containers"] = self.facade.planets.get_containers(entry["id"])

        return sources

    def discover_pod_designs(self, scene) -> List[str]:
        """Discover all pod-type design names from the per-empire catalog.

        PROJ-427 Phase 6: was ``DesignLibrary.filter_designs(...)``; now
        reads the per-empire ``DesignCatalog``. PROJ-475: routed through
        ``facade.facade_state.get_design_catalog_for_empire`` anchored on
        ``viewing_empire_id`` (the canonical "whose data" anchor — decisions.md),
        off the direct ``scene.session`` read. Returns a sorted list of design
        names with ``vehicle_type=='Drop Pod'``. Falls back to ``[]`` on any
        error so the dialog still opens.
        """
        try:
            empire_id = scene.viewing_empire_id
            if empire_id is None:
                empire_id = 0
            catalog = scene.facade.facade_state.get_design_catalog_for_empire(
                empire_id
            )
            if catalog is None:
                return []
            pod_designs = [
                m for m in catalog.list_designs() if m.vehicle_type == "Drop Pod"
            ]
            return sorted({d.name for d in pod_designs})
        except Exception:  # Intentional broad catch: catalog lookup must not block the transfer dialog from opening
            logger.debug(
                "Could not discover pod designs, falling back to empty list",
            )
            return []

    # ------------------------------------------------------------------
    # Source/target object resolution (DTOs from the facade)
    # ------------------------------------------------------------------

    def fetch_dto(self, entry: Optional[dict]) -> Optional[Any]:
        """Resolve an ``available_sources`` / ``available_targets``
        entry into a FleetInfo / PlanetInfo DTO via the facade.

        Returns ``None`` if entry is ``None``.
        """
        if entry is None:
            return None
        if entry["type"] == "fleet":
            return self.facade.fleets.get(entry["id"])
        return self.facade.planets.get(entry["id"])

    # ------------------------------------------------------------------
    # Command emission
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_cargo_key(cargo_key: str) -> Tuple[str, Optional[str]]:
        """Parse a cargo_key into ``(cargo_type, species_id)``.

        Conventions:

        * ``"drop_pod:<pod_name>"`` → ``("drop_pod", pod_name)``
        * ``"passengers"`` → ``("passengers", None)``
        * ``"passengers_<race_id>"`` → ``("passengers", race_id)``
        * Anything else → ``(cargo_key, None)``
        """
        if cargo_key.startswith("drop_pod:"):
            return "drop_pod", cargo_key[len("drop_pod:"):]
        if cargo_key.startswith("vehicle:"):
            return "vehicle", cargo_key[len("vehicle:"):]
        if cargo_key.startswith("passengers_"):
            return "passengers", cargo_key[len("passengers_"):]
        if cargo_key == "passengers":
            return "passengers", None
        return cargo_key, None

    def _resolve_endpoints(
            self, source: dict, target: dict,
    ) -> Optional[Tuple[Optional[int], Optional[int], Optional[int], bool, bool]]:
        """Compute ``(fleet_id, planet_id, target_fleet_id,
        source_is_fleet, target_is_fleet)``.

        Returns ``None`` when neither side is a fleet (transfer
        between two non-fleet entities is unsupported).
        """
        source_is_fleet = source["type"] == "fleet"
        target_is_fleet = target["type"] == "fleet"

        if source_is_fleet and not target_is_fleet:
            return source["id"], target["id"], None, True, False
        if not source_is_fleet and target_is_fleet:
            return target["id"], source["id"], None, False, True
        if source_is_fleet and target_is_fleet:
            return source["id"], None, target["id"], True, True
        return None

    def _direction(self, amount: Any, source_is_fleet: bool,
                   target_is_fleet: bool) -> str:
        """Direction (commands are fleet-centric).

        * source_is_fleet, positive amount = "load" (target → fleet).
        * target_is_fleet, positive amount = "unload" (fleet → target).
        * Both fleets, positive = "load" by convention.
        """
        if source_is_fleet:
            return "load" if amount > 0 else "unload"
        if target_is_fleet:
            return "unload" if amount > 0 else "load"
        return "load" if amount > 0 else "unload"

    def confirm_pending(self) -> ConfirmResult:
        """Issue an ``IssueTransferCommand`` for each non-zero pending entry.

        Returns a :class:`ConfirmResult` so the dialog can distinguish
        "validation abort — keep dialog open for correction" from
        "successful issue or catastrophic dispatch — close dialog".

        Aborts with ``aborted_for_correction=True`` (no commands issued)
        when:

        * No current source or target.
        * Both endpoints are non-fleet (planets/colonies cannot
          transfer to each other directly).
        * All pending entries are zero.

        PROJ-343 T1.4: prior return type was plain int and `_on_confirm`
        used always-kill `try/finally`, killing the dialog even on
        validation aborts and breaking pre-refactor UX.
        """
        vm = self.view_model
        source = vm.current_source
        target = vm.current_target

        logger.info(
            "TransferDialog._on_confirm: source=%s target=%s pending=%s",
            source, target, dict(vm.pending_transfers),
        )

        if source is None or target is None:
            logger.warning(
                "TransferDialog._on_confirm: No source or target, aborting",
            )
            return ConfirmResult(orders_issued=0, aborted_for_correction=True)

        endpoints = self._resolve_endpoints(source, target)
        if endpoints is None:
            logger.info(
                "Transfer between two non-fleet entities not supported.",
            )
            return ConfirmResult(orders_issued=0, aborted_for_correction=True)
        fleet_id, planet_id, target_fleet_id, source_is_fleet, target_is_fleet = endpoints

        orders_issued = 0
        first_rejection: Optional[str] = None
        for cargo_key, amount in vm.pending_transfers.items():
            if amount == 0:
                logger.debug(
                    "TransferDialog: Skipping %s (amount=0)", cargo_key,
                )
                continue

            cargo_type, species_id = self._parse_cargo_key(cargo_key)
            is_max = amount in (vm.MAX_LOAD, vm.MAX_DROP)
            direction = self._direction(amount, source_is_fleet, target_is_fleet)
            transfer_amount = 0 if is_max else int(abs(amount))

            logger.info(
                "TransferDialog: Issuing command: fleet=%s planet=%s "
                "cargo=%s dir=%s amt=%s species=%s target_fleet=%s",
                fleet_id, planet_id, cargo_type, direction,
                transfer_amount, species_id, target_fleet_id,
            )

            cmd = IssueTransferCommand(
                fleet_id=fleet_id,
                planet_id=planet_id,
                cargo_type=cargo_type,
                direction=direction,
                amount=transfer_amount,
                species_id=species_id,
                target_fleet_id=target_fleet_id,
            )

            result = self.facade.handle_command(cmd)
            if result.is_valid:
                orders_issued += 1
                logger.info(
                    "TransferDialog: Command accepted for %s", cargo_type,
                )
            else:
                logger.warning(
                    "TransferDialog: Command REJECTED for %s: %s",
                    cargo_type, result.message,
                )
                # QA Obs 5 follow-up (2026-05-16): capture the first
                # rejection message so the dialog can surface it when
                # every command was rejected. Without this the user sees
                # a no-op button and the only feedback is in the log.
                if first_rejection is None:
                    first_rejection = getattr(result, "message", None)

        if orders_issued > 0:
            logger.info(
                "TransferDialog: %d transfer order(s) issued.", orders_issued,
            )
            return ConfirmResult(orders_issued=orders_issued, aborted_for_correction=False)

        # All pending were zero (or facade rejected every command).
        # Treat zero-pending as user-correctable; if every command was
        # rejected by the facade, ALSO surface as correctable so the user
        # can see the issue and adjust rather than having the dialog vanish.
        logger.warning(
            "TransferDialog: No orders issued (pending had %d entries)",
            len(vm.pending_transfers),
        )
        return ConfirmResult(
            orders_issued=0,
            aborted_for_correction=True,
            rejection_message=first_rejection,
        )


__all__ = ["ConfirmResult", "TransferController"]
