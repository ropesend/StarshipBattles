# QA Specialist Review: Test Stabilization

**Role:** QA_Specialist
**Focus:** Deterministic test isolation and hazard test efficacy.
**Date:** 2026-01-03

## High-Level Verdict
**APPROVED WITH STIPULATIONS**

The proposed refactor to move from global dictionaries to a `RegistryManager` singleton is **critical** for test stability. The current architecture in `ship.py` and `component.py` relies on mutable module-level globals (`VEHICLE_CLASSES`, `COMPONENT_REGISTRY`), which is a primary cause of non-deterministic test failures (State Pollution).

However, the plan must strictly address **Data Re-hydration**. Simply clearing registries (`.clear()`) between tests will cause subsequent tests to fail if they rely on the standard "Escort", "Cruiser", etc., definitions. The `conftest.py` fixture must ensure a **Reset-to-Default** state, not just an empty state.

## Critical Issues (Blocking)

1.  **Missing `conftest.py` Infrastructure**:
    *   `tests/conftest.py` does not currently exist. This means there is no central place for shared fixtures yet. Creating this is a prerequisite.
    *   **Risk**: If the new fixture is not correctly scoped (e.g., `autouse=True`), pollution will persist.

2.  **Registry Re-Hydration Strategy**:
    *   The proposal mentions `clear()`.
    *   **The Hazard**: If Test A runs `clear()`, Test B starts with empty registries. Test B attempts to create a "Cruiser" and fails because `VEHICLE_CLASSES` is empty.
    *   **Requirement**: The RegistryManager must support a method like `reset_to_defaults()` which clears *and* reloads the baseline JSON data (or hardcoded defaults) to ensure every test starts with a "fresh install" state.

## Questions (Ambiguities)

1.  **Lazy Loading vs. Explicit Initialization**:
    *   Current code (`ship.py:load_vehicle_classes`) is explicit.
    *   Should `RegistryManager` lazy-load defaults on first access if empty? Or should `conftest.py` explicitly call `RegistryManager.instance().load_defaults()`?
    *   *Recommendation*: Explicit initialization in `conftest.py` is safer for testing transparency and performance control.

## Code Suggestions

### 1. `game/core/registry.py` (Skeleton)
Ensure the manager handles the *specific* loading logic or delegates it cleanly.

```python
import threading
from typing import Dict, Any, Optional

class RegistryManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        # The actual data stores
        self.vehicle_classes: Dict[str, Any] = {}
        self.components: Dict[str, Any] = {}
        self.modifiers: Dict[str, Any] = {}
        
        # Paths for re-hydration
        self.paths = {
            "vehicles": "data/vehicleclasses.json",
            "components": "data/components.json",
            "modifiers": "data/modifiers.json"
        }

    @classmethod
    def instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls()
        return cls._instance

    def clear(self):
        """Wipes all data. Dangerous if not followed by reload."""
        self.vehicle_classes.clear()
        self.components.clear()
        self.modifiers.clear()

    def reset(self):
        """The core test fixture method: Clear + Reload Defaults."""
        self.clear()
        # In a real implementation, you might want these to be optimized 
        # (e.g., memory copy of a clean state instead of IO reading)
        self.load_defaults()

    def load_defaults(self):
        # Call the existing loaders (refactored to accept a target dict or use the manager)
        # OR implement logic here which populates self.vehicle_classes, etc.
        pass
```

### 2. `tests/conftest.py` (The Guardrail)
This is strictly required to enforce isolation.

```python
import pytest
from game.core.registry import RegistryManager

@pytest.fixture(autouse=True)
def isolation_protocol():
    """
    Automatic fixture to enforce state isolation between tests.
    Runs before AND after each test to ensure cleanliness.
    """
    # Setup: Ensure fresh state
    RegistryManager.instance().reset()
    
    yield
    
    # Teardown: Clean up any mess left
    RegistryManager.instance().clear()
```

### 3. `tests/repro_issues/test_sequence_hazard.py` (The Canary)
This test proves isolation works by attempting to poison the well.

```python
import pytest
from game.core.registry import RegistryManager

# Force sequential execution order if possible, or reliance on random ordering catching it eventually.
# Ideally, we define two tests that run in a guaranteed order for this specific verification suite.

def test_A_pollute_registry():
    """Inject a poison pill into the global registry."""
    reg = RegistryManager.instance()
    reg.vehicle_classes["POISON_PILL"] = {"hull_mass": 99999}
    assert "POISON_PILL" in reg.vehicle_classes

def test_B_verify_isolation():
    """Verify the poison pill from test_A is GONE."""
    reg = RegistryManager.instance()
    # If isolation works, reset() was called between A and B
    assert "POISON_PILL" not in reg.vehicle_classes, "State Pollution Detected: Registry leaked between tests!"
```
