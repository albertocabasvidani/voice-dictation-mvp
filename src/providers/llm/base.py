from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base class for LLM providers"""

    SYSTEM_PROMPT = """You are a text formatter. Clean up speech transcriptions by:
- Removing filler words (um, uh, eh, allora, cioè, tipo)
- Adding proper punctuation (periods, commas, question marks)
- Fixing capitalization
- Resolving self-corrections (e.g., "tomorrow, no Friday" → "Friday")
- Preserving the original meaning and tone
Output ONLY the cleaned text, nothing else. No explanations."""

    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs

    @abstractmethod
    def process(self, text: str) -> str:
        """
        Process transcribed text with LLM

        Args:
            text: Raw transcription text

        Returns:
            Cleaned and formatted text

        Raises:
            Exception: If processing fails
        """
        pass
