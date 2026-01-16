# Strategy Scene Split Plan

## Status: COMPLETED

**Completed on:** 2026-01-16

## Executive Summary

This document provided a **comprehensive, test-driven plan** to split `strategy_scene.py` (1,568 lines) into 6 focused modules.

**Result:** Reduced `strategy_scene.py` from 1,568 lines to 417 lines while maintaining full backward compatibility.

### Files Created

| File | Lines | Responsibility |
|------|-------|----------------|
| [strategy_scene.py](../../game/ui/screens/strategy_scene.py) | 417 | Main coordinator & state |
| [strategy_renderer.py](../../game/ui/screens/strategy_renderer.py) | 480 | All drawing logic |
| [strategy_input_handler.py](../../game/ui/screens/strategy_input_handler.py) | 260 | Event & click routing |
| [strategy_camera_nav.py](../../game/ui/screens/strategy_camera_nav.py) | 120 | Camera focus & zoom |
| [strategy_fleet_ops.py](../../game/ui/screens/strategy_fleet_ops.py) | 150 | Fleet movement commands |
| [strategy_colonization.py](../../game/ui/screens/strategy_colonization.py) | 180 | Colonization workflow |

**Total:** ~1,607 lines (slight increase due to docstrings and cleaner structure)

### Previously Extracted (already existed)

| File | Lines | Responsibility |
|------|-------|----------------|
| [strategy_screen.py](../../game/ui/screens/strategy_screen.py) | 768 | UI interface (StrategyInterface) |
| [strategy_detail_fmt.py](../../game/ui/screens/strategy_detail_fmt.py) | 230 | HTML formatting utilities |

---

## Original Analysis

---

## Current Structure Analysis

### StrategyScene Responsibilities (Lines by Category)

| Responsibility | Lines | Methods |
|----------------|-------|---------|
| **Rendering** | ~580 | `draw`, `_draw_grid`, `_draw_warp_lanes`, `_draw_systems`, `_draw_system_details`, `_draw_planet_sprite`, `_draw_fleets`, `_draw_move_preview`, `_draw_hover_hex`, `_draw_processing_overlay` |
| **Fleet Movement** | ~130 | `_handle_move_designation`, `_handle_join_designation`, `_get_fleet_at_hex`, `calculate_hybrid_path` |
| **Colonization** | ~175 | `on_colonize_click`, `_issue_colonize_order`, `_handle_colonize_designation`, `_queue_colonize_mission`, `request_colonize_order` (duplicate) |
| **Camera/Navigation** | ~90 | `center_camera_on`, `_zoom_to_galaxy`, `_zoom_to_system`, `cycle_selection` |
| **Input Handling** | ~180 | `handle_event`, `handle_click`, `_handle_picking`, `update_input` |
| **Core/State** | ~413 | `__init__`, properties, `update`, `advance_turn`, `_process_full_turn`, `on_ui_selection`, `_get_object_asset`, `_load_assets`, `handle_resize` |

### Key Dependencies

```
StrategyScene
├── self.session (GameSession) - Primary state container
├── self.camera (Camera) - Viewport management
├── self.ui (StrategyInterface) - UI layer
├── self.galaxy, self.empires, self.systems - Properties from session
├── self.selected_fleet, self.selected_object - Selection state
├── self.input_mode - Input state machine
└── self.empire_assets - Loaded visual assets
```

### Identified Issues

1. **Duplicate method**: `request_colonize_order` at lines 147-153 AND 902-924
2. **Mixed concerns**: Rendering logic alongside game logic
3. **Input mode state machine**: Scattered across multiple methods
4. **Heavy coupling**: `self.camera`, `self.ui`, `self.session` used everywhere

---

## Target Architecture

```
game/ui/screens/
├── strategy_scene.py           (~400 lines) - Coordinator & state
├── strategy_renderer.py        (~580 lines) - All drawing logic
├── strategy_input_handler.py   (~180 lines) - Event & click routing
├── strategy_camera_nav.py      (~90 lines)  - Camera focus & zoom
├── strategy_fleet_ops.py       (~130 lines) - Fleet movement commands
└── strategy_colonization.py    (~175 lines) - Colonization workflow
```

---

## Phase 1: Test Infrastructure Setup

### Step 1.1: Create Test Fixtures

**File:** `tests/strategy/test_strategy_scene_split.py`

```python
"""
Test suite for StrategyScene refactoring.
These tests verify behavior BEFORE and AFTER the split.
"""
import pytest
from unittest.mock import MagicMock, patch
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType


@pytest.fixture
def mock_session():
    """Create a mock GameSession with minimal galaxy."""
    session = MagicMock()
    session.galaxy = MagicMock()
    session.galaxy.systems = {}
    session.empires = []
    session.systems = []
    session.player_empire = MagicMock()
    session.player_empire.colonies = []
    session.player_empire.fleets = []
    session.enemy_empire = MagicMock()
    session.human_player_ids = [0]
    session.turn_engine = MagicMock()
    return session


@pytest.fixture
def mock_camera():
    """Create a mock Camera."""
    camera = MagicMock()
    camera.zoom = 2.0
    camera.position = MagicMock()
    camera.position.x = 0
    camera.position.y = 0
    camera.width = 1280
    camera.height = 720
    camera.world_to_screen = lambda v: v
    camera.screen_to_world = lambda p: MagicMock(x=p[0], y=p[1])
    return camera
```

### Step 1.2: Document Current Behavior Tests

Create tests that capture current behavior before refactoring:

```python
class TestCurrentBehavior:
    """Tests capturing current StrategyScene behavior."""

    def test_selection_updates_ui(self, mock_session):
        """Selecting an object should update the UI panel."""
        # This test documents current coupling between selection and UI
        pass

    def test_colonize_validates_with_engine(self, mock_session):
        """Colonize action should validate with TurnEngine."""
        pass

    def test_camera_centers_on_object(self, mock_session, mock_camera):
        """center_camera_on should update camera position."""
        pass

    def test_input_mode_transitions(self, mock_session):
        """Input mode should transition correctly on key presses."""
        pass
```

