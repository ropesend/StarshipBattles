import os
import yaml
import random
from collections import defaultdict
import logging

# Configure logging
logger = logging.getLogger(__name__)

class NameRegistry:
    def __init__(self, data_file_path=None):
        self.available_names = []
        self.used_names = set()
        
        if data_file_path:
            self.load_data(data_file_path)
            
    def load_data(self, file_path):
        """Load names from YAML file."""
        if not os.path.exists(file_path):
            logger.error(f"Name data file not found: {file_path}")
            return
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                
            if "names" in data and isinstance(data["names"], list):
                self.available_names = data["names"]
                # Default behavior per file: "RandomMode: ShuffleDraw"
                # We enforce this by shuffling and popping.
                random.shuffle(self.available_names)
            else:
                logger.warning(f"Invalid format in {file_path}: 'names' list missing.")
                
        except Exception as e:
            logger.error(f"Failed to load name data: {e}")

    def get_system_name(self):
        """
        Get a unique system name.
        Returns a fallback name if all names are exhausted.
        """
        if not self.available_names:
            return f"Unknown-{len(self.used_names) + 1}"
            
        name = self.available_names.pop()
        while name in self.used_names:
            if not self.available_names:
                return f"Unknown-{len(self.used_names) + 1}"
            name = self.available_names.pop()
            
        self.used_names.add(name)
        return name

    @staticmethod
    def to_roman(n):
        """Convert integer to Roman numeral (1-3999)."""
        if not (0 < n < 4000):
            return str(n)
            
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syb = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]
        roman_num = ''
        i = 0
        while  n > 0:
            for _ in range(n // val[i]):
                roman_num += syb[i]
                n -= val[i]
            i += 1
        return roman_num

    def name_planets(self, system_name, planets):
        """
        Apply naming convention to a list of planets.
        Planets should be objects with attributes:
         - orbit_distance (int/float)
         - location (hashable, usually HexCoord) (optional, for co-orbital distinction)
         - size/weight (optional, for moon hierarchy)
         
        Modifies the planet objects in-place by setting a 'name' attribute.
        """
        # Sort by distance first
        # We need a stable sort keys.
        # Primary: Orbit Distance
        # Secondary: Location (to group co-orbitals if we implemented that)
        # Tertiary: Arbitrary tie-breaker
        
        # In current galaxy implementation:
        # Planets are unique per ring.
        
        # Group by Distance
        by_distance = defaultdict(list)
        for p in planets:
            by_distance[p.orbit_distance].append(p)
            
        sorted_distances = sorted(by_distance.keys())
        
        roman_counter = 1
        
        for dist in sorted_distances:
            group = by_distance[dist]
            
            # If logic requires differentiating planets at same distance:
            # "if two planets are the same distance I don't care which uses the lower number"
            # So we treat them as sequential Roman numerals UNLESS they are in the same location (moons).
            
            # Further group by location to detect moons
            by_location = defaultdict(list)
            for p in group:
                loc_key = p.location if hasattr(p, 'location') else 'uknown'
                by_location[loc_key].append(p)
                
            # Sort locations arbitrarily to be deterministic
            # HexCoord defines __lt__? If not, use ID or something.
            # safe assumption: we just iterate the locations
            
            for loc, sub_group in by_location.items():
                # sub_group are planets at SAME distance and SAME location.
                # Use largest as Primary (Roman), others as moons (a,b,c).
                # Current Planet class doesn't have size, but uses PlanetType with implicit size.
                # Let's assume passed order or stable sort is "largest first" if we can't determine.
                # Or sort by planet_type value (Gas Giant > Earth > etc) if accessible.
                # For now, simplistic approach:
                
                base_name = f"{system_name} {self.to_roman(roman_counter)}"
                roman_counter += 1
                
                # If only one, just name it
                if len(sub_group) == 1:
                    sub_group[0].name = base_name
                else:
                    # Multiple objects in exact same slot.
                    # Primary gets base_name.
                    # Moons get base_name + 'a', 'b'...
                    # "largest should be names as above... smaller planets lower case a"
                    # We blindly assume sub_group[0] is primary for now as we don't have size logic here easily
                    # without importing PlanetType or assuming modification.
                    
                    sub_group[0].name = base_name
                    
                    suffix_char = ord('a')
                    for moon in sub_group[1:]:
                        moon.name = f"{base_name}{chr(suffix_char)}"
                        suffix_char += 1
