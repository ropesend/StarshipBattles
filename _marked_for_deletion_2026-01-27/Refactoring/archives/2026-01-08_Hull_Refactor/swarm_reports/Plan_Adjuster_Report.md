# Plan_Adjuster Report: Phase 5 - Legacy Purge & Final Polish

## Focus: Generate DETAILED SPECS for Phase 5

### 1. Overview
The objective of Phase 5 is the final removal of all legacy architectural bridge-heads. This includes purging physical stats (`hull_mass`) and redundant configuration (`requirements`) from class definitions, and eliminating fallback logic in the `Ship` entity.

---

### 2. Physical Stat Purge (JSON)

**File:** `data/vehicleclasses.json`

**Action:** Remove the following keys from all vehicle class definitions:
- `hull_mass`: Superseded by `default_hull_id` lookup and `ShipStatsCalculator`.
- `requirements`: Superseded by capability-based derelict logic and systemic validation.

**Success Criteria:** `vehicleclasses.json` contains only structural data (type, code, layer_config) and constraints (max_mass), but NO intrinsic physical properties of the hull.

---

### 3. Core Logic Cleanup (Python)

**File:** `game/simulation/entities/ship.py`

**Task 3.1: Remove `load_vehicle_classes` Fallback Registry**
- **Action:** Delete the `defaults` dictionary inside `load_vehicle_classes`.
- **Target Line (~93-101):** Remove the logic that populates `vehicle_classes` if the JSON is missing. This ensures the system fails fast if the data layer is corrupt.

**Task 3.2: Eliminate `base_mass` Fallback**
- **Action:** Update `Ship.__init__` and `Ship.change_class` to always set `self.base_mass = 0.0`.
- **Logic:** In the unified architecture, a ship without a `Hull` component is invalid. We no longer support "Mass Shadowing" from a legacy float.

**Task 3.3: Capabilty-Based Derelict Logic**
- **Action:** Fully implement the logic in `update_derelict_status` that checks for `CommandAndControl` and `CrewRequired` without referencing the `requirements` JSON key.
- **Implementation:**
```python
def update_derelict_status(self) -> None:
    # Essential Capability Check
    has_ccc = any(c.is_operational and c.has_ability('CommandAndControl') 
                 for layer in self.layers.values() for c in layer['components'])
    
    # Resource Capability Check
    crew_capacity = self.get_ability_total('CrewCapacity')
    crew_required = self.get_ability_total('CrewRequired')
    
    is_derelict = not has_ccc or (crew_required > crew_capacity)
    
    if is_derelict and not self.is_derelict:
        log_debug(f"Ship {self.name} is now derelict.")
    self.is_derelict = is_derelict
```

---

### 4. Validation Refactor

**File:** `ship_validator.py`

**Task 4.1: Static Type Requirements**
- **Action:** Refactor `ClassRequirementsRule` to `TypeRequirementsRule`.
- **Implementation:** Define a mapping of `VehicleType` -> `RequiredAbilities`.
    - `Ship`: `CommandAndControl`, `CombatPropulsion`, `FuelStorage`.
    - `Fighter`: `CommandAndControl`, `CombatPropulsion`, `FuelStorage`.
    - `Satellite`: `CommandAndControl`.
- **Benefit:** Simplifies `vehicleclasses.json` and ensures all ships of a certain type meet the same gameplay-critical standards.

---

### 5. Final Verification & Polish
- **Gauntlet Run:** 100% pass on `tests/unit/entities/` and `tests/integration/`.
- **Stat Audit:** Confirm `Ship.mass` exactly matches `HullComponent.mass` + `SystemMass`.
- **Save/Load:** Confirm fuel/ammo levels are persisted without resetting to "Full" on load (already implemented in Phase 1, but needs final verification).

---

**Status:** READY FOR SYNTHESIS
**Next Steps:** Proceed to EXECUTION of Phase 5.
