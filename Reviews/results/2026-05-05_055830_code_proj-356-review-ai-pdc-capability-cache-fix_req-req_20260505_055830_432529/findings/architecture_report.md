# Architecture Review: PROJ-356 — AI PDC Capability Cache Fix

**Date:** 2026-05-05
**Reviewer:** OpenCode Architecture Reviewer
**Commit:** 309ecef93 (reported)
**Docs consulted:** `docs/01_ARCHITECTURE.md` (AI layer section), `docs/02_PATTERNS.md` (Protocol+TypeGuard, DI, Facade)

---

## Summary

- **Total issues found:** 5
- **Critical:** 0, **Major:** 0, **Minor:** 3, **Info:** 2

The fix correctly replaces the dead `has_ability('PDCAbility')` string check with the canonical PROJ-241 tag-based `has_pdc_ability()` surface. No layer violations or compatibility shims detected. Three minor findings relate to duplicated PDC discovery logic, simulation-internal protocol imports, and unused cache keys — all documented in scope.md and not blocking.

---

## Findings

#### MINOR: PDC weapon discovery logic duplicated between cache builder and is_in_pdc_arc
**ID:** AR-001
**Location:** `game/ai/controller.py:226-231`, `game/ai/combat_utils.py:216-234`
**Issue:** Both `_build_capabilities_cache` and `is_in_pdc_arc` independently call `get_components_by_ability('WeaponAbility')` followed by `has_pdc_ability()` filtering. The cache pre-computes `pdc_components` but `is_in_pdc_arc` ignores it and rediscover PDC weapons from scratch on every evaluation call.
**Impact:** Efficiency: PDC filtering runs O(1) times in the cache build but may run O(n) times in `_eval_pdc_arc_rule` for every target candidate. In practice, PDC weapons per ship are few and the cost is low, but the duplication creates a maintenance hazard — if PDC detection logic changes, both sites must be updated.
**Recommendation:** Extend `is_in_pdc_arc` to accept an optional `pdc_components` list from the cache when the caller has it available. Add a kwarg `pdc_components: list | None = None` and use the pre-computed list when provided, falling back to the current query. The `_eval_pdc_arc_rule` caller in `target_evaluator.py` can then pass `ship_capabilities_cache.get(entity_id, {}).get('pdc_components')`.
**Effort:** Simple

---

#### MINOR: is_combat_ship imported from simulation-internal module rather than core protocols
**ID:** AR-002
**Location:** `game/ai/controller.py:68`
**Issue:** The controller imports `is_combat_ship` from `game/simulation/interfaces/entity_protocols.py` (designated "Simulation-Internal Protocols" per `docs/01_ARCHITECTURE.md` § Simulation-Internal Protocols). There is a parallel `is_combat_ship` at `game/core/protocols/combat.py:131` with different matching criteria (`'angle', 'layers'` in simulation-internal vs `'team_id', 'hp', 'is_derelict'` in core). The architecture doc lists `ICombatShip` / `is_combat_ship` under core-level Combat Protocols and prescribes cross-layer communication through `game/core/protocols/`.
**Impact:** While AI→Simulation is an allowed dependency, importing from "internal" simulation modules creates a fragility risk — if simulation refactors its internal protocol module layout, the AI layer breaks. The simulation-internal TypeGuard checks `angle` and `layers` (matching actual `Ship` class internals) and is arguably more correct for the AI's needs, but this divergence from the documented pattern is architectural drift.
**Recommendation:** Either (a) promote the simulation-internal `is_combat_ship` signature into `game/core/protocols/combat.py` (single source of truth for `ICombatShip`), or (b) document the intentional split and update `01_ARCHITECTURE.md` to note that AI-layer combat code prefers the simulation-internal TypeGuard for tighter matching. Option (a) is preferred; consolidate into one canonical `is_combat_ship` in core that checks `('team_id', 'hp', 'is_derelict', 'angle', 'layers')` to satisfy both consumers.
**Effort:** Medium (requires audit of all callers of both TypeGuards)

---

#### MINOR: Cache keys 'has_pdc' / 'pdc_components' written but never consumed
**ID:** AR-003
**Location:** `game/ai/controller.py:233-238`, `game/ai/target_evaluator.py:169` (sole consumer)
**Issue:** `_build_capabilities_cache` computes `has_pdc` and `pdc_components` for every cached ship, but no code reads these keys. The sole cache consumer (`_eval_has_weapons_rule` at `target_evaluator.py:169`) only reads `has_weapons`. `_eval_pdc_arc_rule` bypasses the cache entirely. This is confirmed in `decisions.md` ("purely correctness for future consumers") and `scope.md`.
**Impact:** Dead compute. For a typical battle with N ships, this adds N `has_pdc_ability()` calls per tick that produce unused data. While `has_pdc_ability()` is cheap (iterates ability instances, checks tags), it's wasted work. More importantly, it's a maintenance hazard: future developers may add a consumer without realizing the cache already provides PDC data, or may assume the cache covers all PDC needs when it doesn't.
**Recommendation:** Either (a) remove `has_pdc` / `pdc_components` from the cache until a real consumer exists (keep the code in a branch/comment), or (b) adopt them immediately in `_eval_pdc_arc_rule` via a helper that uses the cache when available (see AR-001). The decisions.md rationale ("correctness for future consumers") is valid but the dead store should have a ticket (e.g., PROJ-XXX Phase 2) tracking the follow-through.
**Effort:** Simple (remove or wire up)

