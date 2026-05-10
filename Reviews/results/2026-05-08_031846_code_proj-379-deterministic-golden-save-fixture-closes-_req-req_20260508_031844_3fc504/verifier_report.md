# Verifier Report: PROJ-379 Deterministic Golden-Save Fixture

**Verifier:** Claude (independent of OpenCode)
**Verified:** 2026-05-08
**Subject report:** `report.md` (OpenCode review of commits 0837a32e6, bfe4c680c, a84713f75, a1bcd1b6e on `feat/03c-phase-aware-execution`)
**OpenCode verdict:** 0 CRIT, 0 MAJ, 0 MIN, 1 INFO (pre-existing unrelated). All 9 focus areas pass.

## Verdict Table

| Area | OpenCode Claim | Verifier Verdict |
|---|---|---|
| 1. Byte-determinism (G1) — same-process md5 stability | PASS | CONFIRM |
| 2. Subprocess test correctness (PYTHONHASHSEED + bytes compare) | PASS | CONFIRM |
| 3. Field-coverage guard correctness (incl. mutation test) | PASS | CONFIRM |
| 4. Production registration pattern (`append` + `register_planet`) | PASS | CONFIRM |
| 5. No production-code changes under `game/**` | PASS | CONFIRM |
| 6. PROJ-377 cross-link consistency | PASS | CONFIRM (with minor doc-hygiene observation, see INFO-V1) |
| 7. Sharded-suite test growth (+7 from 19077 → 19084) | PASS | CONFIRM |
| 8. No `set` iteration in builder | PASS | CONFIRM |
| 9. Pre-existing unrelated failure (`test_pathfinder_attached_after_init`) | INFO | CONFIRM |

**Aggregate:** 0 CRIT, 0 MAJ, 0 MIN, 1 INFO (verifier adds INFO-V1, which is doc-hygiene, not an OpenCode miss).

## Per-Finding Details

### Area 1 — Byte-determinism (G1): CONFIRM

Ran `python tests/fixtures/saves/_build_galaxy_fixture.py` twice; md5sums stable:

```
f001b3241764e5d05550f361944cd8a4 *galaxy_proj372_baseline.json
1d17015f70735054f4046bbba74bede6 *galaxy_proj372_populated.json
```

Both runs produced identical hashes. Matches OpenCode's reported md5s exactly.

### Area 2 — Subprocess test correctness: CONFIRM

Read `tests/integration/strategy/test_save_round_trip.py:162-208`. The helper:
- Sets `env["PYTHONHASHSEED"] = hash_seed` on a fresh `os.environ.copy()` — confirmed.
- Spawns `sys.executable -c "..."` via `subprocess.run(... env=env, check=True)` — confirmed.
- Returns `result.stdout` (raw string), not a re-parsed-and-re-dumped JSON. The two assertions `assert a == b; assert b == c` compare raw bytes, not normalized representations. A set-iteration regression that produces the same JSON tree but different key insertion order would still emit identical `json.dumps(..., sort_keys=True)` output — but the test's intent (catch order-dependent serialization in the builder) is preserved because the builder uses no intermediate dicts whose insertion order matters before `sort_keys=True`. The check is correct as designed.

### Area 3 — Field-coverage guard correctness: CONFIRM (with mutation test)

Read `test_golden_fixture_field_coverage.py`. The guard derives the emitted-keys set and per-key default values from `planet_to_dict(_minimal_planet())` — the serialized-baseline pattern matches design intent.

**Mutation test (the load-bearing check):**
1. Commented out `planet.owner_id = 1` in `_build_decorated_planet`.
2. Re-ran the builder.
3. Re-ran the guard. **Result:** FAILED with the expected message:
   `"... no planet ... has a non-default value for them: ['owner_id']. Update tests/fixtures/saves/_build_galaxy_fixture.py::build_populated() ..."`
4. Restored the line, re-ran the builder, re-ran 14 PROJ-379 scope tests. **Result:** all 14 pass; md5s match originals (`f001b324...` and `1d17015f...`). No drift.

