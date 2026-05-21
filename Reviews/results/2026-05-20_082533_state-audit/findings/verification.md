# Verification Report

**Date:** 2026-05-20
**Audit run:** 2026-05-20_082533_state-audit
**Agent:** OpenCode verification

## Summary

- **CRITICAL findings examined:** 2
- **MAJOR findings spot-checked:** 10 (of ~14 unique, ~71% coverage)
- **CONFIRMED:** 11 | **DOWNGRADED:** 1 | **DISPUTED:** 0

---

## Critical Finding Verification

| Finding ID | Variable | File | Verdict | Reason |
|------------|----------|------|---------|--------|
| Cross-shard CRITICAL | `_default_provider` | `game/core/registry.py:466` | **CONFIRMED** | No `set_default_registry_provider()` exists. Auto-creates `DefaultRegistryProvider` on first `get_default_registry_provider()` call (line 480-482). 68+ call sites across 4 layers (Core, Strategy, UI, App). No ctx binding. Divergence window: if `_default_provider` auto-creates before `ctx.create_production()` hydrates `RegistryManager`, the provider references a different manager instance. `set_default_registry_manager()` (line 175 of context.py) is called in production bootstrap, but no corresponding provider sync exists. CRITICAL severity justified. |
| ST-01-001 | `_exit_yes_rect` / `_exit_no_rect` | `game/exit_dialog.py:11-12` | **CONFIRMED** (downgrade → MAJOR) | Finding is accurate: `_exit_yes_rect = None` and `_exit_no_rect = None` at lines 11-12, `global` keyword at line 24, read by `handle_exit_dialog_click()` (line 86) and `handle_exit_dialog_cancel()` (line 101). However, severity is overstated. The rects are pure derived values computed from screen dimensions each frame, the dialog is modal (shown on a single screen at a time), and the click handlers only fire while the dialog is active. Functional risk is limited to maintainability (implicit coupling through globals), not state corruption. **Downgraded from CRITICAL to MAJOR.** |

---

## MAJOR Finding Spot Checks

| Finding ID | Variable | File | Verdict | Reason |
|------------|----------|------|---------|--------|
| ST-04-010 | `random.seed(galaxy_seed)` | `game/strategy/engine/game_initializer.py:250` | **CONFIRMED** | Line 248 creates per-instance `rng = random.Random(galaxy_seed)` (compliant). Line 250 additionally calls `random.seed(galaxy_seed)` with comment "Also seed global random for star/planet generation" — an unnecessary global side effect that violates Pattern #18. |
| ST-02-001 / Report 03 | `ShipCombatEngine._targeting_system`, `_damage_calculator`, `_weapon_firing_system` | `game/simulation/entities/ship_combat_engine.py:41-43` | **CONFIRMED** | Three class-level `Optional[X] = None` attributes shared across all instances. `__init__` (lines 56-63) lazily populates on first construction. `battle_setup.py:49` overwrites `_damage_calculator` from an external module. `_weapon_firing_system` chains through `_targeting_system` (line 61-62). Test isolation risk confirmed. |
| ST-01-002 | `_next_fleet_id` | `game/ui/screens/battle_setup_state.py:24` | **CONFIRMED** | `_next_fleet_id = 1000` (line 24). `_generate_fleet_id()` (lines 27-31) uses `global _next_fleet_id` and increments with `+= 1`. Unbounded growth across process lifetime. No reset. |
| ST-04-002 | `_default_cache_manager` | `game/simulation/components/component_loader.py:37` | **CONFIRMED** | `_default_cache_manager = None` (line 37). No `set_default_cache_manager()` function exists. `get_default_cache_manager()` auto-creates (line 48-50). `ctx.create_production()` assigns directly via `_ccm_module._default_cache_manager = component_cache` (line 188). `reset_component_caches()` (lines 67-70) directly reassigns without ctx path — creates divergence from `ctx.component_cache`. |
| ST-04-004 | `_SERIALIZABLE_REGISTRY` | `game/core/json_utils.py:53` | **CONFIRMED** | `_SERIALIZABLE_REGISTRY: Dict[str, type] = {}` (line 53). Mutated by `@register_serializable` decorator (line 69). `get_serializable_registry()` returns a `dict()` copy (line 76) mitigating read-side race but no `clear_serializable_registry()` exists for test isolation. Finding accurate, though the copy-on-read pattern limits practical risk. |
| ST-04-005 | `_catalog` | `game/ui/screens/transfer_mass_preview.py:186` | **CONFIRMED** | `_catalog = None` (line 186). `_get_catalog()` lazy-loads `ResourceCatalog.from_json()` (lines 189-203). No invalidation/clear function. File's own docstring (lines 192-197) explicitly warns: "Tests that swap the catalog through set_resource_catalog do not affect this cache." |
| ST-04-011 | `random.seed(self.galaxy_seed)` | `game/ui/screens/galaxy_test/galaxy_mode.py:239` | **CONFIRMED** | `random.seed(self.galaxy_seed)` at line 239, then `rng = random.Random(self.galaxy_seed)` at line 261. Same anti-pattern as ST-04-010 — unnecessary global `random.seed()` alongside proper per-instance RNG. Galaxy test tool, not production combat path, but still violates Pattern #18. |
| Cross-shard MAJOR | `_default_policy_manager` | `game/ai/policy_manager.py:23` | **CONFIRMED** | `_default_policy_manager = None` (line 23). No `set_default_policy_manager()` function. `get_default_policy_manager()` auto-creates (lines 34-36). `ctx.create_production()` line 190 assigns directly: `_pm_module._default_policy_manager = policy_manager`. Same anti-pattern as ST-04-002. |
| Cross-shard MAJOR | `_default_sprite_manager` | `game/ui/renderer/sprites.py:14` | **CONFIRMED** | Has proper setter (`set_default_sprite_manager()` line 122) called in `create_production()` line 180. However, `app_bootstrap.py:265` calls `get_default_sprite_manager()` even though `ctx` is in scope (line 264 uses `ctx.profiler`). This is the canonical dual-pattern coexistence — confirmed at source. |
| Cross-shard MAJOR | `_default_manager` (RegistryManager) | `game/core/registry.py:284` | **CONFIRMED** | 9 module-level call sites vs 2 ctx accesses. Both patterns coexist within Core layer. Auto-create path in `get_default_registry_manager()` (line 314) creates divergence window. 8 module-level convenience wrappers in `registry.py` itself route through module-level, not ctx. Dual-pattern in single file confirmed. |

