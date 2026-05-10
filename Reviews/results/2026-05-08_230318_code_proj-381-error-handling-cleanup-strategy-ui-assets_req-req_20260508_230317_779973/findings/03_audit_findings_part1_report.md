# Audit Findings Root-Cause Analysis — Part 1

## Summary

ValueError→ValidationException migrations in the strategy layer are mostly complete but
with one missed `ValueError` site in `CommandRegistry.register()` and stale docstrings in
`handlers/base.py`. JSON bypass migrations are fully complete across all six audited
files — every JSON operation routes through the canonical `json_utils.load_json` /
`json_utils.save_json` API with proper atomic-write and graceful-fallback contracts.

---

## ValueError → ValidationException Migrations

### commands/registry.py — `CommandSpec.__post_init__` (ERR-01-002)

**Site 1 (lines 108–120): Invalid category validation**
```python
raise ValidationException(
    message=(...),
    code=ErrorCode.VALIDATION_FAILED.value,  # "V001"
    context={
        "command_class": self.command_class.__name__,
        "category": self.category,
        "allowed": sorted(ALLOWED_CATEGORIES),
    },
)
```
**Site 2 (lines 121–134): Invalid execution_model validation**
```python
raise ValidationException(
    ...,
    code=ErrorCode.VALIDATION_FAILED.value,
    context={
        "command_class": self.command_class.__name__,
        "execution_model": self.execution_model,
        "allowed": sorted(ALLOWED_EXECUTION_MODELS),
    },
)
```

**Assessment: Genuine migration, not a rename.** Both sites carry:
- An `ErrorCode` (`VALIDATION_FAILED.value` = `"V001"`).
- Rich `context` with the offending command class name, the invalid value, and the
  allowed set (sorted for determinism).
- Proper per-site scoped imports inside `__post_init__` to avoid circular dependencies.

The inline comment on line 102–104 explicitly references PROJ-381 Phase 2 ERR-01-002,
confirming this was a deliberate structured-exception migration from a prior
string-only `ValueError`.

**Missed site: `CommandRegistry.register()` (line 191)**
```python
raise ValueError(
    f"Command {name!r} already registered. Pass replace=True "
    f"to override (e.g. for mod overlays)."
)
```
This `ValueError` was **not** migrated to `ValidationException`. It carries no
`ErrorCode` and no `context` dict. It is a duplicate-registration guard triggered
when `register()` is called for a command name that already exists and `replace`
is `False`. This should be a `ValidationException` with a code like
`ErrorCode.DUPLICATE_COMMAND.value` and context carrying `command_name` and
`existing_handler`.

### handlers/base.py (3 sites — ERR-01-003)

**Site 1: `_resolve_fleet_required` — fleet not found (lines 186–190)**
```python
raise ValidationException(
    message="Fleet not found.",
    code=ErrorCode.MISSING_ENTITY.value,
    context={"fleet_id": fleet_id},
)
```

**Site 2: `_resolve_fleet_required` — ownership mismatch (lines 193–197)**
```python
raise ValidationException(
    message="Fleet does not belong to this empire.",
    code=ErrorCode.OWNERSHIP_MISMATCH.value,
    context={"fleet_id": fleet_id, "empire_id": empire_id},
)
```

**Site 3: `_resolve_planet_optional` — planet not found with `required=True` (lines 265–269)**
```python
raise ValidationException(
    message="Planet not found.",
    code=ErrorCode.MISSING_ENTITY.value,
    context={"planet_id": planet_id},
)
```

**Assessment: Genuine migration with full context.** All three sites carry:
- Distinct, appropriate `ErrorCode` values (`MISSING_ENTITY`, `OWNERSHIP_MISMATCH`).
- Meaningful entity identifiers in `context` (`fleet_id`, `planet_id`, `empire_id`).
- Proper `from e` chaining was not applicable here (these are direct raises, not wrapping
  a caught exception).

**Stale docstrings found:**

Two docstrings still reference the old `ValueError` type:

- Line 165 (`_resolve_fleet_required` docstring): "raising **ValueError** if not found"
  — should say `ValidationException`.
- Line 253 (`_resolve_planet_optional` docstring): "If True, raise **ValueError** when
  not found" — should say `ValidationException`.

**Test site context:** No test coverage is needed for docstring correctness, but this is a
documentation drift issue.

---

## JSON Bypass Migrations

### colony_output.py

