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
| 2. design_role migration to RoleRegistry (mods + user overlay, runtime add) | Not Started | TBD |
| 3. Combat Lab scenario_role migration (typed, file-driven) | Not Started | TBD |
| 4. ShipSpec field separation (design_role + scenario_role) | Not Started | TBD |
| 5. Cache invalidation hooks for runtime additions | Not Started | TBD |
| 6. Documentation + tests | Not Started | TBD |

## Current State
**Last Updated:** 2026-04-17
**Active Phase:** Phase 2 (ready to start) — design_role migration to RoleRegistry
**Last Action:** Phase 1 complete — `Role` dataclass + `RoleRegistry` class shipped in [game/core/roles.py](../../../game/core/roles.py) with 30 passing tests (10 Role + 20 RoleRegistry covering empty / loading / runtime add / invalidation). Re-exports added to [game/core/__init__.py](../../../game/core/__init__.py); [docs/01_ARCHITECTURE.md](../../../docs/01_ARCHITECTURE.md) updated (export count 42→45, package map row added). Full `tests/unit/core/` suite (990 tests) green. No production callers wired — pure infrastructure delivered.
**Next Action:** Phase 2 — write Phase 2 checklist, then migrate `data/design_roles.json` from existing `{"roles": {id: {...}}}` shape to new `{"roles": [{...}]}` shape (or update RoleRegistry loader to consume the existing shape — decide in Phase 2 design). Wire `design_role_registry` into `ApplicationContext` with layered loading (`data/design_roles.json` + `mods/*/design_roles.json` + `user_data/design_roles.json`). Replace existing `DesignRoleRegistry` callers with `design_role_registry`.
**Blockers:** None
**Context for Next Agent:**
- Phase 1 chose JSON shape `{"roles": [{...}, ...]}` (list of dicts). Existing `data/design_roles.json` uses `{"roles": {id: {...}}}` (dict keyed by id) with field names `name`/`allowed_vehicle_types`. Two options for Phase 2: (a) port the data file to the new shape OR (b) extend `RoleRegistry._role_from_dict` to accept both shapes. Recommend (a) — clean migration, no permanent loader complexity
- `RoleRegistry.load_from_file` uses `load_json_required` (raises on missing/malformed). For the user-overlay path (`user_data/design_roles.json`) which won't exist on first run, Phase 2 should add a tolerant `load_from_file_optional` variant OR check existence before calling
- Cache invalidation callbacks are wired to fire on `add_user_role`. Phase 5 will identify the actual subsystems that need to register callbacks (formation defaults, AI policy manager). Phase 2 just needs to ensure `design_role_registry` is the single source consulted everywhere
- Decision pending: keep legacy `DesignRoleRegistry` class as a thin wrapper around `RoleRegistry` or delete it entirely and migrate all 28 call sites — recommend deletion per the eradicate-old-systems policy

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
