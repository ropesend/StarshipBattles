"""
ResearchTreeScene - Main scene for the stochastic tech tree research sandbox.

Provides a full-screen interface with:
- Pannable/zoomable tech tree canvas
- Node selection and detail view
- RP allocation controls
- Turn simulation with event logging
"""
import pygame
import pygame_gui

from game.core.logger import log_info, log_debug
from game.ui.renderer.camera import Camera
from game.research.data.tech_tree import TechTree
from game.research.data.research_tracker import ResearchTracker
from game.research.systems.research_service import ResearchService
from .research_renderer import ResearchRenderer
from .research_controls import ResearchControlPanel


class ResearchTreeScene:
    """
    Full-screen scene for the research tree sandbox.

    Manages:
    - Tech tree loading and resolution
    - Camera for pan/zoom
    - Node layout calculation
    - Input handling
    - UI panels
    """

    # Layout constants
    SIDEBAR_WIDTH = 350
    COLUMN_SPACING = 280
    ROW_SPACING = 100
    NODE_WIDTH = 220
    NODE_HEIGHT = 70

    def __init__(self, screen_width: int, screen_height: int, on_close_callback=None):
        """
        Initialize the research tree scene.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            on_close_callback: Function to call when closing the scene
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.on_close_callback = on_close_callback

        # Canvas area (excluding sidebar)
        self.canvas_width = screen_width - self.SIDEBAR_WIDTH
        self.canvas_height = screen_height

        # Load tech tree
        self.tech_tree = TechTree.load_from_json()

        # Create research tracker (generates session seed)
        self.tracker = ResearchTracker()

        # Resolve fuzzy requirements
        self.tech_tree.resolve_all_requirements(self.tracker.session_seed)

        # Validate tech tree
        errors = self.tech_tree.validate_requirements()
        if errors:
            for err in errors[:5]:  # Log first 5 errors
                log_info(f"TechTree validation: {err}")

        # PROJ-40/NEW-RES-005: Check for cycles in tech tree
        cycle_errors = self.tech_tree.detect_cycles()
        if cycle_errors:
            for err in cycle_errors[:5]:  # Log first 5 cycle errors
                log_info(f"TechTree validation: {err}")

        # Calculate node positions for layout
        self.node_positions = {}  # node_id -> (world_x, world_y)
        self._calculate_layout()

        # Camera for canvas pan/zoom
        self.camera = Camera(self.canvas_width, self.canvas_height)
        self.camera.min_zoom = 0.15
        self.camera.max_zoom = 2.0
        self.camera.zoom = 0.4
        self.camera.target_zoom = 0.4

        # Center camera on tree
        self._center_camera()

        # UI Manager for pygame_gui elements
        self.ui_manager = pygame_gui.UIManager((screen_width, screen_height))

        # Selected node
        self.selected_node_id = None

        # Create renderer
        self.renderer = ResearchRenderer(
            self.tech_tree,
            self.tracker,
            self.node_positions,
            self.camera,
            self.NODE_WIDTH,
            self.NODE_HEIGHT
        )

        # Create control panel
        self.control_panel = ResearchControlPanel(
            pygame.Rect(self.canvas_width, 0, self.SIDEBAR_WIDTH, screen_height),
            self.ui_manager,
            self.tracker,
            self.tech_tree,
            on_next_turn=self._on_next_turn,
            on_close=self._on_close,
            on_reset=self._on_reset,
            on_auto_spread_changed=self._on_auto_spread_changed
        )

        log_info(f"ResearchTreeScene: Initialized with {len(self.tech_tree.nodes)} nodes")

    def _calculate_layout(self):
        """Calculate world positions for all nodes (left-to-right by depth)."""
        max_depth = self.tech_tree.get_max_depth()

        for depth in range(max_depth + 1):
            nodes_at_depth = self.tech_tree.get_nodes_at_depth(depth)

            # Sort nodes alphabetically for consistent ordering
            nodes_at_depth.sort(key=lambda n: n.name)

            for i, node in enumerate(nodes_at_depth):
                x = depth * self.COLUMN_SPACING + 150
                y = i * self.ROW_SPACING + 100
                self.node_positions[node.id] = (x, y)

        log_debug(f"ResearchTreeScene: Layout calculated for {len(self.node_positions)} nodes")

    def _center_camera(self):
        """Center the camera on the tech tree."""
        if not self.node_positions:
            return

        # Find bounding box
        min_x = min(pos[0] for pos in self.node_positions.values())
        max_x = max(pos[0] for pos in self.node_positions.values())
        min_y = min(pos[1] for pos in self.node_positions.values())
        max_y = max(pos[1] for pos in self.node_positions.values())

        # Center on middle of tree
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.camera.position = pygame.math.Vector2(center_x, center_y)

    def update(self, dt: float):
        """
        Update the scene.

        Args:
            dt: Delta time in seconds
        """
        self.camera.update(dt)
        self.ui_manager.update(dt)

    def draw(self, screen: pygame.Surface):
        """
        Draw the scene.

        Args:
            screen: pygame surface to draw on
        """
        # Clear background
        screen.fill((20, 25, 35))

        # Draw canvas area background
        canvas_rect = pygame.Rect(0, 0, self.canvas_width, self.canvas_height)
        pygame.draw.rect(screen, (15, 20, 30), canvas_rect)

        # Draw tech tree on canvas
        self.renderer.draw(screen, self.selected_node_id, canvas_rect)

        # Draw sidebar background
        sidebar_rect = pygame.Rect(self.canvas_width, 0, self.SIDEBAR_WIDTH, self.screen_height)
        pygame.draw.rect(screen, (30, 35, 45), sidebar_rect)

        # Draw pygame_gui elements
        self.ui_manager.draw_ui(screen)

    def handle_event(self, event: pygame.event):
        """
        Handle pygame events.

        Args:
            event: pygame event
        """
        # Let pygame_gui handle its events first
        if self.ui_manager.process_events(event):
            return

        # Handle control panel events
        if self.control_panel.handle_event(event, self.selected_node_id, self.tech_tree):
            return

        # ESC to close
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._on_close()
                return

        # Mouse events for canvas interaction
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if mx < self.canvas_width:  # Only handle clicks on canvas
                if event.button == 1:  # Left click
                    self._handle_click(mx, my)

        # Pass scroll events to camera (only when over canvas)
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if mx < self.canvas_width:
                self.camera.update_input(0, [event])

    def handle_resize(self, width: int, height: int):
        """
        Handle window resize.

        Args:
            width: New width
            height: New height
        """
        self.screen_width = width
        self.screen_height = height
        self.canvas_width = width - self.SIDEBAR_WIDTH
        self.canvas_height = height

        # Update camera viewport
        self.camera.width = self.canvas_width
        self.camera.height = self.canvas_height

        # Recreate UI manager with new size
        self.ui_manager = pygame_gui.UIManager((width, height))

        # Recreate control panel
        self.control_panel = ResearchControlPanel(
            pygame.Rect(self.canvas_width, 0, self.SIDEBAR_WIDTH, height),
            self.ui_manager,
            self.tracker,
            self.tech_tree,
            on_next_turn=self._on_next_turn,
            on_close=self._on_close,
            on_reset=self._on_reset,
            on_auto_spread_changed=self._on_auto_spread_changed
        )

        # Update selection if still valid
        if self.selected_node_id:
            node = self.tech_tree.get_node(self.selected_node_id)
            if node:
                self.control_panel.update_selected_node(node, self.tracker)

    def _handle_click(self, mx: int, my: int):
        """
        Handle canvas click for node selection.

        Args:
            mx: Mouse x position
            my: Mouse y position
        """
        # Convert screen to world coordinates
        world_pos = self.camera.screen_to_world((mx, my))

        # Check if clicked on a node
        clicked_node_id = self._get_node_at_position(world_pos)

        if clicked_node_id:
            self.selected_node_id = clicked_node_id
            node = self.tech_tree.get_node(clicked_node_id)
            if node:
                self.control_panel.update_selected_node(node, self.tracker)
                log_debug(f"Selected node: {node.name}")
        else:
            # Clicked empty space - deselect
            self.selected_node_id = None
            self.control_panel.clear_selection()

    def _get_node_at_position(self, world_pos: pygame.math.Vector2) -> str:
        """
        Find which node (if any) is at the given world position.

        Args:
            world_pos: Position in world coordinates

        Returns:
            Node ID if found, None otherwise
        """
        half_w = self.NODE_WIDTH / 2
        half_h = self.NODE_HEIGHT / 2

        for node_id, (nx, ny) in self.node_positions.items():
            if (nx - half_w <= world_pos.x <= nx + half_w and
                ny - half_h <= world_pos.y <= ny + half_h):
                return node_id

        return None

    def _on_next_turn(self):
        """Process one turn of research."""
        # Cache tech_levels once for performance (avoid recomputing)
        tech_levels = self.tracker.get_all_tech_levels()

        # If auto-spread is enabled, recalculate allocations before processing
        if self.tracker.auto_spread_enabled:
            self.tracker.spread_rp_evenly(self.tech_tree, tech_levels)
            self.control_panel.update_budget_display()

        events = ResearchService.process_turn(self.tech_tree, self.tracker, tech_levels)

        # Update control panel with results
        self.control_panel.update_turn_log(events, self.tracker.turn_number)

        # Update selected node if still selected
        if self.selected_node_id:
            node = self.tech_tree.get_node(self.selected_node_id)
            if node:
                self.control_panel.update_selected_node(node, self.tracker)

        log_info(f"Turn {self.tracker.turn_number}: {len(events)} events")

    def _on_close(self):
        """Close the scene."""
        log_info("ResearchTreeScene: Closing")
        if self.on_close_callback:
            self.on_close_callback()

    def _on_reset(self):
        """Reset the research session."""
        log_info("ResearchTreeScene: Resetting session")

        # Generate new session seed
        self.tracker = ResearchTracker()

        # Re-resolve fuzzy requirements
        self.tech_tree.resolve_all_requirements(self.tracker.session_seed)

        # Clear selection
        self.selected_node_id = None

        # Update control panel via proper reset method (RES-01 fix)
        self.control_panel.reset(self.tracker, self.tech_tree)

    def _on_auto_spread_changed(self, enabled: bool):
        """Handle auto-spread toggle change."""
        log_debug(f"Auto-spread {'enabled' if enabled else 'disabled'}")

        # Update selected node display if one is selected
        if self.selected_node_id:
            node = self.tech_tree.get_node(self.selected_node_id)
            if node:
                self.control_panel.update_selected_node(node, self.tracker)

    def handle_input(self, dt: float, events: list):
        """
        Handle continuous input (keyboard pan).

        Args:
            dt: Delta time
            events: List of pygame events
        """
        # Let camera handle keyboard pan
        mx, my = pygame.mouse.get_pos()

        # Only handle input when mouse is over canvas
        if mx < self.canvas_width:
            self.camera.update_input(dt, events)
