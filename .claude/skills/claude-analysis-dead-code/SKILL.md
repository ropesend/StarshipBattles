---
name: claude-analysis-dead-code
description: Run Vulture dead code analysis on game/ and tests/, categorize findings, and report confirmed dead code
disable-model-invocation: true
argument-hint: [min-confidence (default: 60)]
---

# Dead Code Analysis (Vulture)

Scan the codebase for unused classes, functions, variables, imports, and constants using **Vulture**.

## Confidence Threshold

Use $0 as the minimum confidence percentage. If no argument provided, default to **60**.

## Steps

### Step 1: Ensure Vulture is installed

```bash
pip show vulture || pip install vulture
```

### Step 2: Run Vulture on game/ and tests/

Run three passes and capture the output:

```bash
# High-confidence pass (100%) — definitely dead
vulture game/ tests/ --min-confidence 100

# Medium-confidence pass (80%) — very likely dead
vulture game/ tests/ --min-confidence 80

# Full pass at requested threshold — needs manual verification
vulture game/ --min-confidence <threshold>
```

### Step 3: Categorize findings

Group the `game/` results by type:
- **Dead classes** — entire classes never instantiated or referenced
- **Dead functions** — standalone functions never called
- **Dead methods** — class methods never called
- **Dead constants/variables** — assigned but never read
- **Dead imports** — imported but never used

### Step 3b: Cross-reference against docs/

Check if any dead code corresponds to patterns or classes documented in `docs/`:
- **Dead code matching removed patterns:** If `docs/` no longer describes a pattern but dead code still implements it, this confirms the code is intentionally eradicated — prioritize removal.
- **Docs still referencing dead code:** If `docs/` files still reference dead classes, functions, or patterns, flag these as documentation discrepancies that need fixing alongside the dead code removal.

### Step 4: Identify false positives

Flag these common false positive patterns — do NOT report them as dead code:
- **`__exit__` parameters** (`exc_type`, `exc_val`, `exc_tb`) — required by context manager protocol
- **Pytest fixtures** — variables that appear "unused" but are injected by pytest's fixture mechanism
- **Protocol/ABC classes** — may be used in `isinstance()` checks, type annotations, or `TYPE_CHECKING` blocks
- **Command classes** — may be instantiated via registry dispatch or string-based lookup (check `CommandHandlerRegistry` usage)
- **Factory functions** — verify they aren't called from tests before flagging

For each flagged class or function at 60% confidence, do a quick Grep to verify it's truly unused before including it in the report.

### Step 5: Identify hotspot files

Report the top 15 files by finding count (at the requested confidence level).

### Step 6: Categorize test/ findings

For `tests/` findings at 80%+:
- **Unused imports** — safe to remove (e.g., `PropertyMock` imported but never used)
- **Unused fixture variables** — usually false positives from tuple unpacking of fixtures; note but don't prioritize
- Report top 10 test files by finding count

### Step 7: Report

Present results as markdown with these sections:

1. **Summary table** — total findings by scope and confidence level
2. **Confirmed dead code** — items verified via Grep as truly unused, grouped by tier:
   - Tier 1: Dead files (entire files that can be deleted)
   - Tier 2: Dead functions/classes (remove from their files)
   - Tier 3: Dead constants (remove from config files)
   - Tier 4: Dead imports (remove import lines)
   - Tier 5: Dead variables (remove assignments)
3. **False positives** — items Vulture flagged but are actually used, with explanation
4. **Hotspot files** — top files by dead code count
5. **Test file findings** — worst test files
6. **Recommended cleanup order** — prioritized by safety and impact

### Step 8: Compare to previous run

If memory files contain previous Vulture results, compare:
- New dead code introduced since last run
- Dead code that was cleaned up since last run
- Trend direction (improving or worsening)

## Output Format

Use markdown tables grouped by tier. Include clickable file:line links for each finding.
