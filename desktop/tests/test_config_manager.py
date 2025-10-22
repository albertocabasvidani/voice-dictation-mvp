import pytest
import os
import tempfile
from src.core.config_manager import ConfigManager


def test_load_default_config():
    """Test loading default configuration"""
    config_manager = ConfigManager()
    config = config_manager.load()

    assert 'version' in config
    assert 'hotkey' in config
    assert 'transcription' in config
    assert 'llm' in config


def test_save_and_load_config():
    """Test saving and loading configuration"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    try:
        config_manager = ConfigManager(temp_path)
        config = config_manager.load()

        # Modify config
        config['transcription']['provider'] = 'openai'
        config_manager.save(config)

        # Load again
        config_manager2 = ConfigManager(temp_path)
        config2 = config_manager2.load()

        assert config2['transcription']['provider'] == 'openai'

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_api_key_encryption():
    """Test API key encryption/decryption"""
    config_manager = ConfigManager()

    api_key = "test_api_key_12345"

    # Encrypt
    encrypted = config_manager.encrypt_api_key(api_key)
    assert encrypted != api_key

    # Decrypt
    decrypted = config_manager.decrypt_api_key(encrypted)
    assert decrypted == api_key
