# Phase 1: Direct Attribute Access (Ship Properties)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-194 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace getattr(ship, 'attr', default) with direct ship.attr access where the attribute is always present after Ship.__init__() and recalculate_stats().

---

## Tasks

### Task 1.1: right_panel.py — Ship property getattr removal [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 79: `getattr(self.builder.ship, 'theme_id', 'Federation')` → `self.builder.ship.theme_id`
- [ ] Line 91: `getattr(self.builder.ship, 'vehicle_type', "Ship")` → `self.builder.ship.vehicle_type`
- [ ] Line 172: `getattr(s, 'theme_id', 'Federation')` → `s.theme_id`
- [ ] Line 181: `getattr(s, 'vehicle_type', "Ship")` → `s.vehicle_type`
- [ ] Line 241: `getattr(self.builder.ship, 'theme_id', 'Federation')` → `self.builder.ship.theme_id`
- [ ] Verify: Run tests, confirm no AttributeError

**Notes:**

---

### Task 1.2: design_report_panel.py — Ship property getattr removal [Simple]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 143: `getattr(ship, 'vehicle_type', 'Unknown')` → `ship.vehicle_type`
- [ ] Line 144: `getattr(ship, 'ship_class', 'Unknown')` → `ship.ship_class`
- [ ] Line 183: `getattr(ship, 'theme_id', 'Federation')` → `ship.theme_id`
- [ ] Line 184: `getattr(ship, 'ship_class', 'Unknown')` → `ship.ship_class`
- [ ] Verify: Run tests, confirm no AttributeError

**Notes:**

---

### Task 1.3: weapons_viewmodel.py — Ship defense score getattr removal [Simple]
**File:** `game/ui/screens/builder/weapons_viewmodel.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 147: `getattr(ship, 'total_defense_score', 0.0)` → `ship.total_defense_score`
- [ ] Verify: Run tests

**Notes:**

---

### Task 1.4: workshop_event_router.py — Ship property getattr removal [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 375: `getattr(gui.ship, 'vehicle_type', "Ship")` → `gui.ship.vehicle_type`
- [ ] Verify: Run tests

**Notes:**

---

### Task 1.5: stats_config.py — Ship property getattr removal (non-resource) [Simple]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/ --testmon`

These lines use getattr for ship attributes that are always present:
- [ ] Line 111: `getattr(ship, 'max_targets', 1)` → `ship.max_targets`
- [ ] Line 124: `getattr(ship, 'total_maneuver_points', 0)` → `ship.total_maneuver_points`
- [ ] Line 133: `getattr(ship, 'mass', 0)` → `ship.mass`
- [ ] Line 134: `getattr(ship, 'total_strategic_movement', 0)` → `ship.total_strategic_movement`
- [ ] Line 143: `getattr(ship, 'fuel_consumption', 0)` → `ship.fuel_consumption`
- [ ] Line 146: `getattr(ship, 'ammo_consumption', 0)` → `ship.ammo_consumption`
- [ ] Line 149: `getattr(ship, 'energy_consumption', 0)` → `ship.energy_consumption`
- [ ] Line 570: `hasattr(ship, 'resources')` → remove check (ship.resources always exists, may be None)
- [ ] Line 603: `hasattr(ship, 'construction_cost')` → remove check (always present as dict)
- [ ] Verify: Run tests

**Notes:** Lines 29-30 (StatDefinition.get_value) are intentional generic dispatch — DO NOT change.

---

### Task 1.6: components.py — Ship property getattr/hasattr removal [Simple]
**File:** `game/ui/screens/builder/components.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Lines 84-92: Replace `getattr(ship_context, 'base_mass', 1000)` / `hasattr(ship_context, 'max_mass_budget')` / `hasattr(ship_context, 'base_mass')` chain → `ship_context.max_mass_budget` (always present on Ship)
- [ ] Verify: Run tests

**Notes:** The entire if/elif chain (lines 84-92) can be simplified to just use `ship_context.max_mass_budget`.

---

### Task 1.7: workshop_ship_io.py — Context property getattr removal [Simple]
**File:** `game/ui/screens/workshop_ship_io.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 100: `getattr(self.context, 'built_designs', set())` → `self.context.built_designs` (always present on WorkshopContext dataclass with default_factory=set)
- [ ] Verify: Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
