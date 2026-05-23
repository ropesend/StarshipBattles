# Verification Report — PROJ-468 (reference bundle)

- **Source audit:** `Reviews/results/2026-05-20_073330_docs-audit/`
- **Run date:** 2026-05-20
- **Batch summary (full run):** 40 verified / 4 rejected / 1 uncertain / ~10 out-of-scope categories.
- **This bundle:** 18 verified.

Verification was performed directly by reading live code/docs (Agent/Explore subagents unavailable in this harness), a different reader than the audit, per protocol 17's skeptical-verification requirement. Filesystem stats confirmed every dead-ref and content-error claim; the deleted/renamed files (`component_inspector.py`, `effect_ability_metadata.py`, `planetary.py`, `planet_context_menu.py`, `data/spectrum.py`, `game/research/ui/`) are all confirmed absent and replacements present.

## Verified (this bundle)

| id | doc_file | line | category | current text → recommended change | severity | mislead risk |
|----|----------|------|----------|-----------------------------------|----------|--------------|
| DEAD-04SVC-480 | docs/04_SERVICES.md | 58,480-482 | content_error | remove "thin re-export shim" claim → component_abilities.py + component_layers.py | CRITICAL | Doc claims a deleted shim still exists |
| DEAD-ABREF-ci | docs/systems/ability_reference.md | 19,489 | content_error | component_inspector.py → component_abilities.py / component_layers.py | CRITICAL | Canonical inspection path is dead; imports fail |
| DEAD-ABREF-eam | docs/systems/ability_reference.md | 18,184 | content_error | effect_ability_metadata.py → ability_metadata.py | CRITICAL | Doc references deleted file |
| DEAD-SL-eam | docs/systems/strategy_layer.md | 692 | content_error | remove "remains importable" → ability_metadata.py | CRITICAL | Doc asserts deleted file importable |
| DEAD-AB-ci | docs/guides/adding_abilities.md | 55,422,495 | content_error | component_inspector + effect_ability_metadata → current modules | CRITICAL | Example imports fail |
| DEAD-CS-ci | docs/guides/component_system.md | 23,130-133 | content_error | component_inspector + re-export claim → current modules | CRITICAL | Example imports fail |
| DEAD-QS-ci | docs/guides/qs_complex_design.md | 32 | content_error | component_inspector.py → current modules | CRITICAL | Example imports fail |
| DEAD-ABREF-plan | docs/systems/ability_reference.md | 373 | dead_ref | planetary.py → planetary/ package | MAJOR | File→package |
| DEAD-ABREF-tests | docs/systems/ability_reference.md | 108,571,585 | dead_ref | test_effect_ability_metadata.py → current tests | MAJOR | Dead test paths |
| DEAD-SL-spec | docs/systems/strategy_layer.md | 831 | dead_ref | data/spectrum.py → game/strategy/data/spectrum.py | MAJOR | Path drift |
| DEAD-FIGHT-pcm | docs/systems/fighters.md | 244 | dead_ref | planet_context_menu.py → planet_menu_items.py + fms_menu_callbacks.py | MAJOR | Split file |
| DEAD-MINE-pcm | docs/systems/minefields.md | 247,323 | dead_ref | planet_context_menu.py → split files | MAJOR | Split file |
| DEAD-RES-ui | docs/systems/research_system.md | 24 | dead_ref | clarify/remove self-contradictory game/research/ui path | MAJOR | Self-contradictory live path |
| DEAD-AB-tests | docs/guides/adding_abilities.md | 434,539 | dead_ref | test_effect_ability_metadata.py → current tests | MAJOR | Dead test paths |
| DEAD-CS-test | docs/guides/component_system.md | 347 | dead_ref | test_component_inspector.py → current tests | MAJOR | Dead test path |
| DEAD-QS-test+plan | docs/guides/qs_complex_design.md | 212,319 | dead_ref | planetary.py → planetary/; test_component_inspector.py → current tests | MAJOR | File→package + dead test |
| DEAD-TI-damage | docs/guides/testing_infrastructure.md | 170 | dead_ref | test_damage.py command → existing path/placeholder | MAJOR | Broken command example |
| G3-M3-precommit | docs/guides/pre_commit_hooks.md | — | doc_staleness | add Last verified blockquote | MAJOR | Only G3 guide lacking freshness stamp |
| MISS-superweapon | docs/systems/strategy_layer.md (host) | — | missing_docs | document superweapon_order_processor.py (506 LOC) | MAJOR | Major subsystem undocumented |
| MISS-gameinit | docs/01_ARCHITECTURE.md (host) | — | missing_docs | document game_initializer.py (446 LOC) | MAJOR | Critical bootstrap path undocumented |

(Counts as 18 distinct verified items; some span multiple lines/refs grouped under one checklist task.)

## Rejected

| id | original audit recommendation | contrary evidence | rationale |
|----|-------------------------------|-------------------|-----------|
| XDOC-compscope | Add `player_sector`/`player_system` to `docs/guides/component_system.md` AbilityScope list (cross-doc #9) | `component_system.md:101` already lists "enemy_sector, enemy_system, player_sector, player_system"; enum `game/simulation/components/abilities/base.py:53-56` confirms both exist | Already present — false positive |
| XDOC8-abmeta | Change `docs/guides/adding_abilities.md` to use exact filename `effect_ability_metadata.py` (cross-doc #8) | `effect_ability_metadata.py` is deleted; `ability_metadata.py` is canonical (filesystem + docs_accuracy_code confirm) | Cross-doc reviewer inverted the canonical filename; the real dead-ref is captured by DEAD-AB-ci instead |

(The other 2 rejections — Simulation-deps-Assets, G3-M7 inverted python version — belong to the foundation cluster; logged in PROJ-467's verification_report.md.)

## Uncertain (resolved)

None assigned to this bundle. The single UNCERTAIN (`docs/_ignore/`) was resolved to EXCLUDE under PROJ-467.

## Out of Scope

| id | why excluded |
|----|--------------|
| combat_lab-falsepos | `docs/guides/simulation_testing.md` `data/scenario_roles.json` + `data/ships/` are scanner substring artifacts of `combat_lab/data/` which exists. |
| galaxy-gen-doc | DOC-G1-07 new `galaxy_generation.md` — audit phrases as "consider"; speculative scope addition, not a confirmed gap. |
| dto-doc | DTO-layer doc (plan item #20) phrased as "assess need" — speculative. |
| ability-keycount | `ability_reference.md:3` "72 keys" possibly-stale — UNCERTAIN per audit; refresh only if the doc is touched for other reasons (timestamp-only drift). |
| systems-falsepos | combat_simulation.md / orders_system.md / production_system.md self-documented stale-reference-correction blocks (command_handlers.py, specs.py) are intentional do-not-use warnings, not live refs. |
