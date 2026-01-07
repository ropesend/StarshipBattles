# Active Refactor: Hull Component & Ship Cohesion
**Goal:** Unify Ship stats with V2 Ability System (Hull Component) and eliminate architectural incoherence.

## Status
**Current Phase:** Phase 5 (Legacy Purge & Final Polish)
**Start Date:** 2026-01-05
**Phase 1 Review:** ✅ APPROVED (2026-01-06)
**Phase 2 Review:** ✅ APPROVED (2026-01-06)
**Phase 3 Review:** ✅ APPROVED (2026-01-06)
**Phase 4 Review:** ✅ APPROVED (2026-01-06)
**Status:** [PHASE_5_IN_PROGRESS]

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

### Phase 2: Core Logic & Stability (The Engine) [Complete]
**Objective:** Implement the "Hull as Component" logic and fix core simulation loops.
- [x] **Task 2.1:** Update `Ship.__init__` to auto-equip `default_hull_id`. [Core Engineer]
- [ ] **Task 2.2:** Switch `Ship.mass` and `Ship.hp` to cached properties in `ShipStatsCalculator`. (DEFERRED - optimization)
- [x] **Task 2.3:** Implement `CommandAndControl` and `CrewRequired` logic in `update_derelict_status`.
- [x] **Task 2.4:** Remove duplicate To-Hit/Derelict initializations in `Ship.py`.
- [x] **Task 2.5:** Standardize MRO-based identity checks (remove brittle class name checks).
- [x] **Task 2.6:** Fix detail panel rendering test regressions. [UI Specialist]
  - **File:** `tests/unit/ui/test_detail_panel_rendering.py`
  - **Fix:** Added missing `uitextbox_patch_real.stop()` in tearDown to prevent patch leakage causing intermittent failures in parallel execution.

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

### Phase 3: Test Infrastructure & Verification (The Guardrails) [Complete]
**Objective:** Restore test isolation and verify unified stats.
- [x] **Task 3.1:** Restore/Fix `tests/conftest.py` for proper `RegistryManager` isolation. [QA Lead]
  - Added pre-test `mgr.clear()` before marker check
  - Restructured with try/finally for unconditional post-test cleanup
- [x] **Task 3.2:** Create `tests/unit/entities/test_ship_core.py` (Mocked Hull/Stat verification).
  - Created 6 test cases covering Hull auto-equip, legacy fallback, mass/HP aggregation, derelict status
  - All tests passing
- [x] **Task 3.3:** Audit existing Ship tests for `RegistryManager` usage compliance.
  - grep for COMPONENT_REGISTRY → 0 matches ✓
  - grep for VEHICLE_CLASSES → 0 matches ✓

---

## Phase 3 Implementation Specifications

### Task 3.1: Registry Isolation in `conftest.py`
**File:** `tests/conftest.py`
**Root Cause:** `reset_game_state` fixture skips cleanup when `use_custom_data` marker is present.

**Target Implementation:**
```python
@pytest.fixture(autouse=True)
def reset_game_state(monkeypatch, request):
    from game.core.registry import RegistryManager
    mgr = RegistryManager.instance()
    
    # Pre-test cleanup (ALWAYS)
    mgr.clear()

    if "use_custom_data" not in request.keywords:
        # Standard Fast Hydration
        cache = SessionRegistryCache.instance()
        cache.load_all_data()
        mgr.hydrate(...)
        
    yield
    
    # Post-test cleanup (ALWAYS RUNS)
    mgr.clear()
```

**Steps:**
1. Open `tests/conftest.py`.
2. Locate `reset_game_state` fixture.
3. Add `mgr.clear()` call BEFORE the marker check.
4. Ensure `mgr.clear()` is called AFTER `yield` unconditionally.
5. Run `pytest tests/unit/entities/test_sequence_hazard.py` to verify isolation.

---

### Task 3.2: Create `test_ship_core.py`
**File:** `tests/unit/entities/test_ship_core.py`

**Test Cases:**

#### TC-3.2.1: Hull Auto-Equip Verification
```python
def test_hull_auto_equip(registry_with_hull):
    """Verify Ship auto-equips default_hull_id from vehicle class."""
    ship = Ship(name="Test", x=0, y=0, color=(255,255,255), ship_class="Escort")
    
    core_comps = ship.layers[LayerType.CORE]['components']
    assert len(core_comps) == 1
    assert core_comps[0].id == "hull_escort"
    assert ship.base_mass == 0.0  # Attribute Shadowing
```