**No JSON operations present.** File contains pure-function mathematical helpers
(`planet_habitability_multiplier`, `projected_growth_rate`). No `json.load`,
`json.dump`, `save_json`, or `load_json` calls. Not applicable for migration.

### ship_instance.py

**No raw JSON operations.** The file delegates all serialization through
`ShipInstanceSerializer` (`to_dict`, `from_dict`, `to_json`, `from_json`, `clone`).
`ShipInstanceSerializer` is a separate module responsible for JSON encoding, so
this file is a correct delegate with no direct JSON I/O. Not applicable for
migration.

### galaxy_system_generator.py

**Module-level JSON loading — properly migrated (ERR-04-003 + ERR-04-008).**

The `_load_json_or_empty()` wrapper (line 221) routes through `json_utils.load_json`:
```python
from game.core.json_utils import load_json
data = load_json(path_value, default={})
```
Used by three module-level caches: `_load_planet_types()` (PROJ-301),
`_load_star_types()` (PROJ-302), and `_load_system_archetypes()` (PROJ-304). All
correctly use `default={}` for graceful degradation when JSON files are missing
or corrupt. The inline comment explicitly references PROJ-381 Phase 3
ERR-04-003 + ERR-04-008, confirming the migration replaced manual `path.exists()`
guards and raw `json.load` calls.

### galaxy_warp_generator.py

**Module-level JSON loading — properly migrated (ERR-04-004).**

`_load_warp_point_types()` (line 358) routes through `json_utils.load_json`:
```python
from game.core.json_utils import load_json
data = load_json(Paths.WARP_POINT_TYPES_FILE, default={})
_WARP_POINT_TYPES_CACHE = data.get('warp_point_types', {})
```
Uses `default={}` for graceful degradation. Inline comment references
ERR-04-004, confirming the migration removed the prior manual `path.exists()`
guard.

### star_generation_config.py

**No JSON operations in this file.** The `StarGenerationConfig` class receives
pre-parsed `Dict[str, Any]` data from `AstrophysicsLoader.load()`. The
`get_star_generation_config()` function catches `FileNotFoundError` and `OSError`
for graceful fallback but does not perform JSON I/O itself.

**Error catch narrowing (ERR-04-007) is correctly implemented:**
Lines 192–193:
```python
except (ImportError, FileNotFoundError, OSError, TypeError) as e:
```
Previously, `ValueError` and `KeyError` were also caught, which would silently
mask data-integrity bugs. The test file (`test_star_generation_config.py`,
`TestStarGenerationConfigCatchNarrowing`) validates that `ValueError` and
`KeyError` now propagate correctly while `FileNotFoundError` still returns
defaults.

### economy_config.py

**Properly migrated to canonical `json_utils` (ERR-02-004).**

`load_economy_config()` (line 88):
```python
from game.core.json_utils import load_json
data = load_json(resolved, default={})
```
Uses `default={}` for graceful degradation. The inline comment on line 104–107
explicitly references PROJ-381 Phase 2 ERR-02-004. The function correctly handles:
- Missing file → `load_json` returns `{}` → falls back to `DEFAULT_POPULATION_CONSUMPTION`.
- Corrupt JSON → `load_json` returns `{}` → same fallback.
- `population_consumption` not a dict → explicit `isinstance` guard → fallback.

**No `save_json` needed** — economy config is load-only.

### turn_state_snapshot.py

**Properly migrated to canonical `json_utils` for writes (ERR-02-005).**

`dump_crash_snapshot()` (line 128):
```python
from game.core.json_utils import save_json
if save_json(filepath, crash_data, indent=2):
```
Uses `save_json` which provides:
- Atomic write via `.tmp`-then-rename — a mid-write crash no longer leaves a
  partial snapshot file.
- Parent-directory auto-creation.
- `True`/`False` return for success/failure.

The inline comment on lines 128–132 explicitly references ERR-02-005 and notes
that the prior `os.makedirs` call was redundant (now removed). The `restore()`
method does not perform JSON I/O — it uses `from_dict()` deserializers.

---

## Findings

### CRIT-01: `CommandRegistry.register()` still uses bare `ValueError`

- **File:** `game/strategy/engine/commands/registry.py:191`
- **Severity:** Moderate-to-High
- **Issue:** Duplicate-registration guard raises a plain `ValueError` with no
  `ErrorCode` and no `context` dict. This is the only remaining production
  `ValueError` site in the command-registry subsystem after the ERR-01-002
  migration of `CommandSpec.__post_init__`.
