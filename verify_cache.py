import sys
import os

# Ensure root is in path
sys.path.append(os.getcwd())

try:
    print("Importing SessionRegistryCache...")
    from tests.infrastructure.session_cache import SessionRegistryCache
    
    print("Getting instance...")
    cache = SessionRegistryCache.instance()
    
    print("Loading data...")
    cache.load_all_data()
    
    comps = cache.get_components()
    print(f"Components in Cache: {len(comps)}")
    
    print("Importing RegistryManager...")
    from game.core.registry import RegistryManager
    
    print("Hydrating Registry...")
    RegistryManager.instance().hydrate(
        cache.get_components(),
        cache.get_modifiers(),
        cache.get_vehicle_classes()
    )
    
    reg_comps = RegistryManager.instance().components
    print(f"Components in Registry: {len(reg_comps)}")
    
    if len(comps) > 0 and len(comps) == len(reg_comps):
        print("SUCCESS: Registry Hydration Verified.")
    else:
        print("FAILURE: Registry Mismatch or Empty.")

except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
