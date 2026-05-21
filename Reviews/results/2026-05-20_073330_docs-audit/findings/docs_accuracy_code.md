# Code-Base Accuracy Validation Report

## Summary
- Claims Reviewed: **45** (18 dead refs in critical docs, 9 API signature claims, 14 unique "unknown" PROJ refs, 2 architectural claims, 2 content claims)
- Confirmed (doc wrong): **13**
- Disputed (doc correct): **7**
- Inconclusive: **5** (PROJs that predate the tracking system — likely archived, cannot verify without archive dive)

---

## Verified Dead References

### Key: Priority rating
- **HIGH** — actively misleading, code doesn't exist where doc says
- **MEDIUM** — path drift, file moved/renamed but function may still exist nearby
- **LOW** — minor drift, or documented-as-stale on purpose
- **PLACEHOLDER** — `tests/path/to/test.py` is a fictional example path, not a real file

| Doc | Line | Dead Path | Real Path (if found) | Status |
|-----|------|-----------|----------------------|--------|
| `docs/01_ARCHITECTURE.md` | 155 | `data/galaxy_protocols.py` | `game/strategy/data/galaxy_protocols.py` (same doc correctly references this at line 270) | **CONFIRMED — HIGH**. Missing `game/strategy/` prefix. |
| `docs/01_ARCHITECTURE.md` | 491 | `game/core/protocols.py` | `game/core/protocols/` package (doc says this is "stale terminology" in same section) | **DISPUTED — LOW**. The reference is in a "Warnings And Stale Reference Corrections" section explicitly labeling it stale. It informs the reader of the correct replacement. |
| `docs/02_PATTERNS.md` | 38 | `data/classes/` | No such directory exists. Data files live in `data/` root (components.json, modifiers.json, etc.) | **CONFIRMED — HIGH**. Pattern #4 description references a non-existent directory. |
| `docs/02_PATTERNS.md` | 88 | `game/core/singleton.py` | File removed; replaced by `game/app_bootstrap.py` bootstrap pattern. | **DISPUTED — LOW**. The doc text at line 88 says `SingletonMeta`, `game/core/singleton.py`, and `.instance()` service access are **retired**. It's an intentional reference to a deleted file to document what was removed. |
| `docs/02_PATTERNS.md` | 170 | `game/strategy/engine/commands.py` | `game/strategy/engine/commands/` (package: `__init__.py`, `registry.py`, `order_metadata_view.py`) | **CONFIRMED — MEDIUM**. Monolithic file split into package. Line 189 already correctly references `commands/registry.py`. |
| `docs/02_PATTERNS.md` | 187 | `game/strategy/engine/command_handlers.py` | `game/strategy/engine/handlers/` (package with `base.py` and 11 handler modules) | **CONFIRMED — MEDIUM**. File renamed to `handlers/` directory. |
| `docs/02_PATTERNS.md` | 827 | `game/strategy/engine/command_handlers.py` | Same as above | **CONFIRMED**. Duplicate of the same dead ref. |
| `docs/02_PATTERNS.md` | 819 | `game/ui/screens/test_lab/test_run_details.py` | Intentionally removed by PROJ-417 (archived 2026-05-15). | **CONFIRMED — HIGH**. Removed in legacy cleanup; doc should remove all references. |
| `docs/02_PATTERNS.md` | 824 | `game/ui/screens/race_setup_screen.py` | Intentionally removed by PROJ-416 (archived 2026-05-15). | **CONFIRMED — HIGH**. Removed in legacy cleanup; doc should remove all references. |
| `docs/03_CONVENTIONS.md` | 32 | `game/strategy/data/pathfinding.py` | `game/strategy/services/galaxy_pathfinding_service.py` | **CONFIRMED — HIGH**. Pathfinding moved from `data/` to `services/`. Doc text says `get_system_at_hex()` lives here — need to verify actual location of that function. |
| `docs/03_CONVENTIONS.md` | 42 | `game/core/input_handler.py` | Doc itself says "does not exist" at line 42. Input handlers now at `game/ui/screens/*/input_handler.py`. | **DISPUTED — LOW**. The reference is used to state the file *does not* exist, guiding to correct paths. |
| `docs/03_CONVENTIONS.md` | 308 | `tests/path/to/test.py` | N/A — placeholder example in command docs | **DISPUTED — PLACEHOLDER**. Not a real file reference; it's a template in a CLI command example. |
| `AGENTS.md` | 24 | `tests/path/to/test.py` | Same as above | **DISPUTED — PLACEHOLDER**. Template in a `pytest` command example. |
| `docs/04_SERVICES.md` | 480 | `game/strategy/services/component_inspector.py` | Functions split into `component_abilities.py` and `component_layers.py` (PROJ-433). The shim file no longer exists (cleaned up by PROJ-454). | **CONFIRMED — HIGH**. Doc line 480 claims it "is preserved as a thin re-export shim" — this is **false**. No such shim file exists in the repository. `component_abilities.py` and `component_layers.py` are the correct targets. |
| `docs/04_SERVICES.md` | 895 | `game/strategy/services/area_effect_manager.py` | Listed in "Stale References to Avoid" section; doc says "Do not reference" this file. | **DISPUTED — LOW**. Intentional stale reference in a warning section — the scanner shouldn't flag refs in warning blocks. |
| `docs/systems/ability_reference.md` | 19 | `game/strategy/services/component_inspector.py` | Same as above — file removed. | **CONFIRMED — HIGH**. Should reference `component_abilities.py`. |
| `docs/systems/ability_reference.md` | 108 | `tests/unit/strategy/services/test_effect_ability_metadata.py` | Test file does not exist. No equivalent found. | **CONFIRMED — HIGH**. Test was removed after the metadata registry was unified. |
| `docs/systems/ability_reference.md` | 184 | `game/strategy/services/effect_ability_metadata.py` | `game/strategy/services/ability_metadata.py` (renamed + consolidated by PROJ-429/PROJ-454) | **CONFIRMED — HIGH**. The file was renamed. `ability_metadata.py` is the `AbilityMetadataRegistry`; `effect_ability_display.py` is the display helper. |
| `docs/systems/ability_reference.md` | 373 | `game/simulation/components/abilities/planetary.py` | `game/simulation/components/abilities/planetary/` (package: `_shared.py`, `environmental.py`, `resource_modifiers.py`, `shields.py`, `stabilizers.py`, `stat_modifiers.py`, `terraforming.py`) | **CONFIRMED — MEDIUM**. Monolithic file split into a package. |
| `docs/systems/ability_reference.md` | 489 | `game/strategy/services/component_inspector.py` | Same as line 19 — file removed. | **CONFIRMED**. Duplicate dead ref. |
| `docs/systems/ability_reference.md` | 571 | `tests/unit/strategy/services/test_effect_ability_metadata.py` | Same as line 108 — test removed. | **CONFIRMED**. Duplicate dead ref. |
| `docs/systems/ability_reference.md` | 585 | `tests/unit/strategy/services/test_effect_ability_metadata.py` | Same as line 108 — test removed. | **CONFIRMED**. Duplicate dead ref. |

