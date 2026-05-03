# ABS-SIM: Simulation Abstraction Designer Report

## Summary
- **Total issues found:** 4
- **Critical:** 1, **Major:** 2, **Minor:** 1, **Info:** 0

---

## Prior Art Verification

The DRY-SIM-COMP report (CQ-001, CQ-002, CQ-004) and the consolidated review correctly identified
these clusters. Key refinements from this deep analysis:

1. **CQ-001 (value extraction)**: The prior art claimed 15+ classes need `_parse_primary_value()`.
   **Verified and corrected**: `_parse_primary_value()` already exists on the base class (added
   since the review). 11 call sites already use it. Only **1 class** (CrewRequired) still uses
   the legacy inline pattern. The remaining classes that use `isinstance(data, dict)` do so
   for **multi-field extraction** (not primary value), which is a different pattern entirely.

2. **CQ-002 (recalculate boilerplate)**: The prior art claimed 16+ identical recalculate() methods.
   **Verified**: 15 non-trivial recalculate() methods exist. Of those, **11 are simple
   base*mult**, **1 is base*mult with int()**, **1 uses int(base*mult) with capacity**, and
   **2 are complex** (CrewRequired uses sqrt+ceil, WeaponAbility uses multi-field+arc logic).

3. **CQ-004 (get_ui_rows boilerplate)**: The prior art claimed 20+ classes.
   **Verified**: Color constants were already consolidated to `ui_colors.py` (PROJ-167).
   The remaining boilerplate is the return format itself, which varies enough that a
   `SimpleMultiplierAbility` base class handles the common cases better than a UIRowBuilder.

---

## Findings

### CRITICAL: Remaining Legacy Value Extraction in CrewRequired

**ID:** ABS-SIM-001
**Location:** `game/simulation/components/abilities/crew.py:73`
**Issue:** CrewRequired is the **only** ability class that still uses the legacy inline value
extraction pattern instead of the base class `_parse_primary_value()`:

```python
# Current (crew.py:73) - LEGACY PATTERN
val = data if isinstance(data, (int, float)) else data.get('value', data.get('amount', 0))
self.amount = int(val)
```

This is the sole surviving instance of DUP-003 / CQ-001. All other ability classes have been
migrated to `_parse_primary_value()`.

**Impact:** Inconsistency -- CrewRequired accepts both `'value'` and `'amount'` keys, while
all other abilities only accept `'value'`. This creates a hidden behavior divergence that can
confuse data authors. If the intent is to support `'amount'` as an alias, this should be
explicit and documented, not buried in a one-off inline pattern.

**Proposed API:** Two options:

*Option A (simple -- use existing helper):*
```python
# If 'amount' alias is not intentional, just use _parse_primary_value:
self.amount = int(self._parse_primary_value(data))
```

*Option B (preserve 'amount' alias -- extend helper):*
```python
# In base.py, _parse_primary_value already supports custom keys:
val = self._parse_primary_value(data)  # tries 'value' key
if val == 0.0 and isinstance(data, dict) and 'amount' in data:
    val = float(data['amount'])
self.amount = int(val)
```

*Option C (cleanest -- add fallback_key parameter):*
```python
# Extend _parse_primary_value signature:
@staticmethod
def _parse_primary_value(data, key: str = 'value', default: float = 0.0,
                         fallback_keys: tuple = ()) -> float:
    if isinstance(data, (int, float)):
        return float(data)
    if isinstance(data, dict):
        val = data.get(key)
        if val is not None:
            return float(val)
        for fk in fallback_keys:
            val = data.get(fk)
            if val is not None:
                return float(val)
        return float(default)
    return float(default)

# Then in CrewRequired:
self.amount = int(self._parse_primary_value(data, fallback_keys=('amount',)))
```

**Before/After:**

*Before (crew.py, CrewRequired.__init__):*
```python
def __init__(self, component, data: Dict[str, Any]):
    super().__init__(component, data)
    val = data if isinstance(data, (int, float)) else data.get('value', data.get('amount', 0))
    self.amount = int(val)
    self._base_amount = self.amount
```

*After (Option A -- simplest, drops 'amount' alias):*
```python
def __init__(self, component, data: Dict[str, Any]):
    super().__init__(component, data)
    self.amount = int(self._parse_primary_value(data))
    self._base_amount = self.amount
```

