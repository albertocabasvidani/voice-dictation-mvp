# Voice Dictation MVP

App desktop Windows per dettatura vocale intelligente con trascrizione e auto-formattazione, ispirata a Wispr Flow.

## Caratteristiche

- **Push-to-talk** con hotkey configurabile
- **Multi-provider trascrizione**: Groq Whisper, OpenAI Whisper, Deepgram
- **Multi-provider LLM**: Ollama (locale), OpenAI, Groq
- **Auto-formattazione**: rimozione filler words, punteggiatura, correzioni
- **Inserimento automatico** testo nell'app attiva
- **Configurazione completa** tramite file JSON

## Requisiti

- Windows 10/11 64-bit
- Python 3.11+
- (Opzionale) Ollama installato per LLM locale

## Installazione

1. Clona il repository
2. Crea virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Installa dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

4. Copia template configurazione:
   ```bash
   copy config\config.template.json config\config.json
   ```

5. Modifica `config/config.json` con le tue API keys e preferenze

## Configurazione

### Trascrizione

Scegli uno dei provider:

- **Groq** (gratis): Registrati su https://console.groq.com
- **OpenAI**: API key da https://platform.openai.com
- **Deepgram**: API key da https://console.deepgram.com

### LLM Post-Processing

Scegli uno dei provider:

- **Ollama** (locale, gratis):
  - Installa: https://ollama.ai/download
  - Scarica modello: `ollama pull llama3.2:3b`

- **OpenAI**: Usa stessa API key della trascrizione

- **Groq** (gratis): Usa stessa API key della trascrizione

### File Configurazione

Esempio `config/config.json`:

```json
{
  "transcription": {
    "provider": "groq",
    "api_key_encrypted": "BASE64_ENCRYPTED_STRING"
  },
  "llm": {
    "provider": "ollama",
    "model": "llama3.2:3b",
    "ollama_url": "http://localhost:11434"
  },
  "hotkey": {
    "modifiers": ["ctrl", "shift"],
    "key": "space"
  }
}
```

## Uso

### Opzione 1: Eseguibile Windows (Più Semplice)

1. **Download** o build eseguibile (vedi sezione Build)
2. Crea `config.json` con le tue API keys (vedi `README_USER.txt`)
3. Esegui `VoiceDictation.exe`
4. Premi `Ctrl+Shift+Space` per registrare

### Opzione 2: Da Codice Sorgente

1. Avvia l'app:
   ```bash
   python src/main.py
   ```

2. Premi hotkey (default: `Ctrl+Shift+Space`)
3. Parla
4. Rilascia hotkey
5. Il testo verrà inserito automaticamente

## Build Eseguibile Windows

### Build Automatico

```cmd
build_exe.bat
```

Output: `dist/VoiceDictation.exe`

### Build Manuale

```bash
pip install pyinstaller
pyinstaller VoiceDictation.spec
```

Vedi `BUILD.md` per dettagli completi.

## Sviluppo

### Struttura Progetto

```
src/
├── core/           # Logica principale
├── providers/      # Implementazioni provider API
├── ui/             # Interface utente
└── main.py         # Entry point

config/             # File configurazione
tests/              # Test unitari
```

### Test

```bash
pytest tests/
```

### Build Eseguibile

```bash
pyinstaller --onefile --windowed src/main.py
```

## License

MIT
