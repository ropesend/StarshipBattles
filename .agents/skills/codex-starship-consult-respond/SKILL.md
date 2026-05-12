---
name: codex-starship-consult-respond
description: Respond as Codex to Starship Battles consult/v1 request files created by Claude Code or OpenCode. Use when a partner agent invokes Codex non-interactively with a request path for advisory planning, review, pre-final checks, or deep-dive feedback without allowing Codex to edit project files.
---

# Codex Starship Consult Respond

Respond to a partner-created `consult/v1` request. This is advisory only. Do not implement, patch, stage, commit, branch, or modify tracked project artifacts.

Reference:

- `AgentCoordination/protocols/partner_cli.md`
- `AgentCoordination/protocols/consult_prompt_block.md`

## Input

Argument surface:

```text
--request <path>
```

The request path must point to a `request.md` file with `protocol: consult/v1` and `complete: true`.

## Read And Validate

1. Read `request.md`.
2. Validate frontmatter fields: `protocol`, `from`, `to`, `mode`, `allow_tests`, `created_at_utc`, `repo_root`, `consult_leaf`, and `complete`.
3. Confirm `to: codex`.
4. Confirm `complete: true`.
5. Work from `repo_root`, not from a hardcoded checkout path.
6. Use `consult_leaf` for `response.md`, `log.txt`, and any temporary transfer notes.
7. Read the canonical prompt block from `AgentCoordination/protocols/consult_prompt_block.md` under `repo_root`. Honor it as the shared constraint source; do not rely only on the request body's copy if the file exists.

If validation fails, write `response.md` with `exit_status: error` and a concise `## Open questions` entry naming the invalid field.

## Permissions

Allowed:

- Read repo files, except `docs/_ignore/`.
- Run searches and read command output.
- Run tests only when the request has `allow_tests: true` and the mode is `pre-final-check` or `deep-dive`.
- Write `response.md`, `log.txt`, or temporary notes only inside `consult_leaf`.

Forbidden:

- Do not edit production code.
- Do not edit tracked docs.
- Do not edit tickets, projects, configs, or protocol files.
- Do not stage, commit, branch, push, or open PRs.
- Do not delegate implementation to another agent.
- Do not read `docs/_ignore/`.

## Context Rules

For coding or design advice, read the standard Starship docs before making material claims:

1. `docs/README.md`
2. `docs/01_ARCHITECTURE.md`
3. `docs/02_PATTERNS.md`
4. `docs/03_CONVENTIONS.md`
5. Task-specific docs named or implied by the request

Use evidence. Cite file paths, line numbers, command summaries, or test output for material claims. Label unchecked claims `[unverified]`.

Run tests only when allowed. If tests are not allowed, suggest the relevant tests instead of running them.

## Response Format

You must write `response.md` explicitly inside `consult_leaf`. Publish through a same-directory `.tmp_*` file and final rename. Final-message capture is not an acceptable fallback for the responder; it is only a caller-side safety net and may contain ordinary chat output.

### How to write the file

**Use your native file-write tool (e.g., `apply_patch`)** against the consult leaf. The caller invokes you with `--sandbox workspace-write` so writes inside the workspace (which includes `consult_leaf` under `AgentCoordination/Scratchpad/Consult/`) succeed.

**Do NOT shell out to `powershell.exe`, `cmd.exe`, `bash`, `python`, or any other process** to write the file. Shell exec calls add no value over `apply_patch` and risk being declined by approval rules or constrained-language-mode policies, falling through to "final-message capture" which the harvester treats as `missing-response`.

The atomic write is two operations against the leaf:

1. Write the response body to `<consult_leaf>/.tmp_<random>.md` via `apply_patch`.
2. Move/rename `<consult_leaf>/.tmp_<random>.md` to `<consult_leaf>/response.md` via `apply_patch` (or a single direct write to `response.md` if your patch surface doesn't expose a rename — that's still preferable to a shell exec).

### Sandbox note — important

`--sandbox workspace-write` grants you write access to the entire workspace, not only the consult leaf. **You are still bound by the Permissions section above:** write ONLY inside `consult_leaf`. Do not modify production code, tracked docs, tickets, projects, configs, or protocols. The sandbox is a permission ceiling, not your permission floor. If you violate this contract, the caller (Claude) will see the diff in `git status` after the consult and route the disobedience to the user.

If `apply_patch` is rejected, set `exit_status: partial`, name the rejection cause in `## Open questions`, and emit the response artifact as your final assistant message. The caller's harvester will surface this as a missing-response failure so the user can route the fix to the wrapper or sandbox policy.

```yaml
---
protocol: consult/v1
from: codex
to: <request.from>
mode: <same as request>
created_at_utc: <ISO8601>
complete: true
exit_status: ok
---
```

Body sections, in this order:

```markdown
## Findings

<Direct answers to the request's specific asks. Cite evidence.>

## Risks

<Likely misses, weak assumptions, or implementation hazards.>

## Open questions

<Only questions that block or materially affect the advice. Use "None." if empty.>
```

Use `exit_status: partial` when useful advice is possible but context is incomplete; in that case, `## Open questions` must state what context or evidence is missing. Use `exit_status: error` only when the request cannot be processed.

Error response shape:

```yaml
---
protocol: consult/v1
from: codex
to: <request.from>
mode: <same as request>
created_at_utc: <ISO8601>
complete: true
exit_status: error
error_kind: invocation-failed
partner_completed: false
---
```

## Behavioral Contract

Answer as an independent reviewer, not as an executor. Push back when the request conflicts with Starship rules. Do not agree by default. Keep feedback actionable and bounded to the request.
