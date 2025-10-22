import requests
from .base import TranscriptionProvider


class OpenAIWhisperProvider(TranscriptionProvider):
    """OpenAI Whisper transcription provider"""

    API_URL = "https://api.openai.com/v1/audio/transcriptions"
    MODEL = "whisper-1"

    def transcribe(self, audio_data: bytes, language: str = "auto") -> str:
        """Transcribe audio using OpenAI Whisper API"""

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        files = {
            "file": ("audio.wav", audio_data, "audio/wav")
        }

        data = {
            "model": self.MODEL,
        }

        if language != "auto":
            data["language"] = language

        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")

        except requests.exceptions.Timeout:
            raise Exception("OpenAI API timeout - try again")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid OpenAI API key")
            elif e.response.status_code == 429:
                raise Exception("OpenAI rate limit exceeded")
            else:
                raise Exception(f"OpenAI API error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"OpenAI transcription failed: {str(e)}")
