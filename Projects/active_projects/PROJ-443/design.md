# PROJ-443: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

This project addresses a discovery surfaced during PROJ-436 Phase 2 and bundles four follow-up items deferred by PROJ-436's Codex consults. The discovery is documented in [PROJ-436/decisions.md](../PROJ-436/decisions.md) under the 2026-05-18 "DISCOVERY" row.

## Initial Analysis

### The pytest config issue

`pytest.ini` declares:

```ini
norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv data ShipThemes Assets combat_lab
```

The `data` token's intent is to skip the top-level `data/` directory (JSON game data, image assets, etc.) so pytest doesn't waste time descending it. But `norecursedirs` is documented as a list of glob-style patterns matched against directory **basenames** at any depth, not anchored to repo root. So `data` matches:

- `data/` (top-level — intended)
- `tests/unit/strategy/data/` (1575 tests — unintended)
- any other `**/data/` that may be added in future

The effect: when the sharded runner calls `pytest tests/ --collect-only`, the collector walks `tests/` but refuses to enter any directory named `data`. The 1575 tests in `tests/unit/strategy/data/` never reach the runner.

Direct invocation works: `pytest tests/unit/strategy/data/` collects the tests because the user explicitly named the directory, overriding `norecursedirs`.

### Hidden-test current state (at PROJ-436 Phase 2 baseline)

Per `tests/unit/strategy/data/` direct invocation:
- 1510 pass
- 65 fail

Breakdown of the 65 (audit-validated during PROJ-436):
- ~30 in `test_cargo_tracking.py` — PROJ-431's completion report explicitly flagged these as pre-existing and unrelated to the PROJ-422..435 arc. After PROJ-436 Phase 3's cargo manager API migration, many should now pass naturally.
- ~9 in `test_mutator_boundary_ast_guard.py` — AST static guards that have drifted relative to the current entity surfaces.
- ~26 spread across other files in the directory.

PROJ-436 Phases 3-7 touched code that these hidden tests cover. Phase 0 of this project recaptures the actual current baseline at the new HEAD before any triage.

### Why this matters

