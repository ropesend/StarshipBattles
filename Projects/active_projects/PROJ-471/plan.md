# PROJ-471: State hygiene — singleton-divergence consolidation + collection/RNG hygiene (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-471` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-471 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical + class-shared-state (state-corruption gate) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major (singleton-divergence + collection + RNG hygiene) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Minor (stale-bridge / dead-code / test-seam cleanup) | Partial (3.4 done; 3.1 dropped; 3.2/3.3 not done) | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Codex-audit remediation | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-21
**Active Phase:** Phase 2/3 tail (partial) — core determinism + seam work complete + Codex-audit Phase 4 complete
**Last Action:** Implemented Phase 1 Task 1.2 (`ShipCombatEngine` → per-battle `CombatSubsystems` bundle, determinism preserved); Phase 2 Tasks 2.1, 2.2, 2.8, 2.9, 2.10; Phase 3 Task 3.4. Ran one-round Codex audit → 4 findings, ALL verified, ALL remediated in new Phase 4 (4.1–4.4). Full sharded suite green (23532 passed / 0 failed). combat_lab 168 passed / 2 PRE-EXISTING failures (`TOHIT-ATK-FLEET-003/004`, unrelated). PROJ-473 populated with the deferred rng-threading scope.
**Next Action (remaining, NOT done this session):** Phase 2 Task 2.3 (`_default_manager` dual-pattern doc decision), 2.4/2.5/2.6/2.7 (UI consumer migrations — bulky, low determinism risk), 2.13 (`exit_dialog` rects — lowest-priority "drop first"); Phase 3 Tasks 3.2 (`_default_profiler` design-cleanup eval), 3.3 (`_default_llm_provider` bridge removal, gated on 2.7).
**Blockers:** None

