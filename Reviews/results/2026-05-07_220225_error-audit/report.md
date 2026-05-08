# Error Handling & Robustness Audit Report

> **Date:** 2026-05-07
> **Review directory:** `Reviews/results/2026-05-07_220225_error-audit/`
> **Scope:** 749 production files across `game/` (all layers)

---

## 1. Executive Summary

**Total unique findings: 28** (after deduplication across shards and cross-cutting reports)

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Major | 13 |
| Minor | 14 |

**Error hygiene by layer:**

| Layer | Broad Except Gaps | JSON Bypass | Other Issues | Overall |
|-------|------------------|-------------|--------------|---------|
| Core | 0 | 0 | 0 | Clean |
| Services | 0 | 0 | 1 Major (Image escape wrapper) | Good |
| Assets | 1 Major | 0 | 0 | Needs 1 fix |
| Engine | 0 | 0 | 0 | Clean |
| Simulation | 0 | 0 | 1 Minor | Good |
| Research | 0 | 0 | 0 | Clean |
| Strategy | 6 Major + 1 Minor | 2 Major + 3 Minor | 2 Minor | Needs work |
| AI | 0 | 0 | 0 | Clean |
| UI | 1 Major | 0 | 3 Minor | Good |

The codebase has strong error handling fundamentals: zero bare excepts, zero generic `raise Exception`, zero `print()/traceback.print_exc()` diagnostic leakage (1 site in top-level app.py crash handler is intentional). All 75 broad-except sites from the deterministic scanner have `# Intentional` comments or legitimate rationale — only 11 genuinely lack the required comment.

---

## 2. Coverage Status

| Shard | Files | Review File | Status |
|-------|-------|-------------|--------|
| Shard 01 | 176 | `findings/error_review_01.md` — 4 findings | Complete |
| Shard 02 | 191 | `findings/error_review_02.md` — 5 findings | Complete |
| Shard 03 | 190 | `findings/error_review_03.md` — 5 findings | Complete |
| Shard 04 | 192 | `findings/error_review_04.md` — 8 findings | Complete |
| Cross-layer | — | `findings/error_propagation_cross_layer.md` — 8 findings | Complete |
| LLM Security | — | `findings/llm_context_security.md` — 3 findings | Complete |
| Verification | — | `findings/verification.md` — all CRITICAL confirmed | Complete |

---

## 3. Error Hygiene Scorecard

| Category | Raw Scan | Verified Findings | Critical | Major | Minor |
|----------|----------|-------------------|----------|-------|-------|
| Broad except w/o comment | 75 scanned | 11 (10 unique) | 0 | 8 | 3 |
| Bare except | 0 | 0 | 0 | 0 | 0 |
| JSON bypass | 7 scanned | 5 (4 unique) | 0 | 1 | 4 |
| Generic raise Exception | 0 | 0 | 0 | 0 | 0 |
| Print/traceback debug | 1 | 0 (intentional) | 0 | 0 | 0 |
| Resource cleanup gaps | — | 0 | 0 | 0 | 0 |
| Additional error handling issues | — | 9 | 0 | 3 | 6 |
| Cross-layer error propagation | — | 8 | 1 | 3 | 4 |
| LLM context security | — | 3 | 0 | 1 | 2 |
| **TOTAL** | — | **28** | **1** | **13** | **14** |

---

## 4. Cross-Layer Error Propagation Issues

The cross-layer validator traced 5 critical paths and audited 11 error boundaries:

**CRITICAL — B-5: Missing UI error boundary for turn processing failures**
- `game/ui/screens/strategy_game_state_manager.py:86-167` — `process_full_turn()` has only a `finally` block, no `except EnginePhaseError` handler
- Turn failures crash the game via `app.py`'s top-level handler instead of showing an in-game error dialog
- State rollback works correctly at the TurnEngine level — the gap is purely at the UI boundary
- **Verified: CONFIRMED** (fully traced 6-link call chain)

**MAJOR — B-7: Silent modifier collection failure**
- `game/strategy/engine/conflict_resolution_engine.py:549-565` — modifier collection catches `Exception`, logs warning, returns None
- Battle proceeds without strategic modifiers on any collection failure — information loss
- Should log at ERROR level and include hex/empire context

**MAJOR — B-10/B-11: ImageBackgroundCall lacks escape wrapper**
- `game/ui/services/image/background.py:166-194` — catches only `ImageCancelled`/`ImageException`
- Non-ImageException provider escapes crash the worker thread silently
- LLM counterpart (`LLMBackgroundCall._run()`) already has `LLMUnexpectedError` safety net

