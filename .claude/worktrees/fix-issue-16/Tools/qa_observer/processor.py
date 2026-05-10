import os
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from google.cloud import speech
from dotenv import load_dotenv

# Load configuration
load_dotenv()
load_dotenv('.env')

def get_audio_files(session_dir: Path):
    audio_dir = session_dir / "audio"
    if not audio_dir.exists():
        return []
    
    files = []
    for f in audio_dir.glob("*.wav"):
        txt_file = f.with_suffix('.txt')
        if txt_file.exists():
            with open(txt_file, 'r') as tf:
                start_time = float(tf.read().strip())
                files.append({"path": f, "start_time": start_time})
                
    # Sort by start time
    files.sort(key=lambda x: x["start_time"])
    return files

def get_screenshots(session_dir: Path):
    images_dir = session_dir / "images"
    if not images_dir.exists():
        return []

    images = []
    for f in images_dir.glob("*.*"):
        if f.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            txt_file = f.with_suffix('.txt')
            if txt_file.exists():
                with open(txt_file, 'r') as tf:
                    capture_time = float(tf.read().strip())
                    images.append({"path": f, "capture_time": capture_time})
                    
    images.sort(key=lambda x: x["capture_time"])
    return images

def transcribe_audio_chunk(client, filepath: Path, global_start_time: float):
    """Transcribes one audio file and returns a list of words with global timestamps."""
    with open(filepath, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_word_time_offsets=True,
    )

    print(f"  Transcribing {filepath.name}...")
    response = client.recognize(config=config, audio=audio)

    words = []
    for result in response.results:
        alternative = result.alternatives[0]
        for word_info in alternative.words:
            word = word_info.word
            
            # Extract time offsets
            start_time = word_info.start_time
            # Convert Duration to float seconds
            word_offset = start_time.seconds + start_time.microseconds * 1e-6
            
            global_word_time = global_start_time + word_offset
            words.append({
                "word": word,
                "time": global_word_time
            })
            
    return words

def write_word_timestamps(session_dir: Path, words: list):
    """Write per-word timestamps to a JSONL file for precise time lookups.

    Each line includes a sliding-window 'context' field (last ~8 words)
    so agents can match phrases rather than isolated words.
    """
    output_path = session_dir / "word_timestamps.jsonl"
    context_window_size = 8
    recent_words = []
    with open(output_path, 'w', encoding='utf-8') as f:
        for w in words:
            recent_words.append(w["word"])
            if len(recent_words) > context_window_size:
                recent_words.pop(0)
            ts_str = datetime.fromtimestamp(w["time"]).strftime("%H:%M:%S")
            line = json.dumps({
                "time": round(w["time"], 2),
                "ts": ts_str,
                "word": w["word"],
                "context": " ".join(recent_words),
            })
            f.write(line + "\n")
    print(f"Word timestamps written to {output_path}")


def load_filler_words() -> set:
    """Load filler words from FILLER_WORDS env var (comma-separated, case-insensitive)."""
    raw = os.getenv("FILLER_WORDS", "")
    if not raw.strip():
        return set()
    return {w.strip().lower() for w in raw.split(",") if w.strip()}


def filter_filler_words(words: list, filler_set: set) -> list:
    """Remove filler words from the word list for markdown output.

    Matching is case-insensitive and ignores trailing punctuation so that
    Google Speech variants like 'Um,' or 'uh.' are caught.
    """
    if not filler_set:
        return words
    filtered = []
    for w in words:
        cleaned = w["word"].strip(".,!?;:").lower()
        if cleaned not in filler_set:
            filtered.append(w)
    return filtered


