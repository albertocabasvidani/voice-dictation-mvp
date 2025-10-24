# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📑 Table of Contents

### Windows Desktop Implementation
- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
  - [Multi-Provider Pattern](#multi-provider-pattern)
  - [Core Components](#core-components)
  - [Configuration System](#configuration-system)
  - [LLM Post-Processing Prompt](#llm-post-processing-prompt)
- [Development Commands](#development-commands)
- [Recent Features (v1.1)](#recent-features-v11)
- [Testing Strategy](#testing-strategy)
- [Common Development Tasks](#common-development-tasks)
- [Performance Targets](#performance-targets)
- [Security Notes](#security-notes)
- [Common Issues](#common-issues)

### Android Mobile Implementation
- [Android Version (MVP)](#android-version-mvp)
  - [Project Structure Android](#project-structure-android)
  - [Key Differences from Windows](#key-differences-from-windows)
  - [Architecture Android](#architecture-android)
  - [Android MVP Limitations](#android-mvp-limitations)
  - [Development Android](#development-android)
  - [Configuration Android](#configuration-android)
  - [Common Issues Android](#common-issues-android)
  - [Testing Android](#testing-android)
  - [Performance Targets Android](#performance-targets-android)
  - [Documentation Android](#documentation-android)
  - [Future Android Features](#future-android-features)

---

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
```

**Caratteristiche prompt (v1.2.1 - CRITICAL FIX):**
- **Ruolo esplicito**: "punctuation bot" - non un assistente
- **NEVER answer questions**: previene LLM che risponde invece di punteggiare
- **Problema risolto**: Input "bisogna trovare il modo di permettere a Playwright di testare" generava guida completa invece di solo punteggiare
- **Ultra-semplice**: solo punteggiatura e capitalizzazione, rimuove hesitation sounds
- **Esempi problematici inclusi**: "come si fa questo" per insegnare a NON rispondere
- NO formattazione avanzata (liste, code blocks, etc.)

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

## Recent Features (v1.2)

### 1. Real-time Auto-Gain (NEW in v1.2)
**File**: `src/core/audio_recorder.py` (linee 45-60), `src/main.py` (linee 162-213)
- **Gain applicato in tempo reale** nel callback audio, non a fine registrazione
- Dopo 3s: se audio < 300 → calcola gain automatico (max 10x)
- Applica gain immediatamente a `volume_multiplier`
- Widget mostra notifica: "🔊 Auto-gain applied: 1.0x → 5.2x"
- **Salva automaticamente** nuovo gain in config.json per registrazioni future
- Elimina necessità di calibrazione manuale per la maggior parte degli utenti

### 2. Hotkey Capture Fix (v1.2)
**File**: `src/ui/settings_window.py` (linee 113-157)
- **Fix multi-metodo**: key.name → key.char (solo senza modifier) → vk (virtual key code)
- Virtual key code funziona correttamente con ALT e altri modifier
- Previene cattura caratteri sbagliati (es. ctrl-shift-d → '~', ctrl-alt-d → '~~')
- Ora cattura correttamente il tasto fisico indipendentemente dai modificatori

### 3. Hotkey Re-registration Fix (v1.2)
**File**: `src/main.py` (linee 429-433), `src/core/hotkey_manager.py` (linee 32-42)
- **Race condition fix**: delay 200ms tra unregister e register
- Validazione che modifiers sia una lista
- Logging dettagliato di tutte le operazioni hotkey
- Fix: hotkey non funzionava dopo cambio nelle impostazioni

### 4. UI Improvements (v1.2)
**File**: `src/ui/settings_window.py` (linee 32, 45-54)
- Altezza finestra aumentata: 500px → 550px
- Pulsanti Save/Cancel con height=3, font Arial 10, padding aumentato
- Migliore visibilità e usabilità

### 5. Settings After Cancel Fix (v1.2)
**File**: `src/main.py` (linee 221-253, 404-440)
- Settings bloccate dopo cancellazione registrazione: FIXED
- Cleanup completo in `_cancel_recording()` con try-except-finally
- Check `is_recording` prima di aprire settings
- Notifica utente se tenta apertura durante registrazione

### 6. LLM Conservative Prompt (v1.2)
**File**: `src/providers/llm/base.py` (linee 7-58)
- **CRITICAL RULES** aggiunte per preservare tutte le parole
- Fix: LLM rimuoveva parole significative ("niente", "facciamo")
- Ora rimuove SOLO hesitation sounds: um, uh, eh, ehm, mm, hmm, ah
- Esempi conservativi aggiunti (es. "ok niente facciamo..." → "Ok, niente, facciamo...")

### 7. Bug Fixes v1.2
**API Key Persistence**: `src/core/config_manager.py` (linee 115-138)
- Migliorato fallback decryption: DPAPI → base64 → plaintext
- Previene perdita chiavi quando si passa da exe a dev mode

**Recording Lock After Error**: `src/main.py` (linee 207-284)
- Nuovo metodo `_cleanup_audio_recorder()` per cleanup completo stato
- Chiude stream, svuota buffers, resetta flags
- Previene blocco app dopo errore in registrazione

**Tcl Threading Error**: `src/main.py` (linee 356-388)
- Settings window aperta con `root.after()` nel thread principale
- Fix "Calling Tcl from different apartment"

**Hotkey Validation**: `src/ui/settings_window.py` (linee 496-515), `src/main.py` (linee 111-132)
- Validazione hotkey non vuoto in save e register
- Previene errore "Can only normalize non-empty string names"

**API Connection Tests**: `src/ui/settings_window.py` (linee 488-594)
- Implementati test connessione per Transcription (Groq/OpenAI/Deepgram)
- Implementati test connessione per LLM (Groq/OpenAI/Ollama)
- Verifica API keys prima di salvare

### 4. Calibrazione Microfono Manuale (v1.1)
**File**: `src/ui/settings_window.py` (linee 89-162, 239-295)
- Pulsante "Test Microphone (5s)" nella tab Audio
- Registra 5 secondi di audio, analizza livelli (avg/peak)
- Calcola gain suggerito basato su target_avg=2000
- Applica automaticamente al slider volume gain
- Threading per non bloccare UI durante test

### 5. Auto-Stop su Silenzio (v1.1)
**File**: `src/core/audio_recorder.py` (linee 44-86), `src/main.py` (linee 162-213)
- Silenzio rilevato con `threshold=300` (audio_level < 300)
- Traccia `last_audio_time` aggiornato in audio callback
- Loop registrazione controlla ogni 0.1s con `get_silence_duration()`
- Se silenzio > 60s → auto-stop e processa audio
- Previene registrazioni infinite se utente dimentica di stoppare

### 6. Personalizzazione Hotkey con Cattura (v1.1)
**File**: `src/ui/settings_window.py` (linee 89-162)
- Pulsante "Capture" nella tab Hotkey
- Usa `pynput.keyboard.Listener` per catturare combinazione tasti
- Rileva modifiers (ctrl, shift, alt, win) e key premuta
- Aggiorna entry con formato "ctrl+shift+key"
- Threading per non bloccare UI durante cattura

### 7. Formattazione Automatica Avanzata (v1.1)
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

### 8. Riorganizzazione Struttura Progetto (v1.2)
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

---

## Android Version (MVP)

Port Android dell'applicazione in `mobile/` directory. Stesso concetto, implementazione nativa Android.

### Project Structure Android

```
mobile/
├── app/src/main/
│   ├── java/com/voicedictation/
│   │   ├── service/
│   │   │   ├── VoiceAccessibilityService.kt    # Accessibility service core
│   │   │   └── AudioRecorder.kt                # Audio recording (AudioRecord API)
│   │   ├── provider/
│   │   │   ├── GroqWhisperClient.kt            # Transcription (Retrofit/OkHttp)
│   │   │   └── GroqLLMClient.kt                # LLM post-processing
│   │   ├── ui/
│   │   │   └── MainActivity.kt                 # Settings activity
│   │   └── util/
│   │       ├── ConfigManager.kt                # EncryptedSharedPreferences
│   │       └── TextProcessor.kt                # Pipeline orchestration
│   ├── res/                                    # Android resources (layouts, strings)
│   └── AndroidManifest.xml                     # App manifest + permissions
├── build.gradle.kts                            # Gradle build config
├── README.md                                   # Android-specific documentation
└── TESTING.md                                  # Manual testing checklist
```

### Key Differences from Windows

**Activation**:
- Windows: Global hotkey (ctrl+shift+space)
- Android: Volume Up + Volume Down gesture (via Accessibility Service)

**Permissions**:
- Windows: Admin for global hotkey
- Android: Accessibility Service (must be enabled manually in Settings)

**Storage**:
- Windows: DPAPI encryption (tied to Windows user)
- Android: EncryptedSharedPreferences (tied to device + app signature)

**UI**:
- Windows: System tray + Tkinter settings window
- Android: Main Activity (Settings) + Foreground service notification

**Audio**:
- Windows: sounddevice library
- Android: AudioRecord API (native)

### Architecture Android

Stessa pipeline, componenti Android-nativi:

```
Gesture (Vol Up+Down)
    ↓
VoiceAccessibilityService.onKeyEvent()
    ↓
AudioRecorder.startRecording() [AudioRecord API]
    ↓
[User speaks...]
    ↓
Release gesture or silence timeout
    ↓
AudioRecorder.stopRecording() → WAV bytes
    ↓
TextProcessor.processAudio()
    ├─→ GroqWhisperClient.transcribe() [Retrofit]
    └─→ GroqLLMClient.process() [Retrofit]
    ↓
ClipboardManager + AccessibilityService.PASTE
```

### Android MVP Limitations

- **Solo Groq**: no OpenAI/Deepgram (facile aggiungere dopo)
- **Gesture fisso**: no configurazione trigger
- **No calibration UI**: gain audio fisso
- **No floating widget**: solo notification status
- **Testing parziale**: unit tests su WSL2, testing completo su device fisico

### Development Android

**Setup**:
```bash
cd mobile/
# Open in Android Studio
# Sync Gradle
```

**Build APK**:
```bash
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk
```

**Install**:
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

**Run Tests**:
```bash
# Unit tests (su WSL2/PC)
./gradlew test

# Instrumented tests (richiede device connesso)
./gradlew connectedAndroidTest
```

### Configuration Android

```kotlin
// ConfigManager (EncryptedSharedPreferences)
configManager.setGroqApiKey("gsk_...")
configManager.setVolumeGain(2.0f)
configManager.setSilenceTimeout(30000L)
```

### Common Issues Android

**"Service not enabled"**:
- Settings > Accessibility > Voice Dictation > Enable

**"No API key"**:
- Open app > Enter Groq API key > Save

**Gesture not working**:
- Verify Accessibility Service enabled
- Press Volume Up and Down SIMULTANEOUSLY
- Some devices have hardware conflicts

**Auto-paste not working**:
- Accessibility Service required
- Banking/password apps may block for security
- Fallback: text always in clipboard

### Testing Android

See `mobile/TESTING.md` for complete manual testing checklist.

**Quick smoke test**:
1. Install APK
2. Enable Accessibility Service
3. Enter API key
4. Test microphone (5s)
5. Test transcription
6. Open WhatsApp
7. Volume Up+Down → speak "test" → release
8. Verify "Test." pasted

### Performance Targets Android

Same as Windows:
- Latency <3s (Groq is fast on mobile too)
- Memory <100MB (excluding Android system)
- Battery minimal (service only active during dictation)

### Documentation Android

- `mobile/README.md` - Complete setup and usage guide
- `mobile/TESTING.md` - Manual testing checklist
- `mobile/app/build.gradle.kts` - Dependencies and build config

### Future Android Features

- Multi-provider support (OpenAI, Deepgram)
- Configurable gesture/trigger
- Audio calibration UI
- Floating widget visual feedback
- Custom LLM prompts
- Export/import settings