*After (Option C -- preserves 'amount' alias):*
```python
def __init__(self, component, data: Dict[str, Any]):
    super().__init__(component, data)
    self.amount = int(self._parse_primary_value(data, fallback_keys=('amount',)))
    self._base_amount = self.amount
```

**Call Sites:** 1 location
- `game/simulation/components/abilities/crew.py:73`

**Lines Saved:** 1 line changed, no net lines saved (this is about consistency, not line count)

**Risk:** Low. If Option A is chosen, any component JSON using `"CrewRequired": {"amount": 5}`
instead of `"CrewRequired": {"value": 5}` or `"CrewRequired": 5` would break. Need to grep
component JSON data to verify no such usage exists.

**Category:** Quick Win
**Recommendation:** Grep component JSON for `"CrewRequired"` usage with `"amount"` key. If none
exist, use Option A. If some exist, use Option C.
**Effort:** Simple

---

### MAJOR: Introduce SimpleMultiplierAbility Base Class for recalculate() + get_ui_rows() + get_primary_value() Boilerplate

**ID:** ABS-SIM-002
**Location:** `game/simulation/components/abilities/` (defense.py, crew.py, propulsion.py, cargo.py, resources.py, harvester.py)
**Issue:** 11 ability classes follow the exact same pattern:

```python
class SomeAbility(Ability):
    STAT_BINDINGS = [AbilityStatBinding(StatKey.SOME_MULT, 'field', 'multiply', 'base_field')]

    def __init__(self, component, data):
        super().__init__(component, data)
        self.base_field = self._parse_primary_value(data)
        self.field = self.base_field

    def recalculate(self):
        self.field = self.base_field * self.get_effective_stat('some_mult', 1.0)

    def get_ui_rows(self):
        return [{'label': 'Label', 'value': f"{self.field:.0f}", 'color_hint': HINT_COLOR}]

    def get_primary_value(self) -> float:
        return self.field
```

Each class re-implements all 4 methods identically except for: field name, stat key, label text,
format string, and color hint. This is textbook class-attribute-driven configuration.

**Impact:** 11 classes * ~15 lines each = ~165 lines of boilerplate. Adding a new simple ability
requires copying 15+ lines of boilerplate and changing 5 values. Inconsistencies creep in (some
use `int()`, some use `float()`; some use `:.0f`, others `:.1f`).

**Categorization of ALL recalculate() methods:**

| # | Class | File:Line | Formula | Type Cast | Category |
|---|-------|-----------|---------|-----------|----------|
| 1 | ShieldProjection | defense.py:21 | `base_capacity * capacity_mult` | float | (a) simple |
| 2 | ShieldRegeneration | defense.py:45 | `base_rate * energy_gen_mult` | float | (a) simple |
| 3 | CombatPropulsion | propulsion.py:25 | `base_thrust * thrust_mult` | float | (a) simple |
| 4 | ManeuveringThruster | propulsion.py:52 | `base_turn_rate * turn_mult` | float | (a) simple |
| 5 | StrategicMovement | propulsion.py:97 | `base_movement_points * strategic_mult` | float | (a) simple |
| 6 | ResourceConsumption | resources.py:44 | `_base_amount * consumption_mult` | float | (a) simple |
| 7 | ResourceStorage | resources.py:179 | `_base_max_amount * capacity_mult` | float | (a) simple |
| 8 | ResourceGeneration | resources.py:219 | `_base_rate * energy_gen_mult` | float | (a) simple |
| 9 | CargoStorage | cargo.py:60 | `_base_capacity * capacity_mult` | float | (a) simple |
| 10 | EmpireStorageAbility | harvester.py:71 | `_base_capacity * storage_mult` | float | (a) simple |
| 11 | CrewCapacity | crew.py:20 | `int(_base_amount * crew_capacity_mult)` | int | (b) int-cast |
| 12 | LifeSupportCapacity | crew.py:42 | `int(_base_amount * life_support_capacity_mult)` | int | (b) int-cast |
| 13 | VehicleLaunchAbility | markers.py:24 | `int(_base_capacity * capacity_mult)` | int | (b) int-cast |
| 14 | CrewRequired | crew.py:77 | `int(ceil(_base * sqrt(mass_mult) * crew_req_mult))` | int+ceil+sqrt | (c) complex |
| 15 | WeaponAbility | weapons.py:152 | multi-field + arc_set/arc_add | float | (c) complex |
| 16 | BeamWeaponAbility | weapons.py:280 | super() + accuracy_add | float | (c) extends parent |
| 17 | SeekerWeaponAbility | weapons.py:352 | super() + 4 extra fields | float | (c) extends parent |