**MINOR — B-2:** `process_turn()` crash context missing `turn_number` and `save_path`
**MINOR — B-4:** Facade doesn't convert domain errors for UI consumption
**MINOR — B-6:** Battle-specific context (fleet IDs, hex coords) lost at `_time_phase()` boundary
**MINOR — B-8:** `DesignLoadResult` doesn't perform schema validation

---

## 5. Prioritized Remediation Plan (Top 10)

Ordered by severity × layer criticality × LOC affected:

| Rank | ID | Severity | Location | Issue | LOC |
|------|-----|----------|----------|-------|-----|
| 1 | B-5 | **CRITICAL** | `ui/strategy_game_state_manager.py:86-167` | Missing UI error boundary — turn failures crash to desktop | ~5 |
| 2 | B-7 | MAJOR | `strategy/engine/conflict_resolution_engine.py:549-565` | Silent modifier collection swallow — battles lose effects | ~3 |
| 3 | B-10/LLM-1 | MAJOR | `ui/services/image/background.py:166-194` | `ImageBackgroundCall` missing `ImageUnexpectedError` safety net | ~6 |
| 4 | ERR-03-004 | MAJOR | `strategy/services/design_validator.py:92` | Silent validation swallow — design failures hidden from result | ~1 |
| 5 | ERR-03-001 | MAJOR | `strategy/engine/turn_engine.py:279` | `_time_phase()` broad except missing Intentional comment | 1 |
| 6 | ERR-03-002 | MAJOR | `strategy/engine/turn_engine.py:518` | Snapshot capture broad except missing comment | 1 |
| 7 | ERR-02-001 | MAJOR | `assets/asset_manager.py:154` | Asset load broad except missing comment | 1 |
| 8 | ERR-02-002 | MAJOR | `strategy/data/ship_instance.py:69` | Design materialization broad except missing comment | 1 |
| 9 | ERR-02-004 | MAJOR | `strategy/config/economy_config.py:106` | Direct `json.load()` bypass of `json_utils` | 2 |
| 10 | ERR-01-001 | MAJOR | `strategy/formulas/colony_output.py:85` | Broad except missing comment in colony output calc | 1 |

---

## 6. Trend Comparison

| Category | Previous Run | This Run | Delta |
|----------|-------------|----------|-------|
| Critical | — (first run) | 1 | n/a |
| Major | — | 13 | n/a |
| Minor | — | 14 | n/a |

This is the inaugural error audit run. No prior baseline exists.

---

## 7. Detailed Findings Index

### Broad Except Findings (missing Intentional comment)

| ID | Severity | File | Line | Issue |
|----|----------|------|------|-------|
| ERR-01-001 | MAJOR | `game/strategy/formulas/colony_output.py` | 85 | Missing comment; debug-log-and-continue pattern |
| ERR-02-001 | MAJOR | `game/assets/asset_manager.py` | 154 | Missing comment in `load_star_image` fallback chain |
| ERR-02-002 | MAJOR | `game/strategy/data/ship_instance.py` | 69 | Missing comment in design materialization fallback |
| ERR-02-003 | MINOR | `game/strategy/engine/turn_state_snapshot.py` | 56 | Missing comment (correct wrap-and-re-raise pattern) |
| ERR-03-001 | MAJOR | `game/strategy/engine/turn_engine.py` | 279 | Missing comment in `_time_phase()` wrap |
| ERR-03-002 | MAJOR | `game/strategy/engine/turn_engine.py` | 518 | Missing comment at snapshot capture boundary |
| ERR-03-003 | MAJOR | `game/strategy/services/design_validator.py` | 76 | Missing comment on design loading validation |
| ERR-03-004 | MAJOR | `game/strategy/services/design_validator.py` | 92 | Missing comment + **silently swallows** validation failures |
| ERR-03-005 | MAJOR | `game/ui/screens/transfer_dialog.py` | 383 | Comment on preceding lines, not on `except` line |
| ERR-04-001 | MAJOR | `game/ui/screens/battle_setup/controller.py` | 123 | Missing comment in design scan loop |

### JSON Bypass Findings

| ID | Severity | File | Line | Issue |
|----|----------|------|------|-------|
| ERR-02-004 | MAJOR | `game/strategy/config/economy_config.py` | 106 | `json.load()` instead of `load_json()` |
| ERR-02-005 | MINOR | `game/strategy/engine/turn_state_snapshot.py` | 131 | `json.dump()` instead of `save_json()` in crash dump |
| ERR-04-003 | MINOR | `game/strategy/data/galaxy_system_generator.py` | 229 | `json.load()` — no error handling for corrupt JSON |
| ERR-04-004 | MINOR | `game/strategy/data/galaxy_warp_generator.py` | 368 | `json.load()` — same pattern |
| ERR-04-005 | MINOR | `game/strategy/engine/turn_state_snapshot.py` | 131 | (duplicate of ERR-02-005) |

