# Phase 6: Final Cleanup & Verification

**Objective:** Verify complete elimination of legacy patterns and clean up any remaining references.

**Prerequisite:** Phase 1-5 complete (all tests passing)

---

## Tasks

### 6.1 Comprehensive Grep Audit - Legacy Ability Names
Run these commands - ALL should return ZERO results:

- [ ] `grep -rn '"EnergyStorage"' game/ tests/ data/ simulation_tests/ --include="*.py" --include="*.json"`
- [ ] `grep -rn '"FuelStorage"' game/ tests/ data/ simulation_tests/ --include="*.py" --include="*.json"`
- [ ] `grep -rn '"AmmoStorage"' game/ tests/ data/ simulation_tests/ --include="*.py" --include="*.json"`
- [ ] `grep -rn '"EnergyGeneration"' game/ tests/ data/ simulation_tests/ --include="*.py" --include="*.json"`
- [ ] `grep -rn '"EnergyConsumption"' game/ tests/ data/ simulation_tests/ --include="*.py" --include="*.json"`
- [ ] `grep -rn '"AmmoGeneration"' game/ tests/ data/ simulation_tests/ --include="*.py" --include="*.json"`
- [ ] `grep -rn '"AmmoConsumption"' game/ tests/ data/ simulation_tests/ --include="*.py" --include="*.json"`

### 6.2 Comprehensive Grep Audit - Direct Property Access
Run these commands - ALL should return ZERO results:

- [ ] `grep -rn "\.current_fuel" game/ --include="*.py"`
- [ ] `grep -rn "\.max_fuel" game/ --include="*.py"`
- [ ] `grep -rn "\.current_energy" game/ --include="*.py"`
- [ ] `grep -rn "\.max_energy" game/ --include="*.py"`
- [ ] `grep -rn "\.current_ammo" game/ --include="*.py"`
- [ ] `grep -rn "\.max_ammo" game/ --include="*.py"`
- [ ] `grep -rn "\.fuel_consumption" game/ --include="*.py"` (except where explicitly needed)
- [ ] `grep -rn "\.energy_consumption" game/ --include="*.py"` (except where explicitly needed)

### 6.3 Comprehensive Grep Audit - Legacy Cost Fields
Run these commands - ALL should return ZERO results:

- [ ] `grep -rn "strategic_fuel_per_hex" game/ --include="*.py"`
- [ ] `grep -rn "warp_fuel_cost" game/ --include="*.py"` (except in warp_resource_costs context)
- [ ] `grep -rn "warp_energy_cost" game/ --include="*.py"` (except in warp_resource_costs context)
- [ ] `grep -rn "fuel_cost_per_hex" game/ --include="*.py"` (except in resource_consumption_per_hex context)

### 6.4 Verify No Compatibility Code Remains
- [ ] Verify `abilities/__init__.py` has NO lambda factories for legacy names
- [ ] Verify `abilities/__init__.py` has NO ABILITY_CLASS_MAP entries for legacy names
- [ ] Verify `ship_stats_calculator.py` has NO legacy ability checks
- [ ] Verify `ability_aggregator.py` has NO FuelStorage alias code

### 6.5 Remove Any Deprecated Ship Properties
**File:** `game/simulation/entities/ship.py`

- [ ] Remove `current_fuel` property if it exists (or make it raise error)
- [ ] Remove `max_fuel` property if it exists (or make it raise error)
- [ ] Remove `current_energy` property if it exists
- [ ] Remove `max_energy` property if it exists
- [ ] Remove `current_ammo` property if it exists
- [ ] Remove `max_ammo` property if it exists
- [ ] Or: Convert to properties that raise `DeprecationError`

### 6.6 Update Documentation
- [ ] Update any docstrings mentioning legacy patterns
- [ ] Update `docs/adding_abilities.md` if it references legacy patterns
- [ ] Update any architecture docs

### 6.7 Clean Up Legacy Docs/Tools
- [ ] Review `_legacy_docs/` for references (OK to leave as historical)
- [ ] Review `Tools/` for any migration tools that are now obsolete
- [ ] Archive or remove `Tools/migrate_data.py` if no longer needed

### 6.8 Run Full Test Suite - Final
- [ ] `pytest tests/ -v` - ALL PASS
- [ ] `pytest simulation_tests/ -v` - ALL PASS
- [ ] `pytest tests/ -n 4` - Parallel execution works
- [ ] No warnings about deprecated patterns

### 6.9 Manual Smoke Test
- [ ] Launch game
- [ ] Open ship builder - verify resource display works
- [ ] Create ship with fuel tank - verify FuelStorage → ResourceStorage works
- [ ] Create ship with power plant - verify energy generation works
- [ ] View fleet report - verify fuel/energy totals display
- [ ] Run combat - verify endurance display works

### 6.10 Update Project Index
- [ ] Mark PROJ-52 as complete in `projects_index.md`
- [ ] Add completion notes

---

## Final Verification Script

Create and run a verification script:

```bash
#!/bin/bash
echo "=== PROJ-52 Final Verification ==="

echo -e "\n--- Legacy Ability Names (should be 0) ---"
grep -rn '"EnergyStorage"\|"FuelStorage"\|"AmmoStorage"\|"EnergyGeneration"\|"EnergyConsumption"\|"AmmoGeneration"' \
  game/ tests/ data/ simulation_tests/ --include="*.py" --include="*.json" | wc -l

echo -e "\n--- Direct Property Access (should be 0) ---"
grep -rn '\.current_fuel\|\.max_fuel\|\.current_energy\|\.max_energy\|\.current_ammo\|\.max_ammo' \
  game/ --include="*.py" | wc -l

echo -e "\n--- Legacy Cost Fields (should be 0) ---"
grep -rn 'strategic_fuel_per_hex' game/ --include="*.py" | wc -l

echo -e "\n--- Test Suite ---"
pytest tests/ --tb=no -q 2>&1 | tail -5

echo -e "\n=== Verification Complete ==="
```

---

## Success Criteria (Final)

| Metric | Required |
|--------|----------|
| Legacy ability names in code | 0 |
| Legacy ability names in JSON | 0 |
| Direct property access | 0 |
| Legacy cost field references | 0 |
| Compatibility factories | 0 |
| Unit tests passing | 100% |
| Integration tests passing | 100% |
| Simulation tests passing | 100% |
| Manual smoke test | PASS |

---

## Notes

- Document any intentional exceptions (e.g., warning message text)
- Consider adding linting rule to prevent legacy pattern reintroduction
- Update onboarding docs for new contributors
- Celebrate when done - this is a major cleanup!
