# Phase 4: Strategy Layer Consolidation

**Findings:** CQ-02, CQ-22, CQ-23, CQ-06
**Effort:** Medium
**Goal:** Consolidate strategy layer duplication in resources, serialization, and ability extraction

## Tasks

### 4.1 Consolidate resource verification/consumption (CQ-02)
- [ ] Create `FleetResourceAggregator._verify_and_consume_resources(cost_getter, consume=False)` method
- [ ] Refactor `has_resources_for_movement()` to use generic method
- [ ] Refactor `has_resources_for_warp()` to use generic method
- [ ] Refactor `consume_movement_resources()` to use generic method
- [ ] Refactor `consume_warp_resources()` to use generic method
- [ ] Run targeted resource tests
- [ ] Run full test suite

### 4.2 Create deserialization list utility (CQ-22)
- [ ] Create `deserialize_list()` utility in appropriate module (e.g., `game/core/json_utils.py`)
- [ ] Refactor `StarSystem.from_dict()` error-handling loops (4 loops)
- [ ] Refactor `Planet.from_dict()` error-handling loops (2 loops)
- [ ] Refactor `Galaxy.from_dict()` error-handling loops (5 loops)
- [ ] Write tests for `deserialize_list()` utility
- [ ] Run full test suite

### 4.3 Expand ComponentInspector with ability extraction (CQ-23)
- [ ] Add `get_ability_from_component(comp, ability_name, registries)` to ComponentInspector
- [ ] Add `collect_ability_from_design(design_data, ability_name, registries)` to ComponentInspector
- [ ] Refactor `HarvestingEngine` harvester extraction to use inspector
- [ ] Refactor `EmpireEconomyCalculator` harvester extraction to use inspector
- [ ] Refactor `Planet.get_max_fuel_storage()` to use inspector
- [ ] Run full test suite

### 4.4 Consolidate serialization patterns (CQ-06)
- [ ] Identify shared serialization utilities (HexCoord, safe parsing)
- [ ] Extract shared helpers for Fleet and ShipInstance `to_dict()`/`from_dict()`
- [ ] Refactor both classes to use shared helpers
- [ ] Run save/load tests

## Completion Checklist
- [ ] All tasks above completed
- [ ] Full test suite passes
- [ ] Resource consumption behavior verified unchanged
- [ ] Save/load cycle verified
