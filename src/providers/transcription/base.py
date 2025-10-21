from abc import ABC, abstractmethod


class TranscriptionProvider(ABC):
    """Base class for transcription providers"""

    def __init__(self, api_key: str = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def transcribe(self, audio_data: bytes, language: str = "auto") -> str:
        """
        Transcribe audio data to text

        Args:
            audio_data: Audio file bytes (WAV/MP3)
            language: Language code (e.g., 'it', 'en', 'auto')

        Returns:
            Transcribed text

        Raises:
            Exception: If transcription fails
        """
        pass