**Categories:**
- **(a) Simple base*mult (float):** 10 classes -- perfect candidates for SimpleMultiplierAbility
- **(b) Simple base*mult (int cast):** 3 classes -- candidates with `int_result = True` flag
- **(c) Complex:** 4 classes -- NOT candidates, keep custom recalculate()

**Categorization of ALL get_ui_rows() methods:**

| # | Class | File:Line | Pattern | Rows | Category |
|---|-------|-----------|---------|------|----------|
| 1 | ShieldProjection | defense.py:26 | `f"{self.capacity:.0f}"` | 1 | (a) simple single |
| 2 | ShieldRegeneration | defense.py:50 | `f"{self.rate:.1f}/s"` | 1 | (a) simple single |
| 3 | ToHitAttackModifier | defense.py:73 | sign prefix + `f"{sign}{val:.1f}"` | 1 | (d) custom logic |
| 4 | ToHitDefenseModifier | defense.py:95 | sign prefix + `f"{sign}{val:.1f}"` | 1 | (d) custom logic |
| 5 | EmissiveArmor | defense.py:117 | `f"{self.amount}"` | 1 | (a) simple single |
| 6 | CombatPropulsion | propulsion.py:28 | `f"{self.thrust_force:.0f} N"` | 1 | (a) simple single |
| 7 | ManeuveringThruster | propulsion.py:55 | `f"{self.turn_rate:.1f} deg/s"` | 1 | (a) simple single |
| 8 | StrategicMovement | propulsion.py:100 | `f"{self.movement_points:.0f} MP"` | 1 | (a) simple single |
| 9 | WarpJump | propulsion.py:149 | multiple conditional rows | 2-3 | (d) custom logic |
| 10 | CrewCapacity | crew.py:23 | `f"{self.amount}"` | 1 | (a) simple single |
| 11 | LifeSupportCapacity | crew.py:44 | `f"{self.amount}"` | 1 | (a) simple single |
| 12 | CrewRequired | crew.py:86 | `f"{self.amount}"` | 1 | (a) simple single |
| 13 | ResourceConsumption | resources.py:124 | conditional trigger/color | multi | (d) custom logic |
| 14 | ResourceStorage | resources.py:182 | conditional color | 1 | (d) custom logic |
| 15 | ResourceGeneration | resources.py:222 | conditional color | 1 | (d) custom logic |
| 16 | CargoStorage | cargo.py:64 | conditional type/color | 1 | (d) custom logic |
| 17 | EmpireStorageAbility | harvester.py:80 | 2 fixed rows | 2 | (d) multi-row |
| 18 | ResourceHarvesterAbility | harvester.py:30 | 2 fixed rows | 2 | (d) multi-row |
| 19 | SpaceShipyardAbility | harvester.py:117 | conditional rows | 2-3 | (d) custom logic |
| 20 | WeaponAbility | weapons.py:209 | 3 fixed rows | 3 | (d) multi-row |
| 21 | VehicleLaunchAbility | markers.py:39 | 2 fixed rows | 2 | (d) multi-row |
| 22-25 | Markers | markers.py:54,66,78,90 | fixed `'Yes'`/`'Active'` | 1 | (a) simple single |
| 26-31 | Superweapons (6) | superweapons.py | fixed `'Superweapon'` + name | 1 | (a) simple single |

**Simple single-row candidates:** 17 classes (including markers/superweapons)
Of these, **10 are simple multiplier abilities** that also have simple single-row UI.

**Proposed API:**

