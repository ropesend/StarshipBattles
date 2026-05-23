# PROJ-443: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

This project addresses a discovery surfaced during PROJ-436 Phase 2 and bundles four follow-up items deferred by PROJ-436's Codex consults.

- Original discovery (PROJ-436 Phase 2): documented in [Projects/active_projects/PROJ-436/decisions.md](../PROJ-436/decisions.md) (the 2026-05-18 "DISCOVERY" row).
- PROJ-431 `test_cargo_tracking.py` provenance: cited in [PROJ-436/plan.md:34-37](../PROJ-436/plan.md) and the post-435 discussion at [AgentCoordination/Scratchpad/Discussion/20260517T230029Z_post-435-project-creation/arc01_001_claude_to_codex.md:56-61](../../../AgentCoordination/Scratchpad/Discussion/20260517T230029Z_post-435-project-creation/arc01_001_claude_to_codex.md). PROJ-431 itself has been archived to `Projects/archived_projects/PROJ-431/` and its decisions log does not mention `test_cargo_tracking` directly — the failure-flag trail lives in the PROJ-436 charter and the post-435 design discussion.
- Charter pre-execution Codex consult: [AgentCoordination/Scratchpad/Consult/20260518T034917Z_proj443-charter-review/response.md](../../../AgentCoordination/Scratchpad/Consult/20260518T034917Z_proj443-charter-review/response.md) — surfaced 2 must-fix findings driving the charter revision documented here.

## Initial Analysis

### The pytest config issue (verified via Codex consult)

`pytest.ini` declares:

```ini
norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv data ShipThemes Assets combat_lab
testpaths = tests
```

Per `_pytest/main.py:455-458` (verified by Codex via local pytest 9.0.3 install), `norecursedirs` is a list of `fnmatch`-style patterns matched against directory **basenames** at any depth — not anchored to the repo root. On Windows, `fnmatch.fnmatch` is case-insensitive, so `Assets` matches lowercase `assets` directories.

Three tokens collide with real test directories (audit `find tests -type d \( -name data -o -name combat_lab -o -iname assets -o -name ShipThemes \)`):

| Token | Hidden test directories | `test_*.py` count |
|---|---|---|
| `data` | `tests/integration/data/`, `tests/unit/data/`, `tests/unit/research/data/` (0 tests), `tests/unit/strategy/data/` | 1 + 3 + 0 + 95 = 99 |
| `combat_lab` | `tests/unit/combat_lab/` | 24 |
| `Assets` | `tests/unit/assets/`, `tests/unit/ui/assets/` | 2 + 1 = 3 |
| `ShipThemes` | (no matches) | 0 |
| **Total hidden** | **6 directories** | **126 files** |

The intent of these tokens was to skip the top-level `data/`, `combat_lab/`, `Assets/`, and `ShipThemes/` directories. But `pytest.ini` already has `testpaths = tests`, which restricts default collection to `tests/` regardless. The `norecursedirs` tokens are redundant at best and harmful at worst — they hide real test directories without providing meaningful exclusion benefit during the normal `testpaths`-anchored run.

### Why `--ignore=./data` is the wrong fix (verified by Codex)

The original charter draft proposed adding `--ignore=./data` to `addopts`. Per pytest 9.0.3 source (`_pytest/main.py:433-437` → `_pytest/pathlib.py:998-1004`), `--ignore=path` resolves via `Path(os.path.abspath(path))` — relative to **process cwd**, not config root. The canonical sharded runner is safe because it invokes pytest with `cwd=str(PROJECT_ROOT)` ([Tools/test_sharded/test_sharded.py:104-107](../../../Tools/test_sharded/test_sharded.py)). But direct `pytest .` from a subdirectory, an IDE plugin, or any non-canonical invocation would anchor `./data` somewhere unintended — potentially skipping a different `data` directory than the top-level one.

Codex's recommended approach (adopted): **remove the problematic tokens from `norecursedirs` and stop there.** `testpaths = tests` already prevents pytest from descending into the top-level `data/` / `Assets/` / `combat_lab/` directories during normal runs. The user can still skip them with explicit CLI `--ignore=data` when running from the repo root if they want, but the config itself shouldn't carry the relativity foot-gun.

