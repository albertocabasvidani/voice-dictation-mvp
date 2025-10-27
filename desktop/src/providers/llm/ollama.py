import requests
import logging
from .base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""

    def __init__(self, model: str, ollama_url: str = "http://localhost:11434", **kwargs):
        super().__init__(api_key=None, model=model, **kwargs)
        self.ollama_url = ollama_url.rstrip('/')

    def process(self, text: str) -> str:
        """Process text using Ollama local LLM"""

        url = f"{self.ollama_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            "stream": False,
            "options": {
                "temperature": self.config.get("temperature", 0.3),
                "num_predict": self.config.get("max_tokens", 500)
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            result = response.json()
            llm_output = result.get("message", {}).get("content", "").strip()

            # Validate output
            is_valid, reason = self.validate_output(text, llm_output)
            if not is_valid:
                logger.error(f"LLM output validation failed: {reason}. Using fallback formatting.")
                # Fallback: simple capitalization and period
                fallback = text.strip()
                if fallback and fallback[0].islower():
                    fallback = fallback[0].upper() + fallback[1:]
                if fallback and not fallback.endswith(('.', '!', '?')):
                    fallback += '.'
                return fallback

            return llm_output

        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama - is it running?")
        except requests.exceptions.Timeout:
            raise Exception("Ollama timeout - model may be too slow")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception(f"Model '{self.model}' not found - run: ollama pull {self.model}")
            else:
                raise Exception(f"Ollama API error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Ollama processing failed: {str(e)}")
