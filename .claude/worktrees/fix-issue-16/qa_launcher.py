from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from collections.abc import Sequence
from pathlib import Path


QA_REQUIRED_IMPORTS = (
    ("dotenv", "python-dotenv"),
    ("sounddevice", "sounddevice"),
    ("watchdog.observers", "watchdog"),
    ("google.cloud.speech", "google-cloud-speech"),
    ("audioop", "audioop-lts"),
)
QA_TARGET_PYTHON_VERSION = (3, 14)


def resolve_python_executable(root_dir: str | os.PathLike[str]) -> str:
    """Prefer the project venv so QA child processes get dev-tool deps."""
    root = Path(root_dir)
    if os.name == "nt":
        venv_python = root / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = root / ".venv" / "bin" / "python"

    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def find_missing_qa_dependencies(python_exe: str) -> list[str]:
    """Return package names whose import checks fail in the selected Python."""
    missing_packages: list[str] = []
    for import_name, package_name in QA_REQUIRED_IMPORTS:
        result = subprocess.run(
            [python_exe, "-c", f"import {import_name}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            missing_packages.append(package_name)
    return missing_packages


def get_python_version(python_exe: str) -> tuple[int, int] | None:
    """Return the selected interpreter's major/minor version."""
    result = subprocess.run(
        [
            python_exe,
            "-c",
            "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    try:
        major, minor = result.stdout.strip().split(".", maxsplit=1)
    except ValueError:
        return None
    return int(major), int(minor)


def is_supported_qa_python_version(version: tuple[int, int] | None) -> bool:
    """QA launcher is pinned to the validated Python runtime."""
    return version == QA_TARGET_PYTHON_VERSION


def print_python_version_error(python_exe: str, version: tuple[int, int] | None) -> None:
    """Print setup guidance when the selected interpreter is not QA-supported."""
    expected = ".".join(str(part) for part in QA_TARGET_PYTHON_VERSION)
    actual = "unknown" if version is None else ".".join(str(part) for part in version)
    print("\nError: QA launcher requires Python 3.14.")
    print(f"Selected Python: {python_exe}")
    print(f"Selected version: {actual}")
    print("\nRebuild the project environment from the repo root:")
    print(r"  py -3.14 -m venv .venv")
    print(r"  .venv\Scripts\python.exe -m pip install -r requirements-dev.txt")
    print(f"\nExpected QA runtime: Python {expected}.")


def print_dependency_error(python_exe: str, missing_packages: Sequence[str]) -> None:
    """Print setup guidance before any child process starts."""
    print("\nError: QA launcher dependencies are missing.")
    print(f"Selected Python: {python_exe}")
    print(f"Missing packages: {', '.join(missing_packages)}")
    print("\nSet up the project environment from the repo root:")
    print(r"  py -3.14 -m venv .venv")
    print(r"  .venv\Scripts\python.exe -m pip install -r requirements-dev.txt")
    print("\nThe launcher will use .venv automatically once it exists.")


def main() -> None:
    root_dir = Path(__file__).resolve().parent
    observer_script = root_dir / "Tools" / "qa_observer" / "observer.py"
    game_script = root_dir / "launcher.py"

    python_exe = resolve_python_executable(root_dir)
    python_version = get_python_version(python_exe)
    if not is_supported_qa_python_version(python_version):
        print_python_version_error(python_exe, python_version)
        sys.exit(1)

    missing_packages = find_missing_qa_dependencies(python_exe)
    if missing_packages:
        print_dependency_error(python_exe, missing_packages)
        sys.exit(1)

    if not os.path.exists(observer_script):
        print(f"Error: Could not find QA Observer at {observer_script}")
        sys.exit(1)

    print("=== StarshipBattles QA Debug Launcher ===")
    print(f"Using Python: {python_exe}")
    print("Launching QA Observer in the background...")

    # Needs CREATE_NEW_PROCESS_GROUP on Windows to separate Ctrl+C handling
    creation_flags = 0
    if os.name == 'nt':
        creation_flags = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0x00000200)

    # We run it from its own sub-directory so its .env loads correctly relative to itself
    observer_dir = observer_script.parent

    # Open a pipe to stdin so we can explicitly tell it to quit across platforms
    observer_process = subprocess.Popen(
        [python_exe, str(observer_script), '--child'],
        cwd=observer_dir,
        creationflags=creation_flags,
        stdin=subprocess.PIPE
    )

    # Launch the audio monitor window so user can verify mic is working
    audio_monitor_script = observer_dir / "audio_monitor.py"
    monitor_process = None
    if os.path.exists(audio_monitor_script):
        print("Launching Audio Monitor window...")
        monitor_process = subprocess.Popen(
            [python_exe, str(audio_monitor_script)],
            cwd=observer_dir,
            creationflags=creation_flags,
            stdin=subprocess.PIPE
        )

    # Give the observer a second to initialize microphone/watchdog before starting the game
    time.sleep(1.5)

    print(f"\nLaunching Game Engine...")
    game_process = subprocess.Popen(
        [python_exe, str(game_script)],
        cwd=root_dir
    )

    try:
        # Wait for the user to close the game window or exit the game
        game_process.wait()
    except KeyboardInterrupt:
        # If the user hits Ctrl+C in this launcher window, just kill the game
        print("\nForce-quitting game...")
        if os.name == 'nt':
            game_process.send_signal(signal.CTRL_C_EVENT)
        else:
            game_process.terminate()
        game_process.wait()

    print(f"\nGame process finished (Exit code: {game_process.returncode}).")
    print("Shutting down QA Observer (this will trigger processing)...")

    # Shut down the audio monitor window
    if monitor_process and monitor_process.poll() is None:
        try:
            monitor_process.communicate(input=b"QUIT\n", timeout=5)
        except subprocess.TimeoutExpired:
            monitor_process.kill()

    # Gracefully tell the observer to stop via standard input messaging
    try:
        observer_process.communicate(input=b"QUIT\n", timeout=15)
    except subprocess.TimeoutExpired:
        print("Observer took too long to quit. Forcing termination.")
        observer_process.kill()

    # Wait for the observer to finish
    observer_process.wait()

    # In child mode, the observer doesn't process itself, so we do it here.
    # To do that, we need to know the session dir it created. Let's find the newest one.
    import glob
    sessions_path = observer_dir / "session_data"
    session_dirs = sorted(glob.glob(os.path.join(sessions_path, '*')))
    
    if session_dirs:
        latest_session = session_dirs[-1]
        print(f"\nProcessing QA Session Data: {latest_session}")
        processor_script = observer_dir / "processor.py"
        subprocess.run([python_exe, str(processor_script), latest_session], check=False)
    else:
        print("\nNo session data found to process.")
    
    print("\n=== QA Debug Run Complete ===")

if __name__ == "__main__":
    main()
