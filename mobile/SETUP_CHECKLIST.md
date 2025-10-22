# Voice Dictation Android - Setup Checklist

Use this checklist to ensure everything is configured correctly.

## 📋 Pre-Installation

- [ ] Android device available (Android 8.0 or higher)
- [ ] USB debugging enabled on device
  - Go to: Settings > About Phone > Tap "Build Number" 7 times
  - Go to: Settings > Developer Options > Enable "USB Debugging"
- [ ] ADB installed on computer (or Android Studio)
- [ ] Groq API key obtained from [console.groq.com](https://console.groq.com)
  - Sign up (free)
  - Create new API key
  - Copy key (starts with `gsk_...`)

## 🔨 Build

- [ ] Project opened in Android Studio (or command line ready)
- [ ] Gradle sync completed successfully
  - Android Studio: Wait for "Gradle sync finished" notification
  - Command line: `cd android && ./gradlew clean`
- [ ] No build errors shown
- [ ] Dependencies downloaded (check Gradle build log)

**If using Android Studio**:
- [ ] Device connected via USB and recognized
- [ ] Device appears in device selector dropdown
- [ ] "Run" button (green triangle) is enabled

**If using command line**:
- [ ] ADB recognizes device: `adb devices` shows your device
- [ ] Build completes: `./gradlew assembleDebug` succeeds
- [ ] APK created at: `app/build/outputs/apk/debug/app-debug.apk`

## 📱 Installation

- [ ] APK installed on device
  - Android Studio: Click "Run" button
  - Command line: `adb install app/build/outputs/apk/debug/app-debug.apk`
- [ ] Installation successful (no errors)
- [ ] App appears in app drawer as "Voice Dictation"
- [ ] App icon visible and correct

## ⚙️ Configuration

### Accessibility Service
- [ ] Opened Voice Dictation app
- [ ] Clicked "Enable Service" button
- [ ] Redirected to Accessibility Settings
- [ ] Found "Voice Dictation" in services list
- [ ] Toggled service ON
- [ ] Clicked "Allow" in confirmation dialog
- [ ] Returned to app
- [ ] Status shows "Enabled ✓" in green

### Permissions
- [ ] Microphone permission requested automatically
- [ ] Microphone permission granted
- [ ] No permission errors shown

### API Key
- [ ] Groq API key entered in text field
- [ ] No extra spaces before/after key
- [ ] Password toggle works (shows/hides key)
- [ ] Clicked "Test Transcription"
- [ ] Wait ~5-10 seconds for test
- [ ] Success toast shown: "API connection successful!"

**If test fails**:
- [ ] Check internet connection
- [ ] Verify API key is correct (copy-paste from Groq console)
- [ ] Check API key is active (not revoked)
- [ ] Try again

### Audio
- [ ] Clicked "Test Microphone (5s)"
- [ ] Spoke clearly during 5-second test
- [ ] Results displayed:
  - Audio size >0 bytes
  - Average level >500 (good)
  - Peak level shown
  - Success message shown
- [ ] If levels too low: speak louder or move closer to mic

### Save
- [ ] Clicked "Save" button
- [ ] Toast shown: "Configuration saved"
- [ ] Closed app (swipe away from recents)
- [ ] Reopened app
- [ ] Settings persisted (API key still masked in field)

## ✅ First Test

### Simple Dictation
- [ ] Opened a test app (Notes, Chrome, WhatsApp)
- [ ] Tapped in text field (keyboard should appear, then hide it)
- [ ] **Pressed Volume Up + Volume Down simultaneously**
- [ ] Notification appeared: "Recording..."
- [ ] Said clearly: "Hello world, this is a test"
- [ ] **Released both volume keys**
- [ ] Notification changed: "Transcribing..." → "Processing..." → "Done!"
- [ ] Text appeared in field: "Hello world, this is a test."
- [ ] Capitalization correct (capital H)
- [ ] Punctuation correct (period at end)

### Test in Multiple Apps
- [ ] Chrome (URL bar or search)
- [ ] WhatsApp (new message)
- [ ] Gmail (compose email)
- [ ] Notes app

For each app:
- [ ] Gesture works (Volume Up+Down)
- [ ] Recording starts
- [ ] Text auto-pastes after processing
- [ ] No crashes

### Advanced Features
- [ ] Lists: "first point API, second database, third frontend"
  - Expected: Numbered list (1. API, 2. Database, 3. Frontend)
- [ ] Bullets: "reminder buy milk eggs bread"
  - Expected: Bullet list with items
- [ ] Self-corrections: "tomorrow, no Friday at 3pm"
  - Expected: "Friday at 3pm." (tomorrow removed)

## 🐛 Troubleshooting

**Nothing happens when pressing volume keys?**
- [ ] Accessibility Service enabled? (check status in app)
- [ ] Pressing BOTH keys at same time?
- [ ] Try in different app (some apps may conflict)

**No sound recorded?**
- [ ] Microphone permission granted?
- [ ] Device microphone working? (test with voice recorder)
- [ ] Microphone not blocked physically?

**API errors?**
- [ ] Internet connection active?
- [ ] API key correct?
- [ ] Test transcription passes?

**Text not pasted?**
- [ ] Some apps block auto-paste (banking, passwords)
- [ ] Check clipboard - text should be there
- [ ] Use manual paste (long-press → Paste)

## 📊 Verification

All checks passed? You're ready to use Voice Dictation!

**Final verification**:
- [ ] Can dictate in at least 3 different apps
- [ ] Latency <5 seconds (target <3s)
- [ ] Auto-paste works (or manual paste from clipboard)
- [ ] No crashes or freezes
- [ ] Battery drain minimal (check after 1 hour of normal use)

## 📚 Next Steps

- [ ] Read full documentation: [README.md](README.md)
- [ ] Review testing guide: [TESTING.md](TESTING.md)
- [ ] Try advanced formatting (lists, bullets, corrections)
- [ ] Report issues or feedback
- [ ] Enjoy dictating! 🎤

## 🆘 Need Help?

Check logs:
```bash
adb logcat | grep VoiceDict
```

Review:
- [README.md](README.md) - Full documentation
- [TESTING.md](TESTING.md) - Testing guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start
- [../CLAUDE.md](../CLAUDE.md) - Architecture details

---

**Setup Status**: [ ] Complete ✅ | [ ] Issues ⚠️ | [ ] Not Started ⏳
