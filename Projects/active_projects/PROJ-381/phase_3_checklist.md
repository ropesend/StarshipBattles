# Phase 3: Minor — context enrichment, comment-format, ValueError narrowing, image parity

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-381 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close the 12 verified MINOR items (11 from audit + 1 user-included from UNCERTAIN: ERR-04-007). Covers 4 JSON-bypass file-I/O sites, 4 generic `ValueError` raises that should be `ValidationException`, 1 over-broad exception tuple, 1 comment-format normalization (`# Intentional:` → `# Intentional broad catch:`), 3 cross-layer context-enrichment items (turn_number/save_path on `EnginePhaseError`, facade-level domain conversion, battle-context preservation in sim adapter), and 1 `ImageBackgroundCall` `wait()`/`_done_event` parity addition.

---

## Tasks

### Task 3.1: ValueError → ValidationException in `handlers/base.py` [Simple]
**File:** `game/strategy/engine/handlers/base.py`
**Tests:** `pytest tests/strategy/engine/handlers/test_base.py`

- [ ] Replace `raise ValueError("Fleet not found.")` at line 181 with `raise ValidationException(message="Fleet not found.", code=ErrorCode.MISSING_ENTITY.value, context={"fleet_id": fleet_id})` in `_resolve_fleet_required`.
- [ ] Replace `raise ValueError("Fleet does not belong to this empire.")` at line 184 with `raise ValidationException(message=..., code=ErrorCode.OWNERSHIP_MISMATCH.value, context={"fleet_id": fleet_id, "empire_id": empire_id})`.
- [ ] Replace `raise ValueError("Planet not found.")` at line 251 with `raise ValidationException(message="Planet not found.", code=ErrorCode.MISSING_ENTITY.value, context={"planet_id": planet_id})` in `_resolve_planet_optional` (or whichever helper line 251 belongs to).
- [ ] Add `ErrorCode` constant for `OWNERSHIP_MISMATCH` if it doesn't already exist in `game/core/error_codes.py`. The `MISSING_ENTITY` value should already exist.

### Task 3.2: PersistenceException wrap on `BattleState.from_json` [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/simulation/test_battle_state.py`

- [ ] Wrap the `data = json.loads(json_str)` line (around 657) in `try: data = json.loads(json_str) except json.JSONDecodeError as e: raise PersistenceException(message=f"Corrupt BattleState JSON: {e}", code=ErrorCode.CORRUPT_DATA.value, context={"json_length": len(json_str)}) from e`. Keep the in-memory `json.loads` itself — this is NOT a json_bypass (no file I/O) — only the missing chaining is the issue.

### Task 3.3: JSON bypass — `dump_crash_snapshot` [Simple]
**File:** `game/strategy/engine/turn_state_snapshot.py`
**Tests:** `pytest tests/strategy/engine/test_turn_state_snapshot.py`

- [ ] Replace `with open(filepath, 'w') as f: json.dump(crash_data, f, indent=2)` at line 131 with `save_json(filepath, crash_data, indent=2)`. The `(OSError, TypeError)` catch can stay or be removed depending on whether `save_json` already handles those — verify against `game/core/json_utils.py`. The win is atomic temp-file write so a crash mid-snapshot doesn't leave a partial file.

### Task 3.4: JSON bypass + missing handler — `_load_json_or_empty` (combines ERR-04-003 + ERR-04-008) [Simple]
**File:** `game/strategy/data/galaxy_system_generator.py`
**Tests:** `pytest tests/strategy/data/test_galaxy_system_generator.py`

- [ ] Replace the `with path.open('r', encoding='utf-8') as f: data = json.load(f)` block (lines 228-229) with `data = load_json(path, default={})` from `game.core.json_utils`. Drop the manual `path.exists()` guard — `load_json` already returns the default on missing files. This single fix closes both ERR-04-003 (json_bypass) and ERR-04-008 (no handler for `json.JSONDecodeError`).

### Task 3.5: JSON bypass — `_load_warp_point_types` [Simple]
**File:** `game/strategy/data/galaxy_warp_generator.py`
**Tests:** `pytest tests/strategy/data/test_galaxy_warp_generator.py`

- [ ] Replace the `with path.open('r', encoding='utf-8') as f: data = json.load(f)` block (lines ~367-368) with `data = load_json(path, default={})`. Drop the manual `path.exists()` guard.

### Task 3.6: Comment-format normalization — `tkinter_utils.py` [Simple]
**File:** `game/ui/services/tkinter_utils.py`
**Tests:** `pytest tests/ui/services/test_tkinter_utils.py`

- [ ] Normalize the 4 comments at lines 142, 175, 206, 229 from `# Intentional:` to the canonical `# Intentional broad catch:` form. Lines 69 and 100 already use the canonical form — match that exact prefix. Comment substance can be preserved (the "file dialog is platform-dependent" / clipboard explanations are already correct).

