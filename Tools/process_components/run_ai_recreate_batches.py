from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[2]
RECREATE = REPO_ROOT / "Tools" / "process_components" / "recreate_ai_samples.py"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "assets" / "Images" / "Components" / "_ai_recreate_enhanced_preview"
STATUS_PATH = REPO_ROOT / "output" / "ai_enhanced_batch_status.json"
LOG_DIR = REPO_ROOT / "output"


def timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def validate_outputs(output_root: Path) -> dict:
    output_dir = output_root / "Components 1024"
    files = sorted(output_dir.glob("*.png"))
    bad_dimensions = []
    for path in files:
        with Image.open(path) as image:
            if image.size != (1024, 1024):
                bad_dimensions.append({"file": path.name, "size": list(image.size)})
    return {"count": len(files), "bad_dimensions": bad_dimensions}


def write_status(status: dict) -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(status, indent=2), encoding="utf-8")


def run_batch(start: int, end: int, output_root: Path, quality: str, retries: int, retry_delay: int) -> dict:
    batch_id = f"{start:03d}_{end:03d}"
    stdout_path = LOG_DIR / f"ai_enhanced_{batch_id}.log"
    stderr_path = LOG_DIR / f"ai_enhanced_{batch_id}.err.log"
    names = [f"{index:03d}" for index in range(start, end + 1)]
    command = [
        sys.executable,
        str(RECREATE),
        "--mode",
        "enhanced",
        "--names",
        *names,
        "--output-root",
        str(output_root),
        "--quality",
        quality,
        "--retries",
        str(retries),
        "--retry-delay",
        str(retry_delay),
    ]

    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        result = subprocess.run(command, cwd=REPO_ROOT, stdout=stdout, stderr=stderr, text=True)

    validation = validate_outputs(output_root)
    return {
        "batch": batch_id,
        "start": start,
        "end": end,
        "returncode": result.returncode,
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
        "validation": validation,
        "finished_at": timestamp(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run enhanced AI component recreation in tracked batches.")
    parser.add_argument("--start", type=int, default=150)
    parser.add_argument("--end", type=int, default=538)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--quality", choices=["low", "medium", "high", "auto"], default="medium")
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--retry-delay", type=int, default=60)
    args = parser.parse_args()

    status = {
        "state": "running",
        "started_at": timestamp(),
        "output_root": str(args.output_root),
        "start": args.start,
        "end": args.end,
        "batch_size": args.batch_size,
        "batches": [],
    }
    write_status(status)

    for batch_start in range(args.start, args.end + 1, args.batch_size):
        batch_end = min(batch_start + args.batch_size - 1, args.end)
        status["current_batch"] = f"{batch_start:03d}_{batch_end:03d}"
        status["updated_at"] = timestamp()
        write_status(status)

        result = run_batch(batch_start, batch_end, args.output_root, args.quality, args.retries, args.retry_delay)
        status["batches"].append(result)
        status["updated_at"] = timestamp()

        if result["returncode"] != 0 or result["validation"]["bad_dimensions"]:
            status["state"] = "failed"
            status["failed_batch"] = result["batch"]
            write_status(status)
            raise SystemExit(result["returncode"] or 1)

        write_status(status)

    status["state"] = "completed"
    status["completed_at"] = timestamp()
    status["current_batch"] = None
    status["final_validation"] = validate_outputs(args.output_root)
    write_status(status)


if __name__ == "__main__":
    main()
