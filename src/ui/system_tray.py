import pystray
from PIL import Image, ImageDraw
from typing import Callable


class SystemTray:
    """System tray icon with menu"""

    def __init__(
        self,
        on_settings: Callable = None,
        on_exit: Callable = None
    ):
        self.on_settings = on_settings
        self.on_exit = on_exit
        self.icon = None
        self.is_recording = False

    def create_icon(self, color: str = "green") -> Image.Image:
        """Create a simple colored circle icon"""
        size = 64
        image = Image.new('RGB', (size, size), color="white")
        draw = ImageDraw.Draw(image)

        # Draw filled circle
        margin = 8
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color,
            outline="black",
            width=2
        )

        return image

    def create_menu(self):
        """Create system tray menu"""
        return pystray.Menu(
            pystray.MenuItem(
                "Settings",
                lambda: self.on_settings() if self.on_settings else None
            ),
            pystray.MenuItem(
                "Exit",
                lambda: self.stop()
            )
        )

    def start(self):
        """Start system tray icon"""
        self.icon = pystray.Icon(
            "voice_dictation",
            self.create_icon("green"),
            "Voice Dictation",
            self.create_menu()
        )

        # Run in blocking mode
        self.icon.run()

    def stop(self):
        """Stop system tray icon"""
        if self.on_exit:
            self.on_exit()

        if self.icon:
            self.icon.stop()

    def set_recording(self, recording: bool):
        """Change icon color based on recording state"""
        self.is_recording = recording

        if self.icon:
            color = "red" if recording else "green"
            self.icon.icon = self.create_icon(color)

    def set_status(self, status: str):
        """Update tooltip status"""
        if self.icon:
            self.icon.title = f"Voice Dictation - {status}"

    def notify(self, title: str, message: str):
        """Show notification"""
        if self.icon:
            self.icon.notify(message, title)