- **Impact:** Callers catching `ValidationException` from `seed_default_commands()`
  or `reset_command_registry()` will not catch this duplicate-registration error.
  Automated monitoring/alerts keyed on `ErrorCode` will miss it.
- **Recommendation:** Replace `ValueError` at line 191 with
  `ValidationException(code=ErrorCode.DUPLICATE_COMMAND.value, context={"command_name": name, ...})`.

### CRIT-02: `test_command_handlers.py` ValidationException tests missing code/context assertions

- **File:** `tests/unit/strategy/test_command_handlers.py`
- **Lines:** 551–554 (`test_resolve_fleet_required_raises_when_not_found`),
  572–575 (`test_resolve_fleet_required_validates_ownership`),
  617–620 (`test_resolve_planet_optional_raises_when_not_found_and_required`)
- **Severity:** Moderate
- **Issue:** The three tests correctly check that `ValidationException` is raised
  and that the message contains the expected string, but they do **not** assert on
  `exc_info.value.code` or `exc_info.value.context`. This means a future regression
  that drops the `ErrorCode` or empties the `context` dict would pass these tests.
- **Contrast with `test_base_command_handler.py`:** The parallel tests at lines
  73–95 and 219–229 do assert on code and context. These are the correct pattern.
- **Impact:** Risk of regression where structured error data is accidentally lost
  without test detection.
- **Recommendation:** Add `assert exc.value.code == ErrorCode.MISSING_ENTITY.value`
  and `assert exc.value.context.get("fleet_id") == 999` (or similar) to all three
  test sites. Consolidate with the existing tests in `test_base_command_handler.py`
  to avoid duplication.

### MAJ-01: Stale docstrings reference `ValueError` instead of `ValidationException`

- **File:** `game/strategy/engine/handlers/base.py`
- **Lines:** 165 (`_resolve_fleet_required` docstring says "raising ValueError if not found"),
  253 (`_resolve_planet_optional` docstring says "raise ValueError when not found")
- **Severity:** Low
- **Issue:** Both docstrings were not updated when the ERR-01-003 migration
  replaced `ValueError` with `ValidationException`. The actual code raises
  `ValidationException`, but the docstrings lie.
- **Impact:** Developer confusion — an IDE user reading the docstring will expect
  to catch `ValueError`, not `ValidationException`. This is exactly the kind of
  drift that caused the original PRE-381 error-handling fragility.
- **Recommendation:** Replace `ValueError` with `ValidationException` in both
  docstrings, and add a brief note about the `code` field (e.g., "Raises
  `ValidationException` with code `ErrorCode.MISSING_ENTITY`").

### MAJ-02: `test_command_handlers.py` imports `ValidationException` locally instead of at module top

- **File:** `tests/unit/strategy/test_command_handlers.py`
- **Lines:** 543, 558, 609
- **Severity:** Advisory
- **Issue:** Each test that uses `ValidationException` imports it locally inside
  the test method (`from game.core.exceptions import ValidationException`)
  rather than at the top of the module. The test in
  `test_base_command_handler.py` does the top-level import correctly (line 11).
- **Impact:** Minor inconsistency. Not wrong, but suggests an incremental
  patching approach rather than a fully-integrated migration.
- **Recommendation:** Move `ValidationException` and `ErrorCode` imports to the
  module top in `test_command_handlers.py`, matching the pattern in
  `test_base_command_handler.py`.

### MIN-01: `colony_output.py` and `ship_instance.py` confirmed as non-targets

- **Files:** `colony_output.py`, `ship_instance.py`
- **Issue:** Neither file contains JSON I/O operations. `colony_output.py` is
  pure math; `ship_instance.py` delegates to `ShipInstanceSerializer`.
- **Finding:** Correctly excluded from migration scope. No action needed.

### MIN-02: JSON bypass migration audit — all target files clean

- **Files:** `galaxy_system_generator.py`, `galaxy_warp_generator.py`,
  `star_generation_config.py`, `economy_config.py`, `turn_state_snapshot.py`
- **Issue:** All five files with JSON operations correctly route through
  `json_utils.load_json` / `json_utils.save_json`. No raw `json.load` or
  `json.dump` calls found in any of the six audited production files.
- **Finding:** ERR-02-003, ERR-02-004, ERR-02-005, ERR-04-003, ERR-04-004,
  ERR-04-007 all confirmed complete. No remaining raw JSON bypasses.
