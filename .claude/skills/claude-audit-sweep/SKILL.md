---
name: claude-audit-sweep
description: One-stop pipeline — launch all 9 OpenCode audits sequentially, then dispatch Claude subagents that verify each audit's findings and scaffold cleanup PROJ projects. Fully autonomous; interactive decision points are resolved by a Codex consult (Claude decides).
disable-model-invocation: true
argument-hint: "[optional: space/comma-separated audit names; default = all 9]"
---

# Audit Sweep: OpenCode audits → verified PROJ projects

**Fire-and-forget. No mid-run user questions.** This skill runs the whole
pipeline end to end:

1. **Phase A — Audits.** Launch the OpenCode audit skills **one at a time**
   (they run on DeepSeek and each already fans out into 6–40 concurrent DeepSeek
   calls internally; DeepSeek 429s are non-retryable, so concurrent audits would
   fail unrecoverably).
2. **Phase B — Projects.** For each audit that produced a complete result,
   dispatch a Claude subagent that follows the matching `claude-proj-from-*`
   protocol to skeptically verify findings and scaffold PROJ projects. Where a
   protocol would normally `AskUserQuestion`, the subagent instead runs a Codex
   consult, weighs the advice, and **decides itself** (autonomous-override
   contract below).

This skill only *orchestrates*. The audits self-manage their
`Reviews/results/<ts>_<type>/` output; the proj-from protocols own verification
and project creation. Reuse existing plumbing — do not hand-roll launchers.

## Audit registry (verified mapping)

| Audit (`$ARGUMENTS` name) | OpenCode skill | Command file (prompt source) | Result dir glob | proj-from protocol | Interactive? (consult) |
|---|---|---|---|---|---|
| `audit-shrink` | `ocode-audit-shrink` | `.opencode/commands/audit-shrink.md` | `Reviews/results/*_audit_shrink` | `Projects/protocols/11_create_from_shrink_audit.md` | **No** |
| `test-review` | `ocode-test-review` | `.opencode/commands/test-review.md` | `Reviews/results/*_test-review` | `Projects/protocols/12_create_from_test_review.md` | **No** |
| `type-audit` | `ocode-type-audit` | `.opencode/commands/type-audit.md` | `Reviews/results/*_type-audit` | `Projects/protocols/13_create_from_type_audit.md` | Yes |
| `error-audit` | `ocode-error-audit` | `.opencode/commands/error-audit.md` | `Reviews/results/*_error-audit` | `Projects/protocols/14_create_from_error_audit.md` | Yes |
| `legacy-audit` | `ocode-legacy-audit` | `.opencode/commands/legacy-audit.md` | `Reviews/results/*_legacy-audit` | `Projects/protocols/16_create_from_legacy_audit.md` | Yes |
| `docs-audit` | `ocode-docs-audit` | `.opencode/commands/docs-audit.md` | `Reviews/results/*_docs-audit` | `Projects/protocols/17_create_from_docs_audit.md` | Yes |
| `pattern-audit` | `ocode-pattern-audit` | `.opencode/commands/pattern-audit.md` | `Reviews/results/*_pattern-audit` | `Projects/protocols/18_create_from_pattern_audit.md` | Yes |
| `state-audit` | `ocode-state-audit` | `.opencode/commands/state-audit.md` | `Reviews/results/*_state-audit` | `Projects/protocols/19_create_from_state_audit.md` | Yes |
| `testcoverage-audit` | `ocode-testcoverage-audit` | `.opencode/commands/testcoverage-audit.md` | `Reviews/results/*_testcoverage-audit` | `Projects/protocols/20_create_from_testcoverage_audit.md` | Yes |

Only **audit-shrink** and **test-review** are fixed-shape (their protocols never
ask the user) — those subagents run with **no Codex consult**. The other 7 are
interactive and get exactly **one** consult each.

## Arguments

