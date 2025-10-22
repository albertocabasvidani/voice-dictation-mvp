import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from typing import Callable


class SettingsWindow:
    """Settings window for configuration"""

    LLM_MODELS = {
        'ollama': ['llama3.2:3b', 'gemma2:2b', 'mistral:7b', 'llama3.1:8b'],
        'openai': ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo'],
        'groq': ['llama-3.1-8b-instant', 'mixtral-8x7b-32768', 'gemma2-9b-it']
    }

    def __init__(self, config: dict, config_manager, on_save: Callable = None):
        self.config = config.copy()
        self.config_manager = config_manager
        self.on_save = on_save
        self.window = None

    def show(self):
        """Show settings window"""
        if self.window:
            self.window.lift()
            return

        self.window = tk.Tk()
        self.window.title("Voice Dictation Settings")
        self.window.geometry("600x500")

        # Create notebook (tabs)
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self._create_hotkey_tab(notebook)
        self._create_audio_tab(notebook)
        self._create_transcription_tab(notebook)
        self._create_llm_tab(notebook)
        self._create_advanced_tab(notebook)

        # Buttons frame
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(btn_frame, text="Save", command=self._save, width=15).pack(side='right', padx=5)
        tk.Button(btn_frame, text="Cancel", command=self._cancel, width=15).pack(side='right')

        self.window.protocol("WM_DELETE_WINDOW", self._cancel)
        self.window.mainloop()

    def _create_hotkey_tab(self, notebook):
        """Create hotkey configuration tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Hotkey")

        tk.Label(frame, text="Hotkey Configuration", font=('Arial', 12, 'bold')).pack(pady=10)

        # Current hotkey
        hotkey_config = self.config.get('hotkey', {})
        modifiers = hotkey_config.get('modifiers', ['ctrl', 'shift'])
        key = hotkey_config.get('key', 'space')
        current_hotkey = '+'.join(modifiers + [key])

        tk.Label(frame, text=f"Current hotkey: {current_hotkey}").pack(pady=5)

        # Hotkey entry
        tk.Label(frame, text="Press new hotkey combination:").pack(pady=5)
        self.hotkey_entry = tk.Entry(frame, width=30)
        self.hotkey_entry.pack(pady=5)
        self.hotkey_entry.insert(0, current_hotkey)

        tk.Label(
            frame,
            text="Example: ctrl+shift+space\nSupported modifiers: ctrl, shift, alt, win",
            fg="gray"
        ).pack(pady=10)

    def _create_audio_tab(self, notebook):
        """Create audio configuration tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Audio")

        tk.Label(frame, text="Audio Configuration", font=('Arial', 12, 'bold')).pack(pady=10)

        # Audio device selection
        tk.Label(frame, text="Microphone Device:").pack(anchor='w', padx=20, pady=(10, 0))

        # Get available audio devices
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            input_devices = [(i, dev['name']) for i, dev in enumerate(devices) if dev['max_input_channels'] > 0]
            device_names = [f"{i}: {name}" for i, name in input_devices]
            default_device = sd.default.device[0]
        except:
            device_names = ["Default Device"]
            default_device = -1

        self.device_var = tk.StringVar()
        current_device = self.config.get('audio', {}).get('device_index', -1)
        if current_device == -1:
            self.device_var.set(f"{default_device}: Default Device")
        else:
            matching = [name for name in device_names if name.startswith(f"{current_device}:")]
            if matching:
                self.device_var.set(matching[0])
            else:
                self.device_var.set(device_names[0] if device_names else "Default Device")

        device_combo = ttk.Combobox(frame, textvariable=self.device_var, width=47, state='readonly')
        device_combo['values'] = device_names
        device_combo.pack(padx=20, pady=5)

        # Volume gain control
        tk.Label(frame, text="Volume Amplification:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(20, 5))
        tk.Label(
            frame,
            text="Increase if your microphone is too quiet (not recommended for normal mics)",
            fg="gray",
            font=('Arial', 8)
        ).pack(anchor='w', padx=20)

        # Gain slider
        gain_frame = tk.Frame(frame)
        gain_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(gain_frame, text="1x").pack(side='left')

        current_gain = self.config.get('audio', {}).get('volume_gain', 1000)
        self.gain_var = tk.IntVar(value=current_gain)

        self.gain_slider = tk.Scale(
            gain_frame,
            from_=1,
            to=100000,
            orient='horizontal',
            variable=self.gain_var,
            command=self._update_gain_label,
            length=300
        )
        self.gain_slider.pack(side='left', padx=10)

        tk.Label(gain_frame, text="100000x").pack(side='left')

        # Current gain label
        self.gain_label = tk.Label(frame, text=f"Current: {current_gain}x", font=('Arial', 10, 'bold'))
        self.gain_label.pack(pady=5)

        tk.Label(
            frame,
            text="Note: Higher values amplify weak signals but also amplify noise.\nFor best results, increase Windows microphone level first.",
            fg="gray",
            font=('Arial', 8),
            justify='center'
        ).pack(pady=10)

    def _update_gain_label(self, value):
        """Update gain label when slider moves"""
        self.gain_label.config(text=f"Current: {value}x")

    def _create_transcription_tab(self, notebook):
        """Create transcription provider configuration tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Transcription")

        tk.Label(frame, text="Transcription Provider", font=('Arial', 12, 'bold')).pack(pady=10)

        # Provider selection
        tk.Label(frame, text="Provider:").pack(anchor='w', padx=20)
        self.trans_provider_var = tk.StringVar(value=self.config.get('transcription', {}).get('provider', 'groq'))
        providers_frame = tk.Frame(frame)
        providers_frame.pack(fill='x', padx=20, pady=5)

        tk.Radiobutton(providers_frame, text="Groq (Free, Fast)", variable=self.trans_provider_var, value='groq').pack(anchor='w')
        tk.Radiobutton(providers_frame, text="OpenAI ($0.006/min)", variable=self.trans_provider_var, value='openai').pack(anchor='w')
        tk.Radiobutton(providers_frame, text="Deepgram ($0.0043/min)", variable=self.trans_provider_var, value='deepgram').pack(anchor='w')

        # API Key
        tk.Label(frame, text="API Key:").pack(anchor='w', padx=20, pady=(10, 0))
        self.trans_api_key_entry = tk.Entry(frame, width=50, show='*')
        self.trans_api_key_entry.pack(padx=20, pady=5)

        # Try to get current API key
        current_key = self.config_manager.get_transcription_api_key()
        if current_key:
            self.trans_api_key_entry.insert(0, current_key)

        # Test button
        tk.Button(frame, text="Test Connection", command=self._test_transcription).pack(pady=10)

    def _create_llm_tab(self, notebook):
        """Create LLM provider configuration tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="LLM")

        tk.Label(frame, text="LLM Post-Processing", font=('Arial', 12, 'bold')).pack(pady=10)

        # Provider selection
        tk.Label(frame, text="Provider:").pack(anchor='w', padx=20)
        self.llm_provider_var = tk.StringVar(value=self.config.get('llm', {}).get('provider', 'groq'))
        self.llm_provider_var.trace('w', self._on_llm_provider_change)

        providers_frame = tk.Frame(frame)
        providers_frame.pack(fill='x', padx=20, pady=5)

        tk.Radiobutton(providers_frame, text="Ollama (Local, Free)", variable=self.llm_provider_var, value='ollama').pack(anchor='w')
        tk.Radiobutton(providers_frame, text="OpenAI (Cloud)", variable=self.llm_provider_var, value='openai').pack(anchor='w')
        tk.Radiobutton(providers_frame, text="Groq (Cloud, Free)", variable=self.llm_provider_var, value='groq').pack(anchor='w')

        # Model selection
        tk.Label(frame, text="Model:").pack(anchor='w', padx=20, pady=(10, 0))
        self.llm_model_var = tk.StringVar(value=self.config.get('llm', {}).get('model', 'llama-3.1-8b-instant'))
        self.llm_model_combo = ttk.Combobox(frame, textvariable=self.llm_model_var, width=47, state='readonly')
        self.llm_model_combo.pack(padx=20, pady=5)
        self._update_llm_models()

        # API Key (hidden for Ollama)
        self.llm_api_key_label = tk.Label(frame, text="API Key:")
        self.llm_api_key_entry = tk.Entry(frame, width=50, show='*')

        current_llm_key = self.config_manager.get_llm_api_key()
        if current_llm_key:
            self.llm_api_key_entry.insert(0, current_llm_key)

        # Ollama URL (only for Ollama)
        self.ollama_url_label = tk.Label(frame, text="Ollama URL:")
        self.ollama_url_entry = tk.Entry(frame, width=50)
        self.ollama_url_entry.insert(0, self.config.get('llm', {}).get('ollama_url', 'http://localhost:11434'))

        self._on_llm_provider_change()

        # Test button
        tk.Button(frame, text="Test Connection", command=self._test_llm).pack(pady=10)

    def _create_advanced_tab(self, notebook):
        """Create advanced settings tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Advanced")

        tk.Label(frame, text="Advanced Settings", font=('Arial', 12, 'bold')).pack(pady=10)

        # Auto-paste
        self.auto_paste_var = tk.BooleanVar(value=self.config.get('behavior', {}).get('auto_paste', True))
        tk.Checkbutton(
            frame,
            text="Auto-paste text (Ctrl+V) after processing",
            variable=self.auto_paste_var
        ).pack(anchor='w', padx=20, pady=10)

        # Language
        tk.Label(frame, text="Transcription Language:").pack(anchor='w', padx=20, pady=(10, 0))
        self.language_var = tk.StringVar(value=self.config.get('transcription', {}).get('options', {}).get('language', 'auto'))
        language_combo = ttk.Combobox(frame, textvariable=self.language_var, width=47, state='readonly')
        language_combo['values'] = ['auto', 'it', 'en', 'es', 'fr', 'de']
        language_combo.pack(padx=20, pady=5)

    def _on_llm_provider_change(self, *args):
        """Handle LLM provider change"""
        provider = self.llm_provider_var.get()

        # Update model list
        self._update_llm_models()

        # Show/hide API key and Ollama URL based on provider
        if provider == 'ollama':
            self.llm_api_key_label.pack_forget()
            self.llm_api_key_entry.pack_forget()
            self.ollama_url_label.pack(anchor='w', padx=20, pady=(10, 0))
            self.ollama_url_entry.pack(padx=20, pady=5)
        else:
            self.ollama_url_label.pack_forget()
            self.ollama_url_entry.pack_forget()
            self.llm_api_key_label.pack(anchor='w', padx=20, pady=(10, 0))
            self.llm_api_key_entry.pack(padx=20, pady=5)

    def _update_llm_models(self):
        """Update LLM model list based on selected provider"""
        provider = self.llm_provider_var.get()

        if provider == 'ollama':
            # Try to get models from Ollama
            models = self._get_ollama_models()
            if not models:
                models = self.LLM_MODELS['ollama']
        else:
            models = self.LLM_MODELS.get(provider, [])

        self.llm_model_combo['values'] = models

        # Set current model if in list
        current_model = self.llm_model_var.get()
        if current_model not in models and models:
            self.llm_model_var.set(models[0])

    def _get_ollama_models(self) -> list:
        """Get list of installed Ollama models"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
        except:
            pass
        return []

    def _test_transcription(self):
        """Test transcription API connection"""
        messagebox.showinfo("Test", "Transcription test not implemented in settings window.\nTest will occur during actual use.")

    def _test_llm(self):
        """Test LLM API connection"""
        messagebox.showinfo("Test", "LLM test not implemented in settings window.\nTest will occur during actual use.")

    def _save(self):
        """Save configuration"""
        # Update config from UI
        # Hotkey
        hotkey_str = self.hotkey_entry.get().strip().lower()
        parts = hotkey_str.split('+')
        if len(parts) > 1:
            self.config['hotkey'] = {
                'modifiers': parts[:-1],
                'key': parts[-1]
            }
        else:
            self.config['hotkey'] = {
                'modifiers': [],
                'key': parts[0]
            }

        # Transcription
        self.config['transcription']['provider'] = self.trans_provider_var.get()
        trans_api_key = self.trans_api_key_entry.get().strip()
        if trans_api_key:
            self.config_manager.config = self.config
            self.config_manager.set_transcription_api_key(trans_api_key)
            self.config = self.config_manager.config

        # LLM
        self.config['llm']['provider'] = self.llm_provider_var.get()
        self.config['llm']['model'] = self.llm_model_var.get()
        self.config['llm']['ollama_url'] = self.ollama_url_entry.get().strip()

        llm_api_key = self.llm_api_key_entry.get().strip()
        if llm_api_key:
            self.config_manager.config = self.config
            self.config_manager.set_llm_api_key(llm_api_key)
            self.config = self.config_manager.config

        # Audio
        device_str = self.device_var.get()
        try:
            device_index = int(device_str.split(':')[0])
            self.config['audio']['device_index'] = device_index
        except:
            self.config['audio']['device_index'] = -1
        self.config['audio']['volume_gain'] = self.gain_var.get()

        # Advanced
        self.config['behavior']['auto_paste'] = self.auto_paste_var.get()
        self.config['transcription']['options']['language'] = self.language_var.get()

        # Save to file
        self.config_manager.save(self.config)

        # Callback
        if self.on_save:
            self.on_save(self.config)

        messagebox.showinfo("Success", "Settings saved successfully!")
        self._cancel()

    def _cancel(self):
        """Cancel and close window"""
        if self.window:
            self.window.destroy()
            self.window = None
