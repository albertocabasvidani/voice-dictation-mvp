import sounddevice as sd
import numpy as np
import io
import struct


class AudioRecorder:
    """Records audio from microphone"""

    def __init__(self, sample_rate: int = 16000, device_index: int = -1):
        self.sample_rate = sample_rate
        self.device_index = device_index if device_index >= 0 else None
        self.recording = []
        self.is_recording = False

        # Log device info
        try:
            devices = sd.query_devices()
            if self.device_index is None:
                default_device = sd.default.device[0]
                device_info = devices[default_device]
                print(f"Audio device: DEFAULT - {device_info['name']} (index: {default_device})")
            else:
                device_info = devices[self.device_index]
                print(f"Audio device: {device_info['name']} (index: {self.device_index})")
        except Exception as e:
            print(f"Warning: Could not get device info: {e}")

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

        # Log audio info
        duration = len(audio_data) / self.sample_rate
        print(f"Audio recorded: {duration:.2f}s ({len(audio_data)} samples at {self.sample_rate}Hz)")

        # Convert to WAV bytes
        wav_bytes = self._to_wav_bytes(audio_data)
        print(f"WAV file size: {len(wav_bytes)} bytes")
        return wav_bytes

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
        """Convert numpy array to WAV file bytes (manual WAV writing, no scipy)"""
        # Create in-memory buffer
        buffer = io.BytesIO()

        # Ensure audio_data is int16
        if audio_data.dtype != np.int16:
            audio_data = audio_data.astype(np.int16)

        # WAV file parameters
        num_channels = 1
        sample_width = 2  # 16-bit = 2 bytes
        num_frames = len(audio_data)

        # Write WAV header (44 bytes)
        buffer.write(b'RIFF')
        buffer.write(struct.pack('<I', 36 + num_frames * num_channels * sample_width))  # File size - 8
        buffer.write(b'WAVE')

        # Write fmt chunk
        buffer.write(b'fmt ')
        buffer.write(struct.pack('<I', 16))  # fmt chunk size
        buffer.write(struct.pack('<H', 1))   # PCM format
        buffer.write(struct.pack('<H', num_channels))
        buffer.write(struct.pack('<I', self.sample_rate))
        buffer.write(struct.pack('<I', self.sample_rate * num_channels * sample_width))  # Byte rate
        buffer.write(struct.pack('<H', num_channels * sample_width))  # Block align
        buffer.write(struct.pack('<H', sample_width * 8))  # Bits per sample

        # Write data chunk
        buffer.write(b'data')
        buffer.write(struct.pack('<I', num_frames * num_channels * sample_width))
        buffer.write(audio_data.tobytes())

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
