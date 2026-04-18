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
| 6. Project closure (final docs polish + audit pass + close) | Not Started | TBD |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Phase 6 (ready to start) — project closure
**Last Action:** Phase 5 complete. Audit revealed zero subsystems currently cache `design_role`-derived data — `_DESIGN_ROLE_TO_ARCHETYPE` in `formation.py` is a hardcoded dict (not a cache); `game/ai/` doesn't reference design_role at all; `DesignLibrary.filter_designs` filters in-line; ShipInstance/DesignMetadata/DTOs just pass-through the field. Phase 5 reframed accordingly: shipped end-to-end smoke test [test_design_role_registry_invalidation.py](../../../tests/unit/strategy/data/test_design_role_registry_invalidation.py) (5 tests with worked-example `_FakeRoleArchetypeCache` for future implementers), documented authoring rule in [docs/systems/strategy_layer.md](../../../docs/systems/strategy_layer.md) Design Roles section. Targeted regression: 1330 passed across PROJ-278 test scope.
**Next Action:** Begin Phase 6 — final project closure. Run full sharded test suite, audit pass, run `validate_close_ready.py`, write closure summary in plan.md, archive the project.
**Blockers:** None
**Context for Next Agent:**
- All 5 implementation phases are complete and validated; Phase 6 is closure-only (no new code)
- Phase 5 captured two FUTURE OPPORTUNITIES that should become their own projects after PROJ-278 closes:
  1. **Data-drive `_DESIGN_ROLE_TO_ARCHETYPE`:** add `formation_archetype: Optional[str]` field to `Role` schema; move the mapping into `data/design_roles.json`; have `resolve_default_for_task_force` consult the registry directly. Player-added roles would then participate in formation defaults instead of falling back to LINE_ABREAST. Would be the first real cache-with-invalidation use case.
  2. **DesignLibrary role-filter caching:** if UI dropdowns become slow at scale, cache filtered-by-role lists. Same invalidation infrastructure applies.
- Phase 6 should:
  - Run full sharded test suite to capture absolute baseline (compare to memory's 14685/14686)
  - Audit each phase deliverable against acceptance criteria
  - Update PROJ-278 entry in MEMORY.md with final summary
  - Move project to archived state if user approves
- Pre-existing baseline: `test_galaxy_cleanup.py` has 78 unrelated failures. Skip in regression checks

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
