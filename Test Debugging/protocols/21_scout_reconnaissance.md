# Protocol 21: Scout Reconnaissance
**Role:** Debug Scout (Specialist)
**Objective:** Perform deep reconnaissance in a specific Exploration Zone.

## 1. The Scout Mindset
Unlike the Refactoring Swarm, your goal is not to implement a feature. Your goal is to **find the anomaly**. Assume the obvious areas have already been checked.

## 2. Reconnaissance Loop
If you find a lead (e.g., a suspicious utility function or base class) but do not have the file content in your context:
1. **Identify the missing file.**
2. **Use the `view_file` tool** to read it.
3. **Trace the dependency** until you find where the behavior deviates from expectations.

## 3. Exploration Patterns
- **State Pollution:** Look for variables that are mutated but never reset.
- **Fixture Shadowing:** Check if a local `conftest.py` is overriding a global fixture in an unexpected way.
- **Mock Misalignment:** Check if the production code changed its signature, but the mock in the test file is still using the old signature.
- **MRO Hazards:** In polymorphic entities like `Ship`, check Method Resolution Order if methods are being called from unexpected base classes.

## 4. Reporting
Your report must include:
- **Zone Status:** [CLEAN] or [SIGNAL FOUND].
- **Evidence:** Snippets of code or log output that support your finding.
- **Recommendation:** What should the Synthesizer or Main Agent investigate next?
