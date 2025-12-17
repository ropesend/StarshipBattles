import pygame
import time
from ship import Ship, LayerType
from components import Generator, Tank, BeamWeapon, Bridge, Engine, Thruster, Armor
from main import draw_ship, draw_hud

# Mock Data for Components
GEN_DATA = {'id': 'gen1', 'name': 'Reactor', 'mass': 50, 'hp': 100, 'type': 'Generator', 'allowed_layers': ['CORE', 'INNER'], 'energy_generation': 50}
TANK_DATA = {'id': 'bat1', 'name': 'Battery', 'mass': 20, 'hp': 50, 'type': 'Tank', 'allowed_layers': ['INNER', 'OUTER'], 'capacity': 100, 'resource_type': 'energy'}
BEAM_DATA = {'id': 'las1', 'name': 'Laser', 'mass': 10, 'hp': 40, 'type': 'BeamWeapon', 'allowed_layers': ['OUTER'], 'damage': 10, 'range': 800, 'reload': 0.5, 'energy_cost': 20, 'base_accuracy': 1.0, 'accuracy_falloff': 0.001}
BRIDGE_DATA = {'id': 'br1', 'name': 'Bridge', 'mass': 10, 'hp': 50, 'type': 'Bridge', 'allowed_layers': ['CORE']}

def create_beam_ship(x, y, color):
    s = Ship("BeamShip", x, y, color)
    s.add_component(Bridge(BRIDGE_DATA), LayerType.CORE)
    s.add_component(Generator(GEN_DATA), LayerType.INNER)
    s.add_component(Tank(TANK_DATA), LayerType.INNER)
    s.add_component(BeamWeapon(BEAM_DATA), LayerType.OUTER)
    s.recalculate_stats()
    # Fill energy
    s.current_energy = s.max_energy
    return s

def run_test():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    attacker = create_beam_ship(200, 300, (0, 255, 255))
    target = create_beam_ship(600, 300, (255, 0, 0)) # Using same ship as target for simplicity
    
    running = True
    projectiles = []
    beams = [] # Visuals
    
    print("Test Started. Press SPACE to Fire Beam.")
    
    while running:
        dt = clock.tick(60)/1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    attacker.comp_trigger_pulled = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    attacker.comp_trigger_pulled = False
                    
        # Update
        attacker.update(dt)
        target.update(dt)
        
        # Attack Logic (Simplified from main.py)
        if hasattr(attacker, 'just_fired_projectiles'):
            for attack in attacker.just_fired_projectiles:
                if attack['type'] == 'beam':
                    print("Beam Fired!")
                    start = attack['origin']
                    direction = attack['direction']
                    r_range = attack['range']
                    end = start + direction * r_range
                    
                    # Cheat Raycast (Horizontal only for test)
                    dist = target.position.x - attacker.position.x
                    if dist <= r_range and dist > 0:
                        chance = attack['component'].calculate_hit_chance(dist)
                        print(f"Distance: {dist}, Chance: {chance}")
                        
                        beams.append({'start': start, 'end': target.position, 'timer': 0.5, 'color': (255, 255, 255)})
                    else:
                        print("Target out of range")
                        beams.append({'start': start, 'end': end, 'timer': 0.5, 'color': (100, 100, 255)})
                        
        screen.fill((20, 20, 20))
        draw_ship(screen, attacker)
        draw_ship(screen, target)
        draw_hud(screen, attacker, 10, 10)
        
        # Draw Beams
        for b in beams[:]:
            b['timer'] -= dt
            if b['timer'] <= 0:
                beams.remove(b)
            else:
                pygame.draw.line(screen, b['color'], b['start'], b['end'], 3)
                
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    run_test()
