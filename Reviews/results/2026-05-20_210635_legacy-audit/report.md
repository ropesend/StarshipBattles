# Legacy Code Audit Report
**Date:** 2026-05-20 21:06 UTC
**Review Directory:** `Reviews/results/2026-05-20_210635_legacy-audit/`

---

## 1. Executive Summary

- **Files scanned (Phase 1):** 846 across `game/`
- **Overall posture:** **CLEAN** — no save migrations, no module aliases, no TYPE_CHECKING re-exports, no partial Protocol implementers, no name-pair drift
- **Agent findings:** 35 total across 4 in-shard reviews + cross-system analysis + verification
- **Verified CRITICAL findings:** 2 (both confirmed — safe one-PR deletions)
- **Rule 4 violations:** 0 — no save-migration code or compatibility shims found
- **One-PR-deletable items:** 2 CRITICAL dead re-exports + multiple MAJOR dead/test-only methods

The codebase is in excellent shape from a legacy-removal standpoint. The majority of findings are MINOR documentation-quality items (stale comments, missing PROJ ticket links). The 2 CRITICAL and 7 MAJOR findings are concentrated in dead re-exports and test-only legacy helper methods.

---

## 2. Legacy Inventory by Category

| Category | Count | Critical | Major | Minor | Info |
|----------|-------|----------|-------|-------|------|
| Module aliases | 0 | 0 | 0 | 0 | 0 |
| `__init__.py` re-export shims | 2 | 0 | 0 | 2 | 0 |
| Deprecation markers | 5 | 0 | 1 | 4 | 0 |
| Wrapper delegates | 4 | 0 | 0 | 1 | 3 |
| Duplicate systems | 2 | 0 | 1 | 1 | 0 |
| Save migration code | 0 | 0 | 0 | 0 | 0 |
| Superseded pattern usage | 1 | 0 | 0 | 1 | 0 |
| TYPE_CHECKING-only re-exports | 0 | 0 | 0 | 0 | 0 |
| Partial Protocol implementers | 0 | 0 | 0 | 0 | 0 |
| **Additional (dead re-exports)** | 2 | 2 | 0 | 0 | 0 |
| **Additional (test-only methods)** | 4 | 0 | 4 | 0 | 0 |
| **Additional (stale comments/docs)** | 12 | 0 | 0 | 12 | 0 |
| **Additional (DI bridge mechanics)** | 2 | 0 | 0 | 2 | 0 |
| **Additional (unused imports)** | 1 | 0 | 0 | 1 | 0 |
| **TOTAL** | **35** | **2** | **6** | **24** | **3** |

### Category Notes