```python
# In game/simulation/components/abilities/base.py

class SimpleMultiplierAbility(Ability):
    """
    Base class for abilities with a single numeric value modified by one multiplier.

    Subclasses configure behavior via class attributes:
        - stat_key: The modifier stat key string (e.g. 'thrust_mult')
        - value_attr: Name of the current-value attribute (e.g. 'thrust_force')
        - base_attr: Name of the base-value attribute (e.g. 'base_thrust')
        - ui_label: Display label for get_ui_rows() (e.g. 'Thrust')
        - ui_format: Format string for the value (e.g. '{:.0f} N')
        - ui_color: Color hint constant (e.g. HINT_THRUST)
        - int_result: If True, cast result to int (default: False)
        - parse_key: Key to extract from dict data (default: 'value')

    Subclasses ONLY need to set class attributes and optionally define STAT_BINDINGS.
    All 4 boilerplate methods (__init__, recalculate, get_ui_rows, get_primary_value)
    are provided by this base class.
    """

    # --- REQUIRED class attributes (subclasses MUST override) ---
    stat_key: str = ''         # e.g. 'thrust_mult'
    value_attr: str = ''       # e.g. 'thrust_force'
    base_attr: str = ''        # e.g. 'base_thrust'
    ui_label: str = ''         # e.g. 'Thrust'
    ui_format: str = '{:.0f}'  # e.g. '{:.0f} N'
    ui_color: str = '#FFFFFF'  # e.g. HINT_THRUST

    # --- OPTIONAL class attributes ---
    int_result: bool = False   # Cast recalculate result to int
    parse_key: str = 'value'   # Key to extract from dict data

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        base_val = self._parse_primary_value(data, key=self.parse_key)
        if self.int_result:
            base_val = int(base_val)
        setattr(self, self.base_attr, base_val)
        setattr(self, self.value_attr, base_val)

    def sync_data(self, data: Any):
        super().sync_data(data)
        base_val = self._parse_primary_value(data, key=self.parse_key)
        if self.int_result:
            base_val = int(base_val)
        setattr(self, self.base_attr, base_val)
        setattr(self, self.value_attr, base_val)

    def recalculate(self) -> None:
        base = getattr(self, self.base_attr)
        mult = self.get_effective_stat(self.stat_key, 1.0)
        result = base * mult
        if self.int_result:
            result = int(result)
        setattr(self, self.value_attr, result)

    def get_ui_rows(self) -> List[Dict[str, str]]:
        val = getattr(self, self.value_attr)
        return [{'label': self.ui_label, 'value': self.ui_format.format(val), 'color_hint': self.ui_color}]

    def get_primary_value(self) -> float:
        val = getattr(self, self.value_attr)
        return float(val)
```

**Before/After Examples:**

**Example 1: ShieldProjection (defense.py)**

*Before (14 lines):*
```python
class ShieldProjection(Ability):
    """Provides Shield Capacity."""
    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CAPACITY_MULT, 'capacity', 'multiply', 'base_capacity'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.base_capacity = self._parse_primary_value(data)
        self.capacity = self.base_capacity

    def recalculate(self):
        mult = self.get_effective_stat('capacity_mult', 1.0)
        self.capacity = self.base_capacity * mult

    def get_ui_rows(self):
        return [{'label': 'Shield Cap', 'value': f"{self.capacity:.0f}", 'color_hint': HINT_SHIELD_CAP}]

    def get_primary_value(self) -> float:
        return self.capacity
```

*After (9 lines):*
```python
class ShieldProjection(SimpleMultiplierAbility):
    """Provides Shield Capacity."""
    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CAPACITY_MULT, 'capacity', 'multiply', 'base_capacity'),
    ]
    stat_key = 'capacity_mult'
    value_attr = 'capacity'
    base_attr = 'base_capacity'
    ui_label = 'Shield Cap'
    ui_format = '{:.0f}'
    ui_color = HINT_SHIELD_CAP
```

**Saves: 5 lines per class** (14 -> 9)

**Example 2: CombatPropulsion (propulsion.py)**

*Before (17 lines):*
```python
class CombatPropulsion(Ability):
    """Provides Thrust."""
    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.THRUST_MULT, 'thrust_force', 'multiply', 'base_thrust'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.base_thrust = self._parse_primary_value(data)
        self.thrust_force = self.base_thrust

    def sync_data(self, data: Any):
        super().sync_data(data)
        self.base_thrust = self._parse_primary_value(data)
        self.thrust_force = self.base_thrust

    def recalculate(self):
        self.thrust_force = self.base_thrust * self.get_effective_stat('thrust_mult', 1.0)

    def get_ui_rows(self):
        return [{'label': 'Thrust', 'value': f"{self.thrust_force:.0f} N", 'color_hint': HINT_THRUST}]

    def get_primary_value(self) -> float:
        return self.thrust_force
```

*After (10 lines):*
```python
class CombatPropulsion(SimpleMultiplierAbility):
    """Provides Thrust."""
    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.THRUST_MULT, 'thrust_force', 'multiply', 'base_thrust'),
    ]
    stat_key = 'thrust_mult'
    value_attr = 'thrust_force'
    base_attr = 'base_thrust'
    ui_label = 'Thrust'
    ui_format = '{:.0f} N'
    ui_color = HINT_THRUST
```

