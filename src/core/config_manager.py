import json
import os
import sys
import base64
from pathlib import Path

try:
    import win32crypt
    DPAPI_AVAILABLE = True
except ImportError:
    DPAPI_AVAILABLE = False


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ConfigManager:
    """Manages configuration file with encrypted API keys"""

    DEFAULT_CONFIG_PATH = os.path.join(os.getenv('APPDATA', '.'), 'VoiceDictation', 'config.json')

    def __init__(self, config_path: str = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = {}
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict:
        """Load configuration from file - search order:
        1. Next to executable (config.json)
        2. AppData user folder (default)
        3. Project config folder (development)
        4. Template file
        """
        # 1. Try config.json next to executable (portable mode)
        exe_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
        local_config = os.path.join(exe_dir, 'config.json')

        if os.path.exists(local_config):
            print(f"Loading config from: {local_config}")
            with open(local_config, 'r') as f:
                self.config = json.load(f)
                return self.config

        # 2. Try AppData folder (default Windows location)
        if os.path.exists(self.config_path):
            print(f"Loading config from: {self.config_path}")
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                return self.config

        # 3. Try project config folder (development)
        project_config = os.path.join('config', 'config.json')
        if os.path.exists(project_config):
            print(f"Loading config from: {project_config}")
            with open(project_config, 'r') as f:
                self.config = json.load(f)
                return self.config

        # 4. Load template as fallback
        template_path = get_resource_path(os.path.join('config', 'config.template.json'))
        if os.path.exists(template_path):
            print(f"Loading template from: {template_path}")
            with open(template_path, 'r') as f:
                self.config = json.load(f)
        else:
            # Fallback to hardcoded defaults
            print(f"Warning: Template not found at {template_path}, using defaults")
            self.config = self._get_default_config()

        return self.config

    def save(self, config: dict = None):
        """Save configuration to file"""
        if config:
            self.config = config

        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key using Windows DPAPI"""
        if not DPAPI_AVAILABLE:
            # Fallback: just base64 encode (not secure, but works for testing)
            return base64.b64encode(api_key.encode('utf-8')).decode('ascii')

        try:
            encrypted_bytes = win32crypt.CryptProtectData(
                api_key.encode('utf-8'),
                None, None, None, None, 0
            )
            return base64.b64encode(encrypted_bytes).decode('ascii')
        except Exception as e:
            raise Exception(f"Failed to encrypt API key: {str(e)}")

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key using Windows DPAPI"""
        if not encrypted_key:
            return ""

        if not DPAPI_AVAILABLE:
            # Fallback: just base64 decode
            try:
                return base64.b64decode(encrypted_key).decode('utf-8')
            except:
                return encrypted_key  # Return as-is if not base64

        try:
            encrypted_bytes = base64.b64decode(encrypted_key)
            _, plaintext_bytes = win32crypt.CryptUnprotectData(
                encrypted_bytes, None, None, None, 0
            )
            return plaintext_bytes.decode('utf-8')
        except Exception:
            # If decryption fails, assume it's plaintext (for backward compatibility)
            return encrypted_key

    def get_transcription_api_key(self) -> str:
        """Get decrypted transcription API key"""
        encrypted = self.config.get('transcription', {}).get('api_key_encrypted', '')
        return self.decrypt_api_key(encrypted)

    def get_llm_api_key(self) -> str:
        """Get decrypted LLM API key"""
        encrypted = self.config.get('llm', {}).get('api_key_encrypted', '')
        return self.decrypt_api_key(encrypted)

    def set_transcription_api_key(self, api_key: str):
        """Set and encrypt transcription API key"""
        if 'transcription' not in self.config:
            self.config['transcription'] = {}
        self.config['transcription']['api_key_encrypted'] = self.encrypt_api_key(api_key)

    def set_llm_api_key(self, api_key: str):
        """Set and encrypt LLM API key"""
        if 'llm' not in self.config:
            self.config['llm'] = {}
        self.config['llm']['api_key_encrypted'] = self.encrypt_api_key(api_key)

    def _get_default_config(self) -> dict:
        """Get default configuration"""
        return {
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
                "provider": "ollama",
                "api_key_encrypted": "",
                "model": "llama3.2:3b",
                "ollama_url": "http://localhost:11434",
                "temperature": 0.3,
                "max_tokens": 500
            },
            "audio": {
                "device_index": -1,
                "sample_rate": 16000
            },
            "behavior": {
                "auto_paste": True,
                "show_overlay": True
            }
        }
