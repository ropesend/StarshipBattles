# PROJ-498 Audit Verification

Source: `AgentCoordination/Scratchpad/Consult/20260523T173403Z_audit-PROJ-498/response.md`
Auditor: codex (claude-consult, mid-project-review)
Verifier: claude (orchestrator)
Date: 2026-05-23

| ID | Verdict | Evidence | Action |
|----|---------|----------|--------|
| F1 — battle_state.py grew over the 500-LOC ceiling | VERIFIED + IN-SCOPE | `wc -l game/simulation/battle_state.py` = 630; `git show main:game/simulation/battle_state.py | wc -l` = 612. Codex's "505→523" numbers were wrong but the principle holds: file was already over 500, PROJ-498 added 18 lines (276-296). docs/03_CONVENTIONS.md:173-180 says "Split by responsibility when a touched file approaches that ceiling" — file is well past ceiling but the new block isn't structurally tied to battle_state. The 18-line block is near-identical to a 19-line block added to ship_serialization.py (223-247) — there's real duplication. Extracting a helper deduplicates AND addresses the LOC concern. | Extract `apply_modifier_with_rejection_logging` helper to a new module; both battle_state.py and ship_serialization.py call it. |
| F2 — `docs/guides/modifier_system.md` edited but not in plan scope | VERIFIED + IN-SCOPE | `plan.md:42-43` scopes docs/05_ERROR_HANDLING.md and (optionally) docs/04_SERVICES.md. The guide is not listed. Implementer edited it anyway at :100, :273-282. The edit is coherent and useful; plan.md should be updated retroactively to include it. | Update plan.md Scope/In to add `docs/guides/modifier_system.md`. |
| F3 — No behavioral regression in bool callers | VERIFIED + NO ACTION | `is_modifier_allowed()` at modifier_service.py:106-127 returns bare bool via `check_allowance(...).allowed`. Callers at modifier_manager.py:124-128, component_service.py:104-109, modifier_logic.py:54-56 still use bool-shaped guards. | No action. (Note: Codex noted "the request's latter two paths are stale; the actual callers live under `game/ui/...`" — those are the correct paths I cited; Codex was confirming, not flagging.) |
| F4 — `check_allowance()` doesn't over-promise semantics | VERIFIED + NO ACTION | Enum at modifier_service.py:22-38 is exactly the locked set (ALLOWED / UNKNOWN_MODIFIER_ID / TYPE_NOT_ALLOWED / TYPE_DENIED / ABILITY_NOT_ALLOWED). Implementation at :153-180 only returns those reasons. Matches `plan.md:54-56`. | No action. Clean. |
| F5 — Matrix test is genuinely collection-time and data-driven | VERIFIED + NO ACTION | `test_allowance_matrix.py:42-49` loads JSON; `:88-107` builds cartesian product; `:110-129` asserts. No hardcoded pair list. The aggregate sanity guard at `:139-146` (13×169) pins shipped surface, not pairs. | No action. Clean. |
| F6 — Matrix covers allow AND reject paths | VERIFIED + NO ACTION | Codex command output: modifiers=13, components=169, true=462, false=1735. Matrix asserts both paths. `mini_capital_missile` confirmed as `SeekerWeaponAbility` with endurance=0.05; `efficient_engines` confirmed absent. | No action. Clean. |
| F7 — Save-restore warning formats match goals | VERIFIED + NO ACTION | battle_state.py:289-295 logs modifier_id + component_id + ship_id + reason. ship_serialization.py:239-243 logs same with ship_name instead. The pre-existing unknown-id warning at :246-247 remains distinct ("not found in registry, skipping" vs. new "rejected for component … ; skipping"). Tests pin distinction. | No action. Clean. |
| F8 — Docs compose cleanly with PROJ-489 | VERIFIED + NO ACTION | docs/04_SERVICES.md:269-295 (new), docs/05_ERROR_HANDLING.md:194-217 (new), docs/guides/modifier_system.md:273-282,290 (new) — all preserve PROJ-489's runtime restriction story. No contradiction or duplication. | No action. Clean. |
| F9a — Legacy `typing` generics in test_allowance_matrix.py | VERIFIED + IN-SCOPE | Lines 29, 42, 47, 52 use old `typing.List`/`typing.Dict`/etc. style. docs/03_CONVENTIONS.md:497-503 says use modern syntax (`list[int]`, `dict[str, int]`). Quick fix. | Replace legacy generics with modern syntax. |
| F9b — Stale comment in test_modifier_service.py:1115-1121 | VERIFIED + IN-SCOPE | Comment claims save-restore log tests rely on `AllowanceResult.__str__`, but production logging at battle_state.py:289-295 and ship_serialization.py:239-243 uses `allowance.reason.name` directly. Comment is wrong/stale. Quick fix. | Update or remove the misleading comment. |
| R1 — Codex did not run tests (allow_tests:false) | VERIFIED + NO ACTION | Static-only audit. Implementer already ran full sharded suite (26869 passed). | No action; coverage already verified. |
| R2 — Plan scope vs guide edit | Same as F2 | Same finding from different angle. | Addressed by F2 remediation. |
| R3 — LOC ceiling waiver | Same as F1 | Same finding from different angle. | Addressed by F1 remediation. |

