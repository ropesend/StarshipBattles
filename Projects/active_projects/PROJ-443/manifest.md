# PROJ-443 File Manifest

> Generated during charter creation 2026-05-18. The project triages and unblocks tests hidden by a long-standing `pytest.ini` `norecursedirs` configuration issue uncovered during PROJ-436 Phase 2, then bundles four small follow-up items deferred by PROJ-436 consults.

## Files

### Phase 0 — findings only

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-443/findings/hidden_test_baseline.md` | Findings (new) | Snapshot of pass/fail counts + full list of failing test IDs in `tests/unit/strategy/data/` (and any other hidden `tests/.../data/` dirs) at PROJ-443 start. No code touched. |

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

### Phase 3 — remaining `tests/unit/strategy/data/` failures

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/*` | Test | ~26 remaining after Phases 1+2 (per the 65-failure PROJ-436 Phase 2 baseline). Cluster + fix. |

### Phase 4 — pytest config flip

| File | Type | Notes |
|------|------|-------|
| `pytest.ini` | Config | Remove `data` from `norecursedirs`. Add `--ignore=./data` to `addopts` to anchor the exclusion to the top-level `data/` only. |
| `tests/static_guards/test_no_hidden_test_directories.py` | Test (new) | Regression guard: every `test_*.py` under `tests/` is collected by `pytest tests/ --collect-only`. Prevents future drift if someone adds a new directory name to `norecursedirs`. |
| `Tools/test_sharded/.test_durations.json` | Data | Updated automatically by the first sharded run after the flip; the new tests gain duration entries. |

### Phase 5 — bundled PROJ-436 deferred items

#### 5a — Phase 3 finding (d) dataclass-introspection drift

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | If we choose to clean up: rename `_consumable_levels` and `_cargo_contents` back to public names by relying on `@property` introspection workarounds, OR document the introspection-drift surface as accepted in `decisions.md` and move on. |

#### 5b — Phase 3 finding (e) legacy-kwarg constructor wrapper

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | Delete the module-level legacy-kwarg translator once test fixtures migrate. |
| 7 test files (per PROJ-436 Phase 3 audit) | Test | ~24 sites passing `ShipInstance(consumable_levels=..., cargo_contents=...)` migrate to constructor + post-init `_resource_mgr` / `_cargo_mgr` calls. |

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
| (none expected) | — | This is a test-infrastructure + small-cleanup project; docs already cover the underlying systems. If Phase 4's regression guard surfaces drift in `docs/guides/testing_infrastructure.md`, update there. |