**Saves: 7 lines per class** (17 -> 10, removes sync_data too since base handles it)

**Example 3: CrewCapacity (crew.py, int result)**

*Before (13 lines):*
```python
class CrewCapacity(Ability):
    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CREW_CAPACITY_MULT, 'amount', 'multiply', '_base_amount'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.amount = int(self._parse_primary_value(data))
        self._base_amount = self.amount

    def recalculate(self):
        self.amount = int(self._base_amount * self.get_effective_stat('crew_capacity_mult', 1.0))

    def get_ui_rows(self):
        return [{'label': 'Crew Cap', 'value': f"{self.amount}", 'color_hint': HINT_CREW_CAP}]

    def get_primary_value(self) -> float:
        return float(self.amount)
```

*After (10 lines):*
```python
class CrewCapacity(SimpleMultiplierAbility):
    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CREW_CAPACITY_MULT, 'amount', 'multiply', '_base_amount'),
    ]
    stat_key = 'crew_capacity_mult'
    value_attr = 'amount'
    base_attr = '_base_amount'
    ui_label = 'Crew Cap'
    ui_format = '{}'
    ui_color = HINT_CREW_CAP
    int_result = True
```

**Saves: 3 lines per class** (13 -> 10)

**Complete Migration List:**

| # | Class | File | Can Migrate | Reason if No | Lines Saved |
|---|-------|------|-------------|--------------|-------------|
| 1 | ShieldProjection | defense.py | YES | | 5 |
| 2 | ShieldRegeneration | defense.py | YES | | 5 |
| 3 | CombatPropulsion | propulsion.py | YES | | 7 |
| 4 | ManeuveringThruster | propulsion.py | YES | | 7 |
| 5 | StrategicMovement | propulsion.py | YES | | 7 |
| 6 | ResourceConsumption | resources.py | NO | Multi-field init (resource, trigger); custom update() with resource registry | 0 |
| 7 | ResourceStorage | resources.py | NO | Multi-field init (resource_type); conditional UI color | 0 |
| 8 | ResourceGeneration | resources.py | NO | Multi-field init (resource_type); conditional UI color | 0 |
| 9 | CargoStorage | cargo.py | NO | Multi-field init (cargo_type); conditional UI label/color | 0 |
| 10 | EmpireStorageAbility | harvester.py | NO | Multi-field init (resource_type); multi-row UI | 0 |
| 11 | CrewCapacity | crew.py | YES | | 3 |
| 12 | LifeSupportCapacity | crew.py | YES | | 3 |
| 13 | VehicleLaunchAbility | markers.py | NO | Multi-field init (fighter_class, cycle_time); custom update(); multi-row UI | 0 |
| 14 | CrewRequired | crew.py | NO | Complex recalculate (sqrt + ceil + dual multiplier) | 0 |
| 15 | WeaponAbility | weapons.py | NO | Complex multi-field init + formula system + arc logic | 0 |
| 16 | BeamWeaponAbility | weapons.py | NO | Extends WeaponAbility with accuracy | 0 |
| 17 | SeekerWeaponAbility | weapons.py | NO | Extends WeaponAbility with seeker stats | 0 |
| 18 | ToHitAttackModifier | defense.py | NO | Custom UI (sign prefix); no recalculate | 0 |
| 19 | ToHitDefenseModifier | defense.py | NO | Custom UI (sign prefix); no recalculate | 0 |
| 20 | EmissiveArmor | defense.py | NO | No recalculate; int cast on init only | 0 |

**7 classes can migrate. Total lines saved: ~37 lines** (current ~105 -> target ~68 for these 7 classes)

Plus the base class adds ~30 lines, so net savings = ~7 lines. However, the **real value** is:
1. Adding new simple abilities becomes a 10-line class definition instead of 15-17 lines
2. Guaranteed consistency: recalculate/get_ui_rows/get_primary_value always follow the same pattern
3. sync_data() is automatically handled (currently 3 propulsion classes implement it manually)
4. No risk of forgetting to multiply by the stat key in recalculate()

**Call Sites:** 7 ability class files

