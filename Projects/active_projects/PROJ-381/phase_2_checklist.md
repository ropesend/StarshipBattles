# Phase 2: Major — broad-except hygiene, JSON bypass, cross-layer wrappers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-381 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close the 14 verified MAJOR items from audit `2026-05-07_220225_error-audit` — 8 broad-except sites missing the canonical `# Intentional broad catch:` comment (one of which silently swallows validation errors, two of which sit on the snapshot/rollback path), 1 JSON-bypass file-I/O site that should route through `json_utils`, 1 generic `ValueError` raise that should use `ValidationException`, and 3 cross-layer boundary fixes (`ImageUnexpectedError` parity for `ImageBackgroundCall`, `GameSession.__init__` rollback boundary, modifier-collection logging-and-context fix).

---

## Tasks

### Task 2.1: Broad-except in `colony_output.py:85` [Simple]
**File:** `game/strategy/formulas/colony_output.py`
**Tests:** `pytest tests/strategy/formulas/test_colony_output.py`

- [ ] Replace `except Exception as e:` (line 85) with either (a) a narrow `except (KeyError, TypeError, AttributeError) as e:` if the failure modes from `race_registry.get_race(race_id)` are known, OR (b) keep `except Exception` and add the canonical comment on the same line: `except Exception as e:  # Intentional broad catch: race_registry may raise any type from duck-typed get_race; debug-log and skip species to avoid poisoning colony output calculation`. Bump the existing debug log to `logger.warning` if the species is genuinely silently skipped.

### Task 2.2: Broad-except in `commands/registry.py` — replace `ValueError` with `ValidationException` [Simple]
**File:** `game/strategy/engine/commands/registry.py`
**Tests:** `pytest tests/strategy/engine/test_commands_registry.py`

- [ ] Replace `raise ValueError(...)` at line 103 (category validation) with `raise ValidationException(message=..., code=ErrorCode.VALIDATION_FAILED.value, context={"command_class": self.command_class.__name__, "category": self.category})`.
- [ ] Replace `raise ValueError(...)` at line 108 (execution_model validation) with the same pattern keyed by `execution_model`.
- [ ] Add imports for `ValidationException` and `ErrorCode` from `game.core.exceptions` / `game.core.error_codes` if not already present.

### Task 2.3: Broad-except in `asset_manager.py:154` [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/assets/test_asset_manager.py`

- [ ] Either narrow to `except (FileNotFoundError, pygame.error, ValueError, OSError) as e:` to match the sister method `load_planet_image()` at line ~300, OR add the canonical comment to the broad form: `except Exception as e:  # Intentional broad catch: star image resolution fallback chain — any failure at a given size should try the next; best-effort asset loading is non-critical.` Narrowing is preferred for consistency with `load_planet_image()`.

### Task 2.4: Broad-except in `ship_instance.py:69` [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/strategy/data/test_ship_instance.py`

- [ ] Add canonical comment to the broad except at line 69: `except Exception as e:  # Intentional broad catch: ShipSerializer.from_dict() may raise various exception types on corrupt/incomplete design data; falling back to empty components is safe — callers treat empty dict as "no per-component data available".`

### Task 2.5: Broad-except in `turn_state_snapshot.py:56` (wrap-and-reraise) [Simple]
**File:** `game/strategy/engine/turn_state_snapshot.py`
**Tests:** `pytest tests/strategy/engine/test_turn_state_snapshot.py`

- [ ] Add canonical comment to the broad except at line 56: `except Exception as e:  # Intentional broad catch: any to_dict() failure must become SNAPSHOT_FAILED PersistenceException for the turn rollback contract.` The wrap-and-reraise (`raise PersistenceException(...) from e`) already follows the documented strategy-layer pattern — only the comment is missing.

### Task 2.6: JSON bypass in `economy_config.py:106` [Simple]
**File:** `game/strategy/config/economy_config.py`
**Tests:** `pytest tests/strategy/config/test_economy_config.py`

- [ ] Replace `data = json.load(fh)` (line 106) with `data = load_json(resolved, default={})` from `game.core.json_utils`. Remove the manual `with resolved.open(...)` context manager since `load_json` handles file-open + missing-file + corrupt-JSON internally. Drop the now-redundant `(FileNotFoundError, OSError, json.JSONDecodeError)` catch tuple if `load_json`'s graceful-degradation contract covers the same return-default behavior.

### Task 2.7: Broad-except in `turn_engine.py:279` (`_time_phase`) [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/strategy/engine/test_turn_engine.py`

- [ ] Add canonical comment to the broad except at line 279: `except Exception as e:  # Intentional broad catch: wraps unknown phase failures as EnginePhaseError(T001) and re-raises with phase_name + tick context; documented strategy-layer pattern.`

### Task 2.8: Broad-except in `turn_engine.py:518` (snapshot capture) [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/strategy/engine/test_turn_engine.py`

- [ ] Either narrow to `except PersistenceException:` (since `TurnStateSnapshot.capture()` is documented to raise `PersistenceException(T003)`) — this is the preferred fix — OR keep the broad form and add `except Exception:  # Intentional broad catch: snapshot capture failure aborts turn with state-integrity guarantee; any escape from capture must abort.`

