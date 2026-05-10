# PROJ-354 Architecture Analysis

## 1. Superweapon table

| Superweapon | Order Type | Required Ability | Target Type | Consume Ship | Event Type | Stabilizer Block |
|---|---|---|---|---|---|---|
| Implode Planet | IMPLODE_PLANET | DestroyPlanet | Planet (ref) | No | PLANET_DESTROYED | GeologicStabilizer |
| Stellerate Star | STELLERATE_STAR | (system_destroyer) | None (fleet loc) | **Yes** | STAR_DESTROYED | StellarStabilizer |
| Open Warp Point | OPEN_WARP_POINT | OpenWarpPoint | Dict {target_system_name, target_hex} | No | WARP_POINT_OPENED | WarpFieldStabilizer |
| Close Warp Point | CLOSE_WARP_POINT | CloseWarpPoint | Dict {destination_id, target_hex} | No | WARP_POINT_CLOSED | WarpFieldStabilizer |
| Create Dyson Sphere | CREATE_DYSON_SPHERE | CreateDysonSphere | None (fleet loc) | No | DYSON_SPHERE_CREATED | StellarStabilizer |
| Self-Destruct | SELF_DESTRUCT | (none) | List[ship_ids] | Selective | SHIPS_SELF_DESTRUCTED | None |

Only STELLERATE_STAR consumes the ship; SELF_DESTRUCT is structurally different (no stabilizer block, no ability check, no galaxy mutation) and should stay outside the spec registry.

## 2. Shared tail: `_finalize_superweapon` (lines 61-131)
```
fleet, empire, ship, event_type, event_message, log_message,
consume_ship=True, **event_kwargs -> SuperweaponResult
```
Responsibilities: capture fleet location (FEAT-04), conditionally remove ship, pop order, remove empty fleet from empire (SG-003), log + event_bus emit, return result.

## 3. Common prologue (steps 1-6 are duplicated; step 7 varies)

| Step | Pattern | Differs? | Reference (IMPLODE) |
|---|---|---|---|
| 1. Get current order | `fleet.get_current_order()` | No | 156-158 |
| 2. Validate order type | `order.type != OrderType.*` | No | 157 |
| 3. Resolve target | Planet / system / dict | **Yes** | 160-167 |
| 4. Handle null target | pop_order + return | No | 161-163 |
| 5. Stabilizer check | `_check_blocking_stabilizer(...)` | No (dispatch) | 166-175 |
| 6. Find ship by ability | `SuperweaponValidator.find_ship_with_ability(...)` | **Yes** (ability hardcoded) | 177-187 |
| 7. Execute effect | Galaxy mutation | **Yes** (unique per weapon) | 189-197 |

## 4. Proposed `SuperweaponSpec`
```python
@dataclass(frozen=True)
class SuperweaponSpec:
    order_type: OrderType
    ability_name: str | None              # None for system_destroyer ops
    target_type: str                      # 'planet' | 'dict' | 'none'
    consume_ship: bool
    event_type: EventType
    stabilizer_blocks: tuple[OrderType, ...]   # Mirrors stabilizer_registry pattern
```

## 5. Registry placement & dispatch
**New file:** `game/strategy/services/superweapon_registry.py`
```python
SUPERWEAPONS: tuple[SuperweaponSpec, ...] = (
    SuperweaponSpec(order_type=OrderType.IMPLODE_PLANET, ability_name="DestroyPlanet",
                    target_type="planet", consume_ship=False,
                    event_type=EventType.PLANET_DESTROYED,
                    stabilizer_blocks=(OrderType.IMPLODE_PLANET,)),
    # ...
)
```

**Dispatch refactor in `order_processor.py:704-730`:**
- Replace lambda dict with `find_superweapon_spec(order.type)` lookup.
- New `proc.execute_superweapon(fleet, empire, galaxy, spec, ...)` method runs prologue + dispatches to per-weapon effect handler + calls `_finalize_superweapon`.

## 6. StabilizerRegistry pattern
**Mirror target:** `game/strategy/services/stabilizer_registry.py:36-70`
- Frozen dataclass spec, immutable tuple registry, single lookup function.
- Extensibility: add a tuple entry to extend.

## 7. Risks / exotic behaviors

- **STELLERATE_STAR:** delegates to `system_destroyer.collect_system_contents()` + `destroy_system()` (lines 267-272). Spec only flags suicide+system-scope; effect handler stays separate. **Cannot be generalized** into target_type field, but doesn't need to be.
- **CREATE_DYSON_SPHERE:** lines 597-613 pull race_config preferences for the new planet (gravity/temperature/atmosphere). Contained within effect handler; transparent to spec.
- **CLOSE_WARP_POINT:** lines 464-474 do strict hex validation (sector-level, not system-level). Handled in effect handler; spec just flags `target_type='dict'`.
- **SELF_DESTRUCT:** outlier — no ability, no stabilizer, no galaxy mutation. Keep out of registry; current code at order_processor.py:722-724 already handles separately.

## Conclusion
**Extraction feasibility: ~85%** for the 5 strategic superweapons. SELF_DESTRUCT stays out. STELLERATE_STAR's system_destroyer indirection is already factored — spec just references it. No architectural blockers.
