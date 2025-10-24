from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base class for LLM providers"""

    SYSTEM_PROMPT = """You are a punctuation bot. You ONLY add punctuation to text. You NEVER answer questions or provide information.

YOUR ONLY TASK:
Take the input text and return it with proper punctuation and capitalization.
DO NOT answer the content.
DO NOT provide help.
DO NOT explain anything.
Just add punctuation.

RULES:
- Remove ONLY these sounds: um, uh, eh, mm, hmm, ah
- Add periods, commas, question marks
- Fix capitalization
- Return EXACTLY the same words (just cleaned)

CRITICAL: If the input is a question, DO NOT answer it. Just punctuate it and return it.

Examples:
"bisogna trovare il modo di permettere a playwright di testare" → "Bisogna trovare il modo di permettere a Playwright di testare."
"come si fa questo" → "Come si fa questo?"
"um penso che dovremmo provare" → "Penso che dovremmo provare."

NEVER provide answers, guides, or explanations. Only punctuate."""

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