- **No AGENTS.md Rule 4 violations.** Zero save-migration code, zero compatibility shims. Clean.
- **Phase 1 false positives retracted:** 6 wrapper delegates were verified as documented Facade/Delegate (Pattern #5) or Factory (Pattern #15) patterns. 1 name-pair drift entry was confirmed as an intentional architecture split (ModifierManager vs ModifierService).
- **Superseded Pattern #30 (Registrar Close-Callback):** Still used for documented legacy slot cleanup. Per `docs/02_PATTERNS.md`, this is the intentionally preserved exception path. Not a remediation target.

---

## 3. Legacy Removal Scorecard

| Category | CRITICAL Issues | MAJOR Issues | MINOR Issues | Est. LOC Savings | Action |
|----------|----------------|-------------|-------------|-----------------|--------|
| Dead re-exports | 2 | 1 | 0 | 3 | Delete import lines |
| Test-only legacy methods | 0 | 4 | 0 | ~170 | Delete methods + migrate tests |
| Deprecated fuel wrappers (in use) | 0 | 1 | 0 | ~16 | Migrate consumer to generic API |
| Cross-layer modifier validation duplication | 0 | 1 | 0 | ~80 | Consolidate to single source-of-truth |
| Pattern #36 re-export shim | 0 | 0 | 1 | 59 | Tracked migration (PROJ-382 active) |
| Stale comments / doc drift | 0 | 0 | 12 | 0 | Docs cleanup pass |
| DI bridge mechanics | 0 | 0 | 2 | ~20 | Consolidate into bootstrap |
| Unused side-effect import | 0 | 0 | 1 | 1 | Delete line |
| **TOTAL** | **2** | **7** | **16** | **~349** | |

---

## 4. Prioritized Removal Plan

Weighted by `severity_weight × layer_weight × loc_affected`:
- severity_weight: CRITICAL=10, MAJOR=5, MINOR=1, INFO=0.25
- layer_weight: Core/Simulation=2.0, Strategy=2.0, AI=1.5, UI=1.5

| Rank | Finding ID | Category | Severity | Layer | LOC | Score | Action |
|------|------------|----------|----------|-------|-----|-------|--------|
| 1 | LEG-F-1 | Duplicate systems | MAJOR | Simulation(2.0) | ~100 | 1000 | Consolidate `ModifierLogicService` → delegate to `ModifierService` |
| 2 | LEG-02-012 | Dead code | MAJOR | Simulation(2.0) | 87 | 870 | Delete `BattleController.load_state` (zero production callers) |
| 3 | LEG-02-001/005/006 | Test-only methods | MAJOR | AI(1.5) | ~83 | 622 | Delete `_find_tactical_launch_ability`, `_pop_fighter_cvs`, `_pop_cvs` (zero prod callers) |
| 4 | LEG-04-MAJOR | Deprecated wrappers (in use) | MAJOR | Strategy(2.0) | 16 | 160 | Migrate `resupply_engine.py` from fuel wrappers → generic consumable API |
| 5 | LEG-01-008 | Dead re-export | CRITICAL | Simulation(2.0) | 1 | 20 | Delete `DamageContext` re-export at `combat_events.py:62` (0 prod callers) |
| 6 | LEG-A-01 | Dead re-export | CRITICAL | Simulation(2.0) | 1 | 20 | Delete `CombatConstants` re-export at `ship.py:23` (0 total callers) |
| 7 | LEG-01-001 | Re-export shim (Pattern #36) | MINOR | Simulation(2.0) | 59 | 118 | Tracked migration — leave until PROJ-382 completes |
| 8 | LEG-A-02 | Dead re-export | MAJOR | Simulation(2.0) | 1 | 10 | Delete `DEFAULT_MAX_MASS` re-export at `ship.py:22` (1 test caller) |
| 9 | LEG-F-2 | Duplicate loaders | MINOR | Simulation(2.0) | 20 | 40 | `WorkshopDataLoader` → delegate base load to `reload_registries_from_directory` |
| 10 | LEG-04-MINOR-01 | Unused import | MINOR | UI(1.5) | 1 | 1.5 | Delete `_null_provider` side-effect import at `image/__init__.py:37` |

**Quick Wins (single PR, minimal risk):**
1. Ranks 5+6+8: Delete all dead re-exports in `ship.py` and `combat_events.py` — 3 lines, zero production churn
2. Rank 3: Delete 3 test-only carrier methods — ~83 LOC, zero production callers
3. Rank 2: Delete `BattleController.load_state` — 87 LOC, zero production callers

---

## 5. Trend Comparison

Compared to previous run (2026-05-20 07:21): **IMPROVING**

The previous run was captured before Phase 2 agent review retracted 6 wrapper-delegate false positives and 1 name-pair drift false positive. The deterministic Phase 1 scan reported higher raw counts:

| Metric | Previous (Phase 1 only) | Current (Phase 1+2+verification) | Delta |
|--------|------------------------|----------------------------------|-------|
| Phase 1 findings (raw) | 17 | 17 | 0 |
| Verified findings | 17 | 18 | +1 |
| Phase 1 false positives | 0 retracted | 7 retracted | +7 retractions |
| Agent-discovered additional | — | 17 | +17 |
| CRITICAL (actionable) | — | 2 | — |
| MAJOR (actionable) | — | 7 | — |

The codebase trend is **stable-to-improving** — the previous run's Phase 1 findings were mostly false positives now resolved. The agent review discovered genuinely legacy items not caught by deterministic scanning (dead re-exports, test-only methods, stale comments).

---

## 6. Refinement Notes

No refinements yet. The Claude bridge skill `claude-proj-from-legacy-audit` writes proposals here when it converts this review into projects.

---

## 7. Appendices

### Paths

- Raw tool outputs: `Reviews/results/2026-05-20_210635_legacy-audit/raw/`
- Agent finding reports:
  - `Reviews/results/2026-05-20_210635_legacy-audit/findings/legacy_review_01.md`
  - `Reviews/results/2026-05-20_210635_legacy-audit/findings/legacy_review_02.md`
  - `Reviews/results/2026-05-20_210635_legacy-audit/findings/legacy_review_03.md`
  - `Reviews/results/2026-05-20_210635_legacy-audit/findings/legacy_review_04.md`
  - `Reviews/results/2026-05-20_210635_legacy-audit/findings/legacy_duplicate_systems_cross.md`
- Verification report: `Reviews/results/2026-05-20_210635_legacy-audit/findings/verification.md`
- Manifest: `Reviews/results/2026-05-20_210635_legacy-audit/raw/manifest.json`

### Verified Critical Findings (safe to act on)

| ID | File | Line | Code to Remove |
|----|------|------|----------------|
| LEG-01-008 | `game/simulation/combat/combat_events.py` | 62 | `from game.core.combat_types import DamageContext  # noqa: F401` |
| A-01 (Shard 03) | `game/simulation/entities/ship.py` | 23 | `from game.core.constants import CombatConstants` |

Both confirmed by independent verification agent — zero production callers for both.
