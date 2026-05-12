---
name: claude-consult
description: Pairwise advisory consult with another agent (codex, gemini, or opencode). Single round-trip, autonomous — Claude shells out to the partner CLI directly, no daemon, no manual user invocation on the partner side. Use when you want a second set of eyes/brains on a question, plan, or piece of code; or as the opening move in solving a problem where another perspective helps. NOT a delegation channel — you (the initiator) own synthesis and action; the partner advises only.
argument-hint: --with <codex|gemini|opencode> [--mode <planning|mid-project-review|pre-final-check|deep-dive>] [--model <id>] [--allow-tests] [--slug <kebab>] [--timeout-sec <int>] <question...>
---

# Cross-Agent Consult — Claude Initiates

You are opening a single-round consult with another agent (codex, gemini,
or opencode). The partner's CLI is invoked directly via subprocess; the
user does NOT invoke any skill on the partner side. Gemini in particular
runs with no installed responder skill — the full instruction set is
embedded in the prompt itself (Pattern A: read-only + wrapper-writes).

The harmonized contract this skill implements lives at
`AgentCoordination/Scratchpad/Discussion/20260509T170814Z_consult-discuss-harmonize/plans/consult_harmonization_r002.md`.
Per-agent CLI recipes: `AgentCoordination/protocols/partner_cli.md`.
Subprocess helper: `Tools/agent_coordination/partner_invoke.py`.

This is advisory, not delegation. **You** own synthesis and any action
taken on the partner's response. They advise; they do not implement.

## Modes

| Mode | Default sandbox | Tests | Use when |
|------|-----------------|-------|----------|
| `planning` | read-only | no | Approach, risks, tests, doc impact (default) |
| `mid-project-review` | read-only | no | Pass current state + diff summary, act on valid feedback |
| `pre-final-check` | workspace-write | yes (opt-in) | Catch missed tests, docs, conventions, layer violations |
| `deep-dive` | workspace-write | yes (opt-in) | Multiple follow-ups until advice converges |

`--allow-tests` is required to flip Codex's sandbox to `workspace-write`
even on `pre-final-check` / `deep-dive`.

## Step 1 — Parse arguments and resolve repo root

```powershell
function Get-RepoRoot {
  $root = (git rev-parse --show-toplevel 2>$null)
  if ($LASTEXITCODE -eq 0 -and $root) { return $root.Trim() }
  throw 'Unable to discover repository root.'
}

$RepoRoot = Get-RepoRoot
$Partner = ''
$Mode = 'planning'
$Model = ''
$AllowTests = $false
$Slug = ''
$TimeoutSec = 600
$Idx = 0
while ($Idx -lt $args.Length) {
  switch ($args[$Idx]) {
    '--with'    { $Partner = $args[$Idx+1]; $Idx += 2 }
    '--mode'    { $Mode = $args[$Idx+1]; $Idx += 2 }
    '--model'   { $Model = $args[$Idx+1]; $Idx += 2 }
    '--slug'    { $Slug = $args[$Idx+1]; $Idx += 2 }
    '--allow-tests' { $AllowTests = $true; $Idx += 1 }
    '--timeout-sec' { $TimeoutSec = [int]$args[$Idx+1]; $Idx += 2 }
    default { break }
  }
}
if ($Partner -notin @('codex','gemini','opencode')) {
  Write-Output "ABORT: --with must be codex, gemini, or opencode (got '$Partner')"
  exit 1
}
if ($Mode -notin @('planning','mid-project-review','pre-final-check','deep-dive')) {
  Write-Output "ABORT: --mode must be planning|mid-project-review|pre-final-check|deep-dive"
  exit 1
}
$Question = if ($args.Length -gt $Idx) { ($args[$Idx..($args.Length-1)] -join ' ') } else { '' }
if (-not $Question) { Write-Output 'ABORT: question text required'; exit 1 }
```

If the user did not supply a `--mode`, default to `planning` and tell the
user which mode was selected. If the user invoked the skill without a
question, ask them what they want consulted on rather than guessing.

## Step 1.5 — Gemini auth precondition (only when `--with gemini`)

```powershell
if ($Partner -eq 'gemini') {
  $haveAuth = (
    $env:GEMINI_API_KEY -or
    $env:GOOGLE_GENAI_USE_VERTEXAI -or
    $env:GOOGLE_GENAI_USE_GCA -or
    (Test-Path -LiteralPath "$env:USERPROFILE\.gemini\settings.json")
  )
  if (-not $haveAuth) {
    Write-Output @"
ABORT: gemini binary present but no auth configured.
- Google AI Ultra / Gemini Advanced subscription: set `$env:GOOGLE_GENAI_USE_GCA = "true"` and run `gemini auth login` to OAuth via your Google account.
- Standalone API key: set `$env:GEMINI_API_KEY = "<key>"`.
- Vertex AI project: set `$env:GOOGLE_GENAI_USE_VERTEXAI = "true"`.
Then re-run claude-consult.
"@
    exit 1
  }
}
```

