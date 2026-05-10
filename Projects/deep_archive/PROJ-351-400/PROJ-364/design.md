# PROJ-364: Design Document

## Initial Analysis

`superweapon_order_processor.py` has 5 strategic-superweapon `process_*` methods (~660 LOC total). Each repeats:
1. `fleet.get_current_order()`
2. `if order.type != EXPECTED: return SuperweaponResult(success=False, ...)`
3. Resolve target (planet | system | dict params)
4. `_check_blocking_stabilizer(...)` — pop order + return if blocked
5. `SuperweaponValidator.find_ship_with_ability(fleet, "<HardcodedAbilityName>", component_registry)` — pop + return if no ship
6. **Effect-specific mutation** — varies per weapon
7. `self._finalize_superweapon(...)` — already shared

Steps 1-5 + 7 are identical pattern; step 6 is unique. PROJ-364 makes 1-5 spec-driven so the per-weapon code shrinks to step 6 + a spec entry.

## Swarm Findings Summary

### Architecture (findings/01_architecture.md)

Spec table:
| Superweapon | OrderType | ability_name | target_type | consume_ship | EventType | Stabilizer |
|---|---|---|---|---|---|---|
| Implode Planet | IMPLODE_PLANET | DestroyPlanet | planet | No | PLANET_DESTROYED | GeologicStabilizer |
| Stellerate Star | STELLERATE_STAR | (system_destroyer indirection) | none | **Yes** | STAR_DESTROYED | StellarStabilizer |
| Open Warp Point | OPEN_WARP_POINT | OpenWarpPoint | dict | No | WARP_POINT_OPENED | WarpFieldStabilizer |
| Close Warp Point | CLOSE_WARP_POINT | CloseWarpPoint | dict | No | WARP_POINT_CLOSED | WarpFieldStabilizer |
| Create Dyson Sphere | CREATE_DYSON_SPHERE | CreateDysonSphere | none | No | DYSON_SPHERE_CREATED | StellarStabilizer |
| **Self-Destruct (excluded)** | SELF_DESTRUCT | — | ship_ids | selective | SHIPS_SELF_DESTRUCTED | None |

```python
@dataclass(frozen=True)
class SuperweaponSpec:
    order_type: OrderType
    ability_name: str | None              # None if dispatched via system_destroyer (STELLERATE_STAR exception)
    target_type: str                      # 'planet' | 'dict' | 'none'
    consume_ship: bool
    event_type: EventType
    stabilizer_blocks: tuple[OrderType, ...]
```

### Dependencies (findings/02_dependencies.md)
- Production caller: `order_processor.py:704-730` — `superweapon_handlers` dict of lambdas. Replace with spec-table lookup.
- `SuperweaponValidator.find_ship_with_ability` — used 4 times directly + once in validator. Spec drives the ability_name argument now.
- EventType members emitted: PLANET_DESTROYED, STAR_DESTROYED, WARP_POINT_OPENED, WARP_POINT_CLOSED, DYSON_SPHERE_CREATED, SHIPS_SELF_DESTRUCTED. Replay capture + event log subscribe to these — payloads must remain stable.
- Stabilizer scopes per OrderType — `stabilizer_registry.py` STABILIZERS tuple already defines which stabilizer blocks which superweapon.

### Test Impact (findings/03_test_impact.md)
- Existing per-weapon tests cover happy path + stabilizer-block + missing-ship for all 6 types.
- Gap A: order-pop semantics not unified. Need a 6×3 matrix test (success / failure / missing-ship → does the order pop?).
- Gap B: event payload contents — only PLANET_DESTROYED and SHIPS_SELF_DESTRUCTED have payload assertions today. Need parity for the other 4.
- Gap C: SuperweaponSpec ↔ component-ability contract test.

### Risks
- **STELLERATE_STAR ability-name asymmetry:** the method does NOT call `find_ship_with_ability("DestroyStar", ...)` directly; it delegates to `system_destroyer` (lines 267-272). Spec field `ability_name=None` and a special-case flag, OR put the indirection inside the per-weapon effect closure. **Decision:** put it in the closure; spec carries `ability_name=None` documenting that this weapon delegates.
- **CREATE_DYSON_SPHERE race-config preferences:** lines 597-613 pull race_config to customize the new planet (gravity/temperature/atmosphere). Stays inside the effect closure — transparent to spec.
- **CLOSE_WARP_POINT sector-vs-system validation:** lines 464-474 strictly validate fleet is at the exact warp-point hex, not just the system. Stays in effect closure.
- **Event payload divergence:** if the payload constructor logic moves between `process_*` and `_finalize_superweapon`, the kwargs spread in `_finalize_superweapon` may need adjustment. Phase 1 characterization pins the payload shape.

### Key Patterns to Reuse
- `stabilizer_registry.py:36-70` — frozen dataclass + immutable tuple + `find_*` lookup.
- `_finalize_superweapon(...)` — already shared tail; spec drives the kwargs now.

## Design Decisions
See [decisions.md](decisions.md) for full log.
