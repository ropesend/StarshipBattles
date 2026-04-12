import os
import pygame
pygame.init()
pygame.display.set_mode((100, 100))

from game.ui.services.modifier_icon_service import ModifierIconService
from game.simulation.components.component_loader import load_modifiers_data, load_components_data

def test():
    service = ModifierIconService(icon_size=26)
    
    mods_to_test = ["hardened_mount", "simple_size_mount", "automation", "facing"]
    for mod in mods_to_test:
        icon = service.get_icon(mod)
        if icon:
            print(f"SUCCESS: {mod} -> {icon.get_size()}")
        else:
            print(f"FAILED to load: {mod}")

if __name__ == "__main__":
    test()
