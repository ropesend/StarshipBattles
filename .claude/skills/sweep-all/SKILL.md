---
name: sweep-all
description: Fire-and-forget parallel codebase sweep — launches 25 agents across 5 sweep types and 5 module shards
disable-model-invocation: true
argument-hint: [optional: directory scope, e.g., game/simulation/]
---

# Codebase Sweep: Automated Parallel Review

**Fire-and-forget. No interactive scope definition. Pre-configured for full codebase coverage.**

## Overview

This skill launches 25 Explore agents (5 sweep types x 5 module shards) in 5 sequential waves of 5 parallel agents each. Each agent exhaustively scans its assigned shard for one category of issues.

## Scope

**Default:** Entire `game/` directory tree (production code only).
**Override:** If the user provided arguments, scope to those directories instead (skip sharding if a single module is specified).

**Always exclude:** tests/, __pycache__/, .git/, assets/, refactor_loop/, Reviews/, Projects/

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
- `subagent_type`: `Explore`
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
6. **Next step suggestion**: If Critical or Major findings exist, suggest:
   ```
   To convert these findings into a project:
   python Reviews/scripts/review_to_project.py {REVIEW_FOLDER}
   ```

## Constraints

- Do NOT ask the user any questions during execution
- Do NOT wait for user input between waves
- Do NOT skip any agent -- all 25 MUST run (or all 5 if scope-narrowed)
- If an agent fails retry, note it in the summary but continue with remaining waves
- Announce progress between waves: "Wave 1/5 complete (Duplication). Starting Wave 2 (Legacy Holdovers)..."
