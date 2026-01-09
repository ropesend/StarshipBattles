# Simulation Architect Report - Hull Layer Migration

## Analysis
The migration of the Hull component to a dedicated `LayerType.HULL` is architecturally sound. It decouples the chassis (structure) from the internal slots (CORE), resolving ambiguity in "Core" damage logic and streamlining UI filtering.

The change requires updates to `component.py` to define the new layer and `ship.py` to manage its lifecycle (lifecycle, initialization, serialization).

## Proposed Changes

### 1. `game/simulation/components/component.py`

#### [MODIFY] Class `LayerType`
Add the `HULL` member with index `0` to represent the innermost structural layer.

```python
class LayerType(Enum):
    HULL = 0    # [NEW] Innermost Chassis Layer
    CORE = 1
    INNER = 2
    OUTER = 3
    ARMOR = 4

    @staticmethod
    def from_string(s):
        # Existing logic works, but ensures HULL is handled if string is "HULL"
        return getattr(LayerType, s.upper())
```

### 2. `game/simulation/entities/ship.py`

#### [MODIFY] Method `_initialize_layers`
Ensure `LayerType.HULL` is explicitly created, regardless of the vehicle class definition (which likely predates this change).

**Logic Updates:**
1.  After loading `layer_defs` from class, forcefully inject `LayerType.HULL`.
2.  Set `radius_pct` to `0.0`.
3.  Set `max_mass_pct` to a high value (e.g., `100.0`) or sufficient budget to prevent `ShipStatsCalculator` validation errors, as the Hull provides the baseline mass but technically resides in a layer.
4.  Update `layer_order` to start with `LayerType.HULL` when calculating radii for other layers.

#### [MODIFY] Method `__init__`
Update the explicit auto-equipping of the default hull.

**Change:**
```python
# Before
self.layers[LayerType.CORE]['components'].append(hull_component)
hull_component.layer_assigned = LayerType.CORE

# After
self.layers[LayerType.HULL]['components'].append(hull_component)
hull_component.layer_assigned = LayerType.HULL
```

#### [MODIFY] Method `change_class`
Update the migration/refitting logic.

**Logic Updates:**
1.  **Migration Gathering:** When collecting `old_components`, skip the hull by checking the layer type rather than just the ID prefix (though keeping ID check as backup is fine).
    ```python
    if l_type == LayerType.HULL: continue
    ```
2.  **Auto-Equip New Hull:** Update the equipping block to target `LayerType.HULL`.
    ```python
    self.layers[LayerType.HULL]['components'].append(hull_component)
    hull_component.layer_assigned = LayerType.HULL
    ```

#### [MODIFY] Method `to_dict`
Update serialization to exclude the HULL layer. The hull is auto-equipped based on `ship_class` on load; we do not want to serialize the standard hull instance unless it has unique modifications (which this refactor assumes it largely doesn't, or handled via `ship_class`).

**Change:**
```python
for ltype, layer_data in self.layers.items():
    # [NEW] Skip HULL layer from explicit serialization
    if ltype == LayerType.HULL:
        continue
    
    # ... existing logic ...
```

#### [MODIFY] Method `from_dict`
Implicitly handled. `from_dict` calls `Ship(...)` constructor, which calls `_initialize_layers` (creating HULL layer) and auto-equips default hull. The loop over `data.get("layers")` will simply not find "HULL" in the JSON (due to `to_dict` change) and thus won't add duplicate hulls.

## Impact Analysis
*   **Stats Calculation:** `ShipStatsCalculator` iterates `ship.layers.values()`. It will now encounter the HULL layer. It will sum the Hull's mass into `ship.mass`. This preserves correct behavior (Base Mass + Component Mass = Total Mass).
*   **Validation:** By setting `max_mass_pct` high for the HULL layer, we avoid "Mass Budget Exceeded" errors for the hull component itself.
*   **Damage Logic:** The Hull layer is index 0. Existing logic often iterates layers or picks random components. Targeting logic needs to ensure it can (or cannot) hit the Hull.
    *   *Note:* Historically, "Core" was the death condition. If we move Hull to 0, checks for `LayerType.CORE` (1) still act as the critical system layer. The Hull component at 0 is structural.

## Verification
*   **Unit Tests:**
    *   `test_ship_init`: Verify hull is in strictly `layers[LayerType.HULL]`.
    *   `test_mass_calc`: Verify `ship.mass` includes the hull mass.
    *   `test_serialization`: Verify `to_dict` output does not contain "HULL" key.
