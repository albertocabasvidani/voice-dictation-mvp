# Voice Dictation Android - Manual Testing Guide

Complete manual testing checklist for Voice Dictation Android app.

## Prerequisites

- [ ] Android device with API 26+ (Android 8.0 Oreo or higher)
- [ ] Valid Groq API key from [console.groq.com](https://console.groq.com)
- [ ] USB debugging enabled (Settings > Developer Options > USB Debugging)
- [ ] ADB installed on development machine

## Installation Testing

### APK Installation
- [ ] Build APK: `./gradlew assembleDebug`
- [ ] Install via ADB: `adb install app/build/outputs/apk/debug/app-debug.apk`
- [ ] Verify app appears in app drawer as "Voice Dictation"
- [ ] Verify app icon displays correctly

### Permissions
- [ ] Launch app - microphone permission requested automatically
- [ ] Grant microphone permission
- [ ] Verify no crashes after granting

## Settings Configuration

### Accessibility Service
- [ ] Click "Enable Service" button
- [ ] Verify redirected to Accessibility Settings
- [ ] Find "Voice Dictation" in accessibility services list
- [ ] Enable service
- [ ] Verify service description shows correctly
- [ ] Return to app
- [ ] Verify "Service Status" shows "Enabled ✓" in green

### API Key Configuration
- [ ] Enter valid Groq API key in text field
- [ ] Verify password toggle shows/hides key
- [ ] Click "Test Transcription" button
- [ ] Wait for test to complete (~5-10 seconds)
- [ ] Verify success toast: "API connection successful!"
- [ ] Test with invalid key (remove last character)
- [ ] Verify error toast: "API test failed: ..."
- [ ] Restore valid key

### Save Configuration
- [ ] Click "Save" button
- [ ] Verify success toast: "Configuration saved"
- [ ] Close app (swipe away from recent apps)
- [ ] Reopen app
- [ ] Verify API key persisted (shows masked in field)

## Audio Testing

### Microphone Test
- [ ] Click "Test Microphone (5s)" button
- [ ] Speak clearly for 5 seconds ("testing one two three...")
- [ ] Wait for test to complete
- [ ] Verify results displayed:
  - [ ] Audio size >0 bytes
  - [ ] Average level >500 (good)
  - [ ] Peak level >1000 (good)
  - [ ] Success message "✓ Audio levels good"

### Microphone Test - Low Volume
- [ ] Click "Test Microphone (5s)"
- [ ] Whisper very quietly or don't speak
- [ ] Verify warning: "⚠️ Low audio level - speak louder or move closer to mic"

### Microphone Test - No Permission
- [ ] Revoke microphone permission: Settings > Apps > Voice Dictation > Permissions > Microphone > Deny
- [ ] Return to app
- [ ] Click "Test Microphone (5s)"
- [ ] Verify permission request dialog appears
- [ ] Grant permission
- [ ] Test works correctly

## Voice Dictation Functionality

### Basic Dictation
- [ ] Open any text field (Chrome, Notes, WhatsApp, etc.)
- [ ] **Press Volume Up + Volume Down simultaneously**
- [ ] Verify notification appears: "Recording..."
- [ ] Say: "Hello world, this is a test"
- [ ] **Release both volume keys**
- [ ] Verify notification changes: "Transcribing..." → "Processing..." → "Done!"
- [ ] Verify text appears in active field: "Hello world, this is a test."
- [ ] Verify proper capitalization and punctuation

### Dictation in Different Apps

Test in each app:
- [ ] Chrome browser (URL bar, search box, text area)
- [ ] Gmail (compose email)
- [ ] WhatsApp (chat message)
- [ ] Notes app (note content)
- [ ] Google Keep (note)
- [ ] Slack (message)

For each app:
- [ ] Gesture starts recording
- [ ] Auto-paste works correctly
- [ ] No crashes or errors

### Silence Detection
- [ ] Start dictation (Volume Up + Down)
- [ ] Speak for 5 seconds
- [ ] Stay silent for 60+ seconds
- [ ] Verify auto-stop and processing starts
- [ ] Verify text pasted correctly

### Complex Text Formatting

#### Lists
- [ ] Say: "first point is the API, second the database, third the frontend"
- [ ] Verify formatted as numbered list:
  ```
  1. API
  2. Database
  3. Frontend
  ```

#### Bullet Points
- [ ] Say: "reminder buy milk eggs and bread"
- [ ] Verify formatted as bullet list:
  ```
  Reminder:
  • Buy milk
  • Eggs
  • Bread
  ```

#### Self-Corrections
- [ ] Say: "meeting tomorrow, no Friday at 3pm"
- [ ] Verify output: "Meeting Friday at 3pm." (tomorrow removed)

#### Filler Words
- [ ] Say: "um so uh I think that uh we should um go ahead"
- [ ] Verify output: "I think that we should go ahead." (fillers removed)

### Italian Language
- [ ] Say: "ciao come stai oggi è una bella giornata"
- [ ] Verify proper Italian formatting: "Ciao, come stai? Oggi è una bella giornata."

### Edge Cases

#### Empty Recording
- [ ] Press and immediately release gesture (no speech)
- [ ] Verify no error, no paste
- [ ] Verify notification resets to "Service running"

#### Very Short Recording
- [ ] Say single word "test"
- [ ] Verify transcribes correctly: "Test."

#### Long Recording (2+ minutes)
- [ ] Speak continuously for 2 minutes
- [ ] Verify records full duration
- [ ] Verify transcription complete and accurate
- [ ] Check for memory issues

#### Rapid Repeated Dictations
- [ ] Perform 10 dictations in quick succession
- [ ] Verify each works correctly
- [ ] Verify no memory leaks or slowdown
- [ ] Check notification updates properly

## Error Handling

### No Internet Connection
- [ ] Enable airplane mode
- [ ] Attempt dictation
- [ ] Verify error toast shows
- [ ] Verify app doesn't crash
- [ ] Disable airplane mode
- [ ] Verify next dictation works

### API Key Invalid/Expired
- [ ] Change API key to invalid value
- [ ] Attempt dictation
- [ ] Verify error toast: "Transcription failed. Please check your API key..."
- [ ] Restore valid key
- [ ] Verify works again

### Service Disabled During Use
- [ ] Start dictation
- [ ] While recording, go to Settings > Accessibility
- [ ] Disable Voice Dictation service
- [ ] Return to app
- [ ] Verify graceful handling (no crash)
- [ ] Re-enable service
- [ ] Verify functionality restored

### App Killed During Recording
- [ ] Start dictation
- [ ] While recording, force-stop app (Settings > Apps > Force Stop)
- [ ] Verify recording stops cleanly
- [ ] Restart app
- [ ] Verify service reconnects properly

## Performance Testing

### Latency Measurement
- [ ] Say: "quick test"
- [ ] Measure time from release to paste
- [ ] Target: <3 seconds (p95)
- [ ] Verify within target

### Multiple Rapid Tests
- [ ] Perform 20 dictations back-to-back
- [ ] Verify latency doesn't degrade
- [ ] Check for memory leaks (Settings > Developer > Memory)

### Battery Impact
- [ ] Charge device to 100%
- [ ] Perform 50 dictations over 30 minutes
- [ ] Check battery usage (Settings > Battery)
- [ ] Verify Voice Dictation <5% battery usage

## UI/UX Testing

### Settings Screen
- [ ] All text readable
- [ ] Buttons properly sized
- [ ] Cards display correctly
- [ ] Scrolling smooth
- [ ] No layout issues on different screen sizes

### Notification
- [ ] Notification appears when recording
- [ ] Status updates correctly (Recording → Transcribing → Processing → Done)
- [ ] Notification dismisses after completion
- [ ] Tapping notification (if implemented) works

### Toast Messages
- [ ] All toasts readable
- [ ] Appropriate duration (SHORT/LONG)
- [ ] No overlapping toasts

## Device Compatibility

Test on multiple devices:
- [ ] Android 8.0 (API 26) - minimum supported
- [ ] Android 11 (API 30)
- [ ] Android 13 (API 33)
- [ ] Android 14 (API 34) - latest

For each device:
- [ ] Gesture detection works
- [ ] Auto-paste works
- [ ] No crashes
- [ ] Acceptable performance

## Accessibility Testing

### Talkback
- [ ] Enable Talkback (Settings > Accessibility > Talkback)
- [ ] Navigate Settings screen with Talkback
- [ ] Verify all elements announced correctly
- [ ] Verify buttons actionable via Talkback

### High Contrast / Large Text
- [ ] Enable high contrast mode
- [ ] Verify text readable
- [ ] Enable large text (Settings > Display > Font Size)
- [ ] Verify layout adapts correctly

## Security Testing

### API Key Storage
- [ ] Enter API key and save
- [ ] Use ADB to check SharedPreferences:
  ```bash
  adb shell
  run-as com.voicedictation
  cat shared_prefs/encrypted_prefs.xml
  ```
- [ ] Verify API key is encrypted (not plain text)

### Clipboard Security
- [ ] Dictate sensitive text
- [ ] Verify clipboard cleared after paste (or timeout)
- [ ] Verify no clipboard history leak

## Regression Testing

After any code changes, verify:
- [ ] All basic dictation tests pass
- [ ] No new crashes
- [ ] Performance unchanged
- [ ] API integration still works

## Test Results Template

```
Date: YYYY-MM-DD
Tester: [Name]
Device: [Model] (Android [Version])
Build: app-debug.apk v[Version]

Results:
- Installation: PASS/FAIL
- Settings: PASS/FAIL
- Audio: PASS/FAIL
- Dictation: PASS/FAIL
- Edge Cases: PASS/FAIL
- Performance: PASS/FAIL

Issues Found:
1. [Issue description]
2. [Issue description]

Notes:
[Any additional observations]
```

## Automated Testing

While manual testing above is required, also run automated tests:

```bash
# Unit tests
./gradlew test

# Instrumented tests (with device connected)
./gradlew connectedAndroidTest
```

Verify all tests pass before release.
