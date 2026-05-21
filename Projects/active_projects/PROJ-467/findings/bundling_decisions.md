# Bundling Decisions — `2026-05-20_073330_docs-audit`

This file is identical across all sibling projects created in this run (PROJ-467, PROJ-468, PROJ-469).

## Re-verification totals

Out of the audit candidate set, independent third-pass re-verification produced:

- **40 VERIFIED** (eligible for inclusion)
- **1 UNCERTAIN** (resolved → Exclude; see below)
- **4 REJECTED** (audit false positives)
- **~10 OUT_OF_SCOPE categories** (intentional template/example refs, scanner false positives, INCONCLUSIVE "unknown" PROJ index hygiene, intentional duplications)

V = 40 → protocol 17's `30 <= V <= 100` band → 2-3 projects, merged by doc tier; cross-doc/terminology findings always form their own bundle.

## Default proposal (initial)

| # | Title | Doc clusters | Verified |
|---|-------|--------------|----------|
| 1 | Foundation: root agent + architecture/core docs | AGENTS.md, CLAUDE.md, docs/0N_* | — |
| 2 | Reference: systems + guides docs | docs/systems/*, docs/guides/* | — |
| 3 | Cross-doc consistency + procedural | terminology + cross_doc + protocol fixes | — |

## Codex consult (autonomous second opinion)

Per the autonomous-override contract, a single Codex consult (planning mode) was run instead of pausing for the user:
`AgentCoordination/Scratchpad/Consult/20260521T032207Z_docs-audit-bundling/response.md`.

Codex's advice (all evidence-cited file:line):
- **Bundling:** Keep 3 projects, but make project 3 **cross-doc-only** and fold the small procedural fixes (json_utils path, WORKER_TEMPLATE protocol-08, perf-review path) into the foundation bundle. Folding procedural into foundation is the least-surprising default; a 4-project pure-cluster split is a defensible explicit deviation but not the default.
- **UNCERTAIN (`docs/_ignore/`):** Treat as **Exclude/reject** — the rule is a normative guard, not a filesystem-inventory claim. Softening to "if it exists" weakens an intentional boundary; creating the dir would be repo noise.
- **Rejections:** All 4 rejections are correct (Simulation-deps-Assets misread tier arrow; component_system scope already present; G3-M7 inverted; cross-doc-8 inverted canonical filename).

## Final decision (Claude owns)

Accepted all of Codex's advice:
1. **3 projects.** Foundation (PROJ-467) = root agent docs + `docs/0N_*` + procedural protocol fixes. Reference (PROJ-468) = `docs/systems/*` + `docs/guides/*` + 2 missing-doc items. Cross-doc (PROJ-469) = terminology_drift + cross_doc_inconsistency spanning multiple files only.
2. **`docs/_ignore/` UNCERTAIN → EXCLUDED** (recorded in each project's verification_report.md under Uncertain (resolved)).
3. All 4 REJECTED items stay rejected (see verification_report.md `## Rejected`).

## Final bundle definitions

- **PROJ-467 (foundation):** 18 verified — `AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, `docs/README.md`, `Projects/protocols/14_create_from_error_audit.md`, `Projects/protocols/WORKER_TEMPLATE.md`, `Reviews/protocols/06_performance_review.md`.
- **PROJ-468 (reference):** 18 verified — `docs/systems/ability_reference.md`, `docs/systems/strategy_layer.md`, `docs/systems/fighters.md`, `docs/systems/minefields.md`, `docs/systems/research_system.md`, `docs/guides/adding_abilities.md`, `docs/guides/component_system.md`, `docs/guides/qs_complex_design.md`, `docs/guides/testing_infrastructure.md`, `docs/guides/pre_commit_hooks.md`, plus 2 missing-docs additions (superweapon_order_processor, game_initializer).
- **PROJ-469 (cross-doc consistency):** 4 verified — Pattern #40→#41 (`docs/03_CONVENTIONS.md`), README "33 patterns" count (`docs/README.md`), satellites "fleet namespace" terminology (`docs/systems/satellites.md`), `newdocs/` cross-reference (`docs/guides/testing_infrastructure.md`).

Note: a few doc files (`docs/02_PATTERNS.md`, `docs/README.md`, `docs/03_CONVENTIONS.md`, `docs/guides/testing_infrastructure.md`) appear in more than one bundle because they host findings of different categories. Each finding is assigned to exactly one project; the per-project checklists scope edits to the specific lines named.