---

## Phase 2: Extract Strategy Renderer

### Step 2.1: Write Tests for Renderer

**File:** `tests/unit/ui/test_strategy_renderer.py`

```python
"""Tests for StrategyRenderer - the extracted rendering module."""
import pytest
from unittest.mock import MagicMock, patch
import pygame
from game.strategy.data.hex_math import HexCoord


class TestStrategyRenderer:
    """Unit tests for strategy map rendering."""

    @pytest.fixture
    def renderer_context(self):
        """Create context needed for rendering."""
        return {
            'camera': MagicMock(),
            'galaxy': MagicMock(),
            'empires': [],
            'systems': [],
            'selected_object': None,
            'selected_fleet': None,
            'hover_hex': None,
            'input_mode': 'SELECT',
            'empire_assets': {},
            'screen_width': 1920,
            'screen_height': 1080,
            'HEX_SIZE': 10,
            'SIDEBAR_WIDTH': 600,
            'TOP_BAR_HEIGHT': 50,
        }

    def test_draw_grid_respects_zoom_threshold(self, renderer_context):
        """Grid should not draw when zoom < 0.4."""
        renderer_context['camera'].zoom = 0.3
        # After extraction: StrategyRenderer.should_draw_grid(context) == False
        pass

    def test_draw_systems_culls_offscreen(self, renderer_context):
        """Systems outside viewport should not be drawn."""
        pass

    def test_draw_fleet_path_shows_segments(self, renderer_context):
        """Selected fleet path should show turn-by-turn segments."""
        pass

    def test_planet_sprite_uses_correct_category(self, renderer_context):
        """Planet sprite category should match planet type."""
        # gas giant -> 'gas', ice planet -> 'ice', etc.
        pass
```

### Step 2.2: Create Renderer Module

**File:** `game/ui/screens/strategy_renderer.py`

```python
"""
Rendering logic for the strategy map.
Extracted from StrategyScene to reduce file size and improve testability.
"""
import math
import pygame
from game.strategy.data.hex_math import hex_to_pixel, pixel_to_hex, HexCoord
from game.strategy.data.fleet import OrderType
from ui.colors import COLORS


class StrategyRenderer:
    """Handles all rendering for the strategy map."""

    def __init__(self, context_provider):
        """
        Initialize renderer with a context provider.

        Args:
            context_provider: Object providing camera, galaxy, empires, etc.
                              Typically the StrategyScene instance.
        """
        self.ctx = context_provider

    # --- Property Accessors (delegate to context) ---
    @property
    def camera(self): return self.ctx.camera

    @property
    def galaxy(self): return self.ctx.galaxy

    @property
    def systems(self): return self.ctx.systems

    @property
    def empires(self): return self.ctx.empires

    @property
    def HEX_SIZE(self): return self.ctx.HEX_SIZE

    @property
    def screen_width(self): return self.ctx.screen_width

    @property
    def screen_height(self): return self.ctx.screen_height

    @property
    def SIDEBAR_WIDTH(self): return self.ctx.SIDEBAR_WIDTH

    @property
    def TOP_BAR_HEIGHT(self): return self.ctx.TOP_BAR_HEIGHT

    def draw(self, screen):
        """Main draw entry point."""
        viewport_w = self.screen_width - self.SIDEBAR_WIDTH
        viewport_h = self.screen_height - self.TOP_BAR_HEIGHT

        if viewport_w > 0 and viewport_h > 0:
            viewport_rect = pygame.Rect(0, self.TOP_BAR_HEIGHT, viewport_w, viewport_h)
            screen.set_clip(viewport_rect)
            screen.fill(COLORS['bg_deep'], viewport_rect)
        else:
            screen.fill(COLORS['bg_deep'])

        if self.camera.zoom >= 0.4:
            self._draw_grid(screen)

        self._draw_warp_lanes(screen)
        self._draw_systems(screen)
        self._draw_fleets(screen)

        if getattr(self.ctx, 'input_mode', 'SELECT') == 'MOVE' and self.ctx.selected_fleet:
            self._draw_move_preview(screen)

        if self.ctx.hover_hex and self.camera.zoom >= 0.5:
            self._draw_hover_hex(screen)

        screen.set_clip(None)

        if viewport_w > 0 and viewport_h > 0:
            pygame.draw.rect(screen, COLORS['border_normal'], viewport_rect, 2)

    # ... (move all _draw_* methods here)
```

### Step 2.3: Integration Points

In `strategy_scene.py`, replace draw methods with delegation:

```python
class StrategyScene:
    def __init__(self, ...):
        # ... existing init ...
        from game.ui.screens.strategy_renderer import StrategyRenderer
        self._renderer = StrategyRenderer(self)

    def draw(self, screen):
        """Render the scene."""
        self._renderer.draw(screen)
        self.ui.draw(screen)

    def _draw_processing_overlay(self, screen):
        """Draw modal overlay for turn processing (stays in scene for state access)."""
        # Keep this here as it's tied to turn processing state
        ...
```

### Step 2.4: Verification Tests

```python
def test_renderer_integration():
    """Verify renderer produces same output as before extraction."""
    # Compare screenshots or draw call counts before/after
    pass
```

---

## Phase 3: Extract Camera Navigation

### Step 3.1: Write Tests

**File:** `tests/unit/ui/test_strategy_camera_nav.py`

