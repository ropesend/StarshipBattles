# Phase 5: Aptitudes Tab & Point-Buy System [Complex]

**Objective:** Build the point-buy aptitude system with budget tracking
**Tests:** `pytest tests/unit/strategy/data/test_race_point_budget.py tests/unit/ui/panels/test_race_aptitudes_panel.py -v`

---

## Task 5.1: Create RacePointBudget Class [Medium]
**File:** `game/strategy/data/race_point_budget.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_race_point_budget.py -v`

- [x] Create `RacePointBudget` class with:
  - `total_budget: int` (default 100)
  - `aptitude_base: int = 5` (default value for each aptitude, costs nothing)
- [x] Implement `calculate_aptitude_cost(race_config: RaceConfig) -> int`:
  - For each aptitude: cost = value - aptitude_base points (linear, can be negative for refund)
  - Sum all aptitude costs
- [x] Implement `calculate_tolerance_cost(race_config: RaceConfig) -> int`:
  - For gravity_tolerance: cost based on tolerance steps from minimum (0.0)
  - For temperature_tolerance: cost based on tolerance steps from minimum (0)
  - For water_tolerance: cost based on tolerance steps from minimum (0.0)
  - For radiation (abs from 0): tolerance cost
  - For each atmosphere gas: tolerance cost based on abs(value) from 0
  - Each step costs 2^step_number (doubling: 1, 2, 4, 8, 16...)
  - Define step sizes: gravity=0.1g per step, temp=10K per step, water=0.1 per step, radiation=10 per step, atmosphere=10 per step
- [x] Implement `calculate_total_cost(race_config: RaceConfig) -> int`:
  - Returns aptitude_cost + tolerance_cost
- [x] Implement `get_remaining_points(race_config: RaceConfig) -> int`:
  - Returns total_budget - total_cost
- [x] Implement `is_within_budget(race_config: RaceConfig) -> bool`:
  - Returns remaining_points >= 0
- [x] Write test: `test_default_aptitudes_cost_zero` (all at base=5 → 0 cost)
- [x] Write test: `test_aptitude_cost_one_above_base` (one stat at 6 → 1 cost)
- [x] Write test: `test_aptitude_cost_one_below_base` (one stat at 4 → -1 cost refund)
- [x] Write test: `test_aptitude_cost_multiple_stats` (3 stats at 8 → 9 cost)
- [x] Write test: `test_tolerance_cost_zero_tolerance` (all at 0 → 0 cost)
- [x] Write test: `test_tolerance_cost_one_step` (gravity_tolerance=0.1 → 1 cost)
- [x] Write test: `test_tolerance_cost_doubling` (gravity_tolerance=0.3 → 1+2+4=7 cost)
- [x] Write test: `test_tolerance_cost_exponential_growth` (verify 2^n pattern)
- [x] Write test: `test_total_cost_combines_aptitudes_and_tolerance`
- [x] Write test: `test_within_budget_default_config` (default → within budget)
- [x] Write test: `test_over_budget_detection` (maxed everything → over budget)
- [x] Write test: `test_remaining_points_calculation`
- [x] Run tests: all 25 tests pass
**Notes:** The 2^n curve makes broad tolerance very expensive. A race that tolerates everything would cost enormous points, forcing specialization. Aptitude costs can be negative (lowering a stat refunds points).

---

## Task 5.2: Create RaceAptitudesPanel Class [Medium]
**File:** `game/ui/panels/race_aptitudes_panel.py` (NEW)
**Tests:** `pytest tests/unit/ui/panels/test_race_aptitudes_panel.py -v`

- [x] Create `RaceAptitudesPanel` class following extracted panel pattern
- [x] Constructor: `__init__(self, panel, manager, race_config)` — stores references, creates RacePointBudget
- [x] Create budget display section at top:
  - Large label: "Points Remaining: X / 100"
  - Color-coded: green if >=20%, yellow if >=0%, red if <0%
- [x] Create aptitude sliders section (9 sliders):
  - Each: Name label | Slider (1-10, start=5, increment=1) | Value label | Cost label
  - Names: Strength, Intelligence, Constitution, Dexterity, Species Tolerance, Cooperation, Happiness, Population Growth, Conflict Tolerance
- [x] Create tolerance cost display section:
  - Label showing total tolerance cost from environment tab settings
  - Read-only — tolerance values are set on Environment tab, cost is displayed here
- [x] Store all slider and label references
- [x] Write test: `test_aptitudes_panel_creates_successfully`
- [x] Write test: `test_aptitudes_panel_has_9_sliders`
- [x] Write test: `test_aptitudes_panel_has_budget_display`
- [x] Write test: `test_aptitudes_panel_default_shows_budget`
- [x] Run tests: all pass
**Notes:** Tolerance cost is READ-ONLY on this panel — it shows the cost from Environment tab choices. Aptitude sliders are the adjustable part.

---

## Task 5.3: Implement Data Synchronization & Budget Tracking [Medium]
**File:** `game/ui/panels/race_aptitudes_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_aptitudes_panel.py -v -k "config or budget"`

- [x] Implement `update_config()`: reads slider values → writes to race_config aptitude fields
- [x] Implement `set_from_config()`: reads race_config → sets slider values
- [x] Implement `update_labels()`: updates value labels and cost labels for each aptitude
- [x] Implement `update_budget_display()`: recalculates and displays remaining points
  - Call RacePointBudget.get_remaining_points(race_config)
  - Update color based on remaining (green/yellow/red)
  - Update text with current/total
- [x] Budget display should update whenever any slider moves
- [x] Write test: `test_update_config_reads_aptitude_sliders`
- [x] Write test: `test_set_from_config_sets_aptitude_sliders`
- [x] Write test: `test_update_budget_display_shows_remaining`
- [x] Write test: `test_budget_display_red_when_over`
- [x] Write test: `test_budget_display_green_when_under`
- [x] Run tests: all pass
**Notes:** All 17 panel tests pass.

---

## Phase 5 Completion Checklist
- [x] All tasks above checked off
- [x] Run `pytest tests/unit/strategy/data/test_race_point_budget.py -v` — 25 tests pass
- [x] Run `pytest tests/unit/ui/panels/test_race_aptitudes_panel.py -v` — 17 tests pass
- [x] Run `pytest tests/ --testmon` — no new regressions (3 pre-existing failures)
- [x] Point budget math is correct (verified by unit tests)
- [x] Panel displays budget correctly with cost breakdown