#### TC-3.2.2: Legacy Fallback (No Hull)
```python
def test_no_hull_fallback(registry_no_hull):
    """Verify Ship uses legacy hull_mass when no default_hull_id."""
    ship = Ship(name="Test", x=0, y=0, color=(255,255,255), ship_class="TestShip")
    
    core_comps = ship.layers[LayerType.CORE]['components']
    assert len(core_comps) == 0
    assert ship.base_mass == 100.0
```

#### TC-3.2.3: Mass Aggregation
```python
def test_mass_from_components(ship_with_components):
    """Verify Ship.mass equals sum of all component masses + base_mass."""
    ship = ship_with_components
    ship.recalculate_stats()
    
    expected_mass = ship.base_mass + sum(
        c.mass for layer in ship.layers.values() for c in layer['components']
    )
    assert ship.mass == expected_mass
```

#### TC-3.2.4: HP Aggregation
```python
def test_hp_from_components(ship_with_components):
    """Verify Ship.max_hp equals sum of component max_hp values."""
    ship = ship_with_components
    
    expected_hp = sum(
        c.max_hp for layer in ship.layers.values() for c in layer['components']
    )
    assert ship.max_hp == expected_hp
```

#### TC-3.2.5: Derelict Status from CommandAndControl
```python
def test_derelict_on_bridge_destruction(ship_with_bridge):
    """Verify ship becomes derelict when CommandAndControl component destroyed."""
    ship = ship_with_bridge
    bridge = next(c for c in ship.layers[LayerType.CORE]['components'] 
                  if c.has_ability('CommandAndControl'))
    
    bridge.current_hp = 0
    ship.update_derelict_status()
    
    assert ship.is_derelict is True
```

**Fixtures Required:**
- `registry_with_hull`: Populates RegistryManager with Escort class + hull_escort component.
- `registry_no_hull`: Populates RegistryManager with TestShip class (hull_mass=100, no default_hull_id).
- `ship_with_components`: Creates Ship with known components for mass/HP testing.
- `ship_with_bridge`: Creates Ship with Bridge component having CommandAndControl ability.

---

### Task 3.3: Audit Ship Tests for RegistryManager Compliance
**Scope:** `tests/unit/entities/`, `tests/integration/`

**Verification Steps:**
1. `grep -r "COMPONENT_REGISTRY" tests/` → Should return 0 matches.
2. `grep -r "VEHICLE_CLASSES" tests/` → Should return 0 matches.
3. `grep -r "from game.simulation.entities.ship import" tests/` → Verify imports use `get_vehicle_classes`, `get_component_registry`.

**Remediation Pattern:**
```python
# OLD (Direct Import)
from game.simulation.entities.ship import COMPONENT_REGISTRY

# NEW (RegistryManager Access)
from game.core.registry import get_component_registry
components = get_component_registry()
```

**Run Verification:**
```bash
pytest tests/unit/entities/ -v
pytest tests/integration/ -v
```

### Phase 4: UI Reconstruction (The Interface) [Complete] ✅
**Objective:** Resolve layout overlaps and ensure builder compatibility.
- [x] **Task 4.1:** Create `game/ui/screens/builder_utils.py` (Layout constants). [UI Specialist]
  - Created centralized module with `PanelWidths`, `PanelHeights`, `Margins`, and `BuilderEvents` constants
- [x] **Task 4.2:** Implement relative/grid sizing for `builder_screen.py` to fix 1920px overlap.
  - FIXED: Changed `layer_panel_width` from fixed `PANEL_WIDTHS.layer_panel` to dynamic `calculate_dynamic_layer_width(screen_width)`
  - FIXED: `weapons_panel_width` calculation now subtracts `right_panel_width` to prevent overlap
- [x] **Task 4.3:** Resolve vertical collision between Weapons Report and Nav Panels.
  - ANALYZED: `right_panel.py` uses single scroll container, no sub-panels needing `update_layout()`
  - RECLASSIFIED: Issue was horizontal overlap (covered by Task 4.2b), not vertical stacking
- [x] **Task 4.4:** Switch `BuilderSceneGUI` to event-based data sync using `REGISTRY_RELOADED`.
  - Added `REGISTRY_RELOADED` event emission in `_reload_data`
  - Updated `BuilderRightPanel` and `BuilderLeftPanel` to subscribe to event

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

## Phase 4 Implementation Specifications

