import os
import time
import wave
import threading
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pyaudio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse

# Load configuration
load_dotenv()
load_dotenv('.env')

SCREENSHOTS_DIR = os.getenv('SCREENSHOTS_DIR', r'C:\Users\rossr\Pictures\Screenshots')
SESSION_OUTPUT_DIR = os.getenv('SESSION_OUTPUT_DIR', './session_data')

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
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
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"Failed to open audio stream. Do you have a microphone connected? Error: {e}")
        return

    print(f"[Audio] Started continuous recording (chunking every {RECORD_SECONDS} seconds)")
    
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
        while not exit_event.is_set():
            # The start time is critical for the processor.py synchronization
            start_time = time.time()
            timestamp_str = datetime.now().strftime('%H%M%S')
            filename = audio_output_dir / f"audio_{timestamp_str}.wav"
            
            frames = []
            
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                if exit_event.is_set():
                    break
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"Audio read error: {e}")
                    break
                    
            wf = wave.open(str(filename), 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Save the exact start time in a sidecar file
            with open(filename.with_suffix('.txt'), 'w') as f:
                f.write(str(start_time))
                
            print(f"[Audio] Saved chunk: {filename.name}")
            
    except KeyboardInterrupt:
        # Save any partial frames that were collected before the interrupt
        if 'frames' in locals() and frames:
            wf = wave.open(str(filename), 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            with open(filename.with_suffix('.txt'), 'w') as f:
                f.write(str(start_time))
            print(f"[Audio] Saved partial chunk: {filename.name}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

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
