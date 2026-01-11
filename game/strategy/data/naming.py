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

