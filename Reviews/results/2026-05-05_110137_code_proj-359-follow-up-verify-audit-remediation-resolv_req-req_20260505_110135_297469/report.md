# Review Report: PROJ-359 Follow-up — Audit Remediation Verification

**Review Type:** code (follow-up)
**Review Mode:** normal
**Request ID:** req_20260505_110135_297469
**Parent Request:** req_20260505_070825_cfa324
**Scope:** `game/simulation/combat/targeting_system.py`, `game/simulation/combat/families/beam.py`, `pdc.py`, new `_beam_common.py`, `tests/unit/simulation/combat/test_weapon_dispatch_golden.py`, `Projects/active_projects/PROJ-359/decisions.md`
**Remediation Commit:** `6d21765f6` ("fix(PROJ-359): audit remediation")
**Checked Out SHA:** `6d21765f6`

---

## Verification Matrix

| Parent Finding | Status | Evidence |
|---|---|---|
| MAJ-001: Redundant `has_ability('BeamWeaponAbility')` in `_get_pdc_valid_targets` | **resolved** | `targeting_system.py:188-189`: PDC branch resolves `BeamWeaponAbility` once via `comp.get_ability(...)` (not `has_ability`) and passes the result to `_get_pdc_valid_targets(beam_ab, weapon_ab)`. The helper (lines 209-239) no longer performs its own ability lookup — it only consults the supplied `beam_ab`, then `weapon_ab`, then a default. Zero redundant lookups. |
| MAJ-002: `BeamHandler`/`PDCHandler` byte-identical `.fire()` bodies with no shared base | **resolved** | `families/_beam_common.py` extracted `build_beam_resolution(request)`. `beam.py:29` and `pdc.py:42` both delegate to it. Adding a `BeamResolution` field is a one-place edit. |
| MAJ-003: `detect_family → None` path had no golden test | **resolved** | `test_weapon_dispatch_golden.py:539-579`: `TestTargetingGolden::test_unrecognized_weapon_family_no_attack_emitted` pins the silent-no-op contract. Component with `WeaponAbility` but no family ability, `is_pdc=False` → `fire_weapons` returns `[]`; no raise. |

---

## Regression Check

### `targeting_system.py`
No regressions. The family-metadata-driven targeting filter (lines 165-206) is structurally identical to the post-Phase-4 layout; the only change is the MAJ-001 fix at lines 182-189 where `beam_ab` is resolved once and passed into `_get_pdc_valid_targets`. All other targeting logic (lead calculation, family branching, range gating) is unchanged.

### `families/beam.py` + `families/pdc.py`
Both handlers now delegate their `.fire()` to `_beam_common.build_beam_resolution()`. The registration calls at the bottom of each module are unchanged. No regression — the `BeamResolution` field set produced is identical to the pre-fix version.

### `families/_beam_common.py` (new)
Single-responsibility helper constructing `BeamResolution`. Used by both `BeamHandler` and `PDCHandler`. Clean, 44 lines, follows existing conventions.

### `test_weapon_dispatch_golden.py`
One new test added: `test_unrecognized_weapon_family_no_attack_emitted` (lines 539-579). No existing test was modified. The golden tests for beam/projectile/seeker/PDC families remain unchanged and continue to pin the dispatch shapes.

### `decisions.md`
Audit remediation table (lines 29-40) documents the resolution of all three MAJ findings. References are accurate. Deferred MIN/NIT items are clearly labeled as follow-ups.

---

## Findings

### CRITICAL (0)
No regressions, no correctness issues.

### MAJOR (0)
All three parent MAJ findings are resolved.

### MINOR (0)
No new issues identified.

### NIT (0)
No new issues identified.

---

## Overall Assessment

All three parent MAJ findings are **resolved** with clean, minimal changes:

- **MAJ-001** (`targeting_system.py`): Signature change on `_get_pdc_valid_targets` to accept already-resolved `beam_ab` — eliminates the redundant `has_ability` lookup.
- **MAJ-002** (`families/_beam_common.py`): Shared `build_beam_resolution` helper — guarantees `BeamHandler` and `PDCHandler` stay in sync.
- **MAJ-003** (`test_weapon_dispatch_golden.py`): New golden test for the `detect_family → None` path — pins the silent-no-op contract.

No regressions introduced by the remediation. The remediation diff is focused and surgically targets only the three findings; no unrelated changes were observed.