### Hidden-test current state

PROJ-436 Phase 2 audit captured a snapshot of `tests/unit/strategy/data/` alone:
- 1510 pass / 65 fail

PROJ-436 Phases 3-7 touched code those hidden tests cover (cargo manager, planet storage, empire pool, protocols, transfer validator). The Phase 2 baseline is stale; Phase 0 recaptures the current actual state across **all 6** hidden directories.

### PROJ-436 deferred items (Phase 5 bundle)

Each is a small, self-contained cleanup that PROJ-436's Codex consults verified as a real issue but deemed out of scope for the cargo-substrate cutover. Detailed in `phase_5_checklist.md`:

- **Phase 3 finding (d)** — dataclass-introspection drift on `ShipInstance` (cosmetic).
- **Phase 3 finding (e)** — legacy-kwarg constructor wrapper smell (~24 sites in 7 test files).
- **Phase 5 D2** — large-empire profiling (conditional on real perf signal).
- **Phase 6** — production_engine test-mock residue (~6 inert MagicMock attributes).

## Architecture

### Phase ordering rationale

```
Phase 0: capture baseline (no code change) — all 6 hidden dirs
   ↓
Phase 1: triage tests/unit/strategy/data/test_cargo_tracking.py (PROJ-431-flagged ~30)
   ↓
Phase 2: triage tests/unit/strategy/data/test_mutator_boundary_ast_guard.py (~9 AST drift)
   ↓
Phase 3: triage long-tail in tests/unit/strategy/data/ (~26) + 5 smaller hidden dirs (31 files)
   ↓                                       ← all 6 hidden directories now green via direct invocation
Phase 4: pytest.ini token removals + regression guard + docs + testmon
   ↓                                       ← sharded suite jumps from ~21233 to ~21359+
Phase 5: bundled PROJ-436 deferred items   ← can run in any order; landing as separate commits
   ↓
Phase 6: Codex consult + remediation
```

Phases 1-3 fix the hidden directories **before** the config flip in Phase 4. If we flipped first, the sharded gate would go red on the next CI run. Triage-first keeps the gate green at every commit boundary.

### Phase 4 config change — exact diff

Before:
```ini
norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv data ShipThemes Assets combat_lab
addopts = -n 4 --ignore=Refactoring --ignore-glob=*.txt --ignore=combat_lab --junitxml=./.pytest_cache/test-results.xml
```

After:
```ini
norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv ShipThemes
addopts = -n 4 --ignore=Refactoring --ignore-glob=*.txt --ignore=combat_lab --junitxml=./.pytest_cache/test-results.xml
```

