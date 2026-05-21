# Verification Report — PROJ-466

**Source audit:** `Reviews/results/2026-05-20_065518_error-audit/`
**Run date:** 2026-05-20
**Verifier:** Claude (independent third pass; a different reader than the OpenCode audit and its internal `findings/verification.md` pass). The `Agent` tool was unavailable in this subagent, so re-verification was done directly by reading each cited `file:line` in the live source on branch `group-b`.
**Batch summary:** 27 verified / 1 rejected / 0 uncertain-unresolved (4 raised, 1 included + 3 deferred) / 4 out-of-scope, out of ~32 candidate items considered.

## Verified

| id | file | symbol | current pattern | recommended pattern | severity | risk |
|----|------|--------|-----------------|---------------------|----------|------|
| CRITICAL-1 | game/screen_router.py:209,266 | _on_new_game_start / _start_quickstart | `GameSession(...)` bare | `except SessionInitializationError` + dialog | CRITICAL | uncaught session-init failure -> hard crash via app.py:518 instead of recoverable dialog |
| XLAYER-MAJ-2 | game/ui/screens/new_game_setup_controller.py:186 | on_start_clicked | `self._on_start_callback(config)` bare, then kill() | catch, keep window alive, set error_label | MAJOR | same root cause; premature kill() leaves session indeterminate |
| XLAYER-MAJ-1 | game/strategy/engine/turn_engine.py:322-333 | _time_phase | `original_error=str(e)` only | merge e.__cause__ BattleResolutionError context | MAJOR | crash dumps lack battle-identifying keys |
| MAJOR-001 | game/simulation/replay/replay_serialization.py:115 | boundary_to_dict | `raise TypeError(...)` | PersistenceException(CORRUPT_DATA) | MAJOR | generic builtin at persistence boundary |
| MAJOR-002 | game/simulation/replay/replay_serialization.py:139 | boundary_from_dict | `raise ValueError(...)` | PersistenceException(CORRUPT_DATA) | MAJOR | generic builtin at persistence boundary |
| MAJOR-003 | game/strategy/engine/happiness_engine.py:96 | _validate_tick_inputs | ValidationException no code= | add code=INVALID_STATE | MAJOR | inconsistent with sibling engines |
| MAJOR-004 | game/strategy/data/planetary_facility.py:149 | _validate_resource_id | `raise ValueError(...)` | ValidationException(RESOURCE_NOT_FOUND) | MAJOR | generic builtin at validation boundary |
| MAJOR-005 | game/strategy/data/ship_stats_cache.py:41 | calculate | `raise ValueError(...)` | ValidationException(MISSING_DEPENDENCY) | MAJOR | generic builtin for missing dependency |
| MAJOR-006 | game/strategy/data/fleet_capability_calculator.py:70,138 | ship_has_spaceyard / _get_registry | `raise ValueError(...)` (2 sites) | ValidationException(MISSING_DEPENDENCY) | MAJOR | generic builtin for missing dependency |
| MAJOR-007 | game/simulation/battle_runner.py:314 | run_battle | `raise RuntimeError(...)` (1 site; audit's 2-site claim corrected) | ValidationException(MISSING_DEPENDENCY) | MAJOR | generic builtin for missing dependency |
| MAJ-01 | game/ui/services/modifier_icon_service.py:81 | load icon | `except (pygame.error, Exception)` no comment | narrow or add # Intentional | MAJOR | gratuitous broad catch |
| MAJ-02 | game/ui/screens/battle_state_viewer.py:135 | show diff | `except json.JSONDecodeError: pass` | log warning + error panels | MAJOR | silent swallow -> blank panels mistaken for "identical" |
| MIN-S3-001 | game/simulation/replay/replay_serialization.py:558-561 | battle_outcome_from_dict | silent `except KeyError` | log warning | MINOR | unknown TelemetryLevel silently accepted |
| MIN-S3-002 | game/assets/asset_manager.py:58-60 | load_manifest | logger.error + silent return | warning or MissingResourceException | MINOR | callers can't distinguish missing vs loaded |
| MIN-S3-003 | game/strategy/services/fleet_write_service.py:57,65 | set_location / set_path | `raise NotImplementedError(...)` | ValidationException(MISSING_DEPENDENCY) | MINOR | config error mislabeled as abstract stub |
| MIN-S3-004 | game/assets/asset_manager.py:319 | load_planet_image | catch tuple missing OSError | add OSError for parity | MINOR | planet path swallows less than star path |
| MIN-S3-005 | game/core/roles.py:61 | RoleRegistryReadOnlyError | inherits Exception | inherit GameException | MINOR | bypasses code/context contract |
| MIN-S3-006 | game/strategy/engine/handlers/construction_queue.py:160 | _check_design_valid | `except (ValueError, KeyError): return True` | add logger.warning | MINOR | corrupt design silently treated valid |
| MIN-S4-1 | game/strategy/data/component_activation_state.py:136-144 | from_dict | bare `data['phase']` KeyError | require_keys + PersistenceException(P003) | MINOR | corrupt save raises raw KeyError |
| MIN-S4-2 | game/strategy/data/component_activation_state.py:77-101 | start_activating / start_deactivating | `raise ValueError(...)` | StateException | MINOR | callers can't discriminate phase error |
| LLM-MIN-1 | game/services/llm/background.py:293 (+ image/background.py:226) | _run | `logger.exception(...: %r, e)` | `%s` | MINOR | third-party exception repr could leak metadata |
| LLM-MIN-2 | game/services/llm/types.py:63 | CompletionResult | default dataclass repr | safe __repr__ | MINOR | repr would dump full LLM response text |
| LLM-MIN-4 | game/services/llm/types.py:41 | Message | default dataclass repr | safe __repr__ | MINOR | repr would dump full prompt content |
| LLM-MIN-3 | game/ui/services/image/types.py:14 | ImageResult | default dataclass repr | safe __repr__ | MINOR | repr would dump binary bytes + revised prompt |
| MIN-S1-03 | game/ui/screens/workshop_data_reloader.py:22-27 | module-level tk_root | duplicate Tk init, never destroyed | use shared get_tk_root() | MINOR | second leaked Tk root |
| JSON-MIN | game/strategy/engine/minefield_balance.py:162 | load_minefield_balance | `json.load(fh)` file I/O | json_utils.load_json | MINOR | direct file-I/O JSON bypass of canonical helper |
| MIN-S3-008 | game/ai/satellite_controller.py:106-109 | _find_nearest_enemy | silent `except AttributeError: return None` | logger.debug | MINOR | (promoted from uncertain) only one of three catches lacking a rationale/diagnostic |

## Rejected

| id | original audit recommendation | contrary-evidence file:line | rationale |
|----|-------------------------------|-----------------------------|-----------|
| MAJ-03 | scope the broad `except (TypeError, AttributeError): pass` in strategy_detail_formatter.py:355 | game/ui/screens/strategy_detail_formatter.py:355 (comment `# Mock objects in tests — skip layout` present) | The audit's own verifier downgraded this to MINOR and acknowledged the comment already documents intent; the production scenario is extremely low-probability. No actionable defect. |

## Uncertain (resolved)

| id | question raised | decision |
|----|-----------------|----------|
| MIN-S3-008 (satellite_controller.py:106-109) | 2 of 3 AttributeError catches have rationale comments; include just the silent get_position site? | **Include** (Phase 3 Task 3.12) — improves observability with no behavior change; matches the asymmetry the audit flagged. Codex concurred (strongest of the four). |
| MIN-S3-007 (construction_queue.py:186) | already logs a warning; only missing an intent comment for the zero-cost fallback — task or drop? | **Defer** — comment-only with little leverage; whether `return {}` cost is intended is a real design question, not a wording cleanup. Codex advised drop; I agree, recording as deferred rather than normalizing the ambiguity. |
| MIN-S1-07 (strategy_screen_assets.py:76) | AttributeError in a narrow typed catch with a logger.warning but no comment — add comment or drop? | **Defer** — already a narrow typed catch + warning; the broad-catch comment rule targets `except Exception`, and graceful degradation for optional art is allowed by docs/05. Codex advised drop; I agree. |
| MIN-S1-01 (star_list_window.py:395) | `except ValueError: pass` on non-numeric UI entry — add debug log or accept? | **Defer** — the audit itself calls this defensible for UI responsiveness; a debug log on routine typing mistakes is noise. Codex advised drop; I agree. |

## Out of Scope

| id | why excluded |
|----|--------------|
| broad-except (128 sites) | All carry valid `# Intentional broad catch:` comments; the scanner's `has_comment=false` is a known 100% false-positive bug per report.md §8. |
| in-memory json (battle_state, etc.) | `json.loads`/`json.dumps` on in-memory strings, no file I/O; `json_utils` offers no in-memory equivalent. |
| app.py:520 traceback diagnostic | Deliberate top-level crash-handler logging (`traceback.format_exc()` for a log string, not `print_exc`). |
| LLM-MIN-5 (request_id) | Doc-only recommendation (document request_id as safe-for-logging); not a code defect. |