- CI confidence is overstated. The sharded gate has been giving 21000+ green tests, but 1575 tests outside that count have been silently broken (or silently passing — we don't know without auditing).
- New PROJ-436 work and any future test additions in `tests/unit/strategy/data/` continue to not run in the sharded gate. Anyone adding tests there assumes they're protected by CI when they're not.
- The 65 known failures may include real regressions that have been hiding for months.

### PROJ-436 deferred items (Phase 5 bundle)

Each is a small, self-contained cleanup that PROJ-436's Codex consults verified as a real issue but deemed out of scope for the cargo-substrate cutover:

- **Phase 3 finding (d) — dataclass-introspection drift on `ShipInstance`.** Phase 3f deleted `consumable_levels` and `cargo_contents` as dataclass fields and replaced them with `@property` accessors over `_consumable_levels` and `_cargo_contents` private fields. `dataclasses.fields(ShipInstance)` now exposes the private names; `inspect.signature(ShipInstance.__init__)` similarly. No production caller relies on this introspection surface today, but the drift is cosmetic. Cleanup choices: (a) accept and document; (b) revert the rename via a more clever `@dataclass` pattern.
- **Phase 3 finding (e) — legacy-kwarg constructor wrapper.** Phase 3f added a module-level wrapper that translates `ShipInstance(consumable_levels=...)` / `ShipInstance(cargo_contents=...)` kwargs into the private-field names so ~24 sites in 7 test fixtures keep working. The wrapper is functional but a code smell. Cleanup: mechanical sweep of the 24 sites; delete the wrapper at the end.
- **Phase 5 D2 — large-empire profiling.** `Empire.resource_pool` is a pure colony-aggregation query (no caching). Phase 5 ship analysis: net-zero cost change vs the pre-PROJ-436 implementation. No production stress test has shown a hot path. Cleanup is conditional: only execute if a real signal emerges; otherwise document as accepted.
- **Phase 6 — production_engine test-mock residue.** 4 test files attach inert `MagicMock(add_resources=..., consume_resources=...)` attributes for Empire methods that were deleted in Phase 5. Production never invokes them — the mocks are dead weight. Cleanup: delete the attribute attachments.

## Architecture

### Phase ordering rationale

```
Phase 0: capture baseline (no code change)
   ↓
Phase 1: triage test_cargo_tracking.py (PROJ-431-flagged, largest cluster)
   ↓
Phase 2: triage test_mutator_boundary_ast_guard.py (AST guard drift)
   ↓
Phase 3: triage remaining ~26 failures (long tail)
   ↓                                       ← hidden directory now green via direct invocation
Phase 4: flip pytest.ini config             ← sharded suite jumps from ~21233 to ~22700+
   ↓                                       ← regression guard against future drift
Phase 5: bundled PROJ-436 deferred items   ← can run in any order; landing as separate commits
   ↓
Phase 6: Codex consult + remediation
```

Phases 1-3 fix the hidden directory **before** the config flip in Phase 4. If we flipped first, the sharded gate would go red on the next CI run. Triage-first keeps the gate green at every commit boundary.

### Phase 4 config change — exact diff

Before:
```ini
norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv data ShipThemes Assets combat_lab
addopts = -n 4 --ignore=Refactoring --ignore-glob=*.txt --ignore=combat_lab --junitxml=./.pytest_cache/test-results.xml
```

After:
```ini
norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv ShipThemes Assets combat_lab
addopts = -n 4 --ignore=Refactoring --ignore-glob=*.txt --ignore=combat_lab --ignore=./data --junitxml=./.pytest_cache/test-results.xml
```

`--ignore=./data` is relative to the directory pytest is invoked from. The sharded runner invokes from repo root (verified in `Tools/test_sharded/test_sharded.py:107` which passes `cwd=str(PROJECT_ROOT)`). So `./data` resolves to the top-level `data/` only — `tests/unit/strategy/data/` is no longer affected.

### Phase 4 regression guard

```python
# tests/static_guards/test_no_hidden_test_directories.py
def test_every_test_file_is_collected():
    """Every test_*.py under tests/ must be reachable by the sharded runner.

    Guards against future regressions where someone adds a directory name
    to `norecursedirs` that accidentally matches a real test directory
    (the PROJ-443 root cause).
    """
    import subprocess, sys
    from pathlib import Path

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q",
         "--no-header", "-n", "0"],
        capture_output=True, text=True, cwd=str(Path(__file__).resolve().parents[2]),
        timeout=60,
    )
    collected_ids = {line.strip() for line in result.stdout.splitlines() if "::" in line}
    collected_files = {nid.split("::")[0] for nid in collected_ids}

    on_disk = {
        str(p.relative_to(Path(__file__).resolve().parents[2])).replace("\\", "/")
        for p in Path("tests").rglob("test_*.py")
    }
    missing = on_disk - collected_files
    assert not missing, (
        f"{len(missing)} test files exist on disk but were not collected by the sharded runner. "
        f"This usually means a `norecursedirs` entry in pytest.ini matches a directory name in `tests/`. "
        f"First few missing: {sorted(missing)[:5]}"
    )
```

The guard is structural (every on-disk `test_*.py` is in the collection set), not count-based (which would require updating with every test addition).

## Key Patterns to Reuse

- **Substrate-then-sweep-then-delete** ([PROJ-431/decisions.md](../PROJ-431/decisions.md)) — Phase 1-3 triage commits one cluster of failures at a time. Each commit functional.
- **End-of-project Codex consult** — Phase 6, per standing workflow.
- **AST static guard** — `tests/static_guards/` is the canonical pattern for "this invariant must not regress." Phase 4 adds a new file there.

## Dependencies & Risks

### Hard dependencies

- **None.** PROJ-436 Phases 0-7 complete (committed). PROJ-436 Phases 8/9 may run in parallel branches.

### Risks

1. **The 65 hidden failures may include real regressions, not just test bit-rot.** Triage may force production code fixes outside this project's stated scope. Mitigation: if a hidden test exposes a real bug, fix at source and document the production change in `decisions.md`. If it's beyond a reasonable triage budget, escalate to user.

2. **PROJ-436 Phase 8/9 may run concurrently and change the failure count.** Mitigation: recapture Phase 0 baseline if Phase 8/9 land mid-project; treat as a new starting point.

3. **The Phase 4 regression guard subprocess invokes pytest from within a test, which is slow.** Mitigation: keep it in the sharded suite but accept the cost (~5s); alternative is a one-shot check at CI startup if performance becomes an issue.

4. **Phase 5b (legacy-kwarg constructor wrapper) sweep is mechanical but large** (~24 sites in 7 test files). Mitigation: one commit per file; sharded gate at each.

## Opportunities Discovered

- After Phase 4 flips the config, the sharded gate becomes a stronger CI signal. Future test additions under any layer's `data/` subdirectory will automatically be picked up.
- Phase 5b cleanup deletes a non-trivial code smell (~50 lines of constructor-wrapper code in `ship_instance.py`) — the production file size budget improves.
- The regression guard added in Phase 4 catches an entire class of future configuration mistakes.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
