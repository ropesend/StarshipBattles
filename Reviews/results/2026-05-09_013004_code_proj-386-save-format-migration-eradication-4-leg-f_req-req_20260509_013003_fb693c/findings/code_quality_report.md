# Legacy Eradication Verification — Code Quality Findings

## CRITICAL: None

All 4 legacy code paths confirmed fully deleted with zero remaining production references.

## MAJOR: None

## MINOR

### MIN-LQ-001: Stale backward-compat docstrings in `planetary_facility.py`
**File:** `game/strategy/data/planetary_facility.py:81,110`
**Severity:** MINOR

Two docstrings claim backward compatibility with the old `{'active': bool}` format:
- Line 81: `is_component_active` says "`{'active': bool}` format for backward compatibility."
- Line 110: `get_activation_state` says "Handles backward compatibility with old `{'active': bool}` format."

Both methods delegate to `ComponentActivationState.from_dict()` which now requires the `phase` key and raises `KeyError` on old-format data. The docstrings are misleading about the actual behavior post-PROJ-386.

**Recommended fix:** Update both docstrings to remove backward-compat claims.

### MIN-LQ-002: `from_dict` exception contract inconsistency
**File:** `game/strategy/data/ship_instance_serializer.py:82-83,126`
**Severity:** MINOR

The docstring for `ShipInstanceSerializer.from_dict` states it raises `PersistenceException` for missing required keys. However, `require_keys` (line 87) only validates `['instance_id', 'design_id', 'name', 'owner_id']` — it does NOT include `'components'`. Line 126 uses `data['components']` (bare dict access) which raises `KeyError`, not `PersistenceException`, if the key is missing.

Either add `'components'` to the `require_keys` call or document that `KeyError` may be raised for this specific missing key.

## INFO

### INFO-LQ-001: `to_dict` always-emit change is correctly justified
The change from `if ship.components:` (conditional emit) to always emitting `data['components']` is required for round-trip symmetry because `from_dict` now uses `data['components']` (direct access, no `.get()` fallback). Without always-emit, a ship with zero components would serialize without the key and fail on deserialization. No caller depends on omit-when-empty behavior — the 14 fixture rewrites confirm all consumers now expect the key.

### INFO-LQ-002: `set_component_active` legacy-flagged but safe
`planetary_facility.py:92-104` marks `set_component_active` as a "legacy interface" but it constructs `ComponentActivationState(phase=...)` directly (bypassing `from_dict`), so it is unaffected by the removed legacy deserialization path.
