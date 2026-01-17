import pygame
import os

# Base directory for assets
BASE_DIR = "assets" # Change to "assets" if that's where the game looks
# Wait, the plan says "resources/images/..."
# Let's check where the game usually keeps images.

RESOURCES_DIR = os.path.join("Resources") # Case sensitive? 

# Plan says:
# resources/images/icons/
# resources/images/portraits/

RESOURCE_DATA = {
    "metals": {"color": (128, 128, 128)},
    "organics": {"color": (0, 204, 0)},
    "vapors": {"color": (0, 204, 255)},
    "radioactives": {"color": (204, 255, 0)},
    "exotics": {"color": (204, 0, 255)}
}

def create_placeholders(base_path):
    pygame.init()
    
    icons_dir = os.path.join(base_path, "images", "icons")
    portraits_dir = os.path.join(base_path, "images", "portraits")
    
    os.makedirs(icons_dir, exist_ok=True)
    os.makedirs(portraits_dir, exist_ok=True)
    
    for name, data in RESOURCE_DATA.items():
        color = data["color"]
        
        # 1. Icon (32x32)
        icon_surf = pygame.Surface((32, 32))
        icon_surf.fill(color)
        # Draw a border
        pygame.draw.rect(icon_surf, (0, 0, 0), icon_surf.get_rect(), 1)
        pygame.image.save(icon_surf, os.path.join(icons_dir, f"resource_{name}_icon.png"))
        
        # 2. Portrait (256x256)
        portrait_surf = pygame.Surface((256, 256))
        portrait_surf.fill(color)
        # Draw a border
        pygame.draw.rect(portrait_surf, (0, 0, 0), portrait_surf.get_rect(), 4)
        pygame.image.save(portrait_surf, os.path.join(portraits_dir, f"resource_{name}_portrait.png"))
        
    print(f"Placeholders created in {base_path}")
    pygame.quit()

if __name__ == "__main__":
    # Check current directory for Resources or assets
    if os.path.exists("Resources"):
        create_placeholders("Resources")
    elif os.path.exists("assets"):
        create_placeholders("assets")
    else:
        # Create Resources directory if none exist
        os.makedirs("Resources", exist_ok=True)
        create_placeholders("Resources")
