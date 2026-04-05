# Phase 3 Checklist: Clean Up Component.__init__ and Formula Parsing
**Status:** Not Started

**Objective:** Fix formula parsing fragility and slim down __init__
**Estimated effort:** Simple (targeted refactor, small blast radius)

## Task 3.1: Write tests for formula parsing improvements [Simple]
**File:** `tests/unit/simulation/components/test_component_stats_calculator.py` (extend existing)
**Tests:** `pytest tests/unit/simulation/components/test_component_stats_calculator.py -v`

- [ ] Test `parse_formulas(data)` extracts formulas from `=`-prefixed string values
- [ ] Test `parse_formulas(data)` skips `_`-prefixed keys (like `_comment`)
- [ ] Test `parse_formulas(data)` strips leading `=` from formula string
- [ ] Test `apply_formula_defaults(component, formulas)` sets `base_mass=0, mass=0` for mass formula
- [ ] Test `apply_formula_defaults` sets `base_max_hp=0, max_hp=0, current_hp=0` for hp formula
- [ ] Test `apply_formula_defaults` sets `cost=0` for cost formula
- [ ] Test `apply_formula_defaults` is no-op for non-mass/hp/cost formulas
- [ ] Run tests -- confirm they FAIL

## Task 3.2: Move formula parsing into ComponentStatsCalculator [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`

Add static methods with a data-driven mapping:

```python
# Mapping: formula key -> list of (attribute_name, default_value) to set
FORMULA_DEFAULTS = {
    'mass': [('base_mass', 0), ('mass', 0)],
    'hp':   [('base_max_hp', 0), ('max_hp', 0), ('current_hp', 0)],
    'cost': [('cost', 0)],
}

@staticmethod
def parse_formulas(data: dict) -> dict[str, str]:
    """Extract formula definitions from component data.
    Returns dict mapping attribute name to formula string (without '=').
    """
    formulas = {}
    for key, value in data.items():
        if key.startswith('_'):
            continue
        if isinstance(value, str) and value.startswith("="):
            formulas[key] = value[1:]
    return formulas

@staticmethod
def apply_formula_defaults(component: 'Component', formulas: dict[str, str]) -> None:
    """Set safe default values for formula-driven attributes."""
    for key in formulas:
        if key in ComponentStatsCalculator.FORMULA_DEFAULTS:
            for attr, default in ComponentStatsCalculator.FORMULA_DEFAULTS[key]:
                setattr(component, attr, default)
```

- [ ] Add `FORMULA_DEFAULTS` mapping at class level
- [ ] Add `parse_formulas(data)` static method
- [ ] Add `apply_formula_defaults(component, formulas)` static method
- [ ] Run tests -- confirm they PASS

## Task 3.3: Simplify Component.__init__ [Simple]
**File:** `game/simulation/components/component.py`

Replace inline formula parsing (lines 183-199):
```python
# BEFORE (17 lines):
self.formulas = {}
for key, value in self.data.items():
    if key.startswith('_'):
        continue
    if isinstance(value, str) and value.startswith("="):
        self.formulas[key] = value[1:]
        if key in ['mass', 'hp', 'cost']:
            ...

# AFTER (2 lines):
self.formulas = ComponentStatsCalculator.parse_formulas(self.data)
ComponentStatsCalculator.apply_formula_defaults(self, self.formulas)
```

- [ ] Replace lines 183-199 with 2-line delegation to ComponentStatsCalculator
- [ ] Verify __init__ is now ~80 lines (down from 117)
- [ ] Run tests: `pytest tests/unit/entities/test_components.py -v`
- [ ] Run tests: `pytest tests/unit/simulation/components/test_component_stats_calculator.py -v`
**Notes:**
