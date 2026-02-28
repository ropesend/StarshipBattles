"""
Fleet movement operations for strategy scene.
Handles move, join, and intercept commands.

Extracted from StrategyScreen to reduce file size and improve testability.

Cross-layer imports (acceptable for UI):
- pixel_to_hex: Runtime - coordinate conversion for command targeting
- IssueMoveCommand, IssueInterceptCommand, IssueJoinFleetCommand: Runtime (local) - UI issues commands
- StrategySessionFacade: TYPE_CHECKING - used for type hints only
"""
import logging
from typing import TYPE_CHECKING
from game.core.hex_math import pixel_to_hex
from game.strategy.engine.commands import IssueMoveCommand, IssueInterceptCommand, IssueJoinFleetCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.facade.strategy_session_facade import StrategySessionFacade


class FleetOperations:
    """Handles fleet movement commands."""

    def __init__(self, scene, facade: 'StrategySessionFacade'):
        """
        Initialize fleet operations handler.

        Args:
            scene: StrategyScreen instance providing camera, empires, hex_size, etc.
            facade: StrategySessionFacade for all engine interactions
        """
        self.scene = scene
        self.facade = facade

    @property
    def camera(self):
        return self.scene.camera

    @property
    def empires(self):
        return self.scene.empires

    @property
    def hex_size(self):
        return self.scene.hex_size

    def get_fleet_at_hex(self, hex_coord):
        """
        Find the first fleet at the given hex.

        Args:
            hex_coord: HexCoord to search

        Returns:
            Fleet object or None if no fleet at location
        """
        for emp in self.empires:
            for f in emp.fleets:
                if f.location == hex_coord:
                    return f
        return None

    def handle_move_designation(self, mx, my, selected_fleet):
        """
        Handle designating a move target.

        Args:
            mx, my: Mouse screen coordinates
            selected_fleet: The fleet to move

        Returns:
            dict with result type:
            - {'type': 'choice', 'target_fleet': Fleet, 'target_hex': HexCoord} for fleet at target
            - {'type': 'success', 'fleet': Fleet} on successful move
            - {'type': 'error', 'message': str} on failure
            - None if no fleet selected
        """
        if not selected_fleet:
            return None

        # PROJ-67: Block movement while fleet is building
        if selected_fleet.is_building:
            logger.warning("Fleet is building - cancel BUILD order first to move.")
            return {'type': 'error', 'message': 'Fleet is building - cancel BUILD order first'}

        world_pos = self.camera.screen_to_world((mx, my))
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.hex_size)

        target_fleet = self.get_fleet_at_hex(target_hex)

        if target_fleet and target_fleet != selected_fleet:
            # Return choice context for UI prompt
            return {
                'type': 'choice',
                'target_fleet': target_fleet,
                'target_hex': target_hex,
            }
        else:
            return self.execute_move(selected_fleet, target_hex)

    def execute_move(self, fleet, target_hex):
        """
        Execute standard move command.

        Args:
            fleet: Fleet to move
            target_hex: Destination HexCoord

        Returns:
            dict with result type and details
        """
        logger.debug(f"Calculating path to {target_hex}...")

        preview_path = self.facade.get_fleet_path_preview(fleet.id, target_hex)

        if preview_path:
            logger.debug(f"Path confirmed: {len(preview_path)} steps.")

            cmd = IssueMoveCommand(fleet.id, target_hex)

            result = self.facade.handle_command(cmd)

            if result and result.is_valid:
                return {'type': 'success', 'fleet': fleet}
            else:
                msg = result.message if result else 'Unknown'
                logger.warning(f"Move Failed: {msg}")
                return {'type': 'error', 'message': msg}
        else:
            logger.warning("Cannot find path to target (Unreachable).")
            return {'type': 'error', 'message': 'Unreachable'}

    def execute_intercept(self, fleet, target_fleet):
        """
        Execute intercept order.

        Args:
            fleet: Fleet to issue order to
            target_fleet: Fleet to intercept

        Returns:
            dict with result type and details
        """
        logger.debug(f"Intercepting Fleet {target_fleet.id}...")

        cmd = IssueInterceptCommand(fleet.id, target_fleet.id)
        result = self.facade.handle_command(cmd)

        if result and result.is_valid:
            return {'type': 'success', 'fleet': fleet}
        else:
            msg = result.message if result else 'Unknown'
            logger.warning(f"Intercept Failed: {msg}")
            return {'type': 'error', 'message': msg}

    def handle_join_designation(self, mx, my, selected_fleet):
        """
        Handle designating a fleet to join.

        Args:
            mx, my: Mouse screen coordinates
            selected_fleet: The fleet that will join another

        Returns:
            dict with result type, or None if invalid
        """
        if not selected_fleet:
            return None

        world_pos = self.camera.screen_to_world((mx, my))
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.hex_size)

        target_fleet = self.get_fleet_at_hex(target_hex)

        if not target_fleet:
            logger.debug("No fleet at target location.")
            return None

        if target_fleet == selected_fleet:
            logger.debug("Cannot join self.")
            return None

        if target_fleet.owner_id != selected_fleet.owner_id:
            logger.debug("Cannot join enemy fleet.")
            return None

        logger.debug(f"Queueing Join Order with Fleet {target_fleet.id}...")

        cmd = IssueJoinFleetCommand(selected_fleet.id, target_fleet.id)
        result = self.facade.handle_command(cmd)

        if result and result.is_valid:
            return {'type': 'success', 'fleet': selected_fleet}
        else:
            msg = result.message if result else 'Unknown'
            logger.warning(f"Join Fleet Failed: {msg}")
            return {'type': 'error', 'message': msg}
