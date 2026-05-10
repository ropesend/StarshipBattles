# PROJ-293 Habitability Factor Display Refactor — Research Findings

## Call Sites

`PreferenceRow.format_value()` is called at:
- game/ui/widgets/preference_row.py:157 (setpoint label, init)
- game/ui/widgets/preference_row.py:182 (tolerance label, init)
- game/ui/widgets/preference_row.py:218 (setpoint label, refresh)
- game/ui/widgets/preference_row.py:220 (tolerance label, refresh)
- game/ui/widgets/preference_row.py:230 (setpoint label, set_preference)
- game/ui/widgets/preference_row.py:232 (tolerance label, set_preference)

`PreferenceRow.calculate_factor_cost()` is called at:
- game/ui/widgets/preference_row.py:190 (cost label, init)
- game/ui/widgets/preference_row.py:222 (cost label, refresh)
- game/ui/widgets/preference_row.py:235 (cost label, set_preference)

## Registry Fields

`HabitabilityFactor` (frozen dataclass, line 44) stores:
- `id`: canonical factor id
- `unit`: storage unit string ("Pa", "K", "m/s^2", "fraction", "earth_equiv", "shielding")
- `display_scale`: float multiplier for UI display (0.001 for Pa→kPa, 1/9.81 for gravity, 100.0 for water percentage, 1.0 for others)

All 17 factors in `FACTOR_REGISTRY` (line 328) carry these fields.

## Factor Inventory

**Scalar factors** (7 items, lines 143–248):
1. gravity: unit="m/s^2", display_scale=1/9.81
2. temperature: unit="K", display_scale=1.0
3. water: unit="fraction", display_scale=100.0
4. pressure: unit="Pa", display_scale=0.001
5. tectonic: unit="fraction", display_scale=1.0
6. magnetic: unit="earth_equiv", display_scale=1.0
7. radiation: unit="shielding", display_scale=1.0

**Gas factors** (10 items, built dynamically lines 281–320):
- O2, N2, CO2, H2O, CH4, H2, He, Ar, NH3, SO2
- All use: unit="Pa", display_scale=0.001

All factors registered in `FACTOR_REGISTRY` dict (line 328–330).

## Other Sized Widgets

`_SETPOINT_LABEL_WIDTH` and `_TOLERANCE_LABEL_WIDTH` (60px each, lines 45–46) are used only in `PreferenceRow._build_widgets()` to size two UILabel instances:
- setpoint_label (line 155–160)
- tolerance_label (line 180–185)

No other widgets reference these constants. However, `_NAME_WIDTH`, `_COST_WIDTH`, `_SLIDER_HEIGHT`, `_LABEL_HEIGHT`, and `_GAP` are also defined (lines 44–50) and used in the same widget layout.

## Test Coverage

**test_preference_row.py** (tests/unit/ui/widgets/):
- `TestPreferenceRowConstruction` (line 88): constructs for scalar/gas factors
- `TestDisplayScaling` (line 176): pressure→kPa, gravity→g, water→%, temperature→K (calls `format_value()` directly at lines 194, 202, 211, 220)
- `TestOnChangeCallback` (line 230): fires callback on slider changes
- `TestCostLabel` (line 298): exponential cost via `calculate_factor_cost()` (lines 305, 320, 333, 347)
- `TestCostLabelLiveUpdate` (line 351): cost label updates (line 378 calls `refresh_from_sliders()`)

**test_habitability_factors.py** (tests/unit/strategy/data/):
- `TestGasFactorWeights` (line 148): checks unit="Pa" and display_scale=0.001 for all gases (lines 160–163)
- `TestRegistryShape` (line 32): validates all 17 factors present, weights, steps, extractors, scorers
- Tests do NOT call `format_value()` or validate display output strings

## Budget Display

`RacePointBudget` (game/strategy/data/race_point_budget.py) handles race-point cost calculations. The per-factor cost display is delegated to `PreferenceRow.calculate_factor_cost()`, which mirrors the exponential cost model (`2^steps - 1`). Cost labels are rendered in `PreferenceRow` (lines 188–193, 222, 235) as plain integer strings ("0p", "1p", "7p") — no formatting complexity. No separate budget display widget shows formatted factor values; cost is points only.

## Dataclass Schema

`HabitabilityFactor` (line 44):
- **Frozen**: `@dataclass(frozen=True)` — instances are immutable
- **Fields** (12 total, lines 66–77):
  - id, display_name, unit, display_scale, weight
  - default_setpoint, default_tolerance, min_value, max_value, step
  - extractor (callable), scorer (callable)
- **No subclasses or dynamic instantiation outside registry** — all instances built in `_SCALAR_FACTORS` tuple (line 143) and `_GAS_FACTORS` via `_build_gas_factors()` (line 281), then merged into `FACTOR_REGISTRY` dict (line 328)
- **Impact**: Frozen status means adding a field requires careful backward-compat; adding data (new factors) requires only registry edits.
