"""
Cravias - Speaker Module (Text-to-Speech)
Uses Piper TTS for natural, fast, fully offline voice output.
Falls back to espeak if Piper is unavailable.
"""

import subprocess
import logging
import os
import shutil
import tempfile

logger = logging.getLogger(__name__)

# Default Piper voice model path
DEFAULT_PIPER_MODEL = os.path.expanduser("~/piper-voices/en_US-lessac-high.onnx")


class Speaker:
    def __init__(self, config: dict):
        self.piper_model = os.path.expanduser(
            config.get("piper_model", DEFAULT_PIPER_MODEL)
        )
        self.volume = config.get("tts_volume", 1.0)
        self.silent_mode = config.get("silent_mode", False)
        self.engine_name = None
        self._piper_cmd = "piper"
        self._init_engine()

    def _init_engine(self):
        # Try Piper first
        if self._check_piper():
            self.engine_name = "piper"
            logger.info(f"TTS engine: Piper | model: {self.piper_model}")
            return

        # Fallback to espeak
        if shutil.which("espeak") or shutil.which("espeak-ng"):
            self.engine_name = "espeak"
            logger.warning("Piper not found, falling back to espeak.")
            return

        logger.error("No TTS engine found. Install piper-tts or espeak.")

    def _check_piper(self) -> bool:
        # Check venv bin first, then system PATH
        venv_piper = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv", "bin", "piper")
        if os.path.exists(venv_piper):
            self._piper_cmd = venv_piper
        elif shutil.which("piper"):
            self._piper_cmd = shutil.which("piper")
        else:
            logger.warning("piper binary not found in venv or system PATH.")
            return False
        if not os.path.exists(self.piper_model):
            logger.warning(f"Piper model not found at: {self.piper_model}")
            return False
        return True

    def speak(self, text: str, silent: bool = False):
        """Convert text to speech and play it. If silent, print only."""
        if not text:
            return

        print(f"\033[1;35m  Cravias ›\033[0m {text}")

        if silent or self.silent_mode:
            return

        try:
            if self.engine_name == "piper":
                self._speak_piper(text)
            elif self.engine_name == "espeak":
                self._speak_espeak(text)
            else:
                logger.error("No TTS engine available.")
        except Exception as e:
            logger.error(f"TTS error: {e}")

    def _speak_piper(self, text: str):
        """Pipe text through Piper and play with aplay."""
        try:
            piper_proc = subprocess.Popen(
                [self._piper_cmd, "--model", self.piper_model, "--output_raw"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            aplay_proc = subprocess.Popen(
                ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"],
                stdin=piper_proc.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            piper_proc.stdin.write(text.encode())
            piper_proc.stdin.close()
            piper_proc.stdout.close()
            aplay_proc.wait()
        except Exception as e:
            logger.error(f"Piper speak error: {e}")
            # Try espeak as emergency fallback
            self._speak_espeak(text)

    def _speak_espeak(self, text: str):
        cmd = shutil.which("espeak-ng") or "espeak"
        subprocess.run(
            [cmd, "-v", "en-gb-x-rp", "-s", "145", text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