`$ARGUMENTS` = optional subset of audit names from the table (space- or
comma-separated, e.g. `type-audit pattern-audit`). Empty → all 9. Unknown names
→ stop and list valid ones. A single name is the cheap smoke-test path.

---

## Phase A — Run the audits (sequential)

### Step A1 — Pre-flight

1. Resolve the repo root at runtime (`git rev-parse --show-toplevel`); do not
   hardcode a checkout path.
2. Confirm the OpenCode CLI is resolvable. Run:
   ```bash
   python -c "import sys; sys.path.insert(0, r'<repo>/Tools/agent_coordination'); import partner_invoke; print(partner_invoke.resolve_binary('opencode'))"
   ```
   If it prints `None`, **stop** and tell the user OpenCode isn't installed /
   on PATH (set `OPENCODE_BIN` or install it).
3. Snapshot the current `Reviews/results/` directory names (so new audit dirs
   are identifiable):
   ```bash
   ls Reviews/results/ > AgentCoordination/Scratchpad/tmp/audit_sweep_snapshot.txt
   ```
4. Resolve the selected audit list from `$ARGUMENTS` (default = all 9).

### Step A2 — Launch each audit, one at a time

For each selected audit, **in order, waiting for each to finish before starting
the next** (audit-concurrency default = **1**; never default higher):

1. Read the audit's command file (e.g. `.opencode/commands/type-audit.md`) and
   take the body *after* the YAML frontmatter as the prompt — source the prompt
   from the registry, don't invent it.
2. Launch the audit headless through the shared subprocess helper (handles the
   canonical `opencode run --dir … --format json --dangerously-skip-permissions`
   argv, timeout, and Windows process-tree kill). Pass **no** `response_file`
   (audits write to `Reviews/results/`, not a consult artifact):
   ```bash
   python -c "
   import sys; from pathlib import Path
   sys.path.insert(0, r'<repo>/Tools/agent_coordination')
   import partner_invoke
   prompt = Path(r'<repo>/.opencode/commands/<audit>.md').read_text(encoding='utf-8')
   prompt = prompt.split('---', 2)[-1].strip()   # drop frontmatter
   r = partner_invoke.invoke_sync(
       'opencode', prompt,
       log_path=Path(r'<repo>/AgentCoordination/Scratchpad/tmp/audit_sweep_<audit>.log'),
       repo_root=Path(r'<repo>'),
       response_file=None,
       timeout_sec=2700,   # ~45 min ceiling; audits run ~2-30 min
   )
   print(r.exit_status, r.error_kind, r.return_code)
   "
   ```
3. Announce start and finish of each audit.

### Step A3 — Confirm each audit's output (guard against partial state)

After each audit process exits, find the result dir matching that audit's glob
that is **(a)** absent from the Step A1 snapshot and **(b) complete** — a
non-empty `report.md` AND the `findings/`/`raw/` subdirs the proj-from protocol
reads. Classify:

- `done` — complete dir found.
- `failed` — process exited but no dir, or a dir that is present-but-incomplete
  (truncated/half-written). **Treat incomplete as `failed`**, never `done`, so
  Phase B never runs against a partial audit. Capture the log tail; look for a
  `429` / rate-limit line.
- `timeout` — `error_kind == "timeout"`.

On a **429-shaped failure**, surface it clearly and **stop launching further
audits** unless the user pre-authorized continue-on-error — retrying into a rate
limit only makes it worse. This is an account-quota issue outside this skill's
control; do not auto-retry.

### Step A4 — Summarize audits

Print a table: audit → status (`done`/`failed`/`timeout`) → result dir →
finding counts (from `result.json` if present, else parsed from `report.md`).

---

## Phase B — Verify findings → create projects (bounded waves + Codex consult)

For every audit with status `done`, dispatch a Claude subagent. Run subagents in
**bounded waves — default 2** (a single message with ≤2 `Agent` tool calls per
wave). Smoke-test at 1, default to 2, only raise to 3 after observed stability.
The project-index lock makes concurrent `create_project.py` calls safe regardless.