---

#### INFO: Duplicate is_projectile TypeGuard definitions across layers
**ID:** AR-004
**Location:** `game/ai/protocols.py:117`, `game/simulation/interfaces/entity_protocols.py:474`
**Issue:** Two separate `is_projectile` TypeGuard functions exist: `game/ai/protocols.py:117` checks `('position', 'type')` and `game/simulation/interfaces/entity_protocols.py:474` checks `('type', 'position')` — same attributes, same semantics, different files. The AI controller imports from the AI-layer protocol, while `combat_utils.py` imports from the simulation protocol (`src/ai/controller.py:67` and `game/simulation/interfaces/entity_protocols.py:474` via `combat_utils.py`). This mirrors the `is_combat_ship` duplication pattern (AR-002).
**Impact:** Conceptual duplication. If the TypeGuard criteria diverge (e.g., one adds a new required attribute), the two copies will behave differently, causing inconsistent guard behavior across the AI layer. Currently benign because both check the same attributes.
**Recommendation:** Consolidate `is_projectile` into `game/core/protocols/combat.py` alongside `is_combatant` and `is_combat_ship`. Update all importers to use the core protocol.
**Effort:** Simple (centralize, update ~3 import sites)

---

#### INFO: Test anti-regression design is exemplary
**ID:** AR-005
**Location:** `tests/unit/ai/test_capability_cache_pdc.py:70-83`
**Issue:** N/A — positive observation. The test helper `_make_weapon` intentionally sets `weapon.has_ability = MagicMock(return_value=False)` so any code still calling the dead `has_ability('PDCAbility')` path would fail. `test_does_not_call_legacy_string_ability_path` (line 127) explicitly asserts `'PDCAbility' not in args` on the `has_ability` call_args_list. This is a well-crafted double-guard: `has_pdc_ability.called` is asserted True AND `has_ability` with the dead string is asserted absent.
**Impact:** Positive — this anti-regression design catches both missing fix (False negative) and re-introduced dead path (False positive from wrong API). The decision to leave `test_controllable_adapter_edge_cases.py:231` as-is (it tests adapter passthrough, not PDC discovery) is correct.
**Recommendation:** Consider adopting this "mock the dead path to return False + assert it wasn't called" pattern as a documented testing convention (add to `docs/02_PATTERNS.md` or `docs/03_CONVENTIONS.md` under a "Regression Test Guardrail" section).
**Effort:** Simple (documentation)

---

## Top 5 Priority Issues

| Rank | ID | Severity | Title |
|------|----|----------|-------|
| 1 | AR-002 | MINOR | `is_combat_ship` imported from simulation internals, not core protocols |
| 2 | AR-001 | MINOR | PDC weapon discovery duplicated between cache and `is_in_pdc_arc` |
| 3 | AR-003 | MINOR | Cache keys `has_pdc` / `pdc_components` written but unconsumed |
| 4 | AR-004 | INFO | Duplicate `is_projectile` TypeGuard across AI and simulation layers |
| 5 | AR-005 | INFO | Exemplary anti-regression test pattern (positive finding) |

---

## Architecture Compliance Checks

| Check | Status | Detail |
|-------|--------|--------|
| AI layer dependency boundaries | **PASS** | All imports from Core, AI, or Simulation — no Strategy/UI imports |
| Protocol + TypeGuard pattern | **PASS** | `is_combat_ship(entity)` guard at `controller.py:218` correct; imported from simulation internals (see AR-002) |
| Facade/Delegate pattern (PROJ-241) | **PASS** | `has_pdc_ability()` delegates through Component facade → AbilityManager → `has_ability_with_tag('pdc')` |
| Per-Battle RNG (Pattern #18) | **PASS** | Controller accepts `rng` kwarg, forwards to ErraticBehavior |
| DI / Registry (Pattern #3) | **PASS** | `PolicyManager` accessed via `get_default_policy_manager()`, consistent with existing pattern |
| No compatibility shims | **PASS** | No fallback `has_ability('PDCAbility')` path; clean replacement |
| LOC ceiling (500) | **PASS** | `controller.py` = 469 lines |
| Return-type annotations | **PASS** | `_build_capabilities_cache` returns `Dict[str, Dict[str, Any]]` |
| Exception hygiene | **PASS** | Broad excepts in `_score_and_sort_enemies` have context-logging; no bare excepts |

---

## Broader Audit Findings

- **No remaining `PDCAbility` string references** in `game/` production code (confirmed via grep). The only occurrence is a comment in `test_ai_capabilities_cache.py:64` explaining the legacy path.
- **No cache bypass for `has_weapons`** — `_eval_has_weapons_rule` correctly reads the cache. Only PDC keys are unused.
- **`_eval_pdc_arc_rule`** at `target_evaluator.py:218` uses `is_in_pdc_arc(ship, candidate)` through a `stat_helpers` dictionary, which runs a fresh component query every call. This is the documented bypass noted in scope.md.
- **`is_in_pdc_arc`** at `combat_utils.py:233` correctly calls `has_pdc_ability()` on each weapon component — consistent with the controller's fix.
- **`test_ai_capabilities_cache.py:63-67`** — The existing `create_mock_enemy` helper was updated to mock `has_pdc_ability` instead of `has_ability`, fixing the bug in the test fixture documented in decisions.md.
