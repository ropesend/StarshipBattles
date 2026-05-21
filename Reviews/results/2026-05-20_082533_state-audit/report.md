# State Management & Mutability Audit — Final Report

**Date:** 2026-05-20
**Review directory:** `Reviews/results/2026-05-20_082533_state-audit`
**Files scanned:** 846 production files across 4 shards

---

## 1. Executive Summary

The state management audit analyzed 846 production files across `game/` for module-level mutable state, singleton divergence risk (ApplicationContext vs module-level accessors), global keyword abuse, class-level mutable defaults, and `random.seed()` bypass.

**Overall ctx adoption: 47.7%** (104 `get_default_xxx()` calls vs 95 `ctx.xxx` accesses). However, this is heavily skewed — `ctx.profiler` in `app_bootstrap.py` drives the ctx count, while the **UI layer sits at ~3% ctx** with ~55 module-level `get_default_*` calls.

### Key Numbers

| Metric | Count |
|--------|-------|
| Singletons detected | 14 |
| Module-level mutables (non-__all__) | 4 |
| `global` keyword usages | 71 |
| Class mutable defaults | 0 |
| `random.seed()` outside RNG | 2 |
| `get_default_xxx()` call sites | 104 |
| `ctx.xxx` accesses | 95 |

---

## 2. State Hygiene Scorecard

| Category | Count | Critical | Major | Minor |
|----------|-------|----------|-------|-------|
| Singleton divergence risk | 14 | 1 | 8 | 5 |
| Module-level mutable collections | 4 | 0 | 3 | 1 |
| Global keyword usages | 71 | 0 | 1 | 70 |
| Class mutable defaults | 0 | 0 | 0 | 0 |
| `random.seed()` outside RNG | 2 | 0 | 2 | 0 |

---

## 3. Singleton Divergence Risk Map

### CRITICAL: `_default_provider` — `game/core/registry.py:466`

- **Call sites:** 68+ across Core, Strategy, UI, App layers
- **ctx binding:** None (no `ctx.registry_provider` field exists)
- **Setter:** None — auto-creates `DefaultRegistryProvider` on first access
- **Risk:** Widest divergence surface in the codebase. If accessed before `ctx.create_production()` hydrates `RegistryManager`, the auto-created provider references a different manager instance. No synchronization path exists.
- **Recommendation:** Add `ctx.registry_provider` binding + `set_default_registry_provider()`, or enforce explicit DI everywhere.

### MAJOR

| Singleton | Files | get_default | ctx | Risk |
|-----------|-------|-------------|-----|------|
| `_default_ship_theme_manager` | UI (15 sites) | 15 | 0 | Heaviest get_default load; ctx-wired but unused |
| `_default_manager` (RegistryManager) | Core (9+2) | 9 | 2 | Dual pattern in Core layer |
| `_default_asset_manager` | UI (7 sites) | 7 | 0 | ctx-wired bridge mechanic |
| `_default_cache_manager` | Simulation (4) | 4 | 0 | No setter; direct attr assignment |
| `_default_policy_manager` | AI/UI (3) | 3 | 0 | No setter; direct attr assignment |
| `_default_sprite_manager` | UI (2) | 2 | 0 | Dual pattern in app_bootstrap.py |
| `_default_llm_provider` | UI (1) | 1 | 0 | Bridge mechanic |
| `_default_provider` (per-shard, ST-04-001) | All (68+) | 68+ | 0 | No setter (see CRITICAL above) |

### MINOR

| Singleton | Status |
|-----------|--------|
| `_default_profiler` | Successfully ctx-migrated — 22+ ctx calls, 0 get_default. Setter is bridge mechanic ready for removal. |
| `_default_game_settings` | Dead code — no consumers found. |
| `_default_image_provider` | Dead code — no consumers found. |
| `_default_sink` | Simulation-layer convention — acceptable. |
| `_default_ship_materializer` | Simulation-layer convention — acceptable. |
| `_default_planet_habitability_service` | Documented extension slot (PROJ-372) — acceptable. |

---

## 4. ApplicationContext Access Pattern Progress

### Layer-by-Layer ctx Adoption

| Layer | get_default | ctx | % ctx | Trend |
|-------|-------------|-----|-------|-------|
| ui | ~55 | ~2 | ~3.5% | Heavily module-level |
| strategy | ~7 | ~2 | ~22% | Mixed; DI in session |
| core | ~12 | ~1 | ~8% | Self-referential module-level |
| ai | ~2 | 0 | 0% | All module-level |
| simulation | ~6 | 0 | 0% | Intentional (by design) |
| app/bootstrap | ~1 | ~22 | ~96% | ctx pattern adopted |

### Per-Shard ctx Usage

| Shard | get_default | ctx | % ctx |
|-------|-------------|-----|-------|
| 01 (UI-heavy) | 40 | 1 | 2.4% |
| 02 (Strategy/UI) | 22 | 9 | 29.0% |
| 03 (app/bootstrap) | 9 | 62 | 87.3% |
| 04 (UI/Strategy) | 33 | 23 | 41.1% |

**7 bridge mechanics** identified: setter functions whose only production caller is `ApplicationContext.create_production()`. Once all consumers migrate to `ctx.xxx`, these can be removed.

**3 missing setters:** `_default_cache_manager`, `_default_policy_manager`, `_default_provider` — assigned via raw module attribute manipulation or auto-created in getter.

---

## 5. Module-Level Mutable Collection Safety

### Confirmed Issues

