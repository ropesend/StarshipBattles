# Documentation Freshness & Accuracy Audit — Final Report

**Date:** 2026-05-04
**Review Directory:** `Reviews/results/2026-05-04_090303_docs-audit/`
**Analyst:** OpenCode (ocode-docs-audit skill)

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| Doc files scanned | 27 (docs/) + 3 (root agent) + 16 (protocols) = 46 |
| Dead file references found | 13 (Phase 1) → 9 unique after dedup |
| Content accuracy issues | 12 confirmed code vs doc mismatches |
| Cross-doc consistency issues | 9 (1 Critical, 4 Major, 4 Minor) |
| Undocumented production modules (>50 LOC) | 194 |
| Doc health score | **72/100** (moderate drift; ~28 issues need attention) |

### Summary by Severity

| Severity | G1 | G2 | G3 | G4 | G5 | Cross-Doc | Code Accuracy | **Total** |
|----------|----|----|----|----|----|-----------|---------------|-----------|
| Critical | 0 | 1 | 2 | 0 | 0 | 1 | 12 | **16** |
| Major | 9 | 6 | 5 | 3 | 0 | 4 | — | **27** |
| Minor | 8 | 14 | 4 | 5 | 13 | 4 | — | **48** |

---

## 2. Doc Health Scorecard

| Group | Docs | Dead Refs | PROJ Issues | Content Errors | Health |
|-------|------|-----------|-------------|---------------|--------|
| Architecture (G1) | 7 | 6 (protocols.py + test_lab) | 0 | 3 (export count, pattern count, Quick Ref) | **78/100** |
| Systems (G2) | 8 | 1 | 0 | 3 (stale ability names) | **82/100** |
| Guides (G3) | 9 | 2 (test file, imports) | 0 | 0 | **72/100** |
| Root + Protocols (G4) | 19 | 1 (Scratchpad dir) | 0 | 2 (Python version, retired protocols) | **85/100** |
| Reviews (G5) | 11 | 0 | 0 | 0 | **92/100** |
| Cross-Doc | 22+ | — | — | 9 | **76/100** |

---

## 3. Dead Reference Register

### 3.1 `game/core/protocols.py` (8 occurrences across 4 docs) — CRITICAL

**Issue:** File `game/core/protocols.py` was decomposed into `game/core/protocols/` directory (9 sub-modules) by PROJ-309 Phase 3.4. Python imports still work via `__init__.py` re-exports, but docs cite a file path that no longer exists.

| Doc | Line | Context |
|-----|------|---------|
| docs/01_ARCHITECTURE.md | 276 | "All defined in `game/core/protocols.py`" |
| docs/01_ARCHITECTURE.md | 346 | "Protocol definitions in `game/core/protocols.py`" |
| docs/02_PATTERNS.md | 150 | "`game/core/protocols.py` -- all protocol definitions and TypeGuard functions" |
| docs/02_PATTERNS.md | 158 | Code example comment |
| docs/02_PATTERNS.md | 183 | Protocol families table: "see `game/core/protocols.py`" |
| docs/02_PATTERNS.md | 1185 | Cross-reference |
| docs/02_PATTERNS.md | 1526 | Quick Reference: Protocol+TypeGuard |
| docs/02_PATTERNS.md | 1546 | Quick Reference: Serializable |
| docs/04_SERVICES.md | 1114 | "`IRaceRegistry` in `game/core/protocols.py`" |
| docs/systems/strategy_layer.md | 680 | "Both Fleet and Planet implement the `IOrderable` protocol (`game/core/protocols.py`)" |

**Remediation:** Change all references to `game/core/protocols/` (directory). For specific protocols, reference the sub-module (e.g., `game/core/protocols/strategy_entities.py` for `IOrderable`, `game/core/protocols/persistence.py` for `ISerializable`).

### 3.2 `game/core/singleton.py` (03_CONVENTIONS.md:139) — MINOR

**Issue:** Scanner flagged as dead, but the doc text correctly states the file was removed by PROJ-297. This is historical documentation, not a stale reference. Recommend adding "formerly at" prefix for clarity.

