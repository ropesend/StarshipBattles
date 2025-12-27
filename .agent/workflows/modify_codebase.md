---
description: detailed workflow for modifying code with strict TDD and regression testing
---

# Modify Codebase (Strict TDD & Regression)

Follow this workflow for ANY code modification to ensure stability.

## 1. Create or Update Unit Tests (TDD)
Before modifying logic, identify the test file in `tests/`. If none exists, create one.
Add a test case that covers the *new* behavior.

- If fixing a bug: Create a reproduction test case that fails.
- If adding a feature: Create a test case that defines the expected behavior.

## 2. Verify Test Failure
Run the specific test file to confirm the new test fails (or errors) as expected.
```powershell
python -m unittest tests/test_your_file.py
```

## 3. Implement Code Changes
Modify the source code to implement the feature or fix the bug.
- Keep changes focused.
- Do not break existing public interfaces if possible.

## 4. Verify Test Success
Run the specific test file again. It MUST pass now.
```powershell
python -m unittest tests/test_your_file.py
```
If it fails, debugging is required. Repeat steps 3-4.

## 5. Run Full Regression Suite
// turbo
Once the new feature works, run the ENTIRE test suite to ensure no regressions.
```powershell
python -m unittest discover -s tests -v
```
**CRITICAL:** If any *other* tests fail, you must fix the regression before finishing.
