# Phase 4a Duplication Consolidation Review — PROJ-319

**Reviewer:** OpenCode (strict byte-identical behavior verification)  
**Date:** 2026-05-03  
**Scope:** Tasks 4.1–4.7, verifying new shared code produces byte-identical behavior to deleted/inlined originals  
**Verdict scale:** PASS / FAIL / UNCERTAIN

---

## Layer Violation Check (all new modules)

All new modules follow the architecture layering rules in `AGENTS.md` and `docs/01_ARCHITECTURE.md`:

| New module | Layer | Imports from | Higher-layer import? | Verdict |
|---|---|---|---|---|
| `game/strategy/services/race_resolver.py` | Strategy/Services | `game.core.protocols` (Core) | No | PASS |
| `game/ui/widgets/column_toggle_section.py` | UI/Widgets | `pygame_gui` (3rd-party) | No | PASS |
| `game/ui/widgets/range_slider_builder.py` | UI/Widgets | `pygame_gui` (3rd-party) | No | PASS |
| `game/ai/spatial_behaviors/_formation_utils.py` | AI/SpatialBehaviors | `math`, `game.core.math.Vector2` (Core) | No | PASS |
| `game/strategy/data/galaxy_system_generator.py` (new helpers in-file) | Strategy/Data | `game.core.paths`, `game.strategy.services.ability_sources` (same layer) | No | PASS |

**Layer violation verdict: PASS — no violations.**

---

## Task 4.1: Race resolver (DUP-X-01)

**Files:** `game/strategy/services/race_resolver.py` (NEW), `game/strategy/engine/happiness_engine.py:131-141`, `game/strategy/engine/population_engine.py:165-175`

**Pre-change reference:** `git show 1eb325608^:game/strategy/engine/happiness_engine.py` lines ~130-159  
**New code:** `game/strategy/services/race_resolver.py:18-43`

### Verification

1. **Resolution order** — `race_resolver.py:34-43`: Consults `race_registry.get_race(race_id)` first (lines 34-37). Falls back to `empire.race_config` with race_id match guard (lines 38-42). Returns `None` if no registry match and no empire fallback match. **Identical to pre-change body.**

2. **Returns `None` when `empire.race_config is None`** — `race_resolver.py:39-40`: Explicit `if race_config is None: return None`. **Identical to pre-change.**

3. **Returns `None` when `race_config.race_id != race_id`** — `race_resolver.py:41-43`: Checks `race_config.race_id == race_id`, returns `None` on mismatch. **Identical to pre-change.** Does NOT silently return wrong race.

4. **`happiness_engine.py` wrapper** — Lines 131-141: Wrapper method `_get_race_config` delegates to `resolve_race_config(race_id, empire, self._race_registry)`. Correctly threads the instance's `self._race_registry`.

5. **`population_engine.py` wrapper** — Lines 165-175: Same pattern. `resolve_race_config(race_id, empire, self._race_registry)`. Correctly threads `self._race_registry`.

6. **Body comparison** — The pre-change `_get_race_config` in `happiness_engine.py` was a 30-line method body. The new `resolve_race_config` is identical line-for-line, extracted as a standalone function with the same `race_registry` parameter replacing `self._race_registry`.

**Notable:** The `_get_race_config` in `game/ui/screens/strategy_event_router.py:327` is a **different method** (takes a `planet`, returns a `RaceConfig` via empire lookup + RaceLibrary). It is NOT part of this duplication and was correctly left untouched.

**Verdict: PASS**

---

## Task 4.2: Superweapon star-targeted validator (DUP-X-09)

**File:** `game/strategy/validation/superweapon_validator.py`

### Verification

1. **`_validate_star_targeted_superweapon` takes `no_stars_message` parameter** — `superweapon_validator.py:99-122`: Signature includes `no_stars_message: str` (line 103). Used at line 120: `return ValidationResult.error(no_stars_message)`. **Correct.**

2. **`validate_stellerate_star` wrapper** — `superweapon_validator.py:125-135`: Passes `"System has no stars to destroy."` as `no_stars_message` and `"DestroyStar"` as `ability_name`. **Identical to pre-change hardcoded string at old line ~95:** `return ValidationResult.error("System has no stars to destroy.")`.