### 3.3 `game/ui/screens/test_lab/test_lab_input_handler.py` (03_CONVENTIONS.md:77) — MAJOR

**Issue:** Actual file is `game/ui/screens/test_lab/screen_input_handler.py`. The handler naming convention table has the wrong filename.

### 3.4 `game/core/input_handler.py` (03_CONVENTIONS.md:80) — FALSE POSITIVE

**Issue:** The doc says "DON'T: Reference `InputHandler` at `game/core/input_handler.py` -- it does not exist." This is a correct negative warning, not a stale reference. No action needed.

### 3.5 `tests/regression/test_modifier_ability_snapshots.py` (adding_modifiers.md) — CRITICAL

**Issue:** The guide references this test file, which was split into a package. The path is dead.

### 3.6 `AgentCoordination/Scratchpad/` directory does not exist — MAJOR

**Issue:** AGENTS.md and CLAUDE.md instruct agents to write to `AgentCoordination/Scratchpad/` subdirectories, but the directory was never created.

---

## 4. Stale PROJ Reference Register

Zero truly stale PROJ references found (features described as "planned/in progress" when completed). All PROJ-IDs cited in docs reflect completed or archived features. The "unknown" scanner status for many PROJs reflects the scanner's inability to classify deep_archive projects — the manually verified context is correct.

---

## 5. Doc Staleness Register

No docs exceed the formal staleness threshold. However, the following have the oldest "Last verified" dates:

| Doc | Last Verified | Age (days) |
|-----|--------------|------------|
| docs/systems/research_system.md | 2026-03-14 | 51 |
| docs/systems/resource_system.md | 2026-03-31 | 34 |
| docs/systems/ai_system.md | 2026-04-11 | 23 |

All other docs are within 7 days. No doc has a missing "Last verified" line among docs/ files. Root agent docs (AGENTS.md, CLAUDE.md, CODEX.md) lack "Last verified" dates but this convention was designed for docs/ only.

---

## 6. Content Accuracy Issues (Code vs Docs)

### 6.1 Exception count: doc says 10, code has 26 (MAJOR)
`docs/01_ARCHITECTURE.md:127` lists "10 exception classes." Actual `game/core/exceptions.py` contains 26 exception classes (LLM and Image hierarchies added 14 classes via PROJ-296 and PROJ-314).

### 6.2 Core exports count: doc says 46, code has 53 (MAJOR)
`docs/01_ARCHITECTURE.md:227` states 46 exports. Running `len(__all__)` on `game/core/__init__.py` returns 53.

