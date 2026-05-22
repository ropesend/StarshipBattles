"""
Unit tests for SuperweaponOperations class.

Tests initialization, property accessors, and all superweapon command workflows:
- Planet Imploder
- Stellerator
- Open/Close Warp Point
- Dyson Sphere
- Self-Destruct
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_scene():
    """Create mock scene with required attributes."""
    scene = Mock()
    scene.camera = Mock()
    scene.camera.screen_to_world = Mock(return_value=Mock(x=100, y=200))
    # PROJ-380 DUP-X-08: superweapon handlers now call camera.hex_at_screen
    scene.camera.hex_at_screen = Mock(return_value=(5, 5))
    scene.hex_size = 50
    scene.galaxy = Mock()
    scene.ui = Mock()
    scene.on_ui_selection = Mock()
    # PROJ-477 Phase 4: superweapons reads galaxy/systems through scene.world
    # (the live traversal seam). Wire a stub backed by the same mock galaxy so
    # iter_systems / planets_at_exact_hex / system_at_map_hex reflect the data
    # tests configure on ``scene.galaxy``.
    scene.world.iter_systems.side_effect = lambda: iter(
        scene.galaxy.systems.values()
    )
    scene.world.planets_at_exact_hex.side_effect = (
        lambda h: scene.galaxy.get_planets_at_global_hex(h)
    )
    scene.world.system_at_map_hex.side_effect = (
        lambda h, radius=50: scene.galaxy._pathfinder.get_system_at_hex(h, radius)
    )
    return scene


@pytest.fixture
def mock_facade():
    """Create mock facade."""
    facade = Mock()
    facade.handle_command = Mock(return_value=Mock(is_valid=True))
    return facade


@pytest.fixture
def mock_fleet():
    """Create mock fleet with capabilities."""
    fleet = Mock()
    fleet.id = "F-001"
    fleet.owner_id = 0
    fleet.capabilities = Mock()
    fleet.capabilities.has_ability = Mock(return_value=True)
    fleet.capabilities.ships_with_ability = Mock(return_value=[Mock(id=1), Mock(id=2)])
    return fleet


@pytest.fixture
def superweapon_ops(mock_scene, mock_facade):
    """Create SuperweaponOperations instance."""
    from game.ui.screens.strategy_superweapons import SuperweaponOperations
    return SuperweaponOperations(mock_scene, mock_facade)


# =============================================================================
# Initialization Tests
# =============================================================================

class TestSuperweaponOperationsInit:
    """Tests for SuperweaponOperations initialization."""

    def test_init_stores_references(self, mock_scene, mock_facade):
        """Test __init__ stores scene and facade references."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        ops = SuperweaponOperations(mock_scene, mock_facade)

        assert ops.scene is mock_scene
        assert ops.facade is mock_facade


class TestPropertyAccessors:
    """Tests for property accessors.

    PROJ-477 Phase 4: the ``systems`` and ``galaxy`` pass-through properties
    were removed (superweapons now reads through ``scene.world``); only the
    ``camera`` / ``hex_size`` proxies remain.
    """

    def test_camera_property(self, superweapon_ops, mock_scene):
        """Test camera property delegates to scene."""
        result = superweapon_ops.camera

        assert result is mock_scene.camera

    def test_hex_size_property(self, superweapon_ops, mock_scene):
        """Test hex_size property delegates to scene."""
        result = superweapon_ops.hex_size

        assert result == mock_scene.hex_size


# =============================================================================
# Shared no-fleet / fleet-without-ability tests
# =============================================================================

# PROJ-323 Task 3.5 (S10-CAT10-004 / S10-CAT10-005): collapse 5 identical
# no_fleet_returns_none and 5 identical fleet_without_ability_returns_error
# tests across handlers with the same (x, y, fleet) signature.
# SelfDestruct keeps its own per-class tests because handle_self_destruct
# takes only `fleet`.
_HANDLER_DESIGNATIONS = [
    pytest.param(
        "handle_implode_planet_designation", "Planet Imploder", id="planet_imploder",
    ),
    pytest.param(
        "handle_stellerate_star_designation", "Stellerator", id="stellerator",
    ),
    pytest.param(
        "handle_open_warp_designation", "Quantum Tunneling Inducer", id="open_warp",
    ),
    pytest.param(
        "handle_close_warp_designation", "Quantum Tunneling Disruptor", id="close_warp",
    ),
    pytest.param(
        "handle_dyson_sphere_designation", "Dyson Sphere Constructor", id="dyson_sphere",
    ),
]


