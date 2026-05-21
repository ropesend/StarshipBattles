# Verification Report — PROJ-471

- **Source audit:** `Reviews/results/2026-05-20_082533_state-audit/`
- **Run date:** 2026-05-20
- **Verifier:** Independent third pass (Claude, reading live code directly — Agent-tool parallel Explore not available, so re-verification done inline per the autonomous-override contract, a different reader than OpenCode's Phase-1 reviewers and its `findings/verification.md`).
- **Batch summary:** 19 verified / 0 rejected / 0 uncertain / 8 out-of-scope, out of ~27 candidate items considered.

> Note on the zero-rejected result: the protocol flags a downstream pass that rejects nothing as suspicious rather than reassuring. Here it reflects that the audit's own verifier had already downgraded the one over-rated item (`exit_dialog` CRITICAL→MAJOR) and disputed none; the candidates that did not survive were filtered as OUT_OF_SCOPE (intentional infrastructure / Pattern-#18-compliant), not rejected as false positives. One audit *claim* was materially corrected without rejecting the item: `_default_profiler` is not dead (see Out of Scope notes / decisions.md Task 3.2).

## Verified

| ID | File | Symbol | Current pattern | Recommended pattern | Severity | Risk |
|----|------|--------|-----------------|---------------------|----------|------|
| XSHARD-CRIT | `game/core/registry.py:466` | `_default_provider` | module-level singleton auto-created in getter; no setter; no ctx binding; 68+ consumers | add `ctx.registry_provider` + `set_default_registry_provider()` wired in `create_production()`, or enforce DI | CRITICAL | consumer accessing before `create_production()` gets provider over a divergent `RegistryManager`; silent divergence |
| ST-04-002 | `game/simulation/components/component_loader.py:37` | `_default_cache_manager` | no setter; raw attr-assign at `context.py:188`; `reset_component_caches()` reassigns bypassing ctx | add setter; wire in `create_production()`; route reset through it | MAJOR | `reset_component_caches()` creates permanent divergence from `ctx.component_cache` |
| ST-04-003 | `game/ai/policy_manager.py:23` | `_default_policy_manager` | no setter; raw attr-assign at `context.py:190`; auto-creates in getter | add setter; wire in `create_production()` | MAJOR | access before `create_production()` forks a divergent PolicyManager |
| XSHARD-MGR | `game/core/registry.py:284` | `_default_manager` (RegistryManager) | dual pattern: 8 module-level convenience wrappers + 2 ctx; auto-create window | route wrappers through `ctx.registry_manager` when available, or document bridge | MAJOR | auto-create divergence window between module-level and `ctx.registry_manager` |
| XSHARD-THEME | `game/ui/assets/ship_theme_manager.py:54` | `_default_ship_theme_manager` | ctx-wired bridge; 15 production consumers all module-level | migrate consumers to `ctx.ship_theme_manager` | MAJOR | bridge-only sync; divergence if ctx set without setter |
| XSHARD-ASSET | `game/assets/asset_manager.py:14` | `_default_asset_manager` | ctx-wired bridge; 7 consumers module-level | migrate consumers to `ctx.asset_manager` | MAJOR | bridge-only sync divergence |
| XSHARD-SPRITE | `game/ui/renderer/sprites.py:14` | `_default_sprite_manager` | ctx-wired; 2 consumers (one in `app_bootstrap.py:265` with ctx in scope); lazy-init fallback (ST-01-005) | migrate consumers; replace lazy-init fallback with sentinel | MAJOR | lazy-init fallback diverges if called before `create_production()` |
| XSHARD-LLM | `game/services/llm/defaults.py:17` | `_default_llm_provider` | ctx-wired; 1 consumer `panel_factory.py:167` | migrate consumer to `ctx.llm_provider`; then remove bridge | MAJOR | bridge-only sync divergence |
| ST-02-001 | `game/simulation/entities/ship_combat_engine.py:41-43` | `ShipCombatEngine._targeting_system/_damage_calculator/_weapon_firing_system` | class-level `Optional[X]=None` shared across all instances; lazily populated; `battle_setup.py:49` overwrites cross-module | thread subsystems via constructor injection (per-instance) | MAJOR | shared subsystems leak across battles/tests; test-isolation bug |
| ST-01-002 | `game/ui/screens/battle_setup_state.py:24` | `_next_fleet_id` | module-level int counter via `global`; no reset | move to `BattleSetupState` instance attribute | MAJOR | unbounded growth; no test-isolation reset |
| ST-04-004 | `game/core/json_utils.py:53` | `_SERIALIZABLE_REGISTRY` | module-level dict mutated by `@register_serializable`; copy-on-read; no reset | add `clear_serializable_registry()` seam | MAJOR | no test-isolation reset (copy-on-read limits practical risk) |
| ST-04-005 | `game/ui/screens/transfer_mass_preview.py:186` | `_catalog` | module-level lazy cache; no invalidation; docstring warns `set_resource_catalog` ignored | add `_clear_catalog()` hook or share container cache | MAJOR | stale catalog in tests |
| ST-01-001 | `game/exit_dialog.py:11-12` | `_exit_yes_rect`/`_exit_no_rect` | module-level rects reassigned every frame via `global`; read by click handlers | encapsulate in dialog-state class | MAJOR (downgraded from CRITICAL) | implicit coupling via globals; maintainability (no corruption per verifier) |
| ST-02-002 | `game/simulation/entities/stat_contributors/registry.py:84-111` | `CREW_PRIORITY_REGISTRY` | module-level list mutated by register/unregister; no reset (unlike sibling registry) | add `reset_crew_priority_registry()`; call in conftest | MINOR | latent test-isolation leak |
| ST-04-010 | `game/strategy/engine/game_initializer.py:250` | `random.seed(galaxy_seed)` | global seed alongside per-instance `random.Random(galaxy_seed)` (line 248) | delete line 250 | MAJOR | global RNG pollution; Pattern #18 violation |
| ST-04-011 | `game/ui/screens/galaxy_test/galaxy_mode.py:239` | `random.seed(self.galaxy_seed)` | global seed alongside per-instance RNG at line 261 | delete line 239 | MAJOR | global RNG pollution; Pattern #18 violation |
| XSHARD-GS | `game/ui/services/game_settings.py:22` | `_default_game_settings` | 0 consumers (dead) for both module-level and ctx | remove module-level default + setter; evaluate ctx field | MINOR | none; dead code |
| XSHARD-IMG | `game/ui/services/image/defaults.py:19` | `_default_image_provider` | 0 consumers (dead) | remove dead default + setter; verify ctx field before removing | MINOR | none; dead code |
| XSHARD-PROF | `game/core/profiling.py:25` | `set_default_profiler` / `_default_profiler` | 0 `get_default_profiler()` consumers, BUT setter still called in `create_production()` and `profile_action`/`profile_block` use `_default_profiler` as live hook | design cleanup: migrate decorators to ctx then remove, OR keep as intentional hook (NOT blind deletion) | MINOR | none if handled as design cleanup; breakage if deleted blindly |

## Rejected

None. No candidate produced counter-evidence warranting rejection. (The audit's own verifier already corrected the single over-rated item via the `exit_dialog` CRITICAL→MAJOR downgrade, which this pass adopted.)

## Uncertain (resolved)

None raised during verification. The three borderline scope calls were resolved via the Codex consult and recorded in `decisions.md` / `bundling_decisions.md` — none required a human-judgement Include/Exclude/Defer split.

## Out of Scope

| ID | Why excluded |
|----|--------------|
| ST-01-003 | `ability_iterator` `_HEX_PROVIDERS`/`_SYSTEM_PROVIDERS` lists — Registry pattern (Pattern #4); additive import-time registration; documented test seam (`unregister_source_provider`) |
| ST-01-004 | `ability_iterator` fleet-lookup slots — session-injected once at startup; documented seam; minor style divergence only |
| ST-02-003 | `density_map` unseeded `random.Random()` — Pattern #18-compliant instance RNG (Pattern #18 targets module-level `random.*`; guard test excludes strategy generation). Docstring-accuracy issue only, not a state bug. Logged in refinement proposal as doc-drift. |
| `_default_sink` | Simulation-layer convention; intentionally not ctx-wired; `NullCaptureSink()` default; bootstrap sets it explicitly |
| `_default_ship_materializer` | Simulation-layer convention; Combat Lab overrides via setter |
| `_default_planet_habitability_service` | Documented PROJ-372 extension slot; intentionally module-level in `context.py` |
| font/portrait/galaxy lazy caches | Lazy-load caches; mostly documented/acceptable; stale-cache notes are not state bugs |
| class_mutable_defaults | Zero findings in the audit; codebase uses `None`/`field(default_factory=...)`/`frozenset` |
