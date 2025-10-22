# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Voice Dictation MVP - Clone di Wispr Flow per Windows. App desktop Python che permette dettatura vocale con trascrizione intelligente e auto-formattazione tramite LLM.

**Pipeline**: Audio recording → Cloud transcription API → LLM post-processing → Clipboard/Auto-paste

## Project Structure

```
project-root/
├── config/
│   ├── config.template.json    # Template configurazione
│   └── config.json              # Config utente (gitignored)
├── docs/
│   ├── BUILD.md                 # Istruzioni build/distribuzione
│   ├── README.md                # Documentazione sviluppatore
│   └── README_USER.txt          # Guida utente finale
├── logs/                        # Log applicazione (auto-generati)
├── recordings/                  # File WAV temporanei (max 10)
├── src/
│   ├── core/                    # Logica business principale
│   ├── providers/               # Provider transcription/LLM
│   │   ├── llm/
│   │   └── transcription/
│   └── ui/                      # Interfaccia utente
├── tests/
│   ├── fixtures/                # File audio/text per test
│   └── *.py                     # Unit/integration tests
├── build/                       # Build artifacts (gitignored)
├── dist/                        # Eseguibili produzione (gitignored)
├── CLAUDE.md                    # Guida Claude Code
├── requirements.txt             # Dipendenze Python
├── run_app.py                   # Entry point applicazione
├── build_exe.bat                # Script build automatico
└── VoiceDictation.spec          # Config PyInstaller
```

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
- Gestisce recording con `sounddevice` in continuous stream mode
- Usa `InputStream` con callback e queue per evitare audio stuttering
- **Auto-stop su silenzio**: rileva silenzio (threshold=300) e ferma dopo 60s
- **Silence detection**: traccia `last_audio_time` per monitorare inattività
- Output: buffer audio 16kHz mono, WAV manuale con `struct` (no scipy)
- Volume gain configurabile (0.1x-100x) con auto-calibration

**`src/core/config_manager.py`**
- Carica/salva `config/config.json`
- Encryption/decryption API keys con Windows DPAPI (`win32crypt`)
- Validazione configurazione

**`src/core/hotkey_manager.py`**
- Global hotkey registration con `keyboard` library
- Supporto combinazioni custom (ctrl+shift+key)
- **ESC registrato** per cancellare registrazione in corso
- Parsing configurazione hotkey da JSON

**`src/core/text_processor.py`**
- Orchestrazione: transcription → LLM → clipboard
- Gestione errori e retry logic
- Logging performance (latency tracking)

**`src/ui/system_tray.py`**
- System tray icon con `pystray`
- **Double-click** apre Settings (usando `default=True` in MenuItem)
- Menu: Settings, Exit
- Visual feedback: icon rosso durante recording, verde idle
- **Threading**: esegue in daemon thread per non bloccare tkinter

**`src/ui/settings_window.py`**
- Tkinter window per configurazione (usa `tk.Toplevel` per child windows)
- Tabs: **Hotkey**, **Audio**, **Transcription**, **LLM**, **Advanced**
- **Hotkey tab**: pulsante "Capture" con `pynput` per catturare combinazione tasti
- **Audio tab**:
  - Device selector (solo input devices)
  - Volume gain slider (0.1x-100x, log scale)
  - **Test Microphone (5s)**: registra 5s, analizza livelli, suggerisce gain ottimale
- Test buttons per validare API keys (Transcription, LLM)
- Auto-detect Ollama models (`subprocess` → `ollama list`)
- Save/Cancel buttons con `height=2` per usabilità

**`src/ui/recording_widget.py`**
- Tkinter window on-top in angolo alto-destro
- Stati: Recording (animazione cerchio rosso) → Transcribing → Processing
- Metodo `update_status(title, status, stop_animation)` per aggiornare fase
- Bordo bianco (`highlightthickness=2`) per visibilità su sfondo scuro
- Si nasconde automaticamente al completamento o su errore

**`src/main.py`**
- **Threading architecture**:
  - Main thread: tkinter event loop (hidden root window)
  - Daemon thread: pystray system tray
  - Background threads: recording loop, audio processing
- **Recording flow**:
  1. Hotkey press → `_start_recording()` → mostra widget
  2. Loop `_record_loop()` con silence check (60s timeout)
  3. ESC → `_cancel_recording()` (scarta audio)
  4. Stop → `_stop_recording()` → `_process_audio()` con status updates
- **WAV cleanup**: mantiene ultimi 10 file in `recordings/` folder

### Configuration System

**File**: `config/config.json` (creato da `config.template.json`)

```json
{
  "hotkey": {
    "modifiers": ["ctrl", "shift"],
    "key": "space"
  },
  "transcription": {
    "provider": "groq|openai|deepgram",
    "api_key_encrypted": "BASE64_DPAPI_ENCRYPTED"
  },
  "llm": {
    "provider": "ollama|openai|groq",
    "model": "llama3.2:3b|gpt-4o-mini|llama-3.1-8b-instant",
    "api_key_encrypted": "BASE64_DPAPI_ENCRYPTED",
    "ollama_url": "http://localhost:11434"
  },
  "audio": {
    "device_index": -1,
    "sample_rate": 16000,
    "volume_gain": 1.0
  }
}
```

**IMPORTANTE**: API keys sono cifrate con Windows DPAPI - non possono essere decriptate su altro PC/utente Windows.

### LLM Post-Processing Prompt

Sistema prompt per tutti i provider LLM (in `src/providers/llm/base.py` - `LLMProvider.SYSTEM_PROMPT`):

