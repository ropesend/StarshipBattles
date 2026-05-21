# Documentation Freshness & Accuracy Audit — Final Report

**Date:** 2026-05-20
**Review Directory:** `Reviews/results/2026-05-20_073330_docs-audit/`
**Phase 1 Scanner:** 67 doc files, 1761 file refs, 155 PROJ refs, 229 undocumented modules

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| Doc files audited | 67 |
| Dead file references (scanner) | 98 |
| Confirmed dead refs (verified) | ~40 (rest are placeholders/stale-warnings) |
| Stale PROJ refs | 0 (scanner), but many "unknown" status PROJs noted |
| Docs missing "Last verified" | 66/67 (only `orders_system.md` has one) |
| Undocumented modules (>50 LOC) | 229 |
| Cross-doc consistency issues | 18 (2 critical) |
| Code accuracy: confirmed doc errors | 13 |
| Code accuracy: disputed (doc correct) | 7 |
| Code accuracy: inconclusive | 5 |

**Doc Health Score: C+** — Functional but with significant stale reference accumulation, inconsistent Python version across agent docs, and widespread missing verification timestamps.

---

## 2. Doc Health Scorecard

| Group | Docs | Dead Refs | Stale PROJs | Content Errors | Health |
|-------|------|-----------|-------------|---------------|--------|
| Architecture (G1) | 7 | 7 (2 real) | 0 | 2 | B |
| Systems (G2) | 12 | 15 (7 real) | 0 | 7 | C+ |
| Guides (G3) | 9 | 17 (10 real) | 0 | 7 | C |
| Root Agent Docs (G4) | 3 | 2 (0 real) | 0 | 4 | B- |
| Project Protocols (G5) | 24 | 22 (all intentional) | 0 | 1 | B+ |
| Review Protocols (G6) | 12 | 4 (all intentional) | 0 | 0 | A- |
| **Cross-Consistency** | — | — | — | 18 issues | C+ |

### Finding Totals by Severity

| Group | Critical | Major | Minor |
|-------|----------|-------|-------|
| G1 Architecture | 0 | 2 | 5 |
| G2 Systems | 2 | 5 | 8 |
| G3 Guides | 4 | 7 | 6 |
| G4 Root Agent | 1 | 3 | 4 |
| G5 Project Protocols | 0 | 2 | 22 |
| G6 Review Protocols | 0 | 0 | 4 |
| Cross-Consistency | 2 | 7 | 9 |
| **Total (unique)** | **~7** | **~23** | **~55** |

---

## 3. Dead Reference Register (Confirmed)

### HIGH Priority — Files referenced as existing but deleted

| Doc | Line | Dead Reference | Reality |
|-----|------|---------------|---------|
| `docs/04_SERVICES.md` | 480 | `game/strategy/services/component_inspector.py` | Deleted (split into `component_abilities.py` + `component_layers.py`; shim removed by PROJ-454) |
| `docs/systems/ability_reference.md` | 19, 489 | `game/strategy/services/component_inspector.py` | Same as above |
| `docs/guides/adding_abilities.md` | 55 | `game/strategy/services/component_inspector.py` | Same as above |
| `docs/guides/component_system.md` | 23 | `game/strategy/services/component_inspector.py` | Same as above |
| `docs/guides/qs_complex_design.md` | 32 | `game/strategy/services/component_inspector.py` | Same as above |
| `docs/systems/ability_reference.md` | 184 | `game/strategy/services/effect_ability_metadata.py` | Deleted; replaced by `ability_metadata.py` |
| `docs/systems/strategy_layer.md` | 692 | `game/strategy/services/effect_ability_metadata.py` | Same as above |
| `docs/guides/adding_abilities.md` | 495 | `game/strategy/services/effect_ability_metadata.py` | Same as above |
| `docs/02_PATTERNS.md` | 819 | `game/ui/screens/test_lab/test_run_details.py` | Removed by PROJ-417 |
| `docs/02_PATTERNS.md` | 824 | `game/ui/screens/race_setup_screen.py` | Removed by PROJ-416 |

### HIGH Priority — Files split into packages, refs need updating

| Doc | Line | Old Path | New Path |
|-----|------|----------|----------|
| `docs/02_PATTERNS.md` | 170 | `game/strategy/engine/commands.py` | `game/strategy/engine/commands/` (package) |
| `docs/02_PATTERNS.md` | 187, 827 | `game/strategy/engine/command_handlers.py` | `game/strategy/engine/handlers/` (package) |
| `docs/systems/ability_reference.md` | 373 | `game/simulation/components/abilities/planetary.py` | `game/simulation/components/abilities/planetary/` (package) |
| `docs/guides/qs_complex_design.md` | 212 | `game/simulation/components/abilities/planetary.py` | Same as above |
| `docs/systems/fighters.md` | 244 | `game/ui/screens/planet_context_menu.py` | `game/ui/screens/planet_menu_items.py` + `fms_menu_callbacks.py` |
| `docs/systems/minefields.md` | 247, 323 | `game/ui/screens/planet_context_menu.py` | Same as above |

