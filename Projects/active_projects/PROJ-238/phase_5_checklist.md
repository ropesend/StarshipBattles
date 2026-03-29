# Phase 5: Rename Processors & Serializer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-238 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rename FleetOrderProcessor → OrderProcessor, FleetOrderSerializer → OrderSerializer. Update all references. Rename files.

---

## Tasks

### Task 5.1: Rename FleetOrderProcessor [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py` → `order_processor.py`
- [ ] Rename class `FleetOrderProcessor` → `OrderProcessor`
- [ ] Rename file `fleet_order_processor.py` → `order_processor.py` (use `git mv`)
- [ ] Update all imports (grep for `fleet_order_processor` and `FleetOrderProcessor`)
- [ ] Update TurnEngine lazy property and constructor references
- [ ] Update interfaces: `IOrderProcessor` (already generic name — verify)

### Task 5.2: Rename FleetOrderSerializer [Medium]
**File:** `game/strategy/data/fleet_order_serializer.py` → `order_serializer.py`
- [ ] Rename class `FleetOrderSerializer` → `OrderSerializer`
- [ ] Rename file (use `git mv`)
- [ ] Update all imports
- [ ] Ensure planet order serialization is handled (dict targets)

### Task 5.3: Rename Fleet-Specific Command Classes [Medium]
**File:** `game/strategy/engine/commands.py`
- [ ] Rename `ClearFleetOrdersCommand` → `ClearOrdersCommand`
- [ ] Rename `DeleteFleetOrderCommand` → `DeleteOrderCommand`
- [ ] Rename `ReorderFleetOrderCommand` → `ReorderOrderCommand`
- [ ] Add `entity_type` field to these commands (to distinguish fleet vs planet)
- [ ] Update command handler registrations in `command_handlers.py`
- [ ] Update StrategyWindowManager callback closures

### Task 5.4: Verify [Simple]
- [ ] `python -m pytest tests/ -n 12 -q` — same count as baseline
- [ ] `grep -r "FleetOrderProcessor\|FleetOrderSerializer\|ClearFleetOrders\|DeleteFleetOrder\|ReorderFleetOrder" game/ tests/` returns 0

---

## Phase Completion Checklist
- [ ] No "Fleet" prefix on any order-related class names
- [ ] Files renamed via git mv
- [ ] All tests pass
