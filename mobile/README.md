# Voice Dictation Android (Wispr Flow Clone)

Android version of Voice Dictation MVP - Voice dictation app for Android using Accessibility Service.

**Pipeline**: Audio recording → Groq Whisper (transcription) → Groq LLM (formatting) → Clipboard + Auto-paste

## Features

- **Gesture-based activation**: Press Volume Up + Volume Down simultaneously to start dictation
- **Voice transcription**: Groq Whisper API (free tier, <1s latency)
- **Smart formatting**: Groq LLM (llama-3.1-8b-instant) for text cleanup and structuring
- **Auto-paste**: Accessibility Service automatically pastes formatted text
- **Silence detection**: Auto-stop after 60 seconds of silence
- **Works in any app**: Chrome, WhatsApp, Notes, Email, etc.

## Requirements

- **Android**: 8.0 (Oreo) or higher (API 26+)
- **Permissions**: Microphone, Accessibility Service, Overlay
- **API Key**: Free Groq API key from [console.groq.com](https://console.groq.com)
- **Development**: Android Studio Hedgehog (2023.1.1) or higher

## Project Structure

```
mobile/
├── app/
│   ├── src/main/java/com/voicedictation/
│   │   ├── service/
│   │   │   ├── VoiceAccessibilityService.kt    # Core accessibility service
│   │   │   └── AudioRecorder.kt                # Audio recording with silence detection
│   │   ├── provider/
│   │   │   ├── GroqWhisperClient.kt            # Transcription API client
│   │   │   └── GroqLLMClient.kt                # LLM post-processing client
│   │   ├── ui/
│   │   │   └── MainActivity.kt                 # Settings activity
│   │   └── util/
│   │       ├── ConfigManager.kt                # Encrypted configuration storage
│   │       └── TextProcessor.kt                # Pipeline orchestration
│   ├── src/test/                               # Unit tests
│   └── src/androidTest/                        # Instrumented tests
└── README.md                                   # This file
```

## Setup Instructions

### 1. Clone and Open in Android Studio

```bash
cd mobile/
# Open in Android Studio: File > Open > select mobile/ folder
```

### 2. Sync Gradle Dependencies

Android Studio will automatically prompt to sync Gradle. If not:
```
File > Sync Project with Gradle Files
```

### 3. Get Groq API Key

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create a new API key (free tier available)
3. Copy the key (you'll enter it in the app later)

### 4. Build the APK

**Option A: Android Studio**
```
Build > Build Bundle(s) / APK(s) > Build APK(s)
```

**Option B: Command Line**
```bash
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk
```

### 5. Install on Device

**Via Android Studio**: Click "Run" button (green triangle)

**Via ADB**:
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

**Via File Transfer**: Copy APK to phone and open to install

### 6. Configure App

1. Open Voice Dictation app
2. Click "Enable Service" → enable "Voice Dictation" in Accessibility settings
3. Go back to app
4. Enter your Groq API key
5. Click "Test Transcription" to validate
6. Click "Test Microphone" to check audio levels
7. Click "Save"

### 7. Grant Permissions

The app will request:
- **Microphone**: Required for voice recording
- **Overlay**: Required for recording status indicator (if using floating widget)

Accessibility Service permission must be granted manually in step 6.

## Usage

1. Open any app where you want to type (Chrome, WhatsApp, Notes, etc.)
2. **Press Volume Up + Volume Down simultaneously** to start dictation
3. Speak your text
4. **Release both keys** to stop recording
5. Wait 1-3 seconds for processing
6. Formatted text will be auto-pasted into the active field

**Alternative stop**: Silence for 60 seconds will auto-stop recording

## Testing

### Unit Tests (Run on Development Machine)

```bash
# All unit tests
./gradlew test

# Specific test
./gradlew test --tests "com.voicedictation.provider.GroqWhisperClientTest"

# With coverage
./gradlew testDebugUnitTest jacocoTestReport
```

**Note**: Some tests require URL injection for proper mocking. See test files for details.

### Instrumented Tests (Require Connected Device)

```bash
# Connect Android device via USB with debugging enabled
adb devices

# Run instrumented tests
./gradlew connectedAndroidTest
```

### Manual Testing

See [TESTING.md](TESTING.md) for detailed manual test checklist.

## Architecture

### Multi-Provider Pattern

Like the Windows version, this uses a provider pattern for future extensibility:

- **Transcription**: Currently Groq Whisper (can add OpenAI, Deepgram)
- **LLM**: Currently Groq LLM (can add OpenAI GPT, local models)

### Pipeline Flow

```
User Press Gesture
    ↓
VoiceAccessibilityService.onKeyEvent()
    ↓
AudioRecorder.startRecording()
    ↓
[User speaks...]
    ↓
User Release Gesture (or silence timeout)
    ↓
AudioRecorder.stopRecording() → WAV bytes
    ↓
TextProcessor.processAudio()
    ├─→ GroqWhisperClient.transcribe() → raw text
    └─→ GroqLLMClient.process() → formatted text
    ↓
ClipboardManager.setPrimaryClip()
    ↓
AccessibilityService.performGlobalAction(PASTE)
```

### Security

- **API Keys**: Encrypted with Android Keystore (EncryptedSharedPreferences)
- **Encryption**: AES256-GCM, tied to device and app signature
- **Audio**: Not saved to disk, only processed in memory
- **Network**: HTTPS only (Groq API enforces TLS)

## Configuration

All settings stored in encrypted SharedPreferences:

```kotlin
// Get/Set API key
configManager.setGroqApiKey("gsk_...")
val key = configManager.getGroqApiKey()

// Volume gain (future feature)
configManager.setVolumeGain(2.0f)

// Silence timeout
configManager.setSilenceTimeout(30000L) // 30 seconds
```

## Troubleshooting

### "Service not enabled"
- Go to Settings > Accessibility > Voice Dictation > Enable
- Grant permission and click "Allow"

### "No API key configured"
- Open app Settings
- Enter Groq API key
- Click "Save"

### "Microphone permission denied"
- Go to Settings > Apps > Voice Dictation > Permissions
- Enable Microphone

### Gesture not working
- Make sure Accessibility Service is enabled
- Try pressing Volume Up and Volume Down at exactly the same time
- Some devices may have hardware volume key conflicts

### Low audio quality
- Click "Test Microphone (5s)" in Settings
- Check audio levels (should be >500 average)
- Speak closer to microphone
- Check device microphone not blocked

### Auto-paste not working
- Accessibility Service must be enabled
- Some apps (banking, password fields) block auto-paste for security
- Manual fallback: text is always in clipboard (Ctrl+V / long-press paste)

## Development

### Code Style

Follow Kotlin coding conventions:
```bash
# Format code
./gradlew ktlintFormat

# Check code style
./gradlew ktlintCheck
```

### Logging

Uses Timber for logging:
```kotlin
Timber.d("Debug message")
Timber.e(exception, "Error message")
```

Logs visible in Android Studio Logcat:
```bash
adb logcat | grep VoiceDict
```

### Adding New Providers

1. Create new client in `provider/` package
2. Implement common interface (transcribe or process)
3. Add to TextProcessor factory
4. Update Settings UI dropdown

## Performance Targets

- **Total latency**: <3s (p95)
  - Transcription: <2s (Groq Whisper is fast)
  - LLM: <1s (llama-3.1-8b-instant)
- **Memory**: <100MB (excluding Android system overhead)
- **Battery**: Minimal impact (service only active during dictation)

## Limitations (MVP)

- Only Groq provider (no OpenAI/Deepgram alternatives)
- Gesture trigger only (no configurable hotkey)
- No audio calibration UI (fixed gain)
- No custom LLM prompts
- English/Italian primarily (depends on Whisper model)

## Roadmap

- [ ] Multi-provider support (OpenAI, Deepgram)
- [ ] Configurable gesture/trigger
- [ ] Audio calibration UI
- [ ] Custom LLM prompts
- [ ] Floating widget for visual feedback
- [ ] Export/import settings
- [ ] Usage statistics

## License

Same as parent project (Windows version).

## Credits

Android port of Voice Dictation (Wispr Flow clone) by the same author.

**Technologies**:
- Kotlin + Coroutines
- Android Accessibility Service
- Groq API (Whisper + LLaMA)
- Retrofit + OkHttp
- EncryptedSharedPreferences
- Material Design Components
