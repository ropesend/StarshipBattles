"""
Planet generation system for star systems.

Generates planetary bodies with realistic physical properties including
mass distribution, moons, atmospheres, and resources.
"""
import random
import math
from typing import List, Dict

from game.core.constants import PLANET_RESOURCES
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.hex_math import HexCoord, hex_ring
from game.strategy.data.physics import calculate_incident_radiation
from game.strategy.data.stars import Star
from game.strategy.data.planet_physics import (
    MASS_CERES, MASS_MOON, MASS_MARS, MASS_EARTH, MASS_NEPTUNE, MASS_JUPITER, ATM_TO_PA, GASES,
    calculate_radius_density_from_mass, calculate_escape_velocity,
    calculate_surface_gravity, calculate_surface_area, calculate_blackbody_temperature
)
from game.strategy.data.planet_atmosphere import generate_atmosphere
from game.strategy.data.planet_naming import assign_body_names


class PlanetGenerator:
    """Generator for creating planetary bodies within star systems."""

    def __init__(self):
        pass

    def generate_system_bodies(self, system_name: str, stars: List[Star]) -> List[Planet]:
        """
        Generate all planetary bodies for a system.

        Args:
            system_name: Name of the star system
            stars: List of stars in the system

        Returns:
            List of Planet objects with assigned names
        """
        bodies = []

        # Determine orbital slots and their masses
        occupied_slots = self._generate_orbital_slots(stars)

        # Generate moons for each primary body
        self._generate_moons(occupied_slots)

        # Create Planet objects for each mass
        bodies = self._create_planet_objects(occupied_slots, stars)

        # Assign names based on distance and mass
        assign_body_names(bodies, system_name)

        return bodies

    def _generate_orbital_slots(self, stars: List[Star]) -> Dict[HexCoord, List[float]]:
        """
        Generate primary orbital slots with masses.

        Returns dict mapping location to list of masses at that location.
        """
        primary = stars[0]
        safe_start = int(primary.diameter_hexes / 2) + 2
        max_dist = 20

        # 3-10 occupied hexes (fewer locations, more bodies per location)
        primary_count = random.randint(3, 10)

        occupied_locations = set()
        occupied_slots = {}

        for _ in range(primary_count):
            for attempt in range(20):
                dist = random.randint(safe_start, max_dist)
                ring_coords = hex_ring(dist)
                if not ring_coords:
                    continue
                loc = random.choice(ring_coords)
                if loc not in occupied_locations:
                    occupied_locations.add(loc)
                    mass = self._generate_mass(is_companion=False)
                    occupied_slots[loc] = [mass]
                    break

        return occupied_slots

    def _generate_moons(self, occupied_slots: Dict[HexCoord, List[float]]) -> None:
        """
        Generate moons/co-orbitals for each primary body.

        Larger primaries have higher chance of additional bodies.
        Moon mass is normally distributed around 10% of primary mass.
        """
        for loc, masses in occupied_slots.items():
            primary_mass = masses[0]

            # Calculate chance based on primary mass (log interpolation)
            chance = self._calculate_moon_chance(primary_mass)

            # Keep rolling for additional moons
            while random.random() < chance:
                if len(masses) > 50:
                    break

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
        # Physical properties
        radius, density = calculate_radius_density_from_mass(mass)
        gravity = calculate_surface_gravity(mass, radius)
        surface_area = calculate_surface_area(radius)

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
            resources=self._generate_resources(mass)
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
        """
        # Gas Giants & Ice Giants (> 10 Earth Masses approx)
        if mass > 6.0e24:
            # Chthonian: Large stripped core. High Temp OR Low Pressure (stripped)
            # Relaxed: Mass > Super Earth, Hot, Low Pressure relative to mass
            if temp > 600 and pressure < 10000:
                return PlanetType.CHTHONIAN
            
            if mass > 1.0e26:
                return PlanetType.JOVIAN
                
            return PlanetType.ICE_GIANT

        # Dwarf Planets & Planetoids (< Mercury Mass approx)
        if mass < 2.0e23:
            # If it's cold, it's an Ice Dwarf (Pluto/Eris)
            if temp < 170:
                return PlanetType.ICE_DWARF
            # If it's hot/warm, it's a rocky Planetoid (Ceres/Vesta)
            return PlanetType.PLANETOID


        # Terrestrial / Rocky range (Mercury sized to Super-Earth)
        
        # 1. Extreme Heat / Magma
        if temp > 700 or (temp > 350 and activity > 0.7):
            return PlanetType.MAGMA

        # 2. Barren / Dead Worlds
        # Low pressure (vacuum)
        if pressure < 500:
            # If it's cold, it could still be barren rock if no ice, 
            # but usually cold + no atm = ice surface (unless stripped).
            # Let's say if temp < 200 it's Cryo (Ice covered rock), else Barren (Rock)
            if temp < 200:
                return PlanetType.CRYOPLANET
            return PlanetType.BARREN

        # 3. Water / Ice
        
        # Frozen?
        if temp < 255:
            return PlanetType.CRYOPLANET
            
        # Liquid Water Heavy?
        if water > 0.85:
            return PlanetType.PELAGIC
            
        # Arid? (Low water OR High Pressure Greenhouse Desert)
        if water < 0.20:
             # If pressure is HUGE and Hot -> Venus-like (Arid/Barren distinction?)
             # Venus is arguably "Volcanic/Barren" or "Super-Arid". 
             # Let's map Venus (High Pressure, Hot) to Arid if not Magma.
             return PlanetType.ARID

        # Continental
        # Moderate water, habitable-ish zone temps (liquids exist)
        if 255 <= temp <= 330 and pressure > 5000:
             return PlanetType.CONTINENTAL
             
        # Catch-all for habitable-adjacent
        if temp < 350 and water > 0.1:
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
