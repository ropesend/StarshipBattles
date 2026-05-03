"""
Review Daemon — watches for pending review requests and dispatches to OpenCode.

Watches AgentCoordination/opencodereview/pending_review_requests/ for new request files,
processes them via `opencode run` (non-interactive), and manages the request
lifecycle: pending → in_progress → completed.

The daemon owns the request lifecycle (moves files between directories).
OpenCode owns content (writes report + result.json sidecar).

Usage:
    python Tools/agent_coordination/review_daemon.py [--max-workers N]

Signals:
    Ctrl+C — graceful shutdown (waits for in-flight workers, then exits)
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = PROJECT_ROOT / "AgentCoordination" / "opencodereview"
PENDING_DIR = SYSTEM_DIR / "pending_review_requests"
IN_PROGRESS_DIR = SYSTEM_DIR / "in_progress_review_requests"
COMPLETED_DIR = SYSTEM_DIR / "completed_review_requests"
REVIEWS_DIR = PROJECT_ROOT / "Reviews" / "results"
LOCAL_DIR = SYSTEM_DIR / "local"
PID_FILE = LOCAL_DIR / "review_daemon.pid"
LOG_FILE = LOCAL_DIR / "review_daemon.log"

# --- Configuration ---
POLL_INTERVAL: int = 3
OPENCODE_TIMEOUT: int = 1800  # 30 minutes (reviews typically complete in 2-5 min)
ORPHAN_AGE: int = 3600  # 60 minutes (2× timeout)
MAX_WORKERS: int = 5
SHUTDOWN_TIMEOUT: int = 60
MAX_LOG_BYTES: int = 10 * 1024 * 1024  # 10 MB

# --- Shutdown flag ---
_shutdown_requested = False
_active_workers: dict[str, concurrent.futures.Future[bool]] = {}
_active_procs: set[subprocess.Popen[Any]] = set()
_procs_lock = threading.Lock()

# Test seam: when set, replaces [opencode_exe, "run", "--dangerously-skip-permissions"]
# in the worker-spawned subprocess. Production code sets None; tests inject
# a Python interpreter + mock script. Keeps run_daemon's flow testable end-to-end
# without resolving real opencode from PATH.
_OPENCODE_CMD_OVERRIDE: list[str] | None = None


def ensure_dirs() -> None:
    for d in (PENDING_DIR, IN_PROGRESS_DIR, COMPLETED_DIR, REVIEWS_DIR, LOCAL_DIR):
        d.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def rotate_log() -> None:
    """Rotate log if it exceeds MAX_LOG_BYTES."""
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > MAX_LOG_BYTES:
        backup = LOG_FILE.with_suffix(".log.1")
        backup.unlink(missing_ok=True)
        LOG_FILE.rename(backup)
        log("Log rotated (exceeded 10 MB)")


def write_pid() -> None:
    ensure_dirs()
    PID_FILE.write_text(str(os.getpid()))


def remove_pid() -> None:
    try:
        PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def _check_no_other_daemon(force: bool = False) -> None:
    """Refuse to start if another daemon instance appears to be running."""
    if not PID_FILE.exists():
        return
    try:
        existing_pid = int(PID_FILE.read_text().strip())
    except (OSError, ValueError):
        existing_pid = None
    if existing_pid and _pid_alive(existing_pid) and existing_pid != os.getpid():
        if not force:
            raise SystemExit(
                f"Another daemon appears to be running (PID={existing_pid}). "
                f"Use --force to override."
            )
        log(f"--force specified; overriding existing PID file (was PID={existing_pid})")


def get_pending_requests() -> list[Path]:
    """Get pending request files sorted by creation time (oldest first)."""
    if not PENDING_DIR.exists():
        return []
    files = sorted(
        PENDING_DIR.glob("req_*.md"),
        key=lambda p: p.stat().st_ctime,
    )
    return files


def _lock_path(request_path: Path, pid: int) -> Path:
    """Return the lock file path for a request, keyed by PID."""
    return request_path.parent / f"{request_path.name}.{pid}.lock"


def claim_request(request_path: Path) -> bool:
    """Atomically claim a request via lock file. Returns True if claimed."""
    pid = os.getpid()
    lock_file = _lock_path(request_path, pid)
    try:
        lock_file.touch(exist_ok=False)
    except FileExistsError:
        return False
    # Clean up stale locks for this request from dead PIDs
    prefix = request_path.name + "."
    for stale in request_path.parent.glob(f"{request_path.name}.*.lock"):
        if stale == lock_file:
            continue
        try:
            pid_str = stale.name[len(prefix):-len(".lock")]
            lock_pid = int(pid_str)
        except (ValueError, IndexError):
            continue
        if not _pid_alive(lock_pid):
            stale.unlink(missing_ok=True)
    return True


def release_lock(request_path: Path) -> None:
    """Remove the lock file for a request."""
    _lock_path(request_path, os.getpid()).unlink(missing_ok=True)


def _pid_alive(pid: int) -> bool:
    """Check if a process with the given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def move_to_in_progress(request_path: Path) -> Path:
    """Move a request to the in_progress directory."""
    dest = IN_PROGRESS_DIR / request_path.name
    dest.unlink(missing_ok=True)
    request_path.rename(dest)
    return dest