Three tokens removed from `norecursedirs`: `data`, `Assets`, `combat_lab`. `ShipThemes` retained (it doesn't match any test directory today, but the asset directory still exists and the cost of keeping the token is zero). `addopts` is unchanged — the existing `--ignore=combat_lab` already covers the top-level `combat_lab/` directory at the addopts level (path-relative to repo root cwd, which is how the sharded runner invokes pytest).

Note: the `--ignore=combat_lab` addopts entry IS cwd-relative per the same pathlib reasoning above. It works for the sharded runner because of its explicit `cwd=PROJECT_ROOT`. Same caveat applies to any non-canonical pytest invocation from a subdirectory; that's a pre-existing risk this project doesn't try to fix.

### Phase 4 regression guard

```python
# tests/static_guards/test_no_hidden_test_files.py
"""File-level regression guard for PROJ-443.

Asserts every on-disk `test_*.py` under `tests/` is reachable by the
sharded runner's collection. Prevents future `norecursedirs` /
`--ignore` / `python_files` regressions that would silently drop
test files from CI.

SCOPE NOTE: this guard is file-level only. A `python_functions` /
`python_classes` / collection-hook drop that silently filters
individual test items out of a still-collected file will NOT be
caught. That's a different class of drift than this guard targets.
"""
def test_every_test_file_is_collected():
    import subprocess, sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q",
         "--no-header", "-n", "0"],
        capture_output=True, text=True, cwd=str(repo_root),
        timeout=60,
    )
    collected_ids = {line.strip() for line in result.stdout.splitlines() if "::" in line}
    collected_files = {nid.split("::")[0] for nid in collected_ids}

    on_disk = {
        str(p.relative_to(repo_root)).replace("\\", "/")
        for p in (repo_root / "tests").rglob("test_*.py")
    }
    missing = on_disk - collected_files
    assert not missing, (
        f"{len(missing)} test files exist on disk but were not collected. "
        f"This usually means a `norecursedirs` entry in pytest.ini matches a "
        f"directory name in `tests/` (the PROJ-443 root cause), or a new "
        f"`--ignore` pattern accidentally caught a real test file. "
        f"First few missing: {sorted(missing)[:5]}"
    )
```

The guard is structural (every on-disk `test_*.py` is in collection) rather than count-based (which would require updating with every test addition). Per Codex's review, it's explicitly NOT a "catches all collection drift" guard — `python_functions`/`python_classes`/hooks can still silently drop items at function level inside collected files. We accept this scope limit.

### `.testmondata` rebuild

After the config flip, pytest's collection set grows by 126 tests. `.testmondata` is the testmon plugin's persistence file tracking which tests cover which code paths. `[unverified]` Testmon's docs don't strictly mandate a clean rebuild after collection-membership changes, but a one-time `rm .testmondata && pytest tests/ --testmon` is the safe default and avoids stale-state surprises. Phase 4 documents this in `decisions.md` and surfaces it to the user; the actual rebuild is a local operation each contributor runs.

### `docs/guides/testing_infrastructure.md` snippet refresh

Per Codex finding, this doc embeds a `pytest.ini` snippet (around lines 187-194) that will go stale after the Phase 4 config change. Phase 4 includes a docs-touch subtask to update the embedded snippet and explain the rationale.

## Key Patterns to Reuse

- **End-of-project Codex consult** — Phase 6, per standing workflow.
- **AST static guard** — `tests/static_guards/` is the canonical pattern for "this invariant must not regress." Phase 4 adds `test_no_hidden_test_files.py` there.
- **Direction rule** — triage before config flip is the substrate-then-sweep-then-delete pattern applied to test infrastructure.

## Dependencies & Risks

### Hard dependencies

- **None.** PROJ-436 Phases 0-7 complete (committed). PROJ-436 Phases 8/9 may run in parallel.

### Risks

1. **The 126 hidden tests may include real regressions, not just test bit-rot.** Triage may force production code fixes outside this project's stated scope. Mitigation: if a hidden test exposes a real bug, fix at source and document the production change in `decisions.md`. If it's beyond a reasonable triage budget, escalate to the user. Codex's sample of `test_cargo_tracking.py` and `test_mutator_boundary_ast_guard.py` suggests test-fixup scope is more likely than production refactor `[unverified — Codex sampled file shapes, didn't run them]`.

2. **PROJ-436 Phase 8/9 may run concurrently and change the failure count.** Mitigation: recapture Phase 0 baseline if Phase 8/9 land mid-project; treat as a new starting point.

3. **`tests/unit/combat_lab/` (24 files) was hidden — these tests cover Combat Lab functionality.** Combat Lab is a complex subsystem and its tests may have drifted significantly. Phase 3's combat_lab triage may surface a larger failure cluster than the `data`-prefixed ones. Mitigation: Phase 0 ledger gives an accurate count; if combat_lab cluster is large, escalate or split into a sibling sub-phase.

4. **The Phase 4 regression guard subprocess invokes pytest from within a test, which is slow (~5s).** Mitigation: accept the cost; the guard runs once per sharded shard, not per test.

5. **`docs/guides/testing_infrastructure.md` snippet update** could expose other doc-drift surfaces. Mitigation: bound the touch to the embedded snippet + a brief rationale line; do not over-scope into a doc refresh.

## Opportunities Discovered

- After Phase 4 flips the config, the sharded gate becomes a stronger CI signal. Future test additions under any layer's `data/` / `assets/` / `combat_lab/` subdirectory will automatically be picked up.
- Phase 5b cleanup deletes a non-trivial code smell (~50 lines of constructor-wrapper code in `ship_instance.py`) — the production file size budget improves.
- The regression guard added in Phase 4 catches an entire class of future configuration mistakes (file-level only, but that's the class PROJ-443 found).

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
