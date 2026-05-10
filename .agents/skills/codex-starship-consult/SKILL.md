---
name: codex-starship-consult
description: Consult Claude Code, OpenCode, or Gemini during Starship Battles work through the lightweight consult/v1 protocol. Use when Codex needs a pairwise second opinion, planning critique, mid-project review, pre-final check, or deep-dive feedback without delegating implementation or starting the heavier v2.6 discussion protocol.
---

# Codex Starship Consult

Use this skill to ask Claude, OpenCode, or Gemini for advisory feedback while Codex remains the task owner. This is a lightweight `consult/v1` workflow, not a v2.6 discussion and not an implementation delegation channel.

References:

- `AgentCoordination/protocols/partner_cli.md`
- `AgentCoordination/protocols/consult_prompt_block.md`
- `Tools/agent_coordination/partner_invoke.py`
- `AgentCoordination/Scratchpad/Discussion/20260509T170814Z_consult-discuss-harmonize/plans/consult_harmonization_r002.md`
- `AgentCoordination/Scratchpad/Discussion/20260510T132557Z_gemini-smoke-revisions/plans/add_gemini_consult_partner_r003.md`

## Role Defaults

- Use Claude as the thinking partner for architecture, ambiguous design, tradeoffs, plans, and hard root-cause reasoning.
- Use OpenCode as the coverage checker for broad repo/doc/test sweeps, convention checks, and "what did Codex miss?" reviews.
- Use Gemini for long-context second opinions, especially when a large embedded request is preferable to asking the partner to open scratchpad files directly.
- If multiple partners are requested, run independent pairwise consults and synthesize locally. This is not a three-way conversation.

## Argument Surface

Expected user shape:

```text
Use $codex-starship-consult --with <claude|opencode|gemini|both> --mode <mode> [--allow-tests] [--dry-run] [--model <gemini-model>]:
<question or project context>
```

Legacy phrasing `with <partner>` is acceptable when the user writes it naturally. `both` means Claude plus OpenCode for backward compatibility; if Gemini should be included with another partner, run each named partner as a separate pairwise consult.

Modes:

- `planning`: approach, risks, tests, doc impact. Default read-only; no tests.
- `mid-project-review`: current state, diff summary, and corrective feedback. Default read-only; no tests.
- `pre-final-check`: missed tests, docs, conventions, and layer risks. Tests only with `--allow-tests`.
- `deep-dive`: one or more follow-up rounds until advice converges. Tests only with `--allow-tests`.

Use `--dry-run` to create/show the request and command without invoking a partner. Use `--model` only for Gemini model overrides; default model selection lives in `partner_invoke.py`.

## Workflow

1. Resolve the repo root at runtime. Never hardcode a checkout path.
2. Confirm current dirty state with `git status --short`.
3. Create a consult leaf under `AgentCoordination/Scratchpad/Consult/<YYYYMMDDTHHMMSSZ>[_<slug>]/`.
4. Write `git_status.txt` with the dirty-state snapshot.
5. Read the canonical prompt block from `AgentCoordination/protocols/consult_prompt_block.md` and embed its literal contents in `request.md` under `## Constraints`. If the file is missing, stop and report that the shared consult prompt block has not landed; do not reconstruct it from memory.
6. Write `request.md` through same-directory `.tmp_*` then rename. Use `complete: true`.
7. Build the partner command through `Tools/agent_coordination/partner_invoke.py`; do not hand-roll argv.
8. For Gemini only, embed the full `request.md` text inside the final prompt passed to `partner_invoke.invoke_sync`. Gemini cannot reliably read gitignored Scratchpad leaves, so do not ask it to open `<consult_leaf>/request.md`.
9. For Gemini only, include these hard rules in the prompt:
   - Do not substitute another topic if file reads or tools are blocked.
   - Return exactly one complete `consult/v1` artifact with `from: gemini`, `to: codex`, and the same `mode` as the request.
   - Use no preamble or postamble; the response text must start at the artifact's opening `---`.
   - If the embedded request cannot be answered, return `exit_status: partial` or `exit_status: error` in the artifact and explain the missing evidence under `## Open questions`.
10. Invoke the selected partner from the repo root with `expected_from=partner` and `expected_to="codex"` when calling `partner_invoke.invoke_sync`. Capture stdout/stderr in `log.txt`.
11. If `--dry-run`, report the request path and exact command; stop without invoking.
12. Validate `response.md`. On timeout, non-zero exit, missing response, direction mismatch, or invocation failure, publish a complete error artifact using the helper. A complete error artifact uses `complete: true`, `exit_status: error`, and `partner_completed: false`.
13. Read the response, ask follow-up questions if needed, and repeat with a new consult leaf for each follow-up round.
14. Synthesize the result. If this consult happened mid-project, act on valid feedback before finalizing the task.

No implementation delegation: the consulted agent advises only. Codex owns synthesis, code edits, tests, and final judgment.

## Request Schema

`request.md` frontmatter:

```yaml
---
protocol: consult/v1
from: codex
to: <claude|opencode|gemini>
mode: <planning|mid-project-review|pre-final-check|deep-dive>
allow_tests: <true|false>
created_at_utc: <ISO8601>
repo_root: <abs-path-to-repo>
consult_leaf: <abs-path-to-leaf>
complete: true
---
```

Body sections:

1. `## Question`
2. `## Repo state`
3. `## Constraints`
4. `## Specific asks`

In `## Constraints`, state that the responder must read and honor the canonical consult prompt block at `<repo-root>/AgentCoordination/protocols/consult_prompt_block.md`, then append that file's literal contents. Do not paraphrase or duplicate the block inside this skill.

## Partner Prompts

Use host-native responder names:

- Claude: `Use $claude-consult-respond with --request <request.md>`
- OpenCode: `Load the ocode-consult-respond skill. Process --request <request.md>`
- Gemini: no responder skill exists. Pass a self-contained prompt that includes the full `request.md` text plus the Gemini hard rules above; the wrapper materializes `response.md` from Gemini stdout.

Prefer the command recipes in `AgentCoordination/protocols/partner_cli.md`. If a recipe fails, do not silently invent a new one; surface the command, log excerpt, and failure mode.

## Response Handling

Accepted response frontmatter:

```yaml
---
protocol: consult/v1
from: <claude|opencode|gemini>
to: codex
mode: <same as request>
created_at_utc: <ISO8601>
complete: true
exit_status: ok | error | partial
---
```

Required body sections are `## Findings`, `## Risks`, and `## Open questions`.

Treat `exit_status: partial` as usable but incomplete; require `## Open questions` to explain what context or evidence is missing. Treat `exit_status: error` as a failed consult unless the user explicitly asks to proceed from the log.
