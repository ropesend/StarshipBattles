import pygame
import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sprites import SpriteManager

def main():
    pygame.init()
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visual Sprite Test - Press SPACE to Toggle Mode")
    
    clock = pygame.time.Clock()
    
    # Load Sprites
    mgr = SpriteManager.get_instance()
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # We use load_sprites now
    mgr.load_sprites(base_path)
    
    # For visualization of full atlas, we need to manually load it if we want to show it
    # But since we are moving away from atlas, maybe we just show the sprites?
    # Or try to load the fallback atlas for visualization purpose if it exists?
    atlas_path = os.path.join(base_path, "resources", "images", "Components.bmp")
    if os.path.exists(atlas_path):
        try:
             mgr.atlas = pygame.image.load(atlas_path).convert()
        except (FileNotFoundError, pygame.error):
             pass 
    
    # mgr.load_atlas(atlas_path) # Deprecated
    
    show_atlas = True
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    show_atlas = not show_atlas
        
        screen.fill((20, 20, 30))
        
        if show_atlas:
            # Draw Full Atlas
            if mgr.atlas:
                screen.blit(mgr.atlas, (50, 50))
                
                # Draw outline
                pygame.draw.rect(screen, (255, 255, 0), (50, 50, mgr.atlas.get_width(), mgr.atlas.get_height()), 2)
                
                font = pygame.font.SysFont("Arial", 24)
                text = font.render(f"Full Atlas ({mgr.atlas.get_width()}x{mgr.atlas.get_height()}) - Press SPACE", True, (255, 255, 255))
                screen.blit(text, (50, 10))
            else:
                font = pygame.font.SysFont("Arial", 24)
                text = font.render("Atlas Failed to Load", True, (255, 0, 0))
                screen.blit(text, (50, 50))
                
        else:
            # Draw Individual Sprites Grid
            font = pygame.font.SysFont("Arial", 24)
            text = font.render(f"Sliced Sprites ({len(mgr.sprites)}) - Press SPACE", True, (255, 255, 255))
            screen.blit(text, (50, 10))
            
            x_start = 50
            y_start = 50
            x = x_start
            y = y_start
            
            for i, sprite in enumerate(mgr.sprites):
                screen.blit(sprite, (x, y))
                # Draw border
                pygame.draw.rect(screen, (50, 50, 50), (x, y, 36, 36), 1)
                
                x += 38 # 36 + padding
                if x > WIDTH - 50:
                    x = x_start
                    y += 38
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