### Task 2.9: Broad-except in `design_validator.py:76` [Simple]
**File:** `game/strategy/services/design_validator.py`
**Tests:** `pytest tests/strategy/services/test_design_validator.py`

- [ ] Add canonical comment to the broad except at line 76: `except Exception as e:  # Intentional broad catch: Ship.from_dict may raise various persistence/validation errors; collect as error string in result.` (No behavioral change — the catch already adds the error to the result.)

### Task 2.10: Silent validation swallow in `design_validator.py:92` [Medium]
**File:** `game/strategy/services/design_validator.py`
**Tests:** `pytest tests/strategy/services/test_design_validator.py`

- [ ] Two changes at line 92: (a) add canonical comment `except Exception as e:  # Intentional broad catch: ShipDesignValidator may raise unexpected types; collect as result error rather than crash the validator.` (b) change the body — currently it only logs a warning and discards the failure. Add `result.add_error(f"Sim validation failed: {e}")` (or equivalent) so callers see the validation signal. The current behavior allows `is_valid=True` despite a failed sim validation — this is the actual bug, the missing comment is secondary.
- [ ] Add a test verifying that a `ShipDesignValidator.validate_design()` failure is reflected in the returned `DesignValidationResult` — the test must fail before this fix and pass after.

### Task 2.11: Broad-except in `battle_setup/controller.py:123` [Simple]
**File:** `game/ui/screens/battle_setup/controller.py`
**Tests:** `pytest tests/ui/screens/battle_setup/test_controller.py`

- [ ] Add canonical comment to the broad except at line 123: `except Exception as e:  # Intentional broad catch: corrupt design data must not poison the design library scan — log and skip per file.`

### Task 2.12: B-7 — modifier collection silent loss in `conflict_resolution_engine.py:549-565` [Medium]
**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/strategy/engine/test_conflict_resolution.py`

- [ ] At line 563: change `logger.warning` to `logger.error` (information loss is being demoted to warning today). Include hex coordinate and empire-team identifiers in the log args (`extra={...}` or formatted message).
- [ ] Update the existing `# Intentional broad catch: external collector` comment to enumerate the expected failure modes — e.g. `# Intentional broad catch: external collector may raise any type from non-engine empire/system extensions; ERROR-log and proceed with degraded modifier stack so battle still resolves. Hex + empire context included to allow log-side debugging.`
- [ ] Add a regression test confirming an `ERROR`-level log line with hex/empire context appears when the collector raises.

### Task 2.13: B-10 — `ImageUnexpectedError` parity wrapper in `ImageBackgroundCall._run()` [Medium]
**File:** `game/core/exceptions.py`, `game/ui/services/image/background.py`, `docs/05_ERROR_HANDLING.md`
**Tests:** `pytest tests/ui/services/image/test_background.py`

- [ ] Add `ImageUnexpectedError(ImageException)` class to `game/core/exceptions.py`, mirroring `LLMUnexpectedError` (same constructor signature: takes original exception, stores `original_exception_type` in `context`, redacts message). Add to `__all__`.
- [ ] In `game/ui/services/image/background.py:166-201` (`ImageBackgroundCall._run()`), add a final `except Exception as e:  # Intentional broad catch: provider escape — wrap as ImageUnexpectedError so worker-thread crashes don't leave caller polling forever.` block that wraps the exception as `ImageUnexpectedError`, transitions `_status` to `ERROR`, and stores the wrapper in `_error`. The `finally` block (in-flight slot release) must continue to run.
- [ ] Update `docs/05_ERROR_HANDLING.md:74` (the section that explicitly notes this gap) — replace the "no equivalent image unexpected wrapper today" sentence with the new contract description.
- [ ] Add a regression test that injects a non-`ImageException` from a stub provider and asserts: status transitions to ERROR, `error` is an `ImageUnexpectedError`, `original_exception_type` context key matches the stub exception type.

### Task 2.14: B-11 — `GameSession.__init__` initialization error boundary [Medium]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/strategy/engine/test_game_session.py`

- [ ] Wrap the `GameInitializer.initialize()` call (around line 154) in `try/except`. On failure, ensure the session is in a deterministic null-object state (`galaxy=None` or empty galaxy, `empires=[]`, `turn_number=0`) rather than partially constructed, then re-raise as a descriptive `StrategyException` (or a new `SessionInitializationError(StrategyException)` subclass) preserving `from e` chaining.
- [ ] Add a regression test injecting a `ValidationException` from a stubbed `GameInitializer.initialize()` and asserting the `GameSession` instance does NOT have unset attributes after the catch.

### Task 2.15: Phase verification
**File:** N/A (validation only)
**Tests:** Full sharded suite

- [ ] Verify: `python Tools/test_sharded/test_sharded.py` passes; `grep -rn "except:" game/` returns nothing in modified files; every modified `except Exception` site now has a canonical `# Intentional broad catch:` comment OR has been narrowed to specific exception types; `ImageUnexpectedError` is exported from `game.core.exceptions.__all__`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220225_error-audit/`. See `findings/source_audit.md` for the link._
