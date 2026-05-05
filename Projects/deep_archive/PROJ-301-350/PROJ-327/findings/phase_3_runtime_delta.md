# PROJ-327 Phase 3 — DUP-001 + HLP-001 Re-judgment

**Date:** 2026-05-04
**Branch:** `feat/03c-phase-aware-execution`

## Disposition summary

| PROJ-322 Task | Item | Outcome |
|---|---|---|
| 6.1 | DUP-001 — superweapon handler factory (5 handlers × 2 contracts) | **RE-CONFIRMED DEFERRED** |
| 6.4 | HLP-001 — `make_mock_ship` 4-shape consolidation | **RE-CONFIRMED DEFERRED** |

## Task 3.1 — DUP-001 measurement + decision

**Files:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py` (633 LOC, 24 tests) + `tests/unit/strategy/engine/test_superweapon_handler_validation.py` (251 LOC, 15 tests).

**Combined runtime:** 1.73 s wall-clock for 39 tests in one process (amortized import). Per `pytest --durations=10`:
- First-import setup costs: 4 tests at ~0.42 s each (~1.68 s) — one-time `superweapon_command_handlers` import + Mock construction.
- Steady-state setup: ~0.05 s per subsequent test (mostly Mock fixture construction across `mock_fleet`, `mock_planet`, `mock_galaxy`, `mock_session`).

**Construction-vs-body split:** ~3.6 s is the **sum** of individually-measured per-test setup times (each measurement includes the redundant import cost — not additive in a single run). The 39 tests share ~1.73 s combined wall-clock when run in one process (import amortized). Test-body time is sub-millisecond per test, so within that 1.73 s, fixture construction still dominates over body execution. The decision to re-confirm DUP-001 as deferred remains valid — it rests on the mutation-surface reasoning in Task 3.1's "Why a shared session fixture STILL doesn't help" section, not on the misstated 3.6 s magnitude.

**Why a shared session fixture STILL doesn't help:**
- Every test calls `handler.execute(mock_session, cmd)` which mutates `mock_fleet.orders` (appends an Order) and records calls on `mock_session._get_fleet_by_id`/`_get_planet_by_id`. Sharing the session between tests requires resetting `mock_fleet.orders = []`, `mock_fleet.path = []`, AND clearing call records on every test — equivalent cost to constructing a fresh fixture, with added risk that one missed reset leaks into later tests.
- 2 tests reassign `mock_fleet.ships = [Mock(id=1), Mock(id=2)]`.
- 2 tests reassign `mock_session._get_fleet_by_id.return_value = None` to test the not-found path. These reassignments would persist into later tests under any rescope without a per-test reset.

**Builder-pattern factory (the original DUP-001 proposal):** The 5+ handlers × 2 contracts (execution mock with empty ships vs DI-validation mock with ships=[Mock(id=1)] + a `mock_component_registry`) still resolves to a switch-statement factory. The two file shapes are genuinely distinct: validation needs `session.registries.components` populated; execution doesn't. A `params=[...]` factory with two factory functions absorbs the shape only by hiding it behind a discriminator — readability cost > LOC win.

**Decision:** RE-CONFIRMED DEFERRED. Original PROJ-322 rationale stands with new measurement context. Per Decision D-006 this is a valid outcome.

## Task 3.2 — HLP-001 measurement + decision

**Files:** `tests/unit/ui/screens/test_fleet_report_filters.py` (61 tests, 1.99 s); `tests/unit/strategy/data/test_fleet_cargo_resources.py`, `tests/unit/strategy/engine/test_resupply_engine.py`, `tests/unit/strategy/facade/test_strategy_session_facade.py` (combined 72 tests, 1.98 s).

**`make_mock_ship` microbenchmark:** 10 000 calls in 6.27 s = **~627 µs/call**.

**Per-file overhead from `make_mock_ship`:** 115 calls in `test_fleet_report_filters.py` × 627 µs = **~72 ms total** (~3.6% of file runtime). Other 3 files use distinct `_make_*` helpers, each with their own per-file overhead but lower call counts.

**Memoization hot-path analysis:** Inspected actual call signatures across the 4 files:
- `test_fleet_cargo_resources.py::_make_ship(cargo_capacity, cargo_contents)` — handled by DUP-003 `cargo_mock_ship` (already factored in PROJ-322 pass 2).
- `test_resupply_engine.py::_make_mock_ship(fuel_capacity, current_fuel, fuel_cost_per_hex)` — distinct surface (fuel-bearing).
- `test_fleet_report_filters.py::make_mock_ship(serial, design_name, hp_pct, is_alive, is_derelict, is_damaged, mass, max_fuel, current_fuel, max_energy, current_energy, warp_tonnage)` — display-bound 11+ params.
- `test_strategy_session_facade.py` — facade-bound mocks (per PROJ-322 phase_2 Task 2.9 deferral text).

No two files share an overlapping shape. A blanket `make_mock_ship` would still be the kitchen-sink builder rejected by PROJ-322. Memoization (`functools.lru_cache` keyed on a frozenset) would cap at ~50 ms reclaim per file (cache hit + deepcopy-on-retrieval to avoid mutation pollution), and would only help `test_fleet_report_filters.py` because the other files already have file-local helpers that don't share shape with it.

**Decision:** RE-CONFIRMED DEFERRED. Construction overhead is small (~3.6%); the disparate shapes don't warrant a builder; memoization gain is marginal and complexity-positive. Per Decision D-006 this is a valid outcome.

## Task 3.3 — Cumulative delta

Phase 3 produces **ZERO runtime change** (no code changes; both items re-confirmed deferred). The work product is the captured measurement + dispositions in:
- `Projects/active_projects/PROJ-322/phase_6_checklist.md` (Tasks 6.1 + 6.4 annotated with re-judgment rationale)
- This file

Phase 3's tech-debt reduction win: **the deferred items are now formally closed with measurement evidence.** Future audits won't re-litigate these from scratch — they'll see the measurement and the disposition trail. That's the maintainability win per user priority order.

## Combined Phase 2 + Phase 3 reclaim

Per-file (single-process):
- Phase 2: ~330 ms (~12% on test_ship_io, ~3% on test_empire_treasury_panel, 0% elsewhere).
- Phase 3: 0 ms.
- **Total reclaim: ~330 ms across 4 files** (single-process; sharded reclaim will be smaller because shards balance load).

Sharded suite measurement is deferred to Phase 5 per the project plan.

## Combined readability / maintainability win

- 7 PROJ-322 deferrals are now dispositioned (5 from Phase 2, 2 from Phase 3) with up-to-date rationale captured **both in the test files themselves** (where future contributors will see them at edit time) **and in the PROJ-322 checklists** (where future audits will see them).
- 2 fixture rescopes landed (test_empire_treasury_panel.py, test_ship_io.py) with explicit scope-justification comments.
- 1 dead-code helper (`minimal_ship`) removed.
- 5 re-confirmation rationales reflect actual re-audit + measurement, not "carried over from PROJ-322".

Per user priority order (readability > maintainability > functionality > runtime), the primary deliverable is the disposition + rationale capture. The 330 ms runtime reclaim is the bonus.
