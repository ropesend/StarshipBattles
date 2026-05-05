# Test Coverage Audit — Shard 06 Skeptical Verification

**Verifier:** Skeptical Verifier (OpenCode)
**Phase 2 report:** `SHARD_06.md` (2026-05-04, 47 files, ~8,495 LOC)
**Verification date:** 2026-05-04
**Methodology:** Read every production file cited, read every corresponding test file, traced code paths for every CRITICAL/MAJOR claim. MINOR claims spot-checked (3 of ~25). ADVISORY claims spot-checked (3 of 14).

---

## Summary

| Verdict | Count |
|---------|-------|
| CONFIRMED (CRITICAL) | 3 |
| CONFIRMED (MAJOR)    | 4 |
| PARTIALLY ACCURATE (MAJOR→MINOR) | 1 |
| DISPUTED (MAJOR→ADVISORY/COVERED) | 2 |
| CONFIRMED (MINOR spot-checks) | 3 |
| DISPUTED (MINOR spot-check) | 1 |

**Overall assessment:** The discovery agent correctly identified the 3 CRITICAL gaps. However, 2 of the 7 MAJOR claims are factually wrong — `star_generation_config.py` and `strategy_screen_lifecycle.py` both have working tests. One MAJOR claim (`projectile.py`) is overstated — the guidance code IS tested indirectly. The telemetry and fleet_capability_calculator claims are directionally correct but imprecise about what's actually tested vs untested.

---

## CRITICAL — CONFIRMED

### 1. `game/simulation/replay/replay_record.py` — Zero Tests
**Verdict:** CONFIRMED — CRITICAL
**Confidence:** HIGH

No test file exists anywhere in the repository matching `test_replay_record*`. The file contains 4 symbols (class + 3 methods) with zero coverage. The dataclass handles serialization/deserialization of the persisted-on-disk replay format (PROJ-312 deliverable).

Production code verified at lines 1-93. No test file found via glob.

### 2. `game/strategy/engine/handlers/movement.py` — Zero Tests
**Verdict:** CONFIRMED — CRITICAL
**Confidence:** HIGH

No test file exists specifically for these command handlers. The three matching test files (`test_movement_and_ai.py`, `test_movement_build_blocking.py`, `test_movement_resources.py`) test unrelated AI movement and fleet resource mechanics — none test `ColonizeCommandHandler`, `MoveCommandHandler`, `InterceptCommandHandler`, `JoinCommandHandler`, or `WarpCommandHandler`.

Production code verified at lines 1-214 (214 LOC, 10 symbols). Five handler classes, all with zero direct coverage.

### 3. `game/strategy/engine/handlers/order_queue.py` — Zero Tests
**Verdict:** CONFIRMED — CRITICAL
**Confidence:** HIGH

No test file exists anywhere in the repository matching `test_order_queue*`. The file contains 5 handler classes (10 symbols) handling fleet composition and order-list mutations. `SplitFleetCommandHandler` is especially risky — it creates new Fleet objects, transfers ships between fleets, and mutates empire registrations.

Production code verified at lines 1-212 (212 LOC, 10 symbols). Zero direct coverage.

---

## MAJOR — CONFIRMED

### 4. `game/simulation/combat/telemetry.py` — 3 Private Methods Under-tested
**Verdict:** CONFIRMED — MAJOR
**Confidence:** HIGH (with nuance)

**Discovery agent claim:** `ShipStatsAggregator._on_damage_event`, `HitLogRecorder._on_hit_event`, `HitLogRecorder._trace_modifiers_for_team` are untested.

**Verification:**
- `test_telemetry.py` (44 lines): Tests **only** the `TelemetryLevel` enum (4 tests). None of the three subscriber classes are touched.
- `test_ship_stats_aggregator.py` (180 lines): Tests `ShipStatsAggregator` via public API (`get_stats`, `sample_tick`, `snapshot`). The `_on_damage_event` callback IS exercised **indirectly** through `CombatEventBus.emit()` calls. But **3 specific edge branches are never triggered:**
  - `target_ship=None` → early return (line 150-151)
  - `instance_id=None` → early return (line 153-154)
  - `damage <= 0` → early return (line 156-157)
