import tkinter as tk
import threading


class RecordingWidget:
    """Small widget shown during recording"""

    def __init__(self):
        self.window = None
        self.is_visible = False
        self.animation_id = None
        self.dot_count = 0

    def show(self):
        """Show recording widget"""
        if self.window:
            return

        def create_window():
            self.window = tk.Tk()
            self.window.title("Recording")
            self.window.attributes('-topmost', True)
            self.window.overrideredirect(True)  # Remove window decorations

            # Small window in top-right corner
            window_width = 250
            window_height = 80
            screen_width = self.window.winfo_screenwidth()
            x = screen_width - window_width - 20
            y = 20
            self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

            # Semi-transparent background
            self.window.configure(bg='#1a1a1a')
            self.window.attributes('-alpha', 0.9)

            # Create content frame
            frame = tk.Frame(self.window, bg='#1a1a1a', padx=20, pady=15)
            frame.pack(fill='both', expand=True)

            # Recording indicator (red circle)
            canvas = tk.Canvas(frame, width=20, height=20, bg='#1a1a1a', highlightthickness=0)
            canvas.pack(side='left', padx=(0, 10))
            canvas.create_oval(2, 2, 18, 18, fill='red', outline='')

            # Text label
            text_frame = tk.Frame(frame, bg='#1a1a1a')
            text_frame.pack(side='left', fill='both', expand=True)

            tk.Label(
                text_frame,
                text="Recording",
                font=('Arial', 14, 'bold'),
                fg='white',
                bg='#1a1a1a'
            ).pack(anchor='w')

            self.status_label = tk.Label(
                text_frame,
                text="Press ESC to cancel",
                font=('Arial', 9),
                fg='#888888',
                bg='#1a1a1a'
            )
            self.status_label.pack(anchor='w')

            self.is_visible = True
            self._animate()
            self.window.mainloop()

        # Create window in separate thread
        thread = threading.Thread(target=create_window, daemon=True)
        thread.start()

    def _animate(self):
        """Animate the status text with dots"""
        if not self.is_visible or not self.window:
            return

        try:
            self.dot_count = (self.dot_count + 1) % 4
            dots = '.' * self.dot_count
            self.status_label.config(text=f"Press ESC to cancel{dots}   ")

            # Schedule next animation frame
            self.animation_id = self.window.after(500, self._animate)
        except:
            pass

    def update_status(self, status: str):
        """Update status text"""
        if self.window and self.status_label:
            try:
                self.status_label.config(text=status)
            except:
                pass

    def hide(self):
        """Hide recording widget"""
        self.is_visible = False

        if self.animation_id and self.window:
            try:
                self.window.after_cancel(self.animation_id)
            except:
                pass

        if self.window:
            try:
                self.window.quit()
                self.window.destroy()
            except:
                pass
            self.window = None
