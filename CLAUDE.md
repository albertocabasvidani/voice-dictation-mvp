# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Voice Dictation MVP - Clone di Wispr Flow per Windows. App desktop Python che permette dettatura vocale con trascrizione intelligente e auto-formattazione tramite LLM.

**Pipeline**: Audio recording → Cloud transcription API → LLM post-processing → Clipboard/Auto-paste

## Architecture

### Multi-Provider Pattern

Il progetto implementa un'architettura multi-provider per massima flessibilità:

**Transcription Providers** (`src/providers/transcription/`):
- `groq_whisper.py` - Groq Whisper API (gratis, <1s latency)
- `openai_whisper.py` - OpenAI Whisper API ($0.006/min)
- `deepgram.py` - Deepgram Nova-2 ($0.0043/min)

**LLM Providers** (`src/providers/llm/`):
- `ollama.py` - Ollama locale (gratis, privato, richiede installazione)
- `openai_llm.py` - OpenAI GPT models (gpt-4o-mini, gpt-4o)
- `groq_llm.py` - Groq inference (llama-3.1-8b, mixtral, gratis)

Ogni provider implementa interfaccia comune:
- Transcription: `transcribe(audio_data: bytes) -> str`
- LLM: `process(text: str) -> str`

### Core Components

**`src/core/audio_recorder.py`**
- Gestisce recording con `sounddevice`
- Rileva inizio/fine tramite hotkey
- Output: buffer audio 16kHz mono
- **Dipendenza pesante**: usa `scipy.io.wavfile` per scrivere WAV (causa import torch → 2.7GB exe)

**`src/core/config_manager.py`**
- Carica/salva `config/config.json`
- Encryption/decryption API keys con Windows DPAPI (`win32crypt`)
- Validazione configurazione

**`src/core/hotkey_manager.py`**
- Global hotkey registration con `keyboard` library
- Supporto combinazioni custom (ctrl+shift+key)
- Parsing configurazione hotkey da JSON

**`src/core/text_processor.py`**
- Orchestrazione: transcription → LLM → clipboard
- Gestione errori e retry logic
- Logging performance (latency tracking)

**`src/ui/system_tray.py`**
- System tray icon con `pystray`
- Menu: Settings, Start/Stop, Exit
- Visual feedback stato (icon change durante recording)

**`src/ui/settings_window.py`**
- Tkinter window per configurazione
- Tabs: Hotkey, Transcription, LLM, Advanced
- Test buttons per validare API keys
- Auto-detect Ollama models (`subprocess` → `ollama list`)

### Configuration System

**File**: `config/config.json` (creato da `config.template.json`)

```json
{
  "transcription": {
    "provider": "groq|openai|deepgram",
    "api_key_encrypted": "BASE64_DPAPI_ENCRYPTED"
  },
  "llm": {
    "provider": "ollama|openai|groq",
    "model": "llama3.2:3b|gpt-4o-mini|llama-3.1-8b-instant",
    "api_key_encrypted": "BASE64_DPAPI_ENCRYPTED",
    "ollama_url": "http://localhost:11434"
  }
}
```

**IMPORTANTE**: API keys sono cifrate con Windows DPAPI - non possono essere decriptate su altro PC/utente Windows.

### LLM Post-Processing Prompt

Sistema prompt per tutti i provider LLM (in `src/core/text_processor.py`):

```python
SYSTEM_PROMPT = """You are a text formatter. Clean up speech transcriptions by:
- Removing filler words (um, uh, eh, allora, cioè, tipo)
- Adding proper punctuation (periods, commas, question marks)
- Fixing capitalization
- Resolving self-corrections (e.g., "tomorrow, no Friday" → "Friday")
- Preserving the original meaning and tone
Output ONLY the cleaned text, nothing else. No explanations."""
```

Questo prompt è **critico** per la qualità output - modifiche devono mantenere stesse istruzioni.

## Development Commands

### Setup Ambiente
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Run
```bash
python src/main.py
```

### Testing
```bash
# Tutti i test
pytest tests/

# Test specifico provider
pytest tests/providers/test_groq_whisper.py -v

# Test con coverage
pytest --cov=src tests/
```

