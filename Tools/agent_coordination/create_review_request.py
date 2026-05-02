"""Create a review request file from a JSON payload file.

Single interface: --payload-file <path>. No per-field or stdin flags.

Prints the request ID to stdout on success; exits non-zero on failure.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_TYPES = {
    "code", "plan", "architecture", "tests", "security",
    "performance", "consistency", "general", "custom",
}

REQUIRED_FIELDS = {"type", "title", "scope", "instructions"}


def _resolve_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _generate_id() -> str:
    now = datetime.now(timezone.utc)
    suffix = secrets.token_hex(3)
    return f"req_{now:%Y%m%d}_{now:%H%M%S}_{suffix}"


def _render_body(payload: dict[str, object]) -> str:
    parent_line = f"**Parent:** {payload['parent']}\n" if payload.get("parent") else ""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    requester = str(payload.get("requester", "claude-code"))

    body = (
        f"# Review Request: {payload['title']}\n"
        f"**Request ID:** {payload['_request_id']}\n"
        f"**Review Type:** {payload['type']}\n"
        f"{parent_line}"
        f"**Created:** {now}\n"
        f"**Requester:** {requester}\n"
        f"\n"
        f"## Scope\n\n{payload['scope']}\n"
        f"\n"
        f"## Instructions\n\n{payload['instructions']}\n"
    )
    if payload.get("context"):
        body += f"\n## Context\n\n{payload['context']}\n"
    body += f"\n## Expected Deliverable\n\n{payload.get('expected_deliverable', 'Report + result.json sidecar.')}\n"
    return body


def _failed_payloads_dir(pending_dir: Path) -> Path:
    """Locate failed_payloads/ relative to the pending dir (test-isolation safe)."""
    # pending_dir is .../AgentCoordination/opencodereview/pending_review_requests
    # failed_payloads is .../AgentCoordination/opencodereview/local/failed_payloads
    # When tests pass a temp --pending-dir, this stays in the same temp tree.
    return pending_dir.parent / "local" / "failed_payloads"


def _save_failed_payload(payload_data: dict[str, object], pending_dir: Path, request_id: str, reason: str) -> None:
    failed_dir = _failed_payloads_dir(pending_dir)
    failed_dir.mkdir(parents=True, exist_ok=True)
    dest = failed_dir / f"{request_id}_{reason}.json"
    dest.write_text(json.dumps(payload_data, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a collision-resistant review request file from a JSON payload"
    )
    parser.add_argument("--payload-file", required=True, help="Path to JSON payload file")
    parser.add_argument("--pending-dir", default="", help="Override pending_review_requests directory (testing)")
    args = parser.parse_args()

    payload_path = Path(args.payload_file)
    if not payload_path.exists():
        print(f"Payload file not found: {payload_path}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"Invalid JSON in payload file: {e}", file=sys.stderr)
        return 1

    if not isinstance(payload, dict):
        print("Payload must be a JSON object", file=sys.stderr)
        return 1

    missing = REQUIRED_FIELDS - set(payload.keys())
    if missing:
        print(f"Missing required fields: {', '.join(sorted(missing))}", file=sys.stderr)
        return 1

    root = _resolve_project_root()
    if args.pending_dir:
        pending_dir = Path(args.pending_dir).resolve()
    else:
        pending_dir = root / "AgentCoordination" / "opencodereview" / "pending_review_requests"
    pending_dir.mkdir(parents=True, exist_ok=True)

    review_type = str(payload.get("type", ""))
    if review_type not in ALLOWED_TYPES:
        print(f"Invalid type: {review_type!r}. Allowed: {', '.join(sorted(ALLOWED_TYPES))}", file=sys.stderr)
        _save_failed_payload(payload, pending_dir, "invalid_type", review_type)
        return 2

    request_id = ""
    for _ in range(5):
        candidate = _generate_id()
        dest = pending_dir / f"{candidate}.md"
        if not dest.exists():
            request_id = candidate
            break
    if not request_id:
        print("Could not generate a unique request ID after 5 attempts", file=sys.stderr)
        return 1

    payload["_request_id"] = request_id
    body = _render_body(payload)

    tmp_path = pending_dir / f".tmp_{request_id}.md"
    dest_path = pending_dir / f"{request_id}.md"

    try:
        tmp_path.write_text(body, encoding="utf-8")
        if sys.platform == "win32":
            dest_path.unlink(missing_ok=True)
        os.replace(tmp_path, dest_path)
    except OSError as e:
        print(f"I/O error writing request file: {e}", file=sys.stderr)
        tmp_path.unlink(missing_ok=True)
        _save_failed_payload(payload, pending_dir, request_id, "io_error")
        return 1

    print(request_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
