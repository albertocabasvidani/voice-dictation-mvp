import pytest
from src.providers.transcription import GroqWhisperProvider, OpenAIWhisperProvider
from src.providers.llm import OllamaProvider, OpenAILLMProvider


def test_groq_whisper_init():
    """Test Groq Whisper provider initialization"""
    provider = GroqWhisperProvider(api_key="test_key")
    assert provider.api_key == "test_key"
    assert provider.MODEL == "whisper-large-v3"


def test_openai_whisper_init():
    """Test OpenAI Whisper provider initialization"""
    provider = OpenAIWhisperProvider(api_key="test_key")
    assert provider.api_key == "test_key"
    assert provider.MODEL == "whisper-1"


def test_ollama_init():
    """Test Ollama provider initialization"""
    provider = OllamaProvider(model="llama3.2:3b", ollama_url="http://localhost:11434")
    assert provider.model == "llama3.2:3b"
    assert provider.ollama_url == "http://localhost:11434"


def test_openai_llm_init():
    """Test OpenAI LLM provider initialization"""
    provider = OpenAILLMProvider(api_key="test_key", model="gpt-4o-mini")
    assert provider.api_key == "test_key"
    assert provider.model == "gpt-4o-mini"


def test_llm_system_prompt():
    """Test that all LLM providers have the same system prompt"""
    from src.providers.llm import LLMProvider

    assert "filler words" in LLMProvider.SYSTEM_PROMPT
    assert "punctuation" in LLMProvider.SYSTEM_PROMPT
    assert "capitalization" in LLMProvider.SYSTEM_PROMPT
