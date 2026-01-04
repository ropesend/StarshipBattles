
import os

target_file = r"c:\Dev\Starship Battles\game\simulation\components\component.py"

new_code = r'''# Caching for performance (Phase 2 Test Stabilization)
_COMPONENT_CACHE = None
_MODIFIER_CACHE = None

def load_components(filepath="data/components.json"):
    global _COMPONENT_CACHE
    import os
    import copy
    from game.core.registry import RegistryManager

    # If cache exists, hydrate Registry from cache (Fast Path)
    if _COMPONENT_CACHE is not None:
        mgr = RegistryManager.instance()
        for c_id, comp in _COMPONENT_CACHE.items():
            mgr.components[c_id] = comp.clone()
        return

    # Slow Path: Load from Disk
    # Try absolute path based on this file if CWD fails
    if not os.path.exists(filepath):
        print(f"WARN: {filepath} not found in CWD ({os.getcwd()}).")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, filepath)

        if os.path.exists(abs_path):
            filepath = abs_path
        else:
            print(f"ERROR: components file not found at {abs_path}")
            return

    try:
        with open(filepath, 'r') as f:
            import json
            data = json.load(f)
            
        temp_cache = {}
        for comp_def in data['components']:
            c_type = comp_def['type']
            try:
                cls = COMPONENT_TYPE_MAP.get(c_type, Component)
                obj = cls(comp_def)
                temp_cache[comp_def['id']] = obj
            except Exception as e:
                print(f"ERROR creating component {comp_def.get('id')}: {e}")
        
        # Populate Cache
        _COMPONENT_CACHE = temp_cache
        
        # Populate Registry from Cache
        mgr = RegistryManager.instance()
        for c_id, comp in _COMPONENT_CACHE.items():
            mgr.components[c_id] = comp.clone()
            
    except Exception as e:
        print(f"ERROR loading/parsing components json: {e}")

def load_modifiers(filepath="data/modifiers.json"):
    global _MODIFIER_CACHE
    import os
    import copy
    from game.core.registry import RegistryManager
    
    # Fast Path
    if _MODIFIER_CACHE is not None:
        mgr = RegistryManager.instance()
        for m_id, mod in _MODIFIER_CACHE.items():
            mgr.modifiers[m_id] = copy.deepcopy(mod)
        return

    # Slow Path
    if not os.path.exists(filepath):
         base_dir = os.path.dirname(os.path.abspath(__file__))
         filepath = os.path.join(base_dir, filepath)
    
    try:
        with open(filepath, 'r') as f:
            import json
            data = json.load(f)
            
        temp_cache = {}
        for mod_def in data['modifiers']:
            mod = Modifier(mod_def)
            temp_cache[mod.id] = mod
        
        _MODIFIER_CACHE = temp_cache
        
        mgr = RegistryManager.instance()
        for m_id, mod in _MODIFIER_CACHE.items():
            mgr.modifiers[m_id] = copy.deepcopy(mod)
            
    except Exception as e:
        print(f"ERROR loading modifiers: {e}")

def create_component(component_id):
    # Use RegistryManager instance instead of alias if possible, but alias is still mapped
    from game.core.registry import RegistryManager
    comps = RegistryManager.instance().components
    if component_id in comps:
        return comps[component_id].clone()
    print(f"Error: Component ID {component_id} not found in registry.")
    return None

def get_all_components():
    from game.core.registry import RegistryManager
    return list(RegistryManager.instance().components.values())
'''

with open(target_file, "r") as f:
    lines = f.readlines()

# Truncate at line 481 (index 480)
# Lines are 1-indexed in editor but 0-indexed in list.
# Line 481 is "def load_components..."
# So we keep 0 to 480.
new_lines = lines[:480] 
content = "".join(new_lines) + new_code

with open(target_file, "w") as f:
    f.write(content)

print("Successfully updated component.py")