```python
"""Tests for camera navigation extracted from StrategyScene."""
import pytest
from unittest.mock import MagicMock
from game.strategy.data.hex_math import HexCoord, hex_to_pixel


class TestCameraNavigation:
    """Tests for camera focus and zoom operations."""

    def test_center_on_planet(self):
        """Camera should center on planet's global hex position."""
        pass

    def test_center_on_fleet(self):
        """Camera should center on fleet location."""
        pass

    def test_center_on_system(self):
        """Camera should center on system's global_location."""
        pass

    def test_zoom_to_galaxy_calculates_bounds(self):
        """Galaxy zoom should fit all systems in view."""
        pass

    def test_zoom_to_system_sets_zoom_level(self):
        """System zoom should set zoom to 2.0."""
        pass

    def test_cycle_selection_wraps_around(self):
        """Cycling past last item should wrap to first."""
        pass
```

### Step 3.2: Create Module

**File:** `game/ui/screens/strategy_camera_nav.py`

```python
"""
Camera navigation operations for strategy scene.
Handles focus, zoom, and selection cycling.
"""
import pygame
from game.core.logger import log_debug
from game.strategy.data.hex_math import hex_to_pixel, HexCoord


class CameraNavigator:
    """Manages camera focus and zoom operations."""

    def __init__(self, scene):
        """
        Args:
            scene: StrategyScene instance providing camera, systems, etc.
        """
        self.scene = scene

    @property
    def camera(self): return self.scene.camera

    @property
    def systems(self): return self.scene.systems

    @property
    def HEX_SIZE(self): return self.scene.HEX_SIZE

    def center_on(self, obj):
        """Center camera on a game object (Planet, Fleet, System)."""
        target_hex = self._resolve_global_hex(obj)

        if target_hex:
            fx, fy = hex_to_pixel(target_hex, self.HEX_SIZE)
            self.camera.position.x = fx
            self.camera.position.y = fy
            log_debug(f"Camera centered on {obj} at {target_hex}")
        else:
            log_debug(f"Could not center camera on {obj}")

    def _resolve_global_hex(self, obj):
        """Resolve object to its global hex coordinate."""
        if hasattr(obj, 'location'):
            if hasattr(obj, 'planet_type'):  # Planet
                sys = next((s for s in self.systems if obj in s.planets), None)
                if sys:
                    return sys.global_location + obj.location
            elif hasattr(obj, 'ships'):  # Fleet
                return obj.location
            elif hasattr(obj, 'global_location'):  # System
                return obj.global_location
        return None

    def zoom_to_galaxy(self):
        """Zoom out to show entire galaxy (Shift+G)."""
        if not self.systems:
            return

        all_positions = []
        for sys in self.systems:
            px, py = hex_to_pixel(sys.global_location, self.HEX_SIZE)
            all_positions.append((px, py))

        if not all_positions:
            return

        min_x = min(p[0] for p in all_positions)
        max_x = max(p[0] for p in all_positions)
        min_y = min(p[1] for p in all_positions)
        max_y = max(p[1] for p in all_positions)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.camera.position.x = center_x
        self.camera.position.y = center_y

        width = max_x - min_x + 600
        height = max_y - min_y + 600

        zoom_x = self.camera.width / width if width > 0 else 1.0
        zoom_y = self.camera.height / height if height > 0 else 1.0
        fit_zoom = min(zoom_x, zoom_y)

        self.camera.target_zoom = max(self.camera.min_zoom, min(self.camera.max_zoom, fit_zoom))
        self.camera.zoom = self.camera.target_zoom

        log_debug(f"Galaxy View: zoom={self.camera.zoom:.2f}")

    def zoom_to_system(self, target_sys=None):
        """Zoom to 2x on a system (Shift+S)."""
        if not target_sys:
            target_sys = self.scene.last_selected_system

        if not target_sys and self.scene.selected_object:
            from game.strategy.data.galaxy import StarSystem
            if isinstance(self.scene.selected_object, StarSystem):
                target_sys = self.scene.selected_object
            elif hasattr(self.scene.selected_object, 'location'):
                target_sys = next(
                    (s for s in self.systems
                     if self.scene.selected_object in s.planets
                     or self.scene.selected_object in s.warp_points),
                    None
                )

        if not target_sys:
            log_debug("No system selected for Shift+S zoom")
            return

        px, py = hex_to_pixel(target_sys.global_location, self.HEX_SIZE)
        self.camera.position.x = px
        self.camera.position.y = py

        self.camera.target_zoom = 2.0
        self.camera.zoom = 2.0

        log_debug(f"System View: {target_sys.name} at zoom=2.0")

    def cycle_selection(self, obj_type, direction):
        """Cycle through colonies or fleets."""
        targets = []
        if obj_type == 'colony':
            targets = self.scene.current_empire.colonies
        elif obj_type == 'fleet':
            targets = self.scene.current_empire.fleets

        if not targets:
            log_debug(f"No {obj_type}s to cycle.")
            return None

        current_idx = -1
        if self.scene.selected_object in targets:
            current_idx = targets.index(self.scene.selected_object)

        next_idx = (current_idx + direction) % len(targets)
        return targets[next_idx]
```

---

## Phase 4: Extract Fleet Operations

### Step 4.1: Write Tests

**File:** `tests/strategy/test_strategy_fleet_ops.py`

```python
"""Tests for fleet movement operations."""
import pytest
from unittest.mock import MagicMock, patch
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType


class TestFleetOperations:
    """Tests for fleet movement command handling."""

    def test_move_issues_command(self):
        """Move designation should issue IssueMoveCommand."""
        pass

    def test_move_detects_fleet_at_target(self):
        """Clicking on a fleet should prompt for move vs intercept."""
        pass

    def test_join_queues_move_and_join_orders(self):
        """Join command should queue MOVE_TO_FLEET then JOIN_FLEET."""
        pass

    def test_join_rejects_enemy_fleet(self):
        """Cannot join enemy fleet."""
        pass

    def test_join_rejects_self(self):
        """Cannot join self."""
        pass

    def test_get_fleet_at_hex_searches_all_empires(self):
        """Fleet lookup should search all empires."""
        pass
```