The guard catches the exact drift class it was built for.

### Area 4 — Production registration pattern: CONFIRM

`game/strategy/data/galaxy_entity_registry.py:85-89`:

```python
def register_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
    """Register a planet, assign next ID, and update indexes."""
    planet.id = self._state.next_planet_id
    self._state.next_planet_id += 1
    self._index_planet(system, planet)
```

`_index_planet` updates `planets_by_id`, `planet_to_system`, and `global_hex_planets`, plus an optional zone register — but does **not** append to `system.planets`. Confirmed.

The builder at `_build_galaxy_fixture.py:259-271` correctly does both:
```python
system.planets.append(planet)
galaxy._registry.register_planet(system, planet)
```
…for both the 16 plain planets and the decorated planet. Without the explicit append, `StarSystem.to_dict` serializes `self.planets` as `[]` and the round-trip would observe zero planets.

### Area 5 — No production-code changes: CONFIRM

`git diff 0837a32e6^..HEAD -- 'game/**'` returns empty. All changes confined to `tests/`, `Projects/active_projects/PROJ-379/`, and `Projects/active_projects/PROJ-377/decisions.md`.

### Area 6 — PROJ-377 cross-link consistency: CONFIRM (with INFO-V1)

`Projects/active_projects/PROJ-377/decisions.md:33` carries the new 2026-05-08 row:

> **PROJ-379 closeout: MIN-002 RESOLVED.** … The "best-effort deterministic" docstring caveat is gone with the file.

This explicitly supersedes the prior 2026-05-07 row that deferred MIN-002 (the "capture-script double-seed fragility" review finding — distinct from PROJ-372's MIN-002 about pathfinding shims).

**INFO-V1 (doc hygiene, not blocking):** the historical 2026-05-07 row at decisions.md:35 still uses the phrase "Capture script idempotence relaxed to best-effort." That row describes a behavior that no longer exists (the file is deleted). It's preserved as a historical record per the project's stated convention ("rows are updated, not replaced") and is not a stale claim — but a future reader skimming for "best-effort" would land on it. Optional future polish: append a parenthetical "(superseded 2026-05-08 by PROJ-379 closeout)" to that row. Not a remediation requirement.

`design.md` line 123 also says "(best-effort)" about populated-planet generation — that document was the original PROJ-377 plan and has been overtaken by PROJ-379's hand-built approach. Same status: historical record, not a stale claim.

### Area 7 — Test growth: CONFIRM

`python Tools/test_sharded/test_sharded.py` ran 65.4s and reported:

```
TOTAL: 19089 tests | 19084 passed | 1 failed | 0 errors | 4 skipped
```

19084 = 19077 (PROJ-378 close) + 7 (PROJ-379 added: 4 in-process + 1 field-coverage + 2 cross-process). Matches the report's claim and the phase-checklist breakdown exactly.

### Area 8 — No `set` iteration in builder: CONFIRM

Grep `\bset\(|frozenset\(` in `_build_galaxy_fixture.py` returned zero matches. All fixture data structures are explicit lists / tuples / dict literals.

### Area 9 — Pre-existing failure: CONFIRM

The 1 failing test in the sharded run is unrelated to PROJ-379 (zero `game/**` changes); matches OpenCode's INFO finding.

## Recommended Actions for Claude

**Now — none required.** PROJ-379 is correct, complete, and the OpenCode review is accurate. The mutation test confirms the field-coverage guard is load-bearing (not a tautology). Ship.

**Defer / optional polish (not remediation):**
- INFO-V1 above — append a "(superseded 2026-05-08)" parenthetical to PROJ-377 `decisions.md` 2026-05-07 row 35, and update `design.md:123` populated-fixture description to point at PROJ-379. Pure doc hygiene; can fold into the next PROJ-377/PROJ-379 archival pass.

**OpenCode misses:** none material. OpenCode did not perform a mutation test on the field-coverage guard, but the verifier did and it passed — so OpenCode's PASS is upheld with stronger evidence.
