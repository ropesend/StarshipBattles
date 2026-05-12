import os
import time
import wave
import threading
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# PROJ-294: Make the project root importable so the post-session log-copy step
# (line ~232: `from game.core.paths import Paths`) works regardless of the
# launcher's cwd. qa_launcher.py:32 spawns this script with `cwd=observer_dir`
# so that observer's local `.env` loads correctly — but that means the project
# root isn't on `sys.path` and `game.*` imports would crash. Mirrors the pattern
# used by other Tools/ scripts that import from game.* (e.g.
# Tools/visual_test_galaxy/visual_test_galaxy.py:17,
# Tools/analyze_dependency_graph/analyze_dependency_graph.py:26).
# `parents[2]` assumes the file lives at `<root>/Tools/qa_observer/observer.py`;
# update if the script ever moves.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from dotenv import load_dotenv
import sounddevice as sd  # PROJ-295: replaced pyaudio for Python 3.13 wheel availability.
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse
import audioop

# Load configuration
load_dotenv()
load_dotenv('.env')

SCREENSHOTS_DIR = os.getenv('SCREENSHOTS_DIR', r'C:\Users\rossr\Pictures\Screenshots')
SESSION_OUTPUT_DIR = os.getenv('SESSION_OUTPUT_DIR', './session_data')

# Audio configuration
VOICE_THRESHOLD = int(os.getenv('VOICE_THRESHOLD', '450'))
SILENCE_TIMEOUT = float(os.getenv('SILENCE_TIMEOUT', '2.0'))


def _parse_input_device_index(raw: str | None) -> int | None:
    if raw is None:
        return None
    text = raw.strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


# Pinned input device — set by sound_check.py when the system default is the
# wrong mic. Both observer and audio_monitor read this so they always agree.
INPUT_DEVICE_INDEX = _parse_input_device_index(os.getenv('INPUT_DEVICE_INDEX'))

# Audio configuration
CHUNK = 1024
SAMPLE_WIDTH = 2  # bytes per sample for int16 (PROJ-295: was pyaudio.paInt16 = 2)
DTYPE = 'int16'
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 45 # Google cloud direct upload limit is ~1 minute

class ScreenshotHandler(FileSystemEventHandler):
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def on_created(self, event):
        if event.is_directory:
            return
            
        filepath = Path(event.src_path)
        if filepath.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            # Wait a brief moment to ensure Snipping Tool has finished writing the file
            time.sleep(1.0) 
            
            timestamp = datetime.now()
            # Standardized name based on when we noticed it
            new_filename = f"bug_capture_{timestamp.strftime('%H%M%S')}.png"
            dest_path = self.output_dir / new_filename
            
            try:
                shutil.copy2(filepath, dest_path)
                # We save a sidecar file with the exact unixtime for processor syncing
                with open(dest_path.with_suffix('.txt'), 'w') as f:
                    f.write(str(timestamp.timestamp()))
                print(f"[Screenshot] Captured: {new_filename}")
            except Exception as e:
                print(f"[Screenshot] Error copying file {filepath}: {e}")