### Step 4.2: Create Module

**File:** `game/ui/screens/strategy_fleet_ops.py`

```python
"""
Fleet movement operations for strategy scene.
Handles move, join, and intercept commands.
"""
import pygame
from game.core.logger import log_debug, log_warning
from game.strategy.data.fleet import FleetOrder, OrderType
from game.strategy.data.hex_math import pixel_to_hex


class FleetOperations:
    """Handles fleet movement commands."""

    def __init__(self, scene):
        self.scene = scene

    @property
    def camera(self): return self.scene.camera

    @property
    def empires(self): return self.scene.empires

    @property
    def HEX_SIZE(self): return self.scene.HEX_SIZE

    def get_fleet_at_hex(self, hex_coord):
        """Find the first fleet at the given hex."""
        for emp in self.empires:
            for f in emp.fleets:
                if f.location == hex_coord:
                    return f
        return None

    def handle_move_designation(self, mx, my, selected_fleet):
        """Handle designating a move target."""
        if not selected_fleet:
            return

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
            return self._execute_move(selected_fleet, target_hex)

    def _execute_move(self, fleet, target_hex):
        """Execute standard move command."""
        log_debug(f"Calculating path to {target_hex}...")

        preview_path = self.scene.session.preview_fleet_path(fleet, target_hex)

        if preview_path:
            log_debug(f"Path confirmed: {len(preview_path)} steps.")

            from game.strategy.engine.commands import IssueMoveCommand
            cmd = IssueMoveCommand(fleet.id, target_hex)

            result = self.scene.session.handle_command(cmd)

            if result and result.is_valid:
                return {'type': 'success', 'fleet': fleet}
            else:
                log_warning(f"Move Failed: {result.message if result else 'Unknown'}")
                return {'type': 'error', 'message': result.message if result else 'Unknown'}
        else:
            log_warning("Cannot find path to target (Unreachable).")
            return {'type': 'error', 'message': 'Unreachable'}

    def execute_intercept(self, fleet, target_fleet):
        """Execute intercept order."""
        log_debug(f"Intercepting Fleet {target_fleet.id}...")

        new_order = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
        fleet.add_order(new_order)

        return {'type': 'success', 'fleet': fleet}

    def handle_join_designation(self, mx, my, selected_fleet):
        """Handle designating a fleet to join."""
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

        order_move = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
        selected_fleet.add_order(order_move)

        order_join = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        selected_fleet.add_order(order_join)

        return {'type': 'success', 'fleet': selected_fleet}
```

---

## Phase 5: Extract Colonization System

### Step 5.1: Write Tests

**File:** `tests/strategy/test_strategy_colonization.py`

```python
"""Tests for colonization workflow."""
import pytest
from unittest.mock import MagicMock
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.fleet import Fleet, OrderType


class TestColonization:
    """Tests for colonization command handling."""

    def test_colonize_validates_with_engine(self):
        """Colonize should validate planet with turn engine."""
        pass

    def test_colonize_single_planet_auto_selects(self):
        """Single valid planet should be auto-selected."""
        pass

    def test_colonize_multiple_planets_prompts(self):
        """Multiple valid planets should prompt user selection."""
        pass

    def test_colonize_issues_command(self):
        """Colonize should issue IssueColonizeCommand."""
        pass

    def test_queue_colonize_mission_adds_move_and_colonize(self):
        """Mission queue should add MOVE then COLONIZE orders."""
        pass

    def test_colonize_at_location_skips_move(self):
        """If already at location, should only add COLONIZE order."""
        pass
```

### Step 5.2: Create Module

**File:** `game/ui/screens/strategy_colonization.py`

