import time
import pyperclip
import pyautogui
from typing import Optional

from src.providers.transcription import (
    TranscriptionProvider,
    GroqWhisperProvider,
    OpenAIWhisperProvider,
    DeepgramProvider
)
from src.providers.llm import (
    LLMProvider,
    OllamaProvider,
    OpenAILLMProvider,
    GroqLLMProvider
)


class TextProcessor:
    """Orchestrates the full pipeline: audio → transcription → LLM → clipboard/paste"""

    def __init__(self, config: dict):
        self.config = config
        self.transcription_provider = self._create_transcription_provider()
        self.llm_provider = self._create_llm_provider()

    def _create_transcription_provider(self) -> TranscriptionProvider:
        """Create transcription provider based on config"""
        trans_config = self.config.get('transcription', {})
        provider_name = trans_config.get('provider', 'groq')
        api_key = self._get_transcription_api_key()

        if provider_name == 'groq':
            return GroqWhisperProvider(api_key=api_key)
        elif provider_name == 'openai':
            return OpenAIWhisperProvider(api_key=api_key)
        elif provider_name == 'deepgram':
            return DeepgramProvider(api_key=api_key)
        else:
            raise ValueError(f"Unknown transcription provider: {provider_name}")

    def _create_llm_provider(self) -> LLMProvider:
        """Create LLM provider based on config"""
        llm_config = self.config.get('llm', {})
        provider_name = llm_config.get('provider', 'ollama')
        model = llm_config.get('model', 'llama3.2:3b')
        api_key = self._get_llm_api_key()

        if provider_name == 'ollama':
            ollama_url = llm_config.get('ollama_url', 'http://localhost:11434')
            return OllamaProvider(
                model=model,
                ollama_url=ollama_url,
                temperature=llm_config.get('temperature', 0.3),
                max_tokens=llm_config.get('max_tokens', 500)
            )
        elif provider_name == 'openai':
            return OpenAILLMProvider(
                api_key=api_key,
                model=model or 'gpt-4o-mini',
                temperature=llm_config.get('temperature', 0.3),
                max_tokens=llm_config.get('max_tokens', 500)
            )
        elif provider_name == 'groq':
            return GroqLLMProvider(
                api_key=api_key,
                model=model or 'llama-3.1-8b-instant',
                temperature=llm_config.get('temperature', 0.3),
                max_tokens=llm_config.get('max_tokens', 500)
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")

    def _get_transcription_api_key(self) -> str:
        """Get transcription API key from config"""
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        config_manager.config = self.config
        return config_manager.get_transcription_api_key()

    def _get_llm_api_key(self) -> str:
        """Get LLM API key from config"""
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        config_manager.config = self.config
        return config_manager.get_llm_api_key()

    def process_audio(self, audio_data: bytes, status_callback: Optional[callable] = None) -> str:
        """
        Process audio through full pipeline

        Args:
            audio_data: Audio file bytes (WAV)
            status_callback: Optional callback for status updates

        Returns:
            Final processed text

        Raises:
            Exception: If any step fails
        """
        start_time = time.time()

        # Step 1: Transcribe
        if status_callback:
            status_callback("Transcribing...")

        trans_start = time.time()
        language = self.config.get('transcription', {}).get('options', {}).get('language', 'auto')
        raw_text = self.transcription_provider.transcribe(audio_data, language=language)
        trans_time = time.time() - trans_start

        if not raw_text.strip():
            raise Exception("No speech detected")

        print(f"Transcription ({trans_time:.2f}s): {raw_text}")

        # Step 2: LLM Post-processing
        if status_callback:
            status_callback("Processing...")

        llm_start = time.time()
        clean_text = self.llm_provider.process(raw_text)
        llm_time = time.time() - llm_start

        print(f"LLM processing ({llm_time:.2f}s): {clean_text}")

        # Step 3: Copy to clipboard
        if status_callback:
            status_callback("Copying...")

        pyperclip.copy(clean_text)

        # Step 4: Auto-paste if enabled
        auto_paste = self.config.get('behavior', {}).get('auto_paste', True)
        if auto_paste:
            if status_callback:
                status_callback("Pasting...")

            time.sleep(0.1)  # Small delay for clipboard to be ready
            try:
                pyautogui.hotkey('ctrl', 'v')
            except:
                pass  # Silently fail if paste doesn't work

        total_time = time.time() - start_time
        print(f"Total processing time: {total_time:.2f}s")

        if status_callback:
            status_callback("Done!")

        return clean_text

    def reload_config(self, config: dict):
        """Reload configuration and recreate providers"""
        self.config = config
        self.transcription_provider = self._create_transcription_provider()
        self.llm_provider = self._create_llm_provider()
