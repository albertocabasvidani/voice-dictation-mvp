"""
Voice Dictation MVP - Main Entry Point

Usage:
    python src/main.py
"""

import os
import sys
import threading
import time

from src.core.config_manager import ConfigManager
from src.core.audio_recorder import AudioRecorder
from src.core.hotkey_manager import HotkeyManager
from src.core.text_processor import TextProcessor
from src.ui.system_tray import SystemTray
from src.ui.settings_window import SettingsWindow


class VoiceDictationApp:
    """Main application controller"""

    def __init__(self):
        print("Starting Voice Dictation MVP...")
        print(f"Working directory: {os.getcwd()}")

        self.config_manager = ConfigManager()
        print(f"Config path: {self.config_manager.config_path}")

        self.config = self.config_manager.load()

        # Check if using template (no API keys configured)
        trans_key = self.config_manager.get_transcription_api_key()
        llm_provider = self.config.get('llm', {}).get('provider', '')
        llm_key = self.config_manager.get_llm_api_key()

        # Ollama doesn't need API key
        llm_needs_key = llm_provider not in ['ollama']

        if not trans_key or (llm_needs_key and not llm_key):
            print("\n" + "!"*60)
            print("WARNING: No API keys configured!")
            print("!"*60)
            print("\nYou need to create a config file with your API keys.")
            print(f"Location: {self.config_manager.config_path}")
            print("\nSee README_USER.txt for instructions.")
            print("\nPress Enter to continue anyway (will fail on first use)...")
            try:
                input()
            except:
                pass

        self.audio_recorder = None
        self.hotkey_manager = None
        self.text_processor = None
        self.system_tray = None

        self.is_running = False
        self.is_recording = False
        self.recording_thread = None

        self._initialize()

    def _initialize(self):
        """Initialize all components"""
        print("Initializing Voice Dictation MVP...")

        try:
            # Audio recorder
            print("- Loading audio recorder...")
            audio_config = self.config.get('audio', {})
            self.audio_recorder = AudioRecorder(
                sample_rate=audio_config.get('sample_rate', 16000),
                device_index=audio_config.get('device_index', -1)
            )
            print("  [OK] Audio recorder loaded")

            # Text processor
            print("- Loading text processor...")
            self.text_processor = TextProcessor(self.config)
            print("  [OK] Text processor loaded")

            # Hotkey manager
            print("- Loading hotkey manager...")
            self.hotkey_manager = HotkeyManager()
            self._register_hotkey()
            print("  [OK] Hotkey manager loaded")

            # System tray
            print("- Loading system tray...")
            self.system_tray = SystemTray(
                on_settings=self._show_settings,
                on_exit=self._exit
            )
            print("  [OK] System tray loaded")

            self.is_running = True
            print("\n[OK] Initialization complete!\n")

        except Exception as e:
            print(f"\n[ERROR] Initialization failed at: {e}")
            raise

    def _register_hotkey(self):
        """Register global hotkey"""
        hotkey_config = self.config.get('hotkey', {})
        modifiers = hotkey_config.get('modifiers', ['ctrl', 'shift'])
        key = hotkey_config.get('key', 'space')

        try:
            self.hotkey_manager.register(modifiers, key, self._toggle_recording)
            print(f"Hotkey registered: {'+'.join(modifiers + [key])}")
        except Exception as e:
            print(f"Failed to register hotkey: {e}")
            print("Make sure to run as administrator on Windows")

    def _toggle_recording(self):
        """Toggle recording on/off"""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return

        print("\n=== Recording started ===")
        self.is_recording = True
        self.system_tray.set_recording(True)
        self.system_tray.set_status("Recording...")

        self.audio_recorder.start_recording()

        # Start recording thread
        self.recording_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.recording_thread.start()

    def _record_loop(self):
        """Record audio in loop until stopped"""
        while self.is_recording:
            try:
                self.audio_recorder.record_chunk(duration=0.1)
            except Exception as e:
                print(f"Recording error: {e}")
                break

    def _stop_recording(self):
        """Stop recording and process audio"""
        if not self.is_recording:
            return

        print("Recording stopped, processing...")
        self.is_recording = False
        self.system_tray.set_recording(False)

        # Wait for recording thread
        if self.recording_thread:
            self.recording_thread.join(timeout=1)

        try:
            # Get audio data
            audio_data = self.audio_recorder.stop_recording()

            # Process in separate thread to not block
            processing_thread = threading.Thread(
                target=self._process_audio,
                args=(audio_data,),
                daemon=True
            )
            processing_thread.start()

        except Exception as e:
            print(f"Error: {e}")
            self.system_tray.set_status("Error!")
            self.system_tray.notify("Error", str(e))

    def _process_audio(self, audio_data: bytes):
        """Process audio data through pipeline"""
        try:
            def status_callback(status: str):
                self.system_tray.set_status(status)

            # Process
            result_text = self.text_processor.process_audio(audio_data, status_callback)

            # Success
            self.system_tray.set_status("Ready")
            self.system_tray.notify("Success", f"Inserted: {result_text[:50]}...")

        except Exception as e:
            print(f"Processing error: {e}")
            self.system_tray.set_status("Error!")
            self.system_tray.notify("Error", str(e))

    def _show_settings(self):
        """Show settings window"""
        def on_save(new_config):
            self.config = new_config

            # Reload text processor with new config
            self.text_processor.reload_config(new_config)

            # Re-register hotkey
            self.hotkey_manager.unregister_all()
            self._register_hotkey()

            print("Configuration reloaded")

        settings = SettingsWindow(self.config, self.config_manager, on_save=on_save)
        settings.show()

    def _exit(self):
        """Exit application"""
        print("\nShutting down...")
        self.is_running = False

        if self.hotkey_manager:
            self.hotkey_manager.unregister_all()

        sys.exit(0)

    def run(self):
        """Run the application"""
        print("\n" + "="*50)
        print("Voice Dictation MVP")
        print("="*50)
        print(f"Hotkey: {'+'.join(self.config['hotkey']['modifiers'] + [self.config['hotkey']['key']])}")
        print(f"Transcription: {self.config['transcription']['provider']}")
        print(f"LLM: {self.config['llm']['provider']} ({self.config['llm']['model']})")
        print("\nPress hotkey to start/stop recording")
        print("Right-click system tray icon for settings")
        print("="*50 + "\n")

        # Run system tray (blocking)
        self.system_tray.start()


def main():
    """Main entry point"""
    try:
        app = VoiceDictationApp()
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n{'='*60}")
        print("FATAL ERROR")
        print('='*60)
        print(f"Error: {e}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        print('='*60)
        print("\nPress Enter to exit...")
        try:
            input()
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
