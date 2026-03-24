# FEAT-06: Populate Treasury Construction Queue Expenses (Split by Ships and Complexes)

## Description
The Treasury view's "Resource Expenses Per Turn" section has a "Construction Queues" line that currently shows 0 for all resources. This line should be replaced with two separate expense lines:

1. **Construction Queues (Ships)** — total resources planned to be spent next turn on ship/fighter/satellite construction across all queues
2. **Construction Queues (Complexes)** — total resources planned to be spent next turn on planetary complex construction across all queues

The calculation should iterate through each construction queue, determine what items will be actively built during the next turn based on available production capacity, classify each by type (using the existing `type` field on queue items), and sum the resource expenditures into the respective category.

The `construction_expenses` field in `EmpireEconomyCalculator` (`game/strategy/engine/empire_economy_calculator.py`) is currently a placeholder set to zero. Queue items already carry a `type` field (`"ship"`, `"fighter"`, `"satellite"`, `"complex"`) so the categorization infrastructure exists.

Note: This feature depends on accurate per-item next-turn calculations (see BUG-98) — the same distribution logic needed there will feed into this aggregate.

### Screenshot

Treasury page showing Construction Queues at 0 for all resources despite active build queues:
[![Treasury view showing Construction Queues expense line at 0 across all five resource types, despite ships being actively queued for construction](../../Tools/qa_observer/session_data/20260322_051459/images/bug_capture_052539.png)](../../Tools/qa_observer/session_data/20260322_051459/images/bug_capture_052539.png)

## Priority
Medium

## Status
Awaiting Confirmation

## Analysis Report

### Architecture Impact

**Layers affected:** Strategy Engine (primary), UI (minor display change)

**Data flow:** Construction queues exist in three locations, all accessible from `EmpireEconomyCalculator`:
- `empire.colonies[].construction_queue` — planet base queues (complexes only)
- `empire.colonies[].facilities[].construction_queue` — shipyard facility queues (ships + complexes)
- `empire.fleets[].construction_queue` — fleet space yard queues (ships + complexes)

**Key files:**
| File | Role | Change needed |
|------|------|---------------|
| `game/strategy/engine/empire_economy_calculator.py` | Economy calculator with placeholder at line 114 | Add `_calculate_construction_expenses()` method, split snapshot fields |
| `game/ui/panels/empire_treasury_panel.py` | Treasury display, line 265 shows single "Construction Queues" row | Split into two rows |
| `game/ui/screens/empire_panel_window.py` | Instantiates calculator at line 189 | No changes needed |
| `game/strategy/data/build_queue_source.py` | Queue discovery utilities, production rate resolution | Reuse existing functions |

**Queue items already carry all needed data:**
- `type`: `"ship"` | `"fighter"` | `"satellite"` | `"complex"`
- `total_cost`: `Dict[str, float]` — full resource cost per item
- `resources_consumed`: `Dict[str, float]` — amount already spent

**No cross-layer violations:** Calculator stays in Strategy layer; UI reads snapshot via existing DTO path. No facade changes needed (economy data bypasses facade — UI instantiates calculator directly).

### Dependency Map

**Direct references to `construction_expenses`:**
- `empire_economy_calculator.py:47` — field definition in `EmpireEconomySnapshot`
- `empire_economy_calculator.py:114` — placeholder set to zero
- `empire_economy_calculator.py:117` — included in `total_expenses` aggregation
- `empire_treasury_panel.py:265` — displayed as "Construction Queues" row
- `test_empire_economy_calculator.py:472` — placeholder test verifying it's zero
- `test_empire_treasury_panel.py:47,212` — test fixture and row structure test

**Blast radius:** 2 production files + 2-3 test files (~5 files total)

### Similar Patterns Found

**Maintenance expense aggregation** (`empire_economy_calculator.py:175-224`) is the direct template:
1. Initialize zero-dict for each resource
2. Iterate `empire.colonies` → facilities and `empire.fleets` → ships
3. Calculate cost per entity via helper
4. Aggregate by summing resource amounts
5. Return totals dict

**Per-turn spend calculation** already exists in `game/ui/screens/build_queue_helpers.py:48-104` — `calculate_per_turn_spend(queue_item, build_rate)` uses limiting-resource formula to determine next-turn expenditure per item.

**Production rate resolution** already exists in `game/strategy/data/build_queue_source.py`:
- `get_default_production_rates(yard_type)` — base rates from JSON
- `_get_facility_production_rates(facility)` — facility-specific rates

### Scope Assessment

**Complexity Rating: Moderate**
- 2 production files modified, 1 layer (Strategy), existing patterns, ~70-90 LOC new production code
- Uses existing queue infrastructure, type fields, and cost data
- Follows established maintenance aggregation pattern exactly

**Feature vs Project: FEATURE** — Single-phase, single-layer, no new abstractions, no refactoring needed.

**BUG-98 dependency assessment:** BUG-98 fixes per-item UI display in the build queue window. FEAT-06 performs aggregate calculation using the same formula but is independent — it can proceed without BUG-98. Both use the limiting-resource formula from `calculate_per_turn_spend()`.

## Requirements Context

**Cost Scope:** Per-turn spend (not total queued cost). Show what will actually be consumed next turn based on production rates and the limiting-resource formula.

**Queue Depth:** All items that will be worked on during the next turn, not just the head. If item 1 completes mid-turn, remaining production capacity carries over to item 2 (and potentially item 3, etc.). This is the same sequential carry-over logic ProductionEngine uses in `_process_queue_tick_dynamic()`.

