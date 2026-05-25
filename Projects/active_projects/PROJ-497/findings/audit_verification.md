# PROJ-497 Audit Verification

Source: `AgentCoordination/Scratchpad/Consult/20260523T150131Z_audit-PROJ-497/response.md`
Auditor: codex (claude-consult, mid-project-review)
Verifier: claude (orchestrator)
Date: 2026-05-23

| ID | Verdict | Evidence | Action |
|----|---------|----------|--------|
| F1 — `mini_capital_missile` retype changes effective range 200 → 14400 | VERIFIED + IN-SCOPE | New payload at `data/components.json:1074-1081` omits `range`; `game/simulation/components/abilities/weapons.py:371-373` defaults range to `int(projectile_speed * endurance * 0.8) = 14400`. Original beam payload (per git diff) had `range: 200`. Plan goal: "Apply only the edits the user approves." User approved retype; did not explicitly approve 72× range jump. **Mitigating context**: standard `capital_missile` at `data/components.json:732-762` uses the SAME implicit seeker default (no `range` field, identical `projectile_speed=6000, endurance=3.0`). The implementer's design mirrors the parent capital missile structurally (mini = fighter-portable version, same range model, lower damage/longer reload). Choice is internally consistent but warrants user confirmation. | Surface to user; remediate based on response. |
| F2 — Pair-cascade matches decisions.md exactly | VERIFIED + NO ACTION | Codex's live-rule diff against main produced exactly: +mini_capital_missile to seeker_endurance/damage/armored/stealth, -from range_mount/precision_mount, unchanged for turret_mount/facing/rapid_fire. Matches `decisions.md:18-20` and `data/modifiers.json:160-195, 199-221, 250-253, 282-288, 316-414`. | No action; clean. |
| F3 — No layer-boundary or convention violations in touched code | VERIFIED + NO ACTION | Only non-data production edit is the dead UI key removal at `game/ui/services/modifier_icon_service.py:25-30`, consistent with data delete. No layer violations per docs/01-03. | No action; clean. |
| F4 — `efficient_engines` cleanup complete | VERIFIED + NO ACTION | Modifier row gone; UI map entry gone; `rg -n 'efficient_engines' game tests/regression data/designs` returns 0 matches. DI-2026-05-23-004 pruned. Remaining mentions only in project-history docs. | No action; clean. |
| F5 — Stale doc claim "seekers ignore firing arc" at `docs/systems/ability_reference.md:287` | VERIFIED + OUT-OF-SCOPE | Decision 3 (`decisions.md:20`) clarifies seekers honor launch-direction arc but ignore targeting arc. The doc still says "seekers ignore firing arc" unqualified. Implementer's decisions.md explicitly deferred doc-edit to a future doc PR. Per plan.md scope, docs/systems/ is not in the project's listed file scope. | Log DI for future doc-clarification. |
| F6 — Live data still carries inert `"Weapon"` tokens in `turret_mount` and `rapid_fire` allow_abilities | VERIFIED + OUT-OF-SCOPE | `data/modifiers.json:57-62` (turret_mount) and `:283-288` (rapid_fire) include `"Weapon"` (a component `type` field, not an `ability` key — same broken namespace pattern as efficient_engines had). However, both rows ALSO include the actual ability keys (ProjectileWeaponAbility, BeamWeaponAbility, SeekerWeaponAbility), so the rows function correctly via those tokens. The `"Weapon"` token is dead data, cosmetic-only. User wasn't asked about these. Plan's user-decision points were specific to 3 rows; this is a 4th/5th. | Log DI; future cleanup project. |
| R1 — Range/firing-model shift not locked by tests | Same as F1 | (Same finding from a different angle.) | Addressed by F1 remediation. |
| R2 — Pair-membership test doesn't lock global counts | VERIFIED + NO ACTION | `tests/unit/validation/test_proj497_mini_capital_missile_retype.py:153-180` asserts membership not counts. Defensible test design — counts can drift legitimately when other modifiers grow/shrink. | No action; matches reasonable test conventions. |
| R3 — `Projects/projects_index.md:8` still lists PROJ-497 as `Planning` | VERIFIED + IN-SCOPE | Project meta drift; implementer noted "index update is the orchestrator's call when actually closing." Trivial fix. | Include in remediation phase. |

## Summary

- **In-scope findings to remediate**: F1 (range pin), R3 (index status).
- **Out-of-scope findings to log as DIs**: F5 (docs/systems/ability_reference.md seeker arc), F6 (inert Weapon tokens in turret_mount/rapid_fire).
- **Clean (no action)**: F2, F3, F4, R2.

## DI candidates

1. `docs/systems/ability_reference.md:287` says "seekers ignore firing arc" — true for target acquisition, false for launch direction. Per PROJ-497 Decision 3.
2. `data/modifiers.json:57-62` (turret_mount) and `:283-288` (rapid_fire) include dead `"Weapon"` namespace tokens. Behavior intact via co-listed ability keys but tokens are inert.
