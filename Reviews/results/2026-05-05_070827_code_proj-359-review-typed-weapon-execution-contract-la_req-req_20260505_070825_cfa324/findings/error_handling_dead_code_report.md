# Findings: Error Handling & Dead Code Review — PROJ-359 Weapon Execution Contract

## CRITICAL
(None found)

## MAJOR

### MAJ-004: `WeaponRegistry.dispatch` raises `UnregisteredWeaponFamilyError` — golden tests do not cover this exception path

**File:** `game/simulation/combat/weapon_registry.py:58-70` and `tests/unit/simulation/combat/test_weapon_registry.py`
**Finding:** `WEAPON_REGISTRY.dispatch(request)` raises `UnregisteredWeaponFamilyError` when no handler is registered for the request's family. The firing system calls this via `_create_attack` (weapon_firing_system.py:240). In production, all four families are registered by the `families` package import, so this path is unreachable in normal operation. However, there is no golden test that verifies the firing system's behavior when `dispatch` raises.
**Severity:** MAJOR — the exception class exists and is documented ("a missing handler is a programming error, not a runtime condition"), but the firing system's `_create_attack` has no try/except and no test for this case. If a production code path deregisters a handler (via `unregister`), the exception would propagate uncaught through the tick loop.
**Remediation:** Add a test that verifies the firing system raises `UnregisteredWeaponFamilyError` when the registry is empty, OR confirm that `_create_attack` should let the exception propagate (design choice: fail-fast for programming errors). If the latter, document in the method docstring.

## MINOR

### MIN-004: `_process_hangar_launch` returns dict — pre-existing out-of-scope pattern, no error handling

**File:** `game/simulation/combat/weapon_firing_system.py:94-120`
**Finding:** The LAUNCH dict path is confirmed as intentionally out-of-scope per the instructions. The method returns `Optional[Dict]` and attaches no error handling. This is consistent with the pre-refactor state and is not a regression. The `_process_attacks` discriminator in `battle_engine.py:589-597` handles the LAUNCH dict separately via `isinstance(attack, dict)` + `attack.get('type')`.
**Severity:** MINOR — confirmed intentional, not a regression, but the LAUNCH dict remains the last dict-shaped attack carrier in the engine. Worth a follow-up PROJ to type it.
**Remediation:** Create a follow-up project to replace the LAUNCH dict with a `LaunchResolution` dataclass, similar to how `BeamResolution` replaced the beam dict.

### MIN-005: `process_beam_attack` indirectly accesses `beam_ab.get_damage` — no null check on ability retrieval

**File:** `game/engine/collision.py:116-140`
**Finding:**
```python
beam_ab = beam_comp.get_ability('BeamWeaponAbility')
# ...
chance = beam_ab.calculate_hit_chance(...)
# ...
damage = beam_ab.get_damage(hit_dist)
```
If `beam_comp.get_ability('BeamWeaponAbility')` returns `None` (e.g., misconfigured component), this would raise `AttributeError`. In production, `detect_family` ensures only beam-capable components reach this path, but the engine layer has no such guard.

**Severity:** MINOR — unreachable in the current production path (the firing system already validated the component), but the engine should be defensive. Pre-existing pattern from pre-refactor, not introduced by PROJ-359.
**Remediation:** Add a guard: `if beam_ab is None: return` before line 133. This is a one-line defensive fix.

## NIT

(None additional)

## Dead Code / Cleanup Verification

### DC-001: `process_beam_attack.*` files removed — CONFIRMED
**Finding:** The scope mentions `game/simulation/combat/process_beam_attack.*` but no such files exist on disk. The legacy beam-attack dict consumer was deleted in Phase 4 as documented. Confirmed clean.

### DC-002: Legacy `comp.has_ability('BeamWeaponAbility')` in dispatch path — CONFIRMED REMOVED
**Finding:** The firing system's `_create_attack` method (weapon_firing_system.py:212-246) and `_find_valid_target` (lines 165-210) now use `detect_family` + `FAMILY_METADATA` instead of string branches. The only remaining `has_ability` calls in these files are:
- `comp.has_ability('VehicleLaunch')` — hangar launch, out of scope
- `comp.has_ability('WeaponAbility')` — generic weapon gate
These are correct and intentional.

### DC-003: `battle_engine.py` has zero `has_ability` calls — CONFIRMED
**Finding:** The battle engine's `_process_attacks` discriminator uses `.type` attribute access for typed resolutions and `.get('type')` only for the remaining LAUNCH dict. No string-based ability lookups. Clean.

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 1 |
| MINOR | 2 |
| NIT | 0 |
