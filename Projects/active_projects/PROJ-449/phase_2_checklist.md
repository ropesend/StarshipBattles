# Phase 2: Sweep direct call sites in tests + rewrite `planet_from_dict_kwargs`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-449 2`
> 2. Sharded suite green (`python Tools/test_sharded/test_sharded.py`)
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Objective:** Migrate every direct call site outside `tests/fixtures/strategy_entities.py` (i.e. every test file passing `consumable_levels=` / `cargo_contents=` / `stockpile=` / `max_stockpile=` / `staging_yard=` directly to a `ShipInstance(...)` / `Planet(...)` / `PlanetaryFacility(...)` constructor). Rewrite `planet_from_dict_kwargs` to emit private kwargs. Wrappers stay; their bodies are now unreached.

**File ownership rule:** This project owns wrapper-related test migrations and the production serde site. Phase 2 touches `game/strategy/data/planet_serde.py` plus the Phase 0 audit's test-file list. No UI / facade / engine edits.

**Source-of-truth findings:** F-A-002 (planet_serde dependency), F-A-025 (`data.get("resources", {})` legacy alias free-rider) — see [findings/PROJ-449_findings.md](findings/PROJ-449_findings.md) and the archived `bucket_a_data_facade_scan.md` for F-A-025.

---

## Tasks

### Task 2.1: Rewrite `planet_from_dict_kwargs` to emit private kwargs [Medium]
**File:** `game/strategy/data/planet_serde.py`
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py tests/unit/strategy/data/test_planet_stockpile.py -n 4 -q`

- [ ] At lines 157-159, change:
  ```python
  stockpile=data.get("stockpile", {}),
  max_stockpile=data.get("max_stockpile", {}),
  staging_yard=data.get("staging_yard", []),
  ```
  to:
  ```python
  _stockpile=data.get("stockpile", {}),
  _max_stockpile=data.get("max_stockpile", {}),
  _staging_yard=data.get("staging_yard", []),
  ```
  (Save-format key names stay public — `"stockpile"` / `"max_stockpile"` / `"staging_yard"`. Only the constructor kwarg spellings change.)
- [ ] F-A-025 free-rider: at line 156, change:
  ```python
  deposits=data.get("deposits", data.get("resources", {})),
  ```
  to:
  ```python
  deposits=data.get("deposits", {}),
  ```
  (Per CLAUDE.md "Old saves are disposable" — the `data.get("resources", {})` fallback supports a pre-PROJ-372 save format that's no longer valid.)
- [ ] Run focused tests above; verify save-load round-trip remains green
- [ ] Verify: `test_roundtrip_planet::test_planet_round_trip_preserves_stockpile_state` still passes

### Task 2.2: Run Phase 0 audit output and migrate each file [Complex]
**Files:** Phase 0 audit output (see `findings/phase_0_audit.md` after Phase 0 lands)
**Tests:** focused per-file pytest invocations, then full sharded suite at the end

- [ ] For each file in the ShipInstance sweep set:
  - [ ] Identify each `ShipInstance(...)` or `PlanetaryFacility(...)` constructor call with legacy kwargs
  - [ ] Translate `consumable_levels=X` → `_consumable_levels=X`
  - [ ] Translate `cargo_contents=X` → `_cargo_contents=X`
  - [ ] Run the file's focused tests (`pytest <file> -q`)
  - [ ] Commit per-file or per-cluster (grouped commits acceptable for trivial sweeps; if any file requires non-mechanical edits, separate commit)
- [ ] For each file in the Planet sweep set:
  - [ ] Identify each `Planet(...)` constructor call with legacy kwargs
  - [ ] Translate `stockpile=X` → `_stockpile=X`
  - [ ] Translate `max_stockpile=X` → `_max_stockpile=X`
  - [ ] Translate `staging_yard=X` → `_staging_yard=X` (rare — only 2 confirmed sites from pre-audit `rg`)
  - [ ] Same per-file test discipline as above
- [ ] Sweep `tests/fixtures/saves/_build_galaxy_fixture.py` separately (PROJ-436 Phase 4f comment names it explicitly as a load-bearing fixture builder)

**Notes:** Mechanical sweep. Each edit is a single-token rename. If a test exercises the wrapper itself ("test that legacy kwargs still translate"), that test becomes vestigial after Phase 3 / 4 — leave it intact in Phase 2 (the wrapper still exists), but add a deletion candidate to `findings/phase_2_followups.md` for Phase 3 / 4.

### Task 2.3: Verify sharded suite green at the same pre-phase count [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite
- [ ] Test count should equal pre-phase count (the wrapper still translates the rare straggler if any was missed — no failures expected)
- [ ] If failures appear, classify per the PROJ-443 Phase 5b pattern:
  - (a) test now exercises a wrapper-translated path that's been removed somewhere → fix the test
  - (b) test missed by the audit → add to the sweep set, repeat Task 2.2 for that file
  - (c) genuine regression in test fixtures or serde → investigate
- [ ] If 5+ stragglers surface, log a finding and update plan.md Current State with the count adjustment

### Task 2.4: Confirm wrapper bodies are now unreached [Simple]
**Tests:** instrumentation; can be done via `coverage.py` or a temporary print/log in the wrapper

- [ ] Optional (recommended): add a temporary `logger.warning("LEGACY KWARG TRANSLATION TRIGGERED: %r", kwargs.keys())` line inside `_planet_init_with_legacy_kwargs` and `_ship_instance_init_with_legacy_kwargs`
- [ ] Run sharded suite; capture log output
- [ ] Expected: zero warnings emitted (Phase 1 + Phase 2 covered all callers)
- [ ] **Remove the temporary log line before committing**
- [ ] If warnings appear, the audit missed at least one site; add it to the sweep set and re-run

---

## Phase Completion Checklist
- [ ] `planet_from_dict_kwargs` rewritten; save-load round-trip green
- [ ] All Phase 0 audit sweep sites migrated
- [ ] F-A-025 free-rider (`data.get("resources", {})`) removed
- [ ] Sharded suite green
- [ ] Wrapper-translation log instrumentation confirms zero triggers (Task 2.4 optional but recommended)
- [ ] Plan.md Quick Status → Complete
- [ ] Plan.md Current State updated; ready for Phase 3 (wrapper + property deletion)

## Notes / Risks / Coordination Touchpoints
- **PROJ-450 is sequenced after Phase 3**, not Phase 2. Phase 2 changes only kwarg spellings — the substrate stays `List[Dict[str, Any]]`. PROJ-450 starts its work on the same Planet surface after Phase 3 deletes the property cluster.
- **Save format unchanged.** `planet_to_dict` continues to emit `"stockpile"` / `"max_stockpile"` / `"staging_yard"` as save keys. Phase 3 will update `planet_to_dict` to read from `_stockpile` etc. directly (no longer through the property).
- **Wrapper bodies survive this phase.** If a Phase 2 commit silently breaks because the audit missed a site, the wrapper still translates and the suite stays green. Task 2.4's instrumentation is the gate that catches missed sites BEFORE Phase 3 deletes the wrapper.
- **Risk of regression**: PROJ-443 Phase 5b hit 19 failures + 16 errors when the wrapper was deleted before the sweep. This phase reverses that ordering — sweep first (Phase 1+2), delete after (Phase 3+4). If Phase 2 audit was complete, Phase 3 / 4 deletion is a no-op for callers.
