# PROJ-381 Verification Report

**Source audit:** `Reviews/results/2026-05-07_220225_error-audit/`
**Verification run date:** 2026-05-08
**Method:** 4 parallel `Explore` subagents, one per category batch (exception hygiene / JSON-IO / cross-layer boundaries / LLM-security). Each agent re-read the cited `file:line` against the current source on branch `feat/03c-phase-aware-execution` and returned a verdict + evidence line per item.

**Batch summary:** 30 candidates evaluated → **26 verified / 1 rejected / 1 uncertain (resolved Include) / 2 out-of-scope**.

Severity breakdown of VERIFIED + UNCERTAIN-included (= this project's scope, 27):
- CRITICAL: 1
- MAJOR: 14
- MINOR: 12

---

## Verified (26 items, all entered the project plan)

| ID | Severity | File | Symbol | Current pattern | Recommended pattern | Risk |
|---|---|---|---|---|---|---|
| ERR-01-001 | MAJOR | `game/strategy/formulas/colony_output.py:85` | colony output factor loop | `except Exception as e:` no comment | Add canonical `# Intentional broad catch:` OR narrow to `(KeyError, TypeError, AttributeError)` | Silent species skip on registry bug |
| ERR-01-002 | MAJOR | `game/strategy/engine/commands/registry.py:103,108` | `CommandSpec.__post_init__` | `raise ValueError(...)` | `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value)` | No code/context for handlers |
| ERR-02-001 | MAJOR | `game/assets/asset_manager.py:154` | `load_star_image` fallback | `except Exception as e:` no comment | Narrow to `(FileNotFoundError, pygame.error, ValueError, OSError)` matching `load_planet_image` | Silent swallow of `MemoryError` etc. |
| ERR-02-002 | MAJOR | `game/strategy/data/ship_instance.py:69` | `_build_full_hp_components_from_design` | `except Exception as e:` no comment | Add canonical comment | Silent swallow of unexpected types |
| ERR-02-003 | MAJOR | `game/strategy/engine/turn_state_snapshot.py:56` | `TurnStateSnapshot.capture` | `except Exception as e:` no comment (wraps to PersistenceException correctly) | Add canonical comment — behavior already correct | Pattern lint regression |
| ERR-02-004 | MAJOR | `game/strategy/config/economy_config.py:106` | `load_economy_config` | `data = json.load(fh)` (file-I/O) | `data = load_json(resolved, default={})` from `game.core.json_utils` | Inconsistent error contract |
| ERR-03-001 | MAJOR | `game/strategy/engine/turn_engine.py:279` | `TurnEngine._time_phase` | `except Exception as e:` no comment | Add canonical comment — wrap-and-reraise behavior already correct | Pattern lint regression |
| ERR-03-002 | MAJOR | `game/strategy/engine/turn_engine.py:518` | snapshot capture call | `except Exception:` no comment | Narrow to `except PersistenceException:` (preferred) OR add comment | Pattern lint regression |
| ERR-03-003 | MAJOR | `game/strategy/services/design_validator.py:76` | `validate_design_dict` | `except Exception as e:` no comment | Add canonical comment | Pattern lint regression |
| ERR-03-004 | MAJOR | `game/strategy/services/design_validator.py:92` | sim-validator call | `except Exception as e:` discards validation signals (only `logger.warning`, doesn't append to result) | Add canonical comment AND `result.add_error(...)` | **Real bug** — `is_valid=True` despite failed sim validation |
| ERR-04-001 | MAJOR | `game/ui/screens/battle_setup/controller.py:123` | `scan_designs` loop | `except Exception as e:` no comment | Add canonical comment | Pattern lint regression |
| B-5 | **CRITICAL** | `game/ui/screens/strategy_game_state_manager.py:122-128` | `process_full_turn` | `try/finally` with NO `except` | Add `except EnginePhaseError as e` → modal error dialog | **Game crashes to desktop on any turn-phase failure** |
| B-7 | MAJOR | `game/strategy/engine/conflict_resolution_engine.py:549-565` | `_collect_team_modifiers` | Catches `Exception`, `logger.warning`, returns None | Promote to `logger.error` with hex/empire context; expand intentional-broad-catch comment to enumerate failure modes | Silent strategic-modifier loss |
| B-10 | MAJOR | `game/ui/services/image/background.py:166-201` | `ImageBackgroundCall._run` | Only catches `ImageCancelled`/`ImageException` — non-`ImageException` escape leaks worker thread | Add `ImageUnexpectedError` class + broad catch in `_run` (mirror `LLMUnexpectedError`) | Worker thread leak; status stays RUNNING forever |
| B-11 | MAJOR | `game/strategy/engine/game_session.py:149-158` | `GameSession.__init__` | No try/except around `GameInitializer.initialize()` | Wrap with try/except → null-object recovery state | Partially constructed session on init failure |
| ERR-01-003 | MINOR | `game/strategy/engine/handlers/base.py:181,184,251` | `_resolve_fleet_required` / `_resolve_planet_optional` | 3× `raise ValueError(...)` | `raise ValidationException(..., code=ErrorCode.MISSING_ENTITY.value or OWNERSHIP_MISMATCH)` | No structured handler signal |
| ERR-01-004 | MINOR | `game/simulation/battle_state.py:655-658` | `BattleState.from_json` | `data = json.loads(json_str)` no chaining | Wrap with `try/except json.JSONDecodeError` → `raise PersistenceException(...) from e` | Corrupt-state failures indistinguishable |
| ERR-02-005 | MINOR | `game/strategy/engine/turn_state_snapshot.py:131` | `dump_crash_snapshot` | `json.dump(crash_data, f, indent=2)` (file-I/O) | `save_json(filepath, crash_data, indent=2)` for atomic writes | Partial crash dump on crash mid-write |
| ERR-04-003 | MINOR | `game/strategy/data/galaxy_system_generator.py:229` | `_load_json_or_empty` | `json.load(f)` (file-I/O) | `load_json(path, default={})` | Galaxy-gen crash on corrupt JSON |
| ERR-04-004 | MINOR | `game/strategy/data/galaxy_warp_generator.py:368` | `_load_warp_point_types` | `json.load(f)` (file-I/O) | `load_json(path, default={})` | Galaxy-gen crash on corrupt JSON |
| ERR-04-006 | MINOR | `game/ui/services/tkinter_utils.py:142,175,206,229` | clipboard / file-dialog wrappers | Comments use `# Intentional:` not canonical `# Intentional broad catch:` | Normalize 4 comments | Pattern lint regression |
| ERR-04-008 | MINOR | `game/strategy/data/galaxy_system_generator.py:228-229` | `_load_json_or_empty` | No exception handling around `json.load` | Same fix as ERR-04-003 (`load_json` handles internally) | Galaxy-gen crash on corrupt JSON |
| B-2 | MINOR | `game/strategy/engine/turn_engine.py:285-294` | `_time_phase` context dict | Missing `turn_number` and `save_path` keys | Add both via `getattr` | Crash-dump correlation gap |
| B-4 | MINOR | `game/strategy/facade/strategy_session_facade.py:164-182` | facade `process_turn` | No try/except, no domain conversion | Wrap and re-raise as `TurnFailedError` | Layering — UI sees domain error |
| B-6 | MINOR | `game/strategy/adapters/simulation_adapter.py:236-325` | `_run_simulated_battle` | No try/except around `run_battle()` | Wrap → re-raise with `fleet_ids`, `hex_coord` context | Battle context absent from crash dumps |
| LLM-3 | MINOR | `game/ui/services/image/background.py` | `ImageBackgroundCall` | No `_done_event` / `wait()` parity with `LLMBackgroundCall` | Mirror PROJ-324 Phase 2 pattern | Test-flakiness; no deterministic blocking |

## Rejected (1 item)

| ID | Original audit recommendation | Contrary evidence | Rationale |
|---|---|---|---|
| ERR-03-005 | Add canonical comment to `except Exception:` at `game/ui/screens/transfer_dialog.py:383` (catastrophic dispatch failure handler) | `transfer_dialog.py:373-377` — block-comment explaining the catch-and-rethrow rationale on the lines preceding the `except` | The verifier judged the preceding-line comment block sufficient — the catch is correctly-coded catch-and-rethrow with clear intent, and the only thing flagging it is an automated scanner expecting a same-line comment. Marking REJECTED rather than UNCERTAIN because the verifier had a confident reading. The audit's own scan-format requirement is the lint-level concern, not a real handling defect. |

## Uncertain (resolved)

| ID | Question raised by verifier | User decision |
|---|---|---|
| ERR-04-007 | `star_generation_config.py:192` catches `(ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError)` — narrowing to drop `ValueError` and `KeyError` is defensible but might be intentional defensive caching. Should we narrow? | **Include** — narrow the catch tuple. User accepts that malformed config now raises rather than silently returning defaults. Recorded in `bundling_decisions.md`. |

## Out of Scope (2 items)

| ID | Verifier rationale |
|---|---|
| B-8 | DesignLibrary schema validation is the *caller*'s responsibility, not part of `DesignLoadResult`'s contract. The "missing schema validation" the audit flagged is actually a design choice — schema validation lives in `ShipDesignValidator`. Logging as compliance evidence rather than action. |
| LLM-2 | Audit's own analysis (`findings/llm_context_security.md`) confirms NO actual leak — every `LLMException` subclass message is verified safe (no API keys, request bodies, or response bodies). The recommendation is only verbosity-trim / future-proofing, not a security action. Not actionable in this project. |