- `test_hit_log_recorder.py` (170 lines): Tests `HitLogRecorder` via public API. `_on_hit_event` IS exercised **indirectly**, including the `context=None` branch (line 161 of test file). But **untested branches:**
  - `_trace_modifiers_for_team()` with `modifier_stack is not None` (lines 337-358 of production code) — entirely untested
  - `attacker_team_id=None` in `_trace_modifiers_for_team` (line 340-343)
  - Placeholder effect filtering with non-empty stat_key (line 351)

**Nuance:** The phrase "3 untested symbols" is imprecise. The symbols ARE exercised indirectly. It's specific edge branches within those symbols that are untested. MAJOR severity is appropriate because the untested branches include the entire `_trace_modifiers_for_team` non-None path.

### 5. `game/strategy/data/fleet_capability_calculator.py` — `list_abilities()` Untested
**Verdict:** CONFIRMED — MAJOR
**Confidence:** HIGH

**Discovery agent claim:** `_get_ship_component_registry`, `_get_registry`, `list_abilities` have untested branches.

**Verification:**
- `list_abilities()` (line 244-264): **TRULY UNTESTED.** Grep across all test files confirms zero calls to `list_abilities()`. The only reference in tests is a mocked-out stub (`fleet.capabilities.list_abilities = Mock(return_value=[])` in `test_strategy_session_facade.py:38`). The real implementation has never been exercised.
- `_get_ship_component_registry()` (line 18-34): One branch untested — the fallback `return None` when `_registries` is None or missing. All existing tests supply registries via DI.
- `_get_registry()` (line 118-139): **MOSTLY COVERED.** The constructor-injection branch (line 128-129) is tested in `test_fleet_capability_calculator_di.py`. The ship-registry fallback (lines 131-134) is exercised by standard tests. The ValueError branch (line 135-138) is unreachable by existing test patterns because `space_shipyard_count` short-circuits with `return 0` before calling `_get_registry()` when the fleet has no combat ships.

**Refinement to agent claim:** The primary gap is `list_abilities()` (zero coverage). The other two functions have minor untested branches. MAJOR severity is appropriate for `list_abilities()` alone.

### 6. `game/strategy/engine/turn_state_snapshot.py` — `dump_crash_snapshot()` Untested
**Verdict:** CONFIRMED — MAJOR
**Confidence:** HIGH

Production code lines 102-134: `dump_crash_snapshot()` writes crash forensic data to disk. Branches include `os.makedirs` (line 129), `json.dump` (line 131), and `OSError/TypeError` catch (line 133).

**Verification:** `test_turn_state_snapshot.py` (156 lines) tests `capture()` and `restore()` extensively (10 tests), but **never calls `dump_crash_snapshot()`**. The integration test `test_turn_engine_snapshot_integration.py` calls it only on a **MagicMock fake snapshot** — the real implementation with its file-system I/O and error handling is never exercised. MAJOR is appropriate: this is the crash-forensics path for PROJ-251.

### 7. `game/ui/screens/list_data_source_base.py` — Zero Direct Tests
**Verdict:** CONFIRMED — MAJOR
**Confidence:** HIGH

Production code lines 1-104: `ListDataSource` abstract base class with `_extract_value()` containing complex branch logic (func, attr with dot-path, fmt formatting at lines 80-95). No test file matching `test_list_data_source*` exists. No test file references `ListDataSource` directly.

The class IS exercised indirectly through `PlanetDataSource` and `StarDataSource` subclass tests, but the base class's own branch logic (especially `_extract_value`) lacks direct coverage. MAJOR severity is appropriate for Tier 0 non-UI Python logic with no pygame dependency.

---

## MAJOR — PARTIALLY ACCURATE (Downgrade to MINOR)

### 8. `game/simulation/entities/projectile.py` — `_update_guidance()` Under-tested
**Verdict:** PARTIALLY ACCURATE — DOWNGRADE TO MINOR
**Confidence:** HIGH

**Discovery agent claim:** `Projectile._update_guidance()` untested. MAJOR severity.

**Verification:** `test_projectile.py` (717 lines) has a dedicated `TestMissileGuidance` class (lines 550-662) with 5 tests:
- `test_missile_turns_toward_target`: Exercises the core guidance path (leads target, rotates velocity)
- `test_missile_ignores_dead_target`: Tests `target.is_alive=False` → guidance bypassed (line 104 guard)
- `test_missile_ignores_none_target`: Tests `target=None` → guidance bypassed
- `test_non_missile_does_not_guide`: Tests non-MISSILE type → guidance bypassed
- `test_last_turn_direction_tracking`: Initial state assertion