def generate_markdown(session_dir: Path, words: list, screenshots: list):
    output_path = session_dir / "QA_Session_Log.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# QA Session Log - {session_dir.name}\n\n")
        
        # Merge sort words and screenshots into a single timeline
        timeline = []
        for w in words:
            timeline.append({"type": "word", "time": w["time"], "data": w["word"]})
            
        for s in screenshots:
            # We delay the image placement slightly so it appears after the sentence
            # representing the user talking, then snapping.
            # However, we'll keep its true capture_time in the element data.
            timeline.append({"type": "image", "time": s["capture_time"] - 2.0, "true_time": s["capture_time"], "data": s["path"]})
            
        timeline.sort(key=lambda x: x["time"])
        
        current_sentence = []
        sentence_start_time = None
        last_time = 0
        
        for item in timeline:
            if item["type"] == "word":
                if not current_sentence:
                    sentence_start_time = item["time"]
                current_sentence.append(item["data"])

                # Sentence breaking on long pause (>3s gap between words)
                if last_time > 0 and (item["time"] - last_time > 3.0) and len(current_sentence) > 1:
                    # Flush everything except the word we just appended (it starts the next sentence)
                    new_word = current_sentence.pop()
                    ts_str = datetime.fromtimestamp(sentence_start_time).strftime("%H:%M:%S")
                    f.write(f"**[{ts_str}]** " + " ".join(current_sentence) + ".\n\n")
                    current_sentence = [new_word]
                    sentence_start_time = item["time"]

                last_time = item["time"]
                    
            elif item["type"] == "image":
                # Print any pending words first
                if current_sentence:
                    ts_str = datetime.fromtimestamp(sentence_start_time).strftime("%H:%M:%S")
                    f.write(f"**[{ts_str}]** " + " ".join(current_sentence) + "...\n\n")
                    current_sentence = []
                    sentence_start_time = None
                
                # Make the relative path link
                img_ts_str = datetime.fromtimestamp(item["true_time"]).strftime("%H:%M:%S")
                rel_path = item["data"].relative_to(session_dir).as_posix()
                f.write(f"**[{img_ts_str}] 📸 *Screenshot***\n![{item['data'].name}]({rel_path})\n\n")

        # Flush remaining words
        if current_sentence:
            ts_str = datetime.fromtimestamp(sentence_start_time).strftime("%H:%M:%S")
            f.write(f"**[{ts_str}]** " + " ".join(current_sentence) + ".\n\n")

        # Append Game Logs section if logs were captured
        logs_dir = session_dir / "logs"
        if logs_dir.exists():
            log_descriptions = {
                "battle.log": "Main game log (DEBUG level, `asctime` timestamps)",
                "battle_log.txt": "Combat simulation events",
                "crash_log.txt": "Crash tracebacks",
                "combat_lab.log": "Combat Lab test framework log",
                "profiling_history.json": "Performance profiling data",
            }
            log_files = sorted(f for f in logs_dir.iterdir() if f.is_file())
            if log_files:
                f.write("---\n## Game Logs\n\n")
                for log_file in log_files:
                    rel = log_file.relative_to(session_dir).as_posix()
                    desc = log_descriptions.get(log_file.name, "")
                    suffix = f" — {desc}" if desc else ""
                    f.write(f"- [{log_file.name}]({rel}){suffix}\n")
                f.write("\n")

    print(f"\nSuccess! Markdown written to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Process QA Session audio and images.")
    parser.add_argument("session_dir", type=str, help="Path to the session_data/TIMESTAMP folder")
    args = parser.parse_args()

    session_dir = Path(args.session_dir)
    if not session_dir.exists():
        print(f"Error: Session directory '{session_dir}' does not exist.")
        return

    # Initialize Google Cloud Client
    try:
        client = speech.SpeechClient()
    except Exception as e:
        print(f"Error initializing Google Cloud Speech Client: {e}")
        print("Did you set GOOGLE_APPLICATION_CREDENTIALS in your environment or .env?")
        return

    print(f"Processing session: {session_dir}")

    audio_files = get_audio_files(session_dir)
    screenshots = get_screenshots(session_dir)
    
    print(f"Found {len(audio_files)} audio chunks and {len(screenshots)} screenshots.")

    all_words = []
    for chunk in audio_files:
        words = transcribe_audio_chunk(client, chunk["path"], chunk["start_time"])
        all_words.extend(words)
        
    print("Writing word-level timestamps...")
    write_word_timestamps(session_dir, all_words)

    # Filter filler words for markdown only (JSONL keeps the raw transcript)
    filler_set = load_filler_words()
    if filler_set:
        filtered_words = filter_filler_words(all_words, filler_set)
        removed = len(all_words) - len(filtered_words)
        if removed:
            print(f"Filtered {removed} filler word(s) from transcript.")
    else:
        filtered_words = all_words

    print("Generating synchronized Markdown...")
    generate_markdown(session_dir, filtered_words, screenshots)

    # Prune old sessions, keeping only the 5 most recent
    prune_old_sessions(session_dir.parent, keep=5)


def prune_old_sessions(sessions_root: Path, keep: int = 5):
    """Delete oldest session directories, keeping only the most recent `keep`."""
    if not sessions_root.exists():
        return

    session_dirs = sorted(
        [d for d in sessions_root.iterdir() if d.is_dir()],
        key=lambda d: d.name
    )

    if len(session_dirs) <= keep:
        return

    to_delete = session_dirs[:len(session_dirs) - keep]
    for d in to_delete:
        print(f"Pruning old session: {d.name}")
        shutil.rmtree(d)


if __name__ == "__main__":
    main()
