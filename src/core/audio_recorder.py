import sounddevice as sd
import numpy as np
import io
import struct
import queue
import time


class AudioRecorder:
    """Records audio from microphone"""

    def __init__(self, sample_rate: int = 16000, device_index: int = -1, max_gain: float = 1.0):
        self.sample_rate = sample_rate
        self.device_index = device_index if device_index >= 0 else None
        self.volume_multiplier = max_gain  # Direct volume multiplier (1.0 = no change)
        self.recording = []
        self.is_recording = False
        self.stream = None
        self.audio_queue = queue.Queue()
        self.last_audio_time = None  # Track last time audio was detected
        self.silence_threshold = 300  # Below this level is considered silence

        # Log ALL devices and select best one
        try:
            devices = sd.query_devices()
            print("\n=== Available Audio Devices ===")
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    default_marker = " [DEFAULT]" if i == sd.default.device[0] else ""
                    print(f"  {i}: {device['name']} (in:{device['max_input_channels']}, out:{device['max_output_channels']}){default_marker}")

            if self.device_index is None:
                default_device = sd.default.device[0]
                device_info = devices[default_device]
                print(f"\n>>> Using DEFAULT device: {device_info['name']} (index: {default_device})")
            else:
                device_info = devices[self.device_index]
                print(f"\n>>> Using device: {device_info['name']} (index: {self.device_index})")

            print("=== End of Audio Devices ===\n")
        except Exception as e:
            print(f"Warning: Could not get device info: {e}")

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for continuous audio stream"""
        if status:
            print(f"Audio callback status: {status}")

        # Put audio data in queue (copy to avoid issues)
        self.audio_queue.put(indata.copy())

        # Check if audio or silence
        audio_level = np.abs(indata).mean()
        if audio_level > self.silence_threshold:
            self.last_audio_time = time.time()

    def start_recording(self):
        """Start recording audio"""
        self.recording = []
        self.is_recording = True
        self.last_audio_time = time.time()  # Initialize with current time

        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        # Start continuous stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            device=self.device_index,
            callback=self._audio_callback,
            blocksize=1600  # ~0.1 seconds at 16000 Hz
        )
        self.stream.start()
        print("Audio stream started")

    def get_silence_duration(self) -> float:
        """Get seconds since last audio detected"""
        if self.last_audio_time is None:
            return 0.0
        return time.time() - self.last_audio_time

    def stop_recording(self) -> bytes:
        """Stop recording and return audio data as WAV bytes"""
        self.is_recording = False

        # Stop stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("Audio stream stopped")

        # Collect any remaining data from queue
        while not self.audio_queue.empty():
            try:
                chunk = self.audio_queue.get_nowait()
                self.recording.append(chunk)
            except queue.Empty:
                break

        if not self.recording:
            raise Exception("No audio recorded")

        # Convert list of chunks to single array
        audio_data = np.concatenate(self.recording, axis=0)

        # Log audio info
        duration = len(audio_data) / self.sample_rate
        avg_level = np.abs(audio_data).mean()
        max_level = np.abs(audio_data).max()
        print(f"Audio recorded: {duration:.2f}s ({len(audio_data)} samples at {self.sample_rate}Hz)")
        print(f"Audio levels BEFORE gain - Average: {avg_level:.1f}, Peak: {max_level:.1f} (max: 32767)")

        # Apply volume multiplier from settings (if != 1.0)
        if self.volume_multiplier != 1.0:
            print(f"Applying volume multiplier: {self.volume_multiplier}x")
            audio_data = np.clip(audio_data * self.volume_multiplier, -32767, 32767).astype(np.int16)
            new_avg = np.abs(audio_data).mean()
            new_peak = np.abs(audio_data).max()
            print(f"Audio levels AFTER gain - Average: {new_avg:.1f}, Peak: {new_peak:.1f}")

            # Warning if audio is clipping
            if new_peak >= 32767:
                print("WARNING: Audio is clipping! Reduce volume multiplier in settings.")

        # Warning if signal is very low even after amplification
        final_avg = np.abs(audio_data).mean()
        if final_avg < 500:
            print(f"WARNING: Audio level very low ({final_avg:.1f}) - increase volume multiplier in settings")

        # Convert to WAV bytes
        wav_bytes = self._to_wav_bytes(audio_data)
        print(f"WAV file size: {len(wav_bytes)} bytes")
        return wav_bytes

    def record_chunk(self, duration: float = 0.1):
        """Collect audio chunks from queue (called repeatedly during recording)"""
        if not self.is_recording:
            return

        try:
            # Collect all available chunks from queue
            collected_any = False
            while not self.audio_queue.empty():
                try:
                    chunk = self.audio_queue.get_nowait()
                    self.recording.append(chunk)
                    collected_any = True
                except queue.Empty:
                    break

            # Log audio level periodically
            if collected_any and len(self.recording) % 10 == 0:
                last_chunk = self.recording[-1]
                volume = np.abs(last_chunk).mean()
                print(f"Audio level: {volume:.1f} (chunks: {len(self.recording)})")

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