### MEDIUM Priority — Path drift

| Doc | Line | Dead Reference | Real Path |
|-----|------|---------------|-----------|
| `docs/01_ARCHITECTURE.md` | 155 | `data/galaxy_protocols.py` | `game/strategy/data/galaxy_protocols.py` (missing prefix) |
| `docs/02_PATTERNS.md` | 38 | `data/classes/` | Directory never existed; should reference `data/` root |
| `docs/03_CONVENTIONS.md` | 32 | `game/strategy/data/pathfinding.py` | `game/strategy/services/galaxy_pathfinding_service.py` |
| `docs/systems/strategy_layer.md` | 831 | `data/spectrum.py` | `game/strategy/data/spectrum.py` |
| `docs/systems/research_system.md` | 24 | `game/research/ui/` | Research UI now lives under `game/ui/screens/` |
| `docs/06_UI_STYLE_GUIDE.md` | 229 | `data/FiraCode-Regular.ttf` | Font may have been relocated or renamed |

### Test path references that need updating

| Doc | Line | Dead Reference |
|-----|------|---------------|
| `docs/systems/ability_reference.md` | 108, 571, 585 | `tests/unit/strategy/services/test_effect_ability_metadata.py` |
| `docs/guides/adding_abilities.md` | 434, 539 | `tests/unit/strategy/services/test_effect_ability_metadata.py` |
| `docs/guides/component_system.md` | 347 | `tests/unit/strategy/test_component_inspector.py` |
| `docs/guides/qs_complex_design.md` | 319 | `tests/unit/strategy/test_component_inspector.py` |
| `docs/guides/testing_infrastructure.md` | 170 | `tests/unit/simulation/test_damage.py` |
| `docs/systems/combat_simulation.md` | 546-548, 556 | Various test paths |

### Placeholder references (not actionable)

`tests/path/to/test.py` appears in 10+ docs. These are intentional example placeholders in command syntax examples. No action required.

---

## 4. Stale PROJ Reference Register

The scanner found **0 stale PROJ refs** (all matched against `projects_index.md`). However, the cross-reference audit found:

- **Many PROJ refs with "unknown" status**: Several PROJs (PROJ-252, PROJ-258, PROJ-269, PROJ-302, PROJ-373, PROJ-381, PROJ-382, PROJ-383, PROJ-390, PROJ-392, PROJ-396, PROJ-410, PROJ-411, PROJ-412) appear in docs with `"unknown"` status from `projects_index.md`. These are likely archived but the tracking system doesn't have their final status.
- **PROJ-433** (`component_inspector` split) is referenced as "follow-up" in docs but the file it references is fully deleted. Docs should reflect that the work is complete.
- **PROJ-416/417** (legacy removal) are referenced in `docs/02_PATTERNS.md` with "removed by" notes but the dead file references still remain as pattern examples.

**Recommendation**: Audit the "unknown" PROJs against `Projects/archived_projects/` to determine final status, then update `projects_index.md`.

---

## 5. Doc Staleness Register

Only **1 out of 67** doc files has a `Last verified:` timestamp:
- `docs/systems/orders_system.md` — 2026-05-07 (13 days ago, within threshold)

All other 66 docs lack the `> **Last verified:** YYYY-MM-DD` line required by `docs/03_CONVENTIONS.md`. This is a systematic gap — every doc should be verified and timestamped.

---

## 6. Undocumented Modules

229 modules > 50 LOC have zero doc mentions. Key architectural surface modules that most need documentation:

| Module | LOC | Reason |
|--------|-----|--------|
| `game/strategy/engine/superweapon_order_processor.py` | 506 | Major subsystem, no doc coverage |
| `game/simulation/interfaces/entity_protocols.py` | 487 | Cross-layer protocol surface |
| `game/strategy/engine/game_initializer.py` | 446 | Critical bootstrap path |
| `game/simulation/interfaces/ability_protocols.py` | 359 | Cross-layer protocol surface |
| `game/strategy/facade/dto/fleet_dto.py` | 332 | DTO layer, public API |
| `game/strategy/engine/empire_economy_calculator.py` | 333 | Core economy engine |
| `game/ui/screens/transfer_grid_renderer.py` | 436 | Key UI component |
| `game/ui/panels/modifier_impact_grid.py` | 514 | Complex widget |
| `game/ui/screens/build_queue_input_router.py` | 548 | Complex input routing |

---

## 7. Cross-Doc Consistency Issues

### Critical
1. **Python version mismatch**: `AGENTS.md:52` says **Python 3.14**. Every other doc (CLAUDE.md, README.md, 03_CONVENTIONS.md, simulation_testing.md) and `pyproject.toml` says **3.13+**. AGENTS.md is wrong.
2. **Layer dependency error in AGENTS.md**: Lists Assets as depending on Simulation, violating the documented layer architecture (Assets depends on Core + Services only).

