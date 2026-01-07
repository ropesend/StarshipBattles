# Active Refactor: Hull Component & Ship Cohesion
**Goal:** Unify Ship stats with V2 Ability System (Hull Component) and eliminate architectural incoherence.

## Status
**Current Phase:** Phase 2 (Core Logic & Stability) - IN PROGRESS
**Start Date:** 2026-01-05
**Phase 1 Review:** ✅ APPROVED (2026-01-06)
**Status:** [PHASE_2_IN_PROGRESS]

---

## Migration Map (The Constitution)

| Concept | Legacy State | Target State | Source of Truth |
| :--- | :--- | :--- | :--- |
| **Hull Definition** | `vehicleclasses.json` (hull_mass, hp) | `components.json` ("type": "Hull") | Component Data |
| **Base Mass** | `Ship.base_mass` (manual float) | Sum of `Hull` component + Systems | `ShipStatsCalculator` |
| **Requirements** | Hardcoded checks & `Ship.requirements` | `CrewRequired`, `FuelStorage` Abilities | Ability System V2 |
| **Resource State** | Reset on Load (Volatile) | Persisted in `Ship.resources` | Save Data |
| **UI Layout** | Hardcoded Pixel Overlaps | Responsive/Grid-based | `builder_utils.py` |

---

## Phased Schedule

### Phase 1: Data & State Foundations (The Bedrock) [Complete]
**Objective:** Fix critical state bugs and prepare data structures.
- [x] **Critical Fix:** Patch `resource_manager.py` clamping bug (resets to 0 on overflow).
- [x] **Data Migration:** Create `Hull` components in `data/components.json` for all 18 classes. [Data Architect]
- [x] **Data Migration:** Add `default_hull_id` to `data/vehicleclasses.json`. [Data Architect]
- [x] **Serialization:** Update `Ship.to_dict`/`from_dict` to persist `ResourceRegistry` values. [Data Architect]
- [x] **Cleanup:** Remove hardcoded ability string maps in `Component._instantiate_abilities`.

---

### Phase 2: Core Logic & Stability (The Engine) [In Progress]
**Objective:** Implement the "Hull as Component" logic and fix core simulation loops.
- [ ] **Task 2.1:** Update `Ship.__init__` to auto-equip `default_hull_id`. [Core Engineer]
- [ ] **Task 2.2:** Switch `Ship.mass` and `Ship.hp` to cached properties in `ShipStatsCalculator`.
- [ ] **Task 2.3:** Implement `CommandAndControl` and `CrewRequired` logic in `update_derelict_status`.
- [ ] **Task 2.4:** Remove duplicate To-Hit/Derelict initializations in `Ship.py`.
- [ ] **Task 2.5:** Standardize MRO-based identity checks (remove brittle class name checks).

---

## Phase 2 Implementation Specifications

### Task 2.1: Auto-Equip `default_hull_id` in `Ship.__init__`
**File:** `game/simulation/entities/ship.py`
**Method:** `__init__`

**Current State (lines ~223-230):**
```python
class_def = get_vehicle_classes().get(self.ship_class, {"hull_mass": 50, "max_mass": 1000})
self.base_mass: float = class_def.get('hull_mass', 50)  # LEGACY
```

**Target Implementation:**
```python
from game.simulation.components.component import create_component

# In __init__, AFTER _initialize_layers():
class_def = get_vehicle_classes().get(self.ship_class, {})
default_hull_id = class_def.get('default_hull_id')

if default_hull_id:
    hull_component = create_component(default_hull_id)
    if hull_component:
        self.add_component(hull_component, LayerType.CORE)
    else:
        print(f"WARNING: Hull '{default_hull_id}' not found for {self.ship_class}")
```

**Steps:**
1. Import `create_component` from `game.simulation.components.component`.
2. Remove `self.base_mass` assignment from `class_def.get('hull_mass', ...)`.
3. After `_initialize_layers()`, lookup `default_hull_id` and call `create_component()`.
4. Add Hull to `CORE` layer via `add_component()`.

**Edge Cases:**
- Missing `default_hull_id` → Log warning, continue (test-only ships).
- Component registry not loaded → Graceful `None` return from `create_component`.

---

### Task 2.2: Cached `mass` and `hp` Properties
**Files:** `game/simulation/entities/ship.py`, `ship_stats.py`

**Current State:**
- `self.mass: float = 0.0` (direct attribute)
- `@property max_hp` / `hp` → O(n) iteration on every access

**Target Implementation in `Ship.__init__`:**
```python
self._cached_mass: float = 0.0
self._cached_max_hp: int = 0
self._cached_hp: int = 0
```

**Target Properties:**
```python
@property
def mass(self) -> float:
    return self._cached_mass

@property
def max_hp(self) -> int:
    return self._cached_max_hp

@property
def hp(self) -> int:
    return self._cached_hp
```