3. **`validate_create_dyson_sphere` wrapper** — `superweapon_validator.py:223-233`: Passes `"System must have stars to create a Dyson Sphere."` as `no_stars_message` and `"CreateDysonSphere"` as `ability_name`. **Identical to pre-change hardcoded string at old line ~219:** `return ValidationResult.error("System must have stars to create a Dyson Sphere.")`.

4. **Validation logic comparison** — Pre-change both validators had identical 5-line blocks: (1) `_require_ability(fleet, ability_name, component_registry)`, (2) error guard, (3) `_require_at_star_system(galaxy, fleet)`, (4) error guard, (5) `if not system.stars: return ValidationResult.error(...)`, (6) `return ValidationResult.success()`. The new `_validate_star_targeted_superweapon` has the same sequence exactly. **Byte-identical.**

**Verdict: PASS**

---

## Task 4.3: Column toggle section widget (DUP-X-08)

**Files:** `game/ui/widgets/column_toggle_section.py` (NEW), `game/ui/screens/event_log_sidebar.py:58-64`, `game/ui/screens/fleet_report_sidebar.py:317-323`

### Verification

1. **Returns `(new_y, buttons_dict)`** — `column_toggle_section.py:64`: `return y, column_buttons` where `column_buttons` is a `Dict[str, UIButton]`. **Correct.**

2. **`event_log_sidebar.py` merges into `self.column_buttons`** — Line 60-63: `new_y, buttons = build_column_toggle_section(...)` then `self.column_buttons.update(buttons)`. **Correct — preserves the same dict mutation pattern as the old inline code.**

3. **`fleet_report_sidebar.py` merges into `self.column_buttons`** — Line 319-322: Same pattern. `self.column_buttons.update(buttons)`. **Correct.**

4. **Pre-change comparison** — Both old `_build_column_section` methods had identical bodies: `UILabel` for "COLUMNS" label, loop over `column_manager.get_toggleable_columns()`, create `UIButton` per column with `btn.col_ref = col` and `object_id=f"#column_{col_id}"`, store in `self.column_buttons`, return `y`. The new `build_column_toggle_section` replicates all of this exactly, with:
   - Same `Rect` dimensions (`10, y, sidebar_width - 20, 30` for label; `10, y, sidebar_width - 20, 28` for buttons)
   - Same `btn.col_ref = col` pattern
   - Same `object_id=f"#column_{col_id}"` pattern
   - Same y-increments (`+35` after label, `+30` per button, `+20` trailing)
   - Same label text default `"COLUMNS"`
   - **Byte-identical.**

**Verdict: PASS**

---

## Task 4.4: Range slider widget (DUP-X-07)

**Files:** `game/ui/widgets/range_slider_builder.py` (NEW), `game/ui/screens/planet_list_sidebar.py:199-212`, `game/ui/screens/star_list_sidebar.py:94-110`

### Verification

1. **Returns dict with keys `{'min', 'max', 'min_txt', 'max_txt', 'limits'}`** — `range_slider_builder.py:76-82`: The `filter_entry` dict has all five keys. **Correct.**

