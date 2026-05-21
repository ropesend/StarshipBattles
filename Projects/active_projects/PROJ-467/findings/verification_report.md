# Verification Report — PROJ-467 (foundation bundle)

- **Source audit:** `Reviews/results/2026-05-20_073330_docs-audit/`
- **Run date:** 2026-05-20
- **Batch summary (full run):** 40 verified / 4 rejected / 1 uncertain / ~10 out-of-scope categories, out of the audit candidate set.
- **This bundle:** 18 verified at planning; **17 implemented** (`DEAD-PAT-legacy` dropped on revision as a false/stale finding — see Verified table and decisions.md).

## Phase 4 — Codex audit remediation (2026-05-20)
A one-round Codex audit (`AgentCoordination/Scratchpad/Consult/proj467_audit/`) returned 4 findings; all 4 independently VERIFIED, 0 rejected. They were incomplete-cleanup gaps in files Phases 1-3 touched: (1) `Last verified:` stamps not bumped on `docs/01_ARCHITECTURE.md` / `02_PATTERNS.md` / `03_CONVENTIONS.md`; (2)+(3) `WORKER_TEMPLATE.md:63` still pointed audits at retired Protocol 08 (Phase 3 fixed only line 37); (4) `WORKER_TEMPLATE.md:64,67` "5 audit cycles" vs Protocol 04's 3-cycle escalate. All four fixed in Phase 4.

Verification was performed directly by reading live code/docs (Agent/Explore subagents unavailable in this harness), a different reader than the audit, per protocol 17's skeptical-verification requirement. Filesystem stats and `grep` were used to confirm every dead-ref and content-error claim.

## Verified (this bundle)

| id | doc_file | line | category | current text → recommended change | severity | mislead risk |
|----|----------|------|----------|-----------------------------------|----------|--------------|
| XDOC-pyver | AGENTS.md | 52 | content_error | "Python 3.14" → "Python 3.13+" | CRITICAL | Canonical rules file states wrong baseline; pyproject requires >=3.13 |
| ~~DEAD-PAT-legacy~~ DROPPED | docs/02_PATTERNS.md | 818-827 | dead_ref | ~~remove `test_run_details.py` / `race_setup_screen.py`~~ — **DROPPED 2026-05-20 on revision**: these lines are inside the "Re-Export Shim" section and explicitly annotated "(Removed PROJ-417/416/383)"; they document deleted shims as removed, NOT as live pattern examples. False/stale finding (dual independent+Codex review). No edit made. | ~~CRITICAL~~ N/A | None — lines correctly mark refs as removed |
| F5-broadexcept | CLAUDE.md | 112 | cross_doc_inconsistency | drop "or immediately above" | MAJOR | Relaxes canonical broad-catch placement rule |
| F8-marked-del | CLAUDE.md | 5 | dead_ref | remove `_marked_for_deletion_2026-05-29/` pointer | MAJOR | Directs agents to a soon-deleted location |
| DEAD-CONV-pf | docs/03_CONVENTIONS.md | 32 | dead_ref | `data/pathfinding.py` → `services/galaxy_pathfinding_service.py` | MAJOR | Dead path for canonical `get_system_at_hex()` |
| G5-jsonutils | Projects/protocols/14_create_from_error_audit.md | 122,124 | content_error | `game/services/json_utils.py` → `game/core/json_utils.py` | MAJOR | Wrong path in verifier checklist |
| DEAD-ARCH-gp | docs/01_ARCHITECTURE.md | 155 | dead_ref | add `game/strategy/` prefix to `galaxy_protocols.py` | MINOR | Missing prefix |
| ERR-ARCH-pathfind | docs/01_ARCHITECTURE.md | 154 | content_error | move "pathfinding" from data/ to services/ listing | MINOR | Wrong layer placement |
| ERR-CONV-hardpath | docs/03_CONVENTIONS.md | 332 | content_error | replace hardcoded `C:/Users/rossr/...` path | MINOR | Violates own no-checkout-path convention |
| DEAD-PAT-cmds | docs/02_PATTERNS.md | 170 | dead_ref | `commands.py` → `commands/` package | MINOR | File→package drift |
| DEAD-PAT-handlers | docs/02_PATTERNS.md | 187,827 | dead_ref | `command_handlers.py` → `handlers/` (live refs only) | MINOR | File→package; some refs are intentional-stale warnings |
| DEAD-PAT-classes | docs/02_PATTERNS.md | 38 | content_error | reword `data/classes/` (never existed) | MINOR | References nonexistent dir |
| XDOC-comblab | AGENTS.md | 27 | cross_doc_inconsistency | note combat_lab.run_tests is non-pytest | MINOR | Agents may run via pytest |
| G5-worker08 | Projects/protocols/WORKER_TEMPLATE.md | 37 | content_error | "Follow Protocol 08" → 03a | MINOR | Directs to retired protocol |
| G6-perfreview | Reviews/protocols/06_performance_review.md | 430 | dead_ref | `game/combat/` → `game/simulation/combat/` | MINOR | Wrong example path if copied |
| STALE-readme | docs/README.md | — | doc_staleness | add `Last verified:` line | MINOR | No freshness tracking |
| STALE-agentdocs | AGENTS.md / CLAUDE.md / .agents/CODEX.md | — | doc_staleness | add `Last verified:` lines | MINOR | No freshness tracking |

