#!/usr/bin/env python3
"""Thin wrapper around partner_invoke.invoke_sync for the legacy-project
codex review subagents.

Usage:
    python Tools/agent_coordination/_proj_codex_consult.py \
        --project-id PROJ-413 \
        --request-file <path to pre-written request.md> \
        [--timeout-sec 900]

Creates `AgentCoordination/Scratchpad/Consult/<timestamp>_<proj_id>_legacy_review/`
with `request.md`, `partner_prompt.txt`, `git_status.txt`, then invokes codex.
Codex writes `response.md` into the same leaf. Prints JSON with the leaf
path and exit status so the calling subagent can read the response.

This is a one-off helper for the 9 parallel reviews spawned by
/claude-proj-from-legacy-audit's follow-up consult step. It is NOT a
general-purpose tool — the SKILL.md of claude-consult remains the canonical
recipe for ad-hoc consults.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import partner_invoke  # type: ignore


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-id", required=True)
    ap.add_argument("--request-file", required=True, help="Path to the pre-composed consult/v1 request.md body (no frontmatter — wrapper adds it)")
    ap.add_argument("--timeout-sec", type=int, default=900)
    args = ap.parse_args()

    repo_root = partner_invoke.resolve_repo_root()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = f"{timestamp}_{args.project_id.lower()}_legacy_review"
    leaf = repo_root / "AgentCoordination" / "Scratchpad" / "Consult" / slug
    leaf.mkdir(parents=True, exist_ok=True)

    # Capture git state
    git_status = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip() or "?"
    (leaf / "git_status.txt").write_text(git_status, encoding="utf-8")

    # Load request body and canonical consult prompt block
    request_body = Path(args.request_file).read_text(encoding="utf-8")
    prompt_block_path = repo_root / "AgentCoordination" / "protocols" / "consult_prompt_block.md"
    prompt_block = prompt_block_path.read_text(encoding="utf-8")

    request_path = leaf / "request.md"
    response_path = leaf / "response.md"
    log_path = leaf / "log.txt"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    request_text = f"""---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: {now}
repo_root: {repo_root}
consult_leaf: {leaf}
complete: true
---

# Consult request — review {args.project_id} legacy-removal project plan

## Question

{request_body}

## Repo state

Branch: {branch}

```
{git_status}
```

## Constraints

Read and honor the canonical consult prompt block. The file's verbatim content follows; the source of truth is `{prompt_block_path}`.

{prompt_block}

## Specific asks

Reply by writing `response.md` in this consult leaf (path in `consult_leaf` frontmatter) with the schema:

```yaml
---
protocol: consult/v1
from: codex
to: claude
mode: planning
created_at_utc: <ISO 8601 UTC>
complete: true
exit_status: ok            # or: partial | error
---
```

Body sections, in order:

1. `## Findings` — direct answers to the question above, evidence-cited (`file:line`).
2. `## Risks` — what the initiator might miss.
3. `## Open questions` — what you lack information to advise on (do NOT speculate). REQUIRED if `exit_status: partial`.
"""

    partner_invoke.atomic_write_text(request_path, request_text)

    partner_prompt = (
        f"Load the codex-starship-consult-respond skill. Process the consult request at {request_path}. "
        f"Honor the permission contract: read-only by default; tests only if allow_tests=true (here: false). "
        f"Write your response.md atomically (temp+rename) at {response_path}. "
        f"The full schema is in the request body. Final ownership belongs to the initiator; you advise, you do not implement."
    )
    (leaf / "partner_prompt.txt").write_text(partner_prompt, encoding="utf-8")

    result = partner_invoke.invoke_sync(
        "codex",
        partner_prompt,
        log_path=log_path,
        repo_root=repo_root,
        response_file=response_path,
        sandbox="workspace-write",  # see SKILL.md Step 5 note — codex requires this even for read-only
        timeout_sec=args.timeout_sec,
        expected_from="codex",
        expected_to="claude",
    )

    out = {
        "leaf": str(leaf),
        "request_path": str(request_path),
        "response_path": str(response_path),
        "log_path": str(log_path),
        "exit_status": result.exit_status,
        "error_kind": result.error_kind,
        "return_code": result.return_code,
        "partner_completed": result.partner_completed,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
