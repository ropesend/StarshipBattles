# PROJ-278: Unified Role Registry (design_role + Combat Lab scenario_role)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-278` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-278 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Shared Role schema + RoleRegistry machinery | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. design_role migration to RoleRegistry (mods + user overlay, runtime add) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Combat Lab scenario_role registry (data + machinery + consistency test) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. ShipSpec.scenario_role field — delete substring parsing | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Cache invalidation hooks (audit + smoke test + authoring rule) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Project closure (full suite + docs verify + memory + archive) | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Archived
**Last Action:** Closure audit (5 skeptical agents) ran; user approved fixing 4 worth-fixing items before archival. Applied: re-entrance guard on `RoleRegistry._fire_invalidation_callbacks`; 3 missing-required-field tests; 2 missing-`roles`-key tests; 3 mod-layer tests. Test count rose 66 → 75. Two impl findings deferred with rationale (race condition matches codebase pattern; identical-role callback is by-design). Final regression: 4692 tests across PROJ-278 scope, all green. Archived to `Projects/archived_projects/PROJ-278/`.
**Next Action:** None — project closed.
**Blockers:** None

---

## Closure Summary

### Project arc (2026-04-17 → 2026-04-18)
- **Goal achieved:** Replaced two ad-hoc role concepts with one shared `Role` schema + `RoleRegistry` machinery. Made gameplay `design_role` runtime-extensible via layered loading (base + mods + user overlay) so players can add roles during play. Replaced fragile `instance_id` substring parsing in Combat Lab with a typed `ShipSpec.scenario_role` field.
- **6 phases, all complete and validated.**

### What shipped

**New modules:**
- [game/core/roles.py](../../../game/core/roles.py) — `Role` frozen dataclass + `RoleRegistry` class + `RoleRegistryReadOnlyError`. Layered loading via `load_from_file` / `load_from_file_optional`. Runtime mutation via `add_user_role` (gated by `allow_runtime_add`). Invalidation callbacks via `register_invalidation_callback`.
- [game/strategy/data/design_role_registry.py](../../../game/strategy/data/design_role_registry.py) — module-level accessor for the gameplay design_role registry. Layered: `data/design_roles.json` (base) → `mods/*/design_roles.json` (optional dir) → `output/design_roles_overlay.json` (user overlay). `allow_runtime_add=True`.
- [combat_lab/scenario_role_registry.py](../../../combat_lab/scenario_role_registry.py) — module-level accessor for the Combat Lab scenario_role registry. Static, single-file, `allow_runtime_add=False` (calling `add_user_role` raises `RoleRegistryReadOnlyError`).

**Schema changes:**
- `ShipSpec.scenario_role: Optional[str]` field (PROJ-278 Phase 4) — typed wiring label for Combat Lab scenarios; `None` for Battle Setup / Strategy specs.

**Data files:**
- [data/design_roles.json](../../../data/design_roles.json) — ported to new shape (`{"roles": [{...}, ...]}`, fields: `id` / `display_name` / `description` / `vehicle_type_filter`). 27 roles preserved.
- [combat_lab/data/scenario_roles.json](../../../combat_lab/data/scenario_roles.json) — NEW. 14 roles covering every literal label used by Combat Lab templates.

**Path constants added** ([game/core/paths.py](../../../game/core/paths.py)):
- `Paths.MODS_DIR` (= `mods/` at project root)
- `Paths.USER_DESIGN_ROLES_FILE` (= `output/design_roles_overlay.json`)

**Deleted:**
- `DesignRoleRegistry` class + `get_default_design_role_registry()` singleton from [game/strategy/data/design_role.py](../../../game/strategy/data/design_role.py). The `DesignRole` enum + `classify_design_role` + `classify_from_design_data` remain.
- `_role_from_instance_id` substring parser from [combat_lab/runner.py](../../../combat_lab/runner.py).
- `instance_id`-rsplit logic in [game/simulation/battle_runner.py::materialize_spec_ships](../../../game/simulation/battle_runner.py).

**Migrated:**
- 3 production call sites of legacy `DesignRoleRegistry`: `design_selector_window.py`, `right_panel.py`, `workshop_event_router.py`.
- 1 existing test file `tests/unit/strategy/data/test_design_role_registry.py` (225 lines) migrated to new API.
- 8 test assertions in `test_spec_compiler.py` migrated from `instance_id.endswith(":role")` to `scenario_role == "role"`.
- Combat Lab `_ship_spec` helper + 3 custom `ShipSpec` construction sites populate `scenario_role`.

