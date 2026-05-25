# PROJ-498: Source Review

## Provenance
- Parent project: PROJ-489 (ModifierService consolidation)
- Parent audit verification: `Projects/active_projects/PROJ-489/findings/audit_verification.md`
- Codex audit consult: `AgentCoordination/Scratchpad/Consult/20260523T120008Z_audit-PROJ-489/response.md`
- Codex planning consult (split into 497/498): `AgentCoordination/Scratchpad/Consult/20260523T120100Z_plan-PROJ-489-blast-radius/response.md`
- Sibling project: **PROJ-497 (data-intent decisions; MUST close before PROJ-498 starts Phase 3)**

## Background

PROJ-489 closed a long-standing bug where `ModifierManager.add_modifier` silently bypassed the `allow_abilities` check. The canonical `ModifierService` now correctly returns False on disallowed pairs from all five `Component.add_modifier()` production callers. Two of those callers (save-restore paths) silently drop rejected modifiers today, with no log. Test coverage for the rejection paths is thin: 7 re-shot snapshots out of ~580 theoretical mismatch pairs.

## Production callers of `Component.add_modifier()`

| Site | Behavior on rejection today | This project's action |
|------|-----------------------------|------------------------|
| `game/simulation/components/component.py:328-333` | Returns False (the method itself) | None — keep contract |
| `game/simulation/battle_state.py:274-280` | **Silently drops** rejected mods on battle save restore | **Add `logger.warning` (Phase 2)** |
| `game/simulation/entities/ship_serialization.py:223-228` | Logs unknown-id; does NOT log allow_abilities rejection | **Add `logger.warning` (Phase 2)** |
| `game/simulation/services/modifier_service.py:222-234` (`ensure_mandatory_modifiers`) | Service-internal contradiction if a "mandatory" modifier is rejected; skipped silently | Out of scope this project (Decision: defer) |
| `game/ui/panels/builder_widgets.py:256` + `game/ui/screens/builder/interaction_controller.py:98` | UI surfaces rejection in builder | Out of scope (UI already covers) |

## Existing allowance API

`game/simulation/services/modifier_service.py` currently exposes `is_modifier_allowed(component, modifier_id) -> bool`. A bare bool conflates four rejection reasons:
- Unknown modifier id
- Component type not in `allow_types`
- Component type in `deny_types`
- Component abilities not matching `allow_abilities`
- Component abilities matching `deny_abilities`

PROJ-498 adds `check_allowance() -> AllowanceResult` to make save-restore logs diagnostic. Existing `is_modifier_allowed()` becomes a thin delegating wrapper, preserving contract.

## Allowed-implies-mandatory coupling

`get_mandatory_modifiers()` returns every allowed modifier; `ShipComponentManager.add_component()` auto-runs `ensure_mandatory_modifiers()`. This is why PROJ-497 must run first: any allowlist edit in PROJ-497 changes the auto-application surface PROJ-498's matrix test asserts. See `game/simulation/services/modifier_service.py:108-125,222-234`; `game/simulation/entities/ship_component_manager.py:72-80`.

## Snapshot harness caveat (informational)

`tests/regression/modifier_ability_snapshots/conftest.py:147-173` iterates only expected JSON keys, so the snapshot comparator silently ignores extra keys in actual output. This is unrelated to PROJ-498 but it is the reason the matrix test is *parametrized* rather than per-rejected-pair snapshot.

## Out-of-scope artifacts logged separately

- Snapshot comparator extra-keys-strict mode — pre-existing, separate triage if user wants it.
- `mini_capital_missile` type quirk — out of scope (handled in PROJ-497).
- `efficient_engines` data bug — out of scope (handled in PROJ-497).
- Save-file migration for old saves containing now-rejected modifiers — explicit anti-pattern per CLAUDE.md "no save-file migrations".

## PROJ-497 outcomes

Filed by PROJ-497 Phase 3 Task 3.3 on 2026-05-23. Full decisions log:
`Projects/active_projects/PROJ-497/decisions.md`.

**Final data surface relevant to PROJ-498's rejection-matrix test:**

| Row | Action taken in PROJ-497 | Effect on PROJ-498 matrix |
|-----|---------------------------|---------------------------|
| `efficient_engines` (modifier) | Decision 1 = DELETE (user reversed an earlier REDESIGN choice on 2026-05-23 with rationale: "too specific to a specific type of component/ability"). The modifier row was removed from `data/modifiers.json`. Stale icon-map entry in `game/ui/services/modifier_icon_service.py:30` also removed. DI-2026-05-23-004 pruned. | The modifier no longer exists in the live registry, so PROJ-498's matrix test simply will not generate any `(efficient_engines, *)` pairs. Nothing to plan around. The recommendation to derive expected pairs from live data (rather than from a hard-coded list at PROJ-489 audit time) still stands as good defensive practice. |
| `mini_capital_missile` (component) | Decision 2 = RETYPE. Edited BOTH the `type` field (`BeamWeaponAbility` -> `SeekerWeaponAbility`) AND the ability-payload key (`abilities.BeamWeaponAbility` removed, `abilities.SeekerWeaponAbility` added with seeker-shaped payload mirroring `capital_missile`). | Cascade: `seeker_endurance/damage/armored/stealth` each gain `mini_capital_missile` (1 -> 2). `range_mount` loses it (6 -> 5). `precision_mount` loses it (5 -> 4). `turret_mount`, `facing`, `rapid_fire` unchanged. PROJ-498's matrix test, if derived from live data at collection time, will pick up the cascade automatically. |
| `facing` and `turret_mount` (modifiers) | Decision 3 = KEEP `SeekerWeaponAbility` in `allow_abilities`. Documented as intentional. User clarified semantics: seekers do honor firing-arc/facing for **launch direction**, but ignore arc for **target acquisition**. | No data edit. PROJ-498's matrix test should NOT mark `(facing, seeker)` or `(turret_mount, seeker)` as expected-reject pairs. The doc claim in `docs/systems/ability_reference.md:287` ("seekers ignore firing arc") is ambiguous and may benefit from a future doc clarification (out of PROJ-497 scope). |
| Override pairs (PROJ-498 pre-question) | Decision 4 = NONE. User pre-confirmed no override pairs for PROJ-498. | PROJ-498 may skip its "override pairs" follow-up question. |

**PROJ-499 coordination:** PROJ-497 Phase 2 did NOT pre-empt PROJ-499's bulk
snapshot re-shoot. No snapshots under `tests/regression/snapshots/` were
re-shot because (a) no existing snapshot references `mini_capital_missile`,
and (b) no existing snapshot referenced `efficient_engines`.

**Open follow-up that affects PROJ-498:** None. All three PROJ-497 data
decisions are final and applied. PROJ-498 may proceed with its rejection-
matrix work against the live `data/modifiers.json` + `data/components.json`
surface as of 2026-05-23.
