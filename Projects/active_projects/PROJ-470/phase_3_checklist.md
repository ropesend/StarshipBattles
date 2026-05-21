# Phase 3: Minor - TypeGuards, source_kind enum, doc-drift, LOC triage

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-470 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (TypeGuards scoped per-site: TG-003 swapped, TG-001/002/004 KEPT; LOC triage OUT OF SCOPE)
**Objective:** Resolve the verified MINOR findings from audit `2026-05-20_075227_pattern-audit`: replace 4 same-layer concrete `isinstance` checks with the existing TypeGuards (Pattern #2), add a typed enum for `IAbilitySource.source_kind` (Pattern #29), reconcile 2 doc-drift entries (Patterns #32, #36), and triage the LOC ceiling.

---

## Tasks

### Task 3.1: TG-001 (`order_types.py`) — KEEP isinstance (NOT swapped) [scoped out]
**File:** `game/strategy/data/order_types.py`
**Pattern:** #2 (Protocol + TypeGuard)
**Tests:** N/A (no change)
**Status:** Resolved — KEEP isinstance, do not swap.

> **SCOPE REVISION 2026-05-20 (per-site TypeGuard scoping):** `order_types.py:104,116,119` is in
> `to_dict()` SERIALIZATION code that emits branch-specific save payloads (`planet_ref` vs
> `fleet_ref` vs `colonize_params` vs `dict`/`raw`). The candidate `is_planet`/`is_fleet`
> TypeGuards are duck-typed (`_has_attrs`, strictly BROADER than exact `isinstance`). Swapping
> could misclassify a target into the wrong serialized `*_ref` payload, a save-compat/determinism
> hazard. **KEEP exact isinstance.** (Verified against `strategy_entities.py:425-432` guards.)

- [x] TG-001 evaluated and KEPT as isinstance (serialization-adjacent; broader guard would change emitted payload). No code change.

### Task 3.2: TypeGuard swaps — per-site scoped (TG-003 SWAP; TG-002/TG-004 KEEP) [Medium]
**File:** `game/strategy/facade/slices/system_slice.py`
**Pattern:** #2 (Protocol + TypeGuard)
**Tests:** `pytest tests/ -k "system_slice or storm"` then `pytest tests/ --testmon`

> **SCOPE REVISION 2026-05-20 (per-site TypeGuard scoping):** the candidate guards are duck-typed
> (`_has_attrs`), strictly broader than exact `isinstance`. Each site evaluated individually.

- [x] **TG-002 (`fleet_dto.py:152-183`) — KEEP isinstance.** `FleetInfo.from_fleet` branches DTO
  field population (`target_id`/`target_hex`/`target_description`) by Planet vs Fleet. The
  broader duck-typed guards gain nothing and widen the type net on a behavior-branching factory.
  No change.
- [x] **TG-003 (`system_slice.py:132`) — SWAP to `is_storm`.** PROVEN exactly equivalent for the
  zone domain: the zone spatial index registers stars, storms, and planets
  (`galaxy_entity_registry.py:50,52,83`); `storm_type` is unique to `Storm` across
  `game/strategy/` and `is_storm` requires BOTH `storm_type` AND `abilities`, so no star/planet
  passes. Read-only filter, not serialization/value-affecting. Characterization test added
  (`tests/unit/strategy/facade/slices/test_system_slice.py::test_get_storm_names_at_hex_excludes_abilities_carrying_non_storm`).
- [x] **TG-004 (`build_queue_source.py:294`) — KEEP isinstance.** Dispatches DIFFERENT numeric
  production rates (determinism-adjacent); the else-branch treats "everything not a fleet" as a
  planet. Keeping exact `isinstance` preserves the value-affecting branch precisely. No change.
- [x] Verify: targeted suites green — system_slice (10 passed), strategy services+facade (1230 passed), order/build_queue serialization (152 passed).

### Task 3.3: Type the IAbilitySource.source_kind discriminator [Medium]
**File:** `game/core/protocols/strategy_entities.py`
**Pattern:** #29 (Universal Ability Source)
**Tests:** `pytest tests/ --testmon` + type check (`mypy`/`pyright` per project config)

- [x] Added `SourceKind(StrEnum)` with the 7 members to `game/core/protocols/strategy_entities.py`; changed `IAbilitySource.source_kind` annotation `-> str` → `-> SourceKind`. Exported `SourceKind` from `game.core.protocols`. (Chose StrEnum over Literal so existing raw-string consumers `== 'storm'` / `!= 'star'` / f-strings + the collector payload keep working unchanged — see decisions.md.)
- [x] Updated all 7 adapters in `game/strategy/services/ability_sources/` (facility, fleet, planet_intrinsic, star, storm, system_archetype, warp_point) to return typed `SourceKind` members.
- [x] Verify: `test_source_kind_enum.py` pins StrEnum-ness, the 7 members, string-compat, and adapter usage. 119 protocols+adapters tests green; full strategy services+facade suites green (1230 passed).

### Task 3.4: Reconcile Pattern #32 and #36 doc-drift [Simple]
**File:** `docs/02_PATTERNS.md`
**Pattern:** #32 (Compositional Construction), #36 (Re-Export Shim)
**Tests:** N/A (doc-only)

- [x] Pattern #32: added an adoption note (single current production consumer is `StrategyScreen`; the "three or more collaborators" line is the adoption threshold, not an adopter count) (DOC-032)
- [x] Pattern #36: updated line ref `395-405` → `392-405` (block header at 392, `from...import(...)` 395-405) to match `component.py` (DOC-036; verified live)
- [x] Verify: doc line references match live code

### Task 3.5: LOC ceiling triage (top-10 prioritization) [Medium] — OUT OF SCOPE
**File:** `game/simulation/battle_state.py` (et al.)
**Pattern:** n/a (LOC ceiling is a `game/`-only convention, not tied to a pattern)
**Status:** OUT OF SCOPE — deferred to a future decomposition project.

> **SCOPE REVISION 2026-05-20 (Protocol 06):** The broad LOC-ceiling triage program (splitting the
> ten 600+ LOC god-modules + the remaining ~59 files) is a maintainability decomposition program,
> not a pattern-conformance fix. Splitting each file requires independent responsibility analysis
> and per-file behavior-preservation tests — out of place in a conformance pass. Logged via
> discovered-issues for folding into a future decomposition project. No LOC split is performed
> under PROJ-470 (the surviving conformance fixes are all localized and stay well under 500 LOC).

- [x] LOC triage program declared OUT OF SCOPE; recorded in decisions.md and logged as a discovered issue. No splits performed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes resolved (TG-001/002/004 KEPT with rationale; TG-003 swapped; ENUM-001 + doc-drift done; LOC OUT OF SCOPE)
- [x] Status set to `Complete`
- [x] plan.md phase table row updated
- [x] plan.md Current State updated

_Source audit: `Reviews/results/2026-05-20_075227_pattern-audit/`. See `findings/source_audit.md` for the link._