---

## Downgraded Findings

| Finding ID | Variable | Original Severity | New Severity | Reason |
|------------|----------|-------------------|--------------|--------|
| ST-01-001 | `_exit_yes_rect` / `_exit_no_rect` | CRITICAL | **MAJOR** | Rects are pure derived values from `screen.get_size()`, recomputed every frame. Modal dialog — only one instance active at a time. Click handlers only fire while dialog is displayed. The implicit coupling through globals is a code smell affecting maintainability, but there is no functional state corruption risk. Pattern should be fixed per recommendation (encapsulate in class), but does not warrant CRITICAL. |

---

## Confirmed Critical

| Finding ID | Variable | File | Risk Summary |
|------------|----------|------|-------------|
| Cross-shard CRITICAL | `_default_provider` | `game/core/registry.py:466` | 68+ call sites across 4 layers. No setter. No ctx binding. Auto-creates on first access, creating singleton divergence window before `create_production()` hydrates `RegistryManager`. Highest remediation priority per cross-shard report item #1. |

---

## Notes

1. **All 10 spot-checked MAJOR findings confirmed.** No false positives found. The audit's MAJOR findings appear reliable.

2. **ShipCombatEngine duplicated finding.** Both Shard 02 (ST-02-001, MAJOR) and Shard 03 (MEDIUM) independently flagged the same class-level mutable state in `ship_combat_engine.py:41-43`. This is expected given the file was assigned to multiple shards (entity vs. system boundary). The findings are consistent — Shard 03's analysis is more detailed regarding the `battle_setup.py` cross-module write.

3. **`_default_provider` severity consistency.** Shard 04 rates this as MAJOR (ST-04-001) while the cross-shard divergence report rates it CRITICAL. The cross-shard report's rating is correct — the scope and call-count justifies CRITICAL. Shard 04's per-file perspective understates the cross-layering impact.

4. **`_SERIALIZABLE_REGISTRY` (ST-04-004) practical risk is low.** The `get_serializable_registry()` returns a `dict()` copy, which mitigates read-side mutation concerns. The finding is factually accurate (no reset exists) but the practical impact is minimal since decorator registrations are idempotent (same key → same value) and the copy-on-read pattern prevents observation of mutation.

5. **No findings DISPUTED.** All examined findings accurately describe the code at the cited locations. The only adjustment is severity downgrade of ST-01-001.
