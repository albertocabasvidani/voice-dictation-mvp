import requests
from .base import TranscriptionProvider


class DeepgramProvider(TranscriptionProvider):
    """Deepgram transcription provider"""

    API_URL = "https://api.deepgram.com/v1/listen"
    MODEL = "nova-2"

    def transcribe(self, audio_data: bytes, language: str = "auto") -> str:
        """Transcribe audio using Deepgram API"""

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "audio/wav"
        }

        # Build query parameters
        params = {
            "model": self.MODEL,
            "smart_format": "true",
        }

        if language != "auto":
            params["language"] = language

        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            # Extract transcription from Deepgram response
            transcript = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
            return transcript

        except requests.exceptions.Timeout:
            raise Exception("Deepgram API timeout - try again")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid Deepgram API key")
            elif e.response.status_code == 429:
                raise Exception("Deepgram rate limit exceeded")
            else:
                raise Exception(f"Deepgram API error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Deepgram transcription failed: {str(e)}")
