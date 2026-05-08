# Review Report: PROJ-379 Deterministic Golden-Save Fixture

**Review Type:** code
**Request ID:** req_20260508_031844_3fc504
**Review Mode:** standard
**Scope:** Commits 0837a32e6..a1bcd1b6e on feat/03c-phase-aware-execution
**Completed:** 2026-05-08T03:30:00Z

## Summary

All 9 focus areas pass. Zero CRITICAL or MAJOR findings. One pre-existing unrelated sharded failure noted as INFO.

## Focus Area Results

### 1. Byte-determinism (G1) — PASS

Re-ran `python tests/fixtures/saves/_build_galaxy_fixture.py` twice; md5sums are stable:

| File | MD5 (run 1) | MD5 (run 2) |
|---|---|---|
| galaxy_proj372_baseline.json | f001b3241764e5d05550f361944cd8a4 | f001b3241764e5d05550f361944cd8a4 |
| galaxy_proj372_populated.json | 1d17015f70735054f4046bbba74bede6 | 1d17015f70735054f4046bbba74bede6 |

Subprocess cross-process tests (`test_baseline_byte_deterministic_across_processes`, `test_populated_byte_deterministic_across_processes`) pass with `PYTHONHASHSEED=0`, `PYTHONHASHSEED=12345`, and `PYTHONHASHSEED=random` — byte-equality asserted across all three.

### 2. Field-coverage guard correctness — PASS

`test_golden_fixture_field_coverage.py::test_populated_fixture_exercises_every_planet_field` passes.

- `planet_to_dict(_minimal_planet())` emits 42 keys (verified against `planet_serde.py:29-80`).
- Skiplist exempts 2: `image_id`, `image_rotation` — justified: these are intentionally cosmetic placeholders matching the old `_normalize_image_fields` contract.
- Serialized-baseline pattern correctly handles `default_factory` mutables (`[]`, `{}`) and `PlanetType` enum-name serialization (`PlanetType.BARREN` → `"BARREN"`).
- All 40 non-skiplisted keys have non-default values on the decorated planet (`_build_decorated_planet()` at `_build_galaxy_fixture.py:82-158`).

### 3. Round-trip identity preserved — PASS

All 7 original round-trip tests pass:
- `test_round_trip_empty_galaxy`
- `test_round_trip_single_system_with_planet`
- `test_round_trip_5_system_synthetic_with_warp`
- `test_round_trip_10_systems_with_planets`
- `test_round_trip_20_systems_planets_warp`
- `test_round_trip_golden_baseline_fixture`
- `test_round_trip_golden_populated_fixture`

Both golden fixture tests assert `Galaxy.from_dict(fixture).to_dict() == fixture`.

### 4. Production registration paths — PASS

Verified at `game/strategy/data/galaxy_entity_registry.py:85-89`: `register_planet` assigns ID and indexes but does **NOT** append to `system.planets`. Builder correctly does both steps:

```python
# _build_galaxy_fixture.py:265-266
system.planets.append(planet)
galaxy._registry.register_planet(system, planet)
```

This satisfies Codex's P2 #2 finding (r001) — `register_planet` alone would produce a fixture with zero planets in `to_dict` since `StarSystem.to_dict` at `star_system.py:106` serializes `self.planets`.

### 5. PYTHONHASHSEED-immune build — PASS

Zero `set(` calls found in `_build_galaxy_fixture.py`. All fixture data structures use explicit lists and tuples:
- System lists at lines 179-184, 208-218
- Planet specs at lines 241-258
- Warp link calls at lines 188-191, 222-230
- `json.dumps(sort_keys=True)` is the final emit backstop

### 6. No production-code changes — PASS

`git diff 0837a32e6^..HEAD -- 'game/**'` returns empty. Zero files under `game/` modified.

### 7. PROJ-377 cross-link consistency — PASS

`Projects/active_projects/PROJ-377/decisions.md` row dated 2026-05-08:

> **PROJ-379 closeout: MIN-002 RESOLVED.** PROJ-379 replaced `tests/fixtures/saves/_capture_baseline.py` with a hand-built fixture builder ...

No stale "best-effort deterministic" or "MIN-002 deferred" claims remain. The old docstring caveat is gone with the deleted file.

### 8. Test growth — PASS

Sharded suite: **19084 passed** (19089 total, 1 failed, 4 skipped). Delta from PROJ-378 close baseline (19077) is **+7**, matching the expected:

| Phase | Tests | Description |
|---|---|---|
| Phase 1 | +4 | In-process determinism (2) + committed-fixture-vs-builder-output (2) |
| Phase 1 | +1 | Field-coverage guard |
| Phase 2 | +2 | Cross-process subprocess + PYTHONHASHSEED (2) |

All 14 scope tests pass in 3.14s (pytest with 4 workers).

### 9. Decorated planet completeness — PASS

The decorated planet (`Beta-9 I (decorated)` in `build_populated()`) exercises all 40 planet_to_dict keys (modulo skiplist) with non-default values. Verified by the field-coverage guard passing and by manual inspection of `_build_decorated_planet()` at `_build_galaxy_fixture.py:82-158`.

## Findings

| ID | Severity | Title | Details |
|---|---|---|---|
| FND-001 | INFO | Pre-existing unrelated failure | `test_pathfinder_attached_after_init` (test_save_round_trip_phase4.py:34) fails with `AttributeError: 'Galaxy' object has no attribute '_intercept'`. This is the known PROJ-372 MIN-001 remediation (Galaxy._intercept deleted). Unrelated to PROJ-379 — zero production-code changes in this project. |

## Conclusion

PROJ-379 is complete and correct. The hand-built fixture builder is deterministic by construction, the field-coverage guard catches "forgot to populate the fixture" drift, round-trip identity is preserved, PYTHONHASHSEED immunity is enforced by subprocess tests, and PROJ-377 MIN-002 is properly cross-linked as resolved. All 9 focus areas pass.