@pytest.mark.parametrize("handler_name,weapon_label", _HANDLER_DESIGNATIONS)
class TestSuperweaponDesignationCommonChecks:
    """Cross-handler common checks (PROJ-323 Task 3.5)."""

    def test_no_fleet_returns_none(self, superweapon_ops, handler_name, weapon_label):
        """Test with no fleet returns None."""
        result = getattr(superweapon_ops, handler_name)(100, 200, None)
        assert result is None

    def test_fleet_without_ability_returns_error(
        self, superweapon_ops, mock_fleet, handler_name, weapon_label,
    ):
        """Fleet without the relevant ability returns an error mentioning the weapon."""
        mock_fleet.capabilities.has_ability = Mock(return_value=False)

        result = getattr(superweapon_ops, handler_name)(100, 200, mock_fleet)

        assert result['type'] == 'error'
        assert weapon_label in result['message']


# =============================================================================
# Planet Imploder Tests
# =============================================================================

class TestPlanetImploderWorkflow:
    """Tests for Planet Imploder superweapon."""

    def test_no_planet_at_location_returns_error(self, superweapon_ops, mock_fleet):
        """Test no planet at target returns error."""
        superweapon_ops.scene.galaxy.get_planets_at_global_hex = Mock(return_value=[])

        result = superweapon_ops.handle_implode_planet_designation(100, 200, mock_fleet)

        assert result['type'] == 'error'
        assert 'No planet' in result['message']

    def test_single_planet_triggers_confirmation(self, superweapon_ops, mock_fleet, mock_scene):
        """Test single planet triggers confirmation dialog."""
        planet = Mock()
        planet.id = "planet-1"
        planet.name = "Target Planet"
        superweapon_ops.scene.galaxy.get_planets_at_global_hex = Mock(return_value=[planet])
        mock_scene.ui.show_confirmation_dialog = Mock()

        result = superweapon_ops.handle_implode_planet_designation(100, 200, mock_fleet)

        assert result['type'] == 'success'
        mock_scene.ui.show_confirmation_dialog.assert_called_once()

    def test_multiple_planets_prompts_selection(self, superweapon_ops, mock_fleet, mock_scene):
        """Test multiple planets prompts selection."""
        planets = [Mock(id="p1"), Mock(id="p2")]
        superweapon_ops.scene.galaxy.get_planets_at_global_hex = Mock(return_value=planets)
        mock_scene.ui.prompt_planet_selection = Mock()

        result = superweapon_ops.handle_implode_planet_designation(100, 200, mock_fleet)

        assert result['type'] == 'prompt'
        assert result['planets'] == planets
        mock_scene.ui.prompt_planet_selection.assert_called_once()


# =============================================================================
# Stellerator Tests
# =============================================================================

class TestStelleratorWorkflow:
    """Tests for Stellerator superweapon."""

    def test_no_system_at_location_returns_error(self, superweapon_ops, mock_fleet):
        """Test no system at target returns error."""

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=None):
            result = superweapon_ops.handle_stellerate_star_designation(100, 200, mock_fleet)

        assert result['type'] == 'error'
        assert 'No star system' in result['message']

    def test_valid_target_triggers_warning_confirmation(self, superweapon_ops, mock_fleet, mock_scene):
        """Test valid target triggers warning confirmation."""
        system = Mock(name="Alpha Centauri")
        mock_scene.ui.show_confirmation_dialog = Mock()

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=system):
            result = superweapon_ops.handle_stellerate_star_designation(100, 200, mock_fleet)

        assert result['type'] == 'success'
        mock_scene.ui.show_confirmation_dialog.assert_called_once()
        # Verify is_warning=True for dangerous action
        call_kwargs = mock_scene.ui.show_confirmation_dialog.call_args[1]
        assert call_kwargs.get('is_warning') is True


# =============================================================================
# Open Warp Point Tests
# =============================================================================

