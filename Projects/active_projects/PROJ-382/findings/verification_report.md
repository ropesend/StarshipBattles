# PROJ-382 Verification Report

> **Source:** `Reviews/results/2026-05-07_220452_pattern-audit/`
> **Re-verification run date:** 2026-05-08
> **Method:** Phase C of Protocol 18 — three parallel `Explore` agents reading both `docs/02_PATTERNS.md` and the cited code at every `file:line`.

## Summary

Out of ~49 audit candidates entering re-verification:

| Bucket          | Count |
|-----------------|-------|
| **VERIFIED**    |  21   |
| **UNCERTAIN**   |   6   |
| **REJECTED**    |  13   |
| **OUT_OF_SCOPE**|   1 (VER-001/PAT-02-001 already DISPUTED in audit's own verifier) |
| LOC ceiling (subset of audit's 14): 5 in scope, 9 already in active PROJs (deferred) |

User decisions during Phase D included U4, U5, U6 from the UNCERTAIN list and deferred U1, U2, U3.

---

## Verified

| ID | Severity | File:line | Pattern | Current state | Recommended state | Phase |
|----|----------|-----------|---------|---------------|-------------------|-------|
| VER-002 | CRITICAL | `game/ui/screens/build_queue_screen.py:425-429, 462-466, 498-501` | #5 | `if facade: facade.handle_command else: session.handle_command` | unconditional `facade.handle_command` | 1 |
| VER-002 | CRITICAL | `game/ui/screens/empire_build_queue_window.py:422-426` | #5 | same dual-dispatch | unconditional facade | 1 |
| VER-003 | CRITICAL | `game/ui/screens/strategy_screen.py:78-83, 86, 155-182` | #5 | public `self.session` propagated to children | `self._session` private; children take only facade | 1 |
| VER-003 | CRITICAL | `game/ui/screens/strategy_build_queue_manager.py:98` | #5 | `session=self._screen.session` kwarg | drop kwarg | 1 |
| VER-003 | CRITICAL | `game/ui/screens/strategy_windows/build_queue_windows.py:73-74` | #5 | `session=c.scene.session` kwarg | drop kwarg | 1 |
| PAT-03-001 | MAJOR | `game/strategy/data/galaxy_spatial_index.py:37` | #2 | `isinstance(obj, Planet)` | `is_planet(obj)` TypeGuard | 2 |
| Cross-shard | MAJOR | `game/strategy/data/empire.py:107-127` | #10 | `if event_bus else log_event` fallback | injected EventBus only | 2 |
| Cross-shard | MAJOR | `game/strategy/data/fleet.py:408-427, 437-454` | #10 | two dual-path emission blocks | injected EventBus only | 2 |
| Cross-shard | MAJOR | `game/simulation/entities/projectile.py:97, 116` | #10 | module-level `log_event` import | injected EventBus | 2 |
| PAT-02-002 | MAJOR | `game/ui/screens/design_selector_window.py:45` | #31 | `class DesignSelectorWindow(UIWindow)` | `(StrategyModalWindow)` | 2 |
| PAT-02-003 | MAJOR | `game/ui/screens/builder/stat_getters.py:288-301` | conv §6.5 | hardcoded `_SUPERWEAPON_ABILITIES` list | iterate `SUPERWEAPONS` registry | 2 |
| PAT-02-004 | MAJOR | `game/simulation/components/__init__.py` | conv | empty file | re-exports or namespace marker comment | 2 |
| U4 (PAT-01-NAME-001) | MAJOR | `game/ui/screens/builder/event_bus.py:12` | #10 | class `EventBus` (collides with core variant) | `WorkshopEventBus` | 2 |
| Cross-shard | MINOR | `game/strategy/engine/game_session.py:343-355` | #6 | tautology guard on `command.type` | unconditional dispatch | 3 |
| PAT-01-CMD-001 | MINOR | `game/strategy/engine/superweapon_command_handlers.py:15` | #7 | imports `BaseCommandHandler` from re-export shim | import from `handlers/base.py` | 3 |
| PAT-02-006 | MINOR | `game/strategy/systems/race_library.py:14` | #12 | bare `import json` + `json.dump/loads` | `json_utils.save_json/load_json` | 3 |
| PAT-02-007 | MINOR | `game/ui/screens/builder/detail_panel.py:11` | #12 | bare `import json` + `json.dumps` | `json_utils` | 3 |
| PAT-03-002 | MINOR | `game/strategy/data/galaxy_warp_generator.py:366-369` | #12 | inline `json.load(f)` | `load_json(...)` | 3 |
| PAT-03-003 | MINOR | `game/ui/screens/setup_data_io.py:15` | #12 | unused `import json` | delete | 3 |
| U5 (PAT-01-DI-001) | MINOR | `game/strategy/engine/production_spawner.py:36, 51-57` | #3 | `Optional[GameRegistries] = None` + lazy mutator | required `registries`; eager mutator | 3 |
| Doc-drift | MINOR | `docs/02_PATTERNS.md` Pattern #23 | #23 | doc lists 5 phases | update to 6 phases incl. `BoundaryEnforcementPhase(250)` + `Phase` suffix | 3 |
| Doc-drift | MINOR | `docs/02_PATTERNS.md` Pattern #7 | #7 | canonical path = `command_handlers.py` shim | update to `handlers/base.py` | 3 |
| PAT-01-UNDOC-002 | STRATEGIC | `docs/02_PATTERNS.md` (new entry) | new | Re-Export Shim used in 4 sites, no doc | new pattern entry post-#35 | 4 |
| U6 (PAT-01-CFG-001) | STRATEGIC | `docs/02_PATTERNS.md` Pattern #12 | #12 | Strategy Config Singleton accessor variant undocumented | add subsection | 4 |
| LOC | MINOR | `game/simulation/components/abilities/planetary.py` (913) | n/a | over 500 LOC | split into `planetary/` package | 5 |
| LOC | MINOR | `game/simulation/systems/battle_engine.py` (775) | n/a | over 500 LOC | extract `BattleLogger` + boundary | 5 |
| LOC | MINOR | `game/strategy/services/fleet_navigation_service.py` (773) | n/a | over 500 LOC | extract cohesive helpers | 5 |
| LOC | MINOR | `game/strategy/engine/superweapon_order_processor.py` (723) | n/a | over 500 LOC | extract per-superweapon closures | 5 |
| LOC | MINOR | `game/strategy/engine/conflict_resolution_engine.py` (567) | n/a | over 500 LOC | one cohesive helper extraction | 5 |

## Rejected

| ID | Original audit recommendation | Contrary evidence | Rationale |
|----|-------------------------------|-------------------|-----------|
| VER-001 / PAT-02-001 | Inject `GameRegistries` into `GameSession` instead of `get_default_registry_provider()` | Pattern #3 doc explicitly limits restriction to simulation: "Simulation code must not call `get_default_registry_provider()`. Leaf factory access may use it outside simulation." `GameSession` is strategy-layer. | Audit's own verifier marked DISPUTED — already excluded. |
| Pattern #3 keyword-only signature wording | Doc-side fix for `Ship(..., *, registries: GameRegistries)` | `game/simulation/entities/ship.py:53-55` actually uses `*, registries: GameRegistries` (keyword-only). Doc matches code. | Audit reviewer misread the signature. |
| Pattern #29 adapter-count clarification | Update to "7 adapters + 1 helper function" | Issue is documentation-clarity only, not a code/doc-divergence violation. | Immaterial. |
| PAT-01-UNDOC-001 (Two-Stage UIWindow Construction) | Promote to documented production pattern | `docs/02_PATTERNS.md` Pattern #33 §"Two-stage UIWindow shape" already documents this for production. | Audit reviewer missed the existing coverage. |
| PAT-01-PROTO-001 (`isinstance` on `WeaponAbility`/`SeekerWeaponAbility`) | Replace with `getattr/hasattr` duck-typing | Both classes are intra-simulation; Pattern #2 targets cross-layer protocol bypass, not internal class hierarchies sharing an Ability ABC. | Intra-layer; out of Pattern #2 scope. |
| PAT-01-PROTO-002 (`isinstance(boundary, UnboundedRegion)`) | Add `has_edge()` method to BoundaryRegion | Same — intra-simulation use of an internal ABC. | Intra-layer. |
| PAT-01-CFG-002 (`PlayerConfig`/`GameConfig` `@dataclass`) | None (audit's own recommendation) | Audit text: "No action — strategy-layer dataclass configs are compatible with Pattern #12's spirit." | Already self-rejected by audit. |
| PAT-01-CFG-003 (raw `json` in `system_blueprints_loader.py`) | None | Audit's own follow-up: "raw `json` import is for `JSONDecodeError` exception type only — legitimate." | Already self-rejected. |
| PAT-01-CFG-004 (economy_config explanatory note) | Already-documented intentional deviation | Comment in code already justifies the choice. | Already documented. |
| PAT-01-CQRS-001 (BattleSetupState imports Fleet/ShipInstance) | Document as intentional CQRS-lite exception | The recommendation is purely architectural-doc work and the audit itself flags this as a known gray area for an interactive editor screen. Out-of-scope here unless a doc-add is wanted later. | Doc-only with no clear doc target. |
| PAT-01-MODAL-001 (legacy slot scanning in `StrategyEventRouter`) | None | Audit text: "No action needed — appropriate for backward-compat." | Already self-rejected. |
| MIN-01 (`StrategyWidgets` `Any = None`) | None (typing nit) | Audit verifier: "Not a Pattern #12 violation." | Already self-rejected. |
| PAT-02-008 (`exit_dialog.py` global rect state) | Convert to class | Module-level globals are UI-scoped click-detection state, not the cross-module mutable globals Pattern #1 / #12 target. Acceptable. | Out of Pattern #1 scope. |
| PAT-02-009 (`ShipInstance` legacy registry fallback) | Remove when legacy save support is dropped | Already documented as `# Intentional broad catch` legacy fallback path; primary path uses `_registries` DI. | Documented; not a current violation. |

## Uncertain (resolved)

| ID | Question raised | User decision (Phase D) |
|----|-----------------|-------------------------|
| U1 (UI command DTO imports, ~127 sites) | Pattern #5 doesn't strictly forbid type-only DTO imports — fix would route via facade dispatch_* helpers; large refactor. | **Defer** to a future dedicated PROJ. |
| U2 (UI service imports, 40 sites) | Read-side facade bypass; fix is large (extend facade DTOs). | **Defer.** |
| U3 (UI systems imports, 26 sites) | Mixed — DesignLibrary/SaveGameService/RaceLibrary cases differ. RaceRandomizer in race_setup is intentional. | **Defer.** |
| U4 (EventBus naming collision) | Pattern #10 already documents both classes as intentional, but rename would remove import-ambiguity surface. | **Include** — Phase 2 Task 2.7. |
| U5 (`ProductionSpawner` Optional registries) | Pattern #3 is simulation-scoped; strategy-layer Optional DI is permitted but stylistically deviates. | **Include** — Phase 3 Task 3.5. |
| U6 (Strategy Config Singleton accessor) | Only 1 confirmed use (economy_config); below 3+ undocumented-pattern bar. | **Include** as doc-add — Phase 4 Task 4.2. The variant has explicit in-code justification. |

## Out of Scope

| ID | Reason |
|----|--------|
| VER-001 / PAT-02-001 | Marked DISPUTED in audit's own `findings/verification.md`; Pattern #3 simulation-scoped. |
| Pattern #30 (Registrar Close-Callback) usages | Documented as superseded by #31; audit explicitly excludes. |
| TYPE_CHECKING-only layer imports | Benign by convention; audit's own scanner explicitly excludes them. |
| 9 LOC ceiling files already in active PROJ | Avoid duplicate work — race_summary_panel (active), battle_screen (active), ship_detail_panel (PROJ-315), production_engine (PROJ-367), workshop_event_router (PROJ-360), build_queue_panel_factory (active), battle_panels (active), registry (PROJ-309), spec_compiler (PROJ-269 archived). |
