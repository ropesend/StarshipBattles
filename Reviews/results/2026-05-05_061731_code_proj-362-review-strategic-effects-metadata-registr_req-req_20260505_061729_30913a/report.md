# PROJ-362 Review: Strategic Effects Metadata Registry

**Review mode:** code (full)
**Scope:** 6 files (2 production, 3 test, 1 decisions doc)
**Request ID:** req_20260505_061729_30913a
**References:** docs/01_ARCHITECTURE.md, docs/02_PATTERNS.md, docs/03_CONVENTIONS.md
**Limitations:** None — all scope files read in full. UI consumer survey limited to `grep` of legacy field names across `game/ui/`.

---

## Instruction Verification Summary

| Instruction | Result |
|---|---|
| Registry covers all current strategic effect abilities | **PASS** — 12/12 legacy names present; `test_registry_covers_exactly_the_legacy_set` confirms no gaps, no extras |
| Decomposed functions layered cleanly with single responsibility | **PASS** — `_collect_providers` (source walk + scope filter + grouping), `_aggregate_status` (activation precedence), `_aggregate_value` (kind-dispatch to rate/multiplier aggregators), `_format_rows` (public shape assembly) are clean single-concern functions |
| EnvironmentalDamage special-case fallback preserved | **PASS** — `make_group_key` line 137-138 returns `"EnvironmentalDamage:environmental"` when `damage_type` is missing; `make_display_name` line 167-169 falls back to `'environmental'` |
| Phase 4 (_legacy_provider_fields) genuinely deferred | **PASS** — `_legacy_provider_fields` still present at line 542, called from `_build_provider` line 322. 5+ UI consumers confirmed reading `facility_name`/`planet_name`/`component_key` from provider dicts (system_tree_panel, planet_abilities_window, planet_report_panel, strategy_detail_fmt, planet_abilities_controller) |
| _aggregate unused params removal would break callers? | **MINOR-001** — removal would break the two production callers in the same file + test callers, but cleanup is straightforward. Deferral justified to minimize diff scope for this project. See finding below. |
| Layer-boundary check | **PASS** — `effect_ability_metadata.py` imports only stdlib (`dataclasses`, `typing`). No UI, simulation, engine, or assets imports. |

---

## Findings

### MAJ-001: `system_effects_collector.py` exceeds 500 LOC ceiling (569 lines)
**File:** `game/strategy/services/system_effects_collector.py`
**Severity:** MAJ
**Rule:** docs/02_PATTERNS.md — production files capped at 500 LOC

The decomposition into `_collect_providers` / `_aggregate_status` / `_aggregate_value` / `_format_rows` is a dramatic improvement (CC 47→3), but the file now holds those four helpers PLUS the public API (`collect_system_effects`, `collect_sector_effects`, `find_sector_effect`, `aggregate_value_or`), grouping/display-name functions, status helpers, `_build_provider`, `_legacy_provider_fields`, and the thin `_aggregate` orchestrator. At 569 lines it exceeds the ceiling by ~14%.

**Remediation:** Split the public API + `_legacy_provider_fields` into a separate module (e.g., `system_effects_api.py`) or extract the grouping/display-name functions into `effect_ability_display.py`. Either would bring the core aggregation file under 500 lines.

---

### MIN-001: `_aggregate` accepts unused `registries` and `system` parameters
**File:** `game/strategy/services/system_effects_collector.py:512-539`
**Severity:** MIN
**Fingerprint:** `sha256:a8f3c2e1d6b7`

The `_aggregate` function accepts `registries` and `system` but neither is referenced in the body. The docstring at line 526-527 acknowledges this ("retained for signature compatibility"). The two production callers (`collect_system_effects` at line 232, `collect_sector_effects` at line 248) both pass these through. The `registries` parameter IS used by the wrapped iterator calls (`iter_ability_sources_in_system` / `iter_ability_sources_at_hex`) but not by `_aggregate` itself. `system` is unused by the iterators in this call path as well (the iterator uses its own `system` parameter which the public functions already provide).

Removing these two params from `_aggregate` would require:
- Dropping `registries` and `system` from the `_aggregate` signature
- Dropping them from the two call sites in `collect_system_effects` / `collect_sector_effects`
- Updating characterization tests that pass `registries=None, system=None`

Deferral is justified per the project's intent to minimize diff scope for this phase. Flag for cleanup in a follow-up.

---

### MIN-002: `all_owner_aware_scopes()` has zero production consumers
**File:** `game/strategy/services/effect_ability_metadata.py:160-172`
**Severity:** MIN
**Fingerprint:** `sha256:b2c7d4f0e8a9`

The function `all_owner_aware_scopes()` is defined, has a docstring, and is unit-tested — but no production code imports it. The original module-level `_OWNER_AWARE_SCOPES` constant was used directly by the collector's D17 guard. After the registry refactor, the collector now reads scopes per-entry via `metadata.owner_aware_scopes` (line 390). The global union function appears to be dead code retained for forward-looking API completeness.

**Remediation:** Either wire this into the collector as a defensive global check (e.g., the initial warning path before the per-entry check) or drop it entirely. The test `test_all_owner_aware_scopes_returns_legacy_set` would need to move/retire accordingly.

---

