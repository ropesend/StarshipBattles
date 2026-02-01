# Phase 4: Enhance UI Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Filter planet selection by available pods and improve UX

---

## Tasks

### Task 4.1: Modify on_colonize_click() to Filter by Pods [Medium]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** Manual testing + integration tests

- [ ] Find `on_colonize_click(self, fleet)` method (around line 50-100)
- [ ] After getting planets at location, add pod inventory check:
  ```python
  # Get available pod types (accounting for committed orders)
  from game.strategy.validation.colonize_validator import ColonizeValidator
  available_pods = ColonizeValidator.get_available_colony_pods(fleet)
  committed_pods = ColonizeValidator.get_committed_colony_pods(fleet)

  remaining_pods = {}
  for planet_type, count in available_pods.items():
      committed = committed_pods.get(planet_type, 0)
      remaining = count - committed
      if remaining > 0:
          remaining_pods[planet_type] = remaining
  ```
- [ ] Add planet filtering logic:
  ```python
  # Filter to colonizable planets with matching pod
  colonizable_planets = []
  for planet in planets:
      # Must be unowned
      if planet.owner_id is not None:
          continue

      # Must have available pod for this type
      planet_type_str = planet.planet_type.name
      if planet_type_str not in remaining_pods:
          continue

      # Must not be targeted by another fleet
      if not self.facade.can_colonize(fleet.id, planet.id):
          continue

      colonizable_planets.append(planet)
  ```
- [ ] Update result handling to use `colonizable_planets` instead of raw `planets`
- [ ] Verify: Logic flows correctly, handles edge cases

**Notes:**

---

### Task 4.2: Add Helpful Error Messages [Simple]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** Manual testing

- [ ] Add method `_show_no_valid_targets_message(self, fleet, available_pods)`:
  ```python
  def _show_no_valid_targets_message(self, fleet, available_pods):
      """Show message explaining why no planets can be colonized."""
      if not available_pods:
          message = "No colony pods in fleet"
      else:
          pod_types = ", ".join(available_pods.keys())
          message = f"No colonizable planets for available pods ({pod_types})"

      self.show_message(message)
  ```
- [ ] In `on_colonize_click()`, when `len(colonizable_planets) == 0`:
  - Call `self._show_no_valid_targets_message(fleet, remaining_pods)`
- [ ] Verify: Messages display correctly

**Notes:** Existing `show_message()` method should handle display

---

### Task 4.3: Display Planet Types in Selection UI [Medium]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** Manual testing

- [ ] Find `_prompt_planet_selection(self, fleet, planets)` method (or equivalent)
- [ ] Modify planet display to include type:
  ```python
  for planet in planets:
      type_display = planet.planet_type.name.replace('_', ' ').title()
      display_text = f"{planet.name} ({type_display})"
      # Use display_text in selection UI rendering
  ```
- [ ] Verify: Planet types display correctly in selection list

**Notes:** Exact implementation depends on current UI framework

---

### Task 4.4: Update UI Tests [Medium]
**File:** `tests/integration/ui/test_colonization_facade.py`
**Tests:** `pytest tests/integration/ui/test_colonization_facade.py -v`

- [ ] Add test: `test_colonization_filters_by_available_pods()`
  - Create fleet with Continental pod only
  - Create system with Continental + Ice Dwarf planets
  - Call colonization UI logic
  - Assert: Only Continental planet shown as option
- [ ] Add test: `test_colonization_accounts_for_committed_orders()`
  - Create fleet with 1 Continental pod
  - Add 1 COLONIZE order for Continental planet
  - Try to colonize 2nd Continental planet
  - Assert: No valid targets (pod already committed)
- [ ] Add test: `test_colonization_shows_message_when_no_pods()`
  - Create fleet without colony pods
  - Try to colonize
  - Assert: Error message about no pods
- [ ] Run tests: `pytest tests/integration/ui/test_colonization_facade.py -v`
- [ ] Verify: All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/integration/ui/ -v` - all tests pass
- [ ] Manual test: Fleet with Continental pod only shows Continental planets
- [ ] Manual test: Chained orders reduce available options
- [ ] Manual test: Error message when no pods
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
