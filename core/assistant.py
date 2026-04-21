"""
Cravias - Assistant Core
Main orchestrator. Wires up all modules and runs the main loop.
"""

import logging
import os
import yaml

from core.speaker import Speaker
from core.listener import Listener
from core.brain import Brain
from modules.memory import Memory
from modules.search import Searcher
from modules.music import MusicPlayer
from modules.system import SystemController
from modules.greet import Greeter
from modules.keyboard import Keyboard

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/settings.yaml") -> dict:
    """Load YAML config file and return as flat-ish dict."""
    try:
        with open(config_path, "r") as f:
            raw = yaml.safe_load(f)
        # Merge all sub-sections into a single flat config
        config = {}
        for section in raw.values():
            if isinstance(section, dict):
                config.update(section)
        return config
    except FileNotFoundError:
        logger.warning(f"Config not found at {config_path}. Using defaults.")
        return {}
    except Exception as e:
        logger.error(f"Config load error: {e}")
        return {}


class Assistant:
    def __init__(self, config_path: str = "config/settings.yaml", silent_mode: bool = False):
        self.config = load_config(config_path)
        self.config["silent_mode"] = silent_mode
        self.crax_name = self.config.get("name", "Cravias")
        self._setup_logging()
        self._init_modules()

    def _setup_logging(self):
        # Only show WARNING and above in terminal — keep it clean
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )

    def _init_modules(self):
        logger.info("Initializing Cravias modules...")
        self.memory = Memory(self.config)
        self.speaker = Speaker(self.config)
        self.listener = Listener(self.config)
        self.searcher = Searcher(self.config)
        self.music = MusicPlayer(self.config)
        self.system = SystemController(self.config)
        self.greeter = Greeter(self.config, memory=self.memory)
        self.keyboard = Keyboard()
        self.brain = Brain(
            memory=self.memory,
            searcher=self.searcher,
            music_player=self.music,
            system_ctrl=self.system,
            greeter=self.greeter,
            speaker=self.speaker,
            keyboard=self.keyboard,
        )
        logger.info("All modules initialized.")

    def run(self, text_mode: bool = False):
        """
        Start the main assistant loop.
        text_mode: use keyboard input instead of microphone (for testing).
        """
        self.speaker.speak(self.greeter.get_greeting())
        self.speaker.speak(self.greeter.get_intro())

        print("\n" + "=" * 50)
        print(f"  {self.crax_name} is active. Say a command.")
        if text_mode:
            print("  [TEXT MODE] Type your commands. Type 'exit' to quit.")
        print("=" * 50 + "\n")

        while True:
            try:
                if text_mode:
                    query = input("You: ").strip()
                    if not query:
                        continue
                else:
                    query = self.listener.listen()
                    if not query:
                        continue

                response, should_exit = self.brain.process(query)
                self.speaker.speak(response)

                if should_exit:
                    break

            except KeyboardInterrupt:
                farewell = self.greeter.get_farewell()
                self.speaker.speak(farewell)
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}", exc_info=True)
                self.speaker.speak("Something went wrong. Let's try again.")

        logger.info("Cravias shutting down.")
