import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import io


class AudioRecorder:
    """Records audio from microphone"""

    def __init__(self, sample_rate: int = 16000, device_index: int = -1):
        self.sample_rate = sample_rate
        self.device_index = device_index if device_index >= 0 else None
        self.recording = []
        self.is_recording = False

    def start_recording(self):
        """Start recording audio"""
        self.recording = []
        self.is_recording = True

    def stop_recording(self) -> bytes:
        """Stop recording and return audio data as WAV bytes"""
        self.is_recording = False

        if not self.recording:
            raise Exception("No audio recorded")

        # Convert list of chunks to single array
        audio_data = np.concatenate(self.recording, axis=0)

        # Convert to WAV bytes
        return self._to_wav_bytes(audio_data)

    def record_chunk(self, duration: float = 0.1):
        """Record a small chunk of audio (called repeatedly during recording)"""
        if not self.is_recording:
            return

        try:
            chunk = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                device=self.device_index
            )
            sd.wait()
            self.recording.append(chunk)
        except Exception as e:
            raise Exception(f"Audio recording failed: {str(e)}")

    def record_blocking(self, duration: float = 5.0) -> bytes:
        """Record audio for a fixed duration (blocking)"""
        try:
            print(f"Recording for {duration} seconds...")
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                device=self.device_index
            )
            sd.wait()
            print("Recording finished")

            return self._to_wav_bytes(audio_data)

        except Exception as e:
            raise Exception(f"Audio recording failed: {str(e)}")

    def _to_wav_bytes(self, audio_data: np.ndarray) -> bytes:
        """Convert numpy array to WAV file bytes"""
        # Create in-memory buffer
        buffer = io.BytesIO()

        # Write WAV file to buffer
        wavfile.write(buffer, self.sample_rate, audio_data)

        # Get bytes
        buffer.seek(0)
        return buffer.read()

    @staticmethod
    def list_devices():
        """List available audio input devices"""
        return sd.query_devices()

    @staticmethod
    def get_default_device():
        """Get default input device index"""
        return sd.default.device[0]
