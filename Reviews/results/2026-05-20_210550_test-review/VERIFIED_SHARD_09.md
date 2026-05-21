# Verified Shard 09 — Test Audit Report

## Verification Summary

- Shard: 09 | Claims reviewed: 11 (9 shard + 2 cross-shard)
- CONFIRMED: 9 | DISPUTED: 0 | PARTIALLY CONFIRMED: 1 | INCONCLUSIVE: 1
- Severity adjustments: 1 downgrade (CRITICAL → MAJOR)

---

## SHARD_09 Findings

### F-001: CAT-10 — Identical parametrization across 10 superweapon tests [MINOR]
**Status: CONFIRMED**

- **File**: `tests/unit/simulation/components/abilities/test_superweapons.py:41-162`
- **Original claim**: 10 test methods each use `@pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())` with identical parametrization over 6 abilities.

**Verification evidence**:
- 10 methods confirmed at lines 42, 52, 63, 78, 84, 96, 102, 141, 149, 157 — all use identical `@pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())`.
- Scope cluster (layer+scope): 4 methods (lines 63, 78, 84, plus `test_ability_in_registry` at 133 — 133 is NOT counted in the 10), all identically parametrized.
- Action-time cluster: 3 methods (lines 141, 149, 157), identically parametrized.
- The claim's suggestion (collapse 4 scope + 3 action-time methods) is mechanically feasible and would reduce 10 methods to ~4.

**Severity**: MINOR — no change.

---

### F-002: CAT-9 — UI-rows test uses `.items()` parametrize where peers use `.keys()` [MINOR]
**Status: CONFIRMED**

- **File**: `tests/unit/simulation/components/abilities/test_superweapons.py:113-126`
- **Original claim**: `test_get_ui_rows_returns_superweapon_row` uses `.items()` parametrize form, different from the other 10 methods using `.keys()`.

**Verification evidence**:
- Line 113: `@pytest.mark.parametrize("ability_name,expected_value", SUPERWEAPON_ABILITIES.items())` — uses `.items()`, providing 2 parameters.
- All 10 peer methods use `SUPERWEAPON_ABILITIES.keys()` — 1 parameter.
- `TestSuperweaponAbilityUIRows` class (line 110) contains only this single test method.
- The claim's suggestion to consolidate with registry presence / instantiation tests is feasible but may reduce clarity of what's being tested.

**Severity**: MINOR — no change.

---

### F-003: CAT-4 — Duplicate colonization validation tests [MAJOR]
**Status: CONFIRMED**

- **File**: `tests/integration/colonization/test_planet_specific_colonization.py:309-337` and `:638-659`
- **Original claim**: Both tests verify the same contract — "Fleet without a drop pod passes validation at command time" with identical assertion `result.is_valid is True`.

**Verification evidence**:
- **Test 1** (line 309, `TestColonizeWithWrongPod.test_colonize_without_drop_pod_succeeds_at_command_time`):
  - Creates combat ship via `make_combat_ship("Combat Ship", 1)`
  - Creates `fleet = Fleet(1, 1, HexCoord(10, 10))`, appends ship
  - Creates `empire = Empire(1, "Player 1", (255, 0, 0))`, appends fleet
  - Calls `ColonizeValidator.validate(galaxy, fleet, ice_planet, component_registry=component_registry)`
  - Asserts `result.is_valid is True` (line 337)

- **Test 2** (line 638, `TestEdgeCases.test_fleet_with_no_pods_succeeds_at_command_time`):
  - Creates combat ship via `make_combat_ship("Combat Ship", 1)`
  - Creates `fleet = Fleet(1, 1, HexCoord(10, 10))`, appends ship
  - Calls `ColonizeValidator.validate(galaxy, fleet, ice_planet, component_registry=component_registry)`
  - Asserts `result.is_valid is True` (line 659)

**Minor difference**: Test 1 explicitly creates an Empire and appends the fleet to it; Test 2 does not create an Empire. The SUT call (`ColonizeValidator.validate`) and the assertion are identical. The claim's "structurally identical" characterization is accurate.

**Severity**: MAJOR — no change. One of these tests is redundant.

---

### F-004: CAT-9 — Triplicate `colony_pod` key in `component_registry` fixture [MINOR]
**Status: CONFIRMED**

- **File**: `tests/integration/colonization/test_planet_specific_colonization.py:172-186`
- **Original claim**: The fixture defines `'colony_pod'` three times with identical content — a copy-paste artifact.