### Task 3.7: Narrow over-broad exception tuple — `star_generation_config.py:192` [Simple]
**File:** `game/strategy/data/star_generation_config.py`
**Tests:** `pytest tests/strategy/data/test_star_generation_config.py`

- [ ] Remove `ValueError` and `KeyError` from the catch tuple at line 192. Keep `(ImportError, FileNotFoundError, OSError, TypeError)` — `ValueError` and `KeyError` typically indicate data-integrity bugs that should not be silently masked behind a defaults fallback. After this change, malformed config raises an unhandled exception; the cache decorator will retry on next call, and surfacing the failure is preferable to the silent fallback. Add a test confirming a config file with a bad dict shape now raises rather than returning defaults.

### Task 3.8: B-2 — Enrich `EnginePhaseError` context with turn_number + save_path [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/strategy/engine/test_turn_engine.py`

- [ ] In the `_time_phase` wrap (lines 285-294 area where the context dict is constructed), add `"turn_number": getattr(self._session, "turn_number", 0)` and `"save_path": getattr(self._session, "save_path", None)` keys when those attributes are available. Use `getattr` defensively — phase wrapping should NOT raise a secondary error during context construction.
- [ ] Update the regression test from Phase 1 (Task 1.2) — or add a sibling assertion — confirming both keys are present in the raised `EnginePhaseError.context`.

### Task 3.9: B-4 — Facade-level error conversion in `strategy_session_facade.py:164-182` [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`, `game/core/exceptions.py`
**Tests:** `pytest tests/strategy/facade/test_strategy_session_facade.py`

- [ ] Wrap the `session.process_turn(...)` delegate call (lines ~164-182) in `try/except EnginePhaseError as e:`, re-raising as a new `TurnFailedError(StrategyException)` (added to `game/core/exceptions.py`). The new exception preserves `from e` chaining and exposes UI-formatted message fields (failed phase name as a property, recoverable=True flag).
- [ ] Update Phase 1's UI handler (Task 1.1) — if it currently catches `EnginePhaseError`, switch it to catch `TurnFailedError` for cleaner layer separation. The catch in `process_full_turn` should never see a domain `EnginePhaseError` after this fix.

### Task 3.10: B-6 — Battle context preservation in `simulation_adapter.py` [Medium]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/strategy/adapters/test_simulation_adapter.py`

- [ ] In `_run_simulated_battle` (lines 236-325), wrap the `run_battle(...)` call (line ~288) in `try/except SimulationException as e:`. Re-raise either as `EnginePhaseError` (preserving `from e`) with `context={"fleet_ids": [...], "hex_coord": (q, r), "empire_ids": [...]}`, OR add a new `BattleResolutionError(StrategyException)` subclass and re-raise as that. Either choice is fine — the priority is making fleet IDs and hex coordinates survive into crash dumps.
- [ ] Add a regression test injecting a `ValidationException` from a stubbed `run_battle` and asserting the propagated exception's `context` contains both `fleet_ids` and `hex_coord`.

### Task 3.11: LLM-3 — Add `_done_event` and `wait()` to `ImageBackgroundCall` [Medium]
**File:** `game/ui/services/image/background.py`
**Tests:** `pytest tests/ui/services/image/test_background.py`

- [ ] Mirror `LLMBackgroundCall`'s PROJ-324-Phase-2 pattern: in `ImageBackgroundCall.__init__`, add `self._done_event = threading.Event()`. In every terminal branch (`CANCELLED`, `ERROR`, `DONE`, and `cancel()`), call `self._done_event.set()` OUTSIDE the state lock (mirror lines 203 / terminal-state setters in the LLM file).
- [ ] Add a public `wait(self, timeout: float | None = None) -> bool` method that delegates to `self._done_event.wait(timeout)` and returns the boolean result. Match the docstring/signature of `LLMBackgroundCall.wait()` exactly.
- [ ] Add a test that verifies `wait(timeout=0.1)` returns `False` while running and `True` after a terminal transition; verify behaviour after `cancel()` and after a `DONE` provider response.

### Task 3.12: Phase verification
**File:** N/A (validation only)
**Tests:** Full sharded suite

- [ ] Verify: `python Tools/test_sharded/test_sharded.py` passes; the new tests in tasks 3.7, 3.8, 3.10, 3.11 are present and pass; `grep -rn "raise ValueError" game/strategy/engine/handlers/base.py game/strategy/engine/commands/registry.py` returns nothing; `grep -rn "json\.load\b\|json\.dump\b" game/strategy/` returns only documented in-memory or non-game-data sites; the `# Intentional:` (sans "broad catch") form does not appear in `game/ui/services/tkinter_utils.py`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220225_error-audit/`. See `findings/source_audit.md` for the link._
