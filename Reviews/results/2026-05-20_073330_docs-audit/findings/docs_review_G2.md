# Documentation Review: Systems Docs (G2)
## Summary
- Group: Systems Docs (G2)
- Docs in Scope: 12
- Docs Actually Read: 12
- Total Findings: 15
- Critical: 2 | Major: 5 | Minor: 8

## Dead Reference Findings
#### CRITICAL: `component_inspector.py` no longer exists — core ability-inspection utility referenced across ability_reference.md
**ID:** DOC-G2-001
**Location:** `docs/systems/ability_reference.md:19,489`
**Reference:** `game/strategy/services/component_inspector.py`
**Issue:** File was split/renamed into `game/strategy/services/component_abilities.py` + `game/strategy/services/component_layers.py`. The doc at line 19 says "Design/facility ability inspection must use `game/strategy/services/component_inspector.py`" and at line 489 lists it as the canonical "Ability Inspection And Registry Lookup" file. The dead reference is also catalogued in `docs/04_SERVICES.md:480` where it's described as preserved "as a thin re-export shim" — but that shim is also gone.
**Recommendation:** Update both references to point at `component_abilities.py` and `component_layers.py`, and verify that all function signatures listed at lines 493-502 of ability_reference.md (e.g. `get_component_abilities`, `extract_abilities_from_component`, `iterate_design_components`, etc.) exist in the replacement modules.

#### CRITICAL: `effect_ability_metadata.py` deleted — doc explicitly claims it "remains importable"
**ID:** DOC-G2-002
**Location:** `docs/systems/ability_reference.md:184` and `docs/systems/strategy_layer.md:692`
**Reference:** `game/strategy/services/effect_ability_metadata.py`
**Issue:** ability_reference.md line 184 says "File: `game/strategy/services/effect_ability_metadata.py`" and references `EFFECT_ABILITY_METADATA`, `collect_system_effects`, etc. Strategy_layer.md line 692 explicitly states: "Shim: `game/strategy/services/effect_ability_metadata.py` **remains importable**. It re-derives `EFFECT_ABILITY_METADATA` from the unified registry's `EffectFacet` entries...". However the file does not exist — it was replaced by `game/strategy/services/ability_metadata.py`. The `_RATE_ABILITIES` and collector-local hardcoded lists that the doc warns against are indeed gone, but so is the shim that supposedly preserves backward compat.
**Recommendation:** Remove or update all references to `effect_ability_metadata.py`. The replacement is `ability_metadata.py`. Verify that `EFFECT_ABILITY_METADATA` is still accessible (or update consumers).

#### MAJOR: `planetary.py` dead reference — file split into `planetary/` package
**ID:** DOC-G2-003
**Location:** `docs/systems/ability_reference.md:373`
**Reference:** `game/simulation/components/abilities/planetary.py`
**Issue:** The file was refactored into a package directory at `game/simulation/components/abilities/planetary/` (containing `__init__.py`, `resource_modifiers.py`, `stat_modifiers.py`, etc.). The doc says "Source: `game/simulation/components/abilities/planetary.py`" in the Planetary And Strategic Abilities section.
**Recommendation:** Update to `game/simulation/components/abilities/planetary/`.

#### MAJOR: `planet_context_menu.py` dead reference — renamed/split
**ID:** DOC-G2-004
**Location:** `docs/systems/fighters.md:244` and `docs/systems/minefields.md:247,323`
**Reference:** `game/ui/screens/planet_context_menu.py`
**Issue:** File does not exist. The planet right-click menu functionality was split into `game/ui/screens/planet_menu_items.py` + `game/ui/screens/fms_menu_callbacks.py`. Both fighters.md and minefields.md reference the old path for planet-issued launch/lay/recover menus.
**Recommendation:** Update references to `planet_menu_items.py` and `fms_menu_callbacks.py`.

#### MAJOR: `data/spectrum.py` dead reference — moved to strategy layer
**ID:** DOC-G2-005
**Location:** `docs/systems/strategy_layer.md:831`
**Reference:** `data/spectrum.py`
**Issue:** File was moved to `game/strategy/data/spectrum.py`. The doc lists spectrum-related files as `data/spectrum.py` alongside `generation/star_generator.py` and `game/core/spectrum_math.py`.
**Recommendation:** Update to `game/strategy/data/spectrum.py`.