**Tests added:**
- `tests/unit/core/test_role.py` — 10 tests
- `tests/unit/core/test_role_registry.py` — 29 tests (loading, runtime add, invalidation, query methods)
- `tests/unit/strategy/data/test_design_role_registry_loader.py` — 12 tests (accessor + production data smoke + layered loading)
- `tests/unit/combat_lab/test_scenario_role_registry.py` — 8 tests (read-only enforcement, expected roles)
- `tests/unit/combat_lab/test_scenario_roles_consistency.py` — 2 tests (AST scanner catches typos)
- `tests/unit/strategy/data/test_design_role_registry_invalidation.py` — 5 tests (worked-example invalidation pattern)
- **Total: 66 new tests.**

**Two-layer protection against role-label typos:**
- **Compile time:** Combat Lab spec compiler validates every `scenario_role` value against `combat_lab_role_registry` → raises `ValueError` with helpful message.
- **Test time:** AST scanner walks `combat_lab/scenarios/*.py` for literal `ships_by_role[<str>]` references → fails CI if any label is unregistered.

### Tests (final)
- **PROJ-278 suite:** 66 tests, all green.
- **Full sharded suite:** 14745 tests, 14744 passed, 1 unrelated pre-existing failure (`test_quickstart_builder.py` — Federation/Klingons theme assertion, untouched by PROJ-278).
- **Combat Lab simulation suite:** 162 / 162 passed.

### Docs updated
- [docs/01_ARCHITECTURE.md](../../../docs/01_ARCHITECTURE.md) — `roles.py` row, export count 42→45, `Roles (PROJ-278)` exports entry, `design_role.py` + `design_role_registry.py` mention in `game/strategy/data/` row.
- [docs/03_CONVENTIONS.md](../../../docs/03_CONVENTIONS.md) — `data/design_roles.json` row (27 roles, new loader module reference).
- [docs/systems/strategy_layer.md](../../../docs/systems/strategy_layer.md) — Design Roles section fully rewritten; layered loading; runtime add; new RoleRegistry API; reverse-lookup pattern; **authoring rule for new role-derived caches** (Phase 5).
- [docs/systems/combat_simulation.md](../../../docs/systems/combat_simulation.md) — Combat Lab Scenario Role Tagging section added.
- [docs/guides/simulation_testing.md](../../../docs/guides/simulation_testing.md) — §"2.5 Scenario Role Labels" added; directory tree updated.

### Future opportunities (NOT in scope for PROJ-278)
1. **Data-drive `_DESIGN_ROLE_TO_ARCHETYPE`:** add `formation_archetype: Optional[str]` field to `Role`. Move the mapping into `data/design_roles.json`. `resolve_default_for_task_force` consults the registry directly → player-added roles participate in formation defaults instead of falling back to LINE_ABREAST. Would be the first real cache-with-invalidation use case.
2. **DesignLibrary role-filter caching:** if UI dropdowns become slow at scale, cache filtered-by-role lists. Same invalidation infrastructure applies.
3. **UI for player runtime-add:** explicitly excluded from PROJ-278 scope by user. Data model is ready; UI is its own project.

### What I'd watch for in the next sprint
- The `test_quickstart_builder.py` failure should be triaged — it's not mine but it's a real failure in unrelated code.
- The two future-opportunity projects above are natural follow-ups when player-add UI is built.

---

## Pre-Closure Verification
- [x] All 5 implementation phases complete + validated (`validate_phase.py PROJ-278 N` PASSED for N=1..5)
- [x] Phase 6 complete + validated (`validate_phase.py` and `validate_close_ready.py` both PASSED)
- [x] Full sharded suite: zero PROJ-278-introduced failures
- [x] All 5 affected docs verified to contain PROJ-278 references
- [x] MEMORY.md captures complete project summary
- [x] User approval to archive: pending

## Overview
Replace the two separate "role" concepts in the codebase with one shared `Role` schema and `RoleRegistry` machinery. Two registry instances are loaded from separate files: `data/design_roles.json` (gameplay archetypes — used by AI behavior, formation defaults, design-library filtering) and `combat_lab/data/scenario_roles.json` (Combat Lab scenario wiring labels). Make `design_role` runtime-extensible via a layered file model (base + mods + user overlay) so players can add roles during play and modders can override them. Replace fragile `instance_id` substring parsing for Combat Lab role wiring with a typed `scenario_role` field on `ShipSpec`.

