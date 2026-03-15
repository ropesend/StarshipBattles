import os
import sys
import subprocess
import signal
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    observer_script = os.path.join(root_dir, 'tools', 'qa_observer', 'observer.py')
    game_script = os.path.join(root_dir, 'launcher.py')
    
    python_exe = sys.executable

    if not os.path.exists(observer_script):
        print(f"Error: Could not find QA Observer at {observer_script}")
        sys.exit(1)

    print("=== StarshipBattles QA Debug Launcher ===")
    print("Launching QA Observer in the background...")

    # Needs CREATE_NEW_PROCESS_GROUP on Windows to separate Ctrl+C handling
    creation_flags = 0
    if os.name == 'nt':
        creation_flags = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0x00000200)

    # We run it from its own sub-directory so its .env loads correctly relative to itself
    observer_dir = os.path.dirname(observer_script)

    # Open a pipe to stdin so we can explicitly tell it to quit across platforms
    observer_process = subprocess.Popen(
        [python_exe, observer_script, '--child'],
        cwd=observer_dir,
        creationflags=creation_flags,
        stdin=subprocess.PIPE
    )

    # Launch the audio monitor window so user can verify mic is working
    audio_monitor_script = os.path.join(observer_dir, 'audio_monitor.py')
    monitor_process = None
    if os.path.exists(audio_monitor_script):
        print("Launching Audio Monitor window...")
        monitor_process = subprocess.Popen(
            [python_exe, audio_monitor_script],
            cwd=observer_dir,
            creationflags=creation_flags,
            stdin=subprocess.PIPE
        )

    # Give the observer a second to initialize microphone/watchdog before starting the game
    time.sleep(1.5)

    print(f"\nLaunching Game Engine...")
    game_process = subprocess.Popen(
        [python_exe, game_script],
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
    sessions_path = os.path.join(observer_dir, 'session_data')
    session_dirs = sorted(glob.glob(os.path.join(sessions_path, '*')))
    
    if session_dirs:
        latest_session = session_dirs[-1]
        print(f"\nProcessing QA Session Data: {latest_session}")
        processor_script = os.path.join(observer_dir, 'processor.py')
        subprocess.run([python_exe, processor_script, latest_session])
    else:
        print("\nNo session data found to process.")
    
    print("\n=== QA Debug Run Complete ===")

if __name__ == "__main__":
    main()
