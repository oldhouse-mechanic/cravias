"""
Cravias - Listener Module (Speech-to-Text)
Uses Vosk for fully offline STT on Linux.
Falls back to SpeechRecognition + Google if Vosk model not found.
"""

import logging
import os
import queue
import json

# Suppress ALSA noise
os.environ.setdefault('PYTHONWARNINGS', 'ignore')
try:
    import ctypes
    ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int,
                                          ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
    def _py_error_handler(filename, line, function, err, fmt): pass
    _c_error_handler = ERROR_HANDLER_FUNC(_py_error_handler)
    ctypes.CDLL('libasound.so.2').snd_lib_error_set_handler(_c_error_handler)
except Exception:
    pass

logger = logging.getLogger(__name__)


class Listener:
    def __init__(self, config: dict):
        self.engine_name = config.get("stt_engine", "vosk")
        self.model_path = os.path.expanduser(config.get("stt_model_path", "~/vosk-model-small-en-us"))
        self.energy_threshold = config.get("energy_threshold", 200)
        self.pause_threshold = config.get("pause_threshold", 1.0)
        self.listen_timeout = config.get("listen_timeout", 10)
        self._model = None
        self._recognizer = None
        self._init_engine()

    def _init_engine(self):
        if self.engine_name == "vosk" and os.path.exists(self.model_path):
            try:
                from vosk import Model, KaldiRecognizer
                self._model = Model(self.model_path)
                logger.info(f"STT engine: Vosk (offline) | model: {self.model_path}")
                return
            except ImportError:
                logger.warning("Vosk not installed. Falling back to SpeechRecognition.")
            except Exception as e:
                logger.warning(f"Vosk init error: {e}. Falling back.")

        # Fallback: SpeechRecognition
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            self._recognizer.energy_threshold = self.energy_threshold
            self._recognizer.pause_threshold = self.pause_threshold
            self.engine_name = "sr_google"
            logger.info("STT engine: SpeechRecognition (Google online fallback)")
        except ImportError:
            logger.error("No STT engine available. Install vosk or SpeechRecognition.")

    def listen(self) -> str:
        """Listen from microphone and return recognized text."""
        print("\033[1;32m  ● Listening...\033[0m")
        try:
            if self.engine_name == "vosk" and self._model:
                return self._listen_vosk()
            elif self.engine_name == "sr_google" and self._recognizer:
                return self._listen_sr_google()
            else:
                logger.error("No STT engine initialized.")
                return ""
        except Exception as e:
            logger.error(f"Listen error: {e}")
            return ""

    def _listen_vosk(self) -> str:
        import sounddevice as sd
        from vosk import KaldiRecognizer

        recognizer = KaldiRecognizer(self._model, 16000)
        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio status: {status}")
            q.put(bytes(indata))

        with sd.RawInputStream(
            samplerate=16000, blocksize=8000, dtype="int16",
            channels=1, callback=callback
        ):
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print(f"[You]: {text}")
                        return text

    def _listen_sr_google(self) -> str:
        import speech_recognition as sr
        with sr.Microphone() as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self._recognizer.listen(
                    source, timeout=self.listen_timeout, phrase_time_limit=10
                )
                text = self._recognizer.recognize_google(audio, language="en-IN")
                print(f"\033[1;36m  You ›\033[0m {text}")
                return text
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except sr.RequestError as e:
                logger.error(f"STT request error: {e}")
                return ""
