# Cross-Doc Consistency Report

> **Generated:** 2026-05-20  
> **Scope:** `docs/` all files + `AGENTS.md` + `CLAUDE.md` + `.agents/CODEX.md`

## Summary

- Doc files analyzed: 30
- Consistency issues found: 18
- Critical: 2 | Major: 7 | Minor: 9

---

## Terminology Issues

### CRITICAL: Python baseline version mismatch

| File | Version stated |
|---|---|
| **AGENTS.md** (line 10) | **Python 3.14** |
| **CLAUDE.md** (line 94) | Python 3.13+ |
| **docs/README.md** (line 86) | Python 3.13 |
| **docs/03_CONVENTIONS.md** (line 489) | Python 3.13+ |
| **docs/guides/simulation_testing.md** (line 614) | Python 3.13+ |

**Impact:** AGENTS.md is the canonical rules file and claims 3.14. Every other doc (and `pyproject.toml` per 03_CONVENTIONS.md: "`requires-python = '>=3.13'`") says 3.13+. Tooling and environment expectations diverge based on which doc an agent reads first.

**Fix:** Update AGENTS.md line 10 to "3.13+".

---

### MAJOR: Pattern #40 / #41 numbering mismatch in 03_CONVENTIONS.md

`docs/03_CONVENTIONS.md` line 131:
```
see Pattern #40 in `docs/02_PATTERNS.md`
```
`docs/02_PATTERNS.md` pattern map:
| # | Pattern |
|---|---|
| 40 | Named Pre-Tick Setup Registry |
| 41 | Polymorphic Order Issuer (`IIssuerAdapter`) |

The text in 03_CONVENTIONS.md discusses `IIssuerAdapter` / FMS command polymorphism, which is **Pattern #41**, not #40.

**Fix:** Change `Pattern #40` to `Pattern #41` in `docs/03_CONVENTIONS.md` line 131.

---

### MAJOR: Stale `strategy_layer.md` satellites description contradicts current implementation

`docs/systems/satellites.md` (line 19-20):
> and a distinct `satellite_group` fleet namespace

