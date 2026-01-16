"""
Fleet movement operations for strategy scene.
Handles move, join, and intercept commands.

Extracted from StrategyScene to reduce file size and improve testability.
"""
import pygame
from game.core.logger import log_debug, log_warning
from game.strategy.data.fleet import FleetOrder, OrderType
from game.strategy.data.hex_math import pixel_to_hex


class FleetOperations:
    """Handles fleet movement commands."""

    def __init__(self, scene):
        """
        Initialize fleet operations handler.

        Args:
            scene: StrategyScene instance providing camera, empires, session, etc.
        """
        self.scene = scene

    @property
    def camera(self):
        return self.scene.camera

    @property
    def empires(self):
        return self.scene.empires

    @property
    def HEX_SIZE(self):
        return self.scene.HEX_SIZE

    @property
    def session(self):
        return self.scene.session

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

        world_pos = self.camera.screen_to_world((mx, my))
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.HEX_SIZE)

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
        log_debug(f"Calculating path to {target_hex}...")

        preview_path = self.session.preview_fleet_path(fleet, target_hex)

        if preview_path:
            log_debug(f"Path confirmed: {len(preview_path)} steps.")

            from game.strategy.engine.commands import IssueMoveCommand
            cmd = IssueMoveCommand(fleet.id, target_hex)

            result = self.session.handle_command(cmd)

            if result and result.is_valid:
                return {'type': 'success', 'fleet': fleet}
            else:
                msg = result.message if result else 'Unknown'
                log_warning(f"Move Failed: {msg}")
                return {'type': 'error', 'message': msg}
        else:
            log_warning("Cannot find path to target (Unreachable).")
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
        log_debug(f"Intercepting Fleet {target_fleet.id}...")

        new_order = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
        fleet.add_order(new_order)

        return {'type': 'success', 'fleet': fleet}

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
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.HEX_SIZE)

        target_fleet = self.get_fleet_at_hex(target_hex)

        if not target_fleet:
            log_debug("No fleet at target location.")
            return None

        if target_fleet == selected_fleet:
            log_debug("Cannot join self.")
            return None

        if target_fleet.owner_id != selected_fleet.owner_id:
            log_debug("Cannot join enemy fleet.")
            return None

        log_debug(f"Queueing Join Order with Fleet {target_fleet.id}...")

        # 1. Move Towards
        order_move = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
        selected_fleet.add_order(order_move)

        # 2. Join
        order_join = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        selected_fleet.add_order(order_join)

        return {'type': 'success', 'fleet': selected_fleet}
