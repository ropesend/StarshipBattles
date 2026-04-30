# Critical Evaluation of Support Systems

Author: Claude Code (Opus 4.7, 1M context)
Date: 2026-04-29
Scope: Process and tooling infrastructure only — `AgentCoordination/`, `Projects/`, `Tracking/`, `Reviews/`, `Tools/`, the four `*/skills/` trees, `docs/`, and the three adapter files (`AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md`). The actual game code under `game/` was not audited.

This is a written report. Nothing was changed.

## TL;DR

The repository has accumulated **multiple layers of process infrastructure** that were each well-intentioned at the time of construction but together form a sediment of abandoned automation, stale state, parallel-but-divergent skill copies, and documentation that contradicts the code. The most recent layer (the agent coordination tooling) is itself now generating its own archival debt — 23 historical review files in `AgentCoordination/` totaling **4,559 lines** of metadiscussion for a 161-test coordination toolkit.

The dominant pattern is *building, briefly using, and abandoning systems without removing them*. Three CLI loop systems are fully dead. 44 reviews have been "In Progress" since January–February. An undocumented "Sweep" sub-system runs in parallel to the documented review protocols. The Tracking and Reviews directories disagree on case conventions. Tracking still ships nine "legacy" prompts that the README explicitly says are deprecated. CLAUDE.md is **377 lines** — almost five times the 80-line target the agent coordination plan set for it, and it still overlaps significantly with AGENTS.md.

The systems that *are* healthy (`Tracking/`, `Tools/test_sharded`, `Tools/agent_coordination`, the active project workflow PROJ-300–318) are surrounded by enough dead infrastructure to obscure the parts that work.

---

## Findings, ranked by severity

### CRITICAL: Three abandoned automated loop systems with no shutdown

`Projects/refactor_loop/`, `Projects/complexity_loop/`, and `Projects/continuous_loop/` are three independent CLI loop frameworks built between January and March 2026. All three are now stale:

| Loop | Last activity | State |
|---|---|---|
| `refactor_loop` | 2026-03-01 | Intentionally complete (master plan all checked off) |
| `complexity_loop` | 2026-02-27 | Hit 8-hour timeout at cycle 20/50; never resumed |
| `continuous_loop` | 2026-02-13 | Stuck mid-cycle 6 with `status: "executing"` and `consecutive_failures: 1`. **Zombie state file: 75+ days old, still says "executing".** |

The three loops share infrastructure (`create_project.py`, `Projects/scripts/`, `Projects/protocols/08_automated_loop_protocol.md`, `WORKER_TEMPLATE.md`) but each has its own:

- WORKER variant (7 distinct WORKER\*.md files; only `WORKER_TEMPLATE.md` is reused)
- Loop runner (6 distinct `.ps1`/`.sh` orchestrators)
- Cycle-state JSON schema (3 incompatible formats)
- Plan-builder Python script (`populate_complexity_plan.py` and `populate_cycle_plan.py`)

Both `complexity_loop/README.md` and `continuous_loop/README.md` warn at line ~136 that the loops "should not run concurrently," but **no locking, no project-ID reservation, and no pre-flight check enforces this**. If two loops run at once, they will collide on `Projects/active_projects/PROJ-XXX/plan.md` and silently lose state.

`Projects/scripts/` itself is **30 Python files driving these loops with zero unit tests**. A bug in `check_completion.py` would cause the loop to skip remaining work; a bug in `commit_phase.py` could corrupt history. Concrete evidence the testing gap matters: `continuous_loop` is in a corrupt state right now and nothing detected or alerted.

**The loops are not deletable today** — refactor_loop's archive contains real history, and the others have legitimate WORKER prompts that could be reused. But they should either be reactivated (with locking + tests) or archived to git history with a one-paragraph "what we tried" note. Letting three abandoned automation systems sit in `Projects/` indefinitely is the worst of both worlds.

### CRITICAL: 44 reviews "In Progress" since January–February; undocumented "Sweep" sub-system