## Overview
Created from the state-management audit at `Reviews/results/2026-05-20_082533_state-audit/` after an independent skeptical re-verification (a third pass with a different reader than OpenCode's Phase-1 reviewers and its internal verifier). 19 findings survived verification and are bundled here. Coverage spans the ApplicationContext-vs-module-default singleton-divergence family (8 singletons), three stale/dead bridge singletons, six module-mutable / class-shared-state / global-keyword collection findings, and two `random.seed()` global-pollution sites. **Includes 1 CRITICAL singleton-divergence item (`_default_provider`, 68+ consumers, no setter, no ctx binding — consumers can silently see a divergent `RegistryManager`) and 1 MAJOR class-shared-state bug (`ShipCombatEngine` subsystems shared across all ship instances).** Phase 1 must close those two before any tail cleanup. The shared root cause across the singleton family is `ApplicationContext.create_production()` acting as a bridge hub (`game/context.py:162-190`); keeping the work in one project avoids re-deriving that bridge mechanic per finding.

## Goals
> **SCOPE REVISED 2026-05-20** (dual independent + Codex review; see decisions.md). Removed items struck through below.
- **Phase 1 (Critical):** ~~Add `ctx.registry_provider` wiring + setter for `_default_provider`~~ (DROPPED — verified false positive; `DefaultRegistryProvider` re-resolves the manager per call and never caches one). Convert `ShipCombatEngine` shared subsystems to per-instance via a per-battle `CombatSubsystems` bundle owned by `BattleEngine`, with a shared-state regression test that proves cross-battle/cross-instance leakage is gone AND a determinism characterization test proving combat behavior is unchanged.
- **Phase 2 (Major):** Add missing setters for `_default_cache_manager` / `_default_policy_manager` and wire through `create_production()`; resolve the `_default_manager` dual pattern in Core; migrate UI consumers of `_default_ship_theme_manager` (15), `_default_asset_manager` (7), `_default_sprite_manager` (2), `_default_llm_provider` (1) toward `ctx.X`; add test-isolation seams for `_next_fleet_id`, `_SERIALIZABLE_REGISTRY`, `_catalog`; ~~remove the two global `random.seed()` calls~~ (DEFERRED to PROJ-473 — global seed is load-bearing for galaxy generation until rng is threaded); encapsulate `exit_dialog` module-level rect globals.
- **Phase 3 (Minor):** ~~Remove the two truly-dead bridge singletons (`_default_game_settings`, `_default_image_provider`)~~ (DROPPED — both still tested/injectable and part of the application-context contract); evaluate/remove the `_default_profiler` bridge (design cleanup — verify `profile_action`/`profile_block` fallback first, NOT blind deletion); remove `_default_llm_provider` bridge if its sole consumer was migrated; add `reset_crew_priority_registry()` test seam.

## Scope
**In:** The 8 singleton-divergence singletons (`_default_provider`, `_default_cache_manager`, `_default_policy_manager`, `_default_manager`, `_default_ship_theme_manager`, `_default_asset_manager`, `_default_sprite_manager`, `_default_llm_provider`); 3 stale/dead bridge singletons (`_default_game_settings`, `_default_image_provider`, `_default_profiler` bridge); 6 collection/class-state/global findings (`ShipCombatEngine` class-level subsystems, `_next_fleet_id`, `_SERIALIZABLE_REGISTRY`, `_catalog`, `exit_dialog` rects, `CREW_PRIORITY_REGISTRY`); 2 `random.seed()` sites.
**Out:** Items the audit and this verification ruled non-issues — `_default_sink`, `_default_ship_materializer`, `_default_planet_habitability_service` (simulation-layer / extension-slot conventions); `ST-01-003` ability_iterator provider lists (Registry pattern); `ST-01-004` session-injected fleet lookups; `ST-02-003` density_map unseeded instance RNG (Pattern #18-compliant; docstring-accuracy issue only, not a state bug); lazy font/portrait/galaxy caches; class-mutable-defaults (0 findings). See `findings/verification_report.md` for the full REJECTED/OUT_OF_SCOPE tables.

## Key Files
| File | Findings |
|------|----------|
| `game/core/registry.py` | ~~`_default_provider` (CRITICAL — DROPPED, false positive)~~, `_default_manager` (MAJOR) |
| `game/context.py` | bridge wiring for all singleton-divergence items |
| `game/simulation/entities/ship_combat_engine.py` | class-shared subsystems (MAJOR) |
| `game/simulation/systems/battle_setup.py` | global `_damage_calculator` overwrite (MAJOR; manifest path corrected from `entities/`) |
| `game/simulation/components/component_loader.py` | `_default_cache_manager` (MAJOR) |
| `game/ai/policy_manager.py` | `_default_policy_manager` (MAJOR) |
| `game/ui/assets/ship_theme_manager.py` | `_default_ship_theme_manager` (MAJOR, 15 consumers) |
| `game/assets/asset_manager.py` | `_default_asset_manager` (MAJOR, 7 consumers) |
| `game/ui/renderer/sprites.py` | `_default_sprite_manager` (MAJOR, lazy-init fallback) |
| `game/core/json_utils.py` | `_SERIALIZABLE_REGISTRY` (MAJOR) |
| `game/ui/screens/transfer_mass_preview.py` | `_catalog` (MAJOR) |
| `game/ui/screens/battle_setup_state.py` | `_next_fleet_id` (MAJOR) |
| `game/exit_dialog.py` | rect globals (MAJOR) |
| ~~`game/strategy/engine/game_initializer.py`~~ | ~~`random.seed()` (MAJOR — DEFERRED to PROJ-473)~~ |
| ~~`game/ui/screens/galaxy_test/galaxy_mode.py`~~ | ~~`random.seed()` (MAJOR — DEFERRED to PROJ-473)~~ |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Independent re-verification (Verified / Rejected / Out-of-scope)
- [findings/source_audit.md](findings/source_audit.md) - Pointer to the source state-audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) - Bundling rationale + Codex consult record

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
