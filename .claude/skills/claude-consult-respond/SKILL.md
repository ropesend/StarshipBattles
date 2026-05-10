---
name: claude-consult-respond
description: Respond to a `consult/v1` request from another agent. Invoked when codex or opencode shells out to `claude -p` with a request to load this skill. Reads the request artifact at the supplied path, advises within the permission contract (read repo + run tests when allowed; write only inside the consult leaf), and writes a complete `response.md` per the harmonized schema. NOT a delegation channel — the initiator owns synthesis and action; you advise only.
argument-hint: --request <path-to-request.md> [--response <path-to-response.md>]
---

# Cross-Agent Consult — Claude Responds

You are responding to a `consult/v1` request from a partner agent (codex
or opencode). The partner shelled out to `claude -p` and asked you to
load this skill. You read the request, advise within the permission
contract, and write a complete response artifact. The partner waits on
your subprocess exit; do NOT loiter.

The harmonized contract this skill implements lives at
`AgentCoordination/Scratchpad/Discussion/20260509T170814Z_consult-discuss-harmonize/plans/consult_harmonization_r002.md`.
Helper module: `Tools/agent_coordination/partner_invoke.py`.

## Permission contract (NON-NEGOTIABLE)

You MAY:
- Read any repo file (subject to standard `docs/_ignore/` exclusion).
- Run tests **only if** the request frontmatter has `allow_tests: true`
  AND the mode is `pre-final-check` or `deep-dive`.
- Write only inside the `consult_leaf` directory named in the request
  frontmatter — `response.md`, `log.txt`, scratch files under that leaf.

You MUST NOT:
- Edit any production code, docs, tickets, projects, or configs.
- Create commits, branches, or pull requests.
- Modify any other Scratchpad leaf.
- Implement on the initiator's behalf — advise only.

If you find yourself wanting to "fix it for them," stop. Surface the fix
in `## Findings` instead.

## Step 1 — Parse arguments

```powershell
$RequestPath = ''
$ResponsePath = ''
$Idx = 0
while ($Idx -lt $args.Length) {
  switch ($args[$Idx]) {
    '--request'  { $RequestPath  = $args[$Idx+1]; $Idx += 2 }
    '--response' { $ResponsePath = $args[$Idx+1]; $Idx += 2 }
    default { break }
  }
}
if (-not $RequestPath) {
  Write-Output 'ABORT: --request <path> required'; exit 1
}
if (-not (Test-Path -LiteralPath $RequestPath)) {
  Write-Output "ABORT: request file not found: $RequestPath"; exit 1
}
```

If `--response` is omitted, default to `<request-leaf>/response.md`:

```powershell
if (-not $ResponsePath) {
  $ResponsePath = Join-Path (Split-Path -Parent $RequestPath) 'response.md'
}
```

## Step 2 — Read and validate the request

The request frontmatter contract (per `consult_harmonization_r002.md:23-26`):

```yaml
---
protocol: consult/v1
from: <codex|opencode>
to: claude
mode: <planning|mid-project-review|pre-final-check|deep-dive>
allow_tests: <true|false>
created_at_utc: <ISO 8601 UTC>
repo_root: <abs-path>
consult_leaf: <abs-path>
complete: true
---
```

Validate via the helper:

```bash
python -c "
import sys
sys.path.insert(0, r'<repo-root>/Tools/agent_coordination')
import partner_invoke
fields = partner_invoke.parse_frontmatter(open(r'<request-path>', encoding='utf-8').read())
required = {'protocol','from','to','mode','allow_tests','created_at_utc','repo_root','consult_leaf','complete'}
missing = required - set(fields)
print('OK' if not missing and fields.get('complete') == 'true' and fields.get('to') == 'claude' else f'INVALID: missing={missing} to={fields.get(\"to\")} complete={fields.get(\"complete\")}')
"
```

If invalid, write an error response with `error_kind: missing-response`
(yes, that kind covers "request was malformed" too — there's no
dedicated kind for it, and surfacing the error is more important than
labeling it precisely):

```bash
python -c "
import sys
sys.path.insert(0, r'<repo-root>/Tools/agent_coordination')
import partner_invoke
from pathlib import Path
partner_invoke.write_error_response(
    Path(r'<response-path>'),
    from_agent='claude',
    to_agent='<request-from>',
    mode='<request-mode>',
    error_kind='missing-response',
    detail='Request file failed validation: <reason>',
)
"
```

Then exit cleanly so the partner subprocess sees a complete artifact.

## Step 3 — Read the request body and constraints

Read the request body. Pay attention to:

- `## Question` — the actual ask.
- `## Repo state` — branch + `git status --short` snapshot. Treat this as
  the source of truth for what the initiator is currently working on.
- `## Constraints` — the canonical consult prompt block embedded by the
  initiator. The single source of truth lives at
  `AgentCoordination/protocols/consult_prompt_block.md`; read THAT file
  directly (not the embedded copy in the request) so you're acting on the
  authoritative version. The embedded copy is for context, not authority.
- `## Specific asks` — the schema and section ordering for `response.md`.

Re-read these before drafting. Do not paraphrase the constraints in your
response; cite by reference where relevant.

## Step 4 — Advise

This is the actual consultation. Per the mode:

| Mode | What to do |
|------|------------|
| `planning` | Propose 1-3 approaches, name risks each carries, identify which tests + docs would change. NO code. |
| `mid-project-review` | Read the diff implied by `git status --short`, evaluate the work-in-progress against the question, point out concrete issues with `file:line` citations. NO code edits. |
| `pre-final-check` | Run tests if `allow_tests: true`. Look for missed tests, missing docs updates, layer violations, broad `except` without justification, 500-LOC violations on touched files. Cite `file:line`. |
| `deep-dive` | Same as `pre-final-check` but you may do multiple search/read passes; the initiator will follow up. |

Across all modes:

- Material claims need evidence: `file:line`, command output, transcript
  reference, or `[unverified]` label.
- Run tests only when both `allow_tests: true` and the mode is one of
  `pre-final-check`/`deep-dive`.
- Do NOT propose backward-compat shims, fallback systems, monkey patches,
  or save-file migrations (per the standard prompt block).
- Do NOT read or cite anything under `docs/_ignore/`.
- Do NOT touch any file outside the consult leaf.

If a question genuinely cannot be answered without information you don't
have access to, say so under `## Open questions` rather than speculating.

## Step 5 — Compose `response.md` (explicit write — MANDATORY)

You MUST call `partner_invoke.atomic_write_text` (or an equivalent
file-write tool) to publish `response.md` at the path the initiator
named. **Final-message capture via `--output-last-message` is NOT an
acceptable substitute** — the wrapper validates the file after harvest
(`partner_invoke.invoke_sync` runs `validate_response_file` automatically
since 2026-05-09 smoke fixes), and an invalid capture gets moved aside
to `*.invalid-output-<timestamp>.txt` while the result downgrades to
`error_kind: missing-response`. If your file write fails, write an
explicit error stub (see "Failure-mode handling" below) — never let the
captured chat output stand in.

### exit_status values

- `ok` — you answered all the asks within the permission contract.
- `partial` — you answered some but not all; explain what you couldn't
  cover (and why) under `## Open questions`. The wrapper accepts this
  per `_VALID_EXIT_STATUSES` in `partner_invoke.py`.
- `error` — see Failure-mode handling. Use `write_error_response` rather
  than constructing the body by hand.

Required schema (per `consult_harmonization_r002.md:28-45` and the
`partner_invoke.validate_response_file` helper):

```markdown
---
protocol: consult/v1
from: claude
to: <initiator-from-request>
mode: <same as request>
created_at_utc: <ISO 8601 UTC>
complete: true
exit_status: ok            # or: partial | error
---

## Findings

[Direct answers to the request's `## Question` and `## Specific asks`.
 Evidence-cited. Mode-appropriate (planning = approaches; review = issues
 with citations; pre-final-check = test/doc/convention gaps).]

## Risks

[What you think the initiator might miss. Concrete and cited where
 possible. If you have nothing to add, write a single line saying so —
 do NOT pad.]

## Open questions

[What you lack information to advise on. Do NOT speculate. REQUIRED
 content if `exit_status: partial` — name the asks you couldn't cover
 and why. If `exit_status: ok` and everything was answerable, write a
 single line saying so.]
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

Calling `validate_response_file` after writing catches schema mistakes
before the partner harvests. If validation raises, fix the schema and
rewrite (atomic temp+rename keeps the partial write out of the partner's
view). If you cannot produce a valid artifact at all, fall through to
Failure-mode handling and use `write_error_response`.

## Step 6 — Exit

The partner subprocess waits on your exit. Do NOT loiter, ask the user
follow-up questions, or write any files outside the consult leaf. If
the initiator wants to follow up, they will issue a new request — that
becomes a separate skill invocation.

Print a short success line to stdout (the partner captures it for the
log) and exit:

```text
consult/v1 response written: <abs-path-to-response.md>
```

## Failure-mode handling

If something goes wrong AFTER successful request validation (e.g., you
can't read a file the question depends on, a test runner is missing,
permission denied), still publish a complete error response so the
partner sees a finished artifact:

```bash
python -c "
import sys
sys.path.insert(0, r'<repo-root>/Tools/agent_coordination')
import partner_invoke
from pathlib import Path
partner_invoke.write_error_response(
    Path(r'<response-path>'),
    from_agent='claude',
    to_agent='<request-from>',
    mode='<request-mode>',
    error_kind='nonzero-exit',
    detail='<one-line description of what failed>',
)
"
```

Then exit non-zero so the initiator knows to surface the error to the user.

## Notes & gotchas

- **You are inside a partner's subprocess.** The user is not watching this
  session. Do NOT prompt for input, do NOT propose interactive follow-ups,
  do NOT wait. Whatever you write to `response.md` is what the initiator
  sees.
- **No multi-turn here.** This skill is single round-trip. If the question
  needs follow-up, the initiator issues a fresh request (potentially
  reusing the same leaf with `request_002.md` etc.).
- **The leaf is the world.** Treat anything outside `consult_leaf` as
  read-only. The permission contract is enforced by you, not by the CLI
  sandbox — see `partner_cli.md` "Sandbox is policy, not enforcement"
  caveat.
- **Standard prompt block.** Already injected into the request body
  verbatim. Honor it; don't restate it back to the initiator unless they
  asked.
