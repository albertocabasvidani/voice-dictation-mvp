#!/usr/bin/env python3
"""
Complete test script for all providers (Transcription + LLM)
Tests with both Italian and English audio samples
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from providers.transcription import GroqWhisperProvider, OpenAIWhisperProvider, DeepgramProvider
from providers.llm import OllamaProvider, OpenAILLMProvider, GroqLLMProvider


def load_env_file(filepath: str = '.env'):
    """Load .env file manually"""
    if not os.path.exists(filepath):
        return

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()


def load_audio_file(filepath: str) -> bytes:
    """Load audio file as bytes"""
    with open(filepath, 'rb') as f:
        return f.read()


def load_reference_text(filepath: str) -> str:
    """Load reference transcription"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def test_transcription_provider(provider_name: str, provider, audio_data: bytes, language: str, reference: str):
    """Test a single transcription provider"""
    print(f"\n{'='*60}")
    print(f"Testing {provider_name} - Language: {language}")
    print('='*60)

    try:
        start_time = time.time()
        result = provider.transcribe(audio_data, language=language)
        elapsed = time.time() - start_time

        print(f"✓ Success - Latency: {elapsed:.2f}s")
        print(f"\nTranscription:\n{result}")
        print(f"\nReference:\n{reference}")

        # Simple accuracy check (word count comparison)
        result_words = len(result.split())
        ref_words = len(reference.split())
        print(f"\nWord count: {result_words} (result) vs {ref_words} (reference)")

        return {
            'success': True,
            'result': result,
            'latency': elapsed,
            'word_count': result_words,
            'error': None
        }

    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return {
            'success': False,
            'result': None,
            'latency': 0,
            'word_count': 0,
            'error': str(e)
        }


def test_llm_provider(provider_name: str, provider, raw_text: str):
    """Test a single LLM provider"""
    print(f"\n{'-'*60}")
    print(f"LLM: {provider_name}")
    print('-'*60)

    try:
        start_time = time.time()
        result = provider.process(raw_text)
        elapsed = time.time() - start_time

        print(f"✓ Success - Latency: {elapsed:.2f}s")
        print(f"\nCleaned text:\n{result}")

        return {
            'success': True,
            'result': result,
            'latency': elapsed,
            'error': None
        }

    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return {
            'success': False,
            'result': None,
            'latency': 0,
            'error': str(e)
        }


