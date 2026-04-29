# Agent Coordination

Generate tracked coordination artifacts for agent-facing repo surfaces.

## Purpose

This tool records observed facts about Codex, Claude, OpenCode, and
Antigravity skill/config surfaces. The generated inventory is an input to the
later validator and prefix migration work; it does not enforce policy itself.

## Requirements

No additional dependencies.

## Usage

```powershell
python Tools/agent_coordination/inventory_agent_surfaces.py
python Tools/agent_coordination/inventory_agent_surfaces.py --stdout
```

### Arguments

- `--repo-root PATH` -- repository root to scan (default: auto-detected).
- `--output PATH` -- inventory JSON path (default: `AgentCoordination/generated/agent_surface_inventory.json`).
- `--stdout` -- print JSON instead of writing the output file.

## Output

Writes `AgentCoordination/generated/agent_surface_inventory.json` with a
schema-versioned inventory of skill surfaces, frontmatter, prefix compliance,
OpenCode visibility, known stale coordination references, and a top-level
`warnings` array for cross-cutting issues such as `opencode.json` permission
ordering.

### Detector notes

- `hardcoded_test_baseline` requires both a 4-5 digit number AND a same-line
  keyword (`tests`, `baseline`, `passed`, `skipped`, `failed`, `errors`). PROJ
  ids and unrelated 5-digit numbers are not flagged.
- `absolute_path` matches Windows drive-letter and POSIX-style absolute path
  prefixes generically. Settings files legitimately carry such paths; downstream
  policy decides severity per the plan (warning in `.claude/settings*.json`,
  failure in adapter docs/SKILL.md).
- `opencode_wildcard_not_first` warns when `opencode.json` lists a permission
  pattern before the wildcard `*`. The inventory's last-match-wins resolution
  matches the user's current ordering; reordering would silently invert
  reported permissions.

## OpenCode permission resolution

Pattern matching uses **last-match-wins** in JSON insertion order. This works
for the current `opencode.json`, where `*` is declared first and specific
patterns follow. If the wildcard is moved after specific patterns it would
override them, so the inventory emits a warning to surface that case. OpenCode
itself may use most-specific-pattern-wins; if so, future migration to that
strategy must be done with a manifest update, not a silent reorder.

## Claude settings sanitizer

```powershell
python Tools/agent_coordination/sanitize_claude_settings.py
python Tools/agent_coordination/sanitize_claude_settings.py --format json
```

Dry-run only. Classifies entries in `.claude/settings.json` and
`.claude/settings.local.json` as one of:

- `OK` — repo-relative, current Starship Battles checkout, or known-safe system library
- `STALE_WARN` — references the legacy `Dev\Starship Battles` checkout layout. Proposed rewrites preserve scope and separator style; the sanitizer refuses any rewrite that would broaden permissions.
- `EXTERNAL_REVIEW` — absolute path outside known Starship Battles roots
- `DANGEROUS` — destructive or overly broad permission (`rm -rf`, `del /s`, `git push --force`, `git reset --hard`, `Read(//**)`, etc.)
- `SECRET` — looks like a hard-coded credential (AWS / OpenAI / GitHub PAT / Slack token)

Exit codes:

- `0` — only OK / STALE_WARN findings; warnings are reported but not blocking.
- `1` — at least one DANGEROUS, SECRET, or EXTERNAL_REVIEW finding.
- `2` — file parse error.

Apply mode is intentionally not implemented yet. Per the final coordination
plan, apply only lands once the dry-run reports have been reviewed and the
classification rules have been exercised on the real settings file.

## Skill usage tracking

```powershell
python Tools/agent_coordination/log_skill_usage.py --agent claude --skill claude-proj-start
python Tools/agent_coordination/summarize_skill_usage.py
```

Counters are **advisory only**. They identify rarely-used skills as cleanup
candidates; they never authorize automatic deletion.

- The first invocation auto-generates a per-checkout `install_id` at
  `AgentCoordination/local/install_id.json` (gitignored).
- Each invocation increments the counter for one (skill, agent) pair in
  `AgentCoordination/generated/skill_usage/by_install/<install_id>.json`.
- `summarize_skill_usage.py` aggregates every per-install file into
  `AgentCoordination/generated/skill_usage/summary.json` (tracked artifact
  with `schema_version`, total counts, per-install breakdown, and most-recent
  `last_used` timestamp).
- Allowed `--agent` values: `claude`, `anti`, `ocode`, `codex`. Skill names
  must satisfy the Agent Skills regex `^[a-z0-9]+(-[a-z0-9]+)*$`.

For Claude Code the natural integration is a skill-scoped hook in
`.claude/settings.json` that calls `log_skill_usage.py` with the matched
skill name. Other agents call the script explicitly; transcript-scanning is
a viable alternative if hook support is missing.

## Test baseline `git_sha` semantics

The companion file `AgentCoordination/generated/test_baseline.json` records
`git_sha` from `HEAD` **at run time**. After a green run, the baseline file is
updated and committed; the recorded `git_sha` therefore refers to the parent
commit (the code that was tested), not the commit that contains the file. This
is the intended contract — see `Tools/test_sharded/README.md` for details.
