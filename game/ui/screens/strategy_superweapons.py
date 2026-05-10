"""
Superweapon operations workflow for strategy scene.
Handles Planet Imploder, Stellerator, Warp Point manipulation, Dyson Sphere, and Self-Destruct.

Extracted following ColonizationSystem pattern for consistency.

Cross-layer imports (acceptable for UI):
- Camera.hex_at_screen: Runtime - coordinate conversion for command targeting
- QueueImplodePlanetMissionCommand, etc.: Runtime - UI issues commands
- StrategySessionFacade: TYPE_CHECKING - used for type hints only
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Any
import logging

logger = logging.getLogger(__name__)
from game.strategy.engine.commands import (
    IssueSelfDestructCommand,
    QueueImplodePlanetMissionCommand,
    QueueStellerateStarMissionCommand,
    QueueOpenWarpPointMissionCommand,
    QueueCloseWarpPointMissionCommand,
    QueueCreateDysonSphereMissionCommand,
)

if TYPE_CHECKING:
    from game.strategy.facade.strategy_session_facade import StrategySessionFacade
    from game.strategy.data.fleet import Fleet


def _check_fleet_ability(
    fleet: 'Fleet', ability_name: str, error_msg: str
) -> Optional[dict]:
    """Validate fleet has ``ability_name``; return an error dict or ``None`` on success.

    Shared validator for the 5 superweapon designation handlers (PROJ-380,
    DUP-X-08). Logs a warning at the call site and returns the standard
    ``{'type': 'error', 'message': ...}`` shape so callers can ``return``
    the result directly when the check fails.

    Args:
        fleet: Fleet to validate.
        ability_name: Capability ability name (e.g. ``"DestroyPlanet"``).
        error_msg: Human-readable message used both for the warning log
            and the returned error dict.

    Returns:
        ``None`` when the fleet has the ability; otherwise an error dict
        with ``type='error'`` and ``message=error_msg``.
    """
    if not fleet.capabilities.has_ability(ability_name):
        logger.warning(error_msg + ".")
        return {'type': 'error', 'message': error_msg}
    return None


class SuperweaponOperations:
    """Handles superweapon commands and workflows."""

    def __init__(self, scene, facade: 'StrategySessionFacade'):
        """
        Initialize superweapon operations.

        Args:
            scene: StrategyScreen instance providing camera, systems, hex_size, etc.
            facade: StrategySessionFacade for all engine interactions
        """
        self.scene = scene
        self.facade = facade

    @property
    def systems(self) -> Any:
        return self.scene.systems

    @property
    def camera(self) -> Any:
        return self.scene.camera

    @property
    def hex_size(self) -> Any:
        return self.scene.hex_size

    @property
    def galaxy(self) -> Any:
        return self.scene.galaxy

    def handle_implode_planet_designation(self, mx: int, my: int, fleet: 'Fleet') -> Optional[dict]:
        """
        Handle selecting a planet to implode.

        Args:
            mx, my: Mouse screen coordinates
            fleet: Fleet to issue mission to

        Returns:
            dict with result type, or None if invalid
        """
        if not fleet:
            return None

        err = _check_fleet_ability(fleet, "DestroyPlanet", "Fleet has no Planet Imploder component")
        if err is not None:
            return err

        target_hex = self.camera.hex_at_screen(mx, my, self.hex_size)

        # Find planets at hex
        planets = self.galaxy.get_planets_at_global_hex(target_hex)
        if not planets:
            logger.debug("No planet at target location.")
            return {'type': 'error', 'message': 'No planet at target location'}

        if len(planets) == 1:
            return self._queue_implode_planet(fleet, target_hex, planets[0])
        else:
            # Multiple planets - prompt selection
            def on_selected(planet) -> None:
                self._queue_implode_planet(fleet, target_hex, planet)

            self.scene.ui.prompt_planet_selection(planets, on_selected)
            return {'type': 'prompt', 'planets': planets}

    def _queue_implode_planet(self, fleet: 'Fleet', target_hex, planet) -> dict:
        """Queue implode planet mission with confirmation."""
        def on_confirm() -> None:
            cmd = QueueImplodePlanetMissionCommand(fleet.id, target_hex, planet.id)
            result = self.facade.handle_command(cmd)
            if result.is_valid:
                logger.info(f"Mission Queued: Implode Planet {planet.name}")
                self.scene.on_ui_selection(fleet)
            else:
                logger.warning(f"Implode planet mission failed: {result.message}")

        self._show_confirmation(
            "Destroy Planet",
            f"Destroy {planet.name}? This action is irreversible.\nThe Planet Imploder will be consumed.",
            on_confirm
        )
        return {'type': 'success'}

    def handle_stellerate_star_designation(self, mx: int, my: int, fleet: 'Fleet') -> Optional[dict]:
        """
        Handle selecting a star system to stellerate.

        Args:
            mx, my: Mouse screen coordinates
            fleet: Fleet to issue mission to

        Returns:
            dict with result type, or None if invalid
        """
        if not fleet:
            return None

        err = _check_fleet_ability(fleet, "DestroyStar", "Fleet has no Stellerator component")
        if err is not None:
            return err

        target_hex = self.camera.hex_at_screen(mx, my, self.hex_size)

        # Find system at hex
        system = self._get_system_at_hex(target_hex)
        if not system:
            logger.debug("No star system at target location.")
            return {'type': 'error', 'message': 'No star system at target location'}

        def on_confirm() -> None:
            cmd = QueueStellerateStarMissionCommand(fleet.id, target_hex)
            result = self.facade.handle_command(cmd)
            if result.is_valid:
                logger.info(f"Mission Queued: Stellerate {system.name}")
                self.scene.on_ui_selection(fleet)
            else:
                logger.warning(f"Stellerate mission failed: {result.message}")

        self._show_confirmation(
            "STELLERATE STAR",
            f"This will destroy {system.name}'s star, ALL planets, and ALL ships in the system - "
            f"INCLUDING YOUR FLEET.\n\nThis action is irreversible.\n\nProceed?",
            on_confirm,
            is_warning=True
        )
        return {'type': 'success'}

    def handle_open_warp_designation(self, mx: int, my: int, fleet: 'Fleet') -> Optional[dict]:
        """
        Handle selecting a hex for warp point creation.

        Args:
            mx, my: Mouse screen coordinates
            fleet: Fleet to issue mission to

        Returns:
            dict with result type, or None if invalid
        """
        if not fleet:
            return None

        err = _check_fleet_ability(fleet, "OpenWarpPoint", "Fleet has no Quantum Tunneling Inducer component")
        if err is not None:
            return err

        target_hex = self.camera.hex_at_screen(mx, my, self.hex_size)

        # Get current system for filtering
        current_system = self._get_system_at_hex(target_hex)
        if not current_system:
            logger.debug("No star system at target location.")
            return {'type': 'error', 'message': 'No star system at target location'}

        # Get all systems for selection
        all_systems = list(self.galaxy.systems.values())

        # Filter: exclude current system and systems already linked
        linked_system_names = {wp.destination_id for wp in current_system.warp_points}
        linked_system_names.add(current_system.name)

        available_systems = [
            s for s in all_systems
            if s.name not in linked_system_names
        ]

        if not available_systems:
            logger.debug("No available systems to link to.")
            return {'type': 'error', 'message': 'No available systems to link to'}

        def on_system_selected(system_name: str) -> None:
            cmd = QueueOpenWarpPointMissionCommand(fleet.id, target_hex, system_name)
            result = self.facade.handle_command(cmd)
            if result.is_valid:
                logger.info(f"Mission Queued: Open Warp Point to {system_name}")
                self.scene.on_ui_selection(fleet)
            else:
                logger.warning(f"Open warp point mission failed: {result.message}")

        self._show_system_picker(available_systems, current_system, on_system_selected)
        return {'type': 'prompt'}

    def handle_close_warp_designation(self, mx: int, my: int, fleet: 'Fleet') -> Optional[dict]:
        """
        Handle selecting a warp point to close.

        Args:
            mx, my: Mouse screen coordinates
            fleet: Fleet to issue mission to

        Returns:
            dict with result type, or None if invalid
        """
        if not fleet:
            return None

        err = _check_fleet_ability(fleet, "CloseWarpPoint", "Fleet has no Quantum Tunneling Disruptor component")
        if err is not None:
            return err

        target_hex = self.camera.hex_at_screen(mx, my, self.hex_size)

        # Find warp point at hex
        warp_point = self._get_warp_point_at_hex(target_hex)
        if not warp_point:
            logger.debug("No warp point at target location.")
            return {'type': 'error', 'message': 'No warp point at target location'}

        def on_confirm() -> None:
            cmd = QueueCloseWarpPointMissionCommand(fleet.id, target_hex, warp_point.destination_id)
            result = self.facade.handle_command(cmd)
            if result.is_valid:
                logger.info(f"Mission Queued: Close Warp Point to {warp_point.destination_id}")
                self.scene.on_ui_selection(fleet)
            else:
                logger.warning(f"Close warp point mission failed: {result.message}")

        self._show_confirmation(
            "Close Warp Point",
            f"Close warp link to {warp_point.destination_id}?\n\nBoth ends will be destroyed.",
            on_confirm
        )
        return {'type': 'success'}

    def handle_dyson_sphere_designation(self, mx: int, my: int, fleet: 'Fleet') -> Optional[dict]:
        """
        Handle selecting a star system for Dyson Sphere creation.

        Args:
            mx, my: Mouse screen coordinates
            fleet: Fleet to issue mission to

        Returns:
            dict with result type, or None if invalid
        """
        if not fleet:
            return None

        err = _check_fleet_ability(fleet, "CreateDysonSphere", "Fleet has no Dyson Sphere Constructor component")
        if err is not None:
            return err

        target_hex = self.camera.hex_at_screen(mx, my, self.hex_size)

        # Find system at hex
        system = self._get_system_at_hex(target_hex)
        if not system:
            logger.debug("No star system at target location.")
            return {'type': 'error', 'message': 'No star system at target location'}

        def on_confirm() -> None:
            cmd = QueueCreateDysonSphereMissionCommand(fleet.id, target_hex)
            result = self.facade.handle_command(cmd)
            if result.is_valid:
                logger.info(f"Mission Queued: Create Dyson Sphere at {system.name}")
                self.scene.on_ui_selection(fleet)
            else:
                logger.warning(f"Dyson Sphere mission failed: {result.message}")

        self._show_confirmation(
            "Create Dyson Sphere",
            f"Create Dyson Sphere at {system.name}?\n\n"
            f"The star and all planets within 9 hexes will be consumed.\n"
            f"A colonizable Dyson Sphere will be created.",
            on_confirm
        )
        return {'type': 'success'}

    def handle_self_destruct(self, fleet: 'Fleet') -> Optional[dict]:
        """
        Handle self-destruct command - show ship picker for ships with SelfDestruct ability.

        Args:
            fleet: Fleet to select ships from

        Returns:
            dict with result type, or None if invalid
        """
        if not fleet:
            return None

        # Get ships with SelfDestruct ability
        ships = fleet.capabilities.ships_with_ability("SelfDestruct")
        if not ships:
            logger.warning("No ships with Self-Destruct Device in fleet.")
            return {'type': 'error', 'message': 'No ships with Self-Destruct Device in fleet'}

        def on_ships_selected(ship_ids: List[int]) -> None:
            if not ship_ids:
                return
            cmd = IssueSelfDestructCommand(fleet.id, ship_ids)
            result = self.facade.handle_command(cmd)
            if result.is_valid:
                logger.info(f"Self-destruct ordered for {len(ship_ids)} ships")
                self.scene.on_ui_selection(fleet)
            else:
                logger.warning(f"Self-destruct failed: {result.message}")

        self._show_ship_picker(ships, "SelfDestruct", on_ships_selected)
        return {'type': 'prompt'}

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _get_system_at_hex(self, hex_coord) -> Any:
        """Find system at hex coordinate."""
        from game.strategy.data.pathfinding import get_system_at_hex
        return get_system_at_hex(self.galaxy, hex_coord)

    def _get_warp_point_at_hex(self, hex_coord) -> Any:
        """Find warp point at the given global hex coordinate."""
        system = self._get_system_at_hex(hex_coord)
        if not system:
            return None

        local_hex = hex_coord - system.global_location
        for wp in system.warp_points:
            if wp.location == local_hex:
                return wp
        return None

    def _show_confirmation(self, title: str, message: str, on_confirm, is_warning: bool = False) -> None:
        """
        Show a confirmation dialog.

        Args:
            title: Dialog title
            message: Message to display
            on_confirm: Callback when user confirms
            is_warning: If True, use warning styling (for dangerous actions)
        """
        # PROJ-198: Direct call - show_confirmation_dialog is always available
        self.scene.ui.show_confirmation_dialog(title, message, on_confirm, is_warning=is_warning)

    def _show_system_picker(self, systems, current_system, on_selected) -> None:
        """
        Show system picker dialog for Open Warp Point.

        Args:
            systems: List of available systems to pick from
            current_system: The current system (for distance calculation)
            on_selected: Callback with selected system name
        """
        # PROJ-198: Direct call - show_system_picker is always available
        self.scene.ui.show_system_picker(systems, current_system, on_selected)

    def _show_ship_picker(self, ships, ability_name: str, on_selected) -> None:
        """
        Show ship picker dialog for multi-select.

        Args:
            ships: List of ships to pick from
            ability_name: Ability name (for display)
            on_selected: Callback with list of selected ship IDs
        """
        # PROJ-198: Direct call - show_ship_picker is always available
        self.scene.ui.show_ship_picker(ships, ability_name, on_selected)
