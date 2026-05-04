# Verification Log

Per `Reviews/protocols/11_apply_doc_audit.md`. Each work item is dispatched to a verifier; verdict + evidence below.

---

## T0-01: Dead test path in adding_modifiers.md

**Source:** report.md Tier 0, row 1 → findings/docs_review_G3.md (Finding 1)
**Doc target:** `docs/guides/adding_modifiers.md:166`
**Claim type:** dead-reference
**Verdict:** CONFIRMED
**Evidence:**
- `tests/regression/test_modifier_ability_snapshots.py` does not exist (ls error).
- `tests/regression/modifier_ability_snapshots/` package exists with `conftest.py`, `test_utility_modifiers.py`, `test_weapon_modifiers.py`.
- Doc text grepped at line 166: `Add regression test in tests/regression/test_modifier_ability_snapshots.py:` — uncorrected.

**Decision:** apply

---

## T0-02: Stale movement.py imports in adding_abilities.md

**Source:** report.md Tier 0, row 2 → findings/docs_review_G3.md (Finding 2, 5)
**Doc target:** `docs/guides/adding_abilities.md:135, 404`
**Claim type:** code-example
**Verdict:** CONFIRMED
**Evidence:**
- `game/simulation/components/abilities/movement.py` does not exist.
- `game/simulation/components/abilities/propulsion.py` exists; `ThrusterAbility` lives there.
- Doc line 34 already references `abilities/propulsion.py` for the example — line 135 (`from .movement import ThrusterAbility`) and line 404 (`from game.simulation.components.abilities.movement import ThrusterAbility`) contradict that.

**Decision:** apply (both lines)

---

## T0-03: Python version in CLAUDE.md and 03_CONVENTIONS.md

**Source:** report.md Tier 0, row 3 → findings/docs_consistency_cross.md
**Doc target:** `CLAUDE.md:94`, `docs/03_CONVENTIONS.md:534`
**Claim type:** cross-doc
**Verdict:** DISPUTED
**Evidence:**
- `python --version` → Python 3.14.4 (installed runtime).
- `pyproject.toml:4` → `requires-python = ">=3.13"` (configured baseline).
- `pyproject.toml:5` → `# PROJ-295: Pinned to 3.13+ on 2026-04-26 because Python 3.10 EOL is 2026-10-04`.
- `CLAUDE.md:94` says "Python baseline: 3.13+." — agrees with pyproject.toml.
- `docs/03_CONVENTIONS.md:534` says "Python 3.13+ baseline (PROJ-295)" — agrees with pyproject.toml.
- `AGENTS.md:52` says "Python 3.14" — disagrees with pyproject.toml.
- The audit chose CLAUDE.md and 03_CONVENTIONS.md as the fix targets, but pyproject.toml is the canonical source for the supported baseline. CLAUDE.md and 03_CONVENTIONS.md are correct; AGENTS.md is the disagreeing doc, but AGENTS.md is not the audit's fix target.

