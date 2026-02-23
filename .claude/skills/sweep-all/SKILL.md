---
name: sweep-all
description: Fire-and-forget parallel codebase sweep — launches 25 agents across 5 sweep types and 5 module shards, then generates prospective projects for user approval
disable-model-invocation: true
argument-hint: [optional: directory scope, e.g., game/simulation/]
---

# Codebase Sweep: Automated Parallel Review

**Fire-and-forget. No interactive scope definition. Pre-configured for full codebase coverage.**

## Overview

This skill launches 25 general-purpose agents (5 sweep types x 5 module shards) in 5 sequential waves of 5 parallel agents each. Each agent exhaustively scans its assigned shard for one category of issues.

## Scope

**Default:** Entire `game/` directory tree (production code only).
**Override:** If the user provided arguments, scope to those directories instead (skip sharding if a single module is specified).

**Always exclude:** tests/, __pycache__/, .git/, assets/, Projects/refactor_loop/, Reviews/, Projects/

## Shard Definitions

| Shard Name | ID Suffix | Directories |
|------------|-----------|-------------|
| UI-Screens | UI1 | `game/ui/screens/`, `game/ui/panels/` |
| UI-Framework | UI2 | `game/ui/` (root files, services/, renderer/, interfaces/, orchestration/, assets/, components/, utils/) |
| Simulation | SIM | `game/simulation/` (all subdirectories) |
| Strategy | STR | `game/strategy/` (all subdirectories) |
| Foundation | FND | `game/core/`, `game/ai/`, `game/research/`, `game/engine/` |

## Sweep Types

| Wave | Sweep Type | Prefix | Prompt File |
|------|-----------|--------|-------------|
| 1 | Duplication & Fragmentation | DUP | `Reviews/Prompts/Sweep - Duplication.txt` |
| 2 | Legacy System Holdovers | LEG | `Reviews/Prompts/Sweep - Legacy Holdovers.txt` |
| 3 | Consistency Violations | CON | `Reviews/Prompts/Sweep - Consistency Violations.txt` |
| 4 | Architecture Drift | ADR | `Reviews/Prompts/Sweep - Architecture Drift.txt` |
| 5 | Test Coverage Gaps | TCG | `Reviews/Prompts/Sweep - Test Coverage Gaps.txt` |

## Execution Sequence

### Step 1: Create Review Folder

Run this command:
```bash
python Reviews/scripts/create_review.py sweep "full-codebase-sweep"
```

If the user provided a scope argument (e.g., `game/simulation/`), use a descriptive slug instead (e.g., `"simulation-sweep"`).

Record the resulting review folder path (printed by the script). Store it as `REVIEW_FOLDER`.

### Step 2: Write Scope Document

Write `Reviews/results/{REVIEW_FOLDER}/scope.md` with:
- Review type: Sweep Review
- Scope: `game/` (or user-specified directory)
- Agent count: 25 (5 sweep types x 5 shards)
- Table of all 25 agents with their sweep type, shard, output file name, and finding ID prefix
- Execution model: 5 waves of 5 parallel agents

### Step 3: Read All Prompt Files

Read all 5 sweep prompt files:
1. `Reviews/Prompts/Sweep - Duplication.txt`
2. `Reviews/Prompts/Sweep - Legacy Holdovers.txt`
3. `Reviews/Prompts/Sweep - Consistency Violations.txt`
4. `Reviews/Prompts/Sweep - Architecture Drift.txt`
5. `Reviews/Prompts/Sweep - Test Coverage Gaps.txt`

### Step 4-8: Execute 5 Waves

For each wave (sweep type), launch 5 Explore agents **in a SINGLE message using 5 parallel Task tool calls**.

**Agent configuration for each Task call:**
- `subagent_type`: `general-purpose`
- `description`: Short description like "DUP sweep: UI-Screens"
- `prompt`: The sweep prompt file content with these placeholders replaced:
  - `{SCOPE}` -> The shard's directories (e.g., "game/ui/screens/ and game/ui/panels/")
  - `{OUTPUT_FILE}` -> Full path like `Reviews/results/{REVIEW_FOLDER}/findings/duplication_ui_screens_report.md`
  - `{SHARD_NAME}` -> Human-readable name (e.g., "UI-Screens")
  - `{SHARD_ID}` -> ID suffix (e.g., "UI1")
- Do NOT use `run_in_background: true` -- synchronous parallel execution is more reliable

**Wave execution order:**
1. **Wave 1:** Launch 5 Duplication agents (one per shard) -> wait for all 5 -> verify outputs
2. **Wave 2:** Launch 5 Legacy Holdovers agents -> wait -> verify
3. **Wave 3:** Launch 5 Consistency Violations agents -> wait -> verify
4. **Wave 4:** Launch 5 Architecture Drift agents -> wait -> verify
5. **Wave 5:** Launch 5 Test Coverage Gaps agents -> wait -> verify

