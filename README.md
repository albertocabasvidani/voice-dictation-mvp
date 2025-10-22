# Voice Dictation - Wispr Flow Clone

Voice dictation application with AI-powered transcription and smart formatting, available for **Windows Desktop** and **Android Mobile**.

**Pipeline**: Audio recording → Groq Whisper API (transcription) → Groq LLM (formatting) → Clipboard + Auto-paste

---

## 🎯 Quick Links

| Platform | Status | Documentation | Quick Start |
|----------|--------|---------------|-------------|
| **Windows Desktop** | ✅ Production Ready | [desktop/docs/README.md](desktop/docs/README.md) | [Setup](#windows-desktop) |
| **Android Mobile** | ✅ MVP Ready | [mobile/README.md](mobile/README.md) | [Setup](#android-mobile) |

---

## 🚀 Features

### Common Features (Both Platforms)
- ✅ **Voice transcription**: Groq Whisper API (free tier, <1s latency)
- ✅ **Smart formatting**: Auto-punctuation, capitalization, lists, paragraphs
- ✅ **LLM post-processing**: Groq LLaMA for intelligent text cleanup
- ✅ **Auto-paste**: Formatted text inserted automatically
- ✅ **Privacy**: API keys encrypted, audio never saved to disk
- ✅ **Works everywhere**: Any text field in any application

### Platform-Specific Features

**Windows Desktop**:
- Global hotkey activation (customizable, default: Ctrl+Shift+Space)
- System tray integration
- Multi-provider support (Groq, OpenAI, Deepgram, Ollama)
- Audio calibration with gain control
- ESC to cancel recording

**Android Mobile**:
- Volume button gesture activation (Volume Up + Down)
- Accessibility Service integration
- Foreground service with notifications
- Encrypted configuration storage

---

## 📦 What's Inside

```
voice-dictation/
├── README.md              ← You are here
├── CLAUDE.md              ← Complete documentation for Claude Code
├── .gitignore             ← Git ignore rules
│
├── desktop/               ← Windows Desktop Implementation (Python)
│   ├── src/               ← Source code
│   ├── config/            ← Configuration files
│   ├── docs/              ← Documentation (BUILD.md, README.md, etc.)
│   ├── tests/             ← Unit and integration tests
│   ├── requirements.txt   ← Python dependencies
│   ├── build_exe.bat      ← Build script
│   └── VoiceDictation.spec ← PyInstaller config
│
└── mobile/                ← Android Mobile Implementation (Kotlin)
    ├── app/               ← Android app source
    ├── gradle/            ← Gradle wrapper
    ├── README.md          ← Android documentation
    ├── QUICKSTART.md      ← 5-minute setup guide
    ├── TESTING.md         ← Testing guide
    └── build.gradle.kts   ← Build configuration
```

---

## 🖥️ Windows Desktop

### Requirements
- Windows 10/11
- Python 3.9+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Quick Setup

```bash
cd desktop/

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

### Build Executable

```bash
cd desktop/
build_exe.bat
# Output: desktop/dist/VoiceDictation/VoiceDictation.exe
```

### Usage
1. Run `VoiceDictation.exe` (icon appears in system tray)
2. Double-click tray icon → enter Groq API key → Save
3. Press **Ctrl+Shift+Space** to start dictation
4. Speak your text
5. Press hotkey again to stop (or ESC to cancel)
6. Formatted text auto-pasted

📚 **Full Documentation**: [desktop/docs/README.md](desktop/docs/README.md)

---

## 📱 Android Mobile

### Requirements
- Android 8.0+ (API 26+)
- Android Studio (for development) or ADB (for installation)
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Quick Setup

```bash
cd mobile/

# Build APK
./gradlew assembleDebug

# Install on connected device
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Configuration
1. Open Voice Dictation app
2. Enable Accessibility Service (Settings → Accessibility → Voice Dictation)
3. Enter Groq API key → Test → Save

### Usage
1. Open any app (WhatsApp, Chrome, Notes, etc.)
2. Tap in text field
3. **Press Volume Up + Volume Down simultaneously**
4. Speak your text
5. Release keys (or wait for auto-stop)
6. Formatted text auto-pasted

📚 **Full Documentation**: [mobile/README.md](mobile/README.md)
⚡ **Quick Start**: [mobile/QUICKSTART.md](mobile/QUICKSTART.md)

---

## 🏗️ Architecture

Both implementations share the same conceptual pipeline:

```
User Input (Hotkey/Gesture)
    ↓
Audio Recording (16kHz mono, silence detection)
    ↓
Groq Whisper API → Raw transcription
    ↓
Groq LLM API → Smart formatting
    ↓
Clipboard + Auto-paste
```

### Key Differences

| Aspect | Windows Desktop | Android Mobile |
|--------|----------------|----------------|
| **Language** | Python 3.9+ | Kotlin |
| **Activation** | Global hotkey | Volume button gesture |
| **Audio** | sounddevice library | AudioRecord API |
| **UI** | System tray + Tkinter | Main Activity + Notification |
| **Storage** | DPAPI encryption | EncryptedSharedPreferences |
| **Permissions** | Admin (for hotkey) | Accessibility Service |
| **Providers** | Groq, OpenAI, Deepgram, Ollama | Groq only (MVP) |

---

## 🧪 Testing

### Desktop
```bash
cd desktop/
pytest tests/
```

### Mobile
```bash
cd mobile/
./gradlew test                    # Unit tests
./gradlew connectedAndroidTest    # Instrumented tests (device required)
```

See platform-specific testing guides for manual testing checklists.

---

## 🔑 API Keys

Both platforms use **Groq API** (free tier available):

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create API key
3. Enter in app settings (encrypted automatically)

**Models used**:
- Transcription: `whisper-large-v3`
- LLM: `llama-3.1-8b-instant`

**Costs**: Free tier generous, then ~$0.10/hour of audio (transcription) + minimal LLM costs

---

## 📊 Performance

| Metric | Target | Typical |
|--------|--------|---------|
| **Total Latency** | <3s | 1-2s |
| Transcription | <2s | 0.5-1s |
| LLM Processing | <1s | 0.3-0.5s |
| **Memory (Desktop)** | <150MB | ~100MB |
| **Memory (Mobile)** | <100MB | ~50MB |

---

## 🔒 Security & Privacy

- ✅ API keys encrypted (DPAPI on Windows, Android Keystore on mobile)
- ✅ Audio processed in memory, never saved to disk
- ✅ HTTPS-only API communication
- ✅ No telemetry or analytics
- ✅ Open source code (auditable)

---

## 🗺️ Roadmap

### Desktop
- [x] Multi-provider support (Groq, OpenAI, Deepgram, Ollama)
- [x] Custom hotkey configuration
- [x] Audio calibration
- [x] Auto-stop on silence
- [ ] Floating widget mode
- [ ] Custom LLM prompts

### Mobile
- [x] Groq provider (MVP)
- [x] Volume gesture activation
- [x] Auto-stop on silence
- [ ] Multi-provider support
- [ ] Configurable gesture
- [ ] Audio calibration UI
- [ ] Floating widget

---

## 🛠️ Development

### For Developers

**Desktop**:
- Language: Python 3.9+
- Key libraries: sounddevice, keyboard, pystray, tkinter
- Entry point: `desktop/src/main.py`
- Build: PyInstaller (`build_exe.bat`)

**Mobile**:
- Language: Kotlin
- Framework: Android SDK (API 26+)
- Build system: Gradle
- Entry point: `mobile/app/src/main/java/com/voicedictation/`

**Shared**:
- Architecture: Multi-provider pattern
- Pipeline: Audio → Transcription → LLM → Output
- Testing: Unit tests + manual testing checklists

### Contributing

This is a personal project, but suggestions welcome:
1. Check platform-specific README for architecture details
2. Review [CLAUDE.md](CLAUDE.md) for development guidelines
3. Open issue or submit PR

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [CLAUDE.md](CLAUDE.md) | Complete guide for Claude Code (both platforms) |
| [desktop/docs/README.md](desktop/docs/README.md) | Windows desktop documentation |
| [desktop/docs/BUILD.md](desktop/docs/BUILD.md) | Desktop build instructions |
| [mobile/README.md](mobile/README.md) | Android mobile documentation |
| [mobile/QUICKSTART.md](mobile/QUICKSTART.md) | Android quick start (5 min) |
| [mobile/TESTING.md](mobile/TESTING.md) | Android testing guide |

---

## ⚠️ Known Issues

### Desktop
- Requires admin privileges for global hotkey
- Ollama local models need 4-8GB RAM
- Some apps block auto-paste (fallback: clipboard)

### Mobile
- Volume button conflicts on some devices
- Banking apps may block auto-paste (security)
- Accessibility Service must be manually enabled

See platform-specific docs for troubleshooting.

---

## 📄 License

[Specify license here - e.g., MIT, GPL, etc.]

---

## 🙏 Credits

**Technologies**:
- **Groq API** - Fast transcription & LLM inference
- **Whisper** - Speech-to-text model by OpenAI
- **LLaMA** - Language model by Meta

**Desktop Stack**:
- Python, sounddevice, keyboard, pystray, tkinter, PyInstaller

**Mobile Stack**:
- Kotlin, Android SDK, Retrofit, OkHttp, Material Design

Built with ❤️ and Claude Code 🤖

---

## 🚦 Status

| Platform | Build | Tests | Release |
|----------|-------|-------|---------|
| Windows Desktop | ✅ Passing | ✅ Passing | v1.1 Production |
| Android Mobile | ✅ Passing | ⏳ Manual Testing | v1.0 MVP |

Last updated: 2025-10-22