This uses "fleet namespace" language for `SatelliteConstellation`, but `SatelliteConstellation` is a `DeployedGroup` (Pattern #37), **NOT a Fleet**. All other docs (02_PATTERNS.md, strategy_layer.md, fighters.md) consistently describe `DeployedGroup` subclasses as siblings of Fleet, not as fleets.

**Fix:** Replace "fleet namespace" with "deployed-group namespace" in `docs/systems/satellites.md` line 20.

---

### MINOR: "System scope" / "Sector scope" - terminology is consistent

All 30 docs use "star system" / "System" meaning radius-50 region (8000 hexes) and "Sector" / "hex" meaning single hex consistently. No violations found. The AGENTS.md definitions are faithfully reproduced across all docs.

---

### MINOR: `CLAUDE.md` duplicates spatial definitions from `AGENTS.md`

`CLAUDE.md` (lines 98-100):
> Spatial terms are precise: a star system is the radius-50 region around a star; a sector is one hex. System-scope effects apply across the star system. Sector-scope effects apply to one hex.

This is an intentional reinforcement (per CLAUDE.md line 47-48: "closed validator markers signal these are intentional duplications, not drift"). Not flagged as an issue but noted for duplicate documentation tracking.

---

### MINOR: "AbilityScope values" listed in `component_system.md` are incomplete vs actual enum

`docs/guides/component_system.md` (lines 98-101):
```
AbilityScope values:
- self, fleet, sector, allied_sector, system, allied_system.
- planet, empire, allied_empire.
- enemy_sector, enemy_system, player_sector, player_system.
```

`docs/systems/ability_reference.md` (lines 112-129) additionally includes `player_sector` and `player_system`, matching the actual `AbilityScope` enum in `game/simulation/components/abilities/base.py`. The guide is missing two scope values.

**Fix:** Add `player_sector` and `player_system` to the scope list in `docs/guides/component_system.md`.

---

## Contradictory Guidance

### MAJOR: `docs/README.md` stale pattern count - "33 patterns" acknowledged but uncorrected

`docs/README.md` (line 166):
> Pattern index currently includes sections `#34 Weapon Family Registry` and `#35 Stat Contributor Registry`; older "33 patterns" summary text is stale.

The README admits the reference to "33 patterns" is stale but does not update the count. The actual count is **43** (per `docs/02_PATTERNS.md` line 9). Leaving "33 patterns" in prose without a replacement number misleads readers who skip the stale-name-traps section.

**Fix:** Replace "33 patterns" with "43 patterns" and remove the self-referential staleness note, or simply state "43 patterns (see `docs/02_PATTERNS.md` for the full map)."

---

### MAJOR: Simulation layer "may depend on" differs between AGENTS.md and 03_CONVENTIONS.md

| Doc | Simulation dependencies |
|---|---|
| **AGENTS.md** (line 8) | Core / Services / Assets / Engine |
| **docs/README.md** (line 67) | Core, Services, Engine |
| **docs/01_ARCHITECTURE.md** (line 18) | Engine, Services, Core |
| **docs/03_CONVENTIONS.md** (line 144) | Core, Services, Engine |

AGENTS.md lists Assets in Simulation's dependency list, but no other doc does. `docs/01_ARCHITECTURE.md` explicitly lists forbidden imports: "`game/engine/` does not import Simulation, Strategy, AI, or UI" and "`game/assets/` does not import UI, Strategy, Simulation, Research, AI, or Engine." Simulation depending on Assets would be an upward dependency that violates the layered architecture since Assets sits at a higher tier than Engine.

**Fix:** Remove "Assets" from Simulation's dependency list in AGENTS.md line 8.

---

### MINOR: `01_ARCHITECTURE.md` "may depend on" for AI differs from other docs

| Doc | AI dependencies |
|---|---|
| **AGENTS.md** (line 10) | Core, Services, Engine, Simulation |
| **docs/README.md** (line 70) | Core, Services, Engine, Simulation |
| **docs/01_ARCHITECTURE.md** (line 15) | Simulation, Engine, Services, Core |
| **docs/03_CONVENTIONS.md** (line 147) | Core, Services, Engine, Simulation |

These are semantically identical (just different ordering), but the ordering inconsistency forces a reader to re-parse. Not a normative conflict.

---

### MINOR: AGENTS.md says "Combat Lab tests" under commands, CLAUDE.md doesn't

AGENTS.md includes `python -m combat_lab.run_tests` in the command list. CLAUDE.md includes it in the canonical commands block. Neither mentions the Combat Lab runner being excluded from pytest. Only `docs/guides/simulation_testing.md` (line 17) explains this: "The scenario suite itself does not use pytest; run it with `python -m combat_lab.run_tests`." New agents reading only AGENTS.md may try to run Combat Lab scenarios through pytest.

---

## Cross-Reference Problems

### MAJOR: `docs/guides/testing_infrastructure.md` references `newdocs/02_PATTERNS.md`

`docs/guides/testing_infrastructure.md` (line 129):
```
`tests/fixtures/ui_widget_factory.py` plus `*_ui_builder.py` fixtures: UI construction seams documented in `newdocs/02_PATTERNS.md`.
```

`newdocs/` does not exist. The correct path is `docs/02_PATTERNS.md` (Patterns #32 and #33).

**Fix:** Change `newdocs/02_PATTERNS.md` to `docs/02_PATTERNS.md`.

---

### MAJOR: `docs/guides/adding_abilities.md` references `docs/02_PATTERNS.md` but doesn't link

`docs/guides/adding_abilities.md` line 417 references `game/strategy/services/ability_metadata.py` as "the unified `AbilityMetadataRegistry` introduced by PROJ-429 / TD-07". The path is correct but the module name is `effect_ability_metadata.py` per `docs/04_SERVICES.md` line 62. The abbreviation "ability_metadata.py" as a conceptual reference doesn't match the actual filename.

**Fix:** Use the exact filename `effect_ability_metadata.py` when referencing the file, or clarify "the unified registry in `effect_ability_metadata.py`."

---

### MINOR: `docs/guides/component_system.md` references `docs/02_PATTERNS.md` correctly

Line 366: `docs/02_PATTERNS.md` - registry DI, two-phase ability aggregation, ability-stat registry, stat contributor registry. All sections exist. Verified.

---

### MINOR: `docs/guides/adding_modifiers.md` references `docs/guides/modifier_system.md` - good

Cross-references between these two guides are consistent and point to real sections.

---

### MINOR: `docs/systems/fighters.md` references project files outside `docs/`

Line 14: `../../Projects/active_projects/PROJ-FMS-shared/design.md` - points to a project file outside the `docs/` tree. This path may rot if the project is archived. Same pattern in `docs/systems/satellites.md` line 21. Not an issue per the methodology (these are cross-references to a project source, not a doc reference), but noted for awareness.

---

## Duplicate Documentation

### MAJOR: TDD, layer model, 500 LOC ceiling, broad-catch rule duplicated across 5 files

The same four non-negotiable rules appear nearly verbatim in:
1. **AGENTS.md** §"Non-Negotiable Rules" (lines 3-8)
2. **CLAUDE.md** §"Reinforcement of AGENTS.md rules" (lines 44-90) — intentionally duplicated with validator markers
3. **docs/README.md** §"Current Contracts" (lines 82-102)
4. **docs/03_CONVENTIONS.md** scattered across multiple sections

CLAUDE.md's duplication is explicitly intentional ("the model loses fidelity past ~50% of the window"). docs/README.md and docs/03_CONVENTIONS.md serve different purposes — README is a quick-reference index, 03_CONVENTIONS is the canonical conventions file. However, rules like "no save-file migrations" appear in all four with slightly different wording, making it unclear which is authoritative when wording diverges.

**Recommendation:** `docs/03_CONVENTIONS.md` is canonical for conventions. `AGENTS.md` is canonical for non-negotiable rules. `docs/README.md` should point to both rather than paraphrasing. `CLAUDE.md` should maintain its reinforcement section but keep wording byte-identical to AGENTS.md.

---

### MINOR: Spatial terminology duplicated 6+ times

The "star system = radius-50, sector = one hex" definition appears in:
- AGENTS.md (lines 11-12)
- CLAUDE.md (lines 98-100)
- docs/README.md (lines 98-100)
- docs/03_CONVENTIONS.md (lines 28-36)
- docs/systems/strategy_layer.md (line 12)
- docs/guides/component_system.md (lines 105-106)

All copies are consistent in meaning, but the AGENTS.md and README.md versions are slightly different in wording from the 03_CONVENTIONS.md version. 03_CONVENTIONS.md has the most detail (400 hex spacing, conversion formula, sector precision).

**Recommendation:** 03_CONVENTIONS.md is the canonical spatial terminology reference. Other docs should reference it rather than rewording.

---

### MINOR: Service-layer rules duplicated in AGENTS.md, 01_ARCHITECTURE.md, 04_SERVICES.md

AGENTS.md architecture quick-reference says "Core / Services / Assets / Engine -> Simulation / Research -> Strategy / AI -> UI". 01_ARCHITECTURE.md has the full layer table with forbidden imports. 04_SERVICES.md has the placement rules. All agree but each contains slightly different subsets of the same rules. The AGENTS.md quick-reference is missing the Assets dependency restrictions that 01_ARCHITECTURE.md and 03_CONVENTIONS.md include.

---

### MINOR: Test commands duplicated in 6 files

The same four test commands appear in: AGENTS.md, CLAUDE.md, docs/README.md, docs/03_CONVENTIONS.md, docs/04_SERVICES.md, and docs/guides/testing_infrastructure.md. The canonical source is `docs/guides/testing_infrastructure.md`.

---

## Terminology Normalization Recommendations

| Term | Canonical definition | Canonical source | Notes |
|---|---|---|---|
| **Star system / System** | Radius-50 circular region around a star (~8000 hexes) | `docs/03_CONVENTIONS.md` lines 28-36 | AGENTS.md, README.md, CLAUDE.md all agree |
| **Sector** | One `HexCoord` (single hex) | `docs/03_CONVENTIONS.md` line 31 | Consistently used |
| **System scope** | Effects apply across the star-system region | `AGENTS.md` line 12 | Used consistently |
| **Sector scope** | Effects apply to one hex | `AGENTS.md` line 12 | Used consistently |
| **Battle** | Full simulation orchestration, engagement state, resolution | `docs/03_CONVENTIONS.md` line 11 | BattleEngine, BattleService, etc. |
| **Combat** | Entity-level per-ship or per-component mechanics | `docs/03_CONVENTIONS.md` line 12 | ShipCombatEngine, CombatConstants, etc. |
| **Screen** | Major game state | `docs/03_CONVENTIONS.md` line 17 | BattleScreen, StrategyScreen |
| **Scene** | Menu/minor state | `docs/03_CONVENTIONS.md` line 19 | MenuScene, KeybindingsScene |
| **Order** | Unified order model (fleet + planet) | `docs/03_CONVENTIONS.md` lines 102-111 | Order, OrderType, OrderProcessor |
| **DeployedGroup** | Typed sibling of Fleet for mines/fighters/satellites | `docs/02_PATTERNS.md` Pattern #37 | NOT a Fleet; no `.group_kind` discriminator |
| **Facade** | Stable narrow API hiding orchestration | `docs/02_PATTERNS.md` Pattern #5 | StrategySessionFacade is the only UI entry |
| **Container** | Unified mass-priced storage substrate | `docs/02_PATTERNS.md` Pattern #43 | BayInventory, resources, items, population |

---

## Issue Index

| # | Severity | Category | Location | Issue |
|---|---|---|---|---|
| 1 | CRITICAL | Terminology | `AGENTS.md:10` | Python baseline says 3.14; all other docs say 3.13+ |
| 2 | CRITICAL | Contradictory | `AGENTS.md:8` | Simulation layer dependency list includes Assets; other docs do not |
| 3 | MAJOR | Cross-reference | `docs/03_CONVENTIONS.md:131` | References Pattern #40; should be Pattern #41 |
| 4 | MAJOR | Cross-reference | `docs/guides/testing_infrastructure.md:129` | `newdocs/02_PATTERNS.md` — directory does not exist |
| 5 | MAJOR | Terminology | `docs/systems/satellites.md:20` | "fleet namespace" for SatelliteConstellation, which is a DeployedGroup |
| 6 | MAJOR | Contradictory | `docs/README.md:166` | "33 patterns" stale text, actual count is 43 |
| 7 | MAJOR | Duplicate | Multi-file | TDD/layer/500LOC rules paraphrased in 4+ files with divergent wording |
| 8 | MAJOR | Cross-reference | `docs/guides/adding_abilities.md:417` | References `ability_metadata.py` but actual filename is `effect_ability_metadata.py` |
| 9 | MINOR | Terminology | `docs/guides/component_system.md:98-101` | Missing `player_sector` and `player_system` from AbilityScope list |
| 10 | MINOR | Contradictory | `docs/01_ARCHITECTURE.md:15` | AI dependency order differs from other docs (same set, different order) |
| 11 | MINOR | Duplicate | Multi-file | Spatial terminology duplicated 6x; 03_CONVENTIONS.md is most detailed |
| 12 | MINOR | Duplicate | Multi-file | Service-layer dependency rules in 3 files with varying completeness |
| 13 | MINOR | Duplicate | Multi-file | Test commands duplicated in 6 files |
| 14 | MINOR | Cross-reference | `docs/systems/fighters.md:14` | Cross-reference to project file may rot after project archival |
| 15 | MINOR | Cross-reference | `docs/systems/satellites.md:21` | Same project-file cross-reference pattern as fighters.md |
| 16 | MINOR | Terminology | `CLAUDE.md:94` | Intentional duplication of spatial terminology (validator-marked) |
| 17 | MAJOR | Contradictory | `AGENTS.md` commands | Combat Lab runner listed but not explained as non-pytest |
| 18 | MINOR | Duplicate | `CLAUDE.md:44-90` | Intentional rule reinforcement; wording differs slightly from AGENTS.md |
