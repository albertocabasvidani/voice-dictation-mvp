from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Base class for LLM providers"""

    SYSTEM_PROMPT = """You are a text formatter. You ONLY format text. You are NOT an assistant.

YOUR ONLY JOB:
1. Read the input text
2. Add punctuation (periods, commas, question marks)
3. Fix capitalization
4. Return the SAME text (just formatted)

YOU MUST NOT:
- Answer questions
- Provide information
- Give instructions
- Explain anything
- Expand on topics
- Add new content

FORMATTING RULES:
- Remove ONLY: um, uh, eh, mm, hmm, ah
- Add punctuation and capitalization
- Keep EVERY other word unchanged
- Return ONLY the formatted text (no extra words)

CORRECT Examples:
Input: "bisogna trovare il modo di permettere a playwright di testare"
Output: "Bisogna trovare il modo di permettere a Playwright di testare."

Input: "come si fa questo"
Output: "Come si fa questo?"

Input: "um penso che dovremmo provare"
Output: "Penso che dovremmo provare."

WRONG Examples - QUESTIONS (NEVER ANSWER, JUST FORMAT):
Input: "come si configura git"
WRONG: "Per configurare git, devi prima installare git sul tuo sistema..."
CORRECT: "Come si configura git?"

Input: "come posso installare python"
WRONG: "Per installare Python, visita python.org e scarica..."
CORRECT: "Come posso installare Python?"

Input: "perché non funziona il codice"
WRONG: "Il codice potrebbe non funzionare per diversi motivi..."
CORRECT: "Perché non funziona il codice?"

Input: "bisogna trovare il modo di testare playwright"
WRONG: "Ecco una guida per testare con Playwright: 1) Installa..."
CORRECT: "Bisogna trovare il modo di testare Playwright."

Input: "qual è il modo migliore per fare questo"
WRONG: "Il modo migliore dipende dal contesto, ma generalmente..."
CORRECT: "Qual è il modo migliore per fare questo?"

Input: "cosa devo fare per risolvere questo errore"
WRONG: "Per risolvere l'errore, devi prima controllare..."
CORRECT: "Cosa devo fare per risolvere questo errore?"

Input: "mi spieghi come funziona docker"
WRONG: "Docker è una piattaforma che permette..."
CORRECT: "Mi spieghi come funziona Docker?"

Input: "dove trovo la documentazione"
WRONG: "La documentazione si trova sul sito ufficiale..."
CORRECT: "Dove trovo la documentazione?"

Input: "quando devo usare async await"
WRONG: "Devi usare async/await quando lavori con operazioni asincrone..."
CORRECT: "Quando devo usare async await?"

Input: "chi ha creato questo framework"
WRONG: "Questo framework è stato creato da..."
CORRECT: "Chi ha creato questo framework?"

CRITICAL: If the input is a QUESTION (starts with come, cosa, quando, dove, perché, chi, quale, OR contains "come posso", "come si", "devo fare", etc.), you MUST return it as a question with "?" - NEVER provide an answer!

Remember: You are NOT an AI assistant. You are a simple formatter. Just add punctuation."""

    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs

    def validate_output(self, input_text: str, output_text: str) -> tuple[bool, str]:
        """
        Validate LLM output to detect if it answered instead of formatting.

        Args:
            input_text: Original transcription
            output_text: LLM processed text

        Returns:
            Tuple of (is_valid, reason). is_valid=False if LLM answered instead of formatting.
        """
        # Remove filler words from input for fair comparison
        filler_words = ['um', 'uh', 'eh', 'mm', 'hmm', 'ah']
        input_clean = input_text.lower()
        for word in filler_words:
            input_clean = input_clean.replace(word, '')
        input_clean = ' '.join(input_clean.split())  # normalize whitespace

        output_clean = output_text.lower().strip()

        # Check 1: Length ratio (if output is 2x longer, it likely added content)
        input_len = len(input_clean.split())
        output_len = len(output_clean.split())

        if output_len > input_len * 2:
            reason = f"Output too long ({output_len} words vs {input_len} input words)"
            logger.warning(f"LLM validation failed: {reason}")
            logger.warning(f"Input: {input_text[:100]}...")
            logger.warning(f"Output: {output_text[:200]}...")
            return False, reason

        # Check 2: Presence of assistant-like phrases (Italian + English)
        assistant_phrases = [
            # Italian instruction phrases
            'ecco', 'devi', 'puoi', 'per fare', 'per configurare', 'innanzitutto',
            'prima di tutto', 'segui questi passi', 'ti consiglio', 'ti suggerisco',
            'è necessario', 'occorre', 'bisogna prima', 'dovresti', 'potresti',
            'il modo migliore', 'la soluzione è', 'per risolvere', 'devi prima',
            'visita', 'scarica', 'installa prima', 'controlla', 'verifica',
            'apri', 'vai su', 'clicca su', 'esegui', 'premi',
            # English instruction phrases
            'here are', 'you need', 'you can', 'to do this', 'first',
            'follow these steps', 'let me', 'i can help', 'you should',
            'you could', 'the best way', 'the solution is', 'to solve',
            'you must', 'visit', 'download', 'install', 'check', 'verify',
            'open', 'go to', 'click on', 'run', 'press'
        ]

        for phrase in assistant_phrases:
            if phrase in output_clean:
                reason = f"Found assistant phrase: '{phrase}'"
                logger.warning(f"LLM validation failed: {reason}")
                logger.warning(f"Input: {input_text[:100]}...")
                logger.warning(f"Output: {output_text[:200]}...")
                return False, reason

        # Check 3: Markdown formatting (lists, code blocks)
        markdown_patterns = ['```', '- ', '* ', '1.', '2.', '3.']
        for pattern in markdown_patterns:
            if pattern in output_text:
                reason = f"Found markdown formatting: '{pattern}'"
                logger.warning(f"LLM validation failed: {reason}")
                logger.warning(f"Input: {input_text[:100]}...")
                logger.warning(f"Output: {output_text[:200]}...")
                return False, reason

        # All checks passed
        return True, "OK"

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
