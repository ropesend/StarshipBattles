from ship import Ship
from components import create_component, LayerType

def create_brick(x, y):
    ship = Ship("The Brick", x, y, (150, 150, 150))
    
    ship.add_component(create_component("bridge"), LayerType.CORE)
    
    for _ in range(15):
         ship.add_component(create_component("armor_plate"), LayerType.ARMOR)
         
    ship.add_component(create_component("railgun"), LayerType.OUTER)
    ship.add_component(create_component("standard_engine"), LayerType.INNER)
    ship.add_component(create_component("standard_engine"), LayerType.INNER)
    ship.add_component(create_component("thruster"), LayerType.INNER)
    ship.add_component(create_component("thruster"), LayerType.INNER)
    
    ship.add_component(create_component("fuel_tank"), LayerType.CORE)
    ship.add_component(create_component("ordnance_tank"), LayerType.CORE)
    
    return ship

def create_interceptor(x, y):
    ship = Ship("The Interceptor", x, y, (50, 200, 50))
    
    ship.add_component(create_component("bridge"), LayerType.CORE)
    
    ship.add_component(create_component("railgun"), LayerType.OUTER)
    ship.add_component(create_component("railgun"), LayerType.OUTER)
    
    ship.add_component(create_component("standard_engine"), LayerType.INNER)
    ship.add_component(create_component("standard_engine"), LayerType.INNER)
    ship.add_component(create_component("standard_engine"), LayerType.OUTER)
    ship.add_component(create_component("standard_engine"), LayerType.OUTER)
    
    for _ in range(6):
        ship.add_component(create_component("thruster"), LayerType.INNER)
        
    ship.add_component(create_component("fuel_tank"), LayerType.CORE)
    ship.add_component(create_component("fuel_tank"), LayerType.INNER)
    ship.add_component(create_component("ordnance_tank"), LayerType.CORE)
    ship.add_component(create_component("ordnance_tank"), LayerType.INNER)
    
    return ship
