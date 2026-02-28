import os
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
                last_time = item["time"]
                
                # Rudimentary sentence breaking if long pause
                if current_sentence and (item["time"] - last_time > 3.0):
                    ts_str = datetime.fromtimestamp(sentence_start_time).strftime("%H:%M:%S")
                    f.write(f"**[{ts_str}]** " + " ".join(current_sentence) + ".\n\n")
                    current_sentence = []
                    sentence_start_time = None
                    
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
        
    print("Generating synchronized Markdown...")
    generate_markdown(session_dir, all_words, screenshots)

if __name__ == "__main__":
    main()