class TestOpenWarpPointWorkflow:
    """Tests for Open Warp Point superweapon."""

    def test_no_system_at_location_returns_error(self, superweapon_ops, mock_fleet):
        """Test no system at target returns error."""

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=None):
            result = superweapon_ops.handle_open_warp_designation(100, 200, mock_fleet)

        assert result['type'] == 'error'
        assert 'No star system' in result['message']

    def test_no_available_systems_returns_error(self, superweapon_ops, mock_fleet, mock_scene):
        """Single-system galaxy: only the current system exists, picker is empty."""
        current_system = Mock()
        current_system.name = "Alpha"
        current_system.warp_points = []

        # Only one system - the current one
        mock_scene.galaxy.systems = {"Alpha": current_system}

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=current_system):
            result = superweapon_ops.handle_open_warp_designation(100, 200, mock_fleet)

        assert result['type'] == 'error'
        assert 'No available systems' in result['message']

    def test_valid_target_shows_system_picker(self, superweapon_ops, mock_fleet, mock_scene):
        """Test valid target shows system picker."""

        current_system = Mock()
        current_system.name = "Alpha"
        current_system.warp_points = []

        other_system = Mock()
        other_system.name = "Beta"

        mock_scene.galaxy.systems = {"Alpha": current_system, "Beta": other_system}
        mock_scene.ui.show_system_picker = Mock()

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=current_system):
            result = superweapon_ops.handle_open_warp_designation(100, 200, mock_fleet)

        assert result['type'] == 'prompt'
        mock_scene.ui.show_system_picker.assert_called_once()

    # Issue #19 AC1: duplicate warp links must be allowed. Filter should
    # exclude only the current system, never the partner system, regardless
    # of whether a warp point to it already exists.
    def test_duplicate_link_allowed_when_partner_already_linked(
        self, superweapon_ops, mock_fleet, mock_scene,
    ):
        """A->B already linked: picker MUST still offer Beta (duplicates allowed)."""
        current_system = Mock()
        current_system.name = "Alpha"
        existing_wp = Mock()
        existing_wp.destination_id = "Beta"
        current_system.warp_points = [existing_wp]

        other_system = Mock()
        other_system.name = "Beta"

        mock_scene.galaxy.systems = {"Alpha": current_system, "Beta": other_system}
        captured_systems = []

        def capture(systems, current, on_selected):
            captured_systems.extend(systems)

        mock_scene.ui.show_system_picker = Mock(side_effect=capture)

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=current_system):
            result = superweapon_ops.handle_open_warp_designation(100, 200, mock_fleet)

        assert result['type'] == 'prompt'
        mock_scene.ui.show_system_picker.assert_called_once()
        assert other_system in captured_systems
        assert current_system not in captured_systems

    def test_only_current_system_excluded(self, superweapon_ops, mock_fleet, mock_scene):
        """3-system galaxy: picker offers exactly the 2 non-current systems."""
        current_system = Mock()
        current_system.name = "Alpha"
        current_system.warp_points = []

        sys_b = Mock()
        sys_b.name = "Beta"
        sys_c = Mock()
        sys_c.name = "Gamma"

        mock_scene.galaxy.systems = {"Alpha": current_system, "Beta": sys_b, "Gamma": sys_c}
        captured_systems = []

        def capture(systems, current, on_selected):
            captured_systems.extend(systems)

        mock_scene.ui.show_system_picker = Mock(side_effect=capture)

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=current_system):
            result = superweapon_ops.handle_open_warp_designation(100, 200, mock_fleet)

        assert result['type'] == 'prompt'
        names = {s.name for s in captured_systems}
        assert names == {"Beta", "Gamma"}

    # Issue #19 AC3 regression: CLOSE_WARP_POINT is a queued mission order
    # (processed at TurnEngine phase 1.5), so within the same turn the
    # warp point is still on `current_system.warp_points`. The picker MUST
    # still offer the partner system — the new filter does not depend on
    # warp_points state at all.
    def test_picker_offers_partner_with_pending_close_order_same_turn(
        self, superweapon_ops, mock_fleet, mock_scene,
    ):
        """Mid-turn: close-warp order queued on fleet, warp_point still present."""
        current_system = Mock()
        current_system.name = "Alpha"
        existing_wp = Mock()
        existing_wp.destination_id = "Beta"
        current_system.warp_points = [existing_wp]  # still present mid-turn

        other_system = Mock()
        other_system.name = "Beta"

        # Fleet has a queued CLOSE_WARP_POINT order but turn hasn't advanced
        mock_fleet.orders = [Mock(order_type='CLOSE_WARP_POINT', target={'destination_id': 'Beta'})]

        mock_scene.galaxy.systems = {"Alpha": current_system, "Beta": other_system}
        captured_systems = []

        def capture(systems, current, on_selected):
            captured_systems.extend(systems)

        mock_scene.ui.show_system_picker = Mock(side_effect=capture)

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=current_system):
            result = superweapon_ops.handle_open_warp_designation(100, 200, mock_fleet)

        assert result['type'] == 'prompt'
        assert other_system in captured_systems


