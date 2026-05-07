# Findings: Test Coverage & Golden Test Review — PROJ-359 Weapon Execution Contract

## CRITICAL
(None found)

## MAJOR

(None found — golden tests cover the core dispatch paths for all four families)

## MINOR

### MIN-006: No isolated unit tests for SeekerHandler arc-check edge cases

**File:** `game/simulation/combat/families/seeker.py:44-50` and `tests/unit/simulation/combat/test_weapon_dispatch_golden.py:307-368`
**Finding:** The golden test `test_seeker_attack_creates_missile_with_pinned_fields` patches `Projectile` to verify constructor kwargs, but the arc-check logic runs before projectile construction and is not directly exercised. The test fires at a target at (100, 0) from (0, 0) with facing_angle=0 and firing_arc=90 — the target IS in arc, so the test only exercises the in-arc path. No test covers:
- Target outside firing arc (launch_vec stays as facing direction)
- Target at exact arc boundary
- Angle wrapping at 360°/0°
- `aim_vec.length() == 0` normalization fallback
**Severity:** MINOR
**Remediation:** Add tests in `tests/unit/simulation/combat/test_weapon_registry.py` or a new `tests/unit/simulation/combat/families/test_seeker_handler.py` for the arc-check edge cases.

### MIN-007: `detect_family` returning `None` has no golden test through the firing pipeline

**File:** `game/simulation/combat/weapon_registry.py:78-95` and `test_weapon_dispatch_golden.py`
**Finding:** `detect_family` returns `None` when a component has `WeaponAbility` but none of the recognized family ability classes. `test_unknown_returns_none` in `test_weapon_registry.py` tests this at the unit level, but no golden test exercises the full `fire_weapons` → `_process_weapon_fire` → `_create_attack` path when `detect_family` returns `None`. In that case, `_create_attack` returns `[]` (empty list), which is correct but untested.
**Severity:** MINOR
**Remediation:** Add a golden test case for an unrecognized weapon component (has `WeaponAbility` but no Beam/Projectile/Seeker ability) to confirm the firing system produces no attacks.

### MIN-008: `TestExtensibilityAcceptance` only tests registry dispatch, not full fire_weapons pipeline

**File:** `tests/unit/simulation/combat/test_weapon_registry.py:168-219`
**Finding:** The acceptance test verifies that a fake handler dispatches via `WeaponRegistry` without editing central files. It does not verify that the fake handler works end-to-end through `WeaponFiringSystem.fire_weapons()`. Adding a real new family requires `detect_family` recognition + `FAMILY_METADATA` entry + handler registration. The acceptance test covers only step 3 (handler registration).
**Severity:** MINOR
**Remediation:** Add an integration-style test that (a) registers a fake family handler under a REAL enum slot, (b) constructs a component that `detect_family` would route to that family, and (c) verifies that `WeaponFiringSystem.fire_weapons()` produces the expected resolution. The `TestFakeFamilyExtensibility::test_fake_handler_dispatches_via_local_registry` partially covers this but doesn't exercise the firing system.

## Verified Positive Findings

### VF-001: Golden tests pass for all four families — CONFIRMED
The golden test suite (`test_weapon_dispatch_golden.py`) covers:
- **Beam:** `test_beam_attack_has_exact_resolution_shape` — verifies `BeamResolution` attributes match legacy dict shape
- **Beam:** `test_beam_collision_telemetry_chain` — verifies `damage_type='beam'` + `DamageContext` structure
- **Projectile:** `test_projectile_attack_creates_projectile_with_pinned_fields` — verifies `Projectile` constructor kwargs
- **Projectile:** `test_projectile_hit_application_telemetry` — verifies `damage_type='projectile'` + `DamageContext` structure
- **Seeker:** `test_seeker_attack_creates_missile_with_pinned_fields` — verifies `Projectile` constructor kwargs for missiles
- **PDC:** `test_pdc_targets_enemy_missile_from_context` — verifies PDC-vs-missile produces `BeamResolution`
- **PDC:** `test_pdc_collision_against_missile_uses_take_damage` — verifies missile `take_damage` path
- **Targeting:** `test_non_pdc_cannot_target_missiles` — verifies non-PDC weapons reject missiles
- **Targeting:** `test_pdc_targets_only_missile_or_fighter_types` — verifies PDC type restriction
- **Targeting:** `test_seeker_uses_endurance_range_gate` — verifies seeker range gating

### VF-002: Damage event shapes converged — CONFIRMED
- Beam damage: `DamageContext(attacker=source_ship, source_weapon=beam_comp, damage_type="beam")` — `collision.py:144-147`
- Projectile damage: `DamageContext(attacker=p.owner, source_weapon=p.source_weapon, damage_type="projectile")` — `projectile_manager.py:148-153`
Both use the same `DamageContext` structure with consistent `attacker`, `source_weapon`, `damage_type` fields. The beam path was previously dict-based; the projectile path was already using `DamageContext`. Post-PROJ-359, both converge on the same event shape.

### VF-003: No regression in targeting restrictions — CONFIRMED
- Non-PDC weapons cannot target missiles (`test_non_pdc_cannot_target_missiles` passes)
- PDC weapons only target types in `pdc_valid_targets` (`test_pdc_targets_only_missile_or_fighter_types` passes)
- These are driven by `FAMILY_METADATA.targets_missiles` rather than `comp.has_pdc_ability()` string branches

### VF-004: LAUNCH dict path intact — CONFIRMED
`_process_hangar_launch` at `weapon_firing_system.py:94-120` still returns a dict with `type: AttackType.LAUNCH`. The `_process_attacks` discriminator at `battle_engine.py:589` handles it via `isinstance(attack, dict)` + `attack.get('type')`. This is intentionally out-of-scope and is not a regression.

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 3 |
| NIT | 0 |
