# BUG-24: Cannot Add Ships to Build Queue With Space Yard

## Description
I can't seem to add ships to the build queue, even when there is a space yard component on a complex

## Status
Awaiting Confirmation

## Work Log
- 2026-01-18: Ticket created

### 2026-01-18 - Phase 1: Analysis

**Root Cause:** The `has_space_shipyard` property in `planet.py` was checking for the wrong data structure. It looked for `abilities` dict inside component data, but saved design JSON stores components as a list with only `id` and `modifiers` fields - not the full component definitions with abilities.

**Data Structure Mismatch:**
- **Expected by old code:** `layers -> CORE -> components -> [{"abilities": {"SpaceShipyard": {...}}}]`
- **Actual saved design format:** `layers -> CORE -> [{"id": "space_shipyard", "modifiers": [...]}]`

The component ID `"space_shipyard"` is the correct identifier in saved designs, not the abilities dict.

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/strategy/data/planet.py`

**Changes Made (lines 105-133):**
Updated `has_space_shipyard` property to handle both data formats:

1. **List format (saved designs):** Checks for `comp.get("id") == "space_shipyard"`
2. **Dict format (test fixtures):** Also checks for `"SpaceShipyard" in comp.get("abilities", {})`

```python
@property
def has_space_shipyard(self) -> bool:
    """Check if planet has operational space shipyard."""
    for facility in self.facilities:
        if not facility.is_operational:
            continue
        for layer_data in facility.design_data.get("layers", {}).values():
            # Handle both list format (saved designs) and dict format (tests)
            if isinstance(layer_data, list):
                for comp in layer_data:
                    if isinstance(comp, dict):
                        # Check component id (real saved designs)
                        if comp.get("id") == "space_shipyard":
                            return True
                        # Check abilities dict (test fixtures)
                        if "SpaceShipyard" in comp.get("abilities", {}):
                            return True
            elif isinstance(layer_data, dict):
                for comp in layer_data.get("components", []):
                    if isinstance(comp, dict):
                        # Check component id (real saved designs)
                        if comp.get("id") == "space_shipyard":
                            return True
                        # Check abilities dict (test fixtures)
                        if "SpaceShipyard" in comp.get("abilities", {}):
                            return True
    return False
```

**Test Results:**
```
======================= 24 passed in 1.53s =======================
```

All production and planetary facilities tests pass, including shipyard detection tests.
