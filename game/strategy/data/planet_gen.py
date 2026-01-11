import random
import math
from typing import List, Dict, Tuple
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.hex_math import HexCoord, hex_ring
from game.strategy.data.physics import calculate_incident_radiation
from game.strategy.data.stars import Star

# Physics Constants
G = 6.67430e-11
BOLTZMANN_K = 1.380649e-23
PROTON_MASS = 1.6726e-27
ATM_TO_PA = 101325.0

# Reference Masses (kg)
MASS_CERES = 9.39e20
MASS_MOON = 7.34e22
MASS_MERCURY = 3.30e23
MASS_MARS = 6.42e23
MASS_EARTH = 5.97e24
MASS_NEPTUNE = 1.02e26
MASS_JUPITER = 1.89e27

# Gas Properties: Molar Mass (kg/mol) approx
GASES = {
    "H2": 0.002,
    "He": 0.004,
    "CH4": 0.016,
    "NH3": 0.017,
    "H2O": 0.018,
    "N2": 0.028,
    "O2": 0.032,
    "Ar": 0.040,
    "CO2": 0.044,
    "SO2": 0.064
}

class PlanetGenerator:
    def __init__(self):
        pass

    def generate_system_bodies(self, system_name: str, stars: List[Star]) -> List[Planet]:
        """
        Generate all planetary bodies for a system.
        Returns a flat list of Planet objects.
        """
        bodies = []
        
        # 1. Determine Number of Primary "Orbit Centers" (Occupied Hexes)
        # User Request: "Decrease number of sectors with planets, but increase number of planets per sector"
        # Let's say 3 to 10 occupied hexes.
        primary_count = random.randint(3, 10)
        
        primary = stars[0]
        safe_start = int(primary.diameter_hexes / 2) + 2
        max_dist = 20
        
        occupied_locations = set()
        occupied_slots = {} # Loc -> List[Mass]
        
        # 2. Generate Primaries
        for _ in range(primary_count):
            # Find unique location
            for attempt in range(20):
                dist = random.randint(safe_start, max_dist)
                ring_coords = hex_ring(dist)
                if not ring_coords: continue
                loc = random.choice(ring_coords)
                if loc not in occupied_locations:
                    occupied_locations.add(loc)
                    
                    # Generate Mass for Primary
                    # Full range, but primary is usually significant
                    mass = self._generate_mass(is_companion=False)
                    occupied_slots[loc] = [mass]
                    break
        
        # 3. Generate Moons / Co-orbitals for each Primary
        for loc, masses in occupied_slots.items():
            primary_mass = masses[0]
            
            # User Algorithm:
            # "For a jupitor sized massed planet have the odds of a aditional planet be 80%... 
            # keep rolling the dice for each additional planet."
            # "Earth mass planet it is 10% to start... ceries would be about 1%."
            
            # Linear Log Interpolation for Base Chance
            # Log10(Jupiter=1.89e27) = 27.27 -> 0.80
            # Log10(Earth=5.97e24) = 24.77 -> 0.10
            # Log10(Ceres=9.39e20) = 20.97 -> 0.01
            
            log_m = math.log10(primary_mass)
            
            # Piecewise Linear Interpolation
            if log_m >= 27.27:
                 chance = 0.8
            elif log_m >= 24.77:
                 # Interp between Earth and Jupiter
                 # Slope = (0.8 - 0.1) / (27.27 - 24.77) = 0.7 / 2.5 = 0.28
                 chance = 0.1 + (log_m - 24.77) * 0.28
            elif log_m >= 20.97:
                 # Interp between Ceres and Earth
                 # Slope = (0.1 - 0.01) / (24.77 - 20.97) = 0.09 / 3.8 = 0.0237
                 chance = 0.01 + (log_m - 20.97) * 0.0237
            else:
                 chance = 0.01 # Floor
                 
            # Clamp
            chance = max(0.0, min(0.95, chance))
            
            # Keep Rolling
            while random.random() < chance:
                # Limit max moons to avoid infinite loops or memory issues (e.g. 50)
                if len(masses) > 50: break
                
                # "Size of the moons should be ... normal distibution centered around 10% of the parent planets mass"
                # Sigma? Let's assume 2% of primary mass (so 3-sigma is 4% to 16%)
                
                target_mu = primary_mass * 0.10
                target_sigma = primary_mass * 0.02 # 2% std dev
                
                moon_mass = random.gauss(target_mu, target_sigma)
                
                # Physical min mass check
                # If calculated mass < Ceres (9e20), should we discard or clamp?
                # User says "Ceries would be about 1% [chance]", implying small things exist.
                # If we clamp to MIN, we get 'Ceres' clones.
                # Let's clamp to MIN_MASS or simply discard if negative/too small?
                # "Infinite loop" issue was max < min.
                # Here we just generate value.
                
                if moon_mass < MASS_CERES: 
                     moon_mass = MASS_CERES # Floor at dwarf planet size
                     
                # Also ensure moon isn't >= primary (unlikely with 10% mean, but possible with huge sigma)
                if moon_mass >= primary_mass:
                     moon_mass = primary_mass * 0.5
                     
                masses.append(moon_mass)

        # 3. Create Planet Objects for each Mass
        for loc, masses in occupied_slots.items():
            # Sort masses descending
            masses.sort(reverse=True)
            
            orbit_dist = max(abs(loc.q), abs(loc.r), abs(-loc.q-loc.r))
            
            # Calculate Radiation / Temperature for this location
            # Using physics library
            incident_spec = calculate_incident_radiation(loc, stars)
            total_flux = incident_spec.get_total_output() # W/m^2
            
            # Determine base blackbody temp
            # Stefan-Boltzmann: P/A = sigma * T^4  => T = ((P/A)/sigma)^0.25
            # P/A is flux.
            sigma = 5.670374e-8
            base_temp = (total_flux / sigma) ** 0.25
            
            for i, mass in enumerate(masses):
                # Naming
                if i == 0:
                    suffix = "I" # Roman 1 (simplified)
                    # We could do actual roman numerals conversion if needed, but for now simple I is fine or use index+1
                    # Actually standard is b, c, d... but user asked for "System I, Ia, Ib"
                    # Wait, user said "Largest = I, others Ia, Ib". 
                    # Actually usually stars are A, B... Planets b, c, d...
                    # User request: "Planet Name I" then "Planet Name II" (Roman by distance).
                    # User update in Step 28: "System Name I", "System Name II" romans by distance.
                    # Moon update: "a large jupitor sized planet has a 80% chance of a moons... separate by naming convention with small letter a,b,c after roman numeral"
                    # So: Planet at distance X -> "System I". Moons -> "System Ia", "System Ib".
                    # But we have multiple planets at different distances.
                    # We need to assign user-visible Roman numerals based on OUTWARD DISTANCE from star, not just local sorting.
                    pass # Will handle naming in a second pass
                
                # Generate Physical Properties
                radius, density = self._calculate_radius_density_from_mass(mass)
                gravity = (G * mass) / (radius ** 2)
                surface_area = 4 * math.pi * (radius ** 2)
                
                # Atmosphere & Pressure & Greenhouse
                escape_vel = math.sqrt(2 * G * mass / radius)
                atmosphere, pressure, final_temp = self._generate_atmosphere(mass, escape_vel, base_temp, total_flux)
                
                # Surface Water / Conditions
                water, activity, mag_field = self._generate_surface_flags(mass, final_temp)
                
                # Classification
                p_type = self._determine_type(mass, final_temp, pressure, water, atmosphere, activity)
                
                p = Planet(
                    name="TEMP", # Assigned later
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
                    magnetic_field=mag_field
                )
                bodies.append(p)

        # 4. Naming Pass
        # Sort entire list by distance, then mass
        # Group by Orbit Distance (or Hex?)
        # User said: "Naming convention for planets within a system (e.g., 'System Name I', 'System Name II'), using Roman numerals based on distance."
        # "Naming convention for secondary bodies at the same location as a planet (e.g., 'Planet Name IIa', 'Planet Name IIb')."
        
        # Group bodies by Location
        bodies_by_loc = {}
        for b in bodies:
            if b.location not in bodies_by_loc:
                bodies_by_loc[b.location] = []
            bodies_by_loc[b.location].append(b)
            
        # Sort locations by distance
        sorted_locs = sorted(bodies_by_loc.keys(), key=lambda l: max(abs(l.q), abs(l.r), abs(-l.q-l.r)))
        
        planet_idx = 1
        for loc in sorted_locs:
            group = bodies_by_loc[loc]
            # Sort group by Mass Descending (Largest is Planet, others are moons)
            group.sort(key=lambda x: x.mass, reverse=True)
            
            roman = self._to_roman(planet_idx)
            base_name = f"{system_name} {roman}"
            
            # Primary
            group[0].name = base_name
            
            # Moons
            import string
            moon_suffixes = list(string.ascii_lowercase)
            for i in range(1, len(group)):
                if i-1 < len(moon_suffixes):
                     suffix = moon_suffixes[i-1]
                else:
                     suffix = f"z{i-1}" # Fallback for absurd counts
                group[i].name = f"{base_name}{suffix}"
            
            planet_idx += 1
            
        return bodies


    def _generate_mass(self, is_companion=False, primary_mass=None):
        """
        Generate Planet Mass in kg.
        Range: Ceres (9e20) to Jupiter (1.9e27).
        Weighted towards Mars (6e23) - Super Earth (1e25).
        """
        min_mass = MASS_CERES
        max_mass = MASS_JUPITER
        if primary_mass:
            # Moon should be smaller than primary (e.g. < 40%)
            target_max = primary_mass * 0.4
            
            if target_max < min_mass:
                # Primary is too small to have a strictly smaller moon that meets min_mass.
                # Return min_mass (result is a binary/double object) to avoid infinite loop.
                return min_mass
                
            max_mass = min(MASS_JUPITER, target_max)
            
        while True:
            # Log-Normal Distribution
            # We want peak around Earth/Super-Earth? 
            # Log10(Earth) = 24.7.
            # Let's try mu=24.5 (log10), sigma=1.5
            log_val = random.gauss(24.5, 1.5)
            mass = 10 ** log_val
            
            if mass < min_mass: continue
            if mass > max_mass: continue
            
            return mass

    def _calculate_radius_density_from_mass(self, mass):
        """
        Approximate radius and density from mass.
        """
        # Simplified models
        if mass > 1e26: # Gas Giant
            # Density ~ 1000-1500 kg/m^3
            density = random.uniform(900, 1600)
        elif mass > 5e24: # Earth / Super Earth
            # Density ~ 4000-6000 kg/m^3 (Iron/Rock)
            density = random.uniform(4000, 6000)
        else: # Small rocky / icy
            # Density ~ 2000-4000
            density = random.uniform(2000, 4500)
            
        # Volume = Mass / Density
        volume = mass / density
        # V = 4/3 pi r^3 => r = (3V / 4pi)^(1/3)
        radius = ((3 * volume) / (4 * math.pi)) ** (1.0/3.0)
        return radius, density

    def _generate_atmosphere(self, mass, escape_vel, base_temp, flux_wm2):
        """
        Generate composition and pressure.
        """
        # Gas Retention: Need v_rms < 1/6 v_escape for long term retention
        # v_rms = sqrt(3kT / m)
        # Check specific gases
        
        composition = {}
        
        # Temp estimate for gas retention (Exosphere is hotter than surface usually)
        # Using base_temp is a simplistic approx.
        retention_temp = base_temp * 1.5 if base_temp > 0 else 50
        
        retained_gases = []
        for gas_name, molar_kg in GASES.items():
            molecular_mass_kg = molar_kg / 6.022e23
            v_rms = math.sqrt(3 * BOLTZMANN_K * retention_temp / molecular_mass_kg)
            if v_rms < (escape_vel / 6.0):
                retained_gases.append(gas_name)
                
        if not retained_gases:
            return {}, 0.0, base_temp
            
        # Pressure Potential based on Mass (Heavier planets hold more)
        # Earth ~ 1e24 kg -> 1 ATM
        # Venus ~ 0.8 Earth -> 90 ATM (Volatiles matter!)
        # Mars ~ 0.1 Earth -> 0.01 ATM
        
        # Volatile inventory roll
        volatile_richness = random.lognormvariate(0, 1.5) # multiplier
        
        # Base pressure scaling with mass^2 (gravity pulls harder, more mass to accrete)
        mass_earth_units = mass / MASS_EARTH
        base_pressure_atm = (mass_earth_units ** 2) * volatile_richness
        
        if 'H2' in retained_gases: # Gas Giant territory
            base_pressure_atm *= 1000 # Massive atmosphere
            
        # Hot planets strip atmosphere
        if base_temp > 500 and mass < MASS_EARTH:
            base_pressure_atm *= 0.1
            
        pressure_pa = base_pressure_atm * ATM_TO_PA
        
        # Distribute pressure among retained gases
        # Gas Giants: Mostly H2/He
        # Terrestrial: CO2, N2 dominant usually. O2 if life (rare).
        
        props = {}
        if 'H2' in retained_gases and mass > MASS_EARTH * 2: # Gas/Ice Giant
            props['H2'] = 75
            props['He'] = 24
            # Trace others
            remaining = 1.0
            for g in retained_gases:
                if g not in ['H2', 'He']: 
                    props[g] = random.uniform(0, 1)
        else:
            # Rocky atmosphere
            # CO2 is common default
            total_weight = 0
            for g in retained_gases:
                w = 1.0
                if g == 'CO2': w = 50
                if g == 'N2': w = 20
                if g == 'O2': w = 0.1 # Rare
                if g == 'H2O': w = 5
                props[g] = random.uniform(0, w)
                
        # Normalize
        total_prop = sum(props.values())
        if total_prop > 0:
            for g in props:
                props[g] /= total_prop
                composition[g] = props[g] * pressure_pa
        
        # Greenhouse Effect
        # dTx = T_effective * (P_greenhouse / P_ref)^0.2 ?
        # Simplified:
        greenhouse_add = 0
        p_atm = base_pressure_atm
        
        # CO2, H2O, CH4 are greenhouse
        gh_factor = 0
        if 'CO2' in composition: gh_factor += composition['CO2'] / pressure_pa
        if 'H2O' in composition: gh_factor += composition['H2O'] / pressure_pa * 2
        if 'CH4' in composition: gh_factor += composition['CH4'] / pressure_pa * 5
        
        # Venus: 90 ATM CO2 -> +400K
        # Earth: 1 ATM (small CO2/H2O) -> +33K
        # Formula debug:
        # Delta T ~ (Pressure * GHG_Conc)^(0.25) * Const?
        
        if p_atm > 0.01:
             greenhouse_add = 10 * (p_atm ** 0.2) * (1 + gh_factor * 5)
        
        final_temp = base_temp + greenhouse_add
        
        return composition, pressure_pa, final_temp

    def _generate_surface_flags(self, mass, coords_temp):
        activity = 0.0
        mag_field = 0.0
        water = 0.0
        
        # Tectonics: Mass keeps heat. Young planets hot.
        # Assume medium age.
        if mass > MASS_MARS:
             activity = random.uniform(0.1, 0.8)
             mag_field = random.uniform(0.5, 2.0)
        else:
             activity = random.uniform(0, 0.2)
             mag_field = random.uniform(0, 0.5)
             
        # Water
        # Needs temp 273 - 373 K (at 1 atm, differs by pressure)
        # Simplified
        if 250 < coords_temp < 350:
             water = random.uniform(0.1, 0.9)
        elif coords_temp <= 250:
             # Ice
             water = random.uniform(0.1, 0.9) # Frozen surface
        else:
             water = 0 # Boiled off
             
        return water, activity, mag_field

    def _determine_type(self, mass, temp, pressure, water, atmosphere, activity=0.0):
        p_atm = pressure / ATM_TO_PA
        
        if mass > MASS_NEPTUNE * 0.8:
            return PlanetType.GAS_GIANT
        if mass > MASS_EARTH * 8: # Arbitrary cutoff
            return PlanetType.ICE_GIANT
            
        if p_atm < 0.01:
            return PlanetType.BARREN
            
        if temp > 1000 or (temp > 400 and activity > 0.8): # Error: 'activity' not defined in scope, assume hot
             return PlanetType.LAVA # Or close orbit
         
        if 'H2O' in atmosphere and water > 0 and 260 < temp < 340:
            return PlanetType.TERRESTRIAL
            
        if water > 0.5 and temp < 250:
            return PlanetType.ICE_WORLD
            
        if temp > 700:
            return PlanetType.LAVA
            
        return PlanetType.TERRESTRIAL # Default generic rocky

    def _to_roman(self, n):
        # Simplified 1-20
        val = [
            10, 9, 5, 4, 1
            ]
        syb = [
            "X", "IX", "V", "IV", "I"
            ]
        roman_num = ''
        i = 0
        while  n > 0:
            for _ in range(n // val[i]):
                roman_num += syb[i]
                n -= val[i]
            i += 1
        return roman_num
