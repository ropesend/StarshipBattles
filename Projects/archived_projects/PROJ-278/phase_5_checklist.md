# Phase 5: Cache invalidation hooks for runtime role additions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-278 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18)
**Objective:** Originally framed as "wire invalidation callbacks for every subsystem that caches role-derived data" — but the audit (Task 5.1) found **zero current cachers**. Phase 5 is therefore reframed: prove the invalidation infrastructure works end-to-end via a smoke test, document the authoring rule for future cachers, and capture future opportunities (e.g. data-driving the `_DESIGN_ROLE_TO_ARCHETYPE` table).

---

## Audit Findings (Task 5.1)

| Candidate from Phase 4 hand-off | Audit result | Action needed |
|---|---|---|
| `game/simulation/combat/formation.py::_DESIGN_ROLE_TO_ARCHETYPE` | Hardcoded module-level dict, NOT a cache. Unknown roles gracefully fall back to `LINE_ABREAST`. | None today. Future opportunity: data-drive via a `formation_archetype` field on `Role`. |
| `game/ai/policy_manager.py` and `game/ai/` | Zero references to `design_role` — combat AI doesn't consume role at all. | None. (`design_role` is gameplay/UI grouping, not combat.) |
| `game/strategy/systems/design_library.py::filter_designs` | In-line list comprehension filter on `design_role` parameter. No role-keyed cache. | None. |
| `game/strategy/data/ship_instance.py`, `design_metadata.py` | Store `design_role` as fields. No derived data cached. | None. |
| `game/strategy/facade/dto/` | DTOs pass through `design_role` as a string field. No caching. | None. |
| Combat Lab `combat_lab_role_registry` | `allow_runtime_add=False` — registry rejects mutation. Invalidation N/A. | None. |

**Conclusion:** No code today caches role-derived data. The invalidation API (`register_invalidation_callback`) ships from Phase 1 ready for future use. Phase 5 establishes the authoring contract so future cachers honour it.

---

## Tasks

### Task 5.1: Audit candidate subsystems for role caching [Simple]
**File:** This checklist (audit table above)
**Tests:** N/A

- [x] Grep `design_role` across `game/` to enumerate consumers
- [x] For each consumer: classify as (a) static data table, (b) per-call computation, (c) cached derived data
- [x] Document findings in the table above

**Notes:** Audit revealed scope was much smaller than originally framed. Surprise finding: `game/ai/` has zero `design_role` references — combat AI literally doesn't consume the field, which makes sense given the [game/strategy/data/design_role.py](../../../game/strategy/data/design_role.py) docstring's note: "they do NOT directly affect combat behavior."

### Task 5.2: Add end-to-end invalidation smoke test [Medium]
**File:** `tests/unit/strategy/data/test_design_role_registry_invalidation.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_design_role_registry_invalidation.py`

- [x] Built `_FakeRoleArchetypeCache` worked-example class (lazy-populate cache + invalidation callback)
- [x] Test: cacher receives callback on `add_user_role`
- [x] Test: cacher picks up new role after invalidation
- [x] Test: multiple reads share one population (cache survives reads)
- [x] Test: each add fires exactly one invalidation
- [x] Test: multiple cachers registered against same registry are all invalidated independently
- [x] All 5 tests pass

**Notes:** The fake cacher is structured to mirror what a future data-driven `_DESIGN_ROLE_TO_ARCHETYPE` would look like — future implementer can copy-paste-modify the pattern.

### Task 5.3: Document authoring rule for future cachers [Simple]
**File:** `docs/systems/strategy_layer.md` (Design Roles section)
**Tests:** N/A

- [x] Added "Authoring rule for new role-derived caches (PROJ-278 Phase 5)" subsection right after "Runtime add"
- [x] Cross-referenced the smoke test as the worked example
- [x] Included the audit-finding callout (zero current cachers) so future readers understand the contract is forward-looking
- [x] Removed the older "Subsystems caching role-derived data (formation defaults, AI behavior dispatch) should call..." sentence since the audit proved neither subsystem actually caches

**Notes:** Doc edit was scoped to the existing "Runtime add" paragraph in [docs/systems/strategy_layer.md](../../../docs/systems/strategy_layer.md) — the new authoring-rule subsection sits right beneath it so future readers find both pieces together. Audit-finding callout uses a blockquote so it's visually distinct from the prescriptive rule above it.

### Task 5.4: Capture future opportunities [Simple]
**File:** This checklist + plan.md Current State
**Tests:** N/A

- [x] **Data-drive `_DESIGN_ROLE_TO_ARCHETYPE`:** add an optional `formation_archetype: Optional[str]` field to `Role`. Move the mapping from a hardcoded Python dict into the JSON data file. Then `resolve_default_for_task_force` consults the registry, picks up player-added roles' archetypes for free, and registers an invalidation callback to drop any per-archetype cache.
- [x] **DesignLibrary role-filter caching:** if UI dropdowns become slow at scale, `filter_designs(design_role=...)` can cache filtered lists per role. This would be the first real cache-with-invalidation use case.
- [x] Documented these in plan.md Current State for the Phase 6 / future-work agent

**Notes:** Both opportunities are explicitly OUT OF SCOPE for PROJ-278 — they're independent feature projects that would benefit from the invalidation infrastructure now in place.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/core/` still green (Phase 1)
- [x] `pytest tests/unit/strategy/data/test_design_role_registry*.py tests/unit/strategy/data/test_design_role_registry_invalidation.py` green (Phase 2 + 5)
- [x] `pytest tests/unit/combat_lab/` still green (Phase 3 + 4)
- [x] Targeted regression sweep: 1330 passed (1325 from Phase 3 baseline + 5 new invalidation tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6 (final docs + project closure)
