# Review Scope: Full review batch 2/6: PROJ-326..328 + audit Sessions 1-4
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260504_231828_f8313b
**Review Mode:** fresh-eyes (no prior review reports consulted)
**Severity:** CRITICAL and MAJOR only

## Scope

PROJ-326 + PROJ-327 + PROJ-328 + the 4 audit sessions that closed out PROJ-321..328.

**Project directories:**
- `Projects/active_projects/PROJ-326/` — test linter + SystemTreePanel coverage + StrategySessionFacade contract guard
- `Projects/active_projects/PROJ-327/` — test runtime reduction (virtual_table @patch sweep + mutable-mock fixture rescope + StrategyScreen Compositional Construction)
- `Projects/active_projects/PROJ-328/` — UIWindow MVVM rollout (BuildQueueListWindow, OrdersWindow, FleetReportWindow, NewGameSetupScreen, TransferDialog)

**Audit closeout commits:**
- d7cd97dc1 fix(llm): wrap unexpected provider exceptions in LLMUnexpectedError (audit S1.1)
- 47ed28aea fix(transfer-dialog): guarantee kill() on _on_confirm exception (audit S1.2)
- 8b41f1420 test(system-tree-panel): cover planet/star/warp-point classification paths (audit S1.3)
- 85d6723b7 docs: README pattern count + §32/§33 reword + PROJ-325 PoC findings backport (audit S1.4-S1.7)
- 7f94a0c94 docs(audit): correct measurement claims in PROJ-327/328 (audit S2.8-S2.10)
- 71d727421 docs(audit): Session 3 — index status, conventions cross-ref, broken links, TransferDialog LOC, allowlist rationale
- da02bee86 test(infra): Session 4 — UI builder hardening + factory introspection guards

## Instructions

Fresh-eyes review. CRITICAL/MAJOR only. 8 specific review items defined in the request.

## Context

Part of a 3-stream end-to-end review of the PROJ-321..341 arc.
