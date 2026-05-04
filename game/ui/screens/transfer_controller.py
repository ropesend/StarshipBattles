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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from game.strategy.engine.commands import IssueTransferCommand

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
        fleets = list(self.facade.get_fleets_at_hex(hex_coord))
        planets = list(self.facade.get_planets_at_hex(hex_coord))

        # If no planets at primary hex, check fleet's projected
        # position (queued MOVE/WARP orders).
        if not planets and source_fleet is not None:
            from game.strategy.services.cargo_transfer_service import (
                project_fleet_position,
            )
            projected = project_fleet_position(source_fleet)
            if projected != hex_coord:
                planets = list(self.facade.get_planets_at_hex(projected))

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

        return sources

    def discover_pod_designs(self, scene) -> List[str]:
        """Discover all pod-type design names from the design
        library. Returns a sorted list of design names with
        vehicle_type=='Drop Pod'. Falls back to ``[]`` on any I/O
        or schema error so the dialog still opens."""
        try:
            from game.strategy.systems.design_library import DesignLibrary
            session = scene.session
            empire = getattr(session, "active_empire", None)
            empire_id = empire.id if empire else 0
            library = DesignLibrary(session.save_path, empire_id)
            pod_designs = library.filter_designs(vehicle_type="Drop Pod")
            return sorted({d.name for d in pod_designs})
        except Exception:  # Intentional broad catch: DesignLibrary load surfaces I/O, JSON, and schema-validation errors; transfer dialog falls back to empty pod list
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
            return self.facade.get_fleet(entry["id"])
        return self.facade.get_planet(entry["id"])

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

    def confirm_pending(self) -> int:
        """Issue an ``IssueTransferCommand`` for each non-zero
        pending entry. Returns the number of orders successfully
        accepted by the facade.

        Aborts (returns 0, no commands issued) when:

        * No current source or target.
        * Both endpoints are non-fleet (planets/colonies cannot
          transfer to each other directly).
        * All pending entries are zero.
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
            return 0

        endpoints = self._resolve_endpoints(source, target)
        if endpoints is None:
            logger.info(
                "Transfer between two non-fleet entities not supported.",
            )
            return 0
        fleet_id, planet_id, target_fleet_id, source_is_fleet, target_is_fleet = endpoints

        orders_issued = 0
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

        if orders_issued > 0:
            logger.info(
                "TransferDialog: %d transfer order(s) issued.", orders_issued,
            )
        else:
            logger.warning(
                "TransferDialog: No orders issued (pending had %d entries)",
                len(vm.pending_transfers),
            )
        return orders_issued


__all__ = ["TransferController"]
