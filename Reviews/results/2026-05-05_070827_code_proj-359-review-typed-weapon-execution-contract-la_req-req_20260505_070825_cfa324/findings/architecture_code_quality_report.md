# Findings: Architecture & Code Quality Review — PROJ-359 Weapon Execution Contract

## CRITICAL
(None found)

## MAJOR

### MAJ-001: Redundant `has_ability('BeamWeaponAbility')` in `_get_pdc_valid_targets` subverts the spirit of string-branch elimination

**File:** `game/simulation/combat/targeting_system.py:222`
**Finding:** The method `_get_pdc_valid_targets()` performs a string-based ability lookup:

```python
beam_ab = comp.get_ability('BeamWeaponAbility') if comp.has_ability('BeamWeaponAbility') else None
```

The agent argues this is "data-fetch not dispatch." The claim is partially valid — the lookup retrieves per-component data (`pdc_valid_targets`) rather than routing behavior. However, the calling context at line 178 already confirms `family is WeaponFamily.PDC`, and the `detect_family` call at line 170 already resolved the family. The `_get_pdc_valid_targets` method re-queries the component for its beam ability when the caller could pass it in directly (the `weapon_ab` parameter already available at the call site). This reintroduces a string-based ability lookup in a method whose entire purpose is tied to a specific family, creating a design smell that contradicts the refactor's goal of single-point family resolution.

**Severity:** MAJOR — not a correctness bug, but undermines the architectural goal of single-point family detection. Future additions of family-specific valid-targets data on other families would require duplicating this pattern.
**Remediation:** Pass the already-retrieved `beam_ab` from the PDC family handler path into `_get_pdc_valid_targets`, or use the `weapon_ab` parameter already available (with fallback logic moved to the call site). Alternatively, store `pdc_valid_targets` on `FAMILY_METADATA[WeaponFamily.PDC]` — but the current design correctly distinguishes per-component configuration from per-family policy. The simpler fix is to avoid the re-lookup.

### MAJ-002: `BeamHandler` and `PDCHandler` `.fire()` implementations are byte-identical with no compile-time sync guarantee

**File:** `game/simulation/combat/families/beam.py:29-46` and `families/pdc.py:37-54`
**Finding:** Both handlers produce identical `BeamResolution` output. The behavioral distinction lives entirely in `FAMILY_METADATA` and the targeting/firing systems that consult it. The docstrings and `attack_contract.py` module doc explicitly document this as intentional. However, the two classes are independent — there is no shared base class, mixin, or factory that guarantees they remain in sync. If `BeamResolution` gains a new field, both handlers must be manually updated.

**Severity:** MAJOR — intentional design choice, defensible, but carries maintenance risk. A developer updating only `BeamHandler` would silently break PDC without compiler or test warning (if PDC tests use a different fixture path).
**Remediation:** Consider extracting a shared `_build_beam_resolution(request, weapon_ab) -> BeamResolution` helper used by both handlers. This is a one-line change per handler and eliminates the duplication while preserving the separate registration. Alternatively, add a test that asserts `BeamHandler().fire(req)` and `PDCHandler().fire(req)` produce identical resolution shapes for the same input.

### MAJ-003: `_find_valid_target` discards militia context when `detect_family` returns `None`

**File:** `game/simulation/combat/weapon_firing_system.py:196-198`
**Finding:**
```python
family = detect_family(comp)
meta = FAMILY_METADATA.get(family) if family else None
if meta is not None and meta.consumes_pdc_missile_context and context:
```

