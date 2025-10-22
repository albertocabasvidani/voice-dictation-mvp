# Voice Dictation Android - Quick Start

Get up and running in 5 minutes!

## 1. Prerequisites

- Android device (8.0+) with USB debugging enabled
- Android Studio installed (or just ADB for building via command line)
- Groq API key (free at [console.groq.com](https://console.groq.com))

## 2. Build & Install

### Option A: Android Studio (Recommended)

```bash
# Open project in Android Studio
File > Open > select this `mobile/` folder

# Wait for Gradle sync to complete

# Connect device via USB

# Click Run button (green triangle)
```

### Option B: Command Line

```bash
cd mobile/

# Build APK
./gradlew assembleDebug

# Install on connected device
adb install app/build/outputs/apk/debug/app-debug.apk
```

## 3. Configure

1. **Open** Voice Dictation app on your device
2. **Click** "Enable Service" button
   - You'll be redirected to Accessibility Settings
   - Find "Voice Dictation" and toggle it ON
   - Click "Allow" in the confirmation dialog
3. **Go back** to the app (it should show "Enabled ✓" now)
4. **Enter** your Groq API key in the text field
5. **Click** "Test Transcription" to verify it works
6. **Click** "Save"

## 4. First Dictation

1. Open any app (WhatsApp, Chrome, Notes, etc.)
2. Tap in a text field
3. **Press Volume Up + Volume Down simultaneously**
4. Speak: "Hello world, this is a test"
5. **Release both keys**
6. Wait 2-3 seconds
7. Text appears: "Hello world, this is a test."

## 5. Troubleshooting

**Nothing happens when pressing volume keys?**
- Make sure Accessibility Service is enabled (step 3.2)
- Press both keys AT THE SAME TIME
- Try again in a different app

**Text not pasted automatically?**
- Some apps block auto-paste for security (banking apps, password fields)
- Text is always copied to clipboard - use manual paste (long-press → Paste)

**API error?**
- Check internet connection
- Verify API key is correct (no extra spaces)
- Test key at [console.groq.com](https://console.groq.com)

**Low audio quality?**
- Click "Test Microphone (5s)" in Settings
- Speak louder or move closer to mic
- Average level should be >500

## Next Steps

- Read [README.md](README.md) for complete documentation
- Check [TESTING.md](TESTING.md) for testing guide
- Try advanced features:
  - Lists: "first point API, second database, third frontend"
  - Bullet points: "reminder buy milk eggs bread"
  - Self-corrections: "tomorrow, no Friday at 3pm"

## Support

If you encounter issues:
1. Check device logs: `adb logcat | grep VoiceDict`
2. Verify all permissions granted
3. Test with simple apps first (Notes, Chrome)
4. Review CLAUDE.md for architecture details

Enjoy dictating! 🎤