def update_request_status(request_path: Path, **fields: str) -> None:
    """Add or update status fields in a request file."""
    content = request_path.read_text(encoding="utf-8")
    for key, value in fields.items():
        line = f"**{key}:** {value}"
        if f"**{key}:**" in content:
            content = re.sub(
                rf"\*\*{re.escape(key)}:\*\*.*",
                line,
                content,
                count=1,
            )
        else:
            content += f"\n{line}\n"
    request_path.write_text(content, encoding="utf-8")


def _write_results_section(request_path: Path, fields: dict[str, str]) -> None:
    """Write a canonical ## Results section per Option B contract."""
    content = request_path.read_text(encoding="utf-8")
    # Strip stale top-level Status (set during pickup, no longer current)
    content = re.sub(r"^\*\*Status:\*\*.*\n", "", content, flags=re.MULTILINE, count=1)
    # Strip any pre-existing Results section
    content = re.sub(r"\n+## Results\b.*\Z", "", content, flags=re.DOTALL).rstrip()
    lines = ["", "", "## Results", ""]
    # Ordered: Status, Completed, Report, Findings, FailureReason
    for key in ("Status", "Completed", "Report", "Findings", "FailureReason"):
        if key in fields:
            lines.append(f"**{key}:** {fields[key]}")
    request_path.write_text(content + "\n".join(lines) + "\n", encoding="utf-8")


def move_to_completed(
    request_path: Path,
    success: bool,
    report_path: str = "",
    findings_summary: str = "",
    failure_reason: str = "",
) -> None:
    """Move a request to the completed directory with a ## Results section."""
    fields: dict[str, str] = {
        "Status": "completed" if success else "failed",
        "Completed": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if success and report_path:
        fields["Report"] = report_path  # raw path, no backticks
    if success and findings_summary:
        fields["Findings"] = findings_summary
    if not success and failure_reason:
        fields["FailureReason"] = failure_reason
    _write_results_section(request_path, fields)

    dest = COMPLETED_DIR / request_path.name
    dest.unlink(missing_ok=True)
    request_path.rename(dest)


def _find_opencode() -> str | None:
    """Find the opencode executable on the system PATH."""
    exe = shutil.which("opencode")
    if exe:
        return exe
    if sys.platform == "win32":
        exe = shutil.which("opencode.cmd")
        if exe:
            return exe
        exe = shutil.which("opencode.ps1")
        if exe:
            return exe
    return None


def _parse_request_type(request_path: Path) -> str:
    """Extract the Review Type from a request file."""
    try:
        content = request_path.read_text(encoding="utf-8")
        m = re.search(r"\*\*Review Type:\*\*\s*(\S+)", content)
        if m:
            return m.group(1).lower()
    except OSError:
        pass
    return "general"


def _parse_request_parent(request_path: Path) -> str | None:
    """Extract the Parent field from a request file, if present."""
    try:
        content = request_path.read_text(encoding="utf-8")
        m = re.search(r"\*\*Parent:\*\*\s*(req_\S+)", content)
        if m:
            return m.group(1)
    except OSError:
        pass
    return None


def _parse_request_title(request_path: Path) -> str:
    """Extract a slug-friendly title from the request."""
    try:
        content = request_path.read_text(encoding="utf-8")
        m = re.search(r"^# Review Request:\s*(.+)$", content, re.MULTILINE)
        if m:
            title = m.group(1).strip().lower()
            title = re.sub(r"[^a-z0-9]+", "-", title).strip("-")[:50]
            return title
    except OSError:
        pass
    return request_path.stem


def _make_review_dir(request_path: Path) -> Path:
    """Create and return a review directory for the given request."""
    review_type = _parse_request_type(request_path)
    title_slug = _parse_request_title(request_path)
    request_id = request_path.stem
    now = datetime.now(timezone.utc)
    dir_name = f"{now:%Y-%m-%d_%H%M%S}_{review_type}_{title_slug}_req-{request_id}"
    review_dir = REVIEWS_DIR / dir_name
    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / "findings").mkdir(exist_ok=True)
    return review_dir


