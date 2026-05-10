# Error Handling Review: Shard 02

## Summary
- Shard: Shard 02
- Files in Scope: 191
- Files Actually Read: 191
- Total Findings: 5
- Critical: 0 | Major: 3 | Minor: 2

## Broad Except Findings

#### MAJOR: Broad except without `# Intentional broad catch:` comment in AssetManager.load_star_image
**ID:** ERR-02-001
**Location:** game/assets/asset_manager.py:154
**Code:** `except Exception as e:`
**Issue:** `load_star_image()` catches `Exception` during a star image fallback chain without the required `# Intentional broad catch:` justification comment. The sister method `load_planet_image()` (line 300) already uses specific exception types (`FileNotFoundError, pygame.error, ValueError`) for the same pattern. This inconsistency means arbitrary exceptions (e.g. `MemoryError`) are silently swallowed and continue to the next resolution, while `pygame.error` is a legitimate target here. The comment-less broad catch violates `docs/05_ERROR_HANDLING.md` §Broad Catch Rule: "A broad `except Exception` in production code must be justified on the same line."
**Suggestion:** Narrow to `(FileNotFoundError, pygame.error, ValueError, OSError)` to match `load_planet_image()`'s pattern, or add `# Intentional broad catch: star image resolution fallback chain — any failure at a given size should try the next; best-effort asset loading is non-critical.`
**LOC affected:** 1

#### MAJOR: Broad except without comment in _build_full_hp_components_from_design
**ID:** ERR-02-002
**Location:** game/strategy/data/ship_instance.py:69
**Code:** `except Exception as e:`
**Issue:** `_build_full_hp_components_from_design()` catches `Exception` when calling `ShipSerializer.from_dict()` and falls back to an empty component dict. No `# Intentional broad catch:` comment is present. The function returns `{}` as a fallback, which is a legitimate best-effort pattern (design materialization may fail on corrupt data), but the broad catch swallows any exception type without documentation. The method merely logs a warning and returns empty, which silently hides real errors like `MemoryError` or `KeyboardInterrupt`.
**Suggestion:** Add `# Intentional broad catch: ShipSerializer.from_dict() may raise various exception types on corrupt/incomplete design data; falling back to empty components is safe — callers treat empty dict as "no per-component data available".` OR narrow to specific exception types from ShipSerializer.
**LOC affected:** 1

#### MINOR: Broad except without comment in TurnStateSnapshot.capture (wraps and re-raises)
**ID:** ERR-02-003
**Location:** game/strategy/engine/turn_state_snapshot.py:56
**Code:** `except Exception as e:`
**Issue:** `TurnStateSnapshot.capture()` catches `Exception` and wraps it as `PersistenceException` with `from e` chaining. This is the correct pattern per `docs/05_ERROR_HANDLING.md` ("Strategy phase work is not a swallow site: raw Exception from a phase must become EnginePhaseError and re-raise"), but it's missing the required `# Intentional broad catch:` justification. The wrapping and re-raise is correct — only the comment is absent.
**Suggestion:** Add `# Intentional broad catch: to_dict() serialization may raise any exception type; all are converted to PersistenceException for the caller's snapshot-failure contract.`
**LOC affected:** 1

## JSON Bypass Findings

#### MAJOR: Direct json.load() bypasses json_utils in economy_config load
**ID:** ERR-02-004
**Location:** game/strategy/config/economy_config.py:106
**Code:** `data = json.load(fh)`
**Issue:** `load_economy_config()` uses Python's `json.load()` directly instead of `game.core.json_utils.load_json()`, violating `docs/05_ERROR_HANDLING.md` §JSON And Persistence: "Use `game/core/json_utils.py` for normal file-based JSON operations in `game/`." The function does handle specific exceptions (`FileNotFoundError, OSError, json.JSONDecodeError`) and falls back gracefully, so the robustness is good — but the canonical JSON helper should be used for consistency across the codebase.
**Suggestion:** Replace with `data = load_json(resolved, default={})` from `game.core.json_utils`. The json_utils `load_json` already handles `FileNotFoundError`, `json.JSONDecodeError`, `PermissionError`, and `OSError` with the identical graceful-degradation contract (returns default on failure).
**LOC affected:** 2