## Goals
- One `Role` dataclass + one `RoleRegistry` class shared by both contexts
- `design_role` registry: layered storage (base + mods + user overlay), runtime `add_user_role()`, cache invalidation on add
- Combat Lab `scenario_role` registry: file-driven (`combat_lab/data/scenario_roles.json`), static (no runtime add)
- `ShipSpec` carries two distinct fields: `design_role: Optional[str]` and `scenario_role: Optional[str]`
- Delete `_role_from_instance_id` substring parsing in Combat Lab runner
- Document precedence rules (base < mods < user) and the modding contract

## Scope
**In:**
- New module `game/core/roles.py` defining `Role` dataclass and `RoleRegistry` class
- Refactor `game/strategy/data/design_role.py::DesignRoleRegistry` to use `RoleRegistry`
- Layered loading for design_role: `data/design_roles.json` + `mods/*/design_roles.json` (mod system out of scope but loader supports the directory) + `user_data/design_roles.json` (player additions persisted here)
- Add `scenario_role` field to `ShipSpec`; populate from each Combat Lab template
- Remove `_role_from_instance_id` and any `instance_id`-string-parsing for role purposes
- Combat Lab `combat_lab/data/scenario_roles.json` shipping with initial roles: `attacker`, `target`, `ship1`, `ship2` (plus any other current ones discovered in templates)
- Cache invalidation contract for any subsystem that caches `design_role` lookups (formation defaults, AI behavior dispatch)
- Tests covering registry layering, runtime add, cache invalidation, ShipSpec round-trip
- Documentation update in [docs/01_ARCHITECTURE.md](../../../docs/01_ARCHITECTURE.md) and [docs/systems/strategy_layer.md](../../../docs/systems/strategy_layer.md)

**Out:**
- The UI for players to add roles at runtime (data model only — UI is a future project)
- Full mod system implementation (loader supports the directory but loose-file mod resolution is a future project)
- Migrating other "role-like" string fields anywhere else in the codebase

## Key Files
| Component | File Path |
|-----------|-----------|
| Existing DesignRoleRegistry | `game/strategy/data/design_role.py` |
| Existing design_role data | `data/design_roles.json` |
| New shared registry | `game/core/roles.py` (NEW) |
| Combat Lab role data | `combat_lab/data/scenario_roles.json` (NEW) |
| ShipSpec | `game/simulation/battle_spec.py` |
| Combat Lab spec compiler (uses roles) | `combat_lab/spec_compiler.py` |
| Combat Lab runner (substring parsing) | `combat_lab/runner.py` |
| Combat Lab templates (consume roles) | `combat_lab/scenarios/templates.py`, `combat_lab/scenarios/base.py` |
| AI behavior dispatch (caches design_role) | `game/ai/policy_manager.py` |
| Formation defaults (consults design_role) | `game/simulation/combat/formation.py` |
| User overlay file (NEW at runtime) | `user_data/design_roles.json` |

## Decisions Log
See [decisions.md](decisions.md) for full rationale.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Unify the machinery (one `Role` schema + one `RoleRegistry` class), not the instances | Combat Lab and gameplay roles serve different purposes (positional vs descriptive) — sharing the schema is a clean win, sharing instances would conflate two concerns |
| 2026-04-17 | Combat Lab loads its own roles file (`combat_lab/data/scenario_roles.json`) | Matches existing Combat Lab pattern of owning its own components.json + ship JSONs |
| 2026-04-17 | `design_role` storage = base data file + mod overlays + user overlay file | Players want runtime-add now; same machinery serves modding later. User answered: "Mods are made by altering the base .json files" + user-overlay file |
| 2026-04-17 | Two separate fields on ShipSpec: `design_role` and `scenario_role` | A ship's gameplay role is intrinsic and persistent; its scenario role is positional and ephemeral. One field would conflate the two |
| 2026-04-17 | Combat Lab `scenario_role` registry is static (no runtime add API) | Players don't write Combat Lab scenarios; runtime add is meaningless there. Same `RoleRegistry` class, but the Combat Lab instance simply doesn't expose the mutation method (or raises) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