def _read_sidecar(review_dir: Path) -> dict[str, Any] | None:
    """Read result.json sidecar from a review directory."""
    sidecar_path = review_dir / "result.json"
    if not sidecar_path.exists():
        return None
    try:
        return json.loads(sidecar_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _clear_status_fields(request_path: Path, *keys: str) -> None:
    """Remove specific **Key:** Value lines from a request file."""
    content = request_path.read_text(encoding="utf-8")
    for key in keys:
        content = re.sub(
            rf"\*\*{re.escape(key)}:\*\*.*\n?",
            "",
            content,
            count=1,
        )
    request_path.write_text(content, encoding="utf-8")


def _sweep_stale_locks() -> None:
    """Remove lock files owned by dead PIDs from pending/."""
    if not PENDING_DIR.exists():
        return
    for lock_file in PENDING_DIR.glob("req_*.md.*.lock"):
        try:
            pid_str = lock_file.name.rsplit(".", 2)[-2]
            lock_pid = int(pid_str)
        except (ValueError, IndexError):
            lock_file.unlink(missing_ok=True)
            continue
        if not _pid_alive(lock_pid):
            lock_file.unlink(missing_ok=True)


def recover_orphans() -> None:
    """On startup, handle orphaned requests left in in_progress/."""
    if not IN_PROGRESS_DIR.exists():
        return
    for req_path in sorted(IN_PROGRESS_DIR.glob("req_*.md")):
        try:
            content = req_path.read_text(encoding="utf-8")
            m = re.search(r"\*\*PickedUp:\*\*\s*(.+)", content)
            if not m:
                log(f"Orphan {req_path.name}: no PickedUp timestamp, marking failed")
                move_to_completed(req_path, success=False, failure_reason="orphaned: no PickedUp timestamp")
                continue

            try:
                picked_up = datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
            except ValueError:
                log(f"Orphan {req_path.name}: unparseable timestamp, marking failed")
                move_to_completed(req_path, success=False, failure_reason="orphaned: unparseable timestamp")
                continue

            age = (datetime.now(timezone.utc) - picked_up.replace(tzinfo=timezone.utc)).total_seconds()
            if age > ORPHAN_AGE:
                log(f"Orphan {req_path.name}: age={age:.0f}s > {ORPHAN_AGE}s, marking failed")
                move_to_completed(req_path, success=False, failure_reason=f"orphaned: age {age:.0f}s exceeded {ORPHAN_AGE}s limit")
            else:
                log(f"Orphan {req_path.name}: age={age:.0f}s, retrying")
                dest = PENDING_DIR / req_path.name
                _clear_status_fields(req_path, "Status", "PickedUp")
                dest.unlink(missing_ok=True)
                req_path.rename(dest)
        except OSError:
            log(f"Orphan {req_path.name}: filesystem error during recovery")


def process_request(request_path: Path, opencode_cmd: list[str] | None = None) -> bool:
    """
    Process a single review request via opencode run.

    The daemon owns lifecycle: moves pending → in_progress → completed.
    OpenCode owns content: writes report.md + result.json sidecar.

    If opencode_cmd is provided, uses that instead of _find_opencode().
    """
    request_id = request_path.stem
    log(f"Processing request: {request_id}")

    # Move to in-progress
    in_progress_path = move_to_in_progress(request_path)
    update_request_status(
        in_progress_path,
        Status="in-progress",
        PickedUp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    # Create review directory and pass its path to OpenCode
    review_dir = _make_review_dir(in_progress_path)
    sidecar_path = review_dir / "result.json"
    review_dir_rel = str(review_dir.relative_to(PROJECT_ROOT)).replace("\\", "/")

    prompt = (
        f"Load the ocode-review-request skill. "
        f"Process the request at AgentCoordination/opencodereview/in_progress_review_requests/{in_progress_path.name}. "
        f"Use review directory: {review_dir_rel}/. "
        f"Write result.json to: {review_dir_rel}/result.json"
    )

    if opencode_cmd is not None:
        cmd = opencode_cmd + [prompt]
    elif _OPENCODE_CMD_OVERRIDE is not None:
        cmd = _OPENCODE_CMD_OVERRIDE + [prompt]
    else:
        opencode_exe = _find_opencode()
        if opencode_exe is None:
            log(f"Request {request_id}: opencode not found on PATH")
            move_to_completed(in_progress_path, success=False, failure_reason="opencode not found on PATH")
            return False
        cmd = [opencode_exe, "run", "--dangerously-skip-permissions", prompt]
    log(f"Launching: {' '.join(cmd)} (request={request_id})")

    proc: subprocess.Popen[Any] | None = None
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        with _procs_lock:
            _active_procs.add(proc)

        try:
            stdout, stderr = proc.communicate(timeout=OPENCODE_TIMEOUT)
        except subprocess.TimeoutExpired:
            log(f"Request {request_id} timed out after {OPENCODE_TIMEOUT}s — killing process")
            _kill_process_tree(proc)
            try:
                stdout, stderr = proc.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                pass
            move_to_completed(in_progress_path, success=False, failure_reason="timed out")
            return False

        if proc.returncode == 0:
            log(f"Request {request_id} completed successfully")
            if stdout:
                log(f"  stdout (first 500 chars): {stdout[:500]}")

            # Read sidecar for structured results
            sidecar = _read_sidecar(review_dir)
            if sidecar:
                if "error" in sidecar:
                    log(f"Request {request_id}: sidecar reports error: {sidecar['error']}")
                    move_to_completed(in_progress_path, success=False,
                                      failure_reason=sidecar["error"])
                    return False
                report_path = sidecar.get("report_path", "")
                findings = sidecar.get("findings", {})
                if isinstance(findings, dict):
                    c = findings.get("critical", 0)
                    m = findings.get("major", 0)
                    mi = findings.get("minor", 0)
                    info = findings.get("info", 0)
                    total = sum([c, m, mi, info])
                    findings_summary = f"{total} total (C: {c}, M: {m}, m: {mi}, I: {info})"
                else:
                    findings_summary = str(findings)
                move_to_completed(in_progress_path, success=True, report_path=report_path, findings_summary=findings_summary)
            else:
                log(f"Request {request_id}: no result.json sidecar found at {sidecar_path}")
                move_to_completed(in_progress_path, success=True, findings_summary="completed (no sidecar)")
            return True
        else:
            log(f"Request {request_id} failed with exit code {proc.returncode}")
            if stderr:
                log(f"  stderr (last 500 chars): {stderr[-500:]}")
            move_to_completed(in_progress_path, success=False, failure_reason=f"exit code {proc.returncode}")
            return False

    except Exception:
        log(f"Request {request_id} raised exception: {traceback.format_exc()}")
        move_to_completed(in_progress_path, success=False, failure_reason="internal daemon error")
        return False
    finally:
        if proc is not None:
            with _procs_lock:
                _active_procs.discard(proc)


def _kill_process_tree(proc: subprocess.Popen[Any]) -> None:
    """Kill a subprocess and its descendants (Windows-aware)."""
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                capture_output=True,
                timeout=10,
            )
        else:
            proc.kill()
    except Exception:
        pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


def signal_handler(signum: int, _frame: Any) -> None:
    global _shutdown_requested
    sig_name = signal.Signals(signum).name
    log(f"Received {sig_name} — shutting down gracefully...")
    _shutdown_requested = True


def run_daemon(install_signal_handlers: bool = True, force: bool = False) -> None:
    """Main loop — watch for requests and process them via worker pool."""
    global _shutdown_requested

    if install_signal_handlers:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    ensure_dirs()
    rotate_log()

    _check_no_other_daemon(force=force)
    write_pid()

    log(f"Review daemon started (PID={os.getpid()})")
    log(f"Watching: {PENDING_DIR}")
    log(f"Poll interval: {POLL_INTERVAL}s, max workers: {MAX_WORKERS}")
    log(f"Orphan age: {ORPHAN_AGE}s, opencode timeout: {OPENCODE_TIMEOUT}s")

    # Recover orphaned requests and clean up stale locks
    recover_orphans()
    _sweep_stale_locks()

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)

    while not _shutdown_requested:
        try:
            requests = get_pending_requests()
            if requests:
                for req_path in requests:
                    if _shutdown_requested:
                        break

                    # Don't claim if we're at max workers
                    if len(_active_workers) >= MAX_WORKERS:
                        break

                    if not claim_request(req_path):
                        continue

                    try:
                        future = executor.submit(_worker_wrapper, req_path, str(req_path))
                        _active_workers[req_path.name] = future
                    except Exception:
                        release_lock(req_path)
                        log(f"Failed to submit worker for {req_path.name}")

                # Clean up completed workers
                _reap_workers()

                # Warn if queue is deep
                if len(requests) > MAX_WORKERS * 5:
                    log(f"WARNING: deep queue — {len(requests)} pending requests, only {MAX_WORKERS} workers")

            # Poll loop
            for _ in range(POLL_INTERVAL):
                if _shutdown_requested:
                    break
                _reap_workers()
                time.sleep(1)

        except Exception:
            log(f"Daemon loop error: {traceback.format_exc()}")
            time.sleep(POLL_INTERVAL)

    # Graceful shutdown: wait for in-flight workers
    if _active_workers:
        log(f"Waiting for {len(_active_workers)} in-flight workers (timeout: {SHUTDOWN_TIMEOUT}s)...")
        deadline = time.time() + SHUTDOWN_TIMEOUT
        while _active_workers and time.time() < deadline:
            _reap_workers()
            if not _active_workers:
                break
            time.sleep(0.5)

    # Kill any still-running subprocesses so worker threads unblock
    with _procs_lock:
        procs = list(_active_procs)
    if procs:
        log(f"Killing {len(procs)} in-flight subprocess(es)...")
        for proc in procs:
            _kill_process_tree(proc)
        with _procs_lock:
            _active_procs.clear()

    executor.shutdown(wait=False)
    log("Daemon shutting down")
    remove_pid()
    log("Daemon stopped")


