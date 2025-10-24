import keyboard
from typing import Callable, List


class HotkeyManager:
    """Manages global hotkey registration"""

    def __init__(self):
        self.registered_hotkeys = []

    def register(self, modifiers: List[str], key: str, callback: Callable):
        """
        Register a global hotkey

        Args:
            modifiers: List of modifier keys (e.g., ['ctrl', 'shift'])
            key: Main key (e.g., 'space')
            callback: Function to call when hotkey is pressed
        """
        # Build hotkey string (e.g., "ctrl+shift+space")
        hotkey_str = '+'.join(modifiers + [key]).lower()

        try:
            print(f"[HotkeyManager] Registering: {hotkey_str}")
            keyboard.add_hotkey(hotkey_str, callback, suppress=False)
            self.registered_hotkeys.append(hotkey_str)
            print(f"[HotkeyManager] ✓ Registered: {hotkey_str}")
        except Exception as e:
            print(f"[HotkeyManager] ✗ Failed to register '{hotkey_str}': {str(e)}")
            raise Exception(f"Failed to register hotkey '{hotkey_str}': {str(e)}")

    def unregister_all(self):
        """Unregister all registered hotkeys"""
        print(f"[HotkeyManager] Unregistering {len(self.registered_hotkeys)} hotkeys...")
        for hotkey_str in self.registered_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey_str)
                print(f"[HotkeyManager] ✓ Unregistered: {hotkey_str}")
            except Exception as e:
                print(f"[HotkeyManager] ✗ Failed to unregister '{hotkey_str}': {e}")
        self.registered_hotkeys.clear()
        print(f"[HotkeyManager] All hotkeys cleared")

    def is_pressed(self, key: str) -> bool:
        """Check if a key is currently pressed"""
        return keyboard.is_pressed(key)

    @staticmethod
    def wait_for_hotkey() -> str:
        """Wait for user to press a key combination and return it"""
        print("Press your desired hotkey combination...")
        event = keyboard.read_event(suppress=False)

        if event.event_type == keyboard.KEY_DOWN:
            # Get current modifiers
            modifiers = []
            if keyboard.is_pressed('ctrl'):
                modifiers.append('ctrl')
            if keyboard.is_pressed('shift'):
                modifiers.append('shift')
            if keyboard.is_pressed('alt'):
                modifiers.append('alt')
            if keyboard.is_pressed('win'):
                modifiers.append('win')

            # Build hotkey string
            key = event.name
            if modifiers:
                return '+'.join(modifiers + [key])
            else:
                return key

        return ""
