"""Camera module for viewport management and coordinate transformations."""
import pygame


class Camera:
    """Handles viewport panning, zooming, and coordinate transformations."""
    
    def __init__(self, width, height, offset_x=0, offset_y=0):
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.position = pygame.math.Vector2(0, 0)
        self.zoom = 1.0
        self.target_zoom = 1.0  # Target for smooth zoom interpolation
        self.zoom_speed = 8.0   # How fast zoom animates (higher = faster)
        self.min_zoom = 0.01
        self.max_zoom = 5.0
        self.target = None # Object to follow (must have .position)
        # For mouse-centered zoom, store the world position to keep stable
        self._zoom_anchor_world = None
        self._zoom_anchor_screen = None
        
    def update(self, dt):
        """Update camera validation, target following, and smooth zoom."""
        # Smooth zoom interpolation
        if abs(self.zoom - self.target_zoom) > 0.001:
            # Exponential interpolation for smooth feel
            self.zoom += (self.target_zoom - self.zoom) * min(1.0, self.zoom_speed * dt)
            
            # Keep the zoom anchor point stable on screen during animation
            if self._zoom_anchor_world is not None and self._zoom_anchor_screen is not None:
                new_world_at_anchor = self.screen_to_world(self._zoom_anchor_screen)
                diff = self._zoom_anchor_world - new_world_at_anchor
                self.position += diff
        else:
            self.zoom = self.target_zoom
            self._zoom_anchor_world = None
            self._zoom_anchor_screen = None
        
        # Update target following
        if self.target:
             if hasattr(self.target, 'is_alive') and not self.target.is_alive:
                 pass # Keep looking at dead ship position
             self.position = pygame.math.Vector2(self.target.position)
             
    def update_input(self, dt, events):
        """Handle keyboard and mouse input for camera movement."""
        keys = pygame.key.get_pressed()
        speed = 1000 / self.zoom  # Pan faster when zoomed out
        
        move = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: move.x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move.x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: move.y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: move.y = 1
        
        if move.length() > 0:
            self.position += move.normalize() * speed * dt
            self.target = None # Break focus on manual move

        # Middle Mouse Panning (or Left Click Drag if implemented later, usually Middle is pan)
        if pygame.mouse.get_pressed()[1]:
            rel = pygame.mouse.get_rel()
            delta = pygame.math.Vector2(rel) / self.zoom
            self.position -= delta
            self.target = None # Break focus
        else:
            pygame.mouse.get_rel()  # clear relative movement

        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                # 1. Get mouse position and store as anchor for smooth zoom
                mx, my = pygame.mouse.get_pos()
                self._zoom_anchor_screen = (mx, my)
                self._zoom_anchor_world = self.screen_to_world((mx, my))

                # 2. Set Target Zoom (will be interpolated smoothly in update())
                if event.y > 0:
                    self.target_zoom *= 1.15
                else:
                    self.target_zoom /= 1.15
                
                self.target_zoom = max(self.min_zoom, min(self.max_zoom, self.target_zoom))

    def world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates."""
        # Center of the VIEWPORT (not screen)
        screen_center = pygame.math.Vector2(self.width / 2, self.height / 2)
        offset = (world_pos - self.position) * self.zoom
        
        # Result is relative to Viewport Top-Left. Add viewport offset.
        return screen_center + offset + pygame.math.Vector2(self.offset_x, self.offset_y)

    def screen_to_world(self, screen_pos):
        """Convert screen coordinates to world coordinates."""
        # Remove Viewport Offset first to get coordinate relative to Viewport
        local_pos = pygame.math.Vector2(screen_pos) - pygame.math.Vector2(self.offset_x, self.offset_y)
        
        screen_center = pygame.math.Vector2(self.width / 2, self.height / 2)
        offset = local_pos - screen_center
        return self.position + (offset / self.zoom)

    def fit_objects(self, objects):
        """Adjust camera to fit all objects in view."""
        if not objects:
            return
        
        min_x = min(o.position.x for o in objects)
        max_x = max(o.position.x for o in objects)
        min_y = min(o.position.y for o in objects)
        max_y = max(o.position.y for o in objects)
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.position = pygame.math.Vector2(center_x, center_y)
        
        # Calculate fit zoom
        width = max_x - min_x + 500  # Margin
        height = max_y - min_y + 500
        
        zoom_x = self.width / width
        zoom_y = self.height / height
        self.zoom = min(zoom_x, zoom_y)
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))
