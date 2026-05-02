---
name: anti-analysis-sweep
description: Automated codebase sweep — performs sequential waves of review across duplication, legacy, consistency, architecture, and test coverage.
---

# Codebase Sweep

Exhaustively scan the codebase for multiple categories of issues.

## Execution Model

Claude launched 25 agents (5 waves of 5 parallel shards). As Antigravity, you will execute these waves sequentially using your high-context capability to maintain consistency across the entire codebase.

### Wave Categories
1. **Duplication & Fragmentation** (`Reviews/prompts/Sweep - Duplication.txt`)
2. **Legacy System Holdovers** (`Reviews/prompts/Sweep - Legacy Holdovers.txt`)
3. **Consistency Violations** (`Reviews/prompts/Sweep - Consistency Violations.txt`)
4. **Architecture Drift** (`Reviews/prompts/Sweep - Architecture Drift.txt`)
5. **Test Coverage Gaps** (`Reviews/prompts/Sweep - Test Coverage Gaps.txt`)

## Execution Steps

1. **Initialize**:
   ```bash
   python Reviews/scripts/create_review.py sweep "full-codebase-sweep"
   ```
2. **Setup**: Write `Reviews/results/{FOLDER}/scope.md` documenting the single-agent comprehensive approach.
3. **Execute Waves**:
   - For each wave (1-5), read the corresponding prompt file.
   - Perform a deep scan of the target directory (default: `game/`).
   - Write individual findings reports to `Reviews/results/{FOLDER}/findings/`.
4. **Compile**:
   ```bash
   python Reviews/scripts/compile_findings.py Reviews/results/{FOLDER}
   ```
5. **Analyze**: Read `report.md` and summarize top priority issues for the user.
6. **Propose Projects**:
   ```bash
   python Reviews/scripts/generate_prospective_projects.py Reviews/results/{FOLDER}
   ```
   Launch the project generation logic (`Reviews/prompts/Sweep - Generate Projects.txt`) to create project proposals.
7. **Approve**: Present proposals to user and execute approvals:
   ```bash
   python Reviews/scripts/approve_prospective_projects.py Reviews/results/{FOLDER} --approve "{USER_SELECTIONS}"
   ```

## Constraints
- Do NOT skip any wave.
- Ensure all 5 categories are thoroughly reviewed.
- Use your context to identify cross-module issues that individual agents might miss.
