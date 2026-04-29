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
OpenCode visibility, and known stale coordination references.
