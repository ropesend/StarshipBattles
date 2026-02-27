# Phase 2: Extract Remaining Handlers

**Goal:** Extract all remaining column formatters into dedicated handler methods.

**Expected CC reduction:** ~10-12 points (removing all remaining branches)

---

## Tasks

### 2.1 Extract Simple Handlers

#### 2.1.1 `_format_serial`

- [ ] **Add method:**
  ```python
  def _format_serial(self, ship: "ShipInstance") -> str:
      """Format ship serial ID for display."""
      display_id = ship.get_display_id()
      return display_id if display_id else ship.instance_id[:8]
  ```

- [ ] **Update branch** (lines 143-145):
  ```python
  elif col_id == "serial":
      return self._format_serial(ship)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k serial`

#### 2.1.2 `_format_design`

- [ ] **Add method:**
  ```python
  def _format_design(self, ship: "ShipInstance") -> str:
      """Format ship design name for display."""
      return ship.design_data.get("name", ship.design_id)
  ```

- [ ] **Update branch** (lines 147-148):
  ```python
  elif col_id == "design":
      return self._format_design(ship)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k design`

#### 2.1.3 `_format_name`

- [ ] **Add method:**
  ```python
  def _format_name(self, ship: "ShipInstance") -> str:
      """Format ship name for display."""
      return ship.name
  ```

- [ ] **Update branch** (lines 150-151):
  ```python
  elif col_id == "name":
      return self._format_name(ship)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k name`

#### 2.1.4 `_format_hp_pct`

- [ ] **Add method:**
  ```python
  def _format_hp_pct(self, ship: "ShipInstance") -> str:
      """Format HP percentage for display."""
      return f"{ship.get_hp_percentage() * 100:.0f}%"
  ```

- [ ] **Update branch** (lines 153-154):
  ```python
  elif col_id == "hp_pct":
      return self._format_hp_pct(ship)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k hp`

#### 2.1.5 `_format_tonnage`

- [ ] **Add method:**
  ```python
  def _format_tonnage(self, ship: "ShipInstance") -> str:
      """Format ship tonnage for display."""
      mass = ship.get_calculated_stats().get("mass", 0)
      return f"{mass:,.0f}"
  ```

- [ ] **Update branch** (lines 175-177):
  ```python
  elif col_id == "tonnage":
      return self._format_tonnage(ship)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k tonnage`

---

### 2.2 Extract Service Handlers (with late imports)

#### 2.2.1 `_format_speed`

- [ ] **Add method:**
  ```python
  def _format_speed(self, ship: "ShipInstance") -> str:
      """Format ship speed for display."""
      # INTENTIONAL LATE IMPORT: Avoid circular import
      from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
      speed = FleetSpeedCalculator.calculate_ship_speed(ship)
      return str(speed)
  ```

- [ ] **Update branch** (lines 166-173):
  ```python
  elif col_id == "speed":
      return self._format_speed(ship)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k speed`

#### 2.2.2 `_format_warp`

- [ ] **Add method:**
  ```python
  def _format_warp(self, ship: "ShipInstance") -> str:
      """Format warp capability for display."""
      # INTENTIONAL LATE IMPORT: Avoid circular import
      from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
      return "Yes" if ShipStatsCalculator.has_warp_capability(ship) else "No"
  ```

- [ ] **Update branch** (lines 179-185):
  ```python
  elif col_id == "warp":
      return self._format_warp(ship)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k warp`

#### 2.2.3 `_format_spaceyard`

- [ ] **Add method:**
  ```python
  def _format_spaceyard(self, ship: "ShipInstance") -> str:
      """Format spaceyard capability for display."""
      # INTENTIONAL LATE IMPORT: Avoid circular import
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      return "Yes" if FleetCapabilityCalculator.ship_has_spaceyard(ship) else "No"
  ```

- [ ] **Update branch** (lines 187-195):
  ```python
  elif col_id == "spaceyard":
      return self._format_spaceyard(ship)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k spaceyard`

---

### 2.3 Extract Cargo/Transport Handlers

#### 2.3.1 `_format_transport`

- [ ] **Add method:**
  ```python
  def _format_transport(self, ship: "ShipInstance") -> str:
      """Format passenger transport capacity for display."""
      capacity = ship.get_cargo_capacity("passengers")
      current = ship.get_current_cargo("passengers")
      return f"{current}/{capacity}" if capacity > 0 else "--"
  ```

- [ ] **Update branch** (lines 197-200):
  ```python
  elif col_id == "transport":
      return self._format_transport(ship)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k transport`

#### 2.3.2 `_format_cargo`

- [ ] **Add method:**
  ```python
  def _format_cargo(self, ship: "ShipInstance") -> str:
      """Format total cargo for display."""
      total = sum(ship.cargo_contents.values()) if ship.cargo_contents else 0
      return str(total) if total > 0 else "--"
  ```

- [ ] **Update branch** (lines 216-218):
  ```python
  elif col_id == "cargo":
      return self._format_cargo(ship)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k cargo`

---

### 2.4 Extract Capability Handler (consolidated)

- [ ] **Add method:**
  ```python
  def _format_capability(self, ship: "ShipInstance", col_id: str) -> str:
      """Format special capability for display."""
      # INTENTIONAL LATE IMPORT: Avoid circular import
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      ability_name = SPECIAL_CAPABILITY_COLUMNS[col_id]
      return "Yes" if FleetCapabilityCalculator.ship_has_ability(ship, ability_name) else "No"
  ```

- [ ] **Update branch** (lines 220-231):
  ```python
  elif col_id in SPECIAL_CAPABILITY_COLUMNS:
      return self._format_capability(ship, col_id)
  ```

- [ ] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k "Special"`

---

### 2.5 Phase Verification

- [ ] **Run full test file:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v`
- [ ] **Verify:** All 37+ tests pass
- [ ] **Count handlers:** Should have 13 `_format_*` methods total

---

## Completion Criteria

- All 13 handler methods extracted
- All tests passing
- Late imports preserved in service handlers
- No behavioral changes
