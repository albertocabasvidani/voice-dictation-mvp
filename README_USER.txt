================================================================================
                        VOICE DICTATION MVP
            Voice-to-Text with AI Post-Processing for Windows
================================================================================

QUICK START
-----------

1. SETUP (First time only):
   - Create a file named "config.json" in the same folder as this exe
   - Copy the template below and fill in your API keys

2. GET API KEYS (Free options):
   - Groq (Recommended): https://console.groq.com
     * Sign up, create API key
     * Free tier: 30 requests/minute

   - Alternative: OpenAI (https://platform.openai.com)
     * Requires credits ($5 minimum)

3. RUN:
   - Double-click VoiceDictation.exe
   - System tray icon will appear (green circle)
   - Press Ctrl+Shift+Space to start recording
   - Speak
   - Release Ctrl+Shift+Space to stop
   - Text will be inserted automatically!

================================================================================

CONFIG.JSON TEMPLATE
--------------------

Create this file in the same folder as VoiceDictation.exe:

{
  "version": "1.0",
  "hotkey": {
    "modifiers": ["ctrl", "shift"],
    "key": "space"
  },
  "transcription": {
    "provider": "groq",
    "api_key_encrypted": "YOUR_GROQ_API_KEY_HERE",
    "options": {
      "language": "auto"
    }
  },
  "llm": {
    "provider": "groq",
    "api_key_encrypted": "YOUR_GROQ_API_KEY_HERE",
    "model": "llama-3.1-8b-instant",
    "ollama_url": "http://localhost:11434",
    "temperature": 0.3,
    "max_tokens": 500
  },
  "audio": {
    "device_index": -1,
    "sample_rate": 16000
  },
  "behavior": {
    "auto_paste": true,
    "show_overlay": true
  }
}

IMPORTANT:
- Replace YOUR_GROQ_API_KEY_HERE with your actual API key
- Use the SAME key for both "transcription" and "llm" if using Groq
- Keys will be encrypted automatically on first run

================================================================================

HOW IT WORKS
------------

1. You press the hotkey (Ctrl+Shift+Space)
2. App records your voice
3. Audio is sent to transcription API (Groq/OpenAI/Deepgram)
4. Text is cleaned by AI LLM (removes "um", "uh", adds punctuation)
5. Result is pasted into your active app

SPEED: ~2-3 seconds total (with Groq)

================================================================================

SUPPORTED PROVIDERS
-------------------

TRANSCRIPTION:
- Groq Whisper (RECOMMENDED - Free, Fast: ~2s)
- OpenAI Whisper (Paid: $0.006/min, Slower: ~5s)
- Deepgram (Paid: $0.0043/min, Medium: ~3s)

LLM POST-PROCESSING:
- Groq Llama (RECOMMENDED - Free, Fast: ~0.4s)
- OpenAI GPT-4o-mini (Paid, Slower: ~3s)
- Ollama (Free, Local - requires installation)

BEST COMBO: Groq + Groq = ~2.5s total (FREE!)

================================================================================

CUSTOMIZATION
-------------

Change Hotkey:
- Edit "modifiers" and "key" in config.json
- Options: ctrl, shift, alt, win + any key
- Example: ["ctrl", "alt"] + "d" = Ctrl+Alt+D

Change Language:
- Set "language": "it" for Italian
- Set "language": "en" for English
- Set "language": "auto" for auto-detect

Disable Auto-Paste:
- Set "auto_paste": false
- Text will only be copied to clipboard (Ctrl+V to paste manually)

================================================================================

TROUBLESHOOTING
---------------

"Hotkey not working"
→ Run as Administrator (right-click exe → Run as administrator)
→ Check no other app is using the same hotkey

"No audio detected"
→ Check microphone permissions in Windows Settings
→ Try speaking louder or closer to mic

"API error" or "Invalid API key"
→ Double-check API key in config.json
→ Verify you have credits (for OpenAI/Deepgram)
→ Check internet connection

"Text not pasting"
→ Enable "auto_paste": true in config
→ Manually press Ctrl+V (text is always in clipboard)

"App crashes on startup"
→ Check config.json is valid JSON (use https://jsonlint.com)
→ Install Visual C++ Redistributable:
  https://aka.ms/vs/17/release/vc_redist.x64.exe

================================================================================

REQUIREMENTS
------------

- Windows 10/11 (64-bit)
- Microphone
- Internet connection (for cloud APIs)
- API key (Groq recommended - free)

================================================================================

PRIVACY & SECURITY
------------------

- Audio is sent to cloud API (Groq/OpenAI/Deepgram)
- NOT stored permanently on their servers (check provider ToS)
- API keys encrypted locally with Windows DPAPI
- No telemetry or tracking from this app

For maximum privacy: Use Ollama (local, no cloud)

================================================================================

SUPPORT
-------

Issues & Questions:
https://github.com/albertocabasvidani/voice-dictation-mvp/issues

Documentation:
https://github.com/albertocabasvidani/voice-dictation-mvp

================================================================================

LICENSE
-------

MIT License - Free for personal and commercial use

Built with Claude Code (https://claude.ai/code)

================================================================================
