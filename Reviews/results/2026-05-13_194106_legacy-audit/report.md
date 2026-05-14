# Legacy Code Audit — Final Report

**Date:** 2026-05-13
**Review Directory:** `Reviews/results/2026-05-13_194106_legacy-audit`
**Scope:** 776 production files under `game/` (165,630 LOC estimated)

---

## 1. Executive Summary

- **Total legacy findings:** 21 (after deduplication and false-positive rejection)
- **Posture:** **Clean / light drift** — the codebase is well-maintained. No CRITICAL findings. Three MAJOR items and 14 MINOR items remain. Four Phase 1 detections were false positives (INFO).
- **One-PR-deletable items:** 0 (no CRITICAL zero-call-site findings)
- **CLAUDE.md Rule 3 violations:** 0 (no save-migration code, no compatibility shims found)
- **Duplicate systems:** 0 — all 12 cross-system candidate pairs are intentional architectural splits (verified)

The most significant items are:
1. A documented shim module (`pathfinding.py`) with ~14 callers awaiting a PROJ-376 migration sweep
2. Pattern #30 (Registrar Close-Callback) slot-cleanup redundancy in 13 StrategyModalWindow slots
3. A thin `to_roman()` wrapper with a single internal caller

---

## 2. Legacy Inventory by Category