### Task 4.1: Centralize Layout Constants
**File:** `game/ui/screens/builder_utils.py` [NEW]

**Implementation Spec:**
Create a utility module to define the design system's dimensions.

```python
# game/ui/screens/builder_utils.py

PANEL_WIDTHS = {
    'component_palette': 400,
    'structure_list': 400,
    'detail_panel': 500,
    'ship_stats': 750
}

PANEL_HEIGHTS = {
    'bottom_bar': 60,
    'weapons_report': 500,
    'modifier_panel': 360
}

MARGINS = {
    'edge': 20,
    'gutter': 10
}
```

---

### Task 4.2: Relative/Grid Layout for 1920px+
**File:** `game/ui/screens/builder_screen.py`

**Implementation Spec:**
1. **Calculate Available Center Width:** `center_width = screen_width - PANEL_WIDTHS['component_palette'] - PANEL_WIDTHS['ship_stats']`.
2. **Dynamic Layer Panel:** Instead of fixed 450px, the Layer Panel should take `min(400, center_width * 0.3)`.
3. **Schematic View:** Takes the remaining center space.
4. **Detail Panel Overlay:** Position the Detail Panel as a `pygame_gui.elements.UIPanel` with a relative offset from the right.

---

### Task 4.3: Resolve Vertical Panel Collision
**File:** `ui/builder/right_panel.py`

**Implementation Spec:**
The "Weapons Report" and "Navigation Panels" must use a vertical stack instead of fixed Y-offsets.

```python
def update_layout(self):
    current_y = MARGINS['edge']
    for panel in self.sub_panels:
        panel.set_relative_position((0, current_y))
        current_y += panel.rect.height + MARGINS['gutter']
```

---

### Task 4.4: Event-Based UI Synchronization
**Files:** `ui/builder/event_bus.py`, `game/ui/screens/builder_screen.py`

**Implementation Spec:**
1. **Registry Reload Event:** Add `REGISTRY_RELOADED = 'REGISTRY_RELOADED'` to `EventBus`.
2. **Panel Subscriptions:** `BuilderRightPanel` and `BuilderLeftPanel` subscribe to `REGISTRY_RELOADED`.
3. **Internal Refresh:** Update `BuilderRightPanel.refresh_controls()` to update dropdown *options* without killing the object.
4. **Preserve Selection:** Cache `self.ship.ship_class` before reload and re-apply to dropdown after refresh.

---

## Phase 5 Implementation Specifications

### Task 5.1: Remove `hull_mass` and `requirements` from `vehicleclasses.json`
**File:** `data/vehicleclasses.json`

**Current State:**
```json
{
  "Escort": {
    "name": "Escort",
    "hull_mass": 50,        // LEGACY - remove
    "max_mass": 1000,
    "requirements": {...},  // LEGACY - remove
    "default_hull_id": "hull_escort"
  }
}
```

**Target State:**
```json
{
  "Escort": {
    "name": "Escort",
    "max_mass": 1000,
    "default_hull_id": "hull_escort"
    // NO hull_mass, NO requirements
  }
}
```

**Detailed Steps:**
1. Open `data/vehicleclasses.json`
2. For each vehicle class entry:
   - Delete `"hull_mass"` key-value pair
   - Delete `"requirements"` key-value pair (now handled by `CrewRequired`/`FuelStorage` abilities)
3. Verify every class retains: `name`, `max_mass`, `default_hull_id`
4. Run: `grep -r "hull_mass" data/vehicleclasses.json` → Should return 0 matches
5. Run: `grep -r "requirements" data/vehicleclasses.json` → Should return 0 matches

**Edge Cases:**
- Any code reading `hull_mass` directly will break → run full test suite after change

---

### Task 5.2: Remove Hardcoded Ship Fallback Registry
**File:** `game/data/load_vehicle_classes.py`

**Current State (~lines 93-101):**
```python
def load_vehicle_classes():
    # ... loading logic ...
    
    # LEGACY FALLBACK - DELETE THIS
    defaults = {
        "Escort": {"hull_mass": 50, "max_mass": 1000},
        "Frigate": {"hull_mass": 100, "max_mass": 2000},
        # ...
    }
    if not vehicle_classes:
        vehicle_classes = defaults
```

**Target State:**
```python
def load_vehicle_classes():
    # ... loading logic ...
    
    if not vehicle_classes:
        raise RuntimeError("Failed to load vehicleclasses.json - data layer corrupt")
    # NO FALLBACK - fail fast on corrupt data
```