#### MAJOR: `game/research/ui/` dead reference — moved to UI layer
**ID:** DOC-G2-006
**Location:** `docs/systems/research_system.md:24`
**Reference:** `game/research/ui/`
**Issue:** File was moved to `game/ui/research/`. The doc itself notes this at line 24: "Do not recreate the old `game/research/ui/` path. It was moved to `game/ui/research/` to remove a layer violation." However, listing it as a current file reference at line 24 without qualifying it as historical is confusing. The reference is documented as stale in-text but still appears as a file-path reference.
**Recommendation:** Clarify that the line 24 reference is historical/corrective context, not a live path. Or remove it entirely since it's self-contradictory (warns not to use a path that's already gone).

#### MINOR: `tests/unit/strategy/services/test_effect_ability_metadata.py` — test file removed
**ID:** DOC-G2-007
**Location:** `docs/systems/ability_reference.md:108,571,585`
**Reference:** `tests/unit/strategy/services/test_effect_ability_metadata.py`
**Issue:** Referenced 3 times as a validation/test area for stacking and effect metadata. File no longer exists; tests moved under `tests/unit/strategy/services/test_ability_metadata_contracts.py` or similar.
**Recommendation:** Update test paths to current coverage files.

#### MINOR: Multiple stale test references in combat_simulation.md — already self-documented
**ID:** DOC-G2-008
**Location:** `docs/systems/combat_simulation.md:546-548`
**References:** `tests/unit/simulation/test_unified_entry_guard.py`, `tests/unit/simulation/replay/test_replay_serialization.py`, `tests/unit/strategy/test_replay_resolver.py`, `tests/unit/strategy/test_replay_store.py`
**Issue:** The doc itself lists these as "Stale reference corrections" with corrected paths. However, they appear in an active test-listing section (lines 501-542), not in a clearly marked "corrections" appendix. An agent scrolling through the test list might not read the corrections block at line 544.
**Recommendation:** Remove stale entries from the main test listing; keep only the corrected paths.

#### MINOR: Placeholder `tests/path/to/test.py` in combat_simulation.md
**ID:** DOC-G2-009
**Location:** `docs/systems/combat_simulation.md:556`
**Reference:** `tests/path/to/test.py`
**Issue:** Placeholder pattern used in test commands section. Harmless but flagged by deterministic scan.
**Recommendation:** Replace with actual focused test commands as done in other docs (e.g. ability_reference.md uses real paths).

#### MINOR: `game/strategy/engine/commands/specs.py` and `command_handlers.py` in orders_system.md
**ID:** DOC-G2-010
**Location:** `docs/systems/orders_system.md:137,420,422`
**References:** `game/strategy/engine/commands/specs.py`, `game/strategy/engine/command_handlers.py`
**Issue:** Both properly documented as deleted in PROJ-383; the doc uses them in stale-reference-correction context. Not truly stale — they're cited as examples of what NOT to use.
**Recommendation:** Consider moving these to a dedicated "Stale References" block rather than inline mentions, to avoid false positives in future scans.

#### MINOR: `game/strategy/engine/command_handlers.py` in production_system.md
**ID:** DOC-G2-011
**Location:** `docs/systems/production_system.md:392`
**Reference:** `game/strategy/engine/command_handlers.py`
**Issue:** Doc itself says: "The old broad reference to `game/strategy/engine/command_handlers.py` is stale for construction queue work; that shim was deleted in PROJ-383." Self-documented stale reference. Same as DOC-G2-010 — not truly a finding but triggers the scan.
**Recommendation:** Remove the inline stale-reference mention; the doc already points to the correct file (`game/strategy/engine/handlers/construction_queue.py`).

## Stale PROJ Reference Findings
#### MINOR: Multiple PROJs with "unknown" status referenced as completed work
**ID:** DOC-G2-012
**Location:** Multiple docs
**Issue:** Several PROJ references in G2 docs carry `"unknown"` status in the project tracker but describe completed architectural work:
- `PROJ-383` (orders_system.md:137,422; production_system.md:393; strategy_layer.md:109) — described as the command_handlers.py deletion; work appears complete.
- `PROJ-396` (strategy_layer.md:101) — described as fixing CRIT-002 service-wiring drift; work appears complete.
- `PROJ-411` (strategy_layer.md:166) — described as migration of filter snapshots; work appears complete.
- `PROJ-412` (strategy_layer.md:281,1054,1058) — described as progress callback cadence change; work appears complete.
- `PROJ-269` (strategy_layer.md:367) — described as post-battle hook pruning; work appears complete.
- `PROJ-219`, `PROJ-207`, `PROJ-222` (strategy_layer.md:105) — described as wiring steps in rehydrate parity; work appears complete.

