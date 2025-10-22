# Building Windows Executable

## Prerequisites

- Windows 10/11 64-bit
- Python 3.11+ installed
- All dependencies from `requirements.txt`

## Build Steps

### Option 1: Using Batch Script (Recommended)

1. Open Command Prompt in project directory
2. Run the build script:
   ```cmd
   build_exe.bat
   ```

3. Wait for build to complete (~2-3 minutes)
4. Executable will be in `dist/VoiceDictation.exe`

### Option 2: Manual Build

1. Install PyInstaller:
   ```cmd
   pip install pyinstaller
   ```

2. Clean previous builds:
   ```cmd
   rmdir /s /q build dist
   ```

3. Build with spec file:
   ```cmd
   pyinstaller VoiceDictation.spec
   ```

4. Or build without spec file (one-file):
   ```cmd
   pyinstaller --onefile --windowed --name VoiceDictation src/main.py
   ```

## Output

- **Executable**: `dist/VoiceDictation.exe` (~50-80 MB)
- **Console mode**: Shows debug output (useful for troubleshooting)

## Customization

### Remove Console Window

Edit `VoiceDictation.spec` and change:
```python
console=True,  # Set to False for no console window
```
to:
```python
console=False,  # No console window (windowed mode)
```

Then rebuild.

### Add Icon

1. Create or download a `.ico` file (256x256 recommended)
2. Edit `VoiceDictation.spec`:
   ```python
   icon='path/to/your/icon.ico',
   ```

### Reduce Size

Use UPX compression (already enabled in spec):
- Download UPX: https://upx.github.io/
- Extract to PATH or same directory as PyInstaller
- Rebuild - size should reduce by ~30-40%

## Distribution

### Standalone Distribution

The executable in `dist/` is standalone and includes:
- ✓ Python runtime
- ✓ All dependencies
- ✓ Config template

**What users need:**
1. Copy `VoiceDictation.exe` to their PC
2. Create `config.json` with API keys (see below)
3. Run the exe

### Full Distribution Package

Create a zip with:
```
VoiceDictation/
├── VoiceDictation.exe
├── config/
│   └── config.template.json
└── README_USER.txt
```

## Configuration for End Users

Users must create `config/config.json` in the same directory as the exe:

```json
{
  "version": "1.0",
  "hotkey": {
    "modifiers": ["ctrl", "shift"],
    "key": "space"
  },
  "transcription": {
    "provider": "groq",
    "api_key_encrypted": "",
    "options": {
      "language": "auto"
    }
  },
  "llm": {
    "provider": "groq",
    "api_key_encrypted": "",
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
```

**Important:** API keys will be encrypted automatically on first run using Windows DPAPI.

## Troubleshooting

### Build Errors

**"Module not found"**
- Install all requirements: `pip install -r requirements.txt`

**"Failed to execute script"**
- Run in console mode first to see errors
- Check `console=True` in spec file

**"Import Error: DLL load failed"**
- Install Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

### Runtime Errors

**"Hotkey not working"**
- Run as Administrator (required for global hotkeys)

**"Audio device not found"**
- Check microphone permissions in Windows Settings
- Try different device_index in config

**"API errors"**
- Verify API keys are correct
- Check internet connection
- Test with `test_openai_debug.py` first

## Security Notes

- API keys are encrypted with Windows DPAPI (user-specific)
- Encrypted keys cannot be used on different PC/user
- Keep `config.json` secure (contains encrypted secrets)
- Don't distribute exe with your API keys!

## Advanced: Cross-Compilation

**Note:** Building on WSL/Linux for Windows has limitations.

If building from Linux/WSL:
1. Install Wine: `sudo apt install wine64`
2. Install Python for Wine
3. Use PyInstaller with Wine (not recommended)

**Recommended:** Build on native Windows for best compatibility.