```python
"""
Colonization workflow for strategy scene.
Handles colonize commands, planet validation, and mission queuing.
"""
from game.core.logger import log_debug, log_info, log_warning
from game.strategy.data.fleet import FleetOrder, OrderType
from game.strategy.data.hex_math import pixel_to_hex
from game.strategy.engine.commands import IssueColonizeCommand


class ColonizationSystem:
    """Handles colonization commands and workflows."""

    def __init__(self, scene):
        self.scene = scene

    @property
    def galaxy(self): return self.scene.galaxy

    @property
    def systems(self): return self.scene.systems

    @property
    def turn_engine(self): return self.scene.turn_engine

    def on_colonize_click(self, fleet):
        """Handle colonize button/key action."""
        if not fleet:
            return None

        # Find potential planets at fleet location
        start_sys = self._get_system_at_hex(fleet.location)
        potential_planets = []

        if start_sys:
            loc_local = fleet.location - start_sys.global_location
            for p in start_sys.planets:
                if p.location == loc_local:
                    potential_planets.append(p)
        else:
            for sys in self.systems:
                loc_local = fleet.location - sys.global_location
                for p in sys.planets:
                    if p.location == loc_local:
                        potential_planets.append(p)

        # Validate with engine
        valid_planets = []
        for p in potential_planets:
            res = self.turn_engine.validate_colonize_order(self.galaxy, fleet, p)
            if res.is_valid:
                valid_planets.append(p)

        if not valid_planets:
            log_debug("No colonizable planets at fleet location (Validation Failed).")
            return None

        if len(valid_planets) == 1:
            return self.issue_colonize_order(fleet, valid_planets[0])
        else:
            # Return context for UI to prompt selection
            return {
                'type': 'prompt',
                'planets': valid_planets,
                'fleet': fleet,
            }

    def issue_colonize_order(self, fleet, planet):
        """Issue colonize command to session."""
        cmd = IssueColonizeCommand(fleet.id, planet.id)
        log_info(f"Issued IssueColonizeCommand for {planet.name}")

        result = self.scene.session.handle_command(cmd)
        if not result.is_valid:
            log_warning(f"Command Failed: {result.message}")
            return {'type': 'error', 'message': result.message}

        return {'type': 'success', 'fleet': fleet}

    def handle_colonize_designation(self, mx, my, fleet):
        """Handle selecting a planet for colonization with movement."""
        if not fleet:
            return None

        world_pos = self.scene.camera.screen_to_world((mx, my))
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.HEX_SIZE)

        target_system = self._get_system_at_hex(target_hex)
        if not target_system:
            log_debug("No system at target location.")
            return None

        local_hex = target_hex - target_system.global_location
        candidates = [p for p in target_system.planets
                     if p.owner_id is None and p.location == local_hex]

        if not candidates:
            log_debug(f"No colonizable planets at hex {target_hex}.")
            return None

        if len(candidates) == 1:
            return self.queue_colonize_mission(target_hex, candidates[0], fleet)
        else:
            return {
                'type': 'prompt',
                'planets': candidates,
                'target_hex': target_hex,
                'fleet': fleet,
            }

    def queue_colonize_mission(self, target_hex, planet, fleet):
        """Queue MOVE + COLONIZE orders."""
        if not fleet:
            return None

        start_hex = fleet.location
        if fleet.orders:
            last = fleet.orders[-1]
            if last.type == OrderType.MOVE:
                start_hex = last.target

        from game.strategy.data.pathfinding import find_hybrid_path
        path = find_hybrid_path(self.galaxy, start_hex, target_hex)

        if path:
            if start_hex != target_hex:
                move = FleetOrder(OrderType.MOVE, target_hex)
                fleet.add_order(move)
                if len(fleet.orders) == 1:
                    if path and path[0] == fleet.location:
                        path = path[1:]
                    fleet.path = path

            col = FleetOrder(OrderType.COLONIZE, planet)
            fleet.add_order(col)

            p_name = planet.name if planet else "Any Planet"
            log_info(f"Mission Queued: Colonize {p_name} at {target_hex}")
            return {'type': 'success', 'fleet': fleet}
        else:
            log_warning("Cannot find path.")
            return {'type': 'error', 'message': 'No path found'}

    def _get_system_at_hex(self, hex_coord):
        """Find system at hex coordinate."""
        from game.strategy.data.pathfinding import get_system_at_hex
        return get_system_at_hex(self.galaxy, hex_coord)
```

---

## Phase 6: Extract Input Handler

### Step 6.1: Write Tests

**File:** `tests/unit/ui/test_strategy_input_handler.py`

```python
"""Tests for strategy scene input handling."""
import pytest
from unittest.mock import MagicMock
import pygame


class TestInputHandler:
    """Tests for input event routing."""

    def test_move_mode_on_m_key(self):
        """Pressing M with fleet selected enters MOVE mode."""
        pass

    def test_join_mode_on_j_key(self):
        """Pressing J with fleet selected enters JOIN mode."""
        pass

    def test_colonize_mode_on_c_key(self):
        """Pressing C with fleet selected enters COLONIZE_TARGET mode."""
        pass

    def test_escape_returns_to_select(self):
        """Escape key returns to SELECT mode."""
        pass

    def test_shift_g_zooms_galaxy(self):
        """Shift+G should trigger galaxy zoom."""
        pass

    def test_shift_s_zooms_system(self):
        """Shift+S should trigger system zoom."""
        pass

    def test_click_delegates_to_mode_handler(self):
        """Click should delegate to appropriate mode handler."""
        pass

    def test_picking_updates_selection(self):
        """Left click in SELECT mode updates selected_object."""
        pass
```

### Step 6.2: Create Module

**File:** `game/ui/screens/strategy_input_handler.py`

