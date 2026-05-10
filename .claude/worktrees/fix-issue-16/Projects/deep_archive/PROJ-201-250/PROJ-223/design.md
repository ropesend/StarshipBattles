# PROJ-223: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Serialization Architecture
- **28 serializable types** across 3 layers (Strategy, Simulation, Research)
- **Entry point:** `SaveGameService` in `game/strategy/systems/save_game_service.py`
- **Save format:** v2.0.0, strict version checking, JSON-based
- **Folder structure:** `turns/` (per-turn state), `designs/empire_N/`, `save_metadata.json`

### Multi-Phase Deserialization
The load process has 6 phases with strict ordering due to dependencies:
1. **Metadata validation** — version check, required keys
2. **Galaxy reconstruction** — creates all planets with preserved IDs
3. **Empire loading** — resolves colony_ids → Planet objects via galaxy, injects registries
4. **Fleet registration** — registers all fleets with galaxy for O(1) lookup
5. **Order reference resolution** — resolves `_fleet_ref`/`_planet_ref` marker dicts to objects
6. **Pursuer tracker rebuild** — re-registers pursuers from resolved MOVE_TO_FLEET orders

### DI Chain
```
GameSession.from_dict()
  ├─ Creates GameRegistries from get_default_registry_provider()
  └─ Empire.from_dict(registries=...)
       └─ Fleet.from_dict(registries=...)
            └─ ShipInstance.from_dict(registries=...)
                 └─ instance._registries = registries  (BUG-107 fix point)
```

### Existing Test Coverage
- **6 test files** in `tests/integration/save_load/` covering folder structure, basic round-trip, edge cases
- **Gaps:** No field-level fidelity, no cross-object reference validation, no DI validation
- **Unit tests** exist for ShipInstance, Fleet, Ship, BattleState serialization but with individual field assertions only

### Test Baseline
- **13,426 tests passing**, 2 skipped, 0 failures

## Swarm Findings Summary

### Architecture
- **Test organization:** New tests go in `tests/integration/save_load/` as `test_roundtrip_*.py` files. Existing conftest provides game session fixtures.
- **Deep compare utility:** Lives in `tests/infrastructure/deep_compare.py` (parallels existing `session_cache.py` location)
- **Test factories:** Function-based factories in `tests/fixtures/strategy_entities.py`, following `create_test_ship()` pattern
- **Serializable registry:** Optional `@register_serializable` decorator in `game/core/json_utils.py` (Core layer, no violations)
- **Layer violations:** None detected. All proposals respect dependency rules.

### Key Patterns to Reuse
- **Field-by-field assertions**: `tests/unit/strategy/ship_instance/test_serialization.py` — existing tests compare individual attributes, not dict equality
- **JSON round-trip verification**: `tests/unit/simulation/test_battle_state_serialization.py:140-147` — `to_dict → json.dumps → json.loads → from_dict → compare`
- **DI fixtures**: `tests/conftest.py:114-148` — three-tier fixture hierarchy (`session_registries`, `fresh_registries`, `minimal_registries`)
- **Factory fixture pattern**: `tests/conftest.py:286-320` — `ship_factory` returns a callable that creates objects with pre-injected dependencies
- **Error isolation**: `deserialize_list()` in `game/core/json_utils.py:170-217` — skips corrupt items with warnings

### Dependencies & Risks

1. **HIGH — Float comparison:** 28 types contain float fields with varying precision requirements. Mitigation: Configurable tolerance in deep_compare utility.
2. **HIGH — Registry state coupling:** Tests must have matching registry state between save and load. Mitigation: Use `fresh_registries` fixture consistently; add explicit registry injection verification.
3. **MEDIUM — Set ordering:** `Empire.built_ship_designs` uses `list(set)` which is non-deterministic. Mitigation: Change to `sorted(list(set))` in Phase 1.
4. **MEDIUM — Large state performance:** Full galaxy deep-compare could be slow. Mitigation: Incremental comparison, fail-fast on first mismatch.
5. **LOW — Non-deterministic fields:** UUIDs, timestamps preserved in save (not regenerated). No impact on testing.

### Opportunities Discovered
- `deserialize_list()` helper already provides error isolation pattern — new tests can verify it works for every type
- Existing `game_session_with_state` fixture creates a mini game — extend for richer test state
- `safe_from_dict()` wraps nested deserialization — framework can systematically test this wrapper

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
