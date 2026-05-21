# Error Handling & Robustness Audit — Final Report

> **Date:** 2026-05-20
> **Review Directory:** `Reviews/results/2026-05-20_065518_error-audit/`
> **Scanner:** Tools/error_audit/error_audit.py (Phase 1) + 6 agents (Phase 2) + 1 verification agent (Phase 3)

---

## 1. Executive Summary

**Overall Error Hygiene: GOOD** — The codebase demonstrates disciplined exception handling across all layers. All 128 broad-except sites carry valid `# Intentional broad catch:` comments. Zero bare excepts. Zero generic `raise Exception`. The LLM/image provider layers have exemplary security hygiene with no credential leakage.

**One verified CRITICAL finding** and **11 verified MAJOR findings** remain after verification. The standout finding is an unhandled `SessionInitializationError` propagation path that results in a hard application crash rather than a user-facing error dialog.

| Layer | Error Hygiene | Key Issues |
|-------|--------------|------------|
| Core | EXCELLENT | formula_evaluator.py has clean catch-and-convert |
| Services (LLM/Image) | EXCELLENT | Full security compliance; minor __repr__ hardening |
| Simulation | GOOD | replay_serialization.py uses generic builtins at persistence boundaries |
| Strategy | GOOD | turn_engine.py crash dumps lose BattleResolutionError context |
| AI | GOOD | All broad catches justified |
| UI | GOOD | screen_router.py missing SessionInitializationError guard (CRITICAL) |

---

## 2. Coverage Status

| Shard | Files | LOC Estimate | Review File | Status |
|-------|-------|-------------|-------------|--------|
| Shard 01 | 213 | 45,499 | error_review_01.md | Complete (213/213) |
| Shard 02 | 197 | 45,500 | error_review_02.md | Partial (117/197) |
| Shard 03 | 225 | 45,495 | error_review_03.md | Substantial |
| Shard 04 | 211 | 45,607 | error_review_04.md | Complete (211/211) |
| Cross-Layer | — | — | error_propagation_cross_layer.md | 10 boundaries, 4 paths |
| LLM Security | — | — | llm_context_security.md | 21 sites audited |

**Total production files:** 846 | **Total LOC:** ~182,000

---

## 3. Error Hygiene Scorecard

### Deterministic Scanner Results (Phase 1)

| Category | Raw Count | Actionable | Notes |
|----------|-----------|------------|-------|
| Broad except w/o comment | 128 | **0** | Scanner has known bug: all 128 sites have valid `# Intentional` comments but `has_comment` reports `false`. 100% false positive rate. |
| Bare except | 0 | 0 | Clean |
| JSON bypass | 4 | **1** | 3 in json_utils.py itself (correct). 1 in minefield_balance.py — functional, stylistic only. |
| Generic raise Exception | 0 | 0 | Clean |
| Print/traceback debug | 1 | 0 | app.py:520 top-level crash handler — acceptable |
| Open() blocks | 6 | 0 | All use `with` context managers |

### Agent Discovery Results (Phase 2 + Verification)

| Category | Total | CRITICAL | MAJOR | MINOR |
|----------|-------|----------|-------|-------|
| Exception type misuse (generic builtins vs domain-specific) | 8 | 0 | 5 | 3 |
| Lost exception chaining / context loss | 2 | 0 | 2 | 0 |
| Missing error boundaries / unguarded calls | 2 | 1 | 1 | 0 |
| Silent error swallowing | 3 | 0 | 2 | 1 |
| Missing error codes in domain exceptions | 2 | 0 | 1 | 1 |
| Inconsistent exception handling across layers | 2 | 0 | 0 | 2 |
| LLM/Image security hardening | 5 | 0 | 0 | 5 |
| JSON bypass (stylistic) | 1 | 0 | 0 | 1 |

---

## 4. Cross-Layer Error Propagation

**Overall: SAFE** — All 10 mapped error boundaries correctly convert, chain, and propagate exceptions with adequate context. The battle-simulation-to-UI path has complete coverage from `run_battle()` through `TurnFailedDialog`. The LLM and image provider boundaries are exemplary.

