---
name: ocode-review-request
description: Process a review request delegated by another agent. Reads a structured request file, executes the appropriate review (code, plan, architecture, tests, security, etc.), writes findings and a result.json sidecar to a review directory. The daemon manages request file lifecycle; this skill owns content only.
argument-hint: Path to request file, e.g. AgentCoordination/opencodereview/pending_review_requests/req_20260429_143052.md
---

# Process Review Request

Read a review request file written by another agent (typically Claude Code),
execute the requested review, and produce a report with a `result.json` sidecar.

The review daemon manages request lifecycle (pending → in_progress → completed).
This skill only produces content: writes report + sidecar to the review
directory, then exits. Never moves the request file.

## Overview

This skill is invoked via `opencode run` by the daemon:
```
opencode run "Load the ocode-review-request skill. Process the request at ... Use review directory: ... Write result.json to: ..."
```

Or directly by the user in interactive mode:
```
/ocode-review-request AgentCoordination/opencodereview/pending_review_requests/req_XXX.md
```

## Step 1: Read the Request

Read the request file at the path provided in the arguments. If no path is
provided, scan `AgentCoordination/opencodereview/pending_review_requests/` for the oldest
pending request and use that.

Parse these fields:
- **Request ID** — unique identifier (`req_<YYYYMMDD>_<HHMMSS>_<6hex>`)
- **Review Type** — `code`, `plan`, `architecture`, `tests`, `security`, `performance`, `consistency`, `general`, `custom`
- **Parent** — if present, a parent request ID for follow-up reviews
- **Scope** — files, directories, or conceptual description
- **Instructions** — what to look for, questions to answer
- **Context** — why this review, what changed
- **Expected Deliverable** — what kind of output

## Step 1.25: Scope Sanity Check — Return Early For Out-Of-Repo Paths

**This is a hard precondition. Run it before any other work.** If the
scope references a path the worker cannot reach, the skill must exit
immediately — it must not attempt the read, must not launch any review
agents, must not produce a partial report.

Determine the project root at runtime — it is the current working directory
of this process. Do not assume any specific absolute path; resolve it via
`pathlib.Path.cwd().resolve()` and compare each scope path's resolved form
against it.

A scope path is **reachable** if (after resolution) it equals the project
root or is one of its descendants. Anything else is unreachable. Common
unreachable cases:

- Paths under a user home directory not inside the repo (e.g.
  `~/.claude/...`, `C:\Users\<name>\...`, `/home/<name>/...`,
  `/Users/<name>/...`)
