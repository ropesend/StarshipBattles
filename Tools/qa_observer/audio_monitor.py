"""
Real-time audio level monitor window for QA sessions.
Shows a level meter bar, waveform display, and current RMS value
so the user can verify their microphone is working during QA recording.

Spawned by qa_launcher.py as a separate process.
"""
import sys
import struct
import threading
import tkinter as tk
import pyaudio
import audioop
from collections import deque
from dotenv import load_dotenv
import os

load_dotenv()
load_dotenv('.env')

# Match observer.py audio config
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
VOICE_THRESHOLD = int(os.getenv('VOICE_THRESHOLD', '300'))

# Monitor display config
WINDOW_SIZE = 512
BAR_HEIGHT = 60
WAVEFORM_HEIGHT = 300
UPDATE_MS = 50  # refresh rate in ms
WAVEFORM_SAMPLES = 256  # number of points to draw in waveform
RMS_HISTORY_LEN = 100  # number of RMS values to keep for the rolling bar history


class AudioMonitor:
    def __init__(self):
        self.running = True
        self.current_rms = 0
        self.peak_rms = 0
        self.peak_decay_counter = 0
        self.waveform_data = deque(maxlen=WAVEFORM_SAMPLES)
        self.rms_history = deque(maxlen=RMS_HISTORY_LEN)
        self.is_recording = False  # tracks if RMS > threshold
        self.mic_error = None

        # Initialize audio
        self.pa = pyaudio.PyAudio()
        try:
            self.stream = self.pa.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
        except Exception as e:
            self.mic_error = str(e)
            self.stream = None

        # Build UI
        self.root = tk.Tk()
        self.root.title("QA Audio Monitor")
        self.root.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Also listen for QUIT on stdin (from launcher)
        self.stdin_thread = threading.Thread(target=self._stdin_listener, daemon=True)
        self.stdin_thread.start()

        # Header label
        self.header = tk.Label(
            self.root, text="Audio Monitor", font=("Consolas", 12, "bold"),
            fg="#e0e0e0", bg="#1a1a2e"
        )
        self.header.pack(pady=(8, 2))

        # RMS readout
        self.rms_label = tk.Label(
            self.root, text="RMS: 0", font=("Consolas", 10),
            fg="#888888", bg="#1a1a2e"
        )
        self.rms_label.pack(pady=(0, 4))

        # Status label (listening / recording)
        self.status_label = tk.Label(
            self.root, text="LISTENING", font=("Consolas", 10, "bold"),
            fg="#4a9eff", bg="#1a1a2e"
        )
        self.status_label.pack(pady=(0, 4))

        # Canvas for level meter bar
        self.bar_canvas = tk.Canvas(
            self.root, width=WINDOW_SIZE - 40, height=BAR_HEIGHT,
            bg="#0d0d1a", highlightthickness=1, highlightbackground="#333355"
        )
        self.bar_canvas.pack(padx=20, pady=(0, 8))

        # Canvas for waveform
        self.wave_canvas = tk.Canvas(
            self.root, width=WINDOW_SIZE - 40, height=WAVEFORM_HEIGHT,
            bg="#0d0d1a", highlightthickness=1, highlightbackground="#333355"
        )
        self.wave_canvas.pack(padx=20, pady=(0, 8))

        # Threshold info
        self.thresh_label = tk.Label(
            self.root, text=f"Voice Threshold: {VOICE_THRESHOLD}",
            font=("Consolas", 9), fg="#666666", bg="#1a1a2e"
        )
        self.thresh_label.pack(pady=(0, 4))

        if self.mic_error:
            self.status_label.config(text="MIC ERROR", fg="#ff4444")
            self.rms_label.config(text=self.mic_error[:60], fg="#ff4444")
        else:
            # Start audio reading thread
            self.audio_thread = threading.Thread(target=self._read_audio, daemon=True)
            self.audio_thread.start()

        # Start UI update loop
        self.root.after(UPDATE_MS, self._update_display)

    def _stdin_listener(self):
        """Listen for QUIT signal from launcher on stdin."""
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line or "QUIT" in line:
                    self.running = False
                    self.root.after(0, self._on_close)
                    break
            except (IOError, EOFError):
                break

    def _read_audio(self):
        """Continuously read audio data in a background thread."""
        sample_width = self.pa.get_sample_size(FORMAT)
        while self.running and self.stream:
            try:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                rms = audioop.rms(data, sample_width)
                self.current_rms = rms
                self.rms_history.append(rms)
                self.is_recording = rms > VOICE_THRESHOLD

                # Track peak with decay
                if rms > self.peak_rms:
                    self.peak_rms = rms
                    self.peak_decay_counter = 0
                else:
                    self.peak_decay_counter += 1
                    if self.peak_decay_counter > 30:  # ~1.5s at 50ms updates
                        self.peak_rms = max(self.peak_rms * 0.95, rms)

                # Extract waveform samples (downsample for display)
                samples = struct.unpack(f'<{CHUNK}h', data)
                step = max(1, len(samples) // WAVEFORM_SAMPLES)
                self.waveform_data.clear()
                for i in range(0, len(samples), step):
                    self.waveform_data.append(samples[i])

            except Exception:
                if not self.running:
                    break

    def _update_display(self):
        """Update the visual display (called on UI thread)."""
        if not self.running:
            return

        rms = self.current_rms
        canvas_w = WINDOW_SIZE - 40

        # Update RMS label
        self.rms_label.config(text=f"RMS: {rms}  |  Peak: {self.peak_rms}")

        # Update status
        if self.mic_error:
            pass  # already set
        elif self.is_recording:
            self.status_label.config(text="VOICE DETECTED", fg="#44ff44")
        else:
            self.status_label.config(text="LISTENING", fg="#4a9eff")

        # Draw level meter
        self._draw_level_meter(canvas_w, rms)

        # Draw waveform
        self._draw_waveform(canvas_w)

        self.root.after(UPDATE_MS, self._update_display)

    def _draw_level_meter(self, canvas_w, rms):
        """Draw the horizontal level meter bar with threshold marker."""
        self.bar_canvas.delete("all")

        # Scale: use 2000 as the visual max (clamp above that)
        max_display = 2000
        bar_w = canvas_w - 4
        bar_h = BAR_HEIGHT - 4

        # Background segments for reference
        segment_w = bar_w / 20
        for i in range(20):
            x = 2 + i * segment_w
            shade = "#111122" if i % 2 == 0 else "#0d0d1a"
            self.bar_canvas.create_rectangle(x, 2, x + segment_w, bar_h + 2, fill=shade, outline="")

        # Current level fill
        level_frac = min(rms / max_display, 1.0)
        level_w = level_frac * bar_w

        if rms > VOICE_THRESHOLD:
            color = "#44ff44"  # green when above threshold
        elif rms > VOICE_THRESHOLD * 0.5:
            color = "#ffaa00"  # orange when getting close
        else:
            color = "#4a9eff"  # blue for low level

        if level_w > 0:
            self.bar_canvas.create_rectangle(2, 2, 2 + level_w, bar_h + 2, fill=color, outline="")

        # Peak marker
        peak_frac = min(self.peak_rms / max_display, 1.0)
        peak_x = 2 + peak_frac * bar_w
        self.bar_canvas.create_line(peak_x, 2, peak_x, bar_h + 2, fill="#ffffff", width=2)

        # Threshold marker
        thresh_frac = min(VOICE_THRESHOLD / max_display, 1.0)
        thresh_x = 2 + thresh_frac * bar_w
        self.bar_canvas.create_line(thresh_x, 2, thresh_x, bar_h + 2, fill="#ff4444", width=2, dash=(4, 4))

        # Threshold label
        self.bar_canvas.create_text(
            thresh_x, bar_h + 2, text="T", anchor="s",
            fill="#ff4444", font=("Consolas", 8)
        )

    def _draw_waveform(self, canvas_w):
        """Draw the audio waveform."""
        self.wave_canvas.delete("all")

        h = WAVEFORM_HEIGHT
        mid_y = h // 2

        # Center line
        self.wave_canvas.create_line(0, mid_y, canvas_w, mid_y, fill="#222244", width=1)

        # Threshold envelope lines
        max_amplitude = 32768
        if max_amplitude > 0:
            thresh_visual = (VOICE_THRESHOLD / max_amplitude) * mid_y * 4
            thresh_visual = min(thresh_visual, mid_y - 2)
            self.wave_canvas.create_line(
                0, mid_y - thresh_visual, canvas_w, mid_y - thresh_visual,
                fill="#ff4444", width=1, dash=(2, 4)
            )
            self.wave_canvas.create_line(
                0, mid_y + thresh_visual, canvas_w, mid_y + thresh_visual,
                fill="#ff4444", width=1, dash=(2, 4)
            )

        data = list(self.waveform_data)
        if len(data) < 2:
            return

        # Build polyline points
        points = []
        x_step = canvas_w / (len(data) - 1)
        for i, sample in enumerate(data):
            x = i * x_step
            # Normalize sample to canvas height
            y = mid_y - (sample / max_amplitude) * mid_y * 0.9
            y = max(2, min(h - 2, y))
            points.extend([x, y])

        # Draw waveform line
        color = "#44ff44" if self.is_recording else "#4a9eff"
        if len(points) >= 4:
            self.wave_canvas.create_line(points, fill=color, width=1.5, smooth=True)

    def _on_close(self):
        """Clean shutdown."""
        self.running = False
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            self.pa.terminate()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    monitor = AudioMonitor()
    monitor.run()