### Additional Issues (non-broad-except, non-JSON)

| ID | Severity | File | Line | Issue |
|----|----------|------|------|-------|
| ERR-01-002 | MAJOR | `game/strategy/engine/commands/registry.py` | 103,108 | `ValueError` → should be `ValidationException` |
| ERR-01-003 | MINOR | `game/strategy/engine/handlers/base.py` | 181,184,251 | `ValueError` → `ValidationException` |
| ERR-01-004 | MINOR | `game/simulation/battle_state.py` | 655-658 | `from_json()` missing `PersistenceException` wrap |
| ERR-04-006 | MINOR | `game/ui/services/tkinter_utils.py` | 142,175,206,229 | Comment says "Intentional:" not "Intentional broad catch:" |
| ERR-04-007 | MINOR | `game/strategy/data/star_generation_config.py` | 192 | Over-broad specific exception tuple |
| ERR-04-008 | MINOR | `game/strategy/data/galaxy_system_generator.py` | 228-229 | Uncaught `json.JSONDecodeError` |

### Cross-Layer Propagation Findings

For full details see `findings/error_propagation_cross_layer.md`.

| ID | Severity | Boundary | Issue |
|----|----------|----------|-------|
| B-5 | CRITICAL | UI turn processing | No `except EnginePhaseError` handler |
| B-7 | MAJOR | Conflict resolution | Silent modifier swallow |
| B-10 | MAJOR | Image background | Missing escape wrapper |
| B-11 | MAJOR | Game initialization | Partial object on construction failure |
| B-2 | MINOR | Turn engine | Missing context keys |
| B-4 | MINOR | Facade | No domain error conversion |
| B-6 | MINOR | Simulation adapter | Battle context lost |
| B-8 | MINOR | Design library | No schema validation |

### LLM Context Security Findings

For full details see `findings/llm_context_security.md`.

| ID | Severity | Site | Issue |
|----|----------|------|-------|
| LLM-1 | MAJOR | ImageBackgroundCall | Missing `ImageUnexpectedError` safety net |
| LLM-2 | MINOR | RaceDescriptionLLMController | Verbose `call.error` in log |
| LLM-3 | MINOR | ImageBackgroundCall | Missing `_done_event` / `wait()` |

**No API keys, tokens, request bodies, or prompts leak** into logs or exception context anywhere in the codebase.  All 17 audited LLM/image sites pass content security checks.

---

## 8. Positive Findings

The codebase demonstrates strong error handling discipline across all layers:

- **Zero bare `except:` clauses** across all 749 production files
- **Zero generic `raise Exception()`** — all raises use domain-specific exception types
- **Zero print/traceback diagnostic leakage** in production code (1 site in `app.py:522` is the intentional top-level crash handler)
- **All 15 turn phases and 6 end-of-turn phases** route through `_time_phase()` with proper `EnginePhaseError` wrapping and cause chaining
- **LLM providers** correctly redact API keys in `__repr__`, enforce SSL/timeouts, retry only 5xx, never retry 429
- **All custom exceptions** inherit from `GameException` with `message`, `code`, and `context`
- **Snapshot-and-rollback** works correctly in `TurnEngine.process_turn()` — state integrity is preserved on failure
- **`save_json()`** uses atomic write-via-temp-file with directory creation
- **Proper `from e` chaining** throughout persistence boundaries (`from_dict()`, `save_json()`, `load_json_required()`)
- **64 of 75 broad-except sites** have legitimate `# Intentional broad catch:` comments with proper justification

---

## 9. Appendices

### Raw Tool Outputs
- `raw/manifest.json` — 4-shard file assignment (749 files, ~161K LOC)
- `raw/broad_except_sites.json` — 75 scanner hits
- `raw/bare_except_sites.json` — empty (zero bare excepts)
- `raw/json_bypass_sites.json` — 7 scanner hits
- `raw/raise_generic_sites.json` — empty (zero generic raises)
- `raw/print_debug_sites.json` — 1 scanner hit (intentional)

### Agent Reports
- `findings/error_review_01.md` — Shard 01 (176 files, 4 findings)
- `findings/error_review_02.md` — Shard 02 (191 files, 5 findings)
- `findings/error_review_03.md` — Shard 03 (190 files, 5 findings)
- `findings/error_review_04.md` — Shard 04 (192 files, 8 findings)
- `findings/error_propagation_cross_layer.md` — Cross-layer (8 findings)
- `findings/llm_context_security.md` — LLM Security (3 findings)
- `findings/verification.md` — Critical finding verification (1 confirmed)