**Verification evidence**:
```
Line 174: 'colony_pod': {'id': 'colony_pod', 'abilities': {'ColonizePlanet': True}}
Line 178: 'colony_pod': {'id': 'colony_pod', 'abilities': {'ColonizePlanet': True}}  # duplicate
Line 183: 'colony_pod': {'id': 'colony_pod', 'abilities': {'ColonizePlanet': True}}  # duplicate
```
- Three identical entries, bytes-for-bytes identical.
- Python dict silently takes the last value, so runtime behavior is unaffected.
- The fixture intent is to register a single `colony_pod` entry — the duplicates serve no purpose.

**Severity**: MINOR — no change.

---

### F-005: CAT-3 — Intentionally-red TDD tests for PROJ-410 Phase 2 [CRITICAL → **MAJOR**]
**Status: CONFIRMED (severity DOWNGRADED: CRITICAL → MAJOR)**

- **File**: `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py:877-891`
- **Original claim**: Helper `_spy_invalidate(vt)` asserts `hasattr(vt, "invalidate_widget_caches")` which fails on current `main`. Called by 4 tests. These are "intentionally red" TDD tests. Rated CRITICAL.

**Verification evidence**:

1. **Helper function confirmed** (line 877-891):
   ```python
   def _spy_invalidate(vt):
       assert hasattr(vt, "invalidate_widget_caches"), (
           "PROJ-410 Phase 2: VirtualTable must expose invalidate_widget_caches() method. "
           "See Projects/active_projects/PROJ-410/phase_2_checklist.md Task 2.2."
       )
   ```
   The `assert` is on line 884 — it WILL raise `AssertionError` if the method does not exist.

2. **Actual callers of `_spy_invalidate`**: 3 tests (not 4 as claimed):
   - Line 920: `test_PROJ410_task_1_2_yard_switch_invalidates_widget_caches` (line 894)
   - Line 959: `test_PROJ410_task_1_3_close_and_reopen_invalidates_cache` (line 933)
   - Line 1013: `test_PROJ410_task_1_5_ship_yard_to_planetary_yard_invalidates` (line 979)

3. **`test_issue17_reopen_after_yard_switch_clears_stale_label_text`** (line 1282): Does NOT call `_spy_invalidate`. It references `invalidate_widget_caches` only in docstring/commentary and accesses it directly at line 1455. However, this direct access would also fail if the method doesn't exist. So the claim's count of "4 tests" is slightly inaccurate (3 via the helper, 1 via direct access = 4 affected tests overall).

**Severity adjustment — CRITICAL → MAJOR**:
- AGENTS.md Rule 1 mandates **Strict TDD**: "Write (or identify) the failing test first, run it to confirm failure, then implement. No exceptions."
- These tests are explicitly documented TDD tests pending Phase 2 implementation. The docstring clearly explains the contract and expected failure reason.
- A CRITICAL rating implies the tests are accidentally broken or have no clear purpose. These tests have a clear, documented purpose (PROJ-410 Phase 2 contract).
- However, leaving them to fail on `main` does pollute CI results and could mask real regressions. A MAJOR rating reflects this practical concern while acknowledging TDD compliance.
- The claim's suggestion to add `@pytest.mark.skip(reason="PROJ-410 Phase 2 pending")` is sound.

**Severity**: **MAJOR** (downgraded from CRITICAL).

---

### F-006: CAT-10 — Three identical IScene protocol verification tests [MINOR]
**Status: CONFIRMED**

- **File**: `tests/unit/ui/screens/test_setup_screen.py:389-408`
- **Original claim**: Three methods in `TestBattleSetupScreenISceneProtocol` follow identical pattern: create screen, check `hasattr` + `callable`, differing only in method name.

**Verification evidence**:
```python
# Line 389: test_handle_event_method_exists
screen = self.BattleSetupScreen(800, 600)
assert hasattr(screen, 'handle_event')
assert callable(screen.handle_event)

# Line 396: test_update_method_exists
screen = self.BattleSetupScreen(800, 600)
assert hasattr(screen, 'update')
assert callable(screen.update)

# Line 403: test_draw_method_exists
screen = self.BattleSetupScreen(800, 600)
assert hasattr(screen, 'draw')
assert callable(screen.draw)
```
- Identical 3-line bodies, differing only in the method name string.
- Trivially parametrizable: `@pytest.mark.parametrize("method", ["handle_event", "update", "draw"])`.

**Severity**: MINOR — no change.

---

### F-007: CAT-9 — Repeated inline mock function definitions in race setup tests [MINOR]
**Status: CONFIRMED**

- **File**: `tests/unit/ui/screens/test_race_setup_screen.py:155-167, 173-190, 304-309, 345-352`
- **Original claim**: At least 10 test methods define ad-hoc mock functions in the test body.