### Build Eseguibile
```bash
# Metodo 1: Batch file automatico (raccomandato)
build_exe.bat
# Preserva automaticamente config.json, output: dist/VoiceDictation.exe

# Metodo 2: PyInstaller diretto
pyinstaller VoiceDictation.spec
# Output: dist/VoiceDictation.exe
```

**IMPORTANTE BUILD**:
- File spec: `VoiceDictation.spec` - configurazione PyInstaller
- Entry point: `run_app.py` (wrapper per import compatibility)
- Mode: onefile (tutto in un .exe singolo)
- Dipendenze critiche installate: sounddevice, scipy, keyboard, pystray, pynput, pyautogui
- **Problema noto**: scipy+torch creano exe da 2.7GB che non funziona in onefile mode
- **Soluzione in progress**: rimuovere scipy, sostituire con libreria leggera per WAV writing

## Testing Strategy

**Unit tests** per ogni provider:
- Mock API responses (use `pytest-mock`)
- Test error handling (timeout, 401, 500)
- Validate audio format conversions

**Integration tests** per pipeline completa:
- File audio test: `tests/fixtures/sample.wav`
- Verifica latency < 3s (target MVP)

**Manual testing checklist** (in `tests/manual_test_plan.md`):
- Hotkey funziona in diverse app (Chrome, Notepad, VSCode)
- Auto-paste inserisce testo corretto
- Settings window salva/carica config
- Tutti e 3 transcription provider funzionano
- Tutti e 3 LLM provider funzionano

## Common Development Tasks

### Aggiungere Nuovo Provider Trascrizione

1. Crea `src/providers/transcription/new_provider.py`:
```python
from .base import TranscriptionProvider

class NewProvider(TranscriptionProvider):
    def transcribe(self, audio_data: bytes) -> str:
        # Implementazione
        pass
```

2. Aggiungi factory in `src/core/text_processor.py`:
```python
def get_transcription_provider(config):
    if config['provider'] == 'new_provider':
        return NewProvider(config['api_key'])
```

3. Aggiungi opzione in `src/ui/settings_window.py` dropdown

### Aggiungere Nuovo Modello LLM

Modifica `src/ui/settings_window.py`:
```python
LLM_MODELS = {
    'ollama': ['llama3.2:3b', 'nuovo_modello:7b'],
    'openai': ['gpt-4o-mini', 'gpt-4o'],
    'groq': ['llama-3.1-8b-instant', 'nuovo-modello']
}
```

Nessun cambio codice necessario se provider usa stessa API.

### Debug Hotkey Non Funziona

1. Check admin permissions: hotkey globali richiedono privilegi elevati su Windows
2. Verifica conflitti: `keyboard.is_pressed()` in debug mode
3. Log in `src/core/hotkey_manager.py`: uncomment debug prints

### Debug API Errors

Ogni provider logga in `logs/voice_dictation.log`:
```python
logger.error(f"Groq API error: {response.status_code} - {response.text}")
```

Check API key validity: usa Test button in Settings window.

## Performance Targets

- **Latency totale**: < 3s (p95)
  - Transcription: < 2s
  - LLM: < 1s
  - Groq è il più veloce per entrambi

- **RAM usage**: < 150MB idle (escluso Ollama)

- **Ollama locale**: richiede 4-8GB RAM extra, latency 2-5s

## Security Notes

- API keys cifrate con DPAPI - tied to Windows user account
- Nessun audio salvato su disco - solo buffer temporaneo in RAM
- Config file in `%APPDATA%\VoiceDictation\config.json` (user-specific)

## Common Issues

**"Ollama not found"**:
- Verifica Ollama installato: `ollama --version`
- Check service running: `ollama list`
- Verifica URL in config: default `http://localhost:11434`

**"Hotkey not working"**:
- Esegui come admin (richiesto per global hotkey)
- Check conflitti con altre app
- Prova hotkey diversa in Settings

**"Text not pasting"**:
- Fallback automatico: testo sempre copiato in clipboard
- `auto_paste: false` in config disabilita Ctrl+V automatico
- Alcune app bloccano SendInput - usa Ctrl+V manuale
