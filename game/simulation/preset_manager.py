from game.core.json_utils import load_json, save_json
from game.core.logger import log_error, log_debug

class PresetManager:
    """Manages saving and loading of component configuration presets."""
    
    def __init__(self, filename='component_presets.json'):
        self.filename = filename
        self.presets = {}
        self.load_presets()
        
    def load_presets(self):
        """Load presets from file."""
        data = load_json(self.filename, default={})
        self.presets = data.get('presets', {})
        if self.presets:
            log_debug(f"Loaded {len(self.presets)} presets")

    def save_presets(self):
        """Save presets to file."""
        if save_json(self.filename, {'presets': self.presets}):
            log_debug(f"Saved {len(self.presets)} presets")
        else:
            log_error(f"Failed to save presets to {self.filename}")
            
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