def _worker_wrapper(req_path: Path, path_str: str) -> bool:
    """Wrapper for process_request that manages lock lifecycle."""
    # path_str is unused (kept for future), req_path is the resolved StrPath
    try:
        return process_request(req_path)
    finally:
        release_lock(req_path)


def _reap_workers() -> None:
    """Remove completed workers from the active set."""
    done = [name for name, future in _active_workers.items() if future.done()]
    for name in done:
        try:
            future = _active_workers.pop(name)
            future.result()
        except Exception:
            pass


def main() -> None:
    global POLL_INTERVAL, OPENCODE_TIMEOUT, ORPHAN_AGE, MAX_WORKERS, SHUTDOWN_TIMEOUT

    parser = argparse.ArgumentParser(
        description="Review Daemon — dispatches review requests to OpenCode",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=POLL_INTERVAL,
        help=f"Seconds between scans (default: {POLL_INTERVAL})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=OPENCODE_TIMEOUT,
        help=f"Timeout per request in seconds (default: {OPENCODE_TIMEOUT})",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=MAX_WORKERS,
        help=f"Maximum concurrent review workers (default: {MAX_WORKERS})",
    )
    parser.add_argument(
        "--orphan-age",
        type=int,
        default=ORPHAN_AGE,
        help=f"Seconds before an in_progress request is considered orphaned (default: {ORPHAN_AGE})",
    )
    parser.add_argument(
        "--shutdown-timeout",
        type=int,
        default=SHUTDOWN_TIMEOUT,
        help=f"Seconds to wait for in-flight workers on shutdown (default: {SHUTDOWN_TIMEOUT})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Override PID guard (allow starting alongside another daemon)",
    )
    args = parser.parse_args()

    POLL_INTERVAL = args.poll_interval
    OPENCODE_TIMEOUT = args.timeout
    ORPHAN_AGE = args.orphan_age
    MAX_WORKERS = args.max_workers
    SHUTDOWN_TIMEOUT = args.shutdown_timeout

    run_daemon(force=args.force)


if __name__ == "__main__":
    main()
