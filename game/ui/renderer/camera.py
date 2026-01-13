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
        self.min_zoom = 0.01
        self.max_zoom = 5.0
        self.target = None # Object to follow (must have .position)
        
    def update(self, dt):
        """Update camera validation and target following."""
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
                # 1. Get mouse position and convert to world coords BEFORE zoom
                mx, my = pygame.mouse.get_pos()
                current_mouse_world_pos = self.screen_to_world((mx, my))

                # 2. Apply Zoom
                if event.y > 0:
                    self.zoom *= 1.1
                else:
                    self.zoom /= 1.1
                
                self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

                # 3. Calculate where that world point is NOW on the screen
                # The camera position (center) hasn't moved yet, so the screen position
                # of our target world point will have drifted.
                new_mouse_world_pos = self.screen_to_world((mx, my))
                
                # 4. We want new_mouse_world_pos to be equal to current_mouse_world_pos
                # The difference is how much we need to shift the camera center.
                # If new_mouse_world_pos < current_mouse_world_pos (e.g. 100 < 200),
                # it means the camera center is too far "left" in world space (relative to where it should be).
                # Wait, let's use the vectors directly.
                # diff = old_world_pos - new_world_pos_with_old_center
                # We need to ADD this difference to the camera position.
                
                diff = current_mouse_world_pos - new_mouse_world_pos
                self.position += diff

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
