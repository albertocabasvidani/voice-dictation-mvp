import requests
import logging
from .base import LLMProvider

logger = logging.getLogger(__name__)


class GroqLLMProvider(LLMProvider):
    """Groq LLM provider"""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def process(self, text: str) -> str:
        """Process text using Groq API"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model or "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            "temperature": self.config.get("temperature", 0.3),
            "max_tokens": self.config.get("max_tokens", 500)
        }

        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            llm_output = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

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

        except requests.exceptions.Timeout:
            raise Exception("Groq API timeout - try again")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid Groq API key")
            elif e.response.status_code == 429:
                raise Exception("Groq rate limit exceeded")
            else:
                raise Exception(f"Groq API error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Groq LLM processing failed: {str(e)}")
