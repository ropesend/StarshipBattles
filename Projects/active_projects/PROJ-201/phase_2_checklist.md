# Phase 2: Extract Remaining Handlers

**Goal:** Extract all remaining column formatters into dedicated handler methods.

**Expected CC reduction:** ~10-12 points (removing all remaining branches)
**Actual CC reduction:** 7 points (22 -> 15)

**Status:** COMPLETE

---

## Tasks

### 2.1 Extract Simple Handlers

#### 2.1.1 `_format_serial`

- [x] **Add method:** `_format_serial` - extracts serial ID formatting
- [x] **Update branch:** calls `self._format_serial(ship)`
- [x] **Run tests:** PASSED

#### 2.1.2 `_format_design`

- [x] **Add method:** `_format_design` - extracts design name formatting
- [x] **Update branch:** calls `self._format_design(ship)`
- [x] **Run tests:** PASSED

#### 2.1.3 `_format_name`

- [x] **Add method:** `_format_name` - extracts ship name formatting
- [x] **Update branch:** calls `self._format_name(ship)`
- [x] **Run tests:** PASSED

#### 2.1.4 `_format_hp_pct`

- [x] **Add method:** `_format_hp_pct` - extracts HP percentage formatting
- [x] **Update branch:** calls `self._format_hp_pct(ship)`
- [x] **Run tests:** PASSED

#### 2.1.5 `_format_tonnage`

- [x] **Add method:** `_format_tonnage` - extracts mass formatting
- [x] **Update branch:** calls `self._format_tonnage(ship)`
- [x] **Run tests:** PASSED

---

### 2.2 Extract Service Handlers (with late imports)

#### 2.2.1 `_format_speed`

- [x] **Add method:** `_format_speed` with late import of FleetSpeedCalculator
- [x] **Update branch:** calls `self._format_speed(ship)`
- [x] **Run tests:** PASSED

#### 2.2.2 `_format_warp`

- [x] **Add method:** `_format_warp` with late import of ShipStatsCalculator
- [x] **Update branch:** calls `self._format_warp(ship)`
- [x] **Run tests:** PASSED

#### 2.2.3 `_format_spaceyard`

- [x] **Add method:** `_format_spaceyard` with late import of FleetCapabilityCalculator
- [x] **Update branch:** calls `self._format_spaceyard(ship)`
- [x] **Run tests:** PASSED

---

### 2.3 Extract Cargo/Transport Handlers

#### 2.3.1 `_format_transport`

- [x] **Add method:** `_format_transport` - extracts passenger capacity formatting
- [x] **Update branch:** calls `self._format_transport(ship)`
- [x] **Run tests:** PASSED

#### 2.3.2 `_format_cargo`

- [x] **Add method:** `_format_cargo` - extracts cargo total formatting
- [x] **Update branch:** calls `self._format_cargo(ship)`
- [x] **Run tests:** PASSED

---

### 2.4 Extract Capability Handler (consolidated)

- [x] **Add method:** `_format_capability(ship, col_id)` - consolidated special capability handler
- [x] **Update branch:** calls `self._format_capability(ship, col_id)`
- [x] **Run tests:** PASSED

---

### 2.5 Phase Verification

- [x] **Run full test file:** 41/41 tests PASSED
- [x] **Full test suite:** 12734 passed, 1 skipped
- [x] **Count handlers:** 13 `_format_*` methods total (verified)
- [x] **CC reduction:** 22 -> 15 (7 points)

---

## Completion Criteria

- [x] All 13 handler methods extracted
- [x] All tests passing
- [x] Late imports preserved in service handlers
- [x] No behavioral changes