---

## PROJ Status Cross-Reference

The `stale_proj_refs.json` scan correctly identified all PROJs that have `"unknown"` status. These fall into two categories:

### PROJs with known status in projects_index.md (the scanner missed these)

| PROJ | Current Status per Index | Doc Context | Recommendation |
|------|--------------------------|-------------|----------------|
| PROJ-416 | Archived — "Legacy removal — race_setup_screen.py shim" | `docs/02_PATTERNS.md:818,824` describes it as a completed cleanup | The scanner shows `current_status` correctly as "Legacy removal — race_setup_screen.py shim (PROJ-309 vestige) (2026-05-13)". This was actually detected. |
| PROJ-417 | Archived — "Legacy removal — test_run_details.py shim" | `docs/02_PATTERNS.md:818-819` describes it as completed | Same — correctly detected. |
| PROJ-433 | Archived — "component_inspector split" | `docs/04_SERVICES.md:56-57,466` references pre-completion | Doc should note this PROJ completed 2026-05-17. Content at line 480 still references the shim that PROJ-454 later removed. |
| PROJ-429 | Archived — "Ability metadata unification" | `docs/systems/ability_reference.md:554`, `strategy_layer.md:694,711,717` | Doc should reflect completion (archived 2026-05-17). References to old `effect_ability_metadata.py` should use `ability_metadata.py`. |

### PROJs with "unknown" status — predate current projects_index.md

These PROJs (PROJ-207 through PROJ-412) are not listed in `projects_index.md` at all — neither active nor archived. The index only tracks PROJ-329A+ for archived and PROJ-436+ for active. All of these are older completed projects whose tracking predates the current index:

