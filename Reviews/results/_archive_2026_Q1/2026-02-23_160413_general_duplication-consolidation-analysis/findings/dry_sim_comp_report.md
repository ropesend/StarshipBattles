# DRY-SIM-COMP: Simulation Components & Entities Report

## Summary
- **Total duplication findings:** 12
- **Critical:** 2, **Major:** 4, **Minor:** 4, **Info:** 2

## Findings

### CRITICAL: Ability Parameter Parsing Pattern Duplication
**ID:** CQ-001
**Location:** `game/simulation/components/abilities/weapons.py:47-109`, `abilities/propulsion.py:14-48`, `abilities/defense.py:15-19`, `abilities/resources.py:24-28`, `abilities/cargo.py:35-46`, `abilities/crew.py:14-18`, and 10+ more
**Issue:** Every ability class implements identical parameter parsing: `val = data if isinstance(data, (int, float)) else data.get('value', 0)`. This 2-3 line pattern appears in 15+ ability classes with only the target field name changing.
**Impact:** High maintenance burden - changes to parsing logic must be replicated in 15+ locations. Bug fixes easily missed.
**Recommendation:** Extract `Ability._parse_primary_value(data, default=0.0)` to base class.
**Effort:** Simple

### CRITICAL: Ability Recalculation Pattern Duplication
**ID:** CQ-002
**Location:** 16+ ability classes with `recalculate()` methods
**Issue:** Nearly all abilities implement `self.field = self._base_field * self.get_effective_stat('field_mult', 1.0)` with identical structure but different field names.
**Impact:** Inconsistent recalculation if modifier stat key naming changes. No central hook for logging/caching.
**Recommendation:** Create `_apply_multiplier(base_attr, current_attr, stat_key)` helper in base class.
**Effort:** Medium

### MAJOR: Sync Data Boilerplate
**ID:** CQ-003
**Location:** `abilities/weapons.py:111-149`, `abilities/propulsion.py:21-25`, `abilities/cargo.py:48-57`
**Issue:** Multiple abilities implement `sync_data()` with boilerplate that could be centralized. Some abilities missing sync entirely.
**Impact:** Inconsistent sync behavior. Same changes must be manually applied to multiple classes.
**Recommendation:** Create generic `sync_data()` template in base with hooks for subclasses.
**Effort:** Medium

### MAJOR: UI Row Generation Boilerplate
**ID:** CQ-004
**Location:** 20+ ability classes with `get_ui_rows()` methods
**Issue:** Nearly all abilities return hardcoded single-row lists with scattered color hints: `return [{'label': 'X', 'value': f"{self.x:.0f}", 'color_hint': '#FF6464'}]`
**Impact:** Color hints scattered. UI theming changes require updating 20+ classes.
**Recommendation:** Create `UIRowBuilder` with theme constants (DAMAGE='#FF6464', THRUST='#64FF64', etc.)
**Effort:** Medium

### MAJOR: Data Validation and Default Fallback Duplication
**ID:** CQ-005
**Location:** `abilities/weapons.py:47-109` (damage/range/reload), `abilities/propulsion.py:14-48`
**Issue:** Complex nested conditionals for data extraction with fallback chain (dict → component.data → base_* → default) repeated in 10+ locations. Formula evaluation scattered.
**Impact:** Same fallback chain logic hard to follow, duplicated, and prone to inconsistency.
**Recommendation:** Extract `ParameterResolver.resolve_numeric(data, component, param_name, default)`.
**Effort:** Medium

### MAJOR: Manager Delegation Pattern in Component
**ID:** CQ-006
**Location:** `game/simulation/components/component.py:280-400`
**Issue:** Component class has 20+ methods that delegate to manager classes with minimal logic. Inconsistent - some have guard clauses, others just delegate.
**Impact:** Clutters Component interface. Future maintainers unsure whether to add methods to Component or Manager.
**Recommendation:** Standardize on one delegation approach across all managers.
**Effort:** Complex

### Minor: Cooldown Management Duplication
**ID:** CQ-007
**Location:** `abilities/weapons.py:170-173`, `abilities/markers.py:27-30`
**Issue:** Two unrelated abilities implement identical cooldown countdown logic with different naming (cooldown_timer vs cooldown).
**Recommendation:** Create `CooldownMixin` with `tick_cooldown()`, `reset_cooldown()`, `is_ready()`.
**Effort:** Simple

### Minor: Formula String Validation Pattern
**ID:** CQ-008
**Location:** `weapons.py:59-66,77-82,92-97`, `component_resource_manager.py:113-117`
**Issue:** Multiple places check `startswith('=')` for formula prefix. 10+ locations.
**Recommendation:** Create `FormulaUtils.is_formula()`, `parse_numeric_or_formula()`.
**Effort:** Simple

### Minor: Component Type Checking for Modifiers
**ID:** CQ-009
**Location:** `modifier_manager.py:60-68`
**Issue:** Same restriction checking pattern (deny_types/allow_types) with nested conditionals.
**Recommendation:** Extract `RestrictionChecker.is_restricted()`.
**Effort:** Simple

### Minor: Numeric Type Conversion Inconsistency
**ID:** CQ-011
**Location:** Various abilities using int() vs float() inconsistently
**Issue:** Some abilities store primary values as int, others as float.
**Recommendation:** Standardize on float for all primary values.
**Effort:** Simple

### Info: Lazy Property Initialization Pattern
**ID:** CQ-010
**Location:** `component.py:235-247`, `ship.py:169-171`
**Issue:** Multiple entities use lazy init pattern. Well-known pattern, no consolidation needed.
**Effort:** Info only

### Info: Marker Ability get_primary_value() Pattern
**ID:** CQ-012
**Location:** `markers.py:56-57,68-69,80-81`, `superweapons.py:47-49`
**Issue:** Inconsistent semantics - some markers return 1.0, others 0.0.
**Recommendation:** Standardize all markers to return 0.0.
**Effort:** Info only

## Top 5 Priority Consolidation Opportunities
1. **CQ-001**: Extract `_parse_primary_value()` - 15+ classes, Simple effort, High ROI
2. **CQ-002**: Create recalculation helpers - 16+ classes, Medium effort, High ROI
3. **CQ-004**: Extract UI row builder with theme - 20+ classes, Medium effort, Medium-High ROI
4. **CQ-005**: Create ParameterResolver - 10+ locations, Medium effort, High ROI
5. **CQ-007**: Create CooldownMixin - 2-3 classes, Simple effort, Scalable pattern