```python
SYSTEM_PROMPT = """You are a text formatter. Clean up speech transcriptions by:

BASIC FORMATTING:
- Removing filler words (um, uh, eh, allora, cioè, tipo)
- Adding proper punctuation (periods, commas, question marks)
- Fixing capitalization
- Resolving self-corrections (e.g., "tomorrow, no Friday" → "Friday")

STRUCTURE RECOGNITION (only when obvious):
- **Lists**: When the user says phrases like "first", "second", "next", "also", "another", "punto uno", "punto due", or lists items, format as:
  • Bullet points for unordered items
  • Numbered list (1., 2., 3.) for sequential items
- **Paragraphs**: Add line breaks between distinct topics or logical sections
- **Code**: When the user mentions code, programming, or uses technical terms like "function", "class", "variable", format it in backticks or code blocks
- **Titles/Headings**: When the user explicitly says "title", "heading", "titolo", or emphasizes a section name, put it in quotes

EXAMPLES:
Input: "first point is the API then second the database and third the frontend"
Output: 1. API
2. Database
3. Frontend

Input: "reminder buy milk eggs and bread"
Output: Reminder:
• Buy milk
• Eggs
• Bread

Input: "ho fatto un test e funziona"
Output: Ho fatto un test e funziona.

CRITICAL: Return ONLY the user's words, cleaned and formatted. NEVER add notes, explanations, comments, or meta-text like "Nota:" or "Note:". If there's nothing to format structurally, just clean the text. DO NOT add any text that the user did not say."""
```

Questo prompt è **critico** per la qualità output:
- **Basic formatting** sempre applicato (rimozione filler, punteggiatura, capitalizzazione)
- **Structure recognition** solo quando ovvio (liste, codice, titoli)
- **CRITICAL rule**: LLM NON deve mai aggiungere note/spiegazioni proprie
- Modifiche devono preservare queste istruzioni o la qualità decade

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
- Mode: **onedir** (folder con exe + DLLs separate)
- Output: `dist/VoiceDictation/` (77MB totale)
  - `VoiceDictation.exe` (9.5MB) - bootloader
  - `_internal/` - librerie Python, DLLs, config
- Dipendenze: sounddevice, keyboard, pystray, pynput, pyautogui, numpy, PIL, tkinter, win32crypt
- **scipy rimossa**: sostituita con WAV writing manuale in `audio_recorder.py` usando `struct`
- Build time: ~90-100 secondi
- Distribuzione: zippare intera folder `VoiceDictation/`

## Recent Features (v1.1)

### 1. Calibrazione Microfono Automatica
**File**: `src/ui/settings_window.py` (linee 89-162, 239-295)
- Pulsante "Test Microphone (5s)" nella tab Audio
- Registra 5 secondi di audio, analizza livelli (avg/peak)
- Calcola gain suggerito basato su target_avg=2000
- Applica automaticamente al slider volume gain
- Threading per non bloccare UI durante test

### 2. Auto-Stop su Silenzio
**File**: `src/core/audio_recorder.py` (linee 44-86), `src/main.py` (linee 156-181)
- Silenzio rilevato con `threshold=300` (audio_level < 300)
- Traccia `last_audio_time` aggiornato in audio callback
- Loop registrazione controlla ogni 0.1s con `get_silence_duration()`
- Se silenzio > 60s → auto-stop e processa audio
- Previene registrazioni infinite se utente dimentica di stoppare

### 3. Personalizzazione Hotkey con Cattura
**File**: `src/ui/settings_window.py` (linee 164-250)
- Pulsante "Capture" nella tab Hotkey
- Usa `pynput.keyboard.Listener` per catturare combinazione tasti
- Rileva modifiers (ctrl, shift, alt, win) e key premuta
- Aggiorna entry con formato "ctrl+shift+key"
- Threading per non bloccare UI durante cattura

### 4. Formattazione Automatica Avanzata
**File**: `src/providers/llm/base.py` (linee 7-46)
- Prompt LLM potenziato con structure recognition
- Riconosce liste (bullet/numbered) quando utente dice "first", "second", etc.
- Identifica paragrafi (line breaks tra topic diversi)
- Formatta codice con backticks quando menziona "function", "class", etc.
- Titoli tra virgolette quando utente dice "title", "titolo"
- **CRITICAL rule**: LLM non deve mai aggiungere note proprie

**Altri Fix v1.1**:
- Sistema threading: tkinter main thread, pystray daemon thread (fix RuntimeError)
- Recording widget persiste durante transcription/processing con status updates
- Continuous audio stream con queue (fix stuttering)
- WAV file cleanup: mantiene ultimi 10 recordings
- Save/Cancel buttons con `height=2` per usabilità

### 5. Riorganizzazione Struttura Progetto (v1.2)
**File eliminati** (utility temporanee):
- `output.log`, `test_output.log` - log vuoti
- `conversazione esportata.txt` - file sviluppo
- `list_audio_devices.py`, `test_openai_debug.py`, `test_all_providers.py` - script debug temporanei
- `config.json.bak` - backup temporaneo
- `run_debug.bat` - script debug

**Nuova organizzazione cartelle**:
- `config/` - configurazione centralizzata (`config.json` spostato da root)
- `docs/` - tutta la documentazione (BUILD.md, README.md, README_USER.txt)
- `tests/fixtures/` - file audio e trascrizioni test (wav/txt)
- `logs/` - creata esplicitamente per log runtime
- `recordings/` - creata esplicitamente per WAV temporanei

**Compatibilità**: `src/core/config_manager.py` già supporta la ricerca di config.json in `config/` (linea 68)

## Testing Strategy

**Unit tests** per ogni provider:
- Mock API responses (use `pytest-mock`)
- Test error handling (timeout, 401, 500)
- Validate audio format conversions

**Integration tests** per pipeline completa:
- File audio test: `tests/fixtures/esempio_inglese.wav`, `tests/fixtures/esempio_italiano.wav`
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
