# PROJ-322: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Test Review

- Review directory: `Reviews/results/2026-05-02_204633_test-review/`
- OpenCode CONFIRMED candidates for this tier (P1): 93 - 51 from category-level shard reports (CAT-4: 13 + CAT-5: 14 + CAT-6: 17 + CAT-7: 7) + 42 cross-shard cluster members (APC-001: 16 + APC-002: 11 + APC-003: 8 + DUP-001..3: 3 + HLP-001..4: 4)
- Independently verified: 111
- Needs-rework: 4
- Rejected: 1
- Out-of-scope: 3

The verified-item count exceeds the OpenCode CONFIRMED count because the OpenCode counts in `SUMMARY.md` count the cross-shard clusters (APC/DUP/HLP) once per cluster, while the verifier expanded each cluster into per-file checklist items (e.g., APC-001 = 16 individual files, APC-002 = 10 verified files, APC-003 = 8 files, plus 3 DUP + 4 HLP cluster-level entries). The 115 P1 items in `candidates.json` reflect the per-file/per-cluster expansion.

Claimed total LOC for the P1 tier (sum of `loc_affected` across V + NR items): approximately 9,629 LOC of test-side rewrites and consolidations. There is no separate "claimed vs verified" gap at the LOC level for P1 because the verifier kept all V + NR items at their reviewed LOC scope; rejected (1 item, 40 LOC) and out-of-scope (3 items, ~145 LOC) churn was excluded from this project before the per-phase totals above were computed.

**One-sentence summary:** P1 (CAT-4/5/6/7 + APC/DUP/HLP cross-shard clusters): test quality and performance debt - duplicate tests, expensive fixtures, brittle mocking, sleep-based waits, and cross-file anti-patterns including 16 `__new__` bypass-init UI test files and source-inspection guards.

## Initial Analysis

PROJ-322 sits in the middle of a 3-project sibling chain (PROJ-321 P0 → PROJ-322 P1 → PROJ-323 P2) and inherits a hard cross-project execution-order requirement: PROJ-321 deletes 12 whole files plus 17 partial deletions, which invalidates approximately 17 PROJ-322 tasks whose targets no longer exist by the time this project runs. Per-task obsoletion checks at the start of each phase 5 task were necessary to keep the checklist honest. Within PROJ-322 itself, an internal Phase 3 → Phase 5 ordering exists: 11 Phase 5 APC tasks reference Phase 3 boundary-patching prerequisites, so applying the APC `__new__`-bypass fixes before the boundary refactor would undo Phase 3 work.

Two systemic blockers surfaced during implementation and shaped the deferral set. The **UIWindow super-init chain** limitation prevents the shared `make_ui_widget` factory from intercepting `super().__init__()` calls — Python resolves the MRO at class definition, so element-class patches injected by the factory don't propagate up the chain. This blocks 7 APC-001 tasks plus roughly 5 boundary-patching tasks. The **freezegun / LLMBackgroundCall thread incompatibility** blocks Task 4.3: the production polling loop runs on a real thread, and `freezegun` (which is also not installed in this repo) cannot rewrite the underlying `time.monotonic` calls inside the polling thread. Both blockers are documented per-task and require focused production-side refactors to unblock.

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture

The remediation introduced a new shared-fixture infrastructure under `tests/fixtures/` to replace ad-hoc per-file mocks and `__new__`-bypass init patterns:

- **`tests/fixtures/ui_widget_factory.py`** — ~230 LOC factory plus ~125 LOC of smoke tests. Exposes `make_ui_widget(Cls, extra_modules, **kwargs)` which patches the pygame-gui element classes and the widget's own module imports, then calls the real constructor. Works for non-UIWindow widgets; cannot patch through `super().__init__()` chains (see Dependencies & Risks).
- **`tests/fixtures/cargo_mock_ship.py`** — closure-based capacity / contents lambdas for cargo-system tests.
- **`tests/fixtures/yard_facility.py`** — shared yard facility factory.
- **`tests/fixtures/mock_planet.py`** — shared mock planet factory.
- **`tests/unit/simulation/conftest.py`** — HLP-002 BattleRunner shared fixtures (`_make_ship_spec`, `_make_team`, `ship_builder`).