### 6.3 Pattern count: README says 30, actual is 33 (MAJOR)
`docs/README.md` advertises 30 patterns; `docs/02_PATTERNS.md` documents 33. Three patterns added since README was last updated (Pattern #31: Strategy Modal Window Base Class, #32: Compositional Construction, #33: UI Widget Test Factory).

### 6.4 Assets layer diagram placement (MAJOR)
`docs/01_ARCHITECTURE.md:14-43` places Assets between UI and AI visually, but its dependency set (Services+Core only) places it near Engine. The AGENTS.md bottom-up ordering (Core / Services / Assets / Engine) is correct.

### 6.5 500 LOC ceiling is aspirational (MAJOR)
~84 production files exceed 500 lines, some by 400+ lines (e.g., `planetary.py`: 913 LOC, `order_processor.py`: 910 LOC).

### 6.6 Stale ability class names in combat_simulation.md (MAJOR)
`combat_simulation.md:867` lists `PlanetaryEnergyGeneratorAbility` and `PlanetaryEnergyStorageAbility` which were removed by PROJ-238.

### 6.7 PodStorageAbility does not exist as a class (MAJOR)
`ability_reference.md:773` lists `PodStorageAbility` as a class, but `ship_stats.py:373` confirms it has no Python class — it's read from raw abilities dict.

### 6.8 Missing core modules from architecture doc table (MAJOR)
Four production modules in `game/core/` missing from the architecture reference table: `ship_classes.py`, `component_state.py`, `state_machine.py`, `return_destination.py`.

---

## 7. Undocumented Modules (Top Impact)

194 production modules > 50 LOC have zero doc mention. Highest-priority gaps:

| Module | LOC | Priority | Reason |
|--------|-----|----------|--------|
| `game/strategy/systems/save_game_service.py` | 519 | **P1** | Largest undocumented module; save/load is a core system |
| `game/simulation/replay/replay_serialization.py` | 640 | **P1** | Replay system entirely undocumented |
| `game/ui/panels/race_summary_panel.py` | 733 | **P2** | Largest UI panel with no doc |
| `game/ui/screens/builder/structure_list_items.py` | 640 | **P2** | Large UI builder module |
| `game/strategy/engine/planet_action_engine.py` | 387 | **P2** | Engine module partially referenced but no file-level doc |
| `game/ui/screens/strategy_panel_manager.py` | 507 | **P2** | Large strategy UI module |
| `game/ui/screens/event_log_window.py` | 515 | **P3** | Large strategy UI module |
| `game/ui/screens/design_selector_window.py` | 615 | **P3** | Large strategy UI module |

Remaining 186 modules are UI screens, panels, widgets, and internal services.

---

## 8. Cross-Doc Consistency Issues

### 8.1 Python version contradiction (CRITICAL)
- **AGENTS.md:52** says "Python 3.14"
- **CLAUDE.md:94** says "Python 3.13+"
- **docs/03_CONVENTIONS.md** §8 says "Python 3.13+"
- Actual runtime: Python 3.14.2

AGENTS.md is correct; CLAUDE.md and 03_CONVENTIONS.md need updating.

### 8.2 Stale cross-reference section number (MAJOR)
`docs/03_CONVENTIONS.md` §10.2 references "§5" for PNG format rules, but the PNG rule is in §3.2.

### 8.3 Duplicate heading §6.5 (MINOR)
`docs/03_CONVENTIONS.md` has two `### 6.5` headings (lines 495 and 511). The second should be §6.6.

### 8.4 Retired protocols lack visual markers (MINOR)
Protocols 08 and 10 are retired but appear alongside active protocols with no naming convention distinction. `WORKER_TEMPLATE.md:189` still references retired Protocol 08 as "Primary."

### 8.5 Spatial terminology: Consistent (PASS)
"System" vs "Sector", "Battle" vs "Combat", "Screen" vs "Scene", "Builder" vs "Workshop" — all docs use these consistently with AGENTS.md definitions.

---

## 9. Prioritized Documentation Update Plan

### Tier 0 — Fix Immediately (CRITICAL)

| # | Issue | Docs to Update | Effort |
|---|-------|---------------|--------|
| 1 | Dead test path in `adding_modifiers.md` | `docs/guides/adding_modifiers.md` | Low |
| 2 | Stale imports in `adding_abilities.md` (movement.py → propulsion.py) | `docs/guides/adding_abilities.md` | Low |
| 3 | Fix Python version in CLAUDE.md and 03_CONVENTIONS.md | `CLAUDE.md:94`, `docs/03_CONVENTIONS.md` | Low |

### Tier 1 — Fix Within the Week (CRITICAL/MAJOR)

| # | Issue | Docs to Update | Effort |
|---|-------|---------------|--------|
| 4 | Update all `game/core/protocols.py` references to `game/core/protocols/` | `01_ARCHITECTURE.md`, `02_PATTERNS.md`, `04_SERVICES.md`, `systems/strategy_layer.md` (10 sites) | Medium |
| 5 | Fix exception count (10→26) in architecture doc | `docs/01_ARCHITECTURE.md:127` | Low |
| 6 | Fix core exports count (46→53) | `docs/01_ARCHITECTURE.md:227` | Low |
| 7 | Fix pattern count in README (30→33, 3 locations) | `docs/README.md` | Low |
| 8 | Fix test_lab input handler filename in conventions | `docs/03_CONVENTIONS.md:77` | Low |
| 9 | Fix stale ability class names in combat_simulation.md | `docs/systems/combat_simulation.md:867` | Medium |
| 10 | Fix PodStorageAbility class claim | `docs/systems/ability_reference.md:773` | Low |
| 11 | Fix section reference in 03_CONVENTIONS.md §10.2 | `docs/03_CONVENTIONS.md` | Low |
| 12 | Fix duplicate §6.5 heading | `docs/03_CONVENTIONS.md` | Low |
| 13 | Create `AgentCoordination/Scratchpad/` directory | File system | Low |

### Tier 2 — Fix When Convenient (MAJOR)

| # | Issue | Docs to Update | Effort |
|---|-------|---------------|--------|
| 14 | Fix layer diagram Assets placement or add explanatory note | `docs/01_ARCHITECTURE.md:14-43` | Medium |
| 15 | Add missing core modules to architecture table | `docs/01_ARCHITECTURE.md:115-139` | Low |
| 16 | Add replay_player.py to intentional late-imports list | `docs/01_ARCHITECTURE.md:365-369` | Low |
| 17 | Fix delegate Quick Reference primary file | `docs/02_PATTERNS.md:1530` | Low |
| 18 | Add replay system to architecture doc simulation layer table | `docs/01_ARCHITECTURE.md` | Medium |
| 19 | Add missing strategic abilities to quick-reference table | `docs/systems/ability_reference.md` | Low |
| 20 | Update retired protocol visual markers or rename | `Projects/protocols/08_*`, `Projects/protocols/10_*` | Low |
| 21 | Remove stale Protocol 08 reference from WORKER_TEMPLATE | `Projects/protocols/WORKER_TEMPLATE.md:189` | Low |
| 22 | Add "Last verified" dates to root agent docs | `AGENTS.md`, `CLAUDE.md`, `CODEX.md` | Low |

### Tier 3 — Documentation Coverage Gaps

| # | Topic | New/Update Doc | Effort |
|---|-------|---------------|--------|
| 23 | Battle Replay System (PROJ-312) | New section in `systems/combat_simulation.md` or new doc | High |
| 24 | Strategy Session Facade Slice Architecture | New section in `systems/strategy_layer.md` or `04_SERVICES.md` | High |
| 25 | Save/Load Service | New section in `systems/strategy_layer.md` | Medium |
| 26 | Retreat Manager | New subsection in `systems/combat_simulation.md` | Medium |
| 27 | Ship Component Manager | New subsection in `systems/combat_simulation.md` | Medium |
| 28 | Missing guide: Replay System | New doc in `docs/guides/` | High |

---

## 10. Appendices

### A. Raw Phase 1 Data
- `Reviews/results/2026-05-04_090303_docs-audit/raw/doc_file_refs.json`
- `Reviews/results/2026-05-04_090303_docs-audit/raw/stale_proj_refs.json`
- `Reviews/results/2026-05-04_090303_docs-audit/raw/doc_staleness.json`
- `Reviews/results/2026-05-04_090303_docs-audit/raw/undocumented_modules.json`
- `Reviews/results/2026-05-04_090303_docs-audit/raw/doc_inventory.json`

### B. Phase 2 Agent Findings
- `Reviews/results/2026-05-04_090303_docs-audit/findings/docs_review_G1.md` — Architecture & Reference Docs
- `Reviews/results/2026-05-04_090303_docs-audit/findings/docs_review_G2.md` — System Reference Docs
- `Reviews/results/2026-05-04_090303_docs-audit/findings/docs_review_G3.md` — How-To Guides
- `Reviews/results/2026-05-04_090303_docs-audit/findings/docs_review_G4.md` — Root Agent Docs + Project Protocols
- `Reviews/results/2026-05-04_090303_docs-audit/findings/docs_review_G5.md` — Reviews Protocols
- `Reviews/results/2026-05-04_090303_docs-audit/findings/docs_consistency_cross.md` — Cross-Doc Consistency
- `Reviews/results/2026-05-04_090303_docs-audit/findings/docs_accuracy_code.md` — Code-Base Accuracy Validation

### C. Methodology
1. **Phase 1** — Deterministic scanner (`Tools/docs_audit/docs_audit.py`): file path validation, PROJ status cross-referencing, staleness analysis, undocumented module detection, doc inventory.
2. **Phase 2** — 7 parallel agents: 5 doc-group reviewers, 1 cross-doc consistency validator, 1 code-base accuracy validator.
3. **Phase 3** — Report compilation with severity-weighted prioritization.
