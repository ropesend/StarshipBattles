# Phase 6: UI, Quickstart & Final Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-237 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add shield/energy display to planet info UI, create starting complex, update quickstart builder, run full test suite.

---

## Tasks

### Task 6.1: Add Shield/Energy to Planet Info Display [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** Manual test — start game, select planet, verify info panel

- [ ] In `format_planet_info()` function, after the Colony Status section (~line 100-141), add shield/energy display:
  ```python
  # PROJ-237: Energy & Shield display
  if hasattr(planet, 'energy_capacity') and planet.energy_capacity > 0:
      energy_pct = (planet.energy / planet.energy_capacity * 100) if planet.energy_capacity > 0 else 0
      text += f"<br><b>Energy:</b> {planet.energy:.0f} / {planet.energy_capacity:.0f} ({energy_pct:.0f}%)"

  if hasattr(planet, 'shield_active'):
      # Check if planet has a shield facility
      has_shield = False
      for facility in planet.facilities:
          # Check facility design_data for PlanetaryShield ability
          for layer_data in facility.design_data.get('layers', {}).values():
              if isinstance(layer_data, list):
                  for comp in layer_data:
                      if isinstance(comp, dict) and 'PlanetaryShield' in comp.get('abilities', {}):
                          has_shield = True
                          break
                  if has_shield:
                      break
              if has_shield:
                  break
          if has_shield:
              break
      if has_shield:
          status = "Active" if planet.shield_active else "Inactive"
          text += f"<br><b>Planetary Shield:</b> {status}"
  ```
- [ ] Verify: `format_planet_info()` still works for planets without energy/shield

**Notes:** Use `hasattr()` checks for backward compatibility with mock objects.

---

### Task 6.2: Create Starting Complex Design [Medium]
**File:** `tests/fixtures/quickstart/designs/qs_shield_complex.json` (NEW)
**Tests:** `python -m pytest tests/unit/quickstart/ -v`

Follow `tests/fixtures/quickstart/designs/qs_resupply_depot.json` as template:

- [ ] Create `qs_shield_complex.json`:
  ```json
  {
      "name": "QS Shield Complex",
      "ship_class": "Planetary Complex (Tier 1)",
      "vehicle_type": "Planetary Complex",
      "theme_id": "Federation",
      "team_id": 0,
      "color": [100, 100, 255],
      "ai_strategy": "standard_ranged",
      "layers": {
          "CORE": [
              {
                  "id": "central_complex_command",
                  "modifiers": [
                      {"id": "simple_size_mount", "value": 1.0},
                      {"id": "hardened_mount", "value": 1.0},
                      {"id": "automation", "value": 0.0}
                  ]
              },
              {
                  "id": "crew_quarters",
                  "modifiers": [
                      {"id": "simple_size_mount", "value": 1.0},
                      {"id": "hardened_mount", "value": 1.0}
                  ]
              },
              {
                  "id": "life_support",
                  "modifiers": [
                      {"id": "simple_size_mount", "value": 1.0},
                      {"id": "hardened_mount", "value": 1.0}
                  ]
              }
          ],
          "INNER": [],
          "OUTER": [
              {
                  "id": "planetary_shield_generator",
                  "modifiers": [
                      {"id": "simple_size_mount", "value": 1.0},
                      {"id": "hardened_mount", "value": 1.0}
                  ]
              },
              {
                  "id": "planetary_energy_generator",
                  "modifiers": [
                      {"id": "simple_size_mount", "value": 1.0},
                      {"id": "hardened_mount", "value": 1.0}
                  ]
              },
              {
                  "id": "planetary_energy_battery",
                  "modifiers": [
                      {"id": "simple_size_mount", "value": 1.0},
                      {"id": "hardened_mount", "value": 1.0}
                  ]
              }
          ],
          "ARMOR": []
      },
      "resources": {"fuel": 0.0, "energy": 0.0, "ammo": 0.0},
      "expected_stats": {
          "max_hp": 0, "max_fuel": 0, "max_energy": 0.0,
          "max_ammo": 0.0, "max_speed": 0, "acceleration_rate": 0.0,
          "turn_speed": 0.0, "total_thrust": 0, "mass": 0, "armor_hp_pool": 0
      },
      "_metadata": {
          "is_obsolete": false,
          "times_built": 0,
          "created_date": "2026-03-29T00:00:00.000000",
          "last_modified": "2026-03-29T00:00:00.000000"
      }
  }
  ```

**Notes:** `expected_stats` values will need to be calculated from actual component stats. Set to 0 initially and update after testing.

---

### Task 6.3: Add Shield Complex to Quickstart [Simple]
**File:** `game/strategy/quickstart_builder.py`
**Tests:** `python -m pytest tests/unit/quickstart/ tests/integration/quickstart/ -v`

- [ ] Add `'qs_shield_complex'` to `INITIAL_COMPLEXES` list (line 33, before closing `]`):
  ```python
  INITIAL_COMPLEXES = [
      'qs_complex',
      'qs_metals_complex',
      'qs_organics_complex',
      'qs_vapors_complex',
      'qs_radioactives_complex',
      'qs_exotics_complex',
      'qs_resupply_depot',
      'qs_shield_complex',     # PROJ-237: Planetary shield + energy
  ]
  ```

**Notes:**

---

### Task 6.4: Run Full Test Suite [Simple]
**Tests:** `python -m pytest tests/ -n 12 --timeout=120`

- [ ] Run full test suite
- [ ] Fix any failures from existing tests impacted by new fields
- [ ] Verify all new tests pass
- [ ] Record final test count

**Notes:**

---

### Task 6.5: Manual Verification [Simple]
**Tests:** Manual

- [ ] Start new quickstart game
- [ ] Verify shield complex appears on homeworld's facility list
- [ ] Select homeworld → planet info shows "Planetary Shield: Inactive" and energy display
- [ ] Process a turn → verify energy increases from generator
- [ ] (If UI for issuing orders is available) Activate shield → verify energy drains

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Planet info displays shield status and energy for shielded planets
- [ ] Starting complex created and spawns on homeworld
- [ ] Full test suite passes
- [ ] Manual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
