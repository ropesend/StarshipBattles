# PROJ-54: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

<<<<<<< HEAD
## Initial Analysis

### Code Quality Audit Findings

The Combat Lab has ~60 scenarios across 5 scenario files. The framework is functional but has significant maintainability issues that will compound as we expand coverage.

**Critical Issues Found:**

1. **Massive verify/results duplication** - `self.results['initial_hp'] = self.initial_hp` appears 50 times across 8 files. Scenarios override `verify()` entirely, bypassing template logic.
2. **Projectile scenarios bypass templates** - All 9 projectile scenarios extend raw `TestScenario`, duplicating the full setup/update/verify cycle that `StaticTargetScenario` already provides.
3. **`_resolve_path` duplicated 3 times** - Identical utility in `ExactMatchRule`, `DeterministicMatchRule`, and `PreRunValidator` with varying error quality.
4. **`_extract_ship_validation_data` hardcoded to beam** - Only extracts `BeamWeaponAbility` data, returns immediately after finding one. Cannot validate projectile, seeker, defense, or propulsion data.
5. **Beam scenarios duplicate hit-chance calc** - Every beam scenario has near-identical `custom_setup()`.
6. **Seeker scenarios hardcode magic numbers** - `self.results['missile_speed'] = 1000` instead of reading from loaded ship data.

### Ability System Architecture

25+ ability types in `ABILITY_REGISTRY`:
- **Weapons:** `BeamWeaponAbility`, `ProjectileWeaponAbility`, `SeekerWeaponAbility`
- **Defense:** `ShieldProjection`, `ShieldRegeneration`, `ToHitAttackModifier`, `ToHitDefenseModifier`, `EmissiveArmor`
- **Propulsion:** `CombatPropulsion`, `ManeuveringThruster`, `StrategicMovement`, `WarpJump`
- **Resources:** `ResourceConsumption`, `ResourceStorage`, `ResourceGeneration`
- **Crew:** `CrewRequired`, `CrewCapacity`, `LifeSupportCapacity`
- **Markers:** `Armor`, `Engine`, `Generator`, `Weapon`, `Thruster`
- **Other:** `Harvester`, `HarvestStorage`

All abilities use `STAT_BINDINGS` for modifier integration. Modifiers affect abilities through a two-stage aggregation: intra-group MAX (redundancy), inter-group SUM/MULTIPLY (stacking).

### Current Test Coverage

| Ability Type | Combat Lab Coverage |
|---|---|
| BeamWeaponAbility | 18+ scenarios |
| ProjectileWeaponAbility | 9 scenarios |
| SeekerWeaponAbility | 8 scenarios |
| ResourceConsumption/Storage/Gen | 9 scenarios |
| CombatPropulsion | 3 scenarios |
| ShieldProjection | **None** |
| ShieldRegeneration | **None** |
| EmissiveArmor | **None** |
| ToHitDefenseModifier | **None** |
| ToHitAttackModifier | **None** |
| Component Modifiers | **None** |

---

## Key Patterns to Reuse

- **`StaticTargetScenario`**: `simulation_tests/scenarios/templates.py:33-222` - Template with `custom_setup`/`custom_update` hooks, pass-criteria flags
- **`DuelScenario`**: `simulation_tests/scenarios/templates.py:229-398` - Two-ship engagement template
- **`PropulsionScenario`**: `simulation_tests/scenarios/templates.py:405-572` - Movement/physics template
- **`ExactMatchRule`**: `simulation_tests/scenarios/validation.py:100-226` - Exact value validation with path resolution
- **`StatisticalTestRule`**: `simulation_tests/scenarios/validation.py:378+` - TOST equivalence testing for hit rates
- **`DeterministicMatchRule`**: `simulation_tests/scenarios/validation.py:229-375` - Float comparison with tolerance
- **Zero-mass test components**: `simulation_tests/data/components.json` - All non-hull test components have mass=0

---

## Dependencies & Risks

1. **Phase ordering is critical** - Template refactor (Phase 2) must happen before scenario simplification (Phase 3), because scenarios need the new `_collect_results` hook.
2. **Test ID stability** - All existing test IDs and pass/fail behavior MUST remain identical through Phases 1-3. These are refactors, not rewrites.
3. **Backward compat for `data['weapon']`** - When generalizing `_extract_ship_validation_data`, existing beam scenarios must still resolve `attacker.weapon.damage` paths.
4. **Surface distance calculation** - Beam weapons measure range to target surface, not center. This is a critical formula detail that tests depend on.

---

## Modifier Design

Game modifiers (in `data/modifiers.json`) have complex multi-effect formulas with mass/cost side effects. For testing, we create **simplified single-effect versions** in `simulation_tests/data/modifiers.json`:

| Test Modifier | Game Equivalent | Single Effect | No Side Effects |
|---|---|---|---|
| `test_damage_boost` | `simple_size_mount` | `damage_mult` only | No mass/cost |
| `test_range_boost` | `range_mount` | `range_mult` only | No mass/cost |
| `test_turret` | `turret_mount` | `arc_set` only | No mass |
| `test_reload_boost` | `rapid_fire` | `reload_mult` only | No mass/cost |
| `test_accuracy_boost` | `precision_mount` | `accuracy_add` only | No mass/cost |
| `test_thrust_boost` | `simple_size_mount` | `thrust_mult` only | No mass/cost |
| `test_endurance_boost` | `seeker_endurance` | `endurance_mult` only | No mass/cost |
| `test_consumption_reduction` | `efficiency_mount` | `consumption_mult` only | No mass/cost |

This isolates the variable being tested - if a damage modifier test fails, we know the issue is with `damage_mult` application, not a mass/cost side effect.

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
=======
## Initial Analysis (Phase A)

