---
name: analysis-complexity
description: Run cyclomatic complexity analysis on the codebase using radon and report all high-complexity functions
disable-model-invocation: true
argument-hint: [threshold (default: 15)]
---

# Cyclomatic Complexity Audit

Analyze the `game/` directory for cyclomatic complexity using **radon**.

## Threshold

Use CC >= $0 as the "spaghetti" threshold. If no argument provided, default to **15**.

## Steps

1. **Ensure radon is installed:**
   ```bash
   pip show radon || pip install radon
   ```

2. **Run full analysis** — all functions with CC >= 11 (grade C+):
   ```bash
   radon cc game/ -s -n C -a --total-average
   ```

3. **Compile a sorted report** of the worst offenders (CC >= threshold), organized into tiers:
   - **Tier 1: Extreme (CC >= 40)** — urgent refactoring candidates
   - **Tier 2: Very High (CC 30–39)**
   - **Tier 3: High (CC 20–29)**
   - **Tier 4: Elevated (CC 15–19)** — only if threshold <= 15

4. **For each function**, report:
   - Cyclomatic complexity score
   - File path with line number (as a clickable link)
   - Function/method name
   - Radon grade (A–F)

5. **Summarize distribution by layer** (`ui/`, `simulation/`, `strategy/`, `ai/`, `core/`)

6. **Identify patterns** in the high-complexity functions (e.g., giant event handlers, stat aggregators, serialization, key dispatch)

7. **Compare to previous baseline** if available in memory — note any functions that improved or worsened

8. **Report overall stats:**
   - Total blocks analyzed
   - Average complexity grade
   - Count of functions above threshold
   - Worst single function

## Output Format

Present results as markdown tables grouped by tier, with a summary section at the end.
