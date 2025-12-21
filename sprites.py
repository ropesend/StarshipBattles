import pygame
import os

class SpriteManager:
    _instance = None
    
    def __init__(self):
         self.atlas = None
         self.sprites = []
         self.tile_size = 36
         
    @staticmethod
    def get_instance():
        if SpriteManager._instance is None:
            SpriteManager._instance = SpriteManager()
        return SpriteManager._instance

    def load_atlas(self, path):

        if not os.path.exists(path):
            print(f"ERROR: Atlas file not found at {path}")
            return
            
        try:
            # For BMP, usually convert() is safer than convert_alpha() unless it's 32-bit BMP
            self.atlas = pygame.image.load(path).convert() 
            # Assume black is transparent for now? Or Magenta? 
            # Let's auto-detect top-left pixel or just no transparency key for now
            self.atlas.set_colorkey((0, 0, 0)) # Common for BMP sprites
            
            self._slice_sprites()
            print(f"SUCCESS: Loaded Atlas: {path} ({self.atlas.get_width()}x{self.atlas.get_height()})")

        except Exception as e:
            print(f"ERROR: Exception loading atlas: {e}")
            import traceback
            traceback.print_exc()

    def _slice_sprites(self):
        self.sprites = []
        if not self.atlas: return
        
        cols = self.atlas.get_width() // self.tile_size
        rows = self.atlas.get_height() // self.tile_size
        
        # Assume generic grid order: left to right, top to bottom
        for y in range(rows):
            for x in range(cols):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                self.sprites.append(self.atlas.subsurface(rect))

    def get_sprite(self, index):
        if 0 <= index < len(self.sprites):
            return self.sprites[index]
        return None # Should handle missing sprite ideally
