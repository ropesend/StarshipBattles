# Phase 5: Aptitudes Tab & Point-Buy System [Complex]

**Objective:** Build the point-buy aptitude system with budget tracking
**Tests:** `pytest tests/unit/strategy/data/test_race_point_budget.py tests/unit/ui/panels/test_race_aptitudes_panel.py -v`

---

## Task 5.1: Create RacePointBudget Class [Medium]
**File:** `game/strategy/data/race_point_budget.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_race_point_budget.py -v`

- [ ] Create `RacePointBudget` class with:
  - `total_budget: int` (default 100)
  - `aptitude_base: int = 5` (default value for each aptitude, costs nothing)
- [ ] Implement `calculate_aptitude_cost(race_config: RaceConfig) -> int`:
  - For each aptitude: cost = abs(value - aptitude_base) points (linear, 1 point per step from base)
  - Sum all aptitude costs
- [ ] Implement `calculate_tolerance_cost(race_config: RaceConfig) -> int`:
  - For gravity_tolerance: cost based on tolerance steps from minimum (0.0)
  - For temperature_tolerance: cost based on tolerance steps from minimum (0)
  - For water_tolerance: cost based on tolerance steps from minimum (0.0)
  - For radiation (abs from 0): tolerance cost
  - For each atmosphere gas: tolerance cost based on abs(value) from 0
  - Each step costs 2^step_number (doubling: 1, 2, 4, 8, 16...)
  - Define step sizes: gravity=0.1g per step, temp=10K per step, water=0.1 per step, radiation=10 per step, atmosphere=10 per step
- [ ] Implement `calculate_total_cost(race_config: RaceConfig) -> int`:
  - Returns aptitude_cost + tolerance_cost
- [ ] Implement `get_remaining_points(race_config: RaceConfig) -> int`:
  - Returns total_budget - total_cost
- [ ] Implement `is_within_budget(race_config: RaceConfig) -> bool`:
  - Returns remaining_points >= 0
- [ ] Write test: `test_default_aptitudes_cost_zero` (all at base=5 → 0 cost)
- [ ] Write test: `test_aptitude_cost_one_above_base` (one stat at 6 → 1 cost)
- [ ] Write test: `test_aptitude_cost_one_below_base` (one stat at 4 → 1 cost)
- [ ] Write test: `test_aptitude_cost_multiple_stats` (3 stats at 8 → 9 cost)
- [ ] Write test: `test_tolerance_cost_zero_tolerance` (all at 0 → 0 cost)
- [ ] Write test: `test_tolerance_cost_one_step` (gravity_tolerance=0.1 → 1 cost)
- [ ] Write test: `test_tolerance_cost_doubling` (gravity_tolerance=0.3 → 1+2+4=7 cost)
- [ ] Write test: `test_tolerance_cost_exponential_growth` (verify 2^n pattern)
- [ ] Write test: `test_total_cost_combines_aptitudes_and_tolerance`
- [ ] Write test: `test_within_budget_default_config` (default → within budget)
- [ ] Write test: `test_over_budget_detection` (maxed everything → over budget)
- [ ] Write test: `test_remaining_points_calculation`
- [ ] Run tests: all pass
**Notes:** The 2^n curve makes broad tolerance very expensive. A race that tolerates everything would cost enormous points, forcing specialization.

---

## Task 5.2: Create RaceAptitudesPanel Class [Medium]
**File:** `game/ui/panels/race_aptitudes_panel.py` (NEW)
**Tests:** `pytest tests/unit/ui/panels/test_race_aptitudes_panel.py -v`

- [ ] Create `RaceAptitudesPanel` class following extracted panel pattern
- [ ] Constructor: `__init__(self, panel, manager, race_config)` — stores references, creates RacePointBudget
- [ ] Create budget display section at top:
  - Large label: "Points Remaining: X / 100"
  - Color-coded: green if >=20%, yellow if >=0%, red if <0%
- [ ] Create aptitude sliders section (9 sliders):
  - Each: Name label | Slider (1-10, start=5, increment=1) | Value label | Cost label
  - Names: Strength, Intelligence, Constitution, Dexterity, Species Tolerance, Cooperation, Happiness, Population Growth, Conflict Tolerance
- [ ] Create tolerance cost display section:
  - Label showing total tolerance cost from environment tab settings
  - Read-only — tolerance values are set on Environment tab, cost is displayed here
- [ ] Store all slider and label references
- [ ] Write test: `test_aptitudes_panel_creates_successfully`
- [ ] Write test: `test_aptitudes_panel_has_9_sliders`
- [ ] Write test: `test_aptitudes_panel_has_budget_display`
- [ ] Write test: `test_aptitudes_panel_default_shows_budget`
- [ ] Run tests: all pass
**Notes:** Tolerance cost is READ-ONLY on this panel — it shows the cost from Environment tab choices. Aptitude sliders are the adjustable part.

---

## Task 5.3: Implement Data Synchronization & Budget Tracking [Medium]
**File:** `game/ui/panels/race_aptitudes_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_aptitudes_panel.py -v -k "config or budget"`

- [ ] Implement `update_config()`: reads slider values → writes to race_config aptitude fields
- [ ] Implement `set_from_config()`: reads race_config → sets slider values
- [ ] Implement `update_labels()`: updates value labels and cost labels for each aptitude
- [ ] Implement `update_budget_display()`: recalculates and displays remaining points
  - Call RacePointBudget.get_remaining_points(race_config)
  - Update color based on remaining (green/yellow/red)
  - Update text with current/total
- [ ] Budget display should update whenever any slider moves
- [ ] Write test: `test_update_config_reads_aptitude_sliders`
- [ ] Write test: `test_set_from_config_sets_aptitude_sliders`
- [ ] Write test: `test_update_budget_display_shows_remaining`
- [ ] Write test: `test_budget_display_red_when_over`
- [ ] Write test: `test_budget_display_green_when_under`
- [ ] Run tests: all pass
**Notes:**

---

## Phase 5 Completion Checklist
- [ ] All tasks above checked off
- [ ] Run `pytest tests/unit/strategy/data/test_race_point_budget.py -v` — all pass
- [ ] Run `pytest tests/unit/ui/panels/test_race_aptitudes_panel.py -v` — all pass
- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] Point budget math is correct (verified by unit tests)
- [ ] Panel displays budget correctly with color coding
