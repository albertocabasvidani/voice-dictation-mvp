"""
Voice Dictation MVP - Main Entry Point

Usage:
    python src/main.py
"""

import sys
import threading
import time

from core.config_manager import ConfigManager
from core.audio_recorder import AudioRecorder
from core.hotkey_manager import HotkeyManager
from core.text_processor import TextProcessor
from ui.system_tray import SystemTray
from ui.settings_window import SettingsWindow


class VoiceDictationApp:
    """Main application controller"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load()

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

        # Audio recorder
        audio_config = self.config.get('audio', {})
        self.audio_recorder = AudioRecorder(
            sample_rate=audio_config.get('sample_rate', 16000),
            device_index=audio_config.get('device_index', -1)
        )

        # Text processor
        self.text_processor = TextProcessor(self.config)

        # Hotkey manager
        self.hotkey_manager = HotkeyManager()
        self._register_hotkey()

        # System tray
        self.system_tray = SystemTray(
            on_settings=self._show_settings,
            on_exit=self._exit
        )

        self.is_running = True
        print("Initialization complete!")

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
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