The `detect_family` can return `None` for components that have `WeaponAbility` but none of the four recognized ability classes. In that case, `family` is `None`, `meta` is `None`, and the PDC missile context is silently skipped. This is correct behavior (non-recognized weapons shouldn't get PDC context), but the test suite has no explicit test for this path. If a future component gains `WeaponAbility` without a recognized family ability, it would silently fail to target missiles without diagnostic.

**Severity:** MAJOR — no test coverage for the None-family path through firing/targeting. Production behavior is correct but untested.
**Remediation:** Add a test in `test_weapon_dispatch_golden.py` or `test_weapon_registry.py` for a component that has `WeaponAbility` but no recognized family ability class.

## MINOR

### MIN-001: Seeker arc-check logic lacks edge-case unit tests

**File:** `game/simulation/combat/families/seeker.py:44-50`
**Finding:** The arc-check logic replicates the legacy behavior bit-for-bit, but the test in `test_weapon_dispatch_golden.py::TestSeekerGolden` only asserts constructor kwargs of the resulting projectile. Edge cases like:
- Target exactly at arc boundary (±45 degrees)
- Target behind the ship (outside arc)
- Ship angle wrapping at 360/0 degrees
- `aim_vec.length() == 0` fallback
are not tested in isolation.
**Severity:** MINOR
**Remediation:** Add targeted tests for the arc-check logic with a test-scoped `SeekerHandler` and controlled `AttackRequest` inputs.

### MIN-002: `TestExtensibilityAcceptance` uses existing enum slot, not a new member

**File:** `tests/unit/simulation/combat/test_weapon_registry.py:179-219`
**Finding:** The acceptance test registers a fake handler under `WeaponFamily.PROJECTILE` rather than introducing a new enum member. The test's own docstring notes this limitation: "in a real change the WeaponFamily enum would gain a PLASMA_TORPEDO member." This means the test exercises the handler registration + dispatch chain but NOT the full extensibility story including `detect_family` detection or `FAMILY_METADATA` lookup for a genuinely new family.
**Severity:** MINOR — the test covers the critical contract (dispatch without central edits), but the gap is worth documenting.
**Remediation:** The acceptance test should either (a) use `WeaponRegistry` directly (which it does) and document that enum + detect_family extensions are out of scope for this test, or (b) cover the full end-to-end flow with a temporary enum member. Current approach is acceptable given the test's clear documentation.

### MIN-003: `process_beam_attack` type annotation on `recent_beams` parameter is `List[Dict[str, Any]]`

**File:** `game/engine/collision.py:71`
**Finding:** The `recent_beams` parameter is typed as `List[Dict[str, Any]]` — a legacy dict type. This is a visualization-only side effect (stores start/end/color for rendering) and is not part of the simulation-layer contract. However, it means `process_beam_attack` still constructs and appends a dict, which could be replaced with a typed dataclass (`BeamVisualizationEvent`) to fully eliminate simulation-layer dict shapes from the engine layer.
**Severity:** MINOR — purely visual; no simulation semantics. The dict keys `start`, `end`, `color` are rendering-only.
**Remediation:** Consider a `BeamVisualizationEvent` frozen dataclass in the engine layer (or in a shared rendering-types module below engine). Not blocking.

## NIT

### NIT-001: `AttackRequest` uses `Any` type hints where protocols exist

**File:** `game/simulation/combat/attack_contract.py:75-78`
**Finding:** `source: Any`, `weapon_ability: Any`, `target: Any` use `Any` to avoid runtime import cost. The docstring explains "protocol-compat." While documented, this weakens type checking for callers of `WeaponHandler.fire()`. Consider `TYPE_CHECKING` imports of the appropriate protocols.
**Severity:** NIT — documented, defensible, no production impact.

### NIT-002: `FAMILY_METADATA` dict accessed via `.get()` but no validation that every enum member has an entry

**File:** `game/simulation/combat/attack_contract.py:182-190`
**Finding:** `FAMILY_METADATA` is a module-level dict with entries for all four `WeaponFamily` members. If a new `WeaponFamily` member is added without a corresponding metadata entry, the `.get()` call at `targeting_system.py:171` returns `None`, and the code falls through gracefully. Whether this is intentional (silently use defaults) or a bug (should fail fast) is not documented.
**Severity:** NIT — correct fallback behavior exists, but the silent-default vs fail-fast choice is undocumented.

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 3 |
| MINOR | 3 |
| NIT | 2 |