The check is gemini-specific because gemini-cli refuses to run without
one of these. Codex/Claude/OpenCode have their own auth mechanisms
documented in `partner_cli.md` and are not validated here.

## Step 2 — Create the consult leaf

```powershell
$timestamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$ChildLeaf = if ($Slug) { "${timestamp}_${Slug}" } else { $timestamp }
$ConsultParent = Join-Path $RepoRoot 'AgentCoordination\Scratchpad\Consult'
$Leaf = Join-Path $ConsultParent $ChildLeaf
New-Item -ItemType Directory -Force -Path $Leaf | Out-Null
Write-Output "Consult leaf: $Leaf"
```

## Step 3 — Capture repo state snapshot

```powershell
$gitStatus = git status --short 2>&1 | Out-String
$branch = (git rev-parse --abbrev-ref HEAD 2>&1).Trim()
Set-Content -LiteralPath (Join-Path $Leaf 'git_status.txt') -Value $gitStatus -Encoding utf8
```

If `git status --short` is empty, write an empty file — that's a meaningful
signal (clean tree). Do NOT skip the file.

## Step 4 — Compose `request.md`

The schema is fixed (per `consult_harmonization_r002.md:23-26`). Use atomic
temp+rename with **UTF-8 No-BOM** writes — PowerShell 5.1's
`Set-Content -Encoding utf8` writes a BOM that breaks Python's `json.loads`
and other strict UTF-8 readers (smoke finding 2026-05-09).

The `## Constraints` section is the canonical consult prompt block read
verbatim from `AgentCoordination/protocols/consult_prompt_block.md` —
**do not inline a copy**. The file is the single source of truth; both
initiator and responder skills read from it.

```powershell
$now = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$RequestPath  = Join-Path $Leaf 'request.md'
$ResponsePath = Join-Path $Leaf 'response.md'
$LogPath      = Join-Path $Leaf 'log.txt'

$promptBlockPath = Join-Path $RepoRoot 'AgentCoordination\protocols\consult_prompt_block.md'
$promptBlock     = [System.IO.File]::ReadAllText($promptBlockPath, [System.Text.UTF8Encoding]::new($false))

$body = @"
---
protocol: consult/v1
from: claude
to: $Partner
mode: $Mode
allow_tests: $($AllowTests.ToString().ToLower())
created_at_utc: $now
repo_root: $RepoRoot
consult_leaf: $Leaf
complete: true
---

## Question

$Question

## Repo state

Branch: $branch

``````
$gitStatus
``````

## Constraints

Read and honor the canonical consult prompt block. The file's verbatim content follows; the source of truth is `$promptBlockPath`.

$promptBlock

## Specific asks

Reply by writing ``response.md`` in this consult leaf (path in `consult_leaf` frontmatter) with the schema:

``````yaml
---
protocol: consult/v1
from: $Partner
to: claude
mode: $Mode
created_at_utc: <ISO 8601 UTC>
complete: true
exit_status: ok            # or: partial (with explanation in ## Open questions) | error (with error_kind)
---
``````

Body sections, in order:

1. ``## Findings`` — direct answers to the question above, evidence-cited (`file:line`).
2. ``## Risks`` — what the initiator might miss.
3. ``## Open questions`` — what you lack information to advise on (do NOT speculate). REQUIRED if `exit_status: partial`.
"@

# UTF-8 No-BOM atomic write
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$tmp = Join-Path $Leaf ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
[System.IO.File]::WriteAllText($tmp, $body, $utf8NoBom)
Move-Item -LiteralPath $tmp -Destination $RequestPath
```

## Step 5 — Build the partner prompt and invoke

The partner prompt is a single string the partner CLI receives. For
codex/opencode it instructs the partner to LOAD their consult-respond
skill. For gemini there is no installed responder skill, so the prompt
is fully self-contained (Pattern A: read-only + wrapper-writes).