### Current Implementations Found

1. **PlanetReportPanel Widget** (REUSABLE - BEST IMPLEMENTATION)
   - Location: `game/ui/panels/planet_report_panel.py`
   - Status: ✅ Well-designed, tested, reusable
   - Components: Portrait (150x150), info text, atmosphere graph, complexes list
   - Layout: 580px wide, 350px minimum height
   - Used by: BuildQueueScreen only (currently)
   - Test coverage: Excellent - `tests/integration/ui/test_build_queue_enhanced_planet_report.py`

2. **Strategy UI** (INLINE - SHOULD BE REPLACED)
   - Location: `game/ui/screens/strategy_ui.py` (lines 562-618)
   - Status: ⚠️ Inline HTML formatting, not reusable
   - Problem: Duplicates PlanetReportPanel logic, creates maintenance burden

3. **Planet List Window** (MISSING - NEEDS TO BE ADDED)
   - Location: `game/ui/screens/planet_list_window.py`
   - Status: ❌ No planet report panel exists
   - Needs: Add `PlanetReportPanel` to right side when planet selected

4. **Colonize Planet Window** (BASIC - UPGRADE TO FULL PANEL)
   - Location: `game/ui/screens/planet_selection_window.py`
   - Status: ⚠️ Text-only display via formatter callback
   - Will upgrade to: Full `PlanetReportPanel` for richer display

### Planet Image Bug Identified

**Problem:** Planet images not displaying correctly - show random images instead of persistent assigned images

**Root Cause:** `_get_object_asset()` in `strategy_screen.py` (lines 494-503) ignores planet's stored `image_id` field

**Current (Wrong) Logic:**
- Uses category-based lookup (`'terran'`, `'gas'`, etc.)
- Calls `am.get_random_from_group('planets', cat, seed_id=id(obj))`
- Memory ID as seed = non-deterministic across sessions

**Correct Logic:**
- Use planet's `image_id` field (assigned during galaxy generation)
- Load from `Paths.PLANETS_V3_DIR / image_id`
- Apply `image_rotation` for visual variety

---

## Swarm Findings Summary

### Architecture Analysis

**3-Tier UI Pattern:**
- **Screens** (stateful orchestrators) - StrategyUI, BuildQueueScreen, PlanetListWindow
- **Panels** (stateless containers) - PlanetReportPanel, DesignReportPanel
- **Widgets** (atomic elements) - UIImage, UITextBox, UILabel

**Key Principle:** Panels are dependency-injected stateless containers. Screens handle asset resolution and pass data to panels.

**Current Status:**
- ✅ PlanetReportPanel correctly positioned as reusable widget
- ⚠️ Strategy UI violates architecture (duplicates panel logic inline)
- ❌ Planet List missing panel implementation

### Key Patterns to Reuse

1. **Reusable Panel Pattern:**
   ```python
   def __init__(self, manager, rect, entity, container=None):
       self.panel = UIPanel(relative_rect=rect, manager=manager, container=container)
       # Create sub-elements within self.panel
   ```

2. **Selection-Update Pattern:**
   ```python
   def update_planet(self, planet, portrait_surface=None):
       self.planet = planet
       self.detail_text.html_text = format_planet_info(planet)
       self.detail_text.rebuild()  # CRITICAL: rebuild after html_text change
       self._update_portrait(portrait_surface)
   ```

3. **Optional Components Pattern:**
   ```python
   def __init__(self, ..., show_complexes=True, show_graph=True):
       if show_complexes:
           self.complexes_container = UIScrollingContainer(...)
       else:
           self.complexes_container = None
   ```

4. **External Button Management:**
   - Keep action buttons (Build Queue, Colonize) OUTSIDE panel
   - Positioned by parent screen (below or beside panel)
   - Panel maintains single responsibility (display only)

### Dependencies & Risks

**Critical Issues:**

1. **Duplicate `format_planet_info()` Implementations** (HIGH/HIGH)
   - Primary: `game/ui/screens/strategy_detail_fmt.py` (lines 58-118)
   - Duplicate: `game/ui/screens/strategy_ui.py` (lines 562-618)
   - Mitigation: Delete duplicate, use single source

2. **Layout Cramping** (MEDIUM/MEDIUM)
   - Panel requires minimum 300px width (portrait only)
   - Recommended 580px for full layout
   - Test at 300px, 370px, 580px widths

3. **Missing Planet Data** (MEDIUM/MEDIUM)
   - Some planets may have empty `facilities`, `resources`
   - Maintain existing `hasattr()` and None checks
   - Panel already handles this correctly

4. **Image Loading Failures** (MEDIUM/MEDIUM)
   - Files may not exist, surfaces may be None
   - Wrap in try/except, always have placeholder fallback
   - Panel's gradient placeholder is good pattern

### Test Impact

**~30 Tests Will Need Updates:**
- `test_build_queue_enhanced_planet_report.py` (20 tests)
- `test_planet_complexes_list.py` (8 tests)
- `test_build_queue_formatting.py` (2 tests)
- `build_queue_screen/test_basics.py` (1 test)

**Coverage Gaps to Address:**
- No unit tests for `format_planet_info()` in isolation
- No tests for atmosphere graph edge cases
- No tests for portrait loading/fallback
- No tests for empty atmosphere, missing facilities

### Opportunities Discovered

1. **API Enhancement:** PlanetReportPanel can be improved with backward-compatible parameters
   - Add `portrait_surface` to __init__ (cleaner than update_planet only)
   - Add `show_complexes` parameter (enables Strategy UI reuse)

2. **Code Consolidation:** Eliminating duplicate formatting saves ~60 lines, reduces maintenance

3. **Consistency:** All 4 contexts will show identical planet info (user-friendly)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08
