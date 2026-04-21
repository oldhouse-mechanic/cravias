"""
Cravias - Keyboard Module
Handles keyboard automation, mouse control, screenshots,
and media key commands using pyautogui (X11).
"""

import logging
import time
import subprocess
import shutil

logger = logging.getLogger(__name__)

try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.error("pyautogui not installed. Run: pip install pyautogui")


def _check() -> bool:
    if not PYAUTOGUI_AVAILABLE:
        logger.error("pyautogui unavailable.")
        return False
    return True


class Keyboard:
    def __init__(self):
        if not PYAUTOGUI_AVAILABLE:
            logger.warning("Keyboard module loaded but pyautogui is missing.")

    # ─── Typing ──────────────────────────────────────────────────────────────────

    def type_text(self, text: str) -> str:
        """Type out text at the current cursor position."""
        if not _check():
            return "Keyboard automation is not available."
        if not text:
            return "What would you like me to type?"
        try:
            time.sleep(0.3)  # Small delay so focus settles
            pyautogui.typewrite(text, interval=0.04)
            return f"Typed: {text}"
        except Exception as e:
            logger.error(f"Type error: {e}")
            return "Couldn't type that."

    # ─── Hotkeys ─────────────────────────────────────────────────────────────────

    def press_key(self, key: str) -> str:
        """Press a single key."""
        if not _check():
            return "Keyboard automation is not available."
        try:
            pyautogui.press(key)
            return f"Pressed {key}."
        except Exception as e:
            logger.error(f"Key press error: {e}")
            return f"Couldn't press {key}."

    def hotkey(self, *keys) -> str:
        """Press a key combination e.g. ctrl+c."""
        if not _check():
            return "Keyboard automation is not available."
        try:
            pyautogui.hotkey(*keys)
            return f"Pressed {' + '.join(keys)}."
        except Exception as e:
            logger.error(f"Hotkey error: {e}")
            return "Hotkey failed."

    def copy(self) -> str:
        return self.hotkey('ctrl', 'c')

    def paste(self) -> str:
        return self.hotkey('ctrl', 'v')

    def cut(self) -> str:
        return self.hotkey('ctrl', 'x')

    def undo(self) -> str:
        return self.hotkey('ctrl', 'z')

    def redo(self) -> str:
        return self.hotkey('ctrl', 'y')

    def select_all(self) -> str:
        return self.hotkey('ctrl', 'a')

    def close_window(self) -> str:
        return self.hotkey('alt', 'F4')

    def press_enter(self) -> str:
        return self.press_key('enter')

    def press_escape(self) -> str:
        return self.press_key('escape')

    def press_space(self) -> str:
        return self.press_key('space')

    def press_backspace(self) -> str:
        return self.press_key('backspace')

    def switch_window(self) -> str:
        return self.hotkey('alt', 'tab')

    def new_tab(self) -> str:
        return self.hotkey('ctrl', 't')

    def close_tab(self) -> str:
        return self.hotkey('ctrl', 'w')

    def save(self) -> str:
        return self.hotkey('ctrl', 's')

    def fullscreen(self) -> str:
        return self.press_key('F11')

    # ─── Scrolling ───────────────────────────────────────────────────────────────

    def scroll_up(self, amount: int = 500) -> str:
        if not _check():
            return "Keyboard automation is not available."
        pyautogui.scroll(amount)
        return "Scrolled up."

    def scroll_down(self, amount: int = 500) -> str:
        if not _check():
            return "Keyboard automation is not available."
        pyautogui.scroll(-amount)
        return "Scrolled down."

    def scroll_to_top(self) -> str:
        return self.hotkey('ctrl', 'Home')

    def scroll_to_bottom(self) -> str:
        return self.hotkey('ctrl', 'End')

    # ─── Media Controls ──────────────────────────────────────────────────────────

    def media_play_pause(self) -> str:
        if not _check():
            return "Keyboard automation is not available."
        pyautogui.press('playpause')
        return "Play/pause toggled."

    def media_next(self) -> str:
        if not _check():
            return "Keyboard automation is not available."
        pyautogui.press('nexttrack')
        return "Next track."

    def media_previous(self) -> str:
        if not _check():
            return "Keyboard automation is not available."
        pyautogui.press('prevtrack')
        return "Previous track."

    def media_stop(self) -> str:
        if not _check():
            return "Keyboard automation is not available."
        pyautogui.press('stop')
        return "Media stopped."

    # ─── Screenshot ──────────────────────────────────────────────────────────────

    def screenshot(self) -> str:
        """Take a screenshot and save to ~/Pictures/Screenshots/"""
        if not _check():
            return "Keyboard automation is not available."
        try:
            import os
            from datetime import datetime
            save_dir = os.path.expanduser("~/Pictures/Screenshots")
            os.makedirs(save_dir, exist_ok=True)
            filename = f"cravias_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path = os.path.join(save_dir, filename)
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            return f"Screenshot saved to {path}"
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            # Fallback to scrot
            if shutil.which("scrot"):
                subprocess.run(["scrot", "-d", "1"])
                return "Screenshot taken with scrot."
            return "Screenshot failed."