These tests exercise `_update_guidance()` **indirectly** through `update()` and cover several key branches. The guidance IS tested — it's not "untested."

**What remains untested (6 specific math branches):**
1. `owner=None` with lead solver (line 149) — no test with owner=None for a MISSILE type
2. `t > 0` predictive lead (line 153-154) — mock always returns 0
3. `desired_vec.length_squared() == 0` at same position (line 157)
4. `abs(angle_diff) > max_turn_step` turn-rate clamping (line 166-167) vs `abs(angle_diff) <= max_turn_step` (line 169)
5. Turn commitment threshold with `last_turn_direction != 0` (lines 174-175)
6. `turn_rate=0` → no rotation (line 164 → 0 turn step)

These are legitimate gaps but represent edge-case math branches, not a completely untested algorithm. **Downgrade from MAJOR to MINOR.**

---

## MAJOR — DISPUTED

### 9. `game/strategy/data/star_generation_config.py` — 3 Symbols Claimed Untested
**Verdict:** DISPUTED — DOWNGRADE TO ADVISORY (effectively COVERED)
**Confidence:** HIGH

**Discovery agent claim:** `__init__`, `_load_from_json`, `_use_defaults` are untested. MAJOR severity. Agent states: "Existing test... only covers the factory wrapper, not the config class internals."

**Verification — this claim is FACTUALLY WRONG:**

`test_star_generation_config.py` (220 lines) has **two dedicated test classes** that directly construct `StarGenerationConfig`:

- `TestStarGenerationConfigDefaults` (7 tests, lines 18-101):
  - `test_init_no_data_uses_defaults` (line 21): Constructs `StarGenerationConfig(None)` → exercises `__init__` → `_use_defaults()`. Validates 8 type weights, mass params, age params.
  - `test_default_system_count_thresholds` (line 61): Validates `_use_defaults()` assigns correct threshold values.
  - `test_default_companion_spacing` (line 71): Validates companion spacing defaults.
  - `test_default_stefan_boltzmann_types` (line 80): Validates Stefan-Boltzmann type tables from `_use_defaults()`.

- `TestStarGenerationConfigFromJson` (4 tests, lines 104-186):
  - `test_init_with_json_data` (line 107): Constructs `StarGenerationConfig(data)` → exercises `__init__` → `_load_from_json()`. Validates JSON values loaded.
  - `test_json_overrides_defaults` (line 140): Tests JSON merge-over-default behavior in `_load_from_json()`.
  - `test_partial_json_falls_back_to_defaults` (line 159): Tests `.get()` fallback chains in `_load_from_json()` when only `mass_generation` section provided.
  - `test_no_star_generation_key_uses_defaults` (line 178): Tests data dict without `"star_generation"` key → falls to `_use_defaults()`.

**All three symbols are directly and thoroughly tested.** The agent's claim that tests "only cover the factory wrapper" is incorrect — the test file constructs `StarGenerationConfig` instances directly and validates their internal attributes. **Downgrade to ADVISORY** (effectively COVERED, only remaining gap is partial `stefan_boltzmann_types` JSON loading — the production code at line 151 always uses defaults for that section regardless of JSON input).

### 10. `game/ui/screens/strategy_screen_lifecycle.py` — All 8 Functions Claimed Untested
**Verdict:** DISPUTED — DOWNGRADE TO COVERED
**Confidence:** HIGH

**Discovery agent claim:** 8 untested symbols, MAJOR severity. "All 8 functions untested."

**Verification — this claim is FACTUALLY WRONG:**

`test_strategy_screen_lifecycle.py` (163 lines) has **6 dedicated test classes** covering **all 8 functions:**

| Function | Test Method(s) | Verified? |
|----------|---------------|-----------|
| `on_design_click` | `TestOnDesignClick` (2 tests) | Lines 28-42 |
| `on_menu_option` | `TestOnMenuOption` (7 tests for all 6 branches + unknown) | Lines 45-84 |
| `show_load_game_dialog` | `TestLoadGameDialog.test_show_load_game_dialog_creates_window` | Lines 88-97 |
| `on_load_selected` | `TestLoadGameDialog.test_on_load_selected_calls_callback` | Lines 99-104 |
| `confirm_quit_to_menu` | `TestQuitConfirmation.test_confirm_quit_creates_dialog` | Lines 113-118 |
| `handle_quit_confirmed` | `TestQuitConfirmation.test_handle_quit_confirmed_clears_and_callbacks` | Lines 121-126 |
| `show_coming_soon` | `TestComingSoon.test_show_coming_soon_creates_message_window` | Lines 130-137 |
| `on_save_game_click` | `TestSaveGameClick` (2 tests: success + failure) | Lines 140-163 |