| File | Classes |
|------|---------|
| `game/simulation/components/abilities/defense.py:9-31` | ShieldProjection |
| `game/simulation/components/abilities/defense.py:33-54` | ShieldRegeneration |
| `game/simulation/components/abilities/propulsion.py:8-32` | CombatPropulsion |
| `game/simulation/components/abilities/propulsion.py:35-59` | ManeuveringThruster |
| `game/simulation/components/abilities/propulsion.py:62-104` | StrategicMovement |
| `game/simulation/components/abilities/crew.py:9-27` | CrewCapacity |
| `game/simulation/components/abilities/crew.py:30-48` | LifeSupportCapacity |

**Lines Saved:** ~105 lines current -> ~68 lines target + 30 lines base class = net ~7 lines saved.
Primary benefit is consistency and reduced cognitive load, not raw line count.

**Risk:**

1. **Attribute access via `getattr`/`setattr`**: The base class uses dynamic attribute access.
   This means typos in class attribute strings (e.g. `value_attr = 'thrus_force'`) would fail
   silently. Mitigation: Add a `__init_subclass__` validation that checks all required class
   attributes are set and non-empty.

2. **Test regression**: All 7 migrating classes have existing tests that exercise `__init__`,
   `recalculate()`, `get_ui_rows()`, and `get_primary_value()`. These tests should pass without
   modification after migration since the external behavior is identical. Specifically:
   - `tests/unit/simulation/components/abilities/test_crew_abilities.py` (CrewCapacity, LifeSupportCapacity)
   - `tests/unit/entities/test_abilities.py` (CombatPropulsion, ManeuveringThruster)
   - `tests/unit/modifiers/test_propulsion_ability_bindings.py` (all propulsion)
   - `tests/unit/modifiers/test_ability_stat_binding.py` (binding apply)
   - `tests/unit/simulation/components/abilities/test_ability_base.py` (`_parse_primary_value`)

3. **Subclass overrides**: Some migrated classes might later need custom recalculate() logic.
   This is fine -- they can always override the method. The base class doesn't prevent this.

4. **New tests needed:**
   - `test_simple_multiplier_ability_init_with_int()` -- verify int_result flag
   - `test_simple_multiplier_ability_init_with_float()` -- verify float default
   - `test_simple_multiplier_ability_recalculate()` -- verify base*mult
   - `test_simple_multiplier_ability_sync_data()` -- verify sync updates base
   - `test_simple_multiplier_ability_get_ui_rows()` -- verify format
   - `test_simple_multiplier_ability_missing_class_attrs()` -- verify validation

**Category:** Medium Project
**Recommendation:** Implement in 3 phases:
  1. Add `SimpleMultiplierAbility` to `base.py` with `__init_subclass__` validation
  2. Migrate 7 classes, run full test suite after each
  3. Add new unit tests for the base class itself
**Effort:** Medium

---

### MAJOR: STAT_BINDINGS Redundancy with SimpleMultiplierAbility Class Attributes

**ID:** ABS-SIM-003
**Location:** All ability classes with single STAT_BINDINGS entry
**Issue:** For simple multiplier abilities, the `STAT_BINDINGS` declaration is **redundant** with
the class attributes. The binding specifies the same `stat_key`, `attribute_name`, `base_attribute`,
and `operation` that the class attributes already encode:

```python
class ShieldProjection(SimpleMultiplierAbility):
    STAT_BINDINGS = [AbilityStatBinding(StatKey.CAPACITY_MULT, 'capacity', 'multiply', 'base_capacity')]
    stat_key = 'capacity_mult'      # duplicates STAT_BINDINGS[0].stat_key.value
    value_attr = 'capacity'          # duplicates STAT_BINDINGS[0].attribute_name
    base_attr = 'base_capacity'      # duplicates STAT_BINDINGS[0].base_attribute
```

**Impact:** Information duplication -- if someone changes `stat_key` but forgets to update
`STAT_BINDINGS`, the introspection system will report stale data. Not a runtime bug (recalculate
uses class attributes, not STAT_BINDINGS.apply()), but a maintenance hazard.

**Proposed API:** Auto-generate `STAT_BINDINGS` from class attributes in `__init_subclass__`:

```python
class SimpleMultiplierAbility(Ability):
    # ... class attributes ...

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Auto-generate STAT_BINDINGS if not explicitly defined
        if cls.stat_key and not cls.__dict__.get('STAT_BINDINGS'):
            from .stat_keys import StatKey, AbilityStatBinding
            # Find matching StatKey enum member
            for sk in StatKey:
                if sk.value == cls.stat_key:
                    cls.STAT_BINDINGS = [
                        AbilityStatBinding(sk, cls.value_attr, 'multiply', cls.base_attr)
                    ]
                    break
```

