# PROJ-140: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The colonization system has validation at the UI layer (added in PROJ-55) but critical gaps at the execution and command layers allow mismatched colony pods to colonize planets silently. The colony ship is not consumed when the pod type doesn't match.

### Bugs Identified

| # | Bug | Severity | Location |
|---|-----|----------|----------|
| 1 | `process_colonize()` calls validator WITHOUT `component_registry` — skips pod checks at execution time | Critical | `fleet_order_processor.py:194` |
| 2 | `process_colonize()` silently succeeds when no matching pod found — colonizes planet, consumes no ship | High | `fleet_order_processor.py:216-224` |
| 3 | `handle_colonize_designation()` doesn't filter planets by colony pods — allows targeting uncolonizable planets | Medium | `strategy_colonization.py:179-194` |
| 4 | `ColonizeMissionCommandHandler` doesn't validate pod match before queuing orders | Medium | `command_handlers.py:228-290` |
| 5 | "Any Planet" validation skips pod checks entirely | Medium | `colonize_validator.py:85-89` |

### Colonization Pipeline Architecture

```
UI Layer (strategy_colonization.py)
    ├── on_colonize_click() → facade.can_colonize() → [VALIDATES PODS] ✅
    └── handle_colonize_designation() → queue_colonize_mission() → [NO POD FILTER] ❌

Command Layer (command_handlers.py)
    ├── ColonizeCommandHandler → validate_colonize_order() → [VALIDATES PODS] ✅
    └── ColonizeMissionCommandHandler → [NO VALIDATION] ❌

Execution Layer (fleet_order_processor.py)
    └── process_colonize()
        ├── ColonizeValidator.validate(NO registry) → [SKIPS PODS] ❌
        └── find_ship_with_colony_pod() → [SILENT NONE = NO SHIP REMOVED] ❌
```

## Swarm Findings Summary

### Architecture (Architecture Analyst)
- Validation is split across 3 layers: UI filtering, command validation, execution validation
- `ColonizeValidator.validate()` has conditional pod checking (only if `component_registry` provided)
- `process_colonize()` receives `component_registry` as a parameter but never passes it to the validator
- The "Any Planet" path (`target_planet=None`) returns valid immediately if unowned planets exist, regardless of pod availability

### Dependencies (Dependency Mapper)
- `process_colonize()` is only called from `process_end_turn_orders()` (line 516) — single caller
- `ColonizeValidator.validate()` is called from 2 production paths:
  1. `fleet_order_processor.py:194` — WITHOUT registry ❌
  2. `turn_engine.py:301` — WITH registry ✅
- `handle_colonize_designation()` is only called from `strategy_input_handler.py:415`
- `ColonizeMissionCommandHandler` registered as `'QueueColonizeMissionCommand'` in `create_default_registry()`
- `empire.add_colony()` called from colonization execution and game initialization only
- `fleet.remove_ship()` called from colonization (1 place) and superweapons (5 places)

### Test Impact (Test Impact Analyst)
- Existing coverage: 60+ colonization tests across 10 files
- Coverage gaps: No tests for execution with wrong pod type, no tests for mission handler pod validation
- Tests using `target_planet=None` don't pass `component_registry` — won't break
- Backward-compatible tests explicitly verify legacy behavior (no registry) — must preserve
- Key test fixtures in `tests/integration/colonization/test_planet_specific_colonization.py`:
  `MockPlanet`, `MockGalaxy`, `MockSystem`, `make_colony_ship`, `make_combat_ship`, `component_registry`

### Risks (Risk Assessor)
1. **Registry None safety**: `ColonizeValidator.validate()` handles `component_registry=None` gracefully (line 104 check) — LOW risk
2. **Operation ordering**: `fleet.pop_order()` at line 210 happens BEFORE ship removal — if removal fails, order is lost. Fix by finding ship BEFORE mutation.
3. **"Any Planet" test breakage**: Existing "Any" tests don't use `component_registry` — won't break. New behavior only activates when registry provided.
4. **Mission handler pre-validation vs execution**: Fleet pods can change between queue time and execution (combat losses). Pre-validation is early feedback, not a guarantee. Execution-time validation (Phase 1 fix) is the real safety net.

### Data Flow (Data Flow Tracer)
- `_iterate_colony_pods()` silently yields nothing if ship has no 'layers' — correct behavior
- Planet type matching: exact string equality between `PlanetType.ICE_DWARF.name` ("ICE_DWARF") and ability data ("ICE_DWARF") — consistent, no case issues
- COLONIZE orders with Planet targets serialize as `'fleet_ref'` instead of `'planet_ref'` — separate bug, out of scope
- Component registry access: TurnEngine uses `self._registries.components`, facade uses `get_default_registry_provider().get_components()` — two patterns

### Patterns (Pattern Scout)
- All order processors validate BEFORE mutating state
- Command handlers validate BEFORE queuing orders (except ColonizeMissionCommandHandler)
- `on_colonize_click()` pod filtering pattern: `facade.get_fleet_remaining_pods()` → filter planets by `planet_type.name in remaining_pods`
- Return dict structure: `{'type': 'success'|'error'|'prompt'|'no_targets', ...}`
- Command handlers access registries via `session.turn_engine._registries.components` (established pattern) or `get_default_registry_provider()`

## Key Patterns to Reuse

- **ColonizeValidator.find_ship_with_colony_pod()**: `colonize_validator.py:136-155` — exact pod-type match
- **ColonizeValidator.get_available_colony_pods()**: `colonize_validator.py:157-178` — count by type
- **ColonizeValidator.get_committed_colony_pods()**: `colonize_validator.py:180-204` — committed count
- **facade.get_fleet_remaining_pods()**: `strategy_session_facade.py:408-448` — available - committed
- **Pod filtering in on_colonize_click()**: `strategy_colonization.py:96-123` — filter planets by remaining pods
- **Test fixtures**: `test_planet_specific_colonization.py:32-152` — MockPlanet, MockGalaxy, make_colony_ship, component_registry

## Dependencies & Risks

1. **Backward compatibility**: Legacy path (`component_registry=None`) must remain functional — mitigation: all pod checks are gated on `if component_registry is not None`
2. **Operation ordering in process_colonize()**: Must find colony ship BEFORE calling `empire.add_colony()` — mitigation: restructure to pre-check
3. **Mission handler pre-validation can be stale**: Fleet may lose pods in combat before arriving — mitigation: execution-time validation (Bug 1 fix) is the real safety net; pre-validation is early feedback

## Out of Scope

- COLONIZE order serialization bug (Planet targets stored as `fleet_ref` instead of `planet_ref` in FleetOrder.to_dict)
- Save/load round-tripping of COLONIZE orders
- UI feedback improvements (better error messages, planet type indicators)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
