# PROJ-364 File Manifest

## Files modified or created

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/services/superweapon_registry.py` | Production (new) | 2 | `SuperweaponSpec` dataclass + `SUPERWEAPONS` tuple (5 strategic) + `find_superweapon_spec` lookup |
| `game/strategy/engine/superweapon_order_processor.py` | Production (refactor) | 3 | Add `execute_superweapon(spec, effect_fn, ...)` dispatcher; refactor 5 strategic `process_*` methods to spec lookup + effect closure. SELF_DESTRUCT unchanged. |
| `game/strategy/engine/order_processor.py` | Production (review-only) | 3 | Lines 704-730: existing lambda dispatch dict reviewed; left as-is unless simplification is trivial |
| `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py` | Test (new) | 1 | 6×3 order-pop matrix characterization (success/failure/missing-ship × 6 weapons) |
| `tests/unit/strategy/engine/test_superweapon_event_payloads.py` | Test (new) | 1 | Event payload characterization for STAR_DESTROYED, WARP_POINT_OPENED, WARP_POINT_CLOSED, DYSON_SPHERE_CREATED |
| `tests/unit/strategy/services/test_superweapon_registry_contract.py` | Test (new) | 2 | Spec contract: order_type valid, event_type valid, ability_name resolves to a real component, stabilizer_blocks members are valid OrderTypes |

## Files referenced for context (not modified)

| File | Purpose |
|------|---------|
| `game/strategy/services/stabilizer_registry.py:36-70` | Pattern reference: frozen dataclass + tuple registry |
| `game/strategy/data/order_types.py` | OrderType enum |
| `game/strategy/events/` | EventType definitions (find via grep `class EventType`) |
| `game/strategy/validation/superweapon_validator.py` | `find_ship_with_ability` — used by spec dispatcher |
| `game/strategy/services/system_destroyer.py` | STELLERATE_STAR delegates here; effect closure preserves the indirection |
| `tests/unit/strategy/engine/test_superweapon_order_processor.py` | Existing per-weapon happy/block/no-ship tests — must continue passing |
| `tests/unit/strategy/engine/test_superweapon_edge_cases.py` | Existing edge-case coverage |
| `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py` | OBS-004/005/006 stabilizer-block coverage |
| `tests/integration/strategy/test_superweapon_integration.py` | End-to-end + serialization round-trip — must continue passing |
