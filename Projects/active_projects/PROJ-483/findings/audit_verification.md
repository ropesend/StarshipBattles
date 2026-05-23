# PROJ-483 — Codex Audit Verification Table

- **Audit date:** 2026-05-23
- **Auditor:** codex (mid-project-review, sandbox=workspace-write, allow_tests=false)
- **Consult artifact:** `AgentCoordination/Scratchpad/Consult/20260523T034521Z_audit-PROJ-483/response.md`
- **Orchestrator:** Batch 2 (claude)

## Findings table

| # | Finding (Codex) | Cite | Verified? | Scope | Disposition |
|---|---|---|---|---|---|
| 1 | No Phase 4 scope spillover; mypy.ini limited to declared layers, no `game/strategy/*` or `game/ui/*` edits. | mypy.ini:10-31; plan.md:35-46; phase_4_checklist.md:10-14,75-86 | YES | n/a | REJECTED (clean bill — no action) |
| 2 | `game/engine/collision.py` `if beam_ab is not None:` branch turns invariant failure into silent dropped beam hit. `BeamResolution` always carries a live `weapon_ability` per AttackRequest contract. No regression test added. | collision.py:117-156; _beam_common.py:28-40; attack_contract.py:21-25,152-161,204-207 | YES | IN-SCOPE | REMEDIATE — replace silent skip with assertion; this is exactly the "no bandaids" pattern the user prohibits |
| 3 | `game/ai/controller.py:435-441` uses `is_combatant` guard but then reads `obj.radius`. `ICombatant` lacks `radius`; the actual spatial contract is `IGridEntity`. `# type: ignore` papers over a real guard mismatch. | controller.py:435-441; protocols/combat.py:10-24,127-129; ai/protocols.py:38-63,116-123 | YES | IN-SCOPE | REMEDIATE — swap guard to `is_grid_entity`, remove `# type: ignore` |
| 4 | `game/ai/target_evaluator.py:218-224` calls `candidate.get_components_by_layer(...)` after `is_combat_ship` guard, but the method is NOT declared on `ICombatShip`. Real protocol gap. | target_evaluator.py:218-224; entity_protocols.py:49-60,197-232,473-474 | YES | IN-SCOPE | REMEDIATE — add `get_components_by_layer` to `ICombatShip` protocol, remove `# type: ignore` |
| 5 | `game/ai/interfaces/controllable.py:382-384` `# type: ignore` on `self._ship.layers`. Lower concern — Ship's `layers` is dynamically assigned by ShipLayerManager. Comment incorrectly says `dict[str, Any]` but real key type is `LayerType`. | controllable.py:382-384; ship.py:377-379; ship_layer_manager.py:41-50,63-71 | YES | IN-SCOPE (low priority) | REMEDIATE — add class-level `layers: dict[LayerType, LayerData]` annotation on Ship so the ignore can be dropped; correct the misleading comment in controllable.py |
| 6 | `IEmpire.color -> tuple[int, int, int]` is over-tight narrowing. `Empire.color` is stored without coercion; `from_dict` accepts JSON lists. Protocol stricter than implementation. | strategy_domain.py:32-33; empire.py:24-28,300-310,356-370 | YES | IN-SCOPE | REMEDIATE — widen protocol to `tuple[int, int, int] \| list[int]` OR coerce in `Empire.from_dict`. Choose coerce (preserves protocol contract; converts list→tuple at deserialization boundary). |

## Out-of-scope items / Discovered Issues
None. All in-scope findings are within the PROJ-483 file set.

## Scope-creep escalation (Batch 2 critical check)
Finding 1 explicitly cleared: no Phase 4 scope-creep into simulation/strategy/UI. **No escalation to user.**

## Remediation plan
Create `phase_5_checklist.md` titled "Phase 5: Audit remediation (Codex consult 2026-05-23)" with 5 tasks (findings 2-6). Spawn a single subagent to implement; do not re-audit.