**After each wave**, check that all 5 output files exist in `findings/` and are non-empty. If any file is missing or empty (<100 bytes), retry that single agent once.

**Scope override behavior:** If the user specified a single directory (e.g., `/sweep-all game/simulation/`), skip sharding entirely. Instead, launch just 5 agents (one per sweep type) all targeting the specified directory, in a single wave.

### Step 9: Compile Findings

Run:
```bash
python Reviews/scripts/compile_findings.py Reviews/results/{REVIEW_FOLDER}
```

This parses all finding files, de-duplicates, calculates statistics, and generates `report.md`.

### Step 10: Present Summary

Read the compiled `report.md` and present to the user:

1. **Total findings** by severity (Critical / Major / Minor / Info)
2. **Findings by sweep type** (which dimension found the most issues?)
3. **Findings by shard** (which module is most problematic?)
4. **Top 10 priority issues** across all sweeps
5. **Path to full report**: `Reviews/results/{REVIEW_FOLDER}/report.md`

Announce: "Sweep complete. Generating prospective project proposals..."

### Step 11: Scaffold Prospective Projects

Run:
```bash
python Reviews/scripts/generate_prospective_projects.py Reviews/results/{REVIEW_FOLDER}
```

This parses all findings into structured JSON, checks for overlapping existing projects, and creates the `prospective_projects/` directory structure that the project generation agent will populate.

If the `prospective_projects/` directory already exists from a previous run, add `--force` to overwrite.

### Step 12: Launch Project Generation Agent

Read the prompt file `Reviews/Prompts/Sweep - Generate Projects.txt`.

Launch **1 general-purpose agent** using a single Task tool call:

**Agent configuration:**
- `subagent_type`: `general-purpose`
- `description`: "Generate prospective projects from sweep"
- `prompt`: The prompt file content with these placeholders replaced:
  - `{REVIEW_FOLDER}` -> Full path to the review folder (e.g., `Reviews/results/2026-02-10_sweep_full-codebase-sweep`)
  - `{REVIEW_FOLDER_NAME}` -> Just the folder name (e.g., `2026-02-10_sweep_full-codebase-sweep`)
  - `{PROSPECTIVE_DIR}` -> Full path to `Reviews/results/{REVIEW_FOLDER}/prospective_projects`
- `mode`: `bypassPermissions` (the agent needs to write files into the prospective_projects directory)

Wait for the agent to complete.

**Verify outputs:** Check that `prospective_projects/summary.md` exists and is non-empty. Check that at least 1 project subdirectory exists with `proposal.md` and `findings.json` files. If the agent failed to produce output, note the failure and skip to Step 14 with a message to the user.

### Step 13: Present Proposals to User

Read `prospective_projects/summary.md` and present the comparison table to the user.

For each proposed project, show:
- Project title
- Number of findings by severity (Critical/Major/Minor/Info)
- Affected modules
- Estimated scope (Small/Medium/Large)
- Any overlap warnings with existing projects

Then ask the user which projects to approve. Use AskUserQuestion or accept free-text input. Valid responses:
- **"all"** — approve all proposed projects
- **"none"** — reject all (skip project creation)
- **Comma-separated slugs or numbers** — e.g., "1,3,5" or "architecture,legacy"
- **Individual names** — e.g., "architecture" (partial matching supported)

**This is the ONE interactive step in the entire sweep workflow.** Everything before and after is automated.

### Step 14: Execute Approvals

Based on the user's response from Step 13:

**If the user approved any projects**, run:
```bash
python Reviews/scripts/approve_prospective_projects.py Reviews/results/{REVIEW_FOLDER} --approve "{USER_SELECTIONS}"
```

This calls `review_to_project.py` for each approved project with the appropriate `--findings` and `--title` flags, creating real PROJ-XX entries in the project system. Rejected proposals are moved to `rejected_projects/`.

**If the user selected "none"**, announce that no projects were created and the proposals remain in `prospective_projects/` for future reference.

Present the final summary:
1. **Created projects** with their PROJ-XX IDs
2. **Rejected proposals** (stored in `rejected_projects/` for future reference)
3. **Total findings** covered by created projects
4. **Next step**: "Use 'Continue Project' prompt with any of the created project IDs to begin implementation."

## Constraints

- Do NOT ask the user any questions during Steps 1-12 (fire-and-forget)
- Do NOT wait for user input between waves
- Do NOT skip any agent -- all 25 MUST run (or all 5 if scope-narrowed)
- If an agent fails retry, note it in the summary but continue with remaining waves
- Announce progress between waves: "Wave 1/5 complete (Duplication). Starting Wave 2 (Legacy Holdovers)..."
- Step 13 is the ONLY interactive step -- present proposals and get approval before creating projects
- Do NOT create real projects without user approval
