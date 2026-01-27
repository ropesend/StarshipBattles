# Phase 3: Testing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-23 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add tests for scaled components and verify no regressions

---

## Tasks

### Task 3.1: Add unit tests for scaled battery scenario [Medium]
**File:** `tests/unit/strategy/test_ship_stats_service.py` (add to existing file)
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py::TestModifierApplication -v`

- [ ] Add new test class at end of file:
```python
class TestModifierApplication:
    """Tests for PROJ-23: modifier application in ShipStatsService."""

    def test_scaled_battery_energy_capacity(self, mock_component_registry):
        """Battery with size modifier should have scaled energy capacity.

        PROJ-23 regression test: Ensures modifiers from design are applied.
        """
        # Create mock battery with base capacity
        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'ResourceStorage': [{'resource': 'energy', 'amount': 2000}]}
        )

        # Design with size 20 modifier
        design_data = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [{
                    'id': 'battery',
                    'modifiers': [{'id': 'simple_size_mount', 'value': 20.0}]
                }]
            }
        }

        with mock_component_registry({'battery': battery}):
            stats = ShipStatsService.calculate_stats(design_data, {})

        # Base battery: 2000 energy, size 20 = 40000 energy
        assert stats['resource_storage'].get('energy', 0) == 40000

    def test_multiple_small_vs_one_large_battery(self, mock_component_registry):
        """10 size-1 batteries should equal 1 size-10 battery.

        This validates that modifier scaling is applied consistently.
        """
        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'ResourceStorage': [{'resource': 'energy', 'amount': 2000}]}
        )

        # Design with 10 size-1 batteries
        design_small = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [
                    {'id': 'battery', 'modifiers': [{'id': 'simple_size_mount', 'value': 1.0}]}
                    for _ in range(10)
                ]
            }
        }

        # Design with 1 size-10 battery
        design_large = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [{
                    'id': 'battery',
                    'modifiers': [{'id': 'simple_size_mount', 'value': 10.0}]
                }]
            }
        }

        with mock_component_registry({'battery': battery}):
            stats_small = ShipStatsService.calculate_stats(design_small, {})
            stats_large = ShipStatsService.calculate_stats(design_large, {})

        assert stats_small['resource_storage']['energy'] == stats_large['resource_storage']['energy']

    def test_warp_capability_with_scaled_battery(self, mock_component_registry):
        """Ship with scaled battery should have warp capability.

        PROJ-23 regression test: CRU_1 design with 1 large battery should work.
        """
        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'ResourceStorage': [{'resource': 'energy', 'amount': 2000}]}
        )

        warp_drive = MockComponent(
            'warp_drive',
            mass=250,
            max_hp=250,
            abilities={
                'WarpJump': {'max_tonnage': 16000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 3175, 'trigger': 'warp_jump'}
                ]
            }
        )

        design_data = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [
                    {
                        'id': 'battery',
                        'modifiers': [{'id': 'simple_size_mount', 'value': 20.0}]
                    },
                    {
                        'id': 'warp_drive',
                        'modifiers': [{'id': 'simple_size_mount', 'value': 1.0}]
                    }
                ]
            }
        }

        with mock_component_registry({'battery': battery, 'warp_drive': warp_drive}):
            stats = ShipStatsService.calculate_stats(design_data, {})

        # Warp energy cost: 3175
        # Scaled battery: 2000 * 20 = 40000 energy
        # Should have warp capability
        energy_capacity = stats['resource_storage'].get('energy', 0)
        warp_cost = stats['warp_resource_costs'].get('energy', 0)

        assert energy_capacity >= warp_cost, (
            f"Energy capacity {energy_capacity} should be >= warp cost {warp_cost}"
        )
```
- [ ] Run new tests: `pytest tests/unit/strategy/test_ship_stats_service.py::TestModifierApplication -v`
- [ ] Verify: All 3 tests pass

**Notes:** [Filled during implementation]

---

### Task 3.2: Run full regression test suite [Simple]
**File:** N/A
**Tests:** `pytest tests/ -v --tb=short`

- [ ] Run full test suite: `python -m pytest tests/ -q --tb=no`
- [ ] All 4563+ tests should pass
- [ ] If failures: investigate and fix
- [ ] Document any test fixes needed in Notes below

**Notes:** [Filled during implementation]

---

### Task 3.3: Manual verification with game [Simple]
**File:** N/A
**Tests:** Manual

- [ ] Launch game
- [ ] Load save with CRU_1 and CRU_2 designs
- [ ] Open fleet view
- [ ] Verify CRU_1 shows as warp-capable (was broken before)
- [ ] Verify CRU_2 shows as warp-capable (was working before)
- [ ] Attempt warp jump with CRU_1 - should succeed
- [ ] Attempt warp jump with CRU_2 - should succeed

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -q --tb=no` - all tests pass (4563+)
- [ ] Manual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
- [ ] Update plan.md Verification section - check all boxes
