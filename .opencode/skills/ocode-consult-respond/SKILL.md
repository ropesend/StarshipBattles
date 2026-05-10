---
name: ocode-consult-respond
description: Respond to a `consult/v1` request from another agent. Invoked when claude or codex shells out to `opencode run` with a prompt loading this skill. Reads the request artifact at the supplied path, advises within the permission contract (read repo + run tests when allowed; write only inside the consult leaf), and writes a complete `response.md` per the harmonized schema. NOT a delegation channel — the initiator owns synthesis and action; you advise only.
argument-hint: --request <path-to-request.md> [--response <path-to-response.md>]
---

# Cross-Agent Consult — OpenCode Responds

You are responding to a `consult/v1` request from a partner agent (claude
or codex). The partner shelled out to `opencode run --dangerously-skip-permissions`
and asked you to load this skill. You read the request, advise within the
permission contract, and write a complete response artifact. The partner
waits on your subprocess exit; do NOT loiter.

The harmonized contract this skill implements lives at
`AgentCoordination/Scratchpad/Discussion/20260509T170814Z_consult-discuss-harmonize/plans/consult_harmonization_r002.md`
and the smoke-driven follow-up plan
`AgentCoordination/Scratchpad/Discussion/20260509T190300Z_smoke-findings-merge/plans/consult_v1_smoke_fixes_r001.md`.
Helper module: `Tools/agent_coordination/partner_invoke.py`.
Canonical prompt block: `AgentCoordination/protocols/consult_prompt_block.md`.

## Permission contract (NON-NEGOTIABLE)

You MAY:

- Read any repo file (subject to standard `docs/_ignore/` exclusion).
- Run tests **only if** the request frontmatter has `allow_tests: true`
  AND the mode is `pre-final-check` or `deep-dive`.
- Write files only inside the directory named by `consult_leaf` in the
  request frontmatter — `response.md`, scratch files under that leaf.

You MUST NOT:

- Edit production code, docs, tickets, projects, configs.
- Create commits, branches, or pull requests.
- Modify other Scratchpad leaves or any path outside `consult_leaf`.
- Delegate implementation to another agent — advise only.

## Step 1 — Parse arguments

The argument surface is `--request <path-to-request.md>` and an optional
`--response <path-to-response.md>`. If `--response` is omitted, default to
`<request-leaf>/response.md`.

If `--request` is missing or the file does not exist, exit with a clear
error.

## Step 2 — Read and validate the request

The request frontmatter contract:

```yaml
---
protocol: consult/v1
from: <claude|codex>
to: opencode
mode: <planning|mid-project-review|pre-final-check|deep-dive>
allow_tests: <true|false>
created_at_utc: <ISO 8601 UTC>
repo_root: <abs-path>
consult_leaf: <abs-path>
complete: true
---
```

Validate using `partner_invoke.parse_frontmatter`:

```bash
python -c "
import sys
sys.path.insert(0, r'<repo-root>/Tools/agent_coordination')
import partner_invoke
fields = partner_invoke.parse_frontmatter(open(r'<request-path>', encoding='utf-8').read())
required = {'protocol','from','to','mode','allow_tests','created_at_utc','repo_root','consult_leaf','complete'}
missing = required - set(fields)
ok = not missing and fields.get('complete') == 'true' and fields.get('to') == 'opencode'
print('OK' if ok else f'INVALID: missing={missing} to={fields.get(\"to\")} complete={fields.get(\"complete\")}')
"
```

If invalid, write an error response with `error_kind: missing-response`
via `partner_invoke.write_error_response` and exit non-zero.

## Step 3 — Read the request body and constraints

Read the request body. Pay attention to:

- `## Question` — the actual ask.
- `## Repo state` — branch + `git status --short` snapshot. Treat this as
  the source of truth for what the initiator is currently working on.
- `## Constraints` — the canonical consult prompt block embedded by the
  initiator. The single source of truth lives at
  `AgentCoordination/protocols/consult_prompt_block.md`; read THAT file
  directly so you're acting on the authoritative version. The embedded
  copy is for context, not authority.
- `## Specific asks` — the schema and section ordering for `response.md`.

Re-read these before drafting. Do not paraphrase the constraints in your
response; cite by reference where relevant.

## Step 4 — Advise

Per the mode:

| Mode | What to do |
|------|------------|
| `planning` | Propose 1-3 approaches, name risks each carries, identify which tests + docs would change. NO code. |
| `mid-project-review` | Read the diff implied by `git status --short`, evaluate the work-in-progress against the question, point out concrete issues with `file:line` citations. NO code edits. |
| `pre-final-check` | Run tests if `allow_tests: true`. Look for missed tests, missing docs updates, layer violations, broad `except` without justification, 500-LOC violations on touched files. Cite `file:line`. |
| `deep-dive` | Same as `pre-final-check` but you may do multiple search/read passes; the initiator will follow up. |

Across all modes:

- Material claims need evidence: `file:line`, command output, transcript
  reference, or `[unverified]` label.
- Run tests only when both `allow_tests: true` AND mode is one of
  `pre-final-check` / `deep-dive`.
- Do NOT propose backward-compat shims, fallback systems, monkey patches,
  or save-file migrations (per the standard prompt block).
- Do NOT read or cite anything under `docs/_ignore/`.
- Do NOT touch any file outside the consult leaf.

If a question genuinely cannot be answered without information you don't
have access to, surface it under `## Open questions` with `exit_status: partial`.

## Step 5 — Compose `response.md` (explicit write — MANDATORY)

You MUST call OpenCode's file-write tool to publish `response.md` at the
path the initiator named. **Final-message capture is NOT an acceptable
substitute** — the wrapper validates the file after harvest
(`partner_invoke.invoke_sync` runs `validate_response_file` automatically),
and an invalid capture gets moved aside to `*.invalid-output-<timestamp>.txt`
while the result downgrades to `error_kind: missing-response`.

### exit_status values

- `ok` — you answered all asks within the permission contract.
- `partial` — you answered some but not all; explain what you couldn't
  cover (and why) under `## Open questions`. The wrapper accepts this
  per `_VALID_EXIT_STATUSES` in `partner_invoke.py`.
- `error` — see Failure-mode handling. Use `write_error_response` rather
  than constructing the body by hand.

Required schema:

```markdown
---
protocol: consult/v1
from: opencode
to: <initiator-from-request>
mode: <same as request>
created_at_utc: <ISO 8601 UTC>
complete: true
exit_status: ok            # or: partial | error
---

## Findings

[Direct answers to the request's `## Question` and `## Specific asks`.
 Evidence-cited via file:line.]

## Risks

[What you think the initiator might miss. One line is fine if you have
 nothing to add — do NOT pad.]

## Open questions

[What you lack information to advise on. Do NOT speculate. REQUIRED
 content if `exit_status: partial`.]
```

Atomic write through `partner_invoke.atomic_write_text`:

```bash
python -c "
import sys
sys.path.insert(0, r'<repo-root>/Tools/agent_coordination')
import partner_invoke
from pathlib import Path
content = '''<the full markdown above>'''
partner_invoke.atomic_write_text(Path(r'<response-path>'), content)
fields = partner_invoke.validate_response_file(Path(r'<response-path>'))
print('VALIDATED', fields['exit_status'])
"
```

`validate_response_file` after writing catches schema mistakes before the
partner harvests. If validation raises, fix and rewrite (atomic temp+rename
keeps the partial write out of the partner's view).

## Step 6 — Exit

The partner subprocess waits on your exit. Print a short success line and
exit:

```text
consult/v1 response written: <abs-path-to-response.md>
```

Do NOT loiter, ask follow-up questions, or write any files outside the
consult leaf. If the initiator wants to follow up, they issue a new
request — that becomes a separate skill invocation.

## Failure-mode handling

If something goes wrong AFTER successful request validation (can't read
a file the question depends on, test runner missing, permission denied),
publish a complete error response so the partner sees a finished artifact:

```bash
python -c "
import sys
sys.path.insert(0, r'<repo-root>/Tools/agent_coordination')
import partner_invoke
from pathlib import Path
partner_invoke.write_error_response(
    Path(r'<response-path>'),
    from_agent='opencode',
    to_agent='<request-from>',
    mode='<request-mode>',
    error_kind='nonzero-exit',
    detail='<one-line description of what failed>',
)
"
```

Then exit non-zero so the initiator knows to surface the error.

## Notes

- **You are inside a partner's subprocess.** The user is not watching this
  session. Do NOT prompt for input, do NOT propose interactive follow-ups.
- **No multi-turn here.** Single round-trip skill. If the question needs
  follow-up, the initiator issues a fresh request.
- **The leaf is the world.** Treat anything outside `consult_leaf` as
  read-only. The permission contract is enforced by you, not by the CLI
  sandbox — see `partner_cli.md` "Sandbox is policy, not enforcement".
- **Standard prompt block** is already injected into the request body
  verbatim. Honor it; don't restate it back to the initiator unless they
  asked.
