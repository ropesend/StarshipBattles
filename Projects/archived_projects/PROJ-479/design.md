# PROJ-479: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Test Review

- **Review directory:** `Reviews/results/2026-05-20_210550_test-review/`
- **Run date:** 2026-05-20
- **Priority tier for this project:** P1 (brittle-bloated remediation)
- **Categories included:** CAT-4 Duplicate Testing, CAT-5 Fixture Bloat, CAT-6 Mocking Brittleness, CAT-7 Sleep/Latency + cross-shard DUP-001/002/003/005/006 + HLP-001..006

### Item Counts (P1 tier)
| Metric | Count |
|--------|-------|
| OpenCode CONFIRMED candidates for this tier (CAT-4 + CAT-5 + CAT-6 + CAT-7 + 11 clusters) | 110 |
| Independently verified by Claude (entered the plan) | 95 |
| Needs rework (entered with adjusted suggestion) | 11 |
| Rejected (false positives — mutable shared state for fixtures, etc.) | 8 |
| Out of scope (intentional patterns) | 0 |

### LOC Impact
- **Review-claimed CAT-4..7 + cluster reclaimable LOC:** ~3,200 (within total ~4,800 shard-findings + ~740 cross-shard numbers)
- **Verified-only LOC (sum of `loc_affected` across V + NR items):** ~2,200

### Summary of Categories Included
CAT-4 (duplicate test pairs / clusters mergeable via parametrize); CAT-5 (function-scoped heavy fixtures rescoped to module/class where safe); CAT-6 (private-method patches / brittle call_args asserts replaced with public-boundary or behavioral checks); CAT-7 (`time.sleep` for nondeterministic state replaced with `threading.Event` / `_wait_until`); 5 DUP clusters + 6 HLP helpers extracted to canonical conftest / fixture locations.

## Initial Analysis

The cross-shard layer of this review is uncommonly load-bearing: `_make_fleet` alone has **43+ local definitions** across the test suite. The `MockPlanetType(Enum)` pattern appears in 10+ files. `MockGameSession` exists as 5 byte-identical copies. Phase 6 of this project sweeps these out and replaces them with imports from canonical conftest / fixture files, eliminating ~530 LOC and substantially reducing the surface area where a helper change has to be applied in multiple places.

Within-file findings are dominated by **two tension points**:

1. **CAT-5 fixture scope vs CAT-6 mock brittleness**: many fixtures got flagged CAT-5 (function-scoped, expensive) but verification rejected several because the fixtures are **mutable** (`MagicMock` accumulates call_args_list, `seeded_rng` is stateful PRNG, density maps mutate). Function scope is correct in those cases. The 8 REJECTED items in this tier are mostly CAT-5 claims where the reviewer didn't account for fixture mutability.

2. **`__new__` bypass patterns**: dozens of UI test files use `widget.__new__(WidgetClass) + manual attribute wiring`. Some are documented as intentional (PROJ-322 / PROJ-347 / PROJ-211/DI-compliance comments) and were excluded as `intentional_smoke_test`; others (e.g., `test_race_browser_dialog.py` 12 tests, `test_empire_build_queue_window.py`) should migrate to the canonical `bypass_init` fixture in `tests/fixtures/ui_widget_factory.py`.

## Swarm Findings Summary
Combined analysis from 16 shard verification reports + cross-shard cluster verification in `.agent_reports/2026-05-20_210550_test-review/`.

### Architecture
- **Canonical conftest hierarchy** is the primary extraction target: `tests/conftest.py` (root), `tests/unit/strategy/save_game_service/conftest.py` (save-game cluster), `tests/unit/strategy/engine/conftest.py` (engine cluster), `tests/fixtures/` (new fixture modules for battle panels, colonization, modifier stubs).
- **`bypass_init`** in `tests/fixtures/ui_widget_factory.py` is the documented pattern for pygame_gui widget tests; several brittle local `__init__` patch + manual wiring patterns should migrate to it.
- **`_wait_until`** in `tests/unit/strategy/services/test_race_description_llm_controller.py:133` is the local pattern for deterministic async waits; spread this pattern instead of `time.sleep`.

### Key Patterns to Reuse
- **Parametrization with semantic distinction**: tasks 1.1, 1.6, 1.8, 1.15, 1.16, 1.18 parametrize 2-3-element clusters where each cluster member exercises an equivalent code path. CAT-10 clusters with **<3 members** were rejected during verification (too small to be worth a parametrize); CAT-10 clusters where members exercise **different pipeline stages** (e.g., S06-F005 superweapon per-weapon-class) were also rejected. The verification rules are codified in `Projects/protocols/12_create_from_test_review.md`.
- **`assert_called_once_with` / `call_args.kwargs`** for stable mock assertions instead of `call_args[0][0]` positional tuple indexing.
- **Class-scoped + `deepcopy`** for fixtures that hold mutable state but are otherwise expensive to construct (Task 2.2).

### Dependencies & Risks
1. **HLP-004 sweep (Phase 6 Task 6.4)** touches 43+ files — needs care to avoid regressions. Recommended to batch alphabetically and run targeted pytest after each batch.
2. **DUP-003 + DUP-006 are NEEDS_REWORK** with narrower scope than originally claimed (verification found ~50% overlap not ~70%; one file in DUP-006 was unrelated to the modifier domain). Don't force consolidation beyond the verified scope.
3. **DUP-004 was REJECTED**: do not consolidate ShipInstance serializer files. The three files serve different contract layers (HP roundtrip vs dict schema vs adapter).
4. **CAT-6 brittleness rewrites** often require introducing dependency injection seams in production (Task 3.32 ActionTimeResolver injection, Task 3.20 public state-restore API). Those production changes need their own validation.

### Opportunities Discovered
- The `tests/fixtures/` directory is currently sparse but well-positioned to host the new shared fixture modules created by Phase 5 + Phase 6 (battle_panels.py, modifier_stubs.py, colonization_fixtures.py).
- Phase 4's CAT-7 sleep replacements give measurable CI-time wins (cumulative ~0.3s per run across the 3 files) at low risk.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