All tests use `MagicMock` screens with mocked dependencies (pygame_gui, SaveGameService). Every branch including save success/failure is covered. **Downgrade to COVERED.**

---

## MINOR Spot-Checks (3 of ~25)

### 11. `game/core/math.py:normalize_angle()` — Zero Direct Tests
**Verdict:** CONFIRMED — MINOR
**Confidence:** HIGH

Grep confirms zero test files reference `normalize_angle`. Production code at lines 235-248: simple angle normalization (mod 360, wrap to (-180, 180]). No edge-case tests (0, 180, -180, 360, large values). MINOR severity is appropriate.

### 12. `game/strategy/data/design_metadata.py:_calculate_construction_cost_from_ship()` — Zero Direct Tests
**Verdict:** CONFIRMED — MINOR
**Confidence:** MEDIUM

Grep confirms zero test files reference the function. MINOR severity appropriate.

### 13. `game/strategy/facade/dto/fleet_dto.py:_aggregate_carried_items()` — Zero Direct Tests
**Verdict:** CONFIRMED — MINOR
**Confidence:** MEDIUM

Grep confirms zero test files reference the function. MINOR severity appropriate.

---

## MINOR Spot-Check — DISPUTED

### 14. `game/ui/components/filters/tri_state_widget.py:_update_visuals()` — Claimed Untested
**Verdict:** PARTIALLY ACCURATE — tested indirectly

Grep confirms zero test files directly call `_update_visuals()`. However, the test `test_tri_state_widget.py` calls `set_state()` and `check_pressed()` which internally call `_update_visuals()`. The method IS exercised indirectly. The agent's characterization as "untested" is overstated but not entirely wrong — no edge-case test (e.g., all three FilterState values producing correct button mappings).

---

## Error Rates — Detection Accuracy

| Claim Type | Total | Confirmed | Partially Accurate | Disputed | Error Rate |
|------------|-------|-----------|-------------------|----------|------------|
| CRITICAL   | 3     | 3         | 0                 | 0        | 0%         |
| MAJOR      | 7     | 4         | 1                 | 2        | 29%        |
| MINOR (spot) | 4   | 3         | 1                 | 0        | 0%         |

**Discovery agent errors:**
1. **`star_generation_config.py`** — False negative. All 3 claimed-untested symbols are actually tested. Root cause: agent read the file but failed to notice the test classes construct `StarGenerationConfig` directly (not just via the cached factory). Lines 21, 107, 140, 159 of the test file all construct the config class directly.
2. **`strategy_screen_lifecycle.py`** — False negative. All 8 claimed-untested functions have comprehensive tests. Root cause: agent likely conflated "Tier 0" classification (non-UI) with test existence and didn't verify the test file content.
3. **`projectile.py`** — Overstated severity. `_update_guidance()` IS tested indirectly through `update()`. Agent characterized it as completely untested when 5 dedicated test methods exercise it. The gap is specific math branches, not the entire function.

---

## Final Severity Reclassification

| File | Original | Verified | Notes |
|------|----------|----------|-------|
| `replay_record.py` | CRITICAL | **CRITICAL** | No tests exist |
| `movement.py` | CRITICAL | **CRITICAL** | No tests exist |
| `order_queue.py` | CRITICAL | **CRITICAL** | No tests exist |
| `telemetry.py` | MAJOR | **MAJOR** | Private method edge branches untested |
| `projectile.py` | MAJOR | **MINOR** | Guidance IS tested indirectly; 6 math branches only |
| `fleet_capability_calculator.py` | MAJOR | **MAJOR** | `list_abilities()` zero coverage |
| `star_generation_config.py` | MAJOR | **ADVISORY** | All symbols already tested; agent misread |
| `turn_state_snapshot.py` | MAJOR | **MAJOR** | Crash forensics path untested |
| `strategy_screen_lifecycle.py` | MAJOR | **COVERED** | All 8 functions tested; agent misread |
| `list_data_source_base.py` | MAJOR | **MAJOR** | No direct tests for complex branch logic |