This would eliminate the `STAT_BINDINGS` declaration entirely from the 7 migrated classes:

*Before:*
```python
class ShieldProjection(SimpleMultiplierAbility):
    STAT_BINDINGS = [AbilityStatBinding(StatKey.CAPACITY_MULT, 'capacity', 'multiply', 'base_capacity')]
    stat_key = 'capacity_mult'
    value_attr = 'capacity'
    base_attr = 'base_capacity'
    ...
```

*After:*
```python
class ShieldProjection(SimpleMultiplierAbility):
    stat_key = 'capacity_mult'
    value_attr = 'capacity'
    base_attr = 'base_capacity'
    ...
```

**Lines Saved:** ~3 additional lines per class (7 classes = ~21 more lines)

**Risk:** Medium. The STAT_BINDINGS are consumed by:
- `get_consumed_stats()` -- used by UI for "what stats affect this ability"
- `get_stat_bindings_info()` -- used by tooltips
- `get_effect_summary()` -- used by modifier introspection
- `AbilityStatBinding.apply()` -- **NOT used by recalculate() in practice** (abilities do their own)

Auto-generation must produce identical bindings to manual declarations. Need thorough testing.

**Category:** Small Project (do after ABS-SIM-002)
**Recommendation:** Implement as a follow-up to ABS-SIM-002. Keep explicit STAT_BINDINGS initially,
then add auto-generation once the base class is proven stable.
**Effort:** Medium

---

### MINOR: Superweapon Marker Ability Boilerplate

**ID:** ABS-SIM-004
**Location:** `game/simulation/components/abilities/superweapons.py:24-197`
**Issue:** All 6 superweapon classes (DestroyPlanet, DestroyStar, OpenWarpPoint, CloseWarpPoint,
CreateDysonSphere, SelfDestruct) are **identical** except for the `'value'` string in `get_ui_rows()`:

```python
class DestroyPlanet(Ability):
    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []

    def __init__(self, component, data):
        super().__init__(component, data)

    def get_ui_rows(self):
        return [{'label': 'Superweapon', 'value': 'Planet Imploder', 'color_hint': HINT_SUPERWEAPON}]

    def get_primary_value(self) -> float:
        return 0.0
```

Each class is 15-20 lines. With 6 classes, that's ~100 lines for what could be a single class
with a class attribute.

**Proposed API:**

```python
class SuperweaponMarker(Ability):
    """Base class for all superweapon marker abilities."""
    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []

    weapon_name: str = ''  # Subclasses set this

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [{'label': 'Superweapon', 'value': self.weapon_name, 'color_hint': HINT_SUPERWEAPON}]

    def get_primary_value(self) -> float:
        return 0.0


class DestroyPlanet(SuperweaponMarker):
    """Marks a component as a Planet Imploder."""
    weapon_name = 'Planet Imploder'

class DestroyStar(SuperweaponMarker):
    """Marks a component as a Stellerator."""
    weapon_name = 'Stellerator'

class OpenWarpPoint(SuperweaponMarker):
    """Marks a component as a Warp Point Creator."""
    weapon_name = 'Warp Point Creator'

class CloseWarpPoint(SuperweaponMarker):
    """Marks a component as a Warp Point Closer."""
    weapon_name = 'Warp Point Closer'

class CreateDysonSphere(SuperweaponMarker):
    """Marks a component as a Dyson Sphere Constructor."""
    weapon_name = 'Dyson Sphere Constructor'

class SelfDestruct(SuperweaponMarker):
    """Marks a component as a Self-Destruct Device."""
    weapon_name = 'Self-Destruct Device'
```

**Before:** ~110 lines (6 classes at ~18 lines each)
**After:** ~35 lines (base class + 6 two-line subclasses)

**Lines Saved:** ~75 lines

**Call Sites:**
- `game/simulation/components/abilities/superweapons.py` (entire file)

**Risk:** Very low. These are pure marker abilities with no combat logic. The ABILITY_REGISTRY
maps to class names, so subclass names must remain the same (they do).

**Category:** Quick Win
**Recommendation:** Implement independently of ABS-SIM-002. Simple find-and-replace.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **ABS-SIM-004 (Superweapon Marker Boilerplate)** -- Quick Win, saves 75 lines, zero risk.
   Do first as it's independent and simple.