`Reviews/reviews_index.md` lists 44 reviews in `In Progress` status, the bulk dated 2026-01-23 through 2026-02-27. Only **one** review in the entire index is marked `Completed`. Several "Sweep Review" entries are duplicate runs of the same sweep (`2026-02-14_sweep_full-codebase-sweep` appears more than once). The index has not been pruned in two months.

Adjacent to the documented review system is an entirely **undocumented "Sweep" sub-system**:

- `Reviews/Prompts/` contains 8 prompts prefixed `Sweep -` (Architecture Drift, Consistency Violations, Duplication, Generate Projects, Legacy Holdovers, Shard Definitions, Test Coverage Gaps, Validate Findings).
- **Zero corresponding protocol files exist** in `Reviews/protocols/`. The 11 numbered protocols cover general review, test coverage, focused-question, migration, security, performance, technical debt, consistency, update, and review-to-project — but no Sweep protocol.
- `reviews_index.md` lists Sweep runs as if they are first-class review types.
- The 8 Sweep prompts are evidently driven by something — likely `continuous_loop` (which has its own `SWEEP_WORKER.md`) — but the relationship is not documented anywhere.

This is a half-integrated experiment that became permanent. Either Sweep should be formalized with a protocol and a README section, or its prompts and index entries should be archived. Right now it sits as a parallel review pipeline that no doc explains.

### HIGH: Adapter docs are no longer thin adapters

The agent coordination plan called for `CLAUDE.md` to be a thin adapter — target 80–120 lines, hard cap 200 — that imports `AGENTS.md` and adds only Claude-specific guidance. **CLAUDE.md is currently 377 lines.** It restates the three non-negotiable rules in long prose, the documentation reading order, the project structure, conventions, common tasks, the testing configuration, and the git workflow — most of which is already in `AGENTS.md` (104 lines) or `docs/`.

Reinforcement markers were added in this round, which is good. But adding markers to expanded prose is not the same as trimming the file. The adapter has drifted back toward "Claude's full project documentation" instead of "Claude-only delta over AGENTS.md."

`.agents/CODEX.md` (50 lines) is correctly thin and demonstrates the target shape.

### HIGH: AgentCoordination/ has become its own archival debt source

`AgentCoordination/` contains **23 markdown files totaling 4,559 lines**. The breakdown:

- 1 active policy: `codex_agent_coordination_plan_final.md`
- 5 superseded policy versions: `codex_agent_coordination_plan.md` through `_v4.md` plus `_claim_responses.md`
- 12 historical agent reviews: `claude_code_*_v[1-4]_comments.md`, `opencode_deepseek_*_v[1-3]_comments.md`, `antigravity_*_v[1-3]_comments.md`, three `*_baseline_inventory_review.md`, plus `*_implementation_review.md` and `*_system_review.md`
- 1 README, 1 user response file, 1 SKILL_RENAMES report, 1 toml map

Of these, only the policy_final, README, and the two regenerable reports (SKILL_RENAMES.md, skill_rename_map.toml) reflect current state. Eighteen files are historical artifacts kept for context. The README's recent update partially addresses this by labeling them as "historical agent review artifacts," but the directory still functions as both a working policy directory **and** a review archive. New contributors will reasonably assume all 23 files are equally relevant.

This is the same anti-pattern the audit found elsewhere: keep everything because git history isn't enough. Git history *is* enough; AgentCoordination/ is the wrong place for review archives.

### HIGH: Tracking and Reviews disagree on case conventions and lifecycle

- `Tracking/prompts/` (lowercase) vs `Reviews/Prompts/` (uppercase). No documented reason. The Reviews capitalization predates the Tracking convention; nobody normalized.
- `Tracking/prompts/` contains 9 files and is **explicitly marked legacy** in `Tracking/README.md`: *"Legacy prompt files (being replaced by `/ticket-*` skills)"*. Yet the files are not deleted and not in a `_legacy/` subdir. They sit in the active path advertising themselves as the canonical interface to anyone who lands there first.
- Status vocabulary differs across systems. Tickets use `[Pending]`, `[In-Progress]`, `[Awaiting Confirmation]`, `[Deep Investigation]`, `[Needs Clarification]`, `[Blocked]`. Reviews use `In Progress`, `Completed`, `Archived`, `Led to Project`. There is no mapping between the two vocabularies and no agent doc explains the difference.