```powershell
$promptBlockPath = Join-Path $RepoRoot 'AgentCoordination\protocols\consult_prompt_block.md'

if ($Partner -eq 'codex') {
  $PartnerPrompt = "Load the codex-starship-consult-respond skill. Process the consult request at $RequestPath. Honor the permission contract: read-only by default; tests only if allow_tests=true. Write your response.md atomically (temp+rename) at $ResponsePath. The full schema is in the request body. Final ownership belongs to the initiator; you advise, you do not implement."
}
elseif ($Partner -eq 'opencode') {
  $PartnerPrompt = "Load the ocode-consult-respond skill. Process the consult request at $RequestPath. Honor the permission contract: read-only by default; tests only if allow_tests=true. Write your response.md atomically (temp+rename) at $ResponsePath. The full schema is in the request body. Final ownership belongs to the initiator; you advise, you do not implement."
}
elseif ($Partner -eq 'gemini') {
  # Gemini has no installed responder skill. Pattern A: gemini runs in
  # --approval-mode plan (read-only), CANNOT use file-write tools, and
  # outputs the response artifact as its final assistant message. The
  # wrapper extracts the text from stdout JSON and writes response.md.
  # Live smoke 2026-05-10 surfaced two issues this prompt addresses:
  # (1) gemini's tool layer refuses gitignored paths (Scratchpad/), so the
  #     full request body is embedded INLINE — no path-based read of
  #     request.md is required.
  # (2) when tool calls fail, gemini sometimes substitutes a different
  #     consult topic from whatever it can read. Hard rules below explicitly
  #     forbid topic substitution.
  $utf8NoBomLocal = [System.Text.UTF8Encoding]::new($false)
  $requestBodyEmbed = [System.IO.File]::ReadAllText($RequestPath, $utf8NoBomLocal)
  $PartnerPrompt = @"
You are responding to a Starship Battles consult/v1 request. Output ONLY a consult/v1 response artifact as the LAST thing in your assistant message.

The complete request is embedded below between BEGIN-REQUEST and END-REQUEST markers. The canonical consult prompt block is already inlined inside the request's `## Constraints` section; you have everything needed to answer without additional reads.

==BEGIN-REQUEST==
$requestBodyEmbed
==END-REQUEST==

Hard rules for this Pattern A invocation:
- Reads ARE allowed on tracked repo files (game/, docs/, Tools/, AgentCoordination/protocols/) when you genuinely need additional evidence to answer the embedded request.
- WRITES ARE FORBIDDEN — `--approval-mode plan` blocks them at the CLI level. Do not attempt write_file or run_shell_command.
- If a read tool call fails (gitignored path, permission denied, anything), do NOT substitute a different consult topic. Continue answering the embedded request above. Mark missing evidence under `## Open questions` and set `exit_status: partial`.
- Do NOT preamble. Do NOT announce you are about to respond. Do NOT add postamble after the artifact (commentary about what the wrapper will do, etc.). The artifact must be the LAST content in your message.

Schema (output exactly this shape; the artifact's first character is `-` of the opening `---`):

---
protocol: consult/v1
from: gemini
to: claude
mode: <copy from request frontmatter>
created_at_utc: <ISO 8601 UTC, current time>
complete: true
exit_status: ok | partial | error
---

## Findings
[evidence-cited via file:line; concise]

## Risks
[one paragraph or single line if you have nothing to add]

## Open questions
[REQUIRED if exit_status: partial — name the missing evidence; otherwise one line is fine]
"@
}

# Pick sandbox from mode (codex only — gemini and opencode ignore this).
# Codex always uses workspace-write because codex's `--sandbox read-only` blocks
# ALL writes including its own `apply_patch` against the consult leaf, even when
# `--add-dir <leaf>` is passed (verified 2026-05-12 against codex-cli 0.130.x:
# `--add-dir` extends the writable set "alongside the primary workspace" but
# does nothing when the primary workspace is read-only). The advisory-only
# contract is enforced by the codex responder skill's Permissions section,
# not by sandbox policy. `--allow-tests` is now a "yes, also run tests"
# signal; sandbox is workspace-write regardless.
$sandbox = 'workspace-write'

