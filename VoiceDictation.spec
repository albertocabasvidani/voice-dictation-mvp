# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/config.template.json', 'config'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'src',
        'src.core',
        'src.core.config_manager',
        'src.core.audio_recorder',
        'src.core.hotkey_manager',
        'src.core.text_processor',
        'src.providers',
        'src.providers.transcription',
        'src.providers.transcription.base',
        'src.providers.transcription.groq_whisper',
        'src.providers.transcription.openai_whisper',
        'src.providers.transcription.deepgram',
        'src.providers.llm',
        'src.providers.llm.base',
        'src.providers.llm.ollama',
        'src.providers.llm.openai_llm',
        'src.providers.llm.groq_llm',
        'src.ui',
        'src.ui.system_tray',
        'src.ui.settings_window',
        # UI libraries
        'pystray',
        'pystray._win32',
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'tkinter',
        'tkinter.ttk',
        # Audio libraries
        'sounddevice',
        '_sounddevice',
        'sounddevice._sounddevice',
        'cffi',
        'soundfile',
        # Scientific libraries (scipy removed - manual WAV writing)
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        # Input libraries
        'keyboard',
        'keyboard._winreg',
        'keyboard._keyboard',
        'pynput',
        'pynput.keyboard',
        'pynput.keyboard._win32',
        'pyperclip',
        'pyautogui',
        # Network
        'requests',
        'urllib3',
        'charset_normalizer',
        'idna',
        'certifi',
        # Windows
        'win32crypt',
        'win32api',
        'win32con',
        'pywintypes',
        'win32timezone',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'notebook',
        'IPython',
        'pytest',
        'scipy',  # Not needed - manual WAV writing
        'torch',  # Accidentally imported by some libraries
        'tensorflow',
        'tensorboard',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VoiceDictation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
