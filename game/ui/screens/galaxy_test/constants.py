"""Constants for the Galaxy Test Screen.

Contains layout constants and planet type colors for visualization.
"""

from game.strategy.data.planet import PlanetType


# Layout constants
SIDEBAR_WIDTH = 320
HEX_SIZE = 10.0


# Planet type colors for visualization
PLANET_TYPE_COLORS = {
    PlanetType.CONTINENTAL: (70, 130, 70),   # Green-ish (Earth-like)
    PlanetType.ARID: (180, 140, 80),         # Sandy brown
    PlanetType.PELAGIC: (50, 80, 180),       # Deep blue (Ocean)
    PlanetType.MAGMA: (200, 50, 30),         # Red-orange (Lava)
    PlanetType.CRYOPLANET: (180, 200, 220),  # Ice white-blue
    PlanetType.BARREN: (130, 130, 130),      # Grey (Rock)
    PlanetType.JOVIAN: (200, 160, 100),      # Jupiter tan
    PlanetType.ICE_GIANT: (100, 150, 200),   # Neptune blue
    PlanetType.CHTHONIAN: (100, 80, 60),     # Dark brown
    PlanetType.ICE_DWARF: (200, 210, 230),   # Light ice
    PlanetType.PLANETOID: (90, 90, 90),      # Dark grey
}
