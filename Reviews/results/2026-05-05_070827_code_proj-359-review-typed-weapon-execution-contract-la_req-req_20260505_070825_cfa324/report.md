# Review Report: PROJ-359 Typed Weapon Execution Contract (large refactor)

**Review Type:** code
**Request ID:** req_20260505_070825_cfa324
**Review Mode:** normal
**Scope:** `game/simulation/combat/attack_contract.py`, `game/simulation/combat/weapon_registry.py`, weapon family handlers (`families/{beam,projectile,seeker,pdc}.py`), `weapon_firing_system.py`, `targeting_system.py`, `game/engine/collision.py`, golden tests, `docs/02_PATTERNS.md` § 34, `docs/systems/combat_simulation.md`
**Commits reviewed:** 157264456, a8a2fc10b, b112742e0, 93a2fa8b0, fe5d4a724, a1c1c158b, bd8b48d51
**Parent Request:** none (initial review)

---

## Instruction-by-Instruction Summary

### 1. `has_ability('BeamWeaponAbility')` / `'SeekerWeaponAbility'` string branches in firing/targeting → LARGELY RESOLVED

- **weapon_firing_system.py:** ZERO weapon-family `has_ability` string branches. The two remaining `has_ability` calls are `'VehicleLaunch'` (hangar, out-of-scope) and `'WeaponAbility'` (generic weapon gate, not family-specific). `_create_attack` dispatches via `detect_family` + `WEAPON_REGISTRY.dispatch`. Clean.
- **targeting_system.py:** ONE remaining `comp.has_ability('BeamWeaponAbility')` at line 222 inside `_get_pdc_valid_targets`. This is data-fetch (retrieving `pdc_valid_targets` from the ability instance), not dispatch. However, the call is redundant — the caller already confirmed `family is WeaponFamily.PDC` and could pass the beam ability directly. See MAJ-001.
- **weapon_registry.py:** Contains `has_ability` calls in `detect_family` (lines 89-94) — this is the intentional single-point owning the legacy string lookup, per the contract design.
- **battle_engine.py:** ZERO `has_ability` calls. Clean.
- **collision.py:** ZERO `has_ability` for dispatch. The `get_ability('BeamWeaponAbility')` at line 116 is functional access (needs ability for damage calculation), not dispatch.

### 2. Beam and Projectile damage event/telemetry shapes converged — CONFIRMED

- Beam: `DamageContext(attacker=source_ship, source_weapon=beam_comp, damage_type="beam")` — collision.py:144-147
- Projectile: `DamageContext(attacker=p.owner, source_weapon=p.source_weapon, damage_type="projectile")` — projectile_manager.py:148-153
- Both use identical `DamageContext` structure with `attacker`, `source_weapon`, `damage_type` fields.
- Golden tests (`test_beam_collision_telemetry_chain`, `test_projectile_hit_application_telemetry`) pin both shapes.

### 3. `game/engine/collision.py` dict-carrier audit — CLEAN

- `process_beam_attack` now takes `BeamResolution` (typed dataclass), not a dict.
- All attribute access is via typed dot-access: `attack.origin`, `attack.direction`, `attack.range`, etc.
- The `recent_beams` list for visualization is still a dict (`{'start', 'end', 'color'}`), but this is pure rendering side-effect, not simulation-layer semantics.
- The legacy `process_beam_attack.*` files referenced in the scope do not exist on disk — confirmed deleted in Phase 4.

### 4. BeamHandler/PDCHandler near-duplicates — INTENTIONAL AND CORRECTLY DISTINGUISHED

- Both `.fire()` methods produce identical `BeamResolution` output. This is by design (both are beam-shaped weapons).
- `FAMILY_METADATA` correctly distinguishes them:
  - BEAM: all defaults (no missile targeting)
  - PDC: `targets_missiles=True`, `consumes_pdc_missile_context=True`
