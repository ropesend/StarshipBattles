"""
Planet generation system for star systems.

Generates planetary bodies with realistic physical properties including
mass distribution, moons, atmospheres, and resources.
"""
import logging
import random
import math
from typing import List, Dict

logger = logging.getLogger(__name__)

from game.core.constants import PLANET_RESOURCES
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.generation.planet_image_registry import PlanetImageRegistry
from game.core.hex_math import HexCoord, hex_ring
from game.strategy.data.physics import calculate_incident_radiation
from game.strategy.data.stars import Star
from game.strategy.data.planet_physics import (
    MASS_CERES, MASS_MOON, MASS_MARS, MASS_EARTH, MASS_JUPITER,
    calculate_radius_density_from_mass, calculate_escape_velocity,
    calculate_surface_gravity, calculate_surface_area, calculate_blackbody_temperature
)
from game.strategy.data.planet_atmosphere import generate_atmosphere
from game.strategy.data.planet_naming import assign_body_names


class PlanetGenerator:
    """Generator for creating planetary bodies within star systems."""

    def __init__(self, image_registry: PlanetImageRegistry):
        """Initialize PlanetGenerator with dependencies.

        Args:
            image_registry: Registry for assigning planet images based on type.
        """
        self._image_registry = image_registry

    def generate_system_bodies(
        self,
        system_name: str,
        stars: List[Star],
        blueprint: Dict = None
    ) -> List[Planet]:
        """
        Generate all planetary bodies for a system.

        Args:
            system_name: Name of the star system
            stars: List of stars in the system
            blueprint: Optional blueprint dict with planet_count, planet_mass constraints

        Returns:
            List of Planet objects with assigned names
        """
        bodies = []

        # Determine orbital slots and their masses using blueprint constraints
        occupied_slots = self._generate_orbital_slots(stars, blueprint)

        # Generate moons for each primary body
        # If blueprint specifies max_planets, limit total body count
        if blueprint:
            planet_count_spec = blueprint.get("planet_count", {})
            if isinstance(planet_count_spec, dict):
                max_planets = planet_count_spec.get("max", 20)
            elif isinstance(planet_count_spec, int):
                max_planets = planet_count_spec
            else:
                max_planets = 20
            # Only generate moons if we have room for more bodies
            current_count = sum(len(masses) for masses in occupied_slots.values())
            if current_count < max_planets:
                self._generate_moons(occupied_slots, max_total=max_planets)
        else:
            self._generate_moons(occupied_slots)

        # Create Planet objects for each mass
        bodies = self._create_planet_objects(occupied_slots, stars)

        # Assign names based on distance and mass
        assign_body_names(bodies, system_name)

        return bodies

    def _generate_orbital_slots(
        self,
        stars: List[Star],
        blueprint: Dict = None
    ) -> Dict[HexCoord, List[float]]:
        """
        Generate primary orbital slots with masses.

        Args:
            stars: List of stars in the system
            blueprint: Optional blueprint dict with planet_count, planet_mass,
                      orbital_spacing, and orbital_zones constraints

        Returns dict mapping location to list of masses at that location.
        """
        primary = stars[0]
        safe_start = int(primary.diameter_hexes / 2) + 2
        max_dist = 20

        # Get planet count from blueprint or use default 3-10
        if blueprint:
            planet_count_spec = blueprint.get("planet_count", {})
            if isinstance(planet_count_spec, int):
                primary_count = planet_count_spec
            elif isinstance(planet_count_spec, dict):
                min_count = planet_count_spec.get("min", 3)
                max_count = planet_count_spec.get("max", 10)
                primary_count = random.randint(min_count, max_count)
            else:
                primary_count = random.randint(3, 10)

            # Apply orbital spacing factor if specified
            spacing_spec = blueprint.get("orbital_spacing", {})
            if isinstance(spacing_spec, dict):
                spacing_factor = spacing_spec.get("factor", 1.0)
                max_dist = int(max_dist * spacing_factor)
                max_dist = max(safe_start + 2, max_dist)  # Ensure room for at least some orbits
        else:
            primary_count = random.randint(3, 10)

        # Handle 0 planet case
        if primary_count == 0:
            return {}

        occupied_locations = set()
        occupied_slots = {}

        # Get mass constraints from blueprint
        mass_spec = blueprint.get("planet_mass", {}) if blueprint else {}
        mass_bias = mass_spec.get("bias", None)  # "small" or "large"
        mass_min = mass_spec.get("min", MASS_CERES)
        mass_max = mass_spec.get("max", MASS_JUPITER)

        # Check if hot zone is required (hot_jupiter blueprint)
        orbital_zones = blueprint.get("orbital_zones", {}) if blueprint else {}
        hot_required = orbital_zones.get("hot_required", False)
        hot_zone_placed = False

        for i in range(primary_count):
            for attempt in range(20):
                # If hot zone required and not yet placed, force close orbit for first planet
                if hot_required and not hot_zone_placed and i == 0:
                    # Hot Jupiter: orbit distance 2-3 (very close to star)
                    dist = random.randint(safe_start, safe_start + 1)
                    dist = max(2, min(dist, 3))  # Ensure orbit 2-3
                else:
                    dist = random.randint(safe_start, max_dist)

                ring_coords = hex_ring(dist)
                if not ring_coords:
                    continue
                loc = random.choice(ring_coords)
                if loc not in occupied_locations:
                    occupied_locations.add(loc)

                    # For hot_jupiter first planet, force gas giant mass
                    if hot_required and not hot_zone_placed and i == 0:
                        # Force gas giant: 5e26 to 2e28 kg (Jupiter-like)
                        hot_mass = 10 ** random.uniform(26.7, 28.0)
                        occupied_slots[loc] = [hot_mass]
                        hot_zone_placed = True
                    else:
                        mass = self._generate_mass_constrained(mass_min, mass_max, mass_bias)
                        occupied_slots[loc] = [mass]
                    break

        return occupied_slots

    def _generate_mass_constrained(
        self,
        mass_min: float,
        mass_max: float,
        bias: str = None
    ) -> float:
        """
        Generate planet mass with constraints and optional bias.

        Args:
            mass_min: Minimum mass in kg
            mass_max: Maximum mass in kg
            bias: Optional bias - "small" for rocky planets, "large" for gas giants

        Returns:
            Mass in kg within constraints
        """
        # Determine log-normal parameters based on bias
        if bias == "small":
            # Bias towards smaller rocky planets (Mars to Super-Earth range)
            # log10(Earth) ~ 24.77, log10(Mars) ~ 23.8
            log_mu = 24.0
            log_sigma = 0.8
        elif bias == "large":
            # Bias towards gas giants (Neptune to Jupiter range)
            # log10(Neptune) ~ 26.0, log10(Jupiter) ~ 27.3
            log_mu = 26.5
            log_sigma = 0.8
        else:
            # Default distribution (weighted towards Mars - Super Earth)
            log_mu = 24.5
            log_sigma = 1.5

        log_min = math.log10(mass_min)
        log_max = math.log10(mass_max)

        # Generate mass with bias, respecting constraints
        for _ in range(100):
            log_val = random.gauss(log_mu, log_sigma)
            if log_min <= log_val <= log_max:
                return 10 ** log_val

        # Fallback: uniform in log space within constraints
        return 10 ** random.uniform(log_min, log_max)

    def _generate_moons(
        self,
        occupied_slots: Dict[HexCoord, List[float]],
        max_total: int = None
    ) -> None:
        """
        Generate moons/co-orbitals for each primary body.

        Larger primaries have higher chance of additional bodies.
        Moon mass is normally distributed around 10% of primary mass.

        Args:
            occupied_slots: Dict mapping location to list of masses
            max_total: Optional maximum total body count across all slots
        """
        for loc, masses in occupied_slots.items():
            primary_mass = masses[0]

            # Calculate chance based on primary mass (log interpolation)
            chance = self._calculate_moon_chance(primary_mass)

            # Keep rolling for additional moons
            while random.random() < chance:
                if len(masses) > 50:
                    break

                # Check max_total constraint
                if max_total is not None:
                    current_total = sum(len(m) for m in occupied_slots.values())
                    if current_total >= max_total:
                        return  # Stop all moon generation

                moon_mass = self._generate_moon_mass(primary_mass)
                masses.append(moon_mass)

    def _calculate_moon_chance(self, primary_mass: float) -> float:
        """
        Calculate probability of having additional moons.

        Jupiter-sized: 80% base chance
        Earth-sized: 10% base chance
        Ceres-sized: 1% base chance
        """
        log_m = math.log10(primary_mass)

        if log_m >= 27.27:  # Jupiter+
            chance = 0.8
        elif log_m >= 24.77:  # Earth to Jupiter
            chance = 0.1 + (log_m - 24.77) * 0.28
        elif log_m >= 20.97:  # Ceres to Earth
            chance = 0.01 + (log_m - 20.97) * 0.0237
        else:
            chance = 0.01

        return max(0.0, min(0.95, chance))

    def _generate_moon_mass(self, primary_mass: float) -> float:
        """
        Generate moon mass (normal distribution around 10% of primary).
        """
        target_mu = primary_mass * 0.10
        target_sigma = primary_mass * 0.02

        moon_mass = random.gauss(target_mu, target_sigma)

        # Floor at dwarf planet size
        if moon_mass < MASS_CERES:
            moon_mass = MASS_CERES

        # Ensure moon isn't larger than primary
        if moon_mass >= primary_mass:
            moon_mass = primary_mass * 0.5

        return moon_mass

    def _create_planet_objects(
        self,
        occupied_slots: Dict[HexCoord, List[float]],
        stars: List[Star]
    ) -> List[Planet]:
        """
        Create Planet objects from mass distributions.
        """
        bodies = []

        for loc, masses in occupied_slots.items():
            masses.sort(reverse=True)
            orbit_dist = max(abs(loc.q), abs(loc.r), abs(-loc.q - loc.r))

            # Calculate radiation and temperature for this location
            incident_spec = calculate_incident_radiation(loc, stars)
            total_flux = incident_spec.get_total_output()
            base_temp = calculate_blackbody_temperature(total_flux)

            for mass in masses:
                planet = self._create_single_planet(
                    loc, orbit_dist, mass, base_temp, total_flux
                )
                bodies.append(planet)

        return bodies

    def _create_single_planet(
        self,
        loc: HexCoord,
        orbit_dist: int,
        mass: float,
        base_temp: float,
        total_flux: float
    ) -> Planet:
        """
        Create a single Planet object with all physical properties.
        """
        from game.strategy.data.planet_physics import validate_planet_parameters

        # Physical properties
        radius, density = calculate_radius_density_from_mass(mass)
        gravity = calculate_surface_gravity(mass, radius)
        surface_area = calculate_surface_area(radius)

        # Validate physical parameters
        warnings = validate_planet_parameters(mass, radius, density)
        for warning in warnings:
            logger.warning(f"Planet at orbit {orbit_dist}: {warning}")

        # Atmosphere
        escape_vel = calculate_escape_velocity(mass, radius)
        atmosphere, pressure, final_temp = generate_atmosphere(
            mass, escape_vel, base_temp, total_flux
        )

        # Surface conditions
        water, activity, mag_field = self._generate_surface_flags(mass, final_temp)

        # Classification
        p_type = self._determine_type(
            mass, final_temp, pressure, water, atmosphere, activity
        )

        # Assign persistent image from registry
        image_id = self._image_registry.get_random_image(p_type)
        image_rotation = self._image_registry.get_random_rotation()

        return Planet(
            name="TEMP",  # Assigned later by naming pass
            location=loc,
            orbit_distance=orbit_dist,
            mass=mass,
            radius=radius,
            surface_area=surface_area,
            density=density,
            surface_gravity=gravity,
            surface_pressure=pressure,
            surface_temperature=final_temp,
            atmosphere=atmosphere,
            planet_type=p_type,
            surface_water=water,
            tectonic_activity=activity,
            magnetic_field=mag_field,
            resources=self._generate_resources(mass),
            image_id=image_id,
            image_rotation=image_rotation
        )

    def _generate_mass(self, is_companion=False, primary_mass=None) -> float:
        """
        Generate planet mass in kg using log-normal distribution.

        Range: Ceres (9e20) to Jupiter (1.9e27)
        Weighted towards Mars - Super Earth range.
        """
        min_mass = MASS_CERES
        max_mass = MASS_JUPITER

        if primary_mass:
            target_max = primary_mass * 0.4
            if target_max < min_mass:
                return min_mass
            max_mass = min(MASS_JUPITER, target_max)

        while True:
            log_val = random.gauss(24.5, 1.5)
            mass = 10 ** log_val

            if min_mass <= mass <= max_mass:
                return mass

    def _generate_surface_flags(self, mass: float, temp: float):
        """
        Generate surface water, tectonic activity, and magnetic field.
        """
        activity = 0.0
        mag_field = 0.0
        water = 0.0

        if mass > MASS_MARS:
            activity = random.uniform(0.1, 0.8)
            mag_field = random.uniform(0.5, 2.0)
        else:
            activity = random.uniform(0, 0.2)
            mag_field = random.uniform(0, 0.5)

        # Water presence based on temperature
        if 250 < temp < 350:
            water = random.uniform(0.1, 0.9)
        elif temp <= 250:
            water = random.uniform(0.1, 0.9)  # Frozen
        else:
            water = 0  # Boiled off

        return water, activity, mag_field

    def _determine_type(
        self,
        mass: float,
        temp: float,
        pressure: float,
        water: float,
        atmosphere: dict,
        activity: float = 0.0
    ) -> PlanetType:
        """
        Determine planet type based on physical properties.

        Classification thresholds are loaded from astrophysics.json via
        ClassificationConfig for data-driven configuration.
        """
        from game.strategy.data.classification_config import get_classification_config
        cfg = get_classification_config()

        # Gas Giants & Ice Giants (> 10 Earth Masses approx)
        if mass > cfg.giant_min:
            # Chthonian: Large stripped core. High Temp OR Low Pressure (stripped)
            if temp > 600 and pressure < cfg.chthonian_max:
                return PlanetType.CHTHONIAN

            if mass > cfg.gas_giant_min:
                return PlanetType.JOVIAN

            return PlanetType.ICE_GIANT

        # Dwarf Planets & Planetoids (< Mercury Mass approx)
        if mass < cfg.dwarf_max:
            # If it's cold, it's an Ice Dwarf (Pluto/Eris)
            if temp < cfg.ice_dwarf_max:
                return PlanetType.ICE_DWARF
            # If it's hot/warm, it's a rocky Planetoid (Ceres/Vesta)
            return PlanetType.PLANETOID

        # Terrestrial / Rocky range (Mercury sized to Super-Earth)

        # 1. Extreme Heat / Magma
        if temp > cfg.magma or (temp > cfg.magma_activity and activity > cfg.activity_magma_threshold):
            return PlanetType.MAGMA

        # 2. Barren / Dead Worlds
        # Low pressure (vacuum)
        if pressure < cfg.vacuum:
            # If it's cold, ice surface; else barren rock
            if temp < cfg.cold_limit:
                return PlanetType.CRYOPLANET
            return PlanetType.BARREN

        # 3. Water / Ice

        # Frozen?
        if temp < cfg.cryo_max:
            return PlanetType.CRYOPLANET

        # Liquid Water Heavy?
        if water > cfg.ocean_world:
            return PlanetType.PELAGIC

        # Arid? (Low water)
        if water < cfg.arid:
            return PlanetType.ARID

        # Continental
        # Moderate water, habitable-ish zone temps (liquids exist)
        if cfg.continental_temp_min <= temp <= cfg.continental_temp_max and pressure > cfg.continental_pressure_min:
            return PlanetType.CONTINENTAL

        # Catch-all for habitable-adjacent
        if temp < 350 and water > cfg.continental_water_min:
            return PlanetType.CONTINENTAL

        if temp >= 350:
            return PlanetType.ARID

        return PlanetType.BARREN

    def _generate_resources(self, mass: float) -> dict:
        """
        Generate resources based on mass.

        Large planets: High quantity, low quality (hard to extract)
        Small planets: Low quantity, high quality (easy to extract)
        """
        resources = {}

        log_mass = math.log10(max(mass, 1.0))
        min_log = 20.0
        max_log = 28.0

        size_factor = (log_mass - min_log) / (max_log - min_log)
        size_factor = max(0.0, min(1.0, size_factor))

        for res in PLANET_RESOURCES:
            # Quantity correlates with size
            r_qty = random.random()
            qty_norm = (size_factor * 0.7) + (r_qty * 0.3)
            quantity = int(qty_norm * 1000000)

            # Quality inversely correlates with size
            qual_bias = 1.0 - size_factor
            r_qual = random.random()
            qual_norm = (qual_bias * 0.7) + (r_qual * 0.3)
            quality = qual_norm * 100.0

            resources[res] = {
                'quantity': quantity,
                'quality': quality
            }

        return resources