These are not stale per se (the docs describe completed work accurately), but the project tracker's "unknown" status is a metadata hygiene concern.
**Recommendation:** Update project tracker status for these PROJs. No doc changes needed for these.

## Content Accuracy Findings
#### MAJOR: `ability_reference.md` claims `effect_ability_metadata.py` shim is still importable
**ID:** DOC-G2-013
**Location:** `docs/systems/ability_reference.md:184`, `docs/systems/strategy_layer.md:692`
**Issue:** Strategy_layer.md:692 states the file "remains importable" and "preserves... symbols so existing consumer chains continue to work unchanged." But the file does not exist. Any code trying to import from `game.strategy.services.effect_ability_metadata` will get an `ImportError`. The doc's claim is materially wrong.
**Recommendation:** Either restore the shim file (if backward compat is needed) or delete the claim that it remains importable and document that consumers must migrate to `ability_metadata.py`.

#### MINOR: `ability_reference.md` registry key count may be stale
**ID:** DOC-G2-014
**Location:** `docs/systems/ability_reference.md:3`
**Issue:** The `Last verified` line says "Current live registry has 72 keys" but this was last verified on 2026-05-17. This could have drifted since.
**Recommendation:** Re-verify the count if this doc is updated for other reasons.

## Code Example Issues
#### MINOR: `ability_reference.md` function signatures reference nonexistent file
**ID:** DOC-G2-015
**Location:** `docs/systems/ability_reference.md:489-502`
**Issue:** The "Ability Inspection And Registry Lookup" section lists functions like `get_component_abilities`, `extract_abilities_from_component`, `iterate_design_components`, etc. and directs readers to use `game/strategy/services/component_inspector.py`. Since that file doesn't exist, agents cannot verify these function signatures or import paths.
**Recommendation:** Verify these functions exist in the replacement modules (`component_abilities.py`, `component_layers.py`) and update the file reference.

## Missing Documentation
No major undocumented subsystems identified within G2 scope. The undocumented_modules.json lists 229 modules, but nearly all are UI implementation files, DTOs, sub-package internals, or modules whose functionality is already covered by existing systems docs. None represent a gap where a whole-subsystem doc file is missing from the G2 set.

Notable sub-modules that might benefit from cross-references in existing docs:
- `game/simulation/components/abilities/planetary/resource_modifiers.py` (160 LOC) — covered by ability_reference.md but not explicitly cited
- `game/simulation/components/abilities/planetary/stat_modifiers.py` (233 LOC) — same
- `game/strategy/engine/superweapon_order_processor.py` (506 LOC, exceeds 500 LOC ceiling) — superweapon system covered in strategy_layer.md and orders_system.md

## Doc File Coverage Verification
| Doc File | Status | Findings |
|----------|--------|----------|
| `docs/systems/ability_reference.md` | Active (verified 2026-05-17) | DOC-G2-001,002,003,007,013,014,015 |
| `docs/systems/ai_system.md` | Active (verified 2026-05-08) | None |
| `docs/systems/combat_simulation.md` | Active (verified 2026-05-08) | DOC-G2-008,009 |
| `docs/systems/fighters.md` | Active (verified 2026-05-17) | DOC-G2-004 |
| `docs/systems/minefields.md` | Active (verified 2026-05-17) | DOC-G2-004 |
| `docs/systems/orders_system.md` | Active (verified 2026-05-07) | DOC-G2-010,012 |
| `docs/systems/production_system.md` | Active (verified 2026-05-18) | DOC-G2-011,012 |
| `docs/systems/research_system.md` | Active (verified 2026-05-08) | DOC-G2-006 |
| `docs/systems/resource_system.md` | Active (verified 2026-05-18) | None |
| `docs/systems/satellites.md` | Active (verified 2026-05-18) | None |
| `docs/systems/save_load.md` | Active (verified 2026-05-08) | None |
| `docs/systems/strategy_layer.md` | Active (verified 2026-05-18) | DOC-G2-002,005,012,013 |

## Notes
- All 12 G2 docs have `Last verified` lines (between 2026-05-07 and 2026-05-18). None are stale by the 120-day threshold.
- 11 of 12 use `**Last verified:**` (bold) format that the deterministic scanner could not parse. Only `orders_system.md` uses plain format (`Last verified:`), which the scanner detected.
- The `minefields.md` doc is more recent (verified 2026-05-17) but has a `Last verified` line that uses multiline formatting — the scanner may be confused by line-breaks in the verified-date block.
- `ability_reference.md` and `strategy_layer.md` share the most cross-cutting stale references, largely due to the `component_inspector.py` and `effect_ability_metadata.py` refactors.