# Pick gemini model (other partners ignore)
$modelArg = if ($Partner -eq 'gemini' -and $Model) { $Model } else { '' }
```

Pass `model=$modelArg` to `partner_invoke.invoke_sync` when non-empty
(Python helper has `model: str | None = None` default; empty string
becomes `None`).

Always pass `expected_from=$Partner, expected_to='claude'` so the
wrapper rejects schema-shaped artifacts with reversed direction fields
(r003 Change E; codex live smoke caught a gemini artifact with
`from: codex, to: gemini` that pre-r003 validation accepted).

Now shell out via `Tools/agent_coordination/partner_invoke.py`. Use the
Bash tool (Python invocation) so we can capture the structured
`InvokeResult`:

```bash
python -c "
import json, sys
sys.path.insert(0, r'$RepoRoot/Tools/agent_coordination')
import partner_invoke
from pathlib import Path
result = partner_invoke.invoke_sync(
    '$Partner',
    '''$PartnerPrompt''',
    log_path=Path(r'$LogPath'),
    repo_root=Path(r'$RepoRoot'),
    response_file=Path(r'$ResponsePath'),
    sandbox='$sandbox',
    timeout_sec=$TimeoutSec,
    model='$modelArg' if '$modelArg' else None,
    expected_from='$Partner',
    expected_to='claude',
)
print(json.dumps({
    'exit_status': result.exit_status,
    'error_kind': result.error_kind,
    'return_code': result.return_code,
    'partner_completed': result.partner_completed,
    'log_path': str(result.log_path) if result.log_path else None,
}))
"
```

(In practice, write the python invocation as a one-shot script via the
Bash tool — quoting a multi-line `$PartnerPrompt` through PowerShell into
Python via `-c` is fragile; safer is to write `partner_prompt.txt` to the
leaf and read it from Python.)

### Safer invocation pattern

```powershell
Set-Content -LiteralPath (Join-Path $Leaf 'partner_prompt.txt') -Value $PartnerPrompt -Encoding utf8
```

Then run via Bash:

```bash
python "Tools/agent_coordination/_consult_invoke.py" \
  --partner <codex|opencode> \
  --prompt-file "<leaf>/partner_prompt.txt" \
  --log-path "<leaf>/log.txt" \
  --repo-root "<repo-root>" \
  --response-file "<leaf>/response.md" \
  --sandbox <read-only|workspace-write> \
  --timeout-sec <int>
```

The `_consult_invoke.py` thin wrapper does not yet exist; if you need it,
write it (small adapter that imports `partner_invoke`, parses argv,
prints JSON). Otherwise inline the python with `python -c "..."` and the
prompt body fetched via `Path("<leaf>/partner_prompt.txt").read_text()`.

## Step 6 — Handle the result

Parse the JSON the python invocation prints.

**Success path** (`exit_status == "ok"` and `partner_completed == true`):
- Read `response.md`.
- Validate the YAML frontmatter and required body sections (`## Findings`,
  `## Risks`, `## Open questions`).
- Summarize for the user: 2–4 sentence digest, then key actionable findings.
- Reference the response file with a markdown link so the user can open it.

**Partner ran but did not write `response.md`** (`exit_status == "ok"` and
`partner_completed == false`): write an error stub response.md per the
schema below with `error_kind: missing-response`. Surface the log path.

**Subprocess failure** (`exit_status == "error"`): write the error stub.

### Error stub schema (per r002:28-45)

```markdown
---
protocol: consult/v1
from: <partner>
to: claude
mode: <same as request>
created_at_utc: <ISO 8601 UTC>
complete: true
exit_status: error
error_kind: <timeout|nonzero-exit|missing-response|invocation-failed>
partner_completed: false
---

## Error

<one-paragraph description of what failed, referencing the log file>

## Log

See `<leaf>/log.txt` for captured stdout/stderr.
```

Atomic temp+rename, like all other consult artifacts. Then surface the
error to the user — do NOT auto-retry. Retrying spends model budget and
can duplicate side effects (test runs, etc.); the user decides.

## Step 7 — Report to the user

Tell the user:

- Consult leaf path (markdown link).
- Partner, mode, sandbox.
- Exit status. If error: error kind + log path.
- If success: 2–4 sentence summary of findings, then the actionable points.
- Reminder: you (Claude) own synthesis. Surface the response, propose next
  steps, but don't blindly act on the partner's advice without
  independently verifying material claims.

## Notes & gotchas

- **Live cross-agent invocation is unproven** in this repo (per
  `partner_cli.md`). The first time you run this skill, expect to
  surface flag-name or sandbox-policy issues. Capture the log and tell
  the user; do NOT silently retry with a different flag.
- **No worktrees.** This skill always runs the partner against the live
  working tree. The user is explicit about this — if they want a
  reproducible snapshot, they create one themselves and run the partner
  against it.
- **Multi-partner consults.** If the user wants both partners, run two
  separate pairwise consults in sequence and synthesize the answers
  yourself. Do NOT create an implicit three-way conversation.
- **Follow-ups.** Per the harmonized contract, consult is "one or more
  request/response rounds controlled by the initiator." For a follow-up,
  reuse the same leaf, write `request_002.md` / `response_002.md`, etc.
  Each round still uses atomic temp+rename and the same schema.
- **Async (`--async`).** Not implemented in v1. If the user asks, tell
  them sync is the only mode for now and ask whether they want to wait
  inline or prefer to defer until async is added.