```python
"""
Input handling for strategy scene.
Routes keyboard and mouse events to appropriate handlers.
"""
import pygame
import pygame_gui
from game.core.logger import log_debug
from game.strategy.data.hex_math import pixel_to_hex
from game.strategy.data.physics import SectorEnvironment


class InputHandler:
    """Routes input events for strategy scene."""

    def __init__(self, scene):
        self.scene = scene
        self.input_mode = 'SELECT'

    def handle_event(self, event):
        """Process pygame events."""
        self.scene.ui.handle_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_press(event)

        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

    def _handle_button_press(self, event):
        """Handle UI button presses."""
        ui = self.scene.ui

        if event.ui_element == ui.btn_next_turn:
            self.scene.advance_turn()
        elif event.ui_element == ui.btn_colonize:
            self.scene.on_colonize_click()
        elif event.ui_element == ui.btn_build_ship:
            self.scene.on_build_ship_click()
        elif event.ui_element == ui.btn_prev_colony:
            self.scene.cycle_selection('colony', -1)
        elif event.ui_element == ui.btn_next_colony:
            self.scene.cycle_selection('colony', 1)
        elif event.ui_element == ui.btn_prev_fleet:
            self.scene.cycle_selection('fleet', -1)
        elif event.ui_element == ui.btn_next_fleet:
            self.scene.cycle_selection('fleet', 1)

    def _handle_keydown(self, event):
        """Handle keyboard input."""
        if event.key == pygame.K_m:
            if self.scene.selected_fleet:
                self.input_mode = 'MOVE'
                log_debug("Input Mode: MOVE - Click destination for fleet.")
            else:
                log_debug("Select a fleet first.")

        elif event.key == pygame.K_j:
            if self.scene.selected_fleet:
                self.input_mode = 'JOIN'
                log_debug("Input Mode: JOIN - Select fleet to join.")
            else:
                log_debug("Select a fleet first.")

        elif event.key == pygame.K_ESCAPE:
            if self.input_mode in ('MOVE', 'COLONIZE_TARGET', 'JOIN'):
                self.input_mode = 'SELECT'
                log_debug("Input Mode: SELECT")

        elif event.key == pygame.K_c:
            if self.scene.selected_fleet:
                self.input_mode = 'COLONIZE_TARGET'
                log_debug("Input Mode: COLONIZE - Select target planet.")
            else:
                log_debug("Select a fleet first.")

        elif event.key == pygame.K_g and (event.mod & pygame.KMOD_SHIFT):
            self.scene._camera_nav.zoom_to_galaxy()

        elif event.key == pygame.K_s and (event.mod & pygame.KMOD_SHIFT):
            self.scene._camera_nav.zoom_to_system()

    def handle_click(self, mx, my, button):
        """Handle mouse clicks."""
        if self.scene.ui.handle_click(mx, my, button):
            return True

        if self.input_mode == 'MOVE':
            return self._handle_move_mode_click(mx, my, button)
        elif self.input_mode == 'JOIN':
            return self._handle_join_mode_click(mx, my, button)
        elif self.input_mode == 'COLONIZE_TARGET':
            return self._handle_colonize_mode_click(mx, my, button)
        elif self.input_mode == 'SELECT':
            return self._handle_select_mode_click(mx, my, button)

        return False

    def _handle_move_mode_click(self, mx, my, button):
        """Handle click in MOVE mode."""
        if button == 1:
            result = self.scene._fleet_ops.handle_move_designation(
                mx, my, self.scene.selected_fleet
            )
            if result and result.get('type') == 'choice':
                # Prompt user for move vs intercept
                self.scene.ui.prompt_move_choice(
                    result['target_fleet'],
                    result['target_hex'],
                    lambda: self._on_move_choice_move(result['target_hex']),
                    lambda: self._on_move_choice_intercept(result['target_fleet'])
                )
            elif result and result.get('type') == 'success':
                self._finish_move_action(result['fleet'])
            return True
        elif button == 3:
            self.input_mode = 'SELECT'
            log_debug("Input Mode: SELECT")
            return True
        return False

    def _on_move_choice_move(self, target_hex):
        """User chose standard move."""
        result = self.scene._fleet_ops._execute_move(
            self.scene.selected_fleet, target_hex
        )
        if result.get('type') == 'success':
            self._finish_move_action(result['fleet'])

    def _on_move_choice_intercept(self, target_fleet):
        """User chose intercept."""
        result = self.scene._fleet_ops.execute_intercept(
            self.scene.selected_fleet, target_fleet
        )
        if result.get('type') == 'success':
            self._finish_move_action(result['fleet'])

    def _finish_move_action(self, fleet):
        """Common cleanup after move action."""
        keys = pygame.key.get_pressed()
        if not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.input_mode = 'SELECT'
        self.scene.on_ui_selection(fleet)

    # ... (similar handlers for JOIN and COLONIZE modes)

    def _handle_select_mode_click(self, mx, my, button):
        """Handle click in SELECT mode."""
        if button == 1:
            self._handle_picking(mx, my)
            return True
        elif button == 3:
            if self.scene.selected_fleet:
                result = self.scene._fleet_ops.handle_move_designation(
                    mx, my, self.scene.selected_fleet
                )
                # ... handle result
                return True
        return False

    def _handle_picking(self, mx, my):
        """Raycast from screen to galaxy objects."""
        world_pos = self.scene.camera.screen_to_world((mx, my))
        hex_clicked = pixel_to_hex(world_pos.x, world_pos.y, self.scene.HEX_SIZE)

        # ... (picking logic - builds sector_contents list)

        # Update UI panels
        # ... (existing logic)

    def update_input(self, dt, events):
        """Update camera input."""
        mx, my = pygame.mouse.get_pos()
        over_sidebar = (mx > self.scene.screen_width - self.scene.SIDEBAR_WIDTH)
        over_topbar = (my < self.scene.TOP_BAR_HEIGHT)

        cam_events = []
        for e in events:
            if e.type == pygame.MOUSEWHEEL:
                if over_sidebar or over_topbar:
                    continue
            cam_events.append(e)

        self.scene.camera.update_input(dt, cam_events)

        world_pos = self.scene.camera.screen_to_world((mx, my))
        self.scene.hover_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.HEX_SIZE)
```

---

## Phase 7: Final Integration & Cleanup

### Step 7.1: Refactored StrategyScene

**File:** `game/ui/screens/strategy_scene.py` (~400 lines)