## Summary

- **In-scope findings to remediate**: F1 (extract helper for save-restore rejection logging), F2 (plan.md scope), F9a (typing generics), F9b (stale comment).
- **Clean (no action)**: F3, F4, F5, F6, F7, F8, R1.
- **DI candidates**: None — no out-of-scope structural issues surfaced beyond what's already logged.

## Helper extraction design (Task 5.1 pre-plan)

The 18-line block in battle_state.py:279-296 and the 19-line block in ship_serialization.py:225-244 are near-duplicates. Extract to:

```python
# game/simulation/services/modifier_save_restore.py (new file)
import logging
from typing import Any
from game.simulation.services.modifier_service import ModifierService

logger = logging.getLogger(__name__)

def apply_modifier_with_rejection_logging(
    *,
    modifier_id: str,
    modifier_value: Any,
    component: Any,
    modifier_registry: dict,
    context_label: str,
    target_label: str,
) -> bool:
    """Apply a modifier at save-restore boundaries; log+skip on allow_abilities rejection.

    Returns True if the modifier was applied, False if rejected (and logged).
    """
    allowance = ModifierService(modifier_registry=modifier_registry).check_allowance(
        modifier_id, component
    )
    if not allowance.allowed:
        logger.warning(
            f"{context_label}: Modifier '{modifier_id}' rejected for "
            f"component '{component.id}' on {target_label}: "
            f"{allowance.reason.name}; skipping"
        )
        return False
    component.add_modifier(modifier_id, modifier_value)
    return True
```

Callers:
```python
# battle_state.py (replacing :279-297 with ~3 lines):
from game.simulation.services.modifier_save_restore import apply_modifier_with_rejection_logging
apply_modifier_with_rejection_logging(
    modifier_id=mid, modifier_value=mval, component=new_comp,
    modifier_registry=mod_registry,
    context_label="BattleState restore", target_label=f"ship '{self.ship_id}'",
)

# ship_serialization.py (replacing :225-244 with ~3 lines):
applied = apply_modifier_with_rejection_logging(
    modifier_id=mid, modifier_value=m_dat['value'], component=new_comp,
    modifier_registry=mods,
    context_label="ShipSerializer", target_label=f"ship '{ship.name}'",
)
```

Net effect: battle_state.py drops back to ~615 lines (612 + ~3 for the helper call), ship_serialization.py drops to ~270. New helper file is ~25 lines including docstring. Existing test assertions on the log message format continue to pass (helper produces identical log lines). Caller tests + matrix tests unaffected.