**Budgeting Impact:** Construction expenses must factor into `total_expenses` and `net_resources` calculations, not just display. This means the Treasury's net resource projection will account for construction costs.

**Iteration:** Full implementation from the start — per-turn rate-based calculation with queue-level distribution, no simplified intermediate step.

**BUG-98 Relationship:** BUG-98 needs a queue-level distribution function (replacing per-item `calculate_per_turn_spend()`). FEAT-06 needs the same function to aggregate expenses. The queue-walk distribution logic should be implemented as a shared utility that both BUG-98 and FEAT-06 can use.

## Complexity Assessment

| Criterion | Assessment |
|-----------|------------|
| Lines of Code Affected | ~120-150 new production LOC |
| Files Requiring Changes | 3 production files + 2-3 test files |
| New Abstractions Needed | 1 — queue-level distribution function (shared with BUG-98) |
| Test Infrastructure | Existing test patterns sufficient |
| Cross-Layer Changes | No — Strategy only + minor UI display |

**Rating: Moderate** — 3 files, 1 layer (Strategy + minor UI), one new shared utility, 120-150 LOC.

## Implementation Strategy

### Sub-task 1: Queue-Level Distribution Function (shared utility)
**File:** `game/strategy/engine/construction_forecast.py` (new)
- Implement `forecast_queue_turn_spend(queue: List[Dict], build_rate: Dict) -> List[Dict[str, float]]`
- Walks the queue sequentially with carry-over capacity (mirroring ProductionEngine's tick loop)
- For each item: calculates remaining cost, determines ticks needed via limiting-resource formula, spends min(remaining_capacity, ticks_needed), records per-item spend, carries over remaining capacity
- Returns list of per-item spend dicts indexed by queue position
- This function serves both FEAT-06 (aggregate) and BUG-98 (per-item display)
- **Tests first** in `tests/unit/strategy/engine/test_construction_forecast.py`

### Sub-task 2: EmpireEconomySnapshot Split
**File:** `game/strategy/engine/empire_economy_calculator.py`
- Replace `construction_expenses` field with two new fields:
  - `construction_expenses_ships: Dict[str, float]`
  - `construction_expenses_complexes: Dict[str, float]`
- Update `total_expenses` calculation to include both
- Update `net_resources` calculation (already derived from total_expenses)

### Sub-task 3: Construction Expense Aggregation Method
**File:** `game/strategy/engine/empire_economy_calculator.py`
- Add `_aggregate_construction_expenses(empire)` method
- Iterate all queues (planet base, facility, fleet) using same access pattern as ProductionEngine
- Resolve production rates per queue using `get_default_production_rates()` and `_get_facility_production_rates()`
- Call `forecast_queue_turn_spend()` for each queue
- Classify each item's spend by type (ship/fighter/satellite → ships, complex → complexes)
- Sum into two totals dicts
- **Tests** in existing `tests/unit/strategy/engine/test_empire_economy_calculator.py`

### Sub-task 4: Treasury Panel Display Update
**File:** `game/ui/panels/empire_treasury_panel.py`
- Update `_get_expense_rows()` to show two rows instead of one:
  - "Construction Queues (Ships)" → `snapshot.construction_expenses_ships`
  - "Construction Queues (Complexes)" → `snapshot.construction_expenses_complexes`
- **Tests** in `tests/unit/ui/panels/test_empire_treasury_panel.py`

### Implementation Order
1. Sub-task 1 (shared utility) — foundation, independently testable
2. Sub-task 2 (snapshot structure) — minimal change, enables sub-task 3
3. Sub-task 3 (aggregation logic) — core feature logic
4. Sub-task 4 (UI display) — final presentation layer

## Work Log
- 2026-03-22: Created from QA Session 20260322_051459.
- 2026-03-22: Deep dive Phase 1 complete — agent swarm analysis. Feature rated Moderate complexity, implementable within feature track.
- 2026-03-22: Deep dive Phase 2-4 complete — user interview, complexity assessment, implementation strategy. Key decisions: per-turn spend with queue-level distribution, all active items included, affects budgeting (net_resources). Shared utility with BUG-98 for queue-walk logic.
- 2026-03-22: Implementation complete. All 4 sub-tasks done. 49 tests passing (13 forecast + 21 calculator + 15 treasury panel).

### Files Changed
- **NEW** `game/strategy/engine/construction_forecast.py` — Queue-level distribution function `forecast_queue_turn_spend()`
- **NEW** `tests/unit/strategy/engine/test_construction_forecast.py` — 13 tests for forecast function
- **MODIFIED** `game/strategy/engine/empire_economy_calculator.py` — Split `construction_expenses` into `construction_expenses_ships`/`construction_expenses_complexes`, added `_aggregate_construction_expenses()` method, updated `total_expenses` and `net_resources` calculations
- **MODIFIED** `game/ui/panels/empire_treasury_panel.py` — Split single "Construction Queues" row into "Construction Queues (Ships)" and "Construction Queues (Complexes)"
- **MODIFIED** `tests/unit/strategy/engine/test_empire_economy_calculator.py` — Updated mocks for `construction_queue`, added 6 new tests in `TestConstructionExpenses` class
- **MODIFIED** `tests/unit/ui/panels/test_empire_treasury_panel.py` — Updated fixture and row structure test for new split fields
