
import pytest
from game.core.registry import RegistryManager

@pytest.fixture(autouse=True)
def reset_game_state():
    """
    Context manager for strict test isolation.
    Ensures all global registries are cleared before and after each test.
    """
    # Pre-test cleanup
    RegistryManager.instance().clear()
    
    yield
    
    # Post-test cleanup (catch any pollution)
    RegistryManager.instance().clear()