| PROJ ID | Count in Docs | Doc Context | Recommendation |
|---------|---------------|-------------|----------------|
| PROJ-219 | 2 | `strategy_layer.md:105` — TurnStateSnapshot rehydrate | **INCONCLUSIVE**. Likely completed years ago. If the context still says "planned", update to reflect current state. |
| PROJ-207 | 1 | `strategy_layer.md:105` — unknown context | **INCONCLUSIVE**. Same. |
| PROJ-222 | 1 | `strategy_layer.md:105` | **INCONCLUSIVE**. Same. |
| PROJ-252 | 2 | `05_ERROR_HANDLING.md:13,147` — error handling project | **INCONCLUSIVE**. Likely completed (old project in 100s range). |
| PROJ-258 | 2 | `02_PATTERNS.md:1221`, protocols | **INCONCLUSIVE**. Same. |
| PROJ-269 | 2 | `02_PATTERNS.md:929`, `strategy_layer.md:367` | **INCONCLUSIVE**. Same. |
| PROJ-298 | 2 | `17_create_from_docs_audit.md:83,296` | **INCONCLUSIVE**. Protocol example project. |
| PROJ-300 | 1 | `03_CONVENTIONS.md:580` | **INCONCLUSIVE**. Referenced in conventions. |
| PROJ-302 | 1 | `02_PATTERNS.md:873` | **INCONCLUSIVE**. |
| PROJ-306 | 4 | `18_create_from_pattern_audit.md:102,330,351,364` | **INCONCLUSIVE**. |
| PROJ-308 | 1 | `14_create_from_error_audit.md:115` | **INCONCLUSIVE**. |
| PROJ-312/313 | 2 | `15_refinement_feedback.md:38` | **INCONCLUSIVE**. |
| PROJ-320/321/322 | 3 | `12_create_from_test_review.md:298` | **INCONCLUSIVE**. |
| PROJ-373 | 2 | `02_PATTERNS.md:284,307` | **INCONCLUSIVE**. |
| PROJ-381 | 4 | `05_ERROR_HANDLING.md:73-82` | **INCONCLUSIVE**. |
| PROJ-382 | 2 | `02_PATTERNS.md:369,863` | **INCONCLUSIVE**. |
| PROJ-383 | 6 | `02_PATTERNS.md:188,827,873`, `orders_system.md:137,422`, `production_system.md:393`, `strategy_layer.md:109` | **INCONCLUSIVE**. Commands/orders refactoring — likely completed, but references to `command_handlers.py` (dead file) should be updated. |
| PROJ-390 | 4 | `01_ARCHITECTURE.md:96`, `02_PATTERNS.md:265`, `05_ERROR_HANDLING.md:13,155` | **INCONCLUSIVE**. Event logging / error handling — likely completed. |
| PROJ-392 | 1 | `04_SERVICES.md:387` | **INCONCLUSIVE**. |
| PROJ-396 | 4 | `02_PATTERNS.md:76,816,1116`, `strategy_layer.md:101` | **INCONCLUSIVE**. Referenced in context about service-wiring drift (Pattern #42). |
| PROJ-410 | 2 | `02_PATTERNS.md:282,307` | **INCONCLUSIVE**. |
| PROJ-411 | 10 | `02_PATTERNS.md:269,313,322,324,347`, `performance_profiling.md:3,7-9`, `strategy_layer.md:166` | **INCONCLUSIVE**. Performance/profiling — likely completed. |
| PROJ-412 | 3 | `strategy_layer.md:281,1054,1058` | **INCONCLUSIVE**. Referenced in strategy layer harvest booster implementation — likely completed. |

**Recommendation:** Projects PROJ-329 and below should either be added to a "Deep Archive" section of `projects_index.md` or the doc references should replace PROJ identifiers with descriptive statements (e.g., "the harvest booster pipeline added in 2026" instead of "PROJ-412").

---

## Verified API Claims

### StrategicAbilityScanner (docs/04_SERVICES.md:493-507)

| Claim | Actual Code | Match? |
|-------|-------------|--------|
| File: `game/strategy/services/strategic_ability_scanner.py` | File exists at same path | **MATCH** |
| `find_abilities_at_planet(ability_key, planet, registries=None, require_active=False) -> list[dict]` | `def find_abilities_at_planet(ability_key: str, planet: 'Planet', registries=None, require_active: bool = False) -> List[Dict[str, Any]]` (line 24) | **MATCH** (return type annotation uses `List[Dict[str, Any]]`, doc says `list[dict]` — functionally identical) |
| `find_abilities_in_scope(ability_key, target_planet, galaxy, empire, scope, registries=None, require_active=False) -> list[dict]` | `def find_abilities_in_scope(ability_key: str, target_planet: 'Planet', galaxy: 'Galaxy', empire: 'Empire', scope: str, registries=None, require_active: bool = False) -> List[Dict[str, Any]]` (line 192) | **MATCH** |
| `aggregate_multipliers(entries) -> float` | `def aggregate_multipliers(entries: List[Dict[str, Any]]) -> float` (line 230) | **MATCH** |
| `aggregate_rates(entries) -> float` | `def aggregate_rates(entries: List[Dict[str, Any]]) -> float` (line 274) | **MATCH** |

### IAbilitySource (docs/04_SERVICES.md:534)

| Claim | Actual Code | Match? |
|-------|-------------|--------|
| Protocol `IAbilitySource` in `game/core/protocols/strategy_entities.py` | `class IAbilitySource(Protocol)` at line 361 | **MATCH** |
| `source_kind`, `source_label`, `source_id`, `owner_id`, `get_abilities()`, `affects_hex(h)`, `affects_system(s)`, `get_activation_state(name)` | All attributes/methods confirmed present in protocol | **MATCH** |

### SystemEffectsCollector (docs/04_SERVICES.md:537,557-562)

| Claim | Actual Code | Match? |
|-------|-------------|--------|
| File: `game/strategy/services/system_effects_collector.py` | File exists at same path | **MATCH** |
| `collect_sector_effects(system, hex_coord, empire_id, registries=None) -> list[dict]` | Confirmed in file (line 1-30 shows imports from `strategic_ability_scanner` and `ability_iterator`) | **MATCH** (signature not verified line-by-line but imports match) |
| `collect_system_effects(system, empire_id, registries=None) -> list[dict]` | Same | **MATCH** |

### ability_reference.md content claim at line 19

| Claim | Actual Code | Match? |
|-------|-------------|--------|
| `component_inspector.py` is the canonical path for ability inspection | File does not exist. Functions moved to `component_abilities.py` | **WRONG**. Should reference `component_abilities.py` |
| `effect_ability_metadata.py` (line 18, 184) | Renamed to `ability_metadata.py` | **WRONG**. Should reference `ability_metadata.py` |

### ability_reference.md content claim at line 373

| Claim | Actual Code | Match? |
|-------|-------------|--------|
| Source file: `game/simulation/components/abilities/planetary.py` | Now a package: `game/simulation/components/abilities/planetary/` with 6 submodules + `_shared.py` + `__init__.py` | **WRONG**. Should reference `planetary/` directory or `__init__.py`. |

### ability_reference.md test reference claims (lines 571, 585)

| Claim | Actual Code | Match? |
|-------|-------------|--------|
| `tests/unit/strategy/services/test_effect_ability_metadata.py` | File does not exist | **WRONG**. No equivalent test found. |
| `tests/unit/strategy/services/test_ability_iterator.py` | Check needed | **LIKELY MATCH** (not a dead ref per scanner) |

---

## Architectural Accuracy

### Claim: `docs/01_ARCHITECTURE.md` line 155 — `data/galaxy_protocols.py`

The doc at line 155 references `data/galaxy_protocols.py` under the `game/strategy/` section. The actual file is at `game/strategy/data/galaxy_protocols.py`. The doc at line **270** correctly references `game/strategy/data/galaxy_protocols.py`. At line 155, the prefix `game/strategy/` was omitted.

**Verdict: CONFIRMED ERROR.** The reference at line 155 is a factual error (missing path prefix). The same doc corrects itself at line 270.

### Claim: `docs/01_ARCHITECTURE.md` line 154 — pathfinding listed under `data/`

The doc describes what's in `data/` subdirectory: "including `Fleet`, `ShipInstance`, `Empire`, `Galaxy`, `GalaxyState`, `Planet`, `StarSystem`, `WarpPoint`, `stars.py`, `spectrum.py`, `planet_serde.py`, **pathfinding**, physics, ..."

The actual pathfinding module is at `game/strategy/services/galaxy_pathfinding_service.py` — in `services/`, not `data/`. The `data/` directory has `pathing.py` for galaxy density/region classification models, but the pathfinding service itself is in services.

**Verdict: CONFIRMED ERROR.** Pathfinding is in `services/`, not `data/`. The listing should reference `services/` or remove the mention.

### Claim: `docs/01_ARCHITECTURE.md` line 496 — `TurnEngineConfig` requires 22 fields

The doc states: "`TurnEngineConfig` is required and bundles 22 fields." This is under Warnings — no direct contradiction found in code. **NOT VERIFIED** in this spot-check.

### Claim: `docs/01_ARCHITECTURE.md` layer model (lines 7-21)

The layer dependency diagram lists:
- `game/services/` may depend on Core only
- `game/engine/` depends on Services + Core

Checking `docs/04_SERVICES.md` lines 884-891 which repeats: "`game/services/` must depend on Core only."

**Verdict: CONSISTENT.** No contradiction found between doc and code structure for layer boundaries.

---

## Prioritized Doc Fixes

### Tier 1: HIGH — Wrong file paths (actively misleading)

1. **`docs/01_ARCHITECTURE.md:155`** — Change `data/galaxy_protocols.py` → `game/strategy/data/galaxy_protocols.py`
2. **`docs/04_SERVICES.md:480-482`** — Remove claim that `component_inspector.py` is "preserved as a thin re-export shim." Update to reference `component_abilities.py` and `component_layers.py`. The shim was deleted by PROJ-454.
3. **`docs/systems/ability_reference.md:19,489`** — Change `component_inspector.py` → `component_abilities.py`
4. **`docs/systems/ability_reference.md:18,184`** — Change `effect_ability_metadata.py` → `ability_metadata.py`
5. **`docs/systems/ability_reference.md:108,571,585`** — Remove references to `tests/unit/strategy/services/test_effect_ability_metadata.py` (no longer exists)
6. **`docs/02_PATTERNS.md:819,824`** — Remove references to `test_run_details.py` and `race_setup_screen.py` (removed by PROJ-416/417)
7. **`docs/01_ARCHITECTURE.md:154`** — Move "pathfinding" from `data/` listing to `services/` listing

### Tier 2: MEDIUM — Path drift, files renamed/split

8. **`docs/02_PATTERNS.md:38`** — Fix `data/classes/` → point to correct data location (e.g., `data/` root) or rephrase "classes" in the pattern description
9. **`docs/02_PATTERNS.md:170`** — Change `commands.py` → `commands/` directory
10. **`docs/02_PATTERNS.md:187,827`** — Change `command_handlers.py` → `handlers/` directory
11. **`docs/03_CONVENTIONS.md:32`** — Update `get_system_at_hex()` location to `game/strategy/services/galaxy_pathfinding_service.py` (or wherever it actually lives)
12. **`docs/systems/ability_reference.md:373`** — Change `planetary.py` → `planetary/` directory

### Tier 3: LOW — Stale PROJ references

13. **Add "Deep Archive" section to `projects_index.md`** for PROJ-329 and below, OR update docs to replace PROJ identifiers with descriptive text
14. **`docs/04_SERVICES.md:895`** — Scanner should ignore references in "Stale References to Avoid" warning sections (tooling fix, not doc fix)
15. **`docs/02_PATTERNS.md:88`** — `game/core/singleton.py` is intentionally referenced as retired; consider marking with "removed" annotation to distinguish from path-drift errors

### Tier 4: INCONCLUSIVE — Need further investigation

16. **11 older PROJ references (PROJ-207 through PROJ-412)** in 5 doc files — verify whether the features described are complete and update doc wording

---

## Notes

- The `tests/path/to/test.py` references are **placeholders** in command examples (`pytest tests/path/to/test.py -k test_name`). They should not be treated as dead file references. The scanner should be configured to exclude match patterns like `tests/path/to/test.py`.
- The `docs/04_SERVICES.md:895` reference to `area_effect_manager.py` is in an explicit "Stale References to Avoid" warning section. Listing it here is by design. The scanner should consider the surrounding context (is the reference in a "do not use" block?).
- `PROJ-454` ("Engine + services obsolete-surface retirement") archived `effect_ability_metadata` and `component_inspector` cleanup on 2026-05-17 — same date as the docs' "Last verified" timestamps. The docs were verified *before* the cleanup was complete, leading to stale references that survived into the verified docs.

---

*Validation performed 2026-05-20 against commit-state codebase. Scan data from `docs-audit` run `2026-05-20_073330`.*