> **Verified harness behavior (2026-05-19 smoke test):** a `general-purpose`
> subagent in this environment **cannot itself spawn nested `Agent`/`Explore`
> subagents**, despite the registry listing `Tools: *`. The proj-from protocols
> assume parallel Explore verifiers; in practice the subagent performs the
> skeptical re-verification **directly** (serially, as a different reader of the
> live code). This is correct but slower, and means the real per-subagent
> fan-out is ~1 agent, not ~4 — so the wave bound is *conservative*, not tight.
> The subagent prompt below tells the subagent to fall back to direct
> verification rather than skip it.

### Subagent configuration

- `subagent_type`: `general-purpose` (NOT `Explore` — proj-from protocols spawn
  their own verification subagents, which needs the Agent tool).
- `mode`: `bypassPermissions` (autonomous, writes project files).
- `description`: e.g. `"proj-from type-audit"`.
- `prompt`: built from the template below.

### Subagent prompt template

> You are creating cleanup PROJECT(s) from a completed OpenCode audit, fully
> autonomously.
>
> **Protocol:** read and follow `<protocol-path-from-registry>` exactly.
> **Audit directory:** `<resolved Reviews/results/... dir from Step A3>` — use
> this exact path; do not auto-pick a different one.
>
> Run the protocol's skeptical-verification and project-creation steps. Project
> creation goes through `python Projects/scripts/create_project.py "<title>"`
> (its index transaction is locked, so it is safe to run even if a sibling
> subagent is creating a project at the same time). If the protocol tells you to
> dispatch parallel Explore verifiers but the `Agent` tool is not available to
> you, do the skeptical re-verification **directly** by reading the live code
> yourself (a different reader than the audit) — never skip it.
>
> **[interactive audits only — omit for audit-shrink / test-review]**
> **Autonomous-override contract:** wherever the protocol says to
> `AskUserQuestion` (bundling choices, project scope/title, borderline
> VERIFIED/UNCERTAIN findings), DO NOT pause for a human. Instead, **once**, run
> a single Codex consult to get a second opinion on those decisions:
> `/claude-consult --with codex --mode planning <your decision questions +
> the verified findings + your proposed bundling>`. Read Codex's
> `## Findings` / `## Risks`, **weigh them, then decide yourself** — Codex
> advises, you own the call. Record both Codex's input and your final decision
> in the project's `decisions.md`. Use `claude-consult` / `partner_invoke.py`,
> never raw `codex exec`. One consult total for this subagent — not per project,
> not per finding.
>
> When done, report exactly one line: the PROJ id(s) you created, or
> `"0 verified findings → no project"`. Do nothing outside this audit's scope.

### Notes

- DeepSeek is idle during Phase B (audits already finished); the wave bound is
  about Codex consults + nested Claude agents, not DeepSeek.
- A subagent producing **0 projects** (everything rejected on re-verification)
  is a valid outcome, not an error.

---

## Step C — Final report

Aggregate and present once, at the end:

1. Per audit: status, and PROJ id(s) created (or "none") + verified / rejected /
   uncertain counts.
2. Any `failed` / `timeout` audits, with a one-line reason (surface, don't bury).
3. Next step: `/claude-proj-continue PROJ-NN` for any created project.

## Constraints

- **No user questions mid-run.** The only human-facing interaction is the final
  report. Interactive decisions are delegated to Codex consults, decided by the
  subagent.
- **Audits are strictly sequential** (default concurrency 1). Never stack audits.
- **Never fabricate findings.** Projects come only from the proj-from protocols'
  verified output.
- **Do not act on findings here.** This skill produces *plans* (projects);
  implementation happens later via `/claude-proj-continue`.
- **Surface failures, never silently retry** a 429 or a failed consult.