| Category | Count | Critical | Major | Minor | Info |
|----------|-------|----------|-------|-------|------|
| Module aliases | 0 | 0 | 0 | 0 | 0 |
| `__init__.py` re-export shims | 3 | 0 | 0 | 2 | 1 |
| Deprecation markers (stale comments) | 4 | 0 | 0 | 3 | 1 |
| Wrapper delegates | 2 | 0 | 1 | 0 | 1 |
| Duplicate systems | 0 | 0 | 0 | 0 | 0 |
| Save migration code | 0 | 0 | 0 | 0 | 0 |
| Superseded pattern usage (Pattern #30) | 1 | 0 | 1 | 0 | 0 |
| TYPE_CHECKING-only re-exports | 0 | 0 | 0 | 0 | 0 |
| Partial Protocol implementers | 0 | 0 | 0 | 0 | 0 |
| **Additional — Shim files** | 3 | 0 | 1 | 2 | 0 |
| **Additional — Stale PROJ/structure** | 4 | 0 | 0 | 4 | 0 |
| **Additional — Phase 1 false positives** | 4 | 0 | 0 | 0 | 4 |
| **Total** | **21** | **0** | **3** | **11** | **7** |

---

## 3. Legacy Removal Scorecard

### 3.1 Module Aliases
**Score: 0/776 files — clean.** No `OldName = NewName` aliases detected. PROJ-298's removal of 8 module aliases was effective.

### 3.2 `__init__.py` Re-export Shims
Two documented PROJ-372 backward-compat re-export shims and one intentional provider-registration import:

| ID | File | Issue | Severity |
|----|------|-------|----------|
| LEG-02-002 | `stars.py:31-45` | PROJ-372 re-exports; stale `StarGenerator` in `__all__` (lazy-loaded via `__getattr__`) | MINOR |
| LEG-02-003 | `planet.py:22-25` | PROJ-210/284 re-exports for `PlanetaryFacility`, `SpeciesPopulation`, `ColonySpeciesConfig` | MINOR |
| MIN-03-007 | `image/__init__.py:37` | Provider-registration side-effect import — intentional, not legacy | INFO |

### 3.3 Deprecation Markers
Three stale historical comments with no removal plan:

| ID | File | Issue | Severity |
|----|------|-------|----------|
| LEG-01-001 | `race_summary_panel.py:149` | Stale `# legacy` comment referencing completed three-column migration | MINOR |
| MIN-03-001 | `conflict_resolution_engine.py:379` | Comment references deleted `_rng_resolve_empty_fleets` function | MINOR |
| MIN-03-002 | `open_warp_point.py:89` | `# old route` temporal comment | MINOR |

### 3.4 Wrapper Delegates
One real wrapper; 7 of 8 Phase 1 detections were false positives:

| ID | File | Issue | Severity |
|----|------|-------|----------|
| LEG-01-003 | `planet_naming.py:16` | `to_roman()` wrapper with 1 internal caller | MAJOR |

False-positive rate: 87.5%. The Phase 1 wrapper detector flags thin delegation as a positive signal but in this codebase, most are documented Facade/Delegate patterns (Pattern #5) or extraction-point seams.

### 3.5 Duplicate Systems
**Score: 0/12 candidate pairs — clean.** All 12 pairs (BattleSpec compilers, DesignLoader/DesignLibrary, ShipFactory/VehicleDesignService, FleetAuraManager/CombatModifierCollector, etc.) are intentional architectural splits documented in `docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md`. Recent consolidation efforts (PROJ-204, PROJ-269, PROJ-274, PROJ-382) eliminated the last real duplicates.

### 3.6 Superseded Pattern Usage
One Pattern #30 (Registrar Close-Callback) usage:

| ID | File | Issue | Severity |
|----|------|-------|----------|
| LEG-02-001 | `strategy_event_router.py:427-460` | `_handle_window_close` clears 13 window slots, all StrategyModalWindow subclasses — redundant with Pattern #31 auto-deregistration | MAJOR |

### 3.7 Additional — Shim Files

| ID | File | Issue | Severity |
|----|------|-------|----------|
| MAJ-001 | `pathfinding.py` | Documented shim with 8 production callers, tracked as PROJ-376 | MAJOR |
| MIN-002 | `race_setup_screen.py` | 31-line legacy import shim re-exporting `RaceSetupScreen`, `RaceBrowserDialog`, `RaceRandomizer` | MINOR |
| MIN-003 | `test_run_details.py` | 12-line re-export shim for `TestRunDetailsPanel` (2 callers) | MINOR |

### 3.8 Additional — Stale PROJ / Dead Imports

| ID | File | Issue | Severity |
|----|------|-------|----------|
| MIN-001 | `app.py:124` | Legacy `running` attribute mirroring `RunLoop.running` | MINOR |
| MIN-03-004 | `screen_router.py:182,304,429` | Three dead `import pygame_gui` with "historical parity" comments | MINOR |
| LEG-02-004 | Multiple | Six files with duplicate `global`-keyword lazy-init caches (4 duplicate the same pattern) | MINOR |
| LEG-02-005 | `core/paths.py:98` | Stale `PROJ-XX` placeholder | MINOR |

---

## 4. Prioritized Removal Plan

Top items ordered by `severity_weight × layer_weight × LOC_affected`:

| Rank | Finding ID | Category | Severity | Layer | LOC | Action |
|------|------------|----------|----------|-------|-----|--------|
| 1 | MAJ-001 | Shim file | MAJOR | Strategy/Data | 102 | Execute PROJ-376: migrate ~8 callers to `GalaxyPathfindingService` / `InterceptCalculator` directly, then delete shim module |
| 2 | LEG-02-001 | Superseded pattern | MAJOR | UI | 34 | Audit 13 slot-clears in `_handle_window_close` — all are StrategyModalWindow subclasses using Pattern #31 auto-deregistration. Remove redundant clears or document which are test-observable |
| 3 | LEG-01-003 | Wrapper delegate | MAJOR | Strategy/Data | 13 | Inline 1 internal caller: replace `to_roman(n)` with `NameRegistry.to_roman(n)` at `planet_naming.py:64`, delete wrapper |
| 4 | LEG-02-003 | Re-export shim | MINOR | Strategy/Data | 7 | Audit callers importing from `planet.py` instead of canonical modules; when zero callers remain, delete re-exports |
| 5 | LEG-02-002 | Re-export shim | MINOR | Strategy/Data | 12 | Track migration of 15+ import sites to `game.core.spectrum_math` / `game.strategy.data.spectrum`; delete stale `StarGenerator` from `__all__` |
| 6 | MIN-03-005 | Re-export shim | MINOR | Strategy/Data | 1 | Migrate ~15 `Spectrum` import sites to `game.strategy.data.spectrum`; delete re-export from `stars.py` |
| 7 | MIN-03-006 | Re-export shim | MINOR | Strategy/Data | 1 | Migrate ~7 `WarpPoint`/`StarSystem` import sites to `game.strategy.data.star_system`; delete re-export from `galaxy.py` |
| 8 | LEG-02-004 | Global caches | MINOR | UI + Strategy | ~30 | Consolidate 4 duplicate `_cached_registries` lazy-init blocks into a shared helper |
| 9 | MIN-002 | Shim file | MINOR | UI | 31 | Migrate import callers to canonical paths (`race_setup.screen`, `race_browser_dialog`, `strategy.systems.race_randomizer`), delete 31-line shim |
| 10 | MIN-003 | Shim file | MINOR | UI | 12 | Migrate 2 callers to `game.ui.screens.test_lab.details`, delete 12-line shim |
| 11 | MIN-03-004 | Dead imports | MINOR | UI | 3 | Remove three dead `import pygame_gui` lines in `screen_router.py` |
| 12 | LEG-01-001 | Stale comment | MINOR | UI | 1 | Remove stale `# legacy` comment in `race_summary_panel.py:149` |
| 13 | MIN-03-001 | Stale comment | MINOR | Strategy/Engine | 1 | Trim stale reference to deleted `_rng_resolve_empty_fleets` function |
| 14 | MIN-03-002 | Stale comment | MINOR | Strategy/Engine | 1 | Replace "old route" wording with factual statement |
| 15 | MIN-001 | Legacy attribute | MINOR | App | ~4 | Document removal in PROJ-309; delete after test bypasses are migrated |
| 16 | LEG-02-005 | Stale placeholder | MINOR | Core | 1 | Fill in actual PROJ number for `PROJ-XX Star Expansion` in `core/paths.py:98` |

---

## 5. Trend Comparison

**Previous run:** 2026-05-13 (Phase 1 raw counts)

| Category | Previous Run | This Run | Delta |
|----------|-------------|----------|-------|
| Critical | 0 | 0 | **0** |
| Major | 0 | 3 | **+3** |
| Minor | 5 | 11 | **+6** |
| Info | 0 | 7 | **+7** |

Note: The previous run (Phase 1 deterministic scan) only counted raw detector hits. This run adds manual review findings — the increase reflects discovery of items the AST detectors missed (shim files, stale PROJ comments, dead imports) rather than codebase degradation.

---

## 6. Refinement Notes

No refinements yet. The Claude bridge skill `claude-proj-from-legacy-audit` writes proposals here when it converts this review into projects.

---

## 7. Appendices

### 7.1 Raw Tool Outputs
`Reviews/results/2026-05-13_194106_legacy-audit/raw/`

### 7.2 Agent Finding Reports
- `Reviews/results/2026-05-13_194106_legacy-audit/findings/legacy_review_01.md` — Shard 01 (165 files, 6 findings)
- `Reviews/results/2026-05-13_194106_legacy-audit/findings/legacy_review_02.md` — Shard 02 (177 files, 5 findings)
- `Reviews/results/2026-05-13_194106_legacy-audit/findings/legacy_review_03.md` — Shard 03 (163 files, 7 findings)
- `Reviews/results/2026-05-13_194106_legacy-audit/findings/legacy_review_04.md` — Shard 04 (185 files, 5 findings)
- `Reviews/results/2026-05-13_194106_legacy-audit/findings/legacy_duplicate_systems_cross.md` — Cross-system review (12 pairs, 0 findings)

### 7.3 Verification Report
`Reviews/results/2026-05-13_194106_legacy-audit/findings/verification.md`

**Verification summary:**
- 0 CRITICAL findings (all five reports confirmed independently)
- 3 MAJOR findings spot-checked: 2 accurate, 1 with a classification inaccuracy (LEG-02-001 — all 13 slots are StrategyModalWindow subclasses, not 8 "non-modal" as claimed; the core redundancy observation is still valid but severity justification is weaker)
- 2 MINOR findings spot-checked: both accurate
- 1 minor inaccuracy in LEG-02-002 (`stars.py` uses `__getattr__` for lazy `StarGenerator` import — no ImportError occurs)

### 7.4 Manifest
`Reviews/results/2026-05-13_194106_legacy-audit/raw/manifest.json`
