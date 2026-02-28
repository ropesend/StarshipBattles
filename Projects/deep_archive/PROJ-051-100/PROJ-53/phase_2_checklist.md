# Phase 2: Migrate JSON Configurations

**Objective:** Convert all JSON files from legacy ability format to modern ResourceConsumption/Storage/Generation format.

**Prerequisite:** Phase 1 complete (compatibility layer removed)

**Status:** Complete

---

## Tasks

### 2.1 Migrate data/components.json (Production)
- [x] Find all `"EnergyConsumption": X` patterns
- [x] Convert to `"ResourceConsumption": [{"resource": "energy", "amount": X, "trigger": "constant"}]`
- [x] Find all `"AmmoGeneration": X` patterns
- [x] Convert to `"ResourceGeneration": [{"resource": "ammo", "amount": X}]`
- [x] Verify JSON is valid after changes

**Components updated:**
- [x] `shield_regen` - EnergyConsumption → ResourceConsumption
- [x] `master_computer` - EnergyConsumption → ResourceConsumption
- [x] `robotic_drone_crew` - EnergyConsumption → ResourceConsumption
- [x] `emergency_repair_bay` - EnergyConsumption → ResourceConsumption
- [x] `ordnance_vat` - AmmoGeneration → ResourceGeneration, EnergyConsumption → ResourceConsumption

### 2.2 Migrate simulation_tests/data/components.json (Test Data)
- [x] Convert all `"FuelStorage": X` to `"ResourceStorage": [{"resource": "fuel", "amount": X}]`
- [x] Convert all `"AmmoStorage": X` to `"ResourceStorage": [{"resource": "ammo", "amount": X}]`
- [x] Convert all `"EnergyStorage": X` to `"ResourceStorage": [{"resource": "energy", "amount": X}]`
- [x] Convert all `"EnergyConsumption": X` to appropriate ResourceConsumption
- [x] Verify JSON is valid

**Components updated (11 patterns):**
- [x] `test_storage_fuel` - FuelStorage → ResourceStorage(fuel)
- [x] `test_storage_fuel_small` - FuelStorage → ResourceStorage(fuel)
- [x] `test_storage_ammo` - AmmoStorage → ResourceStorage(ammo)
- [x] `test_storage_ammo_small` - AmmoStorage → ResourceStorage(ammo)
- [x] `test_storage_ammo_100` - AmmoStorage → ResourceStorage(ammo)
- [x] `test_storage_ammo_100k` - AmmoStorage → ResourceStorage(ammo)
- [x] `test_storage_energy` - EnergyStorage → ResourceStorage(energy)
- [x] `test_storage_energy_small` - EnergyStorage → ResourceStorage(energy)
- [x] `test_storage_energy_100` - EnergyStorage → ResourceStorage(energy)
- [x] `test_storage_energy_100k` - EnergyStorage → ResourceStorage(energy)
- [x] `test_shield_regen` - EnergyConsumption → ResourceConsumption

### 2.3 Migrate tests/unit/data/test_components.json
- [x] Convert all `"EnergyGeneration": X` to `"ResourceGeneration": [{"resource": "energy", "amount": X}]`
- [x] Convert all `"FuelStorage": X` to ResourceStorage format
- [x] Convert all `"AmmoStorage": X` to ResourceStorage format
- [x] Convert all `"EnergyStorage": X` to ResourceStorage format
- [x] Convert all `"EnergyConsumption": X` to ResourceConsumption format
- [x] Verify JSON is valid

**Components updated (5 patterns):**
- [x] `test_gen_fusion` - EnergyGeneration → ResourceGeneration(energy)
- [x] `test_storage_fuel` - FuelStorage → ResourceStorage(fuel)
- [x] `test_storage_ammo` - AmmoStorage → ResourceStorage(ammo)
- [x] `test_storage_energy` - EnergyStorage → ResourceStorage(energy)
- [x] `test_shield_regen` - EnergyConsumption → ResourceConsumption

### 2.4 Verify JSON Validity
- [x] Run JSON lint on all modified files (all passed)
- [x] Attempt to load components via game loader (via pytest)
- [x] Check for parse errors (none)

---

## Verification

```bash
# All return ZERO results:
grep -r '"EnergyStorage"' data/ simulation_tests/data/ tests/unit/data/ --include="*.json"  # 0
grep -r '"FuelStorage"' data/ simulation_tests/data/ tests/unit/data/ --include="*.json"    # 0
grep -r '"AmmoStorage"' data/ simulation_tests/data/ tests/unit/data/ --include="*.json"    # 0
grep -r '"EnergyGeneration"' data/ simulation_tests/data/ tests/unit/data/ --include="*.json"  # 0
grep -r '"EnergyConsumption"' data/ simulation_tests/data/ tests/unit/data/ --include="*.json" # 0
grep -r '"AmmoGeneration"' data/ simulation_tests/data/ tests/unit/data/ --include="*.json"    # 0
```

---

## Files Modified
- `data/components.json` - 5 patterns updated
- `simulation_tests/data/components.json` - 11 patterns updated
- `tests/unit/data/test_components.json` - 5 patterns updated

---

## Notes

- All JSON files validated successfully
- 14 test failures remain - these are from Python test code using legacy patterns directly
- Proceed to Phase 5 (Fix Test Breakage) to fix Python test fixtures
