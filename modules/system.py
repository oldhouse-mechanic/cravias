"""
Cravias - System Module
Handles OS-level commands: time, date, shutdown, reboot,
app launching, system info, volume control (Linux/ALSA/PulseAudio).
"""

import datetime
import subprocess
import logging
import os
import shutil

logger = logging.getLogger(__name__)


class SystemController:
    def __init__(self, config: dict):
        self.allow_shutdown = config.get("allow_shutdown", True)
        self.allow_reboot = config.get("allow_reboot", True)
        self.browser = config.get("open_browser", "firefox")

    # ─── Time & Date ─────────────────────────────────────────────────────────────

    def get_time(self) -> str:
        now = datetime.datetime.now()
        return f"The time is {now.strftime('%I:%M %p')}."

    def get_date(self) -> str:
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."

    def get_datetime(self) -> str:
        now = datetime.datetime.now()
        return f"It is {now.strftime('%A, %B %d, %Y')} and the time is {now.strftime('%I:%M %p')}."

    # ─── System Info ─────────────────────────────────────────────────────────────

    def get_system_info(self) -> str:
        try:
            import platform
            uname = platform.uname()
            info = (
                f"Running on {uname.system} {uname.release}, "
                f"machine: {uname.machine}, "
                f"processor: {uname.processor or 'unknown'}."
            )
            return info
        except Exception as e:
            logger.error(f"System info error: {e}")
            return "I couldn't retrieve system information."

    def get_battery(self) -> str:
        try:
            import psutil
            batt = psutil.sensors_battery()
            if batt:
                status = "charging" if batt.power_plugged else "discharging"
                return f"Battery is at {int(batt.percent)}% and {status}."
            return "No battery detected. You might be on a desktop."
        except ImportError:
            return "psutil not installed. Can't check battery."
        except Exception as e:
            logger.error(f"Battery check error: {e}")
            return "Couldn't check battery status."

    def get_cpu_ram(self) -> str:
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            return (
                f"CPU usage is at {cpu}%. "
                f"RAM usage is {ram.percent}%, "
                f"using {ram.used // (1024**2)} MB out of {ram.total // (1024**2)} MB."
            )
        except ImportError:
            return "psutil not installed. Can't check CPU or RAM."
        except Exception as e:
            logger.error(f"CPU/RAM error: {e}")
            return "Couldn't retrieve CPU or RAM usage."

    # ─── Volume Control (PulseAudio / ALSA) ─────────────────────────────────────

    def set_volume(self, level: int) -> str:
        """Set system volume. Level 0-100."""
        level = max(0, min(100, level))
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"],
                           capture_output=True)
            return f"Volume set to {level}%."
        elif shutil.which("amixer"):
            subprocess.run(["amixer", "sset", "Master", f"{level}%"],
                           capture_output=True)
            return f"Volume set to {level}%."
        return "Could not adjust volume. Install pulseaudio or alsa-utils."

    def volume_up(self) -> str:
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"],
                           capture_output=True)
            return "Volume increased."
        return "Could not adjust volume."

    def volume_down(self) -> str:
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-10%"],
                           capture_output=True)
            return "Volume decreased."
        return "Could not adjust volume."

    def mute(self) -> str:
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"],
                           capture_output=True)
            return "Toggled mute."
        return "Could not mute."

    # ─── App Launching ───────────────────────────────────────────────────────────

    def open_app(self, app_name: str) -> str:
        app_map = {
            "browser": self.browser,
            "firefox": "firefox",
            "chrome": "google-chrome",
            "chromium": "chromium-browser",
            "files": "nautilus",
            "file manager": "nautilus",
            "terminal": "gnome-terminal",
            "text editor": "gedit",
            "calculator": "gnome-calculator",
            "settings": "gnome-control-center",
            "spotify": "spotify",
            "vlc": "vlc",
        }

        cmd = app_map.get(app_name.lower(), app_name.lower())

        if not shutil.which(cmd):
            return f"I couldn't find '{cmd}' on your system."

        try:
            subprocess.Popen([cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening {app_name}."
        except Exception as e:
            logger.error(f"App launch error: {e}")
            return f"Failed to open {app_name}."

    # ─── Power ───────────────────────────────────────────────────────────────────

    def shutdown(self, delay_minutes: int = 1) -> str:
        if not self.allow_shutdown:
            return "Shutdown is disabled in settings."
        try:
            subprocess.run(["shutdown", f"+{delay_minutes}"], capture_output=True)
            return f"System will shut down in {delay_minutes} minute(s)."
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            return "Failed to initiate shutdown."

    def reboot(self) -> str:
        if not self.allow_reboot:
            return "Reboot is disabled in settings."
        try:
            subprocess.run(["reboot"], capture_output=True)
            return "Rebooting now."
        except Exception as e:
            logger.error(f"Reboot error: {e}")
            return "Failed to initiate reboot."

    def cancel_shutdown(self) -> str:
        try:
            subprocess.run(["shutdown", "-c"], capture_output=True)
            return "Shutdown cancelled."
        except Exception as e:
            return "Could not cancel shutdown."

    def lock_screen(self) -> str:
        for cmd in [["gnome-screensaver-command", "--lock"],
                    ["xdg-screensaver", "lock"],
                    ["loginctl", "lock-session"]]:
            if shutil.which(cmd[0]):
                subprocess.Popen(cmd)
                return "Screen locked."
        return "Couldn't lock the screen. No compatible lock command found."
