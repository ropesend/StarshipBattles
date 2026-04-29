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

## Test baseline `git_sha` semantics

The companion file `AgentCoordination/generated/test_baseline.json` records
`git_sha` from `HEAD` **at run time**. After a green run, the baseline file is
updated and committed; the recorded `git_sha` therefore refers to the parent
commit (the code that was tested), not the commit that contains the file. This
is the intended contract — see `Tools/test_sharded/README.md` for details.
