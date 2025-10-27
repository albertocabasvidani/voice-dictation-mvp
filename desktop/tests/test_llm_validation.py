"""Test LLM output validation system"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.providers.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing validation"""

    def process(self, text: str) -> str:
        """Not implemented - we only test validation"""
        pass


def test_valid_formatting():
    """Test that valid formatting passes validation"""
    provider = MockLLMProvider()

    # Valid: simple punctuation added
    input_text = "come si fa questo"
    output_text = "Come si fa questo?"
    is_valid, reason = provider.validate_output(input_text, output_text)
    assert is_valid, f"Should be valid but got: {reason}"

    # Valid: filler words removed
    input_text = "um penso che dovremmo provare"
    output_text = "Penso che dovremmo provare."
    is_valid, reason = provider.validate_output(input_text, output_text)
    assert is_valid, f"Should be valid but got: {reason}"


def test_invalid_length():
    """Test that output much longer than input fails validation"""
    provider = MockLLMProvider()

    input_text = "come si configura git"
    output_text = "Per configurare git, devi prima installare git sul tuo sistema. Ecco i passi da seguire: 1) Scarica..."
    is_valid, reason = provider.validate_output(input_text, output_text)
    assert not is_valid, "Should fail validation (too long)"
    assert "too long" in reason.lower()


def test_invalid_assistant_phrases():
    """Test that assistant-like phrases fail validation"""
    provider = MockLLMProvider()

    # Italian assistant phrases
    test_cases = [
        ("come faccio", "Ecco come fare: prima..."),
        ("cosa devo fare", "Devi seguire questi passi..."),
        ("come posso", "Puoi provare a..."),
    ]

    for input_text, output_text in test_cases:
        is_valid, reason = provider.validate_output(input_text, output_text)
        assert not is_valid, f"Should fail for: {output_text}"
        assert "assistant phrase" in reason.lower()


def test_invalid_markdown():
    """Test that markdown formatting fails validation"""
    provider = MockLLMProvider()

    input_text = "come si usa git per fare commit"

    # Test list formatting (same length but with markdown)
    output_text = "Come si usa git:\n- commit"
    is_valid, reason = provider.validate_output(input_text, output_text)
    assert not is_valid, "Should fail validation (markdown list)"
    assert "markdown" in reason.lower()

    # Test code blocks
    output_text = "Usa git: ```commit```"
    is_valid, reason = provider.validate_output(input_text, output_text)
    assert not is_valid, "Should fail validation (code block)"
    assert "markdown" in reason.lower()


def test_filler_words_normalization():
    """Test that filler words are normalized for fair length comparison"""
    provider = MockLLMProvider()

    # Input has many filler words, but output should still be valid
    input_text = "um uh eh bisogna mm trovare ah il modo"
    output_text = "Bisogna trovare il modo."
    is_valid, reason = provider.validate_output(input_text, output_text)
    assert is_valid, f"Should be valid (filler words normalized) but got: {reason}"


if __name__ == "__main__":
    print("Running LLM validation tests...")

    try:
        test_valid_formatting()
        print("✓ Valid formatting test passed")

        test_invalid_length()
        print("✓ Invalid length test passed")

        test_invalid_assistant_phrases()
        print("✓ Invalid assistant phrases test passed")

        test_invalid_markdown()
        print("✓ Invalid markdown test passed")

        test_filler_words_normalization()
        print("✓ Filler words normalization test passed")

        print("\n✅ All tests passed!")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