2. **ABS-SIM-001 (CrewRequired Legacy Pattern)** -- Quick Win, fixes the last inconsistency
   in value extraction. 1 line change, very low risk.

3. **ABS-SIM-002 (SimpleMultiplierAbility)** -- Medium Project, the main abstraction. Saves
   37+ lines and establishes a pattern for all future simple abilities. Good ROI once the
   base class is implemented. Do after the quick wins are done.

4. **ABS-SIM-003 (STAT_BINDINGS Auto-generation)** -- Small Project, builds on ABS-SIM-002.
   Saves 21 more lines and eliminates a source of inconsistency. Do as a follow-up.

---

## Appendix: Full Value Extraction Pattern Audit

The following is a complete catalog of every `isinstance(data, (int, float))` and `isinstance(data, dict)` usage in the abilities directory, categorized by purpose:

### A. Primary Value Extraction (Cluster 3 target)

| File | Line | Class | Pattern | Uses _parse_primary_value? |
|------|------|-------|---------|---------------------------|
| defense.py | 18 | ShieldProjection | `self._parse_primary_value(data)` | YES |
| defense.py | 42 | ShieldRegeneration | `self._parse_primary_value(data)` | YES |
| defense.py | 64 | ToHitAttackModifier | `self._parse_primary_value(data)` | YES |
| defense.py | 89 | ToHitDefenseModifier | `self._parse_primary_value(data)` | YES |
| defense.py | 111 | EmissiveArmor | `int(self._parse_primary_value(data))` | YES |
| propulsion.py | 17 | CombatPropulsion | `self._parse_primary_value(data)` | YES |
| propulsion.py | 44 | ManeuveringThruster | `self._parse_primary_value(data)` | YES |
| propulsion.py | 89 | StrategicMovement | `self._parse_primary_value(data)` | YES |
| crew.py | 17 | CrewCapacity | `int(self._parse_primary_value(data))` | YES |
| crew.py | 38 | LifeSupportCapacity | `int(self._parse_primary_value(data))` | YES |
| crew.py | 73 | CrewRequired | `data if isinstance(data, (int, float)) else data.get('value', data.get('amount', 0))` | **NO** |

**Result:** 10 of 11 migrated. Only CrewRequired remains (ABS-SIM-001).

### B. Multi-Field Dict Extraction (NOT Cluster 3 -- different pattern)

These classes extract multiple named fields from a dict. They use `isinstance(data, dict)`
but are NOT candidates for `_parse_primary_value()` because they read multiple keys:

| File | Class | Fields Extracted |
|------|-------|-----------------|
| resources.py | ResourceConsumption | resource, amount, trigger |
| resources.py | ResourceStorage | resource, amount |
| resources.py | ResourceGeneration | resource, amount |
| cargo.py | CargoStorage | cargo_type, capacity |
| harvester.py | ResourceHarvesterAbility | resource_type, base_harvest_rate |
| harvester.py | EmpireStorageAbility | resource_type, capacity |
| harvester.py | SpaceShipyardAbility | construction_speed_bonus, max_ship_mass, production_rates |
| markers.py | VehicleLaunchAbility | fighter_class, capacity, cycle_time |
| weapons.py | WeaponAbility | damage, range, reload, firing_arc, facing_angle |
| weapons.py | ProjectileWeaponAbility | projectile_speed |
| weapons.py | BeamWeaponAbility | accuracy_falloff, base_accuracy |
| weapons.py | SeekerWeaponAbility | projectile_speed, endurance, turn_rate, etc. |
| propulsion.py | WarpJump | max_tonnage, energy_cost |
| colonize.py | ColonizePlanet | planet_type (string, not numeric) |

These 14 classes use a fundamentally different pattern and should NOT be forced into
`_parse_primary_value()`. Their dict-vs-primitive branching is appropriate for their
multi-field nature.

### C. Sync Data isinstance checks (maintenance pattern)

Several `sync_data()` methods use `isinstance(data, dict)` / `isinstance(data, (int, float))`
to handle both formats. These are handled automatically by `SimpleMultiplierAbility.sync_data()`
for the 7 migrating classes. For the remaining classes (resources, cargo), the pattern is
appropriate given their multi-field nature.

---

*Report compiled: 2026-02-23*
*Agent: ABS-SIM (Simulation Abstraction Designer)*
