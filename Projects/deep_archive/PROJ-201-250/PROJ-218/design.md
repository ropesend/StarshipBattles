# PROJ-218: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Root Cause
`DesignCostCalculator.calculate_total_cost()` in `game/strategy/services/design_cost_calculator.py` iterates design JSON layers and checks `component.get('resource_cost', {})`. But design files only contain component **references** — entries like `{"id": "bridge", "modifiers": [...]}` without `resource_cost`. The actual `resource_cost` data lives in `data/components.json` (component registry definitions).

**Result:** The method always returns `{}` for real design files. Queue items get `total_cost: {}`, and the renderer sees an empty dict (falsy in Python), showing no costs.

### Secondary Bug
`DesignMetadata._calculate_resource_cost()` (line 217) has the same issue AND uses the wrong field name (`"cost"` instead of `"resource_cost"`).

### Why the Design Report Panel Works
The right-side panel loads a full **Ship object** via `BuildQueueController.refresh_design_report()`:
```
design_data → SimulationDesignLoader → Ship(from_dict) → ShipStatsCalculator.calculate()
  → resolves components from registry
  → evaluates formulas (e.g., "=50 * sqrt(ship_class_mass / 1000)")
  → applies modifier multipliers (cost_mult)
  → sets ship.construction_cost
```

### Why Tests Didn't Catch This
All `test_design_cost_calculator.py` tests use inline `resource_cost` on component entries:
```python
{"resource_cost": {"minerals": 100, "gas": 50}}  # Test format
```
Real design files never have this format:
```python
{"id": "bridge", "modifiers": [...]}  # Actual format
```

## Swarm Findings Summary

### Architecture
- **Two cost paths exist:** Ship-based (correct, used by UI) and raw-JSON-scanning (broken, used by command handler)
- **Strategy → Simulation dependency is allowed:** Command handler can use `SimulationDesignLoader` to create Ship objects
- **`session.registries`** provides clean DI access to component definitions from command handlers

### Key Patterns to Reuse
- **`BuildQueueController._get_design_cost()`**: `build_queue_controller.py:176-200` — loads Ship, extracts `construction_cost`. Reference implementation.
- **`ShipStatsCalculator.calculate()`**: `ship_stats.py:104-114` — aggregates component costs with formula evaluation and modifier multipliers.
- **`ComponentResourceManager.get_resource_cost()`**: `component_resource_manager.py:83-119` — handles formulas and `cost_mult` modifier.

### Dependencies & Risks
1. **Performance:** Ship loading involves full stats calculation, but only runs once per queue addition (not per tick). Acceptable cost.
2. **Legacy save data:** Old queue items with `total_cost: {}` will auto-complete for free. Fix: harden `_validate_queue_item()` to reject empty costs.
3. **`Planet.add_production()`:** Legacy method creating incomplete items. Only used by 2 tests. Delete per eradication policy.
4. **All `DesignCostCalculator` callers need updating:** Command handler, ProductionEngine, MaintenanceEngine, EmpireEconomyCalculator.

### Opportunities Discovered
- `DesignMetadata._calculate_resource_cost()` uses wrong field name (`"cost"` vs `"resource_cost"`), fixing this improves design library cost display consistency.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