- System paths (`C:\Windows\`, `C:\Program Files\`, `/etc/`, `/usr/`,
  `/var/`, etc.)
- Sibling-repo paths or scratch directories adjacent to the project

If **any** scope path is unreachable, write the error sidecar shown below
to `{REVIEW_DIR}/result.json` and exit the skill. Do not retry, do not
attempt to read the file, do not launch agents:

```json
{
  "request_id": "req_<id>",
  "error": "cannot reach <offending path>: it resolves outside the project root (cwd=<project root>). The OpenCode worker can only review files inside the repository. Ask the requester to copy the file into the repo and resubmit.",
  "completed_at": "<UTC timestamp>"
}
```

The daemon reads `error` from the sidecar and surfaces it to the requester
as the `FailureReason` on the completed request — so the message above is
what the user sees. Phrase it clearly: "cannot reach &lt;path&gt;" plus a
short reason and the corrective action.

This guard exists because a previous request
(`req_20260502_204250_1944dc`) hung for the full 30-minute timeout pointing
at a plan file under `~/.claude/plans/`. The skill should fail in seconds,
not minutes.

Conceptual scopes that name no filesystem paths at all (e.g. "the
error-handling patterns across the simulation layer") pass this check —
only paths are validated.

## Step 1.5: Parent Context (for follow-up reviews)

If the request has a `**Parent:** req_<id>` field:

1. Read `AgentCoordination/opencodereview/completed_review_requests/req_<id>.md`. If the
   parent is not in `completed/`, write `result.json` with
   `{"error": "parent request not yet completed"}` and exit.
2. Extract parent context by calling:
   ```bash
   python Tools/agent_coordination/parse_results.py AgentCoordination/opencodereview/completed_review_requests/req_<id>.md
   ```
   This prints the `## Results` section fields as JSON. The `Report` value
   is the path to the parent's `report.md`. The parser also returns
   `review_dir` (the directory containing the report).
3. **Derive the parent's `result.json` path** from the parsed `Report`
   value's parent directory:
   ```
   parent_result_json = Path(parsed["Report"]).parent / "result.json"
   # Equivalent: Path(parsed["review_dir"]) / "result.json"
   ```
   Read it for structured findings data (counts, verification matrix from
   prior follow-ups, etc.).
4. Read the parent's `report.md` (the `Report` path itself) for full
   finding text and context.
5. Pass both to your review agents as authoritative prior context.

The review must explicitly:
- Verify each finding the follow-up asks about (status: resolved /
  partially-resolved / unresolved / regressed).
- Surface any new issues introduced by the fixes.

## Step 2: Determine Review Directory

Extract the review directory path from the arguments. The daemon passes it
as part of the prompt: `Use review directory: Reviews/results/.../`.

If a `REVIEW_DIR` path was provided (daemon invocation), use it directly.
It already has `findings/` created.

If no `REVIEW_DIR` was provided (interactive invocation), create one:
```bash
python Reviews/scripts/create_review.py general "{slugified_title}"
```
Record the output path. Create `findings/` directory within it.

## Step 3: Execute the Review

The execution path depends on the review type.

### Type: code, general, consistency

Full code review using the review swarm protocol:

1. **Read documentation reference:**
   ```
   docs/01_ARCHITECTURE.md
   docs/02_PATTERNS.md
   docs/03_CONVENTIONS.md
   ```
   If the scope intersects specific systems, also read relevant `docs/systems/`
   or `docs/guides/` files.

2. **Read parent context** (Step 1.5, for follow-ups).

3. **Write scope document** to `{REVIEW_DIR}/scope.md`:
   ```markdown
   # Review Scope: {review_name}
   **Type:** {review_type} (delegated by Claude Code)
   **Request ID:** {request_id}
   **Scope:** {from request file}
   **Instructions:** {from request file}
   **Context:** {from request file}
   ```

4. **Determine agent configuration** based on scope size:
   - 1-10 files → 3-4 agents (Code Quality, Architecture, Test Coverage)
   - 10-50 files → 5-7 agents (add Security, Error Handling, Dead Code)
   - 50+ files → 8-12 agents (full spectrum)
   
   Select agents from the catalog in `Reviews/protocols/00_review_core.md`
   based on the review type and instructions.

5. **Launch review agents** in parallel using the Task tool with
   `subagent_type: general`. Each agent receives the standard prompt template
   from `Reviews/protocols/00_review_core.md` Phase C, customized with:
   - The scope files/directories
   - The specific instructions from the request
   - The docs/ reference content
   - Parent review context (for follow-ups, include the parent findings as
     prior art to check against)
   
   Each agent writes to `{REVIEW_DIR}/findings/{agent_name}_report.md`.

6. **Compile findings:**
   ```bash
   python Reviews/scripts/compile_findings.py {REVIEW_DIR}
   ```

7. **Validate findings** (skip for quick reviews — only for normal/deep):
   ```bash
   python Reviews/scripts/validate_findings.py {REVIEW_DIR} --format markdown
   ```
   Launch 2-4 validator agents, then:
   ```bash
   python Reviews/scripts/filter_validated_findings.py {REVIEW_DIR}
   ```

8. **For follow-ups**, add a "Verification Matrix" section at the top of
   `report.md`:
   ```markdown
   ## Verification Matrix
   | Parent Finding | Status | Notes |
   |---|---|---|
   | CRIT-001 | resolved | Fix at game/foo.py:42 addresses root cause |
   | MAJ-003 | partially-resolved | Edge case in bar() still unhandled |
   ```

### Type: tests

Focus on test quality, coverage gaps, and test patterns:

1. Read `docs/03_CONVENTIONS.md` for test conventions
2. Identify test files corresponding to the scope using glob patterns
3. Analyze for: missing edge cases, weak assertions, test isolation issues,
   mocking patterns, fixture usage
4. Write findings directly to `{REVIEW_DIR}/report.md`

### Type: plan, architecture

Document/design review — no code analysis needed:

1. Read all referenced documents from the Scope section
2. Also read `docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md` for
   architectural reference
3. Analyze for compatibility, pattern consistency, missing edge cases,
   integration concerns, performance implications, testability
4. Write directly to `{REVIEW_DIR}/report.md`

### Type: security, performance

Specialized reviews following `Reviews/protocols/05_security_review.md`
or `Reviews/protocols/06_performance_review.md`:

1. Read the relevant protocol
2. Use 2-4 focused agents (or inline analysis for small scope)
3. Write to `{REVIEW_DIR}/report.md`

### Type: custom

Follow the instructions literally. Read the scope, follow the instructions,
write findings.

## Step 4: Write result.json Sidecar

After the report is written, write a `result.json` sidecar to the review
directory. If a specific path was provided by the daemon, use that exact path:

```json
{
  "request_id": "req_<timestamp>",
  "review_dir": "Reviews/results/2026-05-02_070000_general_combat-refactor_req-20260502_070000",
  "report_path": "Reviews/results/2026-05-02_070000_general_combat-refactor_req-20260502_070000/report.md",
  "findings": {
    "critical": 2,
    "major": 8,
    "minor": 10,
    "info": 3
  },
  "completed_at": "2026-05-02T07:30:00Z",
  "parent_request_id": "req_20260502_063000",
  "verification": {
    "CRIT-001": "resolved",
    "MAJ-003": "partially-resolved"
  }
}
```

- `findings` — aggregate counts from the compiled report.
- `parent_request_id` — present only for follow-up reviews.
- `verification` — present only for follow-ups; maps parent finding IDs to
  status: `resolved`, `partially-resolved`, `unresolved`, or `regressed`.

Do NOT move or rename the request file — the daemon handles that.

## Step 5: Log Skill Usage

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-review-request
```

## Error Handling

If the review fails at any point:
1. Write an error `result.json` to the review directory:
   ```json
   {
     "request_id": "req_<id>",
     "error": "description of what went wrong",
     "completed_at": "2026-05-02T07:30:00Z"
   }
   ```
2. The daemon reads `error` from the sidecar and moves the request to
   `completed/` with `Status: failed` and `FailureReason: <error>`.
3. **Never write Status directly** — the daemon owns the lifecycle. The
   skill always communicates failure through the `error` key in
   `result.json`, never through the request file's frontmatter.

If `create_review.py` fails (interactive mode only):
- Fall back to creating the directory structure manually
- Write a minimal scope.md and report.md

If agent subprocesses fail:
- Retry once with fewer agents
- Write partial findings if some agents succeeded