# =============================================================================
# Close Warp Point Tests
# =============================================================================

class TestCloseWarpPointWorkflow:
    """Tests for Close Warp Point superweapon."""

    def test_no_warp_point_at_location_returns_error(self, superweapon_ops, mock_fleet):
        """Test no warp point at target returns error."""

        with patch.object(superweapon_ops, '_get_warp_point_at_hex', return_value=None):
            result = superweapon_ops.handle_close_warp_designation(100, 200, mock_fleet)

        assert result['type'] == 'error'
        assert 'No warp point' in result['message']

    def test_valid_warp_point_triggers_confirmation(self, superweapon_ops, mock_fleet, mock_scene):
        """Test valid warp point triggers confirmation."""
        warp_point = Mock()
        warp_point.destination_id = "Beta System"
        mock_scene.ui.show_confirmation_dialog = Mock()

        with patch.object(superweapon_ops, '_get_warp_point_at_hex', return_value=warp_point):
            result = superweapon_ops.handle_close_warp_designation(100, 200, mock_fleet)

        assert result['type'] == 'success'
        mock_scene.ui.show_confirmation_dialog.assert_called_once()


# =============================================================================
# Dyson Sphere Tests
# =============================================================================

class TestDysonSphereWorkflow:
    """Tests for Dyson Sphere superweapon."""

    def test_no_system_at_location_returns_error(self, superweapon_ops, mock_fleet):
        """Test no system at target returns error."""

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=None):
            result = superweapon_ops.handle_dyson_sphere_designation(100, 200, mock_fleet)

        assert result['type'] == 'error'
        assert 'No star system' in result['message']

    def test_valid_target_triggers_confirmation(self, superweapon_ops, mock_fleet, mock_scene):
        """Test valid target triggers confirmation."""
        system = Mock()
        system.name = "Alpha Centauri"
        mock_scene.ui.show_confirmation_dialog = Mock()

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=system):
            result = superweapon_ops.handle_dyson_sphere_designation(100, 200, mock_fleet)

        assert result['type'] == 'success'
        mock_scene.ui.show_confirmation_dialog.assert_called_once()


# =============================================================================
# Self-Destruct Tests
# =============================================================================

