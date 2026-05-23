# PROJ-497: Decisions Log

> **LOG ALL DECISIONS HERE**
> When the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-23 | Project initialized | Carved out of PROJ-489 audit follow-up. See `findings/source_review.md`. |
| 2026-05-23 | Split data-intent (PROJ-497) from engineering hardening (PROJ-498) | Codex consult (`AgentCoordination/Scratchpad/Consult/20260523T120100Z_plan-PROJ-489-blast-radius/response.md`) recommended split because PROJ-498's rejection-matrix test should encode the *chosen* truth, not today's accidental truth. PROJ-497 runs first. |
| 2026-05-23 | Data-edit phase is BLOCKED on user decisions | Each of the three smells (efficient_engines, mini_capital_missile, facing/turret_mount seeker allowance) is a genuine design call, not a foregone fix. Agents must not unilaterally pick. Decision space recorded in `plan.md` "User Decision Points". |
| 2026-05-23 | Codex/Claude agreement: `efficient_engines` is doubly broken | Both agree allow_abilities namespace is wrong (0 valid targets) AND `consumption_mult: -0.2` against default `multiply` operation would drive consumption negative if reachable. See Codex response and `game/simulation/components/modifiers.py:18-48`. |
| 2026-05-23 | New insight from Codex: allowed-implies-mandatory coupling | `get_mandatory_modifiers()` returns every allowed modifier and `ShipComponentManager.ensure_mandatory_modifiers()` auto-applies on add (`game/simulation/services/modifier_service.py:108-125,222-234`; `game/simulation/entities/ship_component_manager.py:72-80`). Any allowlist broadening also broadens auto-application surface. This raises the stakes of option (b) for `efficient_engines` and any seeker-allowance edit. |
| 2026-05-23 | Mid-project review (Codex): `mini_capital_missile` retype Task 2.2 was incomplete | Original wording said "change `type` field" only. The live allowance service keys on `component.abilities` payload keys, NOT on `type`. A type-only edit is a no-op for `is_modifier_allowed()`. Task 2.2 updated to require explicit decision on type vs ability-payload vs both, and per-pair user approval for newly-allowed seeker_* modifiers. See `AgentCoordination/Scratchpad/Consult/20260523T120300Z_mpr-PROJ-497-498/response.md` Q1/Q4. |
| 2026-05-23 | Static-scan script corrected: `deny_abilities` is NOT enforced by live service | Original scan in `findings/source_review.md` applied `deny_abilities` filter, undercounting `hardened_mount` as 162 valid. Live count is 169. PROJ-498's matrix test will be false-red on 7 armor components if it copies the original scan. Findings doc updated with canonical-rule warning. See Codex MPR Q2. |

## Pending user decisions

1. **`efficient_engines`** — see plan.md Section "User Decision Points" item 1.
2. **`mini_capital_missile` type** — see plan.md Section "User Decision Points" item 2.
3. **`facing`/`turret_mount` seeker allowance** — see plan.md Section "User Decision Points" item 3.

Record the chosen option, date, and rationale in the table above when the user answers.