**In `ShipStatsCalculator.calculate(ship)`:**
```python
# Calculate and cache
total_mass = sum(c.mass for layer in ship.layers.values() for c in layer['components'])
total_max_hp = sum(c.max_hp for layer in ship.layers.values() for c in layer['components'])
total_hp = sum(c.current_hp for layer in ship.layers.values() for c in layer['components'])

ship._cached_mass = total_mass
ship._cached_max_hp = total_max_hp
ship._cached_hp = total_hp
```

---

### Task 2.3: Ability-Based Derelict Logic
**File:** `game/simulation/entities/ship.py`
**Method:** `update_derelict_status`

**New Abilities Required (in `abilities.py`):**
```python
class CommandAndControl(Ability):
    """Marks component as command center (Bridge, CIC)."""
    pass
```

**Target Implementation:**
```python
def update_derelict_status(self) -> None:
    # Check 1: Command and Control
    has_command = any(
        comp.is_operational and comp.has_ability('CommandAndControl')
        for layer in self.layers.values()
        for comp in layer['components']
    )
    
    if not has_command:
        self.is_derelict = True
        self.bridge_destroyed = True
        return
    
    # Check 2: Crew Capacity (optional)
    total_crew_req = self.get_total_ability_value('CrewRequired')
    total_crew_cap = self.get_total_ability_value('CrewCapacity')
    
    if total_crew_req > total_crew_cap:
        self.is_derelict = True
        return
    
    self.is_derelict = False
```

**Data Migration:** Add `"CommandAndControl": true` to Bridge components in `components.json`.

---

### Task 2.4: Remove Duplicate Initializations
**File:** `game/simulation/entities/ship.py`

**Remove (lines ~248-251):**
```python
self.baseline_to_hit_offense = 0.0  # DUPLICATE
self.to_hit_profile = 0.0  # DUPLICATE
```

**Keep (lines ~298-300):**
```python
self.to_hit_profile: float = 1.0       # Defensive Multiplier
self.baseline_to_hit_offense: float = 1.0  # Offensive Multiplier
```

---

### Task 2.5: Standardize Identity Checks
**File:** `game/simulation/entities/ship.py`
**Method:** `max_weapon_range` (lines ~325-355)

**Current (brittle):**
```python
if cls.__name__ == 'WeaponAbility':  # STRING CHECK
```

**Target:**
```python
from game.simulation.components.abilities import WeaponAbility, SeekerWeaponAbility

for ab in comp.ability_instances:
    if isinstance(ab, WeaponAbility):  # POLYMORPHIC
        rng = getattr(ab, 'range', 0.0)
        if isinstance(ab, SeekerWeaponAbility) and rng <= 0:
            rng = ab.projectile_speed * ab.endurance
        max_rng = max(max_rng, rng)
```

### Phase 3: Test Infrastructure & Verification (The Guardrails)
**Objective:** Restore test isolation and verify unified stats.
- [ ] **Infrastructure:** Restore/Fix `tests/conftest.py` for proper `RegistryManager` isolation. [QA Lead]
- [ ] **New Test:** Create `tests/unit/entities/test_ship_core.py` (Mocked Hull/Stat verification).
- [ ] **Audit:** Verify `Ship` tests typically use `RegistryManager` utilities.

### Phase 4: UI Reconstruction (The Interface)
**Objective:** Resolve layout overlaps and ensure builder compatibility.
- [ ] **Restoration:** Create/Restore `game/ui/screens/builder_utils.py` (Layout constants). [UI Specialist]
- [ ] **Layout Fix:** Implement relative/grid sizing for `builder_screen.py` to fix 1920px overlap.
- [ ] **Layout Fix:** Resolve vertical collision between Weapons Report and Nav Panels.
- [ ] **Logic Fix:** Switch `BuilderSceneGUI` to event-based data sync (stop recreating dropdowns).

### Phase 5: Legacy Purge & Final Polish (The Cleanup)
**Objective:** Remove deprecated data and finalize the refactor.
- [ ] **Cleanup:** Remove `hull_mass` and `requirements` from `vehicleclasses.json`.
- [ ] **Cleanup:** Remove hardcoded ship fallback registry in `load_vehicle_classes`.
- [ ] **Final Verification:** Run Full Gauntlet (Target: 100% Pass).
- [ ] **Definition of Done:**
    - `Ship.py` has ZERO hardcoded mass/hp assignments.
    - `vehicleclasses.json` contains NO physical stats.
    - Ship Builder UI renders without overlap on 1080p+.
    - Save/Load persists fuel/ammo levels correctly.

---

## Test Triage Table
| Test File | Status | Owner | Notes |
| :--- | :--- | :--- | :--- |
| (Empty) | | | |