**Key gaps:**
- `TurnEngine._time_phase()` does not merge `BattleResolutionError` context (fleet_ids, empire_ids, hex_coord) into the wrapping `EnginePhaseError` — crash dumps cannot identify which battle failed.
- `SessionInitializationError` has no catch at the UI layer (`screen_router.py`, `new_game_setup_controller.py`) — leads to hard crash (CRITICAL-1).

---

## 5. LLM & Image Context Security

**Overall: CLEAN** — Zero credential leaks, zero response body exposure. All 21 audited sites comply with the `docs/05_ERROR_HANDLING.md` service error hygiene contract. The `DeepSeekProvider` and `OpenAIImageProvider` correctly read API keys per-request, redact `repr()`, and never include keys in exception context.

**5 MINOR hardening recommendations:**
1. `%r` formatting in background.py worker catch-all logs should use `%s` to avoid third-party exception repr leakage.
2. `CompletionResult`, `ImageResult`, `Message` DTOs lack explicit `__repr__` — default dataclass repr would expose text/binary data if logged.

---

## 6. Prioritized Remediation Plan

| Priority | Finding | Location | Severity | LOC | Effort |
|----------|---------|----------|----------|-----|--------|
| **P1** | Add `SessionInitializationError` guard to `screen_router.py` and `new_game_setup_controller.py` | screen_router.py:209,266; controller.py:186 | CRITICAL | ~10 | 15 min |
| **P2** | Merge `BattleResolutionError` context into `EnginePhaseError` wrapper | turn_engine.py:322 | MAJOR | ~5 | 10 min |
| **P3** | Replace `TypeError`/`ValueError` with `PersistenceException` at serialization boundaries | replay_serialization.py:115,139 | MAJOR | ~4 | 10 min |
| **P4** | Replace generic `ValueError`/`RuntimeError` with `ValidationException` | planetary_facility.py:149, ship_stats_cache.py:41, fleet_capability_calculator.py:70,138, battle_runner.py:314 | MAJOR | ~15 | 20 min |
| **P5** | Add `code=` parameter to `ValidationException` in happiness_engine.py | happiness_engine.py:96 | MAJOR | ~1 | 5 min |
| **P6** | Remove gratuitous `Exception` from `except (pygame.error, Exception)` tuple | modifier_icon_service.py:81 | MAJOR | ~1 | 5 min |
| **P7** | Log or surface JSON decode errors instead of silent `pass` | battle_state_viewer.py:135 | MAJOR | ~3 | 5 min |
| **P8** | Add explicit `__repr__` to LLM/Image DTOs for safe logging | types.py (llm + image) | MINOR | ~10 | 10 min |
| **P9** | Use `%s` instead of `%r` in background.py worker catch-all logs | background.py (2 sites) | MINOR | ~2 | 2 min |
| **P10** | Replace `json.load` with `json_utils.load_json` in minefield_balance.py | minefield_balance.py:162 | MINOR | ~3 | 5 min |

**Total estimated effort:** ~82 minutes across all findings.

---

## 7. Trend Comparison

No previous error audit run data found. This is the baseline run.

---

## 8. Scanner Refinement Notes

**Known scanner bug:** The comment detection logic in `Tools/error_audit/error_audit.py` reports `has_comment: false` for all 128 broad-except sites even when the `# Intentional broad catch:` comment is present on the same line. The raw context field in every JSON entry contains the comment text. This results in a 100% false positive rate for the broad-except detector.

**Recommendation:** Fix the comment-detection regex to recognize `# Intentional broad catch:` on either the `except` line or the line immediately above it, as documented in `docs/05_ERROR_HANDLING.md`.

---

## Appendices

| Artifact | Path |
|----------|------|
| Raw scanner output | `raw/broad_except_sites.json`, `raw/json_bypass_sites.json`, etc. |
| Shard 01 review | `findings/error_review_01.md` |
| Shard 02 review | `findings/error_review_02.md` |
| Shard 03 review | `findings/error_review_03.md` |
| Shard 04 review | `findings/error_review_04.md` |
| Cross-layer report | `findings/error_propagation_cross_layer.md` |
| LLM security report | `findings/llm_context_security.md` |
| Verification report | `findings/verification.md` |
| Manifest | `raw/manifest.json` |
