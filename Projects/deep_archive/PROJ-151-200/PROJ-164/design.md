# PROJ-164: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### The Duplication
The `Ability` base class (`game/simulation/components/abilities/base.py`) provides `__init__` infrastructure for scope parsing and tag extraction, but does NOT provide a helper for the most common subclass operation: parsing a primary numeric value from the `data` parameter.

Every ability that accepts a single numeric value implements the same 1-2 line pattern:
```python
val = data if isinstance(data, (int, float)) else data.get('value', 0)
self.field = float(val)  # or int(val) for integer abilities
```

This pattern exists because ability data can arrive in two formats:
1. **Primitive shortcut:** `"ShieldProjection": 500` → `data = 500`
2. **Dict format:** `"ShieldProjection": {"value": 500, "scope": "self"}` → `data = {"value": 500, ...}`

### Affected Classes (11 sites for migration)
- **defense.py:** ShieldProjection, ShieldRegeneration, ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor (5)
- **propulsion.py:** CombatPropulsion, ManeuveringThruster, StrategicMovement (3 `__init__` + 3 `sync_data`)
- **crew.py:** CrewCapacity, LifeSupportCapacity (2, plus CrewRequired left as-is)

### NOT Affected (intentionally excluded)
- **weapons.py:** WeaponAbility parses multiple named fields (damage, range, reload) with formula support — fundamentally different pattern
- **resources.py:** ResourceConsumption/Storage/Generation use `data.get('amount')` with resource_type — dict-only pattern
- **harvester.py:** Similar dict-only pattern
- **markers.py/superweapons.py:** Pure markers with no `__init__` override
- **colonize.py:** String shorthand pattern

## Helper Design

### Signature
```python
@staticmethod
def _parse_primary_value(data, key: str = 'value', default: float = 0.0) -> float:
```

### Why Static Method
- No access to `self` or `cls` needed — pure data transformation
- Callable from both `__init__` (where self exists) and as `Ability._parse_primary_value()` in tests
- Consistent with `_parse_scope()` being an instance method only because it needs `self.allowed_scopes`

### Why Return Float (Not Union[int, float])
- Most callers want float
- The 3 integer abilities (CrewCapacity, LifeSupportCapacity, EmissiveArmor) already do `int(float_val)` — they can wrap: `int(self._parse_primary_value(data))`
- Simpler contract: always returns float

### Why `key` Parameter
- Default `'value'` covers 100% of current callers
- Future-proofs for abilities that might use `'amount'` or other keys
- Makes the helper useful beyond just the standard pattern

### Edge Cases
| Input | Behavior | Rationale |
|-------|----------|-----------|
| `42` (int) | → `42.0` | Primitive shortcut format |
| `3.14` (float) | → `3.14` | Primitive shortcut format |
| `True` (bool) | → `1.0` | `bool` is subclass of `int` in Python — matches existing `isinstance(data, (int, float))` behavior |
| `{'value': 100}` | → `100.0` | Dict format |
| `{'other': 5}` | → `0.0` | Key missing → default |
| `{}` | → `0.0` | Empty dict → default |
| `None` | → `0.0` | Not numeric, not dict → default |
| `"hello"` | → `0.0` | Not numeric, not dict → default |

## Dependencies & Risks

1. **Risk: Bool handling** — `isinstance(True, (int, float))` returns True in Python. This matches existing behavior exactly (no change). Documented in tests.
2. **Risk: Existing tests** — This is a pure refactor. Every call site produces identical output for identical input. No behavior change expected.
3. **Dependency: base.py imports** — No new imports needed. The helper uses only built-in types.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