- The distinction is consumed in `targeting_system.py` (`targets_missiles` at line 172) and `weapon_firing_system.py` (`consumes_pdc_missile_context` at line 198).
- See MAJ-002 for maintenance risk.

### 5. `_get_pdc_valid_targets` and `comp.has_ability('BeamWeaponAbility')` — DATA-FETCH, BUT REDUNDANT

- The call at targeting_system.py:222 is data-fetch, not dispatch. The function retrieves `pdc_valid_targets` from the component's `BeamWeaponAbility` instance.
- However, the caller (line 178) already confirmed `family is WeaponFamily.PDC`, making the re-lookup redundant. The `weapon_ab` parameter already available at the call site could be used instead.
- See MAJ-001 for details.

### 6. Extensibility — CONFIRMED, WITH CAVEATS

- Adding a hypothetical 5th family requires:
  1. New `WeaponFamily` enum member
  2. New handler module under `families/<name>.py`
  3. Import in `families/__init__.py`
  4. `FAMILY_METADATA` entry (if special targeting behavior)
- **No edits to weapon_firing_system, targeting_system, collision, or projectile_manager.**
- `TestExtensibilityAcceptance` confirms the dispatch chain. Caveat: the test uses an existing enum slot rather than exercising new enum member + `detect_family` extension. See MIN-002 and MIN-008.
- `WeaponRegistry` has clean extension API: `register`, `unregister`, `reset`, `has`, `dispatch`.

### 7. LAUNCH dict path — OUT-OF-SCOPE, NOT A REGRESSION

- `_process_hangar_launch` at weapon_firing_system.py:94-120 still returns `{'type': AttackType.LAUNCH, ...}` dict.
- The `_process_attacks` discriminator at battle_engine.py:589 handles it via `isinstance(attack, dict)` guard.
- Confirmed intentional. The LAUNCH path is a hangar/fighter-launch path, not a weapon family. Not a regression.

### 8. Seeker arc-check logic — CORRECTLY REPLICATED, UNTESTED EDGE CASES

- The arc-check at families/seeker.py:44-50 uses the standard firing-arc pattern:
  - Compute relative position → target angle
  - Compute difference with modulo-360 wrap
  - Compare to `firing_arc / 2`
  - Fall back to `launch_vec` if target outside arc
- Golden test `test_seeker_attack_creates_missile_with_pinned_fields` confirms the happy path but doesn't exercise out-of-arc, boundary, or angle-wrapping edge cases. See MIN-006.

---

## Findings

### CRITICAL (0)

No broken paths, no correctness regressions.

### MAJOR (3)

#### MAJ-001: Redundant `has_ability('BeamWeaponAbility')` lookup in `_get_pdc_valid_targets`
**File:** `game/simulation/combat/targeting_system.py:222`
**Severity:** MAJ
The method `_get_pdc_valid_targets()` performs a string-based ability lookup when the calling context already knows the family is PDC. The `weapon_ab` parameter is already available and could be passed through instead of re-querying the component. This subverts the spirit of single-point family resolution — not a correctness bug, but a design smell.
**Remediation:** Pass the already-retrieved beam ability from the call site (line 178 area) into `_get_pdc_valid_targets`, or use the existing `weapon_ab` parameter.

#### MAJ-002: BeamHandler and PDCHandler byte-identical `.fire()` with no sync guarantee
**File:** `game/simulation/combat/families/beam.py:29-46` and `families/pdc.py:37-54`
**Severity:** MAJ
Both handlers produce identical `BeamResolution` output with no shared base. If `BeamResolution` gains a field, both must be manually updated. No test verifies they produce identical output for the same input.
**Remediation:** Extract a shared helper `_build_beam_resolution(request, weapon_ab)` used by both handlers, or add a test that asserts output identity.

