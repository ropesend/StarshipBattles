"""
Tests for StrategySessionFacade grouped command-dispatch surface.

PROJ-264 Phase 3 originally covered each top-level ``dispatch_*`` helper.
PROJ-430 / TD-08 deleted that top-level surface; the same wiring is now
reached through ``facade.commands.<verb>(...)`` (prefix stripped). The
parametrized cases below verify each verb instantiates the correct
Command dataclass and routes through ``handle_command``.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult


# =============================================================================
# Fixture
# =============================================================================

@pytest.fixture
def facade():
    """Create a StrategySessionFacade with mocked session and handle_command."""
    from game.strategy.facade.strategy_session_facade import StrategySessionFacade

    session = MagicMock()
    f = StrategySessionFacade(session)
    f.handle_command = MagicMock(return_value=ValidationResult.success())
    return f


# =============================================================================
# Dispatch Method Tests (parametrized)
# =============================================================================

# Each entry: (method_name, kwargs_to_pass, expected_command_class_name)
DISPATCH_CASES = [
    ("dispatch_issue_colonize", {"fleet_id": 1}, "IssueColonizeCommand"),
    ("dispatch_issue_move", {"fleet_id": 1, "target_hex": HexCoord(0, 0)}, "IssueMoveCommand"),
    ("dispatch_issue_intercept", {"fleet_id": 1, "target_fleet_id": 2}, "IssueInterceptCommand"),
    ("dispatch_issue_join_fleet", {"fleet_id": 1, "target_fleet_id": 2}, "IssueJoinFleetCommand"),
    ("dispatch_queue_colonize_mission", {"fleet_id": 1, "target_hex": HexCoord(0, 0), "planet_id": 10}, "QueueColonizeMissionCommand"),
    ("dispatch_clear_orders", {"fleet_id": 1}, "ClearOrdersCommand"),
    ("dispatch_issue_transfer", {"fleet_id": 1, "planet_id": 10, "direction": "load", "cargo_type": "passengers", "amount": 50}, "IssueTransferCommand"),
    ("dispatch_issue_implode_planet", {"fleet_id": 1, "planet_id": 10}, "IssueImplodePlanetCommand"),
    ("dispatch_issue_stellerate_star", {"fleet_id": 1}, "IssueStellerateStarCommand"),
    ("dispatch_issue_open_warp_point", {"fleet_id": 1, "target_hex": HexCoord(5, 5), "target_system_name": "Alpha"}, "IssueOpenWarpPointCommand"),
    ("dispatch_issue_close_warp_point", {"fleet_id": 1, "warp_point_destination_id": "sys2"}, "IssueCloseWarpPointCommand"),
    ("dispatch_issue_create_dyson_sphere", {"fleet_id": 1}, "IssueCreateDysonSphereCommand"),
    ("dispatch_issue_self_destruct", {"fleet_id": 1, "ship_ids": [1]}, "IssueSelfDestructCommand"),
    ("dispatch_queue_implode_planet_mission", {"fleet_id": 1, "target_hex": HexCoord(0, 0), "planet_id": 10}, "QueueImplodePlanetMissionCommand"),
    ("dispatch_queue_stellerate_star_mission", {"fleet_id": 1, "target_hex": HexCoord(0, 0)}, "QueueStellerateStarMissionCommand"),
    ("dispatch_queue_open_warp_point_mission", {"fleet_id": 1, "target_hex": HexCoord(0, 0), "target_system_name": "Beta"}, "QueueOpenWarpPointMissionCommand"),
    ("dispatch_queue_close_warp_point_mission", {"fleet_id": 1, "target_hex": HexCoord(0, 0), "warp_point_destination_id": "sys3"}, "QueueCloseWarpPointMissionCommand"),
    ("dispatch_queue_create_dyson_sphere_mission", {"fleet_id": 1, "target_hex": HexCoord(0, 0)}, "QueueCreateDysonSphereMissionCommand"),
    ("dispatch_issue_warp", {"fleet_id": 1, "warp_point_hex": HexCoord(5, 5)}, "IssueWarpCommand"),
    ("dispatch_issue_build_order", {"fleet_id": 1}, "IssueBuildOrderCommand"),
    ("dispatch_remove_build_order", {"fleet_id": 1}, "RemoveBuildOrderCommand"),
    ("dispatch_split_fleet", {"fleet_id": 1, "ship_instance_ids": ["ship_a", "ship_b"]}, "SplitFleetCommand"),
    ("dispatch_delete_order", {"fleet_id": 1, "order_index": 0}, "DeleteOrderCommand"),
    ("dispatch_reorder_order", {"fleet_id": 1, "order_index": 0, "direction": 1}, "ReorderOrderCommand"),
    ("dispatch_add_to_construction_queue", {"entity_id": 1, "entity_type": "fleet", "design_id": "ship_a", "category": "ship"}, "AddToConstructionQueueCommand"),
    ("dispatch_remove_from_construction_queue", {"entity_id": 1, "entity_type": "fleet", "item_index": 0}, "RemoveFromConstructionQueueCommand"),
    ("dispatch_reorder_construction_queue", {"entity_id": 1, "entity_type": "fleet", "from_index": 0, "to_index": 1}, "ReorderConstructionQueueCommand"),
    ("dispatch_activate_planet_ability", {"planet_id": 100, "facility_instance_id": "fac-1", "ability_name": "shield", "component_key": "OUTER:0:shield"}, "ActivatePlanetAbilityCommand"),
    ("dispatch_deactivate_planet_ability", {"planet_id": 100, "facility_instance_id": "fac-1", "ability_name": "shield", "component_key": "OUTER:0:shield"}, "DeactivatePlanetAbilityCommand"),
    ("dispatch_clear_planet_orders", {"planet_id": 100}, "ClearPlanetOrdersCommand"),
    ("dispatch_delete_planet_order", {"planet_id": 100, "order_index": 0}, "DeletePlanetOrderCommand"),
    ("dispatch_set_atmosphere_target", {"planet_id": 100, "atmosphere_target": {"O2": 0.21}}, "SetAtmosphereTargetCommand"),
]


class TestFacadeDispatch:
    """Verify each dispatch method instantiates the correct command and calls handle_command."""

    @pytest.mark.parametrize("method_name,kwargs,expected_cmd_class", DISPATCH_CASES,
                             ids=[c[0] for c in DISPATCH_CASES])
    def test_dispatch_creates_correct_command(self, facade, method_name, kwargs, expected_cmd_class):
        """Each grouped command verb creates the right Command type and forwards kwargs."""
        # PROJ-430 / TD-08: legacy ``dispatch_<verb>`` reached through
        # ``facade.commands.<verb>`` with the prefix stripped.
        verb = method_name[len("dispatch_"):]
        dispatch_method = getattr(facade.commands, verb)
        result = dispatch_method(**kwargs)

        # handle_command was called once
        facade.handle_command.assert_called_once()

        # The argument was a command of the correct type
        cmd_arg = facade.handle_command.call_args[0][0]
        assert type(cmd_arg).__name__ == expected_cmd_class

        # Result was propagated from handle_command
        assert result.is_valid

    @pytest.mark.parametrize("method_name,kwargs,expected_cmd_class", DISPATCH_CASES,
                             ids=[c[0] for c in DISPATCH_CASES])
    def test_dispatch_propagates_return_value(self, facade, method_name, kwargs, expected_cmd_class):
        """Grouped command verbs return whatever handle_command returns."""
        error_result = ValidationResult.error("test error")
        facade.handle_command.return_value = error_result

        verb = method_name[len("dispatch_"):]
        dispatch_method = getattr(facade.commands, verb)
        result = dispatch_method(**kwargs)

        assert result is error_result