### Major
- Pattern #40 vs #41 mismatch in `03_CONVENTIONS.md:131` (should reference Pattern #41, not #40)
- `docs/guides/testing_infrastructure.md` references `newdocs/02_PATTERNS.md` — `newdocs/` doesn't exist
- `docs/systems/satellites.md` uses incorrect classification ("fleet namespace" instead of "DeployedGroup")
- `docs/README.md` still says "33 patterns" — actual count is 43
- `docs/guides/adding_abilities.md` references `ability_metadata.py` but should reference `effect_ability_metadata.py` (or the renamed replacement)
- Key rules (TDD, layer model, 500 LOC) paraphrased with wording drift across 4+ files
- Combat Lab runner listed in commands but not explained as non-pytest

---

## 8. Prioritized Documentation Update Plan

### Phase 1: Fix CRITICAL Contradictions (immediate)
1. **Fix Python version** in `AGENTS.md:52` → change "3.14" to "3.13+"
2. **Fix layer dependency** in `AGENTS.md` → Assets should not list Simulation as a dependency
3. **Remove `component_inspector.py` references** from all 5 docs that claim it exists → point to `component_abilities.py` + `component_layers.py`
4. **Remove/fix `effect_ability_metadata.py` references** from all 3 docs → point to `ability_metadata.py`
5. **Remove dead references to deleted files** (`race_setup_screen.py`, `test_run_details.py`)

### Phase 2: Fix MAJOR Path Drift and Content Errors
6. Update split-package references (`commands.py` → `commands/`, `command_handlers.py` → `handlers/`, `planetary.py` → `planetary/`)
7. Fix `data/galaxy_protocols.py` → `game/strategy/data/galaxy_protocols.py`
8. Fix `planet_context_menu.py` → split files in fighters.md and minefields.md
9. Update pattern count in README.md (33 → 43)
10. Fix cross-reference errors (Pattern #40 → #41, `newdocs/` → `docs/`)
11. Fix satellites.md classification
12. Add Combat Lab runner explanation

### Phase 3: Fix MINOR Issues and Staleness
13. Add `Last verified:` timestamps to all 66 docs lacking them
14. Update dead test paths in guides and systems docs
15. Fix `data/spectrum.py` → `game/strategy/data/spectrum.py`
16. Fix `game/research/ui/` → current location
17. Audit "unknown" PROJ statuses in `projects_index.md`

### Phase 4: Documentation Gaps
18. Create doc coverage for `superweapon_order_processor.py` (506 LOC, no docs)
19. Create doc coverage for `game_initializer.py` (446 LOC, no docs)
20. Assess need for DTO layer documentation (`fleet_dto.py`, `planet_dto.py`, etc.)

---

## 9. Trend Comparison

*(Trend tracking requires prior runs for comparison. This is the first generated report in this review directory.)*

```python
from Tools._audit_common import run_tracker
current_summary = {
    "dead_refs": 98,
    "stale_projs": 0,
    "stale_docs": 0,
    "undocumented_modules": 229,
    "critical_findings": 7,
    "major_findings": 23,
    "minor_findings": 55,
}
trend = run_tracker.compute_trend("Reviews/results", "docs", current_summary)
# First run — no historical comparison available
run_tracker.add_run("Reviews/results", "docs", current_summary)
```

---

## 10. Appendices

### Raw Data Files
- `raw/doc_file_refs.json` — 1761 total refs, 98 dead
- `raw/stale_proj_refs.json` — 155 PROJ refs, 0 stale
- `raw/doc_staleness.json` — Staleness scores for 31 doc files
- `raw/undocumented_modules.json` — 229 modules > 50 LOC with no doc mention
- `raw/doc_inventory.json` — 31 doc files with headings

### Agent Findings
- `findings/docs_review_G1.md` — Architecture & Core Docs (7 findings)
- `findings/docs_review_G2.md` — Systems Docs (15 findings)
- `findings/docs_review_G3.md` — Guide Docs (17 findings)
- `findings/docs_review_G4.md` — Root Agent Docs (8 findings)
- `findings/docs_review_G5.md` — Project Protocols (24 findings)
- `findings/docs_review_G6.md` — Review Protocols (4 findings)
- `findings/docs_consistency_cross.md` — Cross-Doc Consistency (18 issues)
- `findings/docs_accuracy_code.md` — Code-Base Accuracy Validation (45 claims reviewed)

### Key Files Requiring Immediate Attention
1. `AGENTS.md` — Wrong Python version, wrong layer dependency
2. `docs/04_SERVICES.md:480` — Lies about `component_inspector.py` existing
3. `docs/systems/ability_reference.md` — Most stale content (6 dead refs)
4. `docs/02_PATTERNS.md` — References deleted legacy files
5. `docs/guides/adding_abilities.md` — References deleted metadata file