### MIN-003: `Optional[X]` return-type annotations instead of PEP 604 `X | None`
**Files:**
- `game/strategy/services/effect_ability_metadata.py:150` (`Optional[EffectAbilityMetadata]`)
- `game/strategy/services/system_effects_collector.py:258` (`Optional[Dict[str, Any]]`)
**Severity:** MIN
**Fingerprint:** `sha256:c1d5e3f7b2a4`

docs/03_CONVENTIONS.md: "Return-type annotations required on every public function/method (PEP 604 syntax: `int | None`)". Both files use the older `Optional[X]` from `typing` instead of `X | None`. The `typing.Optional` import is still present at `effect_ability_metadata.py:24`.

**Remediation:** Replace `Optional[EffectAbilityMetadata]` → `EffectAbilityMetadata | None` (line 150), `Optional[Dict[str, Any]]` → `Dict[str, Any] | None` (line 258). Remove `Optional` from the typing import.

---

### NIT-001: `_aggregate_status` uses direct dict access where helpers elsewhere use defensive patterns
**File:** `game/strategy/services/system_effects_collector.py:428`
**Severity:** NIT
**Fingerprint:** `sha256:d4e6f8a0b1c3`

```python
if any(p['is_active'] for p in providers):
```

A malformed provider dict would raise `KeyError` here. The providers are built by `_build_provider` which always includes `is_active`, so this is safe in practice, but `.get('is_active')` would be consistent with the defensive posture of the pipeline (get_abilities/affects_hex error tolerance).

---

### NIT-002: `format_intrinsic_ability_magnitude` has no direct unit test
**File:** `game/strategy/services/system_effects_collector.py:173-217`
**Severity:** NIT
**Fingerprint:** `sha256:e5f7a9b2c3d4`

This function is a public API entry used by UI panels (planet list per-effect columns, system tree panel). The 17-line function handles rate-style (EnvironmentalDamage, FuelDrain, generic) and multiplier-style formatting with identity-value gating. It has no direct unit test; coverage is only via UI integration paths.

**Remediation:** Add parameterized unit tests for: unknown ability returns `""`, rate=0 returns `""`, multiplier=None returns `""`, multiplier=1.0 returns `""`, non-float value returns `""`, EnvironmentalDamage formatting, FuelDrain formatting, generic multiplier formatting.

---

### NIT-003: `_build_provider` and `_legacy_provider_fields` lack direct unit tests
**Files:**
- `game/strategy/services/system_effects_collector.py:287-323`
- `game/strategy/services/system_effects_collector.py:542-569`
**Severity:** NIT
**Fingerprint:** `sha256:f6a8b0c1d2e3`

Both functions are covered indirectly by characterization tests but have no dedicated unit tests. `_legacy_provider_fields` is particularly worth testing directly since its behavior differs significantly for facility vs non-facility sources and will be subject to change in Phase 4.

---

## Architectural / Pattern Assessment

| Concern | Verdict |
|---|---|
| Registry pattern conformance | Matches `stabilizer_registry.py:54-70` pattern — frozen dataclass + tuple registry + name-keyed lookup. Consistent. |
| Dependency direction | `effect_ability_metadata.py` depends only on stdlib; `system_effects_collector.py` depends on Core (via `ComponentActivationState`) + Strategy services (ability_iterator, strategic_ability_scanner, effect_ability_metadata). No upward dependencies. |
| Single-responsibility principle | Each decomposed function has a clear, documented concern. `_collect_providers` is the largest at ~75 lines — acceptable. |
| CQRS-lite alignment | The `_aggregate` pipeline is read-side only (querying effect state). No command emission inside the pipeline. Correct separation. |
| Decisions.md alignment | All 8 decisions verified against code: metadata registry pattern (D4), no data migration (D5), no unification with combat_modifier_collector (D6), signatures preserved (D7), Phase 4 deferred (D8). Fully consistent. |

---

## Test Quality Assessment

| Test File | Lines | Strengths | Gaps |
|---|---|---|---|
| `test_effect_ability_metadata.py` | 174 | Exhaustive registry contract validation; parametrized kind/grouping/display-name/activatable tests; immutability check; legacy set parity | None significant |
| `test_system_effects_collector_aggregate_characterization.py` | 381 | Thorough edge-case coverage: get_abilities exception, affects_hex exception, DEACTIVATING phase, mixed activation precedence, owner filtering, improvement_rate fallback | `_collect_providers` D17 warning path only covered indirectly; `_build_provider` value field selection only covered indirectly |
| `test_system_effects_collector_decomposition.py` | 222 | Direct unit tests for status/value/format contracts; mixed-kind D16 validation; empty-input defense | Missing: parametrized `_aggregate_status` for None provider states; `_aggregate_value` with all-inactive-but-no-active-entries |

---

## Summary

The PROJ-362 refactoring is well-executed. The `EffectAbilityMetadata` registry pattern is correctly applied, the decomposition is clean, all legacy behavior is preserved (including the EnvironmentalDamage and improvement_rate fallbacks), and the Phase 4 deferral is justified by confirmed UI consumers. The CC reduction (47→3) is substantial and the characterization test safety net is thorough.

**Findings tally:** 0 CRIT, 1 MAJ, 3 MIN, 3 NIT