def main():
    # Load environment variables
    load_env_file()

    groq_key = os.getenv('GROQ_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    deepgram_key = os.getenv('DEEPGRAM_API_KEY')

    print("Voice Dictation MVP - Complete Provider Testing")
    print("="*60)

    # Load audio files
    print("\nLoading audio files...")
    audio_it = load_audio_file('tests/esempio italiano.wav')
    audio_en = load_audio_file('tests/esempio inglese.wav')

    ref_it = load_reference_text('tests/esempio italiano trascrizione.txt')
    ref_en = load_reference_text('tests/esempio inglese trascrizione.txt')

    print(f"✓ Italian audio loaded: {len(audio_it)} bytes")
    print(f"✓ English audio loaded: {len(audio_en)} bytes")

    # Results storage
    results = {
        'italian': {'transcription': {}, 'llm': {}},
        'english': {'transcription': {}, 'llm': {}}
    }

    # ========== TRANSCRIPTION TESTS ==========
    print("\n" + "="*60)
    print("PART 1: TRANSCRIPTION PROVIDERS")
    print("="*60)

    # Italian tests
    print("\n### ITALIAN AUDIO ###")

    if groq_key:
        provider = GroqWhisperProvider(api_key=groq_key)
        results['italian']['transcription']['groq'] = test_transcription_provider(
            'Groq Whisper', provider, audio_it, 'it', ref_it
        )

    if openai_key:
        provider = OpenAIWhisperProvider(api_key=openai_key)
        results['italian']['transcription']['openai'] = test_transcription_provider(
            'OpenAI Whisper', provider, audio_it, 'it', ref_it
        )

    if deepgram_key:
        provider = DeepgramProvider(api_key=deepgram_key)
        results['italian']['transcription']['deepgram'] = test_transcription_provider(
            'Deepgram', provider, audio_it, 'it', ref_it
        )

    # English tests
    print("\n### ENGLISH AUDIO ###")

    if groq_key:
        provider = GroqWhisperProvider(api_key=groq_key)
        results['english']['transcription']['groq'] = test_transcription_provider(
            'Groq Whisper', provider, audio_en, 'en', ref_en
        )

    if openai_key:
        provider = OpenAIWhisperProvider(api_key=openai_key)
        results['english']['transcription']['openai'] = test_transcription_provider(
            'OpenAI Whisper', provider, audio_en, 'en', ref_en
        )

    if deepgram_key:
        provider = DeepgramProvider(api_key=deepgram_key)
        results['english']['transcription']['deepgram'] = test_transcription_provider(
            'Deepgram', provider, audio_en, 'en', ref_en
        )

    # ========== LLM POST-PROCESSING TESTS ==========
    print("\n" + "="*60)
    print("PART 2: LLM POST-PROCESSING")
    print("="*60)

    # Test LLM on best transcription from each language
    for lang in ['italian', 'english']:
        print(f"\n### {lang.upper()} ###")

        # Get first successful transcription as input
        trans_results = results[lang]['transcription']
        raw_text = None
        for provider_name, result in trans_results.items():
            if result and result['success']:
                raw_text = result['result']
                print(f"\nUsing {provider_name} transcription as input for LLM tests")
                break

        if not raw_text:
            print(f"No successful transcription for {lang}, skipping LLM tests")
            continue

        # Test Groq LLM
        if groq_key:
            provider = GroqLLMProvider(api_key=groq_key, model='llama-3.1-8b-instant')
            results[lang]['llm']['groq'] = test_llm_provider('Groq (llama-3.1-8b)', provider, raw_text)

        # Test OpenAI LLM
        if openai_key:
            provider = OpenAILLMProvider(api_key=openai_key, model='gpt-4o-mini')
            results[lang]['llm']['openai'] = test_llm_provider('OpenAI (gpt-4o-mini)', provider, raw_text)

        # Note: Ollama skipped (requires local installation)
        print("\nNote: Ollama test skipped (requires local installation)")

    # ========== GENERATE REPORT ==========
    print("\n" + "="*60)
    print("Generating report...")
    generate_report(results, ref_it, ref_en)
    print("✓ Report saved to: test_results.md")


def generate_report(results, ref_it, ref_en):
    """Generate markdown report with all results"""

    report = """# Voice Dictation MVP - Provider Test Results

## Test Configuration

- **Audio samples**: 2 files (Italian + English)
- **Transcription providers tested**: Groq Whisper, OpenAI Whisper, Deepgram
- **LLM providers tested**: Groq (llama-3.1-8b), OpenAI (gpt-4o-mini)
- **Date**: """ + time.strftime('%Y-%m-%d %H:%M:%S') + """

---

## Part 1: Transcription Results

### Italian Audio

**Reference transcription:**
```
""" + ref_it + """
```

"""

    # Italian transcription results
    for provider, result in results['italian']['transcription'].items():
        if result:
            report += f"""
#### {provider.upper()}
- **Status**: {'✓ Success' if result['success'] else '✗ Failed'}
- **Latency**: {result['latency']:.2f}s
- **Word count**: {result['word_count']}
"""
            if result['success']:
                report += f"""- **Transcription**:
```
{result['result']}
```
"""
            else:
                report += f"- **Error**: {result['error']}\n"

    report += """
### English Audio

**Reference transcription:**
```
""" + ref_en + """
```

"""

    # English transcription results
    for provider, result in results['english']['transcription'].items():
        if result:
            report += f"""
#### {provider.upper()}
- **Status**: {'✓ Success' if result['success'] else '✗ Failed'}
- **Latency**: {result['latency']:.2f}s
- **Word count**: {result['word_count']}
"""
            if result['success']:
                report += f"""- **Transcription**:
```
{result['result']}
```
"""
            else:
                report += f"- **Error**: {result['error']}\n"

    report += """
---

## Part 2: LLM Post-Processing Results

### Italian Text Processing
"""

    # Italian LLM results
    for provider, result in results['italian']['llm'].items():
        if result:
            report += f"""
#### {provider.upper()}
- **Status**: {'✓ Success' if result['success'] else '✗ Failed'}
- **Latency**: {result['latency']:.2f}s
"""
            if result['success']:
                report += f"""- **Cleaned text**:
```
{result['result']}
```
"""
            else:
                report += f"- **Error**: {result['error']}\n"

    report += """
### English Text Processing
"""

    # English LLM results
    for provider, result in results['english']['llm'].items():
        if result:
            report += f"""
#### {provider.upper()}
- **Status**: {'✓ Success' if result['success'] else '✗ Failed'}
- **Latency**: {result['latency']:.2f}s
"""
            if result['success']:
                report += f"""- **Cleaned text**:
```
{result['result']}
```
"""
            else:
                report += f"- **Error**: {result['error']}\n"

    # Performance summary
    report += """
---

## Performance Summary

### Transcription Latency Comparison
"""

    # Transcription latency table
    report += """
| Provider | Italian | English | Average |
|----------|---------|---------|---------|
"""

    for provider in ['groq', 'openai', 'deepgram']:
        it_result = results['italian']['transcription'].get(provider)
        en_result = results['english']['transcription'].get(provider)

        it_latency = f"{it_result['latency']:.2f}s" if it_result and it_result['success'] else "Failed"
        en_latency = f"{en_result['latency']:.2f}s" if en_result and en_result['success'] else "Failed"

        avg = "-"
        if it_result and it_result['success'] and en_result and en_result['success']:
            avg = f"{(it_result['latency'] + en_result['latency']) / 2:.2f}s"

        report += f"| {provider.capitalize()} | {it_latency} | {en_latency} | {avg} |\n"

    report += """
### LLM Processing Latency Comparison
"""

    # LLM latency table
    report += """
| Provider | Italian | English | Average |
|----------|---------|---------|---------|
"""

    for provider in ['groq', 'openai']:
        it_result = results['italian']['llm'].get(provider)
        en_result = results['english']['llm'].get(provider)

        it_latency = f"{it_result['latency']:.2f}s" if it_result and it_result['success'] else "Failed"
        en_latency = f"{en_result['latency']:.2f}s" if en_result and en_result['success'] else "Failed"

        avg = "-"
        if it_result and it_result['success'] and en_result and en_result['success']:
            avg = f"{(it_result['latency'] + en_result['latency']) / 2:.2f}s"

        report += f"| {provider.capitalize()} | {it_latency} | {en_latency} | {avg} |\n"

    report += """
---

## Conclusions

### Transcription Providers
"""

    # Find fastest transcription provider
    fastest_trans = None
    fastest_time = float('inf')

    for lang in ['italian', 'english']:
        for provider, result in results[lang]['transcription'].items():
            if result and result['success'] and result['latency'] < fastest_time:
                fastest_time = result['latency']
                fastest_trans = provider

    if fastest_trans:
        report += f"- **Fastest**: {fastest_trans.capitalize()} (avg {fastest_time:.2f}s)\n"

    report += """
### LLM Providers
"""

    # Find fastest LLM provider
    fastest_llm = None
    fastest_time = float('inf')

    for lang in ['italian', 'english']:
        for provider, result in results[lang]['llm'].items():
            if result and result['success'] and result['latency'] < fastest_time:
                fastest_time = result['latency']
                fastest_llm = provider

    if fastest_llm:
        report += f"- **Fastest**: {fastest_llm.capitalize()} (avg {fastest_time:.2f}s)\n"

    report += """
### Recommendations for MVP

Based on test results:
1. **Transcription**: Use the provider with best latency/accuracy trade-off
2. **LLM**: Use fastest provider that maintains quality
3. **Target total latency**: < 3s for good UX

### Two Files Sufficient for Testing?

**YES** - Two audio samples (different languages) are sufficient for MVP validation because:
- ✓ Tests multilingual capability
- ✓ Tests different provider APIs
- ✓ Validates end-to-end pipeline
- ✓ Provides latency benchmarks
- ✓ Identifies potential issues

For production, recommend:
- More diverse audio samples (accents, noise levels, speech patterns)
- Edge cases (very short/long audio, background noise)
- Stress testing (concurrent requests)
"""

    # Write report
    with open('test_results.md', 'w', encoding='utf-8') as f:
        f.write(report)


if __name__ == '__main__':
    main()