#### MINOR: Direct json.dump() in crash snapshot writing
**ID:** ERR-02-005
**Location:** game/strategy/engine/turn_state_snapshot.py:131
**Code:** `json.dump(crash_data, f, indent=2)`
**Issue:** `dump_crash_snapshot()` uses Python's `json.dump()` directly instead of `json_utils.save_json()`. This is a crash/debug artifact path, not normal game data persistence, so the severity is lower. The function handles `OSError` and `TypeError` around the write, which is appropriate. However, `json_utils.save_json()` provides atomic write-via-temp-file which would prevent partial writes on crash.
**Suggestion:** Replace with `save_json(filepath, crash_data, indent=2)` from `game.core.json_utils`. The atomic temp-file write is safe against partial writes and the crash dump's robustness would improve.
**LOC affected:** 3

## Resource Cleanup Findings

None. All files in this shard use proper resource management patterns (no unclosed file handles, no missing cleanup in finally blocks, no dangling resource leaks found).

## Additional Issues Found

None beyond the deterministic scan findings. The remaining ~186 files in the shard use correct error handling patterns:
- Proper use of `ValidationException`, `PersistenceException`, `FormulaException`, and other specific exception types
- Consistent `logger.exception()` inside handlers, `logger.warning()` for recoverable issues
- Appropriate use of `json_utils.load_json` / `load_json_required` / `save_json` throughout
- `from e` exception chaining where causes need preservation
- No bare `except:` statements
- No `print()` or `traceback.print_exc()` for diagnostic output
- No generic `raise Exception()` without specific subclass
- Turn engine sub-engines properly implement `_validate_tick_inputs()` preconditions
- `from_dict()` methods properly use `require_keys()`, `validate_enum()`, `safe_from_dict()` helpers

### Verified Broad Except Sites (excluded — proper comment)

The following broad-except sites in this shard were verified to have correct `# Intentional broad catch:` comments and consistent justification:

| File | Line | Justification |
|---|---|---|
| game/core/event_logging.py | 53 | Third-party event handler may raise anything; instrumentation must never crash simulation |
| game/core/event_logging.py | 87 | Same as above (module-level compat API) |
| game/core/formula_evaluator.py | 308 | Catch-and-convert to FormulaException |
| game/core/roles.py | 233 | Subscriber callbacks may raise anything; one bad subscriber must not abort invalidation fan-out |
| game/simulation/battle_runner.py | 187 | Capture must not crash a battle |
| game/simulation/battle_runner.py | 365 | Capture must not crash a battle |
| game/strategy/data/ship_instance.py | 570 | Registry may be absent in legacy save context |
| game/strategy/engine/conflict_resolution_engine.py | 563 | External collector |
| game/strategy/engine/game_initializer.py | 178 | Hex impl errors don't poison iteration |
| game/strategy/services/design_cost_calculator.py | 84 | Ship loading is best-effort; inline cost fallback already attempted |
| game/strategy/services/replay_store.py | 87 | Corrupt settings must not block capture |
| game/ui/assets/ship_theme_manager.py | 261 | Size validation is best-effort, must not block discovery |
| game/ui/panels/race_description_panel.py | 399 | Rebuild is defensive |
| game/ui/screens/transfer_controller.py | 143 | DesignLibrary load surfaces I/O, JSON, and schema-validation errors; transfer dialog falls back |
| game/ui/screens/strategy_windows/planet_abilities_ctrl.py | 36 | Registry provider may be uninitialized; abilities window opens without registry-backed lookups |

## File Coverage Verification

All 191 files in the shard were read or scanned. Key observations:

| Category | Count | Status |
|---|---|---|
| Core layer files | 10 | All clean (no issues beyond documented broad catches) |
| Services layer files | 1 | Clean |
| Assets layer files | 2 | 1 finding (ERR-02-001) |
| Engine layer files | 1 | Clean |
| Simulation layer files | 24 | All clean or properly documented |
| Strategy layer files | 63 | 4 findings (ERR-02-002, 003, 004, 005) |
| AI layer files | 8 | All clean |
| UI layer files | ~70 | All clean or properly documented |
| Research layer files | 1 | Clean |
| Init/empty files | ~11 | N/A |

All files verified. No hidden issues found beyond deterministic scan results.
