# PROJ-213: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Root Cause
The `AddToConstructionQueueCommandHandler.execute()` (added in PROJ-208 Phase 2) creates queue items with:
```python
"total_cost": {},         # Empty — should be actual design cost
"resources_consumed": {},  # Empty — should be zero-initialized per resource
```

### Consequence Chain
1. Empty `total_cost` → `ProductionEngine._calculate_tick_expenditure()` iterates over nothing
2. `remaining_cost = {}` → item treated as free/complete
3. `_process_queue_tick_dynamic()` line 272: `if not expenditure.remaining_cost:` → `_complete_item()` called
4. Item instantly completed on first tick, no resources consumed

### Existing Correct Systems
- `ProductionEngine._process_queue_tick_dynamic()` — fully implemented tick-based production, correct
- `DesignCostCalculator.calculate_total_cost()` — centralized cost calculation utility
- `BuildQueueController._build_cost_tracking()` — reference implementation in UI layer (not used by handler)

## Swarm Findings Summary

### Architecture
- Build queue uses CQRS command pattern (PROJ-208): UI dispatches `AddToConstructionQueueCommand` → handler creates queue item dict → `ProductionEngine` processes per-tick
- 100 ticks per turn, production rates from `data/production_rates.json`
- Queue items are plain dicts with `design_id`, `type`, `turns_remaining`, `total_cost`, `resources_consumed`

### Key Patterns to Reuse
- **DesignCostCalculator**: `game/strategy/services/design_cost_calculator.py:37` — static method, takes design_data dict, returns cost dict
- **DesignLibrary**: `game/strategy/systems/design_library.py:21` — loads design JSON by empire_id + save_path
- **Entity owner_id**: Both Planet and Fleet have `owner_id` attribute for empire identification

### Dependencies & Risks
1. **DesignLibrary needs save_path** — available via `session.save_path`, may be None before first save. Handled gracefully with try/except.
2. **Empty cost fallback** — if design data can't be loaded, handler falls back to `{}` with a warning log. This preserves existing behavior for edge cases.

### Opportunities Discovered
- The `BuildQueueController._build_cost_tracking()` method exists but was never called during command-based additions. The fix puts cost calculation in the handler (correct layer) rather than the UI controller.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
