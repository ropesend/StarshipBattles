
import os
import pygame

moves = [
    (r"C:/Users/rossr/.gemini/antigravity/brain/a441fe2f-fe2a-4fe3-b565-5c2b804a882b/federation_heavy_fighter_portrait_1767049083270.png", r"c:\Dev\StarshipBattles\Resources\ShipThemes\Federation\Portraits\HeavyFighter_Portrait.jpg"),
    (r"C:/Users/rossr/.gemini/antigravity/brain/a441fe2f-fe2a-4fe3-b565-5c2b804a882b/romulan_large_satellite_portrait_1767049096698.png", r"c:\Dev\StarshipBattles\Resources\ShipThemes\Romulans\Portraits\LargeSatellite_Portrait.jpg"),
    (r"C:/Users/rossr/.gemini/antigravity/brain/a441fe2f-fe2a-4fe3-b565-5c2b804a882b/klingon_small_fighter_portrait_1767049110665.png", r"c:\Dev\StarshipBattles\Resources\ShipThemes\Klingons\Portraits\SmallFighter_Portrait.jpg")
]

pygame.init()
for src, dst in moves:
    try:
        if os.path.exists(src):
            print(f"Processing {src} -> {dst}")
            img = pygame.image.load(src)
            pygame.image.save(img, dst)
            print("Success")
        else:
            print(f"Source not found: {src}")
    except Exception as e:
        print(f"Error: {e}")
pygame.quit()