Tracking itself is otherwise the **healthiest** system in this audit — only 1 active bug vs 140 archived, the QA session of 2026-04-28 archived 9 bugs and 9 features cleanly, and the protocols are well-aligned with the new prefixed skill commands. The naming and legacy-prompt issues are the rough edges around an otherwise functioning system.

### HIGH: `.claude/skills/` and `.agent/skills/` are not byte-identical mirrors

The agent coordination plan documented the Claude/Antigravity skill divergence as "intentional" — Antigravity may not support Claude-specific frontmatter fields like `disable-model-invocation` or `argument-hint`. That is reasonable.

What the plan did **not** lock down is that the skill *bodies* have also diverged structurally. Sample diff between `.claude/skills/claude-proj-start/SKILL.md` and `.agent/skills/anti-proj-start/SKILL.md`:

- Antigravity strips the "Your Role: Project Architect" section, the explicit `Read and follow the full protocol file` directive, the multi-step phase enumeration with TDD reminders, and several other paragraphs.
- The structural divergence isn't documented anywhere; it's the result of two parallel edit histories.

This means there are effectively **two separate skill libraries** for Claude and Antigravity, kept loosely in sync by hand. **65 SKILL.md files** (32 + 33) maintain parallel content. Drift is inevitable. The mirror generator the V3 plan proposed was never implemented; the validator's prefix check verifies *names*, not *content equivalence*.