```python
"""
StrategyScene - Main coordinator for strategy layer.
Delegates to specialized modules for rendering, input, and operations.
"""
import pygame
from game.core.logger import log_debug, log_info, log_warning
from game.strategy.data.galaxy import StarSystem
from game.strategy.data.fleet import Fleet
from game.ui.renderer.camera import Camera
from game.ui.screens.strategy_screen import StrategyInterface

# Extracted modules
from game.ui.screens.strategy_renderer import StrategyRenderer
from game.ui.screens.strategy_camera_nav import CameraNavigator
from game.ui.screens.strategy_fleet_ops import FleetOperations
from game.ui.screens.strategy_colonization import ColonizationSystem
from game.ui.screens.strategy_input_handler import InputHandler


class StrategyScene:
    """Manages strategy layer simulation, rendering, and UI."""

    SIDEBAR_WIDTH = 600
    TOP_BAR_HEIGHT = 50

    def __init__(self, screen_width, screen_height, session=None):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Session Management
        if session:
            self.session = session
        else:
            from game.strategy.engine.game_session import GameSession
            self.session = GameSession()

        # Camera
        self.camera = Camera(
            screen_width - self.SIDEBAR_WIDTH,
            screen_height - self.TOP_BAR_HEIGHT,
            offset_x=0,
            offset_y=self.TOP_BAR_HEIGHT
        )
        self.camera.max_zoom = 25.0
        self.camera.zoom = 2.0

        # Focus on Player Home
        self._focus_on_player_home()

        # UI
        self.ui = StrategyInterface(self, screen_width, screen_height)

        # State
        self.hover_hex = None
        self.HEX_SIZE = 10
        self.DETAIL_ZOOM_LEVEL = 3.0

        self.selected_fleet = None
        self.selected_object = None
        self.last_selected_system = None

        self.turn_processing = False
        self.action_open_design = False
        self.current_player_index = 0

        # Assets
        self.empire_assets = {}
        self._load_assets()

        # Initialize sub-modules
        self._renderer = StrategyRenderer(self)
        self._camera_nav = CameraNavigator(self)
        self._fleet_ops = FleetOperations(self)
        self._colonization = ColonizationSystem(self)
        self._input = InputHandler(self)

    # --- Properties (delegate to session) ---
    @property
    def galaxy(self): return self.session.galaxy

    @property
    def empires(self): return self.session.empires

    @property
    def systems(self): return self.session.systems

    @property
    def turn_engine(self): return self.session.turn_engine

    @property
    def player_empire(self): return self.session.player_empire

    @property
    def enemy_empire(self): return self.session.enemy_empire

    @property
    def human_player_ids(self): return self.session.human_player_ids

    @property
    def current_empire(self):
        current_player_id = self.human_player_ids[self.current_player_index]
        return next((e for e in self.empires if e.id == current_player_id), self.empires[0])

    @property
    def input_mode(self): return self._input.input_mode

    @input_mode.setter
    def input_mode(self, value): self._input.input_mode = value

    # --- Lifecycle ---
    def update(self, dt):
        self.camera.update(dt)
        self.ui.update(dt)

    def draw(self, screen):
        self._renderer.draw(screen)

        if self.turn_processing:
            self._draw_processing_overlay(screen)

        self.ui.draw(screen)

    def handle_resize(self, width, height):
        self.screen_width = width
        self.screen_height = height
        self.camera.width = width - self.SIDEBAR_WIDTH
        self.camera.height = height - self.TOP_BAR_HEIGHT
        self.camera.offset_y = self.TOP_BAR_HEIGHT
        self.ui.handle_resize(width, height)

    # --- Event Handling (delegates to InputHandler) ---
    def handle_event(self, event):
        self._input.handle_event(event)

    def handle_click(self, mx, my, button):
        return self._input.handle_click(mx, my, button)

    def update_input(self, dt, events):
        self._input.update_input(dt, events)

    # --- Navigation (delegates to CameraNavigator) ---
    def center_camera_on(self, obj):
        self._camera_nav.center_on(obj)

    def cycle_selection(self, obj_type, direction):
        new_obj = self._camera_nav.cycle_selection(obj_type, direction)
        if new_obj:
            self.on_ui_selection(new_obj)
            self.center_camera_on(new_obj)

    # --- Colonization (delegates to ColonizationSystem) ---
    def on_colonize_click(self):
        result = self._colonization.on_colonize_click(self.selected_fleet)
        if result and result.get('type') == 'prompt':
            self.ui.prompt_planet_selection(
                result['planets'],
                lambda p: self._colonization.issue_colonize_order(self.selected_fleet, p)
            )
        elif result and result.get('type') == 'success':
            self.on_ui_selection(self.selected_fleet)

    def request_colonize_order(self, fleet, planet=None):
        """Handle colonize request from UI."""
        self.selected_fleet = fleet
        if planet:
            # Direct colonize with known planet
            target_hex = self._resolve_planet_global_hex(planet)
            if target_hex:
                self._colonization.queue_colonize_mission(target_hex, planet, fleet)
                self.on_ui_selection(fleet)
        else:
            self.on_colonize_click()

    # --- Turn Management ---
    def advance_turn(self):
        self.current_player_index += 1

        if self.current_player_index >= len(self.human_player_ids):
            self.current_player_index = 0
            self._process_full_turn()
            self._update_player_label()
        else:
            next_player_id = self.human_player_ids[self.current_player_index]
            log_info(f"Player {next_player_id + 1}'s turn to give orders.")
            self._update_player_label()
            next_empire = next((e for e in self.empires if e.id == next_player_id), None)
            if next_empire and next_empire.colonies:
                self.center_camera_on(next_empire.colonies[0])

    def _process_full_turn(self):
        self.turn_processing = True
        log_info("Processing Turn...")

        screen = pygame.display.get_surface()
        if screen:
            self.draw(screen)
            pygame.display.flip()

        self.session.process_turn()

        current_player_id = self.human_player_ids[self.current_player_index]
        current_empire = next((e for e in self.empires if e.id == current_player_id), self.player_empire)
        if current_empire.colonies:
            self.center_camera_on(current_empire.colonies[0])

        self.turn_processing = False

        if self.selected_object:
            self.on_ui_selection(self.selected_object)

    def _update_player_label(self):
        player_num = self.current_player_index + 1
        self.ui.lbl_current_player.set_text(f"Player {player_num}'s Turn")

    # --- Selection ---
    def on_ui_selection(self, obj):
        self.selected_object = obj

        if isinstance(obj, StarSystem):
            self.last_selected_system = obj
        elif hasattr(obj, 'location'):
            parent_sys = next((s for s in self.systems if obj in s.planets or obj in s.warp_points), None)
            if parent_sys:
                self.last_selected_system = parent_sys

        current_player_id = self.human_player_ids[self.current_player_index]

        if isinstance(obj, Fleet) and obj.owner_id == current_player_id:
            self.selected_fleet = obj
        else:
            if not isinstance(obj, Fleet):
                self.selected_fleet = None

        img = self._get_object_asset(obj)
        self.ui.show_detailed_report(obj, img)

    # --- Actions ---
    def on_build_ship_click(self):
        from game.strategy.data.galaxy import Planet
        if isinstance(self.selected_object, Planet):
            planet = self.selected_object
            if planet.owner_id == self.current_empire.id:
                log_info(f"Queueing Ship at {planet}...")
                from game.strategy.engine.commands import IssueBuildShipCommand
                cmd = IssueBuildShipCommand(planet.id, "Colony Ship")
                res = self.session.handle_command(cmd)
                if res.is_valid:
                    log_info("Ship added to construction queue (via Command).")
                else:
                    log_warning(f"Build Failed: {res.message}")

    def on_design_click(self):
        log_debug("Design button clicked - opening Ship Builder")
        self.action_open_design = True

    # --- Pathfinding (for external access) ---
    def calculate_hybrid_path(self, start_hex, end_hex):
        from game.strategy.data.pathfinding import find_hybrid_path
        return find_hybrid_path(self.galaxy, start_hex, end_hex)

    # --- Private Helpers ---
    def _focus_on_player_home(self):
        from game.strategy.data.hex_math import hex_to_pixel
        if self.player_empire.colonies:
            home_colony = self.player_empire.colonies[0]
            home_sys = next((s for s in self.systems if home_colony in s.planets), None)
            if home_sys:
                target_hex = home_sys.global_location + home_colony.location
                fx, fy = hex_to_pixel(target_hex, 10)
                self.camera.position = pygame.math.Vector2(fx, fy)

    def _load_assets(self):
        # ... (existing asset loading code)
        pass

    def _get_object_asset(self, obj):
        # ... (existing asset resolution code)
        pass

    def _draw_processing_overlay(self, screen):
        # ... (existing overlay code - kept here for state access)
        pass

    def _resolve_planet_global_hex(self, planet):
        for sys in self.galaxy.systems.values():
            if planet in sys.planets:
                return sys.global_location + planet.location
        return None
```