**Detailed Steps:**
1. Open `game/data/load_vehicle_classes.py`
2. Locate any `defaults` or `FALLBACK_CLASSES` dictionary
3. Delete the fallback dictionary definition
4. Replace fallback assignment with `raise RuntimeError(...)`
5. Verify tests don't rely on fallback behavior (use proper fixtures instead)

---

### Task 5.3: Eliminate `base_mass` Fallback in `Ship.__init__`
**File:** `game/simulation/entities/ship.py`

**Current State:**
```python
class_def = get_vehicle_classes().get(self.ship_class, {"hull_mass": 50, "max_mass": 1000})
self.base_mass: float = class_def.get('hull_mass', 50)  # LEGACY FALLBACK
```

**Target State:**
```python
class_def = get_vehicle_classes().get(self.ship_class, {})
self.base_mass: float = 0.0  # Hull component provides mass via ShipStatsCalculator
```

**Detailed Steps:**
1. Open `game/simulation/entities/ship.py`
2. Locate `Ship.__init__` method (~line 223)
3. Change default dict from `{"hull_mass": 50, ...}` to `{}`
4. Set `self.base_mass = 0.0` (Hull component now provides mass)
5. Update `Ship.change_class` method similarly if present
6. Run: `grep -r "self.base_mass\s*=" game/simulation/entities/ship.py`
   - Should only show `self.base_mass = 0.0` assignments

---

### Task 5.4: Finalize Ability-Based Derelict Logic
**File:** `game/simulation/entities/ship.py`
**Method:** `update_derelict_status`

**Target Implementation:**
```python
def update_derelict_status(self) -> None:
    """Update derelict status based on CommandAndControl and CrewCapacity abilities."""
    # Essential Capability Check
    has_command = any(
        c.is_operational and c.has_ability('CommandAndControl')
        for layer in self.layers.values()
        for c in layer['components']
    )
    
    if not has_command:
        self.is_derelict = True
        self.bridge_destroyed = True
        return
    
    # Resource Capability Check
    crew_capacity = self.get_total_ability_value('CrewCapacity')
    crew_required = self.get_total_ability_value('CrewRequired')
    
    if crew_required > crew_capacity:
        self.is_derelict = True
        return
    
    self.is_derelict = False
    self.bridge_destroyed = False
```

**Verification:**
- No references to `requirements` JSON key
- All derelict logic driven by component abilities

---

### Task 5.5: Final Verification Gauntlet
**Objective:** 100% test pass rate

**Verification Commands:**
```bash
# Full test suite
pytest tests/ -v --tb=short

# Targeted entity tests
pytest tests/unit/entities/ -v

# Integration tests
pytest tests/integration/ -v

# Grep for legacy patterns (should all return 0 matches)
grep -r "hull_mass" data/vehicleclasses.json
grep -r "COMPONENT_REGISTRY" tests/
grep -r "VEHICLE_CLASSES" tests/
grep -rn "self.base_mass\s*=\s*[^0]" game/simulation/entities/ship.py
```

---

### Task 5.6: Definition of Done Verification
**Criteria Checklist:**
- [ ] `Ship.py` has ZERO hardcoded mass/hp assignments
- [ ] `vehicleclasses.json` contains NO `hull_mass` or `requirements` fields
- [ ] Ship Builder UI renders without overlap at 1080p, 1440p, 4K
- [ ] Save/Load persists fuel/ammo levels correctly (manual verification)

**Manual Test Protocol:**
1. Launch Ship Builder at 1920x1080
2. Create new ship, add Bridge + Engine + Fuel Tank
3. Verify no panel overlaps
4. Add 50% fuel, save game
5. Reload save → verify fuel shows 50% (not 100%)
6. Repeat test at 2560x1440 and 3840x2160

---

## Test Triage Table
| Issue | File | Status | Owner | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Task 4.2a: Dynamic Layer Width | `builder_screen.py` | RESOLVED | UI Specialist | Changed to `calculate_dynamic_layer_width(screen_width)` |
| Task 4.2b: Weapons Panel Width | `builder_screen.py` | RESOLVED | UI Specialist | Subtracted `right_panel_width` from calculation |
| Task 4.3: Vertical Stacking | `right_panel.py` | NOT_APPLICABLE | UI Specialist | Reclassified: right_panel uses single scroll container, no sub-panels |
