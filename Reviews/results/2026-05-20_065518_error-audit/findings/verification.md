# Verification Report

## Critical Finding Verification

| Finding ID | File | Verdict | Reason |
|------------|------|---------|--------|
| CRITICAL-1 | `game/screen_router.py:209,266` + `new_game_setup_controller.py:186` | CONFIRMED | Both `_on_new_game_start()` (line 209) and `_start_quickstart()` (line 266) call `GameSession(config=...)` without try/except. `on_start_clicked()` at controller.py:186 calls `self._on_start_callback(config)` bare. GameSession constructor catches `SessionInitializationError`, sets null-object state, and re-raises. The exception propagates uncaught through screen_router to `main()` → hard crash log at app.py:518. User sees application crash instead of error dialog. |

## Major Finding Spot-Checks

| Finding ID | File | Verdict | Reason |
|------------|------|---------|--------|
| MAJ-01 (Shard 01) | `game/ui/services/modifier_icon_service.py:81` | CONFIRMED | `except (pygame.error, Exception) as e:` — `Exception` in the tuple has no `# Intentional broad catch:` comment. `pygame.error` alone covers image load/transform; `Exception` is gratuitously broad. |
| MAJ-02 (Shard 01) | `game/ui/screens/battle_state_viewer.py:135` | CONFIRMED | `except json.JSONDecodeError: pass` — silent swallow with no log. If JSON is malformed, diff computation no-ops and panels stay blank with zero feedback. The JSON is in-memory strings from the caller, so blast radius is small but the silent-failure path exists. |
| MAJ-03 (Shard 01) | `game/ui/screens/strategy_detail_formatter.py:355` | CONFIRMED (downgrade to MINOR) | Code matches: `except (TypeError, AttributeError): pass # Mock objects in tests — skip layout`. The report acknowledges the comment exists. The production scenario where real UI objects raise TypeError/AttributeError during `set_relative_position`/`set_dimensions` on CEGUI buttons is extremely low-probability. The comment adequately documents the intent. |
| Report 02 JSON Bypass | `game/strategy/engine/minefield_balance.py:162` | CONFIRMED (downgrade to MINOR) | Code uses `json.load(fh)` directly instead of `json_utils.load_json()`. However, the function has its own comprehensive error handling (FileNotFoundError → default, OSError/JSONDecodeError → default) and deliberately returns default values on failure rather than raising. Switching to `json_utils.load_json` would require wrapping in a try/except for `PersistenceException` — i.e., more code for identical behavior. The violation is stylistic rather than functional. |
| MAJOR-001 (Shard 03) | `game/simulation/replay/replay_serialization.py:115` | CONFIRMED | `raise TypeError(f"boundary_to_dict: unknown BoundaryRegion subtype ...")` — generic built-in exception at a serialization/persistence boundary. Per convention should be `PersistenceException`. |
| MAJOR-002 (Shard 03) | `game/simulation/replay/replay_serialization.py:139` | CONFIRMED | `raise ValueError(f"boundary_from_dict: unknown type {kind!r}")` — generic built-in at a persistence boundary for corrupt/malformed data. Should be `PersistenceException(CORRUPT_DATA)`. |
| MAJOR-003 (Shard 03) | `game/strategy/engine/happiness_engine.py:96` | CONFIRMED | `ValidationException(...)` raised without `code=` parameter. All other engine `_validate_tick_inputs()` methods in the shard include `code=ErrorCode.INVALID_STATE.value`. Inconsistency confirmed. |
| MAJOR-004 (Shard 03) | `game/strategy/data/planetary_facility.py:149` | CONFIRMED | `raise ValueError(f"Unknown resource_id: {resource_id!r}")` — this is a validation check at a validation boundary. Should be `ValidationException`. |
| MAJOR-005 (Shard 03) | `game/strategy/data/ship_stats_cache.py:41` | CONFIRMED | `raise ValueError("ShipInstance requires registries...")` — missing-dependency error. Should be `ValidationException(MISSING_DEPENDENCY)`. |
| MAJOR-006 (Shard 03) | `game/strategy/data/fleet_capability_calculator.py:70,138` | CONFIRMED | Both raise `ValueError` for missing component registry. Both are missing-dependency conditions and should use `ValidationException(MISSING_DEPENDENCY)`. Verified at both line 70 and line 138. |
| MAJOR-007 (Shard 03) | `game/simulation/battle_runner.py:314` | CONFIRMED (line numbers corrected) | Report claimed 2 RuntimeError sites at lines 294 and 314 for both `start_engine_from_spec()` and `run_battle()`. Only 1 `raise RuntimeError` exists in the file — at line 314 in `run_battle()`. Line 294 is mid-docstring. The core finding (RuntimeError for missing-dependency condition) is correct; the 2-site claim is inaccurate. |
| Cross-Layer MAJOR-1 | `game/strategy/engine/turn_engine.py:322-333` | CONFIRMED | `EnginePhaseError` construction at line 322 stores `original_error=str(e)` and `original_type=type(e).__name__` but does NOT inspect `e.__cause__` for a `BattleResolutionError` to merge battle-specific context keys (fleet_ids, empire_ids, hex_coord). Crash dumps lack battle-identifying information. |
| Cross-Layer MAJOR-2 | `game/ui/screens/new_game_setup_controller.py:186` | CONFIRMED | Same root cause as CRITICAL-1. `self._on_start_callback(config)` is called bare with no try/except. Additionally, `self._screen.kill()` at line 187 runs immediately after, so even a caught error would leave the session in an indeterminate state. |

## Downgraded Findings

| Finding ID | Original Severity | New Severity | Reason |
|------------|-------------------|--------------|--------|
| MAJ-03 (Shard 01) | MAJOR | MINOR | Code has explicit comment `# Mock objects in tests — skip layout` documenting the intent. Production UI objects (CEGUI buttons) will not raise TypeError/AttributeError in `set_relative_position`/`set_dimensions` unless there is a far deeper bug. The report itself acknowledges the comment exists. |
| Report 02 JSON Bypass | MAJOR | MINOR | The function has its own correct error handling (returns defaults on FileNotFoundError/OSError/JSONDecodeError). The project rule to use `json_utils.load_json` is a style convention; switching would require wrapping in try/except PersistenceException to preserve the same fallback-to-defaults behavior — net code increase, no correctness gain. |

## Confirmed Critical

1. **CRITICAL-1**: No `SessionInitializationError` catch at `GameSession(...)` construction sites in `screen_router.py:209` and `screen_router.py:266`, and no exception guard at `new_game_setup_controller.py:186`. Session initialization failure propagates uncaught to the top-level `main()` crash handler at `app.py:518`, resulting in a hard application crash (logged as "CRITICAL CRASH") instead of a user-facing error dialog with retry option.

## Verification Coverage

- Critical verified: 1/1 (100%)
- Major spot-checked: 13/13 (100%)

### Notes on verification process
- All CRITICAL site source files were read and compared against the report descriptions.
- 100% of MAJOR findings were spot-checked (13 of 13, exceeding the 30% requirement) by reading the cited source files at the exact line ranges.
- One partial inaccuracy found: MAJOR-007 claims 2 RuntimeError raise sites in `battle_runner.py` but only 1 exists. Core finding remains valid.
- Two findings recommended for downgrade: MAJ-03 and Report 02 JSON Bypass — both are style/convention violations with no correctness impact.
- CRITICAL-1 and Cross-Layer MAJOR-2 share the same root cause (missing SessionInitializationError guard) and should be addressed together.