If Antigravity remains lower-priority and rarely used (per the user's stated direction), maintaining 33 parallel skill copies for it is hard to justify. Either:
- The mirror is generated from `.claude/skills/` with frontmatter stripping (one canonical source), or
- `.agent/skills/` is reduced to the 4–8 skills Antigravity actually uses (asset generation, browser/UI workflows, tooling) and the remaining 25 stale copies are deleted.

The current state is the most expensive option: full duplication, no automation, no enforcement of equivalence.

### HIGH: Two incompatible philosophies of skill granularity coexist

- `.claude/skills/` and `.agent/skills/` use the **fine-grained model**: 32–33 skills, each one workflow (`claude-proj-start`, `claude-ticket-work`, `claude-qa-triage`, etc.). Average ~95 lines per file.
- `.agents/skills/` (Codex) uses the **router model**: 8 skills, each routing to many protocols based on user intent (`codex-starship-project-system` covers start/continue/audit/revise/extract-phase/close/archive in one entry). Average ~54 lines per file.

Both can be defended in isolation. Together, they create a coordination problem: when a new project workflow is added, do you create one new fine-grained Claude/Anti skill *and* update one Codex router skill? Neither convention dominates, neither tooling enforces, and the two surfaces will diverge whenever a workflow changes. The validator has no check for "if Codex skill X mentions protocol Y, the corresponding Claude skill exists."

### MEDIUM: Tools/ has loose files, undocumented entries, and one redundant pair

Per the Tools audit:

- **Loose files violating the directory convention.** `Tools/check_file_size.py` and `Tools/migrate_ai_strategy.py` sit at the top level. `Tools/README.md` itself states *"never add loose files to `Tools/` root"*. `migrate_ai_strategy.py` looks like a one-shot completed migration that should have been archived. `check_file_size.py` is genuinely useful but should be in a subdir.
- **Tools missing from `Tools/README.md`'s inventory:** `audit_shrink`, `captioning`, `check_context`, `component_transparency_viewer`, `process_components`. The README was last synced before these were added.
- **`process_components/` has no README** — the only documented description sits inside `component_transparency_viewer/README.md`.
- **Redundancy: `check_orphans` vs `analyze_dependency_graph`.** Both find unused/unreachable code. `check_orphans` uses regex-based import detection (simpler, can false-positive). `analyze_dependency_graph` uses AST + entry-point tracing (more correct). One should be marked legacy or deleted.
- **`background_eraser`** has minimal value — it's an asset *browser*, not a processor. Probably deletable.
- **`captioning/`** has no Python entry point; it is a workflow guide for an LLM. It belongs in `docs/guides/` or `docs/systems/`, not `Tools/`.

### MEDIUM: Scripts everywhere, tests almost nowhere

| Directory | Python files | Unit tests |
|---|---|---|
| `Projects/scripts/` | ~22 + a `utils/` package | 0 |
| `Tracking/scripts/` | 4 | 0 |
| `Reviews/scripts/` | 11 + `utils/` | 0 |
| `Tools/agent_coordination/` | 9 | **8 test files** |
| `Tools/test_sharded/` | 1 (excluding wrapper) | 1 |
| `Tools/regenerate_ship_portraits/` | several | 1 |
| `Tools/profiling/` | 1 | 1 |
| Other Tools/ subdirs | many | 0 |

The agent-coordination tooling bumps the test count up considerably (+93 cases this round per the prior commit message), but the broader pattern is **process-glue scripts have no tests**. These are precisely the scripts that fail silently — wrong path detection, wrong file format parsing, wrong commit message escaping. The continuous_loop dying mid-cycle 6 with no alert is a downstream consequence of this.

### MEDIUM: `docs/` is large but mostly internally consistent

`docs/` contains 6 numbered files (01_ARCHITECTURE through 06_UI_STYLE_GUIDE) totaling 5,722 lines, plus 8 guides, 8 system docs, the README, and `_ignore/`. This is roughly the right shape for a project of this size and is **not** a problem in the same way the loops/reviews are. Two minor concerns:

- I did not verify whether every `Last verified` date in `docs/` is current, but the AGENTS.md/CLAUDE.md prose explicitly directs agents to update those dates. Whether they actually do isn't enforced by the validator.
- `docs/_ignore/` is correctly gitignored and excluded from validator scans, but the prompt-ingestion convention (Codex-authored prompts ending up there) is not documented in `docs/README.md`. This is invisible to new contributors.

### LOW: Cruft and abandoned single-file artifacts

- `Projects/Triage/fleet_system_review.md` — one analysis from 2026-03-22 that was never converted to a project or assigned. Either it should become PROJ-XXX or be deleted; sitting in `Triage/` does nothing.
- `Reviews/Review_Report_2026_01_27.md` — a top-level dated review report. If this is a one-off output, it belongs under `Reviews/results/`. If it's a template, it should not be dated.
- `Tracking/completed_features.md` and `Tracking/solved_bugs.md` — append-only logs that overlap with the archived/ subdirectories. Whether they're updated automatically or by hand isn't clear from the README.

---

## Cross-cutting observations

### 1. The repository is over-instrumented for a single-developer project

By rough count, the support layer contains:

- 13 Project protocols
- 11 Tracking protocols
- 11 Review protocols
- 25 Review prompts
- 9 (legacy) Tracking prompts
- 11 review-types in `reviews_index.md`
- 32 + 33 + 8 + 1 = **74 skills**
- 23 AgentCoordination files
- 6 docs sections + 8 guides + 8 systems + a README
- ~70+ Python scripts across `Projects/scripts/`, `Tracking/scripts/`, `Reviews/scripts/`, `Tools/`
- 3 automated loop systems with 6 runners total

For a project with one full-time developer collaborating with several agents, this is a lot of process. The systems were built incrementally and each was justified, but **none of them have been removed**. The AgentCoordination layer this round is itself a meta-coordination layer over the previous coordination layers. There is no comparable "delete this old thing" cycle.

### 2. The dominant failure mode is "abandoned in place"

Loops were written, reached a finish line, and were left running with stale state. Reviews were started in January, never closed. Triage created an analysis doc, never acted on it. Tracking has nine legacy prompts the README itself says are deprecated. The pattern repeats: build, partly use, walk away. Nothing removes.

The *symptom* is that new contributors and agents have to figure out which directories matter and which don't. The *cost* is that every audit (including this one) finds the same kind of stale state in a new place.

### 3. Coordination plans solve coordination problems by adding more coordination

The agent coordination work this round produced a real, working tooling layer (validator, sanitizer, prefix migration, usage counters, hook). That's genuinely useful. But it also produced 23 markdown files of plans, reviews, claim-responses, and meta-discussion — most of which are now historical and do not survive scrutiny as policy. The next round's "system review" will need to audit *this* round's review artifacts.

The pattern is recursive. The plan is to plan the plan.

### 4. Healthy systems exist and should be preserved

These work well and should not be touched in any cleanup:

- **`Tools/test_sharded/`** — clean, tested, well-documented, the canonical test runner.
- **`Tools/agent_coordination/`** (most of it) — recent, tested, validator passes 11/11.
- **`Tracking/`** — actively used, low active count, archives cleanly.
- **`docs/01-06`** — substantively current architecture/pattern/conventions docs.
- The active-project workflow (PROJ-300–318) — operating without any of the loop systems and apparently working fine.

The signal that the manual workflow has resumed (15 active projects, none in any loop) is informative: **the loops are not currently necessary**, and the manual workflow is sustainable.

---

## What I would prioritize if asked to clean up

In order, by ratio of payoff to effort:

1. **Decide and act on the three loop systems.** Either revive one (with tests + locking) or archive all three to a single `Projects/_archive/automated_loops/` with a one-page README explaining what was tried and why it stopped. The current limbo is the worst option.
2. **Audit the 44 stale reviews.** Bulk-close anything older than 60 days as `Abandoned` with a one-line reason. Define an SLA: any review older than N days auto-flags. This is mechanical work; a script + a manual pass closes it in an afternoon.
3. **Decide on Sweep.** Either write the missing protocol and document it, or delete the 8 Sweep prompts and remove the index entries. The half-integrated state is the smoking gun.
4. **Move historical AgentCoordination reviews to `AgentCoordination/_archive/`** (or delete; git has them). Keep only `codex_agent_coordination_plan_final.md`, `README.md`, generated reports, and the user response. The new contributor experience improves dramatically.
5. **Trim CLAUDE.md to its 80-line target.** Sections that restate AGENTS.md or docs/ should be replaced with `@AGENTS.md` and links. Reinforcement markers stay.
6. **Delete `Tracking/prompts/`** (or move to `Tracking/_legacy/` with a `DELETE_ME_BY_2026-06-01.md`). It is dead weight.
7. **Decide the mirror policy for `.agent/skills/`.** If Antigravity is low-priority, reduce to ~6 skills it actually uses. The current 33 is maintenance burden without benefit.
8. **Move `Tools/check_file_size.py` and `Tools/migrate_ai_strategy.py`** into subdirectories or delete the migration script. Update `Tools/README.md` inventory.
9. **Standardize prompt directory case** (`Reviews/Prompts/` → `Reviews/prompts/`).
10. **Add a Reviews/README.md.** It is the only top-level subsystem missing a README, and it is the most over-engineered.

Items 1–3 alone would visibly reduce the support-system surface area by ~40%.

---

## Closing observation

The systems that produced concrete, durable value in this audit are the ones that are *small, tested, and used recently*: `Tools/test_sharded`, `Tools/agent_coordination`, `Tracking/`, the manual project workflow. The systems that produced the most evidence of cruft are the ones that grew large, had many moving parts, and were used in bursts: the three automated loops, the Reviews/Sweep complex, the historical AgentCoordination archive.

The repository is not broken. It is *layered*. The most useful single change is not new tooling — it is **deletion**, with a small number of policy decisions to make deletion safe. Most of that deletion is uncontroversial; a handful of items (the automated loops, the Antigravity skill mirror) require an explicit decision before action.

This concludes the report.
