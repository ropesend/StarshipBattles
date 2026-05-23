# PROJ-443 File Manifest

> Generated during charter creation 2026-05-18. Revised after Codex pre-execution consult at `AgentCoordination/Scratchpad/Consult/20260518T034917Z_proj443-charter-review/` expanded the scope from 1 token (`data`) to 3 tokens (`data`, `combat_lab`, `Assets`) and switched the config approach from `--ignore=./data` addition to token removal only.

## Files

### Phase 0 — findings only

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-443/findings/hidden_test_baseline.md` | Findings (new) | Snapshot of pass/fail counts + full list of failing test IDs across **all 6 hidden directories** at PROJ-443 start: `tests/unit/strategy/data/` (95 files), `tests/unit/combat_lab/` (24), `tests/unit/data/` (3), `tests/unit/assets/` (2), `tests/unit/ui/assets/` (1), `tests/integration/data/` (1). No code touched. |

### Phase 1 — `test_cargo_tracking.py` triage

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/test_cargo_tracking.py` | Test | Per-test triage. Some now pass after PROJ-436 Phase 3's cargo manager API migration; some need rewriting against the new contract; some may be obsolete. |
| Production code referenced by failing tests | Production | Only if a test exposes a real bug — fix at the source. |

### Phase 2 — `test_mutator_boundary_ast_guard.py` triage

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` | Test | ~9 AST static-guard failures. Audit guard semantics post-Phase-3/4/5 architecture; rewrite or fix code to satisfy. |
| `game/strategy/data/` files implicated by guards | Production | Only if the guard exposes a real invariant violation. |

### Phase 3 — remaining hidden-test failures (strategy/data long-tail + 5 smaller hidden dirs)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/*` | Test | ~26 long-tail after Phases 1+2. Cluster + fix. |
| `tests/unit/combat_lab/*` | Test | 24 test files. Triage post-PROJ-436 storage / cargo / planet / empire / transfer-validator changes. Combat Lab is a complex subsystem; may surface its own cluster of failures. |
| `tests/unit/data/*` | Test | 3 test files. Quick triage. |
| `tests/unit/assets/*` | Test | 2 test files. Quick triage. |
| `tests/unit/ui/assets/*` | Test | 1 test file. Quick triage. |
| `tests/integration/data/*` | Test | 1 test file. Quick triage. |

### Phase 4 — pytest config flip + regression guard + docs + testmon

| File | Type | Notes |
|------|------|-------|
| `pytest.ini` | Config | **Remove** `data`, `combat_lab`, `Assets` from `norecursedirs`. Keep `ShipThemes` (harmless). Keep all other tokens. **No `--ignore` flag added** — `testpaths = tests` already prevents pytest from descending into the top-level dirs the tokens were trying to skip, and `--ignore` is cwd-relative per pytest 9.0.3 source (`_pytest/pathlib.py:998-1004`), creating a foot-gun for non-canonical invocations. |
| `tests/static_guards/test_no_hidden_test_files.py` | Test (new) | File-level regression guard: every `test_*.py` under `tests/` is in the `pytest tests/ --collect-only` set. Catches the PROJ-443 class of bug + any future `norecursedirs` / `--ignore` / `testpaths` / `python_files` regression that drops a file. Does NOT catch function-level drift (`python_functions`/hooks); accepted scope limit per `decisions.md`. |
| `docs/guides/testing_infrastructure.md` | Docs | Refresh the embedded `pytest.ini` snippet (around lines 187-194) to reflect the new `norecursedirs` value. Add a brief rationale line. |
| `Tools/test_sharded/.test_durations.json` | Data | Updated automatically by the first sharded run after the flip; the ~126 newly-visible tests gain duration entries. First-run shard imbalance is expected and recovers within 1-2 runs. |
| `.testmondata` | Local data (gitignored) | Recommended one-time wipe + rebuild after the config flip: `rm .testmondata && pytest tests/ --testmon`. Documented in `decisions.md`. Not committed; each contributor's choice. |

### Phase 5 — bundled PROJ-436 deferred items

#### 5a — Phase 3 finding (d) dataclass-introspection drift

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | If we choose to clean up: rename `_consumable_levels` and `_cargo_contents` back to public names via a more clever `@property` introspection workaround, OR document the introspection-drift surface as accepted in `decisions.md` and move on. |

#### 5b — Phase 3 finding (e) legacy-kwarg constructor wrapper

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | Delete the module-level legacy-kwarg translator once test fixtures migrate. |
| ~7 test files (per PROJ-436 Phase 3 audit) | Test | ~24 sites passing `ShipInstance(consumable_levels=..., cargo_contents=...)` migrate to constructor + post-init `_resource_mgr` / `_cargo_mgr` calls. |

#### 5c — Phase 6 production_engine test-mock residue

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/engine/test_production_engine_queue.py` | Test | Delete inert `MagicMock(add_resources=...)` / `consume_resources=...` attribute attachments for deleted Empire methods. |
| `tests/unit/strategy/engine/test_production_engine_consumption.py` | Test | Same. |
| `tests/unit/strategy/engine/test_production_engine_refactor.py` | Test | Same. |
| `tests/unit/strategy/engine/test_harvesting_engine.py` | Test | Same. |

#### 5d — Phase 5 D2 large-empire profiling

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-443/findings/d2_profiling.md` | Findings (conditional) | Only landed if a real perf signal emerges. Otherwise `decisions.md` documents "no signal observed; deferred indefinitely." |

### Phase 6 — Codex consult

| File | Type | Notes |
|------|------|-------|
| `AgentCoordination/Scratchpad/Consult/<timestamp>_proj443-final/response.md` | Scratch | Codex pre-final-check consult response. |

### Docs touched

| File | Type | Notes |
|------|------|-------|
| `docs/guides/testing_infrastructure.md` | Docs | Phase 4: refresh embedded `pytest.ini` snippet (lines ~187-194) + brief rationale. Per Codex finding. |