2. **Both sidebars store as `ui_filters[key]`** — Note: both sidebars use a function-local `ui_filters` dict (not `self.ui_filters` since they're top-level builder functions, not class methods). `planet_list_sidebar.py:201`: `y_off, ui_filters[key] = build_range_slider_row(...)`. `star_list_sidebar.py:96-97`: `y_off, ui_filters[key] = build_range_slider_row(...)`. **Correct — same assignment pattern.**

3. **Pre-change comparison** — The old `add_range` nested functions in both sidebars were **identical** (32 lines each). The new `build_range_slider_row` replicates:
   - Same widget creation order: label → "Min" label → s_min slider → t_min text → "Max" label → s_max slider → t_max text
   - Same `Rect` coordinates: label `(10, y_off, width, 20)`, Min label `(10, y_off, 30, 24)`, slider `(45, y_off, width - 105, 24)`, text entry `(width - 55, y_off, 55, 24)`, identical Max row positions
   - Same `value_range=(min_limit, max_limit)`, same `start_value`: `min_limit` for Min slider, `max_limit` for Max slider
   - Same text initial values: `f"{min_limit:.1f}"` / `f"{max_limit:.1f}"`
   - Same y increments: `+20`, `+29`, `+35`
   - **Byte-identical.**

**Verdict: PASS**

---

## Task 4.5: Galaxy system generator — lazy JSON loader (DUP-X-11)

**File:** `game/strategy/data/galaxy_system_generator.py`

### Verification

1. **`_load_json_or_empty` helper** — `galaxy_system_generator.py:221-232`: Takes `path_value: Any` and optional `dict_key: Optional[str] = None`. Opens file, parses JSON, returns `data` if `dict_key is None`, otherwise `data.get(dict_key, {})`. Returns `{}` if file missing. **Correct.**

2. **`_load_planet_types` caller** — Lines 240-245: Calls `_load_json_or_empty(Paths.PLANET_TYPES_FILE, 'planet_types')`. Pre-change did `data.get('planet_types', {})`. Post-change does `data.get('planet_types', {})` via the `dict_key='planet_types'` path. **Byte-identical.**

3. **`_load_star_types` caller** — Lines 294-299: Calls `_load_json_or_empty(Paths.STAR_TYPES_FILE, 'star_types')`. Pre-change did `data.get('star_types', {})`. Post-change does `data.get('star_types', {})` via `dict_key='star_types'`. **Byte-identical.**

4. **`_load_system_archetypes` caller** — Lines 319-324: Calls `_load_json_or_empty(Paths.SYSTEM_ARCHETYPES_FILE)` with `dict_key=None` (default). Returns full JSON. Pre-change returned `json.load(f)` directly. **Byte-identical.**

5. **Module-level cache variables** — `_PLANET_TYPES_CACHE` (line 237), `_STAR_TYPES_CACHE` (line 291), `_SYSTEM_ARCHETYPES_CACHE` (line 316). All three are still global module-level variables populated on first call and returned on subsequent calls via `if _CACHE is None: _CACHE = _load_json_or_empty(...); return _CACHE`. **Correct — caches preserved and reused.**

6. **Pre-change comparison** — The old `_load_*` functions each had inline `from pathlib import Path; import json; ... ; Path(path); if path.exists(): ...; data.get(...)` blocks. The new helper extracts this to a shared function. The imports (`pathlib.Path`, `json`) moved from per-function lazy imports inside the cache-check block to lazy imports inside `_load_json_or_empty`. Both are lazily imported inside the conditional. **Byte-identical behavior.**

**Verdict: PASS**

---

## Task 4.6: Galaxy system generator — intrinsic abilities (DUP-X-12)

**File:** `game/strategy/data/galaxy_system_generator.py`

### Verification

1. **Lambda type-key extractors** — Planet wrapper (line 286): `lambda p: p.planet_type.name`. Star wrapper (line 311): `lambda s: s.star_type.name`. Pre-change planet loop used `planet.planet_type.name`, star loop used `star.star_type.name`. **Byte-identical — lambdas evaluate to same expression.**

2. **`_apply_planet_intrinsic_abilities` wrapper** — Lines 277-287: Calls `_apply_intrinsic_abilities(planets, _load_planet_types(), lambda p: p.planet_type.name, rng)`. Pre-change had `type_key = planet.planet_type.name`. **Identical.**

3. **`_apply_star_intrinsic_abilities` wrapper** — Lines 302-312: Calls `_apply_intrinsic_abilities(stars, _load_star_types(), lambda s: s.star_type.name, rng)`. Pre-change had `type_key = star.star_type.name`. **Identical.**

4. **Idempotency check** — `_apply_intrinsic_abilities:268`: `if entity.intrinsic_abilities: continue`. Pre-change had identical guard. **Preserved.**

5. **Default `random.Random()` fallback when `rng is None`** — `_apply_intrinsic_abilities:265-266`: `if rng is None: rng = random.Random()`. Pre-change had identical fallback. **Preserved.**

6. **Full logic match** — Pre-change `_apply_planet_intrinsic_abilities` and `_apply_star_intrinsic_abilities` were identical except for the type-key extraction. The new `_apply_intrinsic_abilities` captures all shared logic: `if not types_data: return`, `rng` fallback, `if entity.intrinsic_abilities: continue`, `type_key = get_type_key(entity)`, `template = types_data.get(type_key, {}).get('abilities', {})`, `if not template: continue`, `entity.intrinsic_abilities = roll_intrinsic_abilities(template, rng)`. **Byte-identical.**

**Verdict: PASS**

---

## Task 4.7: Spatial behaviors — circle formation (DUP-X-13)

**Files:** `game/ai/spatial_behaviors/_formation_utils.py` (NEW), `game/ai/spatial_behaviors/escort.py:44-49`, `game/ai/spatial_behaviors/screen.py:51-56`

### Verification

1. **Math correctness** — `_formation_utils.py:32-36`:
   - `total = max(int(total), 1)` — same semantics as old `max(len(group_ships), 1)` since `len()` returns int. The `int(total)` cast is defensive; callers pass `len(group_ships)` which is already int. **Slightly more robust, behaviorally identical.**
   - `angle = (2 * math.pi * slot_index) / total` — identical to pre-change.
   - `Vector2(anchor_x + math.cos(angle) * distance, anchor_y + math.sin(angle) * distance)` — cos applied to x, sin to y. Identical to pre-change `math.cos(angle) * distance` and `math.sin(angle) * distance`. **Correct cos/sin order.**

2. **Escort.py passes `anchor_ship.position`** — Lines 44-49: `anchor_ship.position.x`, `anchor_ship.position.y` (from `kwargs.get("anchor_ship")`). Pre-change did `anchor_ship.position.x + math.cos(angle) * self.distance`. Post-change passes `self.distance` as the `distance` parameter. **Identical.**

3. **Screen.py passes `kwargs['anchor_position']`** — Lines 51-56: `anchor_position.x`, `anchor_position.y` (from `kwargs.get("anchor_position")`). Pre-change did `anchor_position.x + math.cos(angle) * self.radius`. Post-change passes `self.radius` as the `distance` parameter. **Identical.**

4. **No dangling `_compute_circular_position` references** — Grep confirms zero references to `_compute_circular_position` (with leading underscore) in any production `.py` files. The only occurrences are in project manifests and review documents. The function is named `compute_circular_position` (no leading underscore) in `_formation_utils.py:13`. **Clean.**

5. **Math comparison** — Pre-change escort had inline: `total = max(len(group_ships), 1); angle = (2 * math.pi * slot_index) / total; target_x = anchor_ship.position.x + math.cos(angle) * self.distance; target_y = anchor_ship.position.y + math.sin(angle) * self.distance`. Pre-change screen had identical math with `anchor_position` and `self.radius`. The new helper evaluates to the same `Vector2(x, y)` in all cases. **Byte-identical.**

**Verdict: PASS**

---

## Summary

| Task | DUP ID | Verdict | Notes |
|---|---|---|---|
| 4.1 | DUP-X-01 | **PASS** | `resolve_race_config` byte-identical to old `_get_race_config` bodies. Both engines correctly thread `self._race_registry`. |
| 4.2 | DUP-X-09 | **PASS** | `_validate_star_targeted_superweapon` byte-identical to old inline sequences. Both wrappers pass correct messages. |
| 4.3 | DUP-X-08 | **PASS** | `build_column_toggle_section` byte-identical to old `_build_column_section` in both sidebars. |
| 4.4 | DUP-X-07 | **PASS** | `build_range_slider_row` byte-identical to old `add_range` nested functions. Return dict shape matches. |
| 4.5 | DUP-X-11 | **PASS** | `_load_json_or_empty` byte-identical to old inline JSON loading. All three caches still populated and reused. |
| 4.6 | DUP-X-12 | **PASS** | `_apply_intrinsic_abilities` byte-identical. Lambda type extractors match old code. Idempotency + RNG fallback preserved. |
| 4.7 | DUP-X-13 | **PASS** | `compute_circular_position` byte-identical. Both behaviors pass correct anchor + distance. No dangling references. |

**Overall verdict: ALL PASS. No failures, no uncertainties. No layer violations.**

## Notable observation (non-blocking)

In Task 4.7, the helper function is named `compute_circular_position` (no leading underscore), but the module file uses a leading underscore: `_formation_utils.py`. This is a minor naming inconsistency — the PROJ-319 manifest (line 53) references `_compute_circular_position` with a leading underscore on the function name, which does not match the implementation. The behavior is correct; this is a documentation/project-tracking issue only. The function is correctly named with no leading underscore since it's a public API for callers within the `spatial_behaviors` package.