#### MAJ-003: `detect_family` returning `None` has untested path through firing/targeting
**File:** `game/simulation/combat/weapon_firing_system.py:196-198` and `targeting_system.py:170-171`
**Severity:** MAJ
When `detect_family` returns `None` (component has `WeaponAbility` but no recognized family ability), the firing/targeting systems gracefully handle it (skip PDC context injection, skip targeting restrictions). This is correct behavior but has no golden test.
**Remediation:** Add a golden test for an unrecognized weapon component through the full `fire_weapons` pipeline.

### MINOR (5)

#### MIN-001: Seeker arc-check lacks edge-case tests
**File:** `game/simulation/combat/families/seeker.py:44-50`
**Severity:** MIN

#### MIN-002: TestExtensibilityAcceptance uses existing enum slot
**File:** `tests/unit/simulation/combat/test_weapon_registry.py:179-219`
**Severity:** MIN

#### MIN-003: `process_beam_attack` visualization still uses dict
**File:** `game/engine/collision.py:71, 155-159`
**Severity:** MIN

#### MIN-004: LAUNCH dict path — out-of-scope, worth a follow-up
**File:** `game/simulation/combat/weapon_firing_system.py:94-120`
**Severity:** MIN

#### MIN-005: `process_beam_attack` no null-guard on `get_ability('BeamWeaponAbility')`
**File:** `game/engine/collision.py:116`
**Severity:** MIN

### NIT (2)

#### NIT-001: `AttackRequest` uses `Any` type hints
**File:** `game/simulation/combat/attack_contract.py:75-78`
**Severity:** NIT

#### NIT-002: `FAMILY_METADATA` silent-default vs fail-fast unwritten
**File:** `game/simulation/combat/attack_contract.py:182-190`
**Severity:** NIT

---

## Verified Positive Findings

| # | Item | Status |
|---|------|--------|
| VF-001 | Golden tests pass for all four families | Confirmed |
| VF-002 | Damage event shapes converged (beam + projectile) | Confirmed |
| VF-003 | No regression in targeting restrictions | Confirmed |
| VF-004 | LAUNCH dict path intact (out-of-scope) | Confirmed |
| VF-005 | `process_beam_attack.*` files deleted | Confirmed |
| VF-006 | Zero `has_ability` in battle_engine.py | Confirmed |
| VF-007 | `_create_attack` is thin family-dispatcher (no string branches) | Confirmed |
| VF-008 | `_find_valid_target` uses FAMILY_METADATA for missile injection | Confirmed |
| VF-009 | Targeting restrictions use FAMILY_METADATA.targets_missiles | Confirmed |
| VF-010 | Seeker arc-check is faithful bit-for-bit replica | Confirmed (edge cases untested) |

---

## Extensibility Assessment

**Question:** Can a hypothetical 5th weapon family be added with one registration call + one family module?

**Answer:** YES, with caveats. The extension points are:

1. **New `WeaponFamily` enum member** — required (1 line)
2. **New handler module** (`families/<name>.py`) — required (~30-50 lines)
3. **Import in `families/__init__.py`** — required (1 line)
4. **`FAMILY_METADATA` entry** — optional, only if special targeting behavior
5. **`detect_family` update** — REQUIRED if the family uses a new ability class name (~3 lines)

Items 1-4 are the design's promised extension surface. Item 5 is an additional requirement not covered by the acceptance test: if the new family uses a new ability class (e.g., `PlasmaWeaponAbility`), `detect_family` must be extended. However, this is a single-point edit in `weapon_registry.py`, not a scatter across four files. The four central files (firing, targeting, collision, projectile_manager) remain unmodified.

---

## Overall Assessment

The PROJ-359 refactor achieves its goals: string-based dispatch is eliminated from firing and targeting, the engine layer no longer leaks simulation semantics through dict carriers, damage event shapes have converged, and the extensibility contract holds. The remaining issues are design cleanliness (MAJ-001, MAJ-002), test coverage gaps (MAJ-003, MIN-001), and minor cleanup items. No correctness regressions were found.