**Verification evidence** (spot-check of cited lines):
- **Lines 155-163** (`test_show_step_updates_current_step`): defines inline `mock_show_step` (9 lines).
- **Lines 173-179** (`test_show_step_hides_other_panels`): defines another inline `mock_show_step` (7 lines), similar but not identical.
- **Lines 304-308** (`test_save_calls_race_library`): defines inline `mock_save_race` (4 lines).
- **Lines 321-326** (`test_load_race_populates_all_tabs`): defines inline `mock_load_race` (6 lines).
- **Lines 345-352** (`test_validate_for_save_checks_required_fields`): defines inline `mock_validate_for_save` (7 lines).

All follow the pattern: define mock function → replace screen method → call → assert. Accumulated LOC impact across the file (~1641 lines total) is material. The claim's estimated ~150 LOC savings from extraction is plausible.

**Severity**: MINOR — no change.

---

### F-008: CAT-10 — Structurally identical pause-flag queue tests [MINOR]
**Status: CONFIRMED**

- **File**: `tests/unit/strategy/engine/test_production_engine_queue.py:125-144` and `:245-259`
- **Original claim**: Both tests verify that a `construction_queue_paused=True` flag blocks queue progress, with structurally identical bodies.

**Verification evidence**:
- **Test 1** (line 125, `test_construction_queue_paused_skips_colony_base_queue`):
  - Creates `_ship_item()`, sets pause on colony mock, asserts `item["resources_consumed"]["A"] == 0.0`
- **Test 2** (line 245, `test_fleet_pause_flag_blocks_fleet_queue_processing`):
  - Creates `_ship_item()`, sets pause on fleet mock, asserts `item["resources_consumed"]["A"] == 0.0`

Both assertions are byte-for-byte identical: `assert item["resources_consumed"]["A"] == 0.0`.

**Minor counterpoint**: The setups differ in a nontrivial way — colony context uses `monkeypatch` for `_colony_has_planetary_yard` while fleet context uses `fleet.capabilities.has_space_shipyard`. A parametrized test would need conditional setup logic. The structural duplication is real, but the parametrization effort is slightly higher than the claim suggests.

**Severity**: MINOR — no change.

---

### F-009: CAT-10 — Four similar energy engine tests with shared setup pattern [MINOR]
**Status: PARTIALLY CONFIRMED**

- **File**: `tests/unit/strategy/engine/test_planet_energy_engine.py:211-269`
- **Original claim**: Lists 4 tests at lines 211-269 — `test_energy_generation_increases_energy`, `test_multiple_generators_stack`, `test_generation_and_drain_balance`, `test_shield_drains_energy` — all follow the same `_make_facility` + `_make_planet` + `_make_empire` pattern.

**What's accurate**:
- The 4 tests at lines 211-269 DO all follow the same setup pattern:
  1. `engine = PlanetEnergyEngine(registries=fresh_registries)`
  2. Create facilities via `_make_facility(...)`, `_make_planet(...)`, `_make_empire(...)`
  3. `engine.process_energy_tick(1, [empire])`
  4. Assert `planet.energy == pytest.approx(...)`
- The structural duplication claim is valid.

**What's inaccurate**:
- Two test names in the claim header are WRONG for the cited line range (211-269):
  - Claim says: `test_multiple_generators_stack` → actual at line 225 is **`test_energy_capped_at_capacity`**
  - Claim says: `test_generation_and_drain_balance` → actual at line 238 is **`test_no_generators_no_energy`**
  - `test_multiple_generators_stack` exists at **line 294** (outside the cited range)
  - `test_generation_and_drain_balance` exists at **line 346** (outside the cited range)

**Correction**: The 4 tests at lines 211-269 are actually:
1. `test_energy_generation_increases_energy` (line 211) ✓
2. `test_energy_capped_at_capacity` (line 225)
3. `test_no_generators_no_energy` (line 238)
4. `test_shield_drains_energy` (line 250)

All 4 follow the same pattern. The parametrization suggestion is valid. `TestPlanetEnergyEngine` has 9 tests total (lines 211-367), and all 9 share the same setup pattern, so the consolidation opportunity is even larger than the claim suggests (~9 tests, ~160 LOC).

**Severity**: MINOR — no change (structural observation is correct, only test names were wrong).

---

## CROSS_SHARD Findings (Involving Shard 09 Files)

### F-010: DUP-005 / HLP-006 — `_make_empire(colonies=None)` duplicated across strategy engine tests [MINOR]
**Status: CONFIRMED**

