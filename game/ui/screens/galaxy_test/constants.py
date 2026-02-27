"""Constants for the Galaxy Test Screen.

Contains layout constants and planet type colors for visualization.
"""

from game.strategy.data.planet import PlanetType
from game.ui.colors import (
    PLANET_CONTINENTAL, PLANET_ARID, PLANET_PELAGIC, PLANET_MAGMA,
    PLANET_CRYO, PLANET_BARREN, PLANET_JOVIAN, PLANET_ICE_GIANT,
    PLANET_CHTHONIAN, PLANET_ICE_DWARF, PLANET_PLANETOID
)


# Layout constants
SIDEBAR_WIDTH = 320
HEX_SIZE = 10.0


# Planet type colors for visualization
PLANET_TYPE_COLORS = {
    PlanetType.CONTINENTAL: PLANET_CONTINENTAL,
    PlanetType.ARID: PLANET_ARID,
    PlanetType.PELAGIC: PLANET_PELAGIC,
    PlanetType.MAGMA: PLANET_MAGMA,
    PlanetType.CRYOPLANET: PLANET_CRYO,
    PlanetType.BARREN: PLANET_BARREN,
    PlanetType.JOVIAN: PLANET_JOVIAN,
    PlanetType.ICE_GIANT: PLANET_ICE_GIANT,
    PlanetType.CHTHONIAN: PLANET_CHTHONIAN,
    PlanetType.ICE_DWARF: PLANET_ICE_DWARF,
    PlanetType.PLANETOID: PLANET_PLANETOID,
}
