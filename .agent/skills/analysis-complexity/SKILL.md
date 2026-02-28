---
name: analysis-complexity
description: Run cyclomatic complexity analysis using radon and report high-complexity functions
---

# Cyclomatic Complexity Audit

Analyze the `game/` directory for "spaghetti" code.

## Execution

1. **Prerequisite**:
   ```bash
   pip show radon || pip install radon
   ```

2. **Run Analysis**:
   ```bash
   radon cc game/ -s -n C -a --total-average
   ```

3. **Tiered Reporting**:
   Organize findings by complexity score:
   - **Tier 1: Extreme (CC >= 40)**
   - **Tier 2: Very High (CC 30–39)**
   - **Tier 3: High (CC 20–29)**
   - **Tier 4: Elevated (CC 15–19)** (if threshold is 15 or less)

4. **Detailed Metrics**: Report CC score, file path, line number, and function name for each offending block.

5. **Layer Summary**: Group by layer (`ui/`, `simulation/`, etc.).

6. **Pattern Recognition**: Identify common high-complexity patterns (event handlers, dispatch loops, etc.).

7. **Baseline Comparison**: Note improvements or regressions if a previous baseline exists.