- **Shard 09 files**:
  - `tests/unit/strategy/engine/test_planet_energy_engine.py:64-68`
  - `tests/unit/strategy/engine/test_component_activation_engine.py:41-46`

**Verification evidence**:

`test_planet_energy_engine.py:64-68`:
```python
def _make_empire(colonies=None):
    """Create a mock Empire."""
    empire = MagicMock()
    empire.colonies = colonies or []
    return empire
```

`test_component_activation_engine.py:41-46`:
```python
def _make_empire(colonies=None):
    empire = MagicMock()
    empire.id = 1
    empire.colonies = colonies or []
    empire.fleets = []
    return empire
```

- **Similarity**: ~80% shared — both accept `colonies=None`, create `MagicMock()`, assign `colonies = colonies or []`.
- **Difference**: The activation-engine version adds `empire.id = 1` and `empire.fleets = []` (domain-specific fields).
- Cross-shard report (HLP-006) identifies 6 total copies across 6 shards. The claim that consolidation would reduce duplication is valid.

**Severity**: MINOR.

---

### F-011: HLP-002 — `MockPlanetType(Enum)` duplicated across 10+ files [MINOR]
**Status: CONFIRMED**

- **Shard 09 files**:
  - `tests/integration/colonization/test_planet_specific_colonization.py:33-37`
  - `tests/integration/strategy/test_commands.py:18-19`

**Verification evidence**:

`test_planet_specific_colonization.py:33-37`:
```python
class MockPlanetType(Enum):
    ICE_DWARF = "ICE_DWARF"
    CONTINENTAL = "CONTINENTAL"
    ARID = "ARID"
```

`test_commands.py:18-19`:
```python
class MockPlanetType(Enum):
    CONTINENTAL = "CONTINENTAL"
```

- Both define `MockPlanetType(Enum)` at module level with the same pattern.
- `test_commands.py` has a minimal variant (1 value), `test_planet_specific_colonization.py` has an extended variant (3 values).
- Cross-shard report identifies 10+ duplicates across 8 shards. Consolidation into `tests/fixtures/colonization_fixtures.py` or `tests/conftest.py` is valid.

**Severity**: MINOR.

---

## Verification Disposition Summary

| F-# | File | Category | Original Severity | Verified Severity | Disposition |
|-----|------|----------|-------------------|-------------------|-------------|
| F-001 | test_superweapons.py | CAT-10 | MINOR | MINOR | CONFIRMED |
| F-002 | test_superweapons.py | CAT-9 | MINOR | MINOR | CONFIRMED |
| F-003 | test_planet_specific_colonization.py | CAT-4 | MAJOR | MAJOR | CONFIRMED |
| F-004 | test_planet_specific_colonization.py | CAT-9 | MINOR | MINOR | CONFIRMED |
| F-005 | test_build_queue_screen_lifecycle.py | CAT-3 | CRITICAL | **MAJOR** | CONFIRMED (severity downgraded) |
| F-006 | test_setup_screen.py | CAT-10 | MINOR | MINOR | CONFIRMED |
| F-007 | test_race_setup_screen.py | CAT-9 | MINOR | MINOR | CONFIRMED |
| F-008 | test_production_engine_queue.py | CAT-10 | MINOR | MINOR | CONFIRMED |
| F-009 | test_planet_energy_engine.py | CAT-10 | MINOR | MINOR | PARTIALLY CONFIRMED |
| F-010 | test_planet_energy_engine.py / test_component_activation_engine.py | DUP-005/HLP-006 | MINOR | MINOR | CONFIRMED |
| F-011 | test_planet_specific_colonization.py / test_commands.py | HLP-002 | MINOR | MINOR | CONFIRMED |

## Verification Notes

1. **F-005 downgrade rationale**: These are compliant TDD tests per AGENTS.md Rule 1 with clear, documented purpose. CRITICAL is appropriate for accidentally-broken tests, not intentionally-red TDD tests. However, they DO pollute CI and should be skipped until Phase 2 lands.

2. **F-009 test name errors**: The claim body contains 2 incorrect test names for the cited line range. The structural observation (same setup pattern) and consolidation suggestion remain valid. Recommend updating the Phase 1 report to correct the test names.

3. **F-005 caller count**: The claim says _spy_invalidate is "called by 4 tests" but grep confirms only 3 direct callers. A 4th test (test_issue17) accesses the method directly without the helper. The practical impact (4 affected tests) is correct, but the wording is slightly misleading.

4. **No DISPUTED findings**: All claims were verifiable against source code. The only discrepancy (F-009) was in test name accuracy, not in the core observation.
