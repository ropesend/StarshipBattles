# Pre-commit hooks

This repo does not use the `pre-commit` framework — hooks live as raw scripts
under `.git/hooks/` and each developer installs them on their own checkout
(`.git/` is not tracked).

## Available hooks

### `lint_test_files`

Flags any test file under `tests/` that imports zero `game.*` modules.
Historically these have been files that re-implement production logic locally
or trivial-pass tests with no real coverage. See
`Tools/lint_test_files.py` for the linter and
`Tools/lint_test_files_allowlist.txt` for legitimate exceptions
(tools tests, infrastructure tests, data fixtures).

**Origin:** PROJ-326 Phase 1 (preventive measure surfaced by the PROJ-321
follow-up review).

## Installing the test-file linter as a pre-commit hook

From the repo root:

```bash
# Bash / Git Bash / WSL
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
# PROJ-326 zero-game-import test-file linter.
# Skip on merge / rebase / cherry-pick states where partial trees are normal.
if [ -f .git/MERGE_HEAD ] || [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
    exit 0
fi
python Tools/lint_test_files.py
EOF
chmod +x .git/hooks/pre-commit
```

```powershell
# PowerShell
@'
#!/bin/sh
if [ -f .git/MERGE_HEAD ] || [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
    exit 0
fi
python Tools/lint_test_files.py
'@ | Set-Content -Path .git/hooks/pre-commit -Encoding ASCII
```

The hook fires on every `git commit`. To bypass for a single commit (rarely
correct — prefer fixing the root cause) use `git commit --no-verify`.

## CI integration

Add this step to the relevant workflow under `.github/workflows/`:

```yaml
- name: Lint test files (zero-game-import detector)
  run: python Tools/lint_test_files.py
```

The current candidate workflow is `.github/workflows/agent_coordination.yml`.
The linter has no third-party dependencies — `python` alone is sufficient.

## Notes

- The linter exits 0 on a clean tree (with the seeded allowlist) — it should
  not block existing development.
- New zero-game-import test files added without an allowlist entry will fail
  the hook. The fix is almost always to delete the file or rewrite it to
  import what it claims to test; legitimate exceptions go in
  `Tools/lint_test_files_allowlist.txt` with a comment explaining why.
- The allowlist supports glob patterns (`**` for recursive matching). See the
  file header for syntax.
