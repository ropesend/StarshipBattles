import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _find_project_root():
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return str(current)
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = _find_project_root()
sys.path.insert(0, PROJECT_ROOT)

from game.core.paths import Paths

REVIEWS_DIR = os.path.join(PROJECT_ROOT, "Reviews", "results")
TOOLS_DIR = os.path.join(PROJECT_ROOT, "Tools")
AUDIT_DIR = os.path.join(TOOLS_DIR, "audit_shrink")


def _run_tool(cmd, output_file, label):
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=PROJECT_ROOT,
        )
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n\n--- STDERR ---\n")
                    f.write(result.stderr)
        status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
        print(f"  [{status}] {label}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {label}")
        return False
    except FileNotFoundError as e:
        print(f"  [MISSING] {label} — {e}")
        return False


def run(force_output_dir=None):
    date_slug = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = force_output_dir or os.path.join(REVIEWS_DIR, f"{date_slug}_audit_shrink")
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print(f"=== Phase 1: Deterministic Analysis ===")
    print(f"Output: {output_dir}")
    print()

    # Step 1: LOC baseline
    print("1. LOC baseline...")
    _run_tool(
        [sys.executable, os.path.join(TOOLS_DIR, "loc", "loc.py"), "--detailed"],
        os.path.join(raw_dir, "loc_baseline.txt"),
        "loc",
    )

    # Step 2-3: Vulture dead code
    print("2. Vulture (100% confidence)...")
    _run_tool(
        [sys.executable, "-m", "vulture", str(Paths.GAME_DIR), "--min-confidence", "100"],
        os.path.join(raw_dir, "vulture_100.txt"),
        "vulture 100%",
    )

    print("3. Vulture (80% confidence)...")
    _run_tool(
        [sys.executable, "-m", "vulture", str(Paths.GAME_DIR), "--min-confidence", "80"],
        os.path.join(raw_dir, "vulture_80.txt"),
        "vulture 80%",
    )

    # Step 4: Orphan check
    print("4. Orphan module check...")
    _run_tool(
        [sys.executable, os.path.join(TOOLS_DIR, "check_orphans", "check_orphans.py")],
        os.path.join(raw_dir, "orphans.txt"),
        "check_orphans",
    )

    # Step 5: Dependency graph
    print("5. Dependency graph (unreachable files)...")
    _run_tool(
        [sys.executable, os.path.join(TOOLS_DIR, "analyze_dependency_graph", "analyze_dependency_graph.py")],
        os.path.join(raw_dir, "dead_deps.txt"),
        "analyze_dependency_graph",
    )

    # Step 6: Radon complexity
    print("6. Cyclomatic complexity (radon)...")
    _run_tool(
        [sys.executable, "-m", "radon", "cc", str(Paths.GAME_DIR), "-s", "-n", "C", "-a", "--json"],
        os.path.join(raw_dir, "radon.json"),
        "radon",
    )

    # Step 7: Clone detector
    print("7. Clone detector...")
    _run_tool(
        [sys.executable, os.path.join(AUDIT_DIR, "clone_detector.py"), os.path.join(raw_dir, "clones.json")],
        None,
        "clone_detector",
    )

    # Step 8: Manifest with rotation
    print("8. File manifest + shard rotation...")
    _run_tool(
        [sys.executable, os.path.join(AUDIT_DIR, "manifest.py"), raw_dir],
        None,
        "manifest",
    )

    print()
    print(f"Phase 1 complete. Raw results saved to: {raw_dir}")
    print(f"Output directory: {output_dir}")
    return output_dir


if __name__ == "__main__":
    force_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run(force_dir)
