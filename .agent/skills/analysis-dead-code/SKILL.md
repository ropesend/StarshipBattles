---
name: analysis-dead-code
description: Run Vulture dead code analysis on game/ and tests/, categorize findings, and report confirmed dead code
---

# Dead Code Analysis (Vulture)

Scan for unused code with confidence filtering and manual verification.

## Execution

1. **Setup**:
   ```bash
   pip show vulture || pip install vulture
   ```

2. **Analysis Passes**:
   - **High-confidence (100%)**: `vulture game/ tests/ --min-confidence 100`
   - **Medium-confidence (80%)**: `vulture game/ tests/ --min-confidence 80`
   - **Targeted pass**: `vulture game/ --min-confidence [threshold (default: 60)]`

3. **Categorization**: Group findings by type (Classes, Functions, Methods, Constants, Imports).

4. **False Positive Filtering**: Review findings against common patterns:
   - Pytest fixtures
   - Command dispatch registries
   - Factory patterns
   - Protocol/ABC implementations

5. **Hotspot Analysis**: Identify the top 15 files by finding count.

6. **Prioritized Report**:
   - **Tier 1**: Entire files ready for deletion.
   - **Tier 2**: Major blocks (classes/functions).
   - **Lower Tiers**: Imports and variables.

7. **Comparison**: Note changes relative to previous runs if available.