| ID | Collection | File | Severity | Issue |
|----|-----------|------|----------|-------|
| ST-02-001 | `ShipCombatEngine._damage_calculator` (class-level) | `ship_combat_engine.py:41-43` | MAJOR | Shared across all instances; reset only on `start()`; test-isolation risk |
| ST-01-002 | `_next_fleet_id` | `battle_setup_state.py:24` | MAJOR | Unbounded global counter; no reset for test isolation |
| ST-04-004 | `_SERIALIZABLE_REGISTRY` | `json_utils.py:53` | MAJOR | Mutable dict with no test reset (copy-on-read mitigates read-side) |
| ST-04-005 | `_catalog` | `transfer_mass_preview.py:186` | MAJOR | Lazy cache with no invalidation; stale data risk for tests |

### Global Keyword Findings

71 global keyword usages across 29 sites. The vast majority (~68) are singleton accessor pairs (`get_default_xxx`/`set_default_xxx`) or lazy-load caches with explicit reset functions — all pattern-compliant.

Non-trivial:
- **ST-01-001 (MAJOR):** `game/exit_dialog.py:24` — `_exit_yes_rect`/`_exit_no_rect` globals reassigned every frame
- **ST-02-002 (MINOR):** `CREW_PRIORITY_REGISTRY` with no test reset function

### Class Mutable Defaults

**Zero findings.** The entire production codebase uses `None`, immutable primitives, `field(default_factory=...)`, or `frozenset` for parameter defaults. No `[]`/`{}`/`set()` parameter defaults found.

---

## 6. Random State Hygiene

| ID | File | Line | Call | Severity |
|----|------|------|------|----------|
| ST-04-010 | `game/strategy/engine/game_initializer.py` | 250 | `random.seed(galaxy_seed)` | MAJOR |
| ST-04-011 | `game/ui/screens/galaxy_test/galaxy_mode.py` | 239 | `random.seed(self.galaxy_seed)` | MAJOR |

Both sites already create a proper per-instance `random.Random(seed)` but additionally call `random.seed()` on the global random module. Per Pattern #18, global `random.seed()` calls are prohibited — remove the global seed lines.

---

## 7. Prioritized Remediation Plan

| # | Item | Risk | Sites | Action |
|---|------|------|-------|--------|
| 1 | `_default_provider` — add ctx wiring + setter | **CRITICAL** | 68+ | Add `set_default_registry_provider()` + ctx binding; or enforce explicit DI |
| 2 | `_default_ship_theme_manager` — migrate to ctx | MAJOR | 15 | Thread ctx through UI constructors — highest get_default reducer |
| 3 | `_default_asset_manager` — migrate to ctx | MAJOR | 7 | Thread ctx through UI constructors |
| 4 | `_default_manager` — resolve dual pattern in Core | MAJOR | 9+2 | Pick ctx or module-level; remove dual-path access |
| 5 | `_default_cache_manager` — add setter | MAJOR | 4 | Add `set_default_cache_manager()`; wire in create_production() |
| 6 | `_default_policy_manager` — add setter | MAJOR | 3 | Add `set_default_policy_manager()`; wire in create_production() |
| 7 | `ShipCombatEngine` — convert to per-instance | MAJOR | 1 file | Thread `DamageCalculator` via constructor injection |
| 8 | `random.seed()` removal ×2 | MAJOR | 2 lines | Delete lines 250 (game_initializer.py), 239 (galaxy_mode.py) |
| 9 | `_next_fleet_id` — instance attribute | MAJOR | 1 file | Move counter to `BattleSetupState` instance |
| 10 | `_SERIALIZABLE_REGISTRY` — add reset | MAJOR | 1 file | Add `reset_serializable_registry()` test seam |
| 11 | `_catalog` — add invalidation | MAJOR | 1 file | Add `_clear_catalog()` test hook |
| 12 | `_default_profiler` setter — remove bridge | MINOR | 1 file | All consumers use ctx; setter is dead weight |
| 13 | `_default_game_settings` + `_default_image_provider` — remove | MINOR | 2 files | Dead code — no consumers |

---

## 8. Verification Summary

All 2 CRITICAL findings and 10 MAJOR findings were spot-checked against source code:

- **1 CRITICAL confirmed:** `_default_provider` — 68+ call sites, no setter, no ctx binding
- **1 downgraded to MAJOR:** `exit_dialog.py` rects — functionally low risk (modal dialog, derived values)
- **10 MAJOR spot-checks:** All CONFIRMED — zero false positives
- **0 DISPUTED**

---

## 9. Trend Comparison

First run for this audit — no trend data yet.

---

## 10. Appendices

### Raw Outputs
- `raw/singleton_sites.json` — 14 singleton definitions
- `raw/module_mutables.json` — 218 module-level mutables (mostly `__all__` lists)
- `raw/global_usages.json` — 71 global keyword usages
- `raw/class_mutable_defaults.json` — 0 findings
- `raw/random_seed_sites.json` — 2 findings
- `raw/ctx_usage_ratio.json` — 47.7% ctx adoption
- `raw/manifest.json` — 4-shard file assignments

### Per-Shard Findings
- `findings/state_review_01.md` — Shard 01 (156 files, 5 findings)
- `findings/state_review_02.md` — Shard 02 (171 files, 5 findings)
- `findings/state_review_03.md` — Shard 03 (195 files, 2 findings)
- `findings/state_review_04.md` — Shard 04 (199 files, 10 findings)

### Cross-Shard Analysis
- `findings/state_divergence_cross_shard.md` — 14 singletons analyzed, divergence risk map
- `findings/verification.md` — 12 findings verified, 1 downgraded, 0 disputed