Two patterns recur across phases:

- **`make_ui_widget(Cls, extra_modules, **kwargs)`** — call the real constructor with patched dependencies instead of `Cls.__new__(Cls)` + manual attribute injection. Limited by the UIWindow chain issue above.
- **Boundary-patching** (Phase 3 + APC-003 cross-coordinated work) — drive tests through public surface (`handle_event`, `update`, `draw`, or domain methods like `engine.start()`) rather than patching private helpers (`_init_layout`, `_build_list`, `_rebuild_ui`, `_initialize_ship`).

### Key Patterns to Reuse
- **`make_ui_widget` factory**: `tests/fixtures/ui_widget_factory.py:1-230` — works for non-UIWindow widgets; pass `extra_modules` for sibling-module imports. Usage examples in `tests/fixtures/test_ui_widget_factory.py`.
- **Cargo mock ship**: `tests/fixtures/cargo_mock_ship.py` — closure-based capacity / contents lambdas.
- **Yard facility factory**: `tests/fixtures/yard_facility.py`.
- **Mock planet factory**: `tests/fixtures/mock_planet.py`.
- **BattleRunner shared fixtures**: `tests/unit/simulation/conftest.py` — `_make_ship_spec`, `_make_team`, `ship_builder`.
- **Public-API boundary patching example**: `tests/unit/simulation/systems/test_battle_engine_init_ship.py` — 4 tests rewritten to drive `engine.start()` instead of the `_initialize_ship()` private helper.

### Dependencies & Risks

1. **UIWindow super-init chain blocker** — affects ~7 APC-001 file rewrites plus several boundary-patching tasks. MRO is resolved at class definition time, so the factory's element-class patches don't intercept `super().__init__()`. Mitigation: documented as deferred with concrete next-step pointers in each affected task; unblocking requires a production-side change (bypass flag on UIWindow subclasses) or a factory enhancement that intercepts the super-call site.
2. **LLMBackgroundCall real-thread polling** — Task 4.3 needs the production thread coordination to be refactored (event/future-based wait) before a mocked clock can replace polling loops. Mitigation: deferred with concrete blocker rationale.
3. **Shape-mismatch shared factories** — DUP-001 / HLP-001 cited helpers across files have meaningfully different shapes; consolidation would lose information. Mitigation: deferred with rationale; the narrower shared factories where shapes did align (DUP-003 cargo, HLP-003 yard, HLP-004 planet) were created.
4. **Cross-project file overlap** — 21 files overlap PROJ-321/322; 4 files have direct delete-vs-rewrite conflict. Mitigation: required PROJ-321-first execution order plus per-task obsoletion check before each Phase 5 task.
5. **Freezegun unavailability** — `freezegun` is not installed; manual `time.monotonic` patching is the fallback for non-thread-coupled cases (worked for some Phase 4 tasks; does not work for Task 4.3's real-thread polling).

### Opportunities Discovered
- The shared `make_ui_widget` factory is reusable across the codebase wherever non-UIWindow widgets need testing — could be referenced in `docs/02_PATTERNS.md` as a canonical pattern.
- The boundary-patching pattern (drive `engine.start()` instead of `_initialize_ship()`) is broadly applicable beyond P1 scope; could be promoted to a convention in `docs/03_CONVENTIONS.md`.
- The remaining UIWindow cluster (~7 files, ~1,400 LOC of bypass-init helpers) suggests a focused follow-up project worth scoping — either a class-level `bypass_init=True` flag on UIWindow subclasses, or a factory enhancement that intercepts the `super().__init__()` call site.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
