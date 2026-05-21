# Phase 4: Strategic - Document 3 Undocumented Patterns

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-470 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Promote the 3 verified recurring undocumented patterns from audit `2026-05-20_075227_pattern-audit` to dedicated entries in `docs/02_PATTERNS.md`. (The other 3 undocumented-pattern candidates — UP-003 PerPlayerUiState, UP-004 Declarative Dispatch Table, UP-005 FacadeSessionState — were deferred during verification; see `findings/verification_report.md`.)

---

## Tasks

### Task 4.1: Document the HabitabilityFactor Registry [Medium]
**File:** `docs/02_PATTERNS.md`
**Pattern:** new entry (UP-001) — add after #43
**Tests:** N/A (doc-only)

- [x] Added Pattern #44 (HabitabilityFactor Registry) to `docs/02_PATTERNS.md`: frozen `HabitabilityFactor` dataclass, `FACTOR_REGISTRY` (7 scalar + 10 gas factors), `get_factor()`/`iter_scalar_factors()`/`iter_gas_factors()` API
- [x] Noted AGENTS.md single-source-of-truth role + ≈24 consumer references
- [x] Verify: entry matches live `FACTOR_REGISTRY` contents and API (read source)

### Task 4.2: Document the AbilityMetadataRegistry [Medium]
**File:** `docs/02_PATTERNS.md`
**Pattern:** new entry (UP-002) — add after #43
**Tests:** N/A (doc-only)

- [x] Added Pattern #45 (AbilityMetadataRegistry): `RoleTag`/`StrategicKind` enums (members listed), `EffectFacet`/`EnergyFacet`/`AbilityMetadata`, and the query API (`get_ability_metadata`, `ability_has_role_tag`, `ability_has_kind_tag`, `abilities_with_role_tag`, `abilities_with_kind_tag`, `ability_action_time_field`, `ability_drains_energy`)
- [x] Documented the cycle-safety invariant (must NOT import simulation abilities; pinned by `test_ability_metadata_module_does_not_import_simulation_abilities`)
- [x] Verify: entry matches live public API and enum members (read source)

### Task 4.3: Document the RoleRegistry layered-loading pattern [Medium]
**File:** `docs/02_PATTERNS.md`
**Pattern:** new entry or Pattern #4 sub-section (UP-006)
**Tests:** N/A (doc-only)

- [x] Added Pattern #46 (RoleRegistry layered-loading): layered JSON load (base→mods→user), `allow_runtime_add` gating + `RoleRegistryReadOnlyError`, `register_invalidation_callback`, the two instances (`design_role_registry` runtime-add=True, `combat_lab_role_registry` runtime-add=False), and the `get_default_*`/`set_default_*`/`reset_default_*` accessor convention
- [x] Decided STANDALONE Pattern #46 (not a #4 sub-section), cross-referenced as a Pattern #4 variant; recorded in decisions.md
- [x] Verify: entry matches live `Role`/`RoleRegistry` contract and accessor convention (read source)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes checked (Patterns #44/#45/#46 added)
- [x] Status set to `Complete`
- [x] plan.md phase table row updated
- [x] plan.md Current State updated

_Source audit: `Reviews/results/2026-05-20_075227_pattern-audit/`. See `findings/source_audit.md` for the link._
