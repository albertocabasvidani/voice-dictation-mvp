import json
import os
import base64
from pathlib import Path

try:
    import win32crypt
    DPAPI_AVAILABLE = True
except ImportError:
    DPAPI_AVAILABLE = False


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
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            # Try loading from project config folder
            project_config = os.path.join('config', 'config.json')
            if os.path.exists(project_config):
                with open(project_config, 'r') as f:
                    self.config = json.load(f)
            else:
                # Load template
                template_path = os.path.join('config', 'config.template.json')
                if os.path.exists(template_path):
                    with open(template_path, 'r') as f:
                        self.config = json.load(f)
                else:
                    self.config = self._get_default_config()
        else:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

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