### Step 7.2: Update Imports

Ensure backward compatibility by re-exporting from main module if needed:

```python
# At bottom of strategy_scene.py, if external code imports these
# (Optional, only if needed for compatibility)
```

### Step 7.3: Final Test Suite

**File:** `tests/strategy/test_strategy_scene_integration.py`

```python
"""Integration tests for refactored StrategyScene."""
import pytest


class TestStrategySceneIntegration:
    """End-to-end tests for refactored scene."""

    def test_scene_initializes_with_modules(self):
        """Scene should initialize all sub-modules."""
        pass

    def test_scene_draws_without_error(self):
        """Scene.draw should complete without errors."""
        pass

    def test_scene_handles_full_turn_cycle(self):
        """Full turn cycle should process correctly."""
        pass

    def test_colonize_workflow_end_to_end(self):
        """Complete colonization workflow should work."""
        pass

    def test_fleet_movement_end_to_end(self):
        """Complete fleet movement workflow should work."""
        pass
```

---

## Implementation Checklist

### Phase 1: Setup (Day 1)
- [ ] Create test file `tests/strategy/test_strategy_scene_split.py`
- [ ] Write behavior-capturing tests for current implementation
- [ ] Run tests to establish baseline

### Phase 2: Renderer (Days 2-3)
- [ ] Create `tests/unit/ui/test_strategy_renderer.py`
- [ ] Write renderer unit tests
- [ ] Create `game/ui/screens/strategy_renderer.py`
- [ ] Move all `_draw_*` methods
- [ ] Update `StrategyScene.draw()` to delegate
- [ ] Run all tests - verify passing

### Phase 3: Camera Navigation (Day 4)
- [ ] Create `tests/unit/ui/test_strategy_camera_nav.py`
- [ ] Write camera nav unit tests
- [ ] Create `game/ui/screens/strategy_camera_nav.py`
- [ ] Move `center_camera_on`, `_zoom_to_*`, `cycle_selection`
- [ ] Update `StrategyScene` to delegate
- [ ] Run all tests - verify passing

### Phase 4: Fleet Operations (Day 5)
- [ ] Create `tests/strategy/test_strategy_fleet_ops.py`
- [ ] Write fleet ops unit tests
- [ ] Create `game/ui/screens/strategy_fleet_ops.py`
- [ ] Move fleet movement methods
- [ ] Update `StrategyScene` to delegate
- [ ] Run all tests - verify passing

### Phase 5: Colonization (Day 6)
- [ ] Create `tests/strategy/test_strategy_colonization.py`
- [ ] Write colonization unit tests
- [ ] Create `game/ui/screens/strategy_colonization.py`
- [ ] Move colonization methods (FIX DUPLICATE!)
- [ ] Update `StrategyScene` to delegate
- [ ] Run all tests - verify passing

### Phase 6: Input Handler (Days 7-8)
- [ ] Create `tests/unit/ui/test_strategy_input_handler.py`
- [ ] Write input handler unit tests
- [ ] Create `game/ui/screens/strategy_input_handler.py`
- [ ] Move input handling methods
- [ ] Update `StrategyScene` to delegate
- [ ] Run all tests - verify passing

### Phase 7: Integration (Day 9)
- [ ] Create `tests/strategy/test_strategy_scene_integration.py`
- [ ] Write integration tests
- [ ] Final cleanup of `strategy_scene.py`
- [ ] Remove dead code
- [ ] Run full test suite
- [ ] Manual testing

---

## Risk Mitigation

### Circular Import Prevention
- Use late imports inside methods where needed
- Avoid cross-module dependencies between extracted modules
- All modules reference `scene` (parent), not each other

### State Synchronization
- `input_mode` is managed by `InputHandler` but exposed via property on `StrategyScene`
- Selection state stays in `StrategyScene` as single source of truth
- Sub-modules read state, scene updates state

### Backward Compatibility
- `StrategyScene` public interface unchanged
- Methods like `handle_click`, `draw`, `update` still exist
- Internal delegation is transparent to callers

---

## Success Criteria

After refactoring:
- [ ] `strategy_scene.py` is under 500 lines
- [ ] All 6 modules have clear single responsibility
- [ ] All existing tests pass
- [ ] New unit tests cover extracted modules
- [ ] No circular imports
- [ ] Manual playthrough shows no regressions