**Decision:** skip (audit's chosen fix targets contradict ground truth in pyproject.toml)

---

## T1-04: `game/core/protocols.py` references (12 sites across 4 docs)

**Source:** report.md Tier 1, row 4 → findings/docs_review_G1.md (DOC-G1-001), G2 strategy_layer.md, accuracy report §1
**Doc targets:**
- `docs/01_ARCHITECTURE.md:124, 276, 346`
- `docs/02_PATTERNS.md:150, 158, 183, 207, 1185, 1526, 1546`
- `docs/04_SERVICES.md:1114`
- `docs/systems/strategy_layer.md:680`

**Claim type:** dead-reference
**Verdict:** CONFIRMED
**Evidence:**
- `ls game/core/protocols.py` → does not exist.
- `ls game/core/protocols/` → directory with 9 sub-modules (`boundary.py`, `combat.py`, `common.py`, `persistence.py`, `registry.py`, `strategy_domain.py`, `strategy_entities.py`, `ui.py`, `__init__.py`).
- Sub-module mapping verified by grep:
  - `IRegistryProvider` → `game/core/protocols/registry.py`
  - `ISerializable` → `game/core/protocols/persistence.py`
  - `IFleet`, `IOrderable` → `game/core/protocols/strategy_entities.py`
  - `IRaceRegistry` → `game/core/protocols/strategy_domain.py`
- All 12 grep'd doc occurrences confirmed present.

**Decision:** apply

---

## T1-05: Exception count 10 → 26 in 01_ARCHITECTURE.md

**Source:** report.md Tier 1, row 5 → findings/docs_accuracy_code.md §2
**Doc target:** `docs/01_ARCHITECTURE.md:126` (audit cited :127, drifted by 1)
**Claim type:** content-count
**Verdict:** CONFIRMED
**Evidence:**
- `grep -c '^class ' game/core/exceptions.py` → 26.
- Doc text at line 126: `exceptions.py | GameException hierarchy (10 exception classes)` — uncorrected.

**Decision:** apply

---

## T1-06: Core exports 46 → 53

**Source:** report.md Tier 1, row 6 → findings/docs_review_G1.md (DOC-G1-004)
**Doc target:** `docs/01_ARCHITECTURE.md:227`
**Claim type:** content-count
**Verdict:** CONFIRMED
**Evidence:**
- `python -c "from game.core import __all__; print(len(__all__))"` → 53.
- Doc heading at line 227: `### \`game.core\` (46 exports)`.

**Decision:** apply

---

## T1-07: Pattern count 30/31 → 33 in README (3 locations)

**Source:** report.md Tier 1, row 7 → findings/docs_review_G1.md (DOC-G1-005), docs_consistency_cross.md
**Doc targets:** `docs/README.md:4, 17, 68`
**Claim type:** content-count
**Verdict:** CONFIRMED
**Evidence:**
- `02_PATTERNS.md` heading scan: highest pattern is `## 33. UI Widget Test Factory` (line 1735); `## 32. Compositional Construction` (line 1676); `## 31. Strategy Modal Window Base Class` (line 1640). Total = 33 patterns.
- `docs/README.md:4` ("pattern count is 31"), `docs/README.md:17` ("30 design patterns"), `docs/README.md:68` ("30 design patterns").

**Decision:** apply (all 3 sites, with consistent 33)

---

## T1-08: test_lab handler filename in 03_CONVENTIONS.md

**Source:** report.md Tier 1, row 8 → findings/docs_review_G1.md (DOC-G1-003)
**Doc target:** `docs/03_CONVENTIONS.md:77`
**Claim type:** dead-reference
**Verdict:** CONFIRMED
**Evidence:**
- `ls game/ui/screens/test_lab/test_lab_input_handler.py` → does not exist.
- `ls game/ui/screens/test_lab/screen_input_handler.py` → exists.

**Decision:** apply

---

## T1-09: Stale ability class names in combat_simulation.md (planetary.py row)

**Source:** report.md Tier 1, row 9 → findings/docs_review_G2.md
**Doc target:** `docs/systems/combat_simulation.md:867`
**Claim type:** stale-symbol
**Verdict:** CONFIRMED
**Evidence:**
- Doc line 867: `| planetary.py | PlanetaryShieldAbility, PlanetaryEnergyGeneratorAbility, PlanetaryEnergyStorageAbility |`.
- `grep "^class.*Ability" game/simulation/components/abilities/planetary.py` → 18 classes; `PlanetaryEnergyGeneratorAbility` and `PlanetaryEnergyStorageAbility` are absent. Current classes match audit's recommended replacement set.
- Note: line 864 (SuperweaponMarker) was flagged in findings but is already present in the doc — that sub-finding is ALREADY-FIXED. Line 865 (harvester.py incomplete list) was also flagged but is outside the prioritized plan row scope; not applied here.

**Decision:** apply (line 867 only, scope of plan row)

---

## T1-10: PodStorageAbility class claim in ability_reference.md

**Source:** report.md Tier 1, row 10 → findings/docs_review_G2.md
**Doc target:** `docs/systems/ability_reference.md:773`
**Claim type:** stale-symbol
**Verdict:** CONFIRMED
**Evidence:**
- `grep -rn "class PodStorageAbility" game/` → no matches.
- `game/simulation/entities/ship_stats.py:373`: `# PodStorage has no ability class — read from raw abilities dict`.
- `game/simulation/entities/ship_stats.py:374`: `pod_data = comp.abilities.get('PodStorage')`.
- Doc line 773: `| Class | \`PodStorageAbility\` |`.
- Quick reference line 1555: `| PodStorage | PodStorageAbility | Cargo |` — same defect, same edit.

**Decision:** apply (line 773 detail row + line 1555 quick-ref row)

---

## T1-11: Wrong section reference in 03_CONVENTIONS.md §10.2

**Source:** report.md Tier 1, row 11 → findings/docs_consistency_cross.md
**Doc target:** `docs/03_CONVENTIONS.md:617`
**Claim type:** heading-structure
**Verdict:** CONFIRMED
**Evidence:**
- Line 617: `All ship-theme assets are PNG only (per §5 / docs/03_CONVENTIONS.md §285–288). JPG is not supported.`
- §3.2 (line 283): `### 3.2 Image Asset Format Convention`. PNG-only rule defined here.
- §5 in 03_CONVENTIONS.md is "JSON Data Conventions" (verified), not image format.
- The `§285–288` is a line-number reference, not a section reference (line numbers drift).

**Decision:** apply

---

## T1-12: Duplicate §6.5 heading

**Source:** report.md Tier 1, row 12 → findings/docs_consistency_cross.md
**Doc target:** `docs/03_CONVENTIONS.md:512`
**Claim type:** heading-structure
**Verdict:** CONFIRMED
**Evidence:**
- `grep '^### 6\.' docs/03_CONVENTIONS.md`:
  - `461:### 6.1 Type Hints and Docstrings`
  - `468:### 6.2 Function Size and Nesting`
  - `473:### 6.3 Preferred Patterns`
  - `486:### 6.4 Error Handling Conventions (PROJ-251)`
  - `495:### 6.5 No Hardcoded Type Lists`
  - `512:### 6.5 System Migration` ← duplicate, should be 6.6.

**Decision:** apply

---

## T1-13: Create AgentCoordination/Scratchpad/ directory

**Source:** report.md Tier 1, row 13 → findings/docs_review_G4.md (Finding 1)
**Doc target:** `AgentCoordination/Scratchpad/` (filesystem)
**Claim type:** dead-reference
**Verdict:** ALREADY-FIXED
**Evidence:**
- `ls -la AgentCoordination/Scratchpad/` → directory exists with subdirectories `Discussion/`, `handoffs/`, `plans/`, `reports/`, `reviews/`, `tmp/`. All documented subdirectories present.

**Decision:** skip

---

## T2-14: Layer diagram Assets placement

**Source:** report.md Tier 2, row 14 → findings/docs_accuracy_code.md §3
**Doc target:** `docs/01_ARCHITECTURE.md:14-43`
**Claim type:** default (subjective layout / prose advice)
**Verdict:** INCONCLUSIVE
**Evidence:**
- The dependency rules table (line 50) correctly states `Assets | Services, Core`.
- The visual diagram orders Assets second-from-top (between UI and AI). This is unconventional vs a strict dependency-tree drawing, but neither incorrect nor a dead reference. Choosing whether to redraw the diagram or add an explanatory note is a prose-authoring judgment that the protocol's default rule routes to INCONCLUSIVE.

**Decision:** skip

---

## T2-15: Missing core modules in 01_ARCHITECTURE.md table

**Source:** report.md Tier 2, row 15 → findings/docs_accuracy_code.md §5
**Doc target:** `docs/01_ARCHITECTURE.md:115-139`
**Claim type:** content-count (table completeness)
**Verdict:** CONFIRMED
**Evidence:**
- `ls game/core/{ship_classes,component_state,state_machine,return_destination}.py` → all 4 exist.
- Architecture core-module table (lines 115-139) does not list any of these 4 — verified by reading the table.

**Decision:** apply

---

## T2-16: replay_player.py late-import addition

**Source:** report.md Tier 2, row 16 → findings/docs_accuracy_code.md §9
**Doc target:** `docs/01_ARCHITECTURE.md:362-369`
**Claim type:** content-count (late-imports list)
**Verdict:** CONFIRMED
**Evidence:**
- `grep "from game.strategy" game/simulation/replay/replay_player.py` → line 72: `from game.strategy.data.ship_instance_serializer import (...)`.
- Late-imports list (lines 365-368) lists 4 sites; replay_player.py is not among them.

**Decision:** apply

---

## T2-17: Delegate Quick Reference primary file

**Source:** report.md Tier 2, row 17 → findings/docs_accuracy_code.md §10
**Doc target:** `docs/02_PATTERNS.md:1530`
**Claim type:** default (subjective "primary" judgment)
**Verdict:** INCONCLUSIVE
**Evidence:**
- `ls game/simulation/entities/ship_combat_engine.py` → exists.
- The audit argues a different file (`ship.py`) would be a better "primary" entry. The cited file exists and contains a real delegate. Whether the table should list ship.py first is a subjective ordering preference — not a dead reference or factual error. Routes to INCONCLUSIVE.

**Decision:** skip

---

## T2-18: Add replay system to architecture doc

**Source:** report.md Tier 2, row 18 → findings/docs_review_G1.md (DOC-G1-009)
**Doc target:** `docs/01_ARCHITECTURE.md`
**Claim type:** missing-docs
**Verdict:** DEFERRED
**Evidence:**
- `game/simulation/replay/` exists with 7 files; replay subsystem is not described in any docs/ entry.
- Adding a new section requires authoring multi-paragraph prose. Per protocol §3 missing-docs claims always defer; new prose authoring is high-risk autonomous work.

**Decision:** defer-to-project — recommend `claude-proj-start "Battle Replay System documentation"`

---

## T2-19: Missing strategic abilities in quick-reference table

**Source:** report.md Tier 2, row 19 → findings/docs_review_G2.md
**Doc target:** `docs/systems/ability_reference.md:1531-1586`
**Claim type:** content-count (table completeness)
**Verdict:** CONFIRMED
**Evidence:**
- Read of the quick-reference table (lines 1531-1586) shows zero rows for `EnvironmentalDamage`, `FuelDrain`, `StrategicSpeedModifier`, `ThrustModifier`.
- `grep "^class.*Ability" game/simulation/components/abilities/planetary.py` confirms `EnvironmentalDamageAbility`, `FuelDrainAbility`, `StrategicSpeedModifierAbility`, `ThrustModifierAbility` all exist.

**Decision:** apply

---

## T2-20: Retired protocol visual markers

**Source:** report.md Tier 2, row 20 → findings/docs_review_G4.md (Finding 10)
**Doc target:** `Projects/protocols/08_*`, `Projects/protocols/10_*`
**Claim type:** default (rename/move/banner judgment)
**Verdict:** INCONCLUSIVE
**Evidence:**
- Both retired protocols already carry status banners declaring retirement (per finding #10 itself).
- The audit recommends "rename, move, or add a README-level index". Renaming/moving is destructive; banner additions are subjective prose work. Routes to INCONCLUSIVE.

**Decision:** skip

---

## T2-21: WORKER_TEMPLATE.md retired Protocol 08 reference

**Source:** report.md Tier 2, row 21 → findings/docs_review_G4.md (Finding 11)
**Doc target:** `Projects/protocols/WORKER_TEMPLATE.md:189`
**Claim type:** stale-symbol (broken protocol pointer)
**Verdict:** CONFIRMED
**Evidence:**
- Line 189: `**Primary:** \`Projects/protocols/08_automated_loop_protocol.md\``.
- Protocol 08 is retired (acknowledged in audit Finding 10 and visible in the file's own status banner).
- A worker following this template would be directed at a retired workflow.

**Decision:** apply (annotate the line as retired; keep the link as historical reference, append explicit RETIRED marker)

---

## T2-22: Add "Last verified" to root agent docs

**Source:** report.md Tier 2, row 22 → findings/docs_review_G4.md
**Doc target:** `AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md`
**Claim type:** content-count (metadata)
**Verdict:** DISPUTED
**Evidence:**
- Protocol 11 §Phase 3 step 4 explicitly states: "Only docs under `docs/` carry this line; skip the update for `AGENTS.md` / `CLAUDE.md` / `.agents/CODEX.md` (per the audit's own scope notes)."
- The audit's own G3 finding "Last Verified Coverage" notes the convention is for `docs/` files, and G4 notes "Root agent docs (AGENTS.md, CLAUDE.md, CODEX.md) lack 'Last verified' dates but this convention was designed for docs/ only" (report.md §5).
- The recommendation contradicts the documented scope of the convention.

**Decision:** skip

---

## T3-23 through T3-28: Tier 3 missing-docs gaps

| ID | Topic | Module(s) | Verdict | Decision |
|----|-------|-----------|---------|----------|
| T3-23 | Battle Replay System | `game/simulation/replay/*` (7 files) | DEFERRED | defer-to-project |
| T3-24 | Strategy Session Facade Slice Architecture | `game/strategy/facade/slices/*` (9 files) | DEFERRED | defer-to-project |
| T3-25 | Save/Load Service | `game/strategy/systems/save_game_service.py` (519 LOC) | DEFERRED | defer-to-project |
| T3-26 | Retreat Manager | `game/simulation/managers/retreat_manager.py` (280 LOC) | DEFERRED | defer-to-project |
| T3-27 | Ship Component Manager | `game/simulation/entities/ship_component_manager.py` (293 LOC) | DEFERRED | defer-to-project |
| T3-28 | Replay System guide | `docs/guides/` new doc | DEFERRED | defer-to-project |

**Verdict rationale (all Tier 3):** Missing-docs claims always defer per protocol §7. Verified gaps; no autonomous prose authoring.

**Recommended follow-up:** `claude-proj-start "Documentation Coverage Backfill — Replay, Facade Slices, Save Service, Retreat Manager, Ship Component Manager"` — single project covering all six gaps in coordinated phases.