## Rejected

| id | original audit recommendation | contrary evidence | rationale |
|----|-------------------------------|-------------------|-----------|
| XDOC-simassets | Remove Assets from Simulation's dependency list in AGENTS.md (cross-doc #2 / report §7) | `AGENTS.md:42` lists simulation deps as "Core + Services + Engine" (no Assets); `AGENTS.md:36` is a tier-ordering arrow, not a dependency list; `docs/README.md:65` agrees | Audit misread the tier arrow as a dependency list — false positive |
| G3-M7-pyver | Change `docs/guides/simulation_testing.md:614` "3.13+" → "3.14" to match AGENTS.md | `pyproject.toml:4` `requires-python=">=3.13"`; CLAUDE.md/03_CONVENTIONS agree on 3.13+ | Recommendation direction inverted; AGENTS.md is the wrong one (fixed via XDOC-pyver) |

(The other 2 rejections — component_system scope already present, cross-doc-8 inverted filename — belong to the systems/guides cluster; logged in PROJ-468's verification_report.md.)

## Uncertain (resolved)

| id | question raised | decision |
|----|-----------------|----------|
| F4-ignore | `docs/_ignore/` does not exist but 6 files instruct "never read docs/_ignore/". Soften wording to "if it exists", or leave the guard as-is? | **EXCLUDE** — the rule is a normative guard for user-managed scratch space, not a filesystem-inventory claim. Softening weakens an intentional boundary (CLAUDE.md treats it as by-design); creating the dir would be repo noise. Codex consult concurred. |

## Out of Scope

| id | why excluded |
|----|--------------|
| G1-falsepos | Scanner dead-refs in "Stale Name Traps"/"Warnings"/"Re-Export Shim (Removed)" sections are intentional non-existent refs (input_handler.py, protocols.py, singleton.py, command_handlers.py warning lines, ship_detail_panel.py, FiraCode ttf). Reviewer-confirmed false positives. |
| placeholders | `tests/path/to/test.py` in command examples — intentional template placeholders. |
| G5-examples | All G5 protocol dead-refs and PROJ refs are intentional template/example references. |
| G6-examples | 3 of 4 G6 dead-refs are illustrative template/example workflow paths (only `06_performance_review` `game/combat/` kept). |
| unknown-projs | PROJ-207..PROJ-412 "unknown" status entries: marked INCONCLUSIVE by audit (predate index); index hygiene, not a docs edit. |
| intentional-dups | CLAUDE.md validator-marked duplication; AI dep ordering semantically identical; by-design test-command duplication. |
| context-window | CONTEXT_WINDOW_TOKENS 1M — speculative, not a confirmed error. |
