import json
import logging
import os

logger = logging.getLogger(__name__)

class PresetManager:
    """Manages saving and loading of component configuration presets."""
    
    def __init__(self, filename='component_presets.json'):
        self.filename = filename
        self.presets = {}
        self.load_presets()
        
    def load_presets(self):
        """Load presets from file."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.presets = data.get('presets', {})
                    logger.debug(f"Loaded {len(self.presets)} presets")
            else:
                self.presets = {}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load presets: {e}")
            self.presets = {}
            
    def save_presets(self):
        """Save presets to file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump({'presets': self.presets}, f, indent=2)
            logger.debug(f"Saved {len(self.presets)} presets")
        except Exception as e:
            logger.error(f"Failed to save presets: {e}")
            
    def get_all_presets(self):
        """Return all presets."""
        return self.presets
        
    def get_preset(self, name):
        """Get a specific preset by name."""
        return self.presets.get(name)
        
    def add_preset(self, name, modifiers):
        """Add or update a preset."""
        if name and name.strip():
            self.presets[name.strip()] = dict(modifiers)
            self.save_presets()
            return True
        return False
        
    def delete_preset(self, name):
        """Delete a preset."""
        if name in self.presets:
            del self.presets[name]
            self.save_presets()
            return True
        return False