class TestSelfDestructWorkflow:
    """Tests for Self-Destruct superweapon."""

    def test_no_fleet_returns_none(self, superweapon_ops):
        """Test with no fleet returns None."""
        result = superweapon_ops.handle_self_destruct(None)

        assert result is None

    def test_no_ships_with_ability_returns_error(self, superweapon_ops, mock_fleet):
        """Test no ships with SelfDestruct ability returns error."""
        mock_fleet.capabilities.ships_with_ability = Mock(return_value=[])

        result = superweapon_ops.handle_self_destruct(mock_fleet)

        assert result['type'] == 'error'
        assert 'Self-Destruct Device' in result['message']

    def test_valid_ships_shows_picker(self, superweapon_ops, mock_fleet, mock_scene):
        """Test valid ships shows ship picker."""
        ships = [Mock(id=1), Mock(id=2)]
        mock_fleet.capabilities.ships_with_ability = Mock(return_value=ships)
        mock_scene.ui.show_ship_picker = Mock()

        result = superweapon_ops.handle_self_destruct(mock_fleet)

        assert result['type'] == 'prompt'
        mock_scene.ui.show_ship_picker.assert_called_once()
        call_args = mock_scene.ui.show_ship_picker.call_args[0]
        assert call_args[0] == ships
        assert call_args[1] == "SelfDestruct"


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling."""

    def test_operation_with_invalid_hex_graceful_failure(self, superweapon_ops, mock_fleet):
        """Test operation with invalid hex coordinates fails gracefully."""
        superweapon_ops.scene.camera.hex_at_screen = Mock(return_value=None)

        # Should not raise exception
        superweapon_ops.scene.galaxy.get_planets_at_global_hex = Mock(return_value=[])
        result = superweapon_ops.handle_implode_planet_designation(100, 200, mock_fleet)

        assert result['type'] == 'error'


# =============================================================================
# Helper Method Tests
# =============================================================================

class TestHelperMethods:
    """Tests for helper methods."""

    def test_get_system_at_hex(self, superweapon_ops, mock_scene):
        """Test _get_system_at_hex delegates to scene.world.system_at_map_hex.

        PROJ-477 Phase 4: the live system-ownership lookup routes through the
        scene-owned world seam (radius=50 pathfinder semantics) instead of
        constructing a GalaxyPathfindingService directly.
        """
        expected = Mock(name="resolved_system")
        mock_scene.world.system_at_map_hex.side_effect = None
        mock_scene.world.system_at_map_hex.return_value = expected
        hex_coord = (5, 5)

        result = superweapon_ops._get_system_at_hex(hex_coord)

        assert result is expected
        mock_scene.world.system_at_map_hex.assert_called_once_with(hex_coord)

    def test_get_warp_point_at_hex_no_system(self, superweapon_ops):
        """Test _get_warp_point_at_hex returns None when no system."""
        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=None):
            result = superweapon_ops._get_warp_point_at_hex((5, 5))

        assert result is None

    def test_get_warp_point_at_hex_finds_warp_point(self, superweapon_ops):
        """Test _get_warp_point_at_hex finds warp point at local hex."""
        from game.core.hex_math import HexCoord

        system = Mock()
        system.global_location = HexCoord(0, 0)

        warp_point = Mock()
        warp_point.location = HexCoord(5, 5)
        system.warp_points = [warp_point]

        with patch.object(superweapon_ops, '_get_system_at_hex', return_value=system):
            result = superweapon_ops._get_warp_point_at_hex(HexCoord(5, 5))

        assert result is warp_point

    # PROJ-198: Fallback tests removed - methods are now always available on StrategyUI
    # test_show_confirmation_fallback_without_ui - deleted (duck typing eliminated)
    # test_show_system_picker_fallback - deleted (duck typing eliminated)
    # test_show_ship_picker_fallback - deleted (duck typing eliminated)


# =============================================================================
# Command Dispatch Tests
# =============================================================================

class TestCommandDispatch:
    """Tests for command dispatch to facade."""

    @patch('game.ui.screens.strategy_superweapons.QueueImplodePlanetMissionCommand')
    def test_implode_planet_creates_correct_command(self, mock_cmd_class,
                                                     superweapon_ops, mock_fleet, mock_scene, mock_facade):
        """Test implode planet creates correct command."""
        planet = Mock()
        planet.id = "planet-1"
        planet.name = "Target Planet"
        superweapon_ops.scene.galaxy.get_planets_at_global_hex = Mock(return_value=[planet])

        # Capture the confirmation callback
        confirm_callback = None

        def capture_callback(title, msg, cb, **kwargs):
            nonlocal confirm_callback
            confirm_callback = cb

        mock_scene.ui.show_confirmation_dialog = capture_callback

        superweapon_ops.handle_implode_planet_designation(100, 200, mock_fleet)

        # Execute the confirmation callback
        confirm_callback()

        mock_cmd_class.assert_called_once_with("F-001", (5, 5), "planet-1")
        mock_facade.handle_command.assert_called_once()

    @patch('game.ui.screens.strategy_superweapons.IssueSelfDestructCommand')
    def test_self_destruct_creates_correct_command(self, mock_cmd_class,
                                                    superweapon_ops, mock_fleet, mock_scene, mock_facade):
        """Test self-destruct creates correct command."""
        ships = [Mock(id=1), Mock(id=2)]
        mock_fleet.capabilities.ships_with_ability = Mock(return_value=ships)

        # Capture the ship picker callback
        picker_callback = None

        def capture_callback(ships, ability, cb):
            nonlocal picker_callback
            picker_callback = cb

        mock_scene.ui.show_ship_picker = capture_callback

        superweapon_ops.handle_self_destruct(mock_fleet)

        # Execute the picker callback
        picker_callback([1, 2])

        mock_cmd_class.assert_called_once_with("F-001", [1, 2])
        mock_facade.handle_command.assert_called_once()