def record_audio_loop(audio_output_dir):
    # PROJ-295: sounddevice replaces pyaudio. Same PortAudio backend, different API.
    # `RawInputStream.read(N)` returns (cffi_buffer, overflow_flag); we convert
    # the buffer to plain bytes for audioop / wave compatibility.
    try:
        stream = sd.RawInputStream(
            samplerate=RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=CHUNK,
            device=INPUT_DEVICE_INDEX,
        )
        stream.start()
    except Exception as e:
        print(f"Failed to open audio stream. Do you have a microphone connected? Error: {e}")
        return

    device_label = "system default" if INPUT_DEVICE_INDEX is None else f"index {INPUT_DEVICE_INDEX}"
    print(f"[Audio] Started continuous recording on device: {device_label} (chunking every {RECORD_SECONDS} seconds)")

    exit_event = threading.Event()

    def stdin_listener():
        while not exit_event.is_set():
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                if "QUIT" in line:
                    print("\n[Observer] Quit signal received from launcher.")
                    exit_event.set()
                    break
            except (IOError, EOFError):
                break

    # We start a daemon thread to listen for the explicit QUIT from qa_launcher
    listener_thread = threading.Thread(target=stdin_listener, daemon=True)
    listener_thread.start()

    try:
        sample_width = SAMPLE_WIDTH

        while not exit_event.is_set():
            print("\nListening for voice...")
            is_recording = False
            frames = []
            silence_start_time = None
            chunk_start_time = None

            while not exit_event.is_set():
                try:
                    raw, _overflow = stream.read(CHUNK)
                    data = bytes(raw)
                except Exception as e:
                    print(f"Audio read error: {e}")
                    break

                rms = audioop.rms(data, sample_width)
                
                if not is_recording:
                    if rms > VOICE_THRESHOLD:
                        is_recording = True
                        # The start time is critical for the processor.py synchronization
                        chunk_start_time = time.time()
                        frames.append(data)
                        print(f"[Audio] Voice detected (RMS: {rms}). Recording started...")
                        # If you want to debug RMS levels continuously, uncomment below:
                        # print(f"RMS: {rms}")
                else:
                    frames.append(data)
                    
                    if rms < VOICE_THRESHOLD:
                        if silence_start_time is None:
                            silence_start_time = time.time()
                        elif time.time() - silence_start_time > SILENCE_TIMEOUT:
                            # Silence timeout reached
                            print(f"[Audio] Silence detected. Saving chunk...")
                            break
                    else:
                        silence_start_time = None
                        
                    # Also respect max RECORD_SECONDS to send to Google API
                    if time.time() - chunk_start_time > RECORD_SECONDS:
                        print(f"[Audio] Max chunk length reached ({RECORD_SECONDS}s). Saving chunk...")
                        break

            if frames and is_recording:
                timestamp_str = datetime.now().strftime('%H%M%S')
                filename = audio_output_dir / f"audio_{timestamp_str}.wav"
                
                wf = wave.open(str(filename), 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(sample_width)
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                # Save the exact start time in a sidecar file
                with open(filename.with_suffix('.txt'), 'w') as f:
                    f.write(str(chunk_start_time))
                    
                print(f"[Audio] Saved chunk: {filename.name}")
            
    except KeyboardInterrupt:
        # Save any partial frames that were collected before the interrupt
        if 'frames' in locals() and frames and is_recording:
            timestamp_str = datetime.now().strftime('%H%M%S')
            filename = audio_output_dir / f"audio_{timestamp_str}.wav"

            wf = wave.open(str(filename), 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            with open(filename.with_suffix('.txt'), 'w') as f:
                f.write(str(chunk_start_time))
            print(f"[Audio] Saved partial chunk: {filename.name}")
    finally:
        stream.stop()
        stream.close()

def main():
    parser = argparse.ArgumentParser(description="QA Observer.")
    parser.add_argument("--child", action="store_true", help="Running as child of qa_launcher.py")
    args = parser.parse_args()

    print("=== StarshipBattles QA Observer ===")
    
    # Setup session directory
    session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = Path(SESSION_OUTPUT_DIR) / session_time
    audio_dir = session_dir / "audio"
    images_dir = session_dir / "images"
    
    audio_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Session data will be stored in: {session_dir}")
    print(f"Monitoring screenshots at: {SCREENSHOTS_DIR}")
    
    # Setup watchdog observer for Snipping tool
    event_handler = ScreenshotHandler(images_dir)
    observer = Observer()
    
    if os.path.exists(SCREENSHOTS_DIR):
        observer.schedule(event_handler, SCREENSHOTS_DIR, recursive=False)
        observer.start()
    else:
        print(f"WARNING: Screenshots directory not found: {SCREENSHOTS_DIR}")
        print("Please check your .env file or Windows Snipping Tool settings.")
        
    try:
        # Start audio recording in the main thread so KeyboardInterrupt works easily
        record_audio_loop(audio_dir)
    except KeyboardInterrupt:
        print("\nStopping QA Observer recording...")
    finally:
        if observer.is_alive():
            observer.stop()
            observer.join()

        # Copy game logs into session data before processing
        logs_dest = session_dir / "logs"
        logs_dest.mkdir(exist_ok=True)
        from game.core.paths import Paths
        game_logs_dir = Path(Paths.LOGS_DIR)
        log_files = [
            "battle.log",
            "battle_log.txt",
            "crash_log.txt",
            "combat_lab.log",
            "profiling_history.json",
        ]
        for name in log_files:
            src = game_logs_dir / name
            if src.exists():
                shutil.copy2(src, logs_dest / name)
                print(f"[Logs] Copied {name} into session data.")

        # If running independently, run processor.py
        # If running as child, the launcher handles the end-of-session
        if not args.child:
            print(f"\nSession ended. Automatically processing {session_dir}...")
            
            # Determine the python executable to use
            python_exe = sys.executable
            processor_script = str(Path(__file__).parent / "processor.py")
            
            try:
                subprocess.run([python_exe, processor_script, str(session_dir)], check=True)
                print("\nObserver standalone workflow complete!")
            except subprocess.CalledProcessError as e:
                print(f"\nError running processor.py: {e}")
            except Exception as e:
                print(f"\nFailed to launch processor.py: {e}")
        else:
            print("\nObserver child process ended cleanly.")

if __name__ == "__main__":
    main()
