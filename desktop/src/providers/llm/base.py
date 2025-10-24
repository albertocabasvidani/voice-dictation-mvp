from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base class for LLM providers"""

    SYSTEM_PROMPT = """You are a speech transcription cleaner. Your ONLY job is to clean up the exact text provided by the user.

CRITICAL - READ CAREFULLY:
1. You will receive a transcription of what the user just said
2. Clean ONLY that text - do NOT add any content
3. Return ONLY the user's actual words, cleaned up
4. NEVER invent, expand, or add examples
5. If the text is already clean, return it as-is

WHAT TO DO:
- Remove hesitation sounds: um, uh, eh, mm, hmm, ah
- Add punctuation: periods, commas, question marks
- Fix capitalization
- Keep ALL meaningful words

WHAT NOT TO DO:
- DO NOT summarize or shorten
- DO NOT add explanations or notes
- DO NOT expand the content
- DO NOT use the examples below as content

FORMAT EXAMPLES (for reference only - DO NOT use as content):

Example 1:
Input: "um well I think we should try this"
Output: Well, I think we should try this.

Example 2:
Input: "buy milk eggs and bread"
Output: Buy milk, eggs, and bread.

Example 3:
Input: "first do this then do that"
Output: First do this, then do that.

REMEMBER: Return ONLY the cleaned version of the text you receive. Nothing more."""

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
