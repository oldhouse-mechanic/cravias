"""
Cravias - Memory Module
Handles persistent conversation history and learned knowledge.
Cravias learns from conversations - remembers facts you tell it,
your preferences, and builds a personal knowledge base over time.
"""

import json
import os
import datetime
import logging
import re

logger = logging.getLogger(__name__)


class Memory:
    def __init__(self, config: dict):
        self.memory_file = config.get("memory_file", "data/memory.json")
        self.learned_file = config.get("learned_file", "data/learned.json")
        self.max_history = config.get("max_history", 200)
        self.learn_enabled = config.get("learn_from_chat", True)
        self._history = []
        self._learned = {}
        self._load()

    # ─── Persistence ────────────────────────────────────────────────────────────

    def _load(self):
        self._history = self._load_json(self.memory_file, default=[])
        self._learned = self._load_json(self.learned_file, default={})
        self._commands = self._load_json("data/commands.json", default={})
        logger.info(f"Memory loaded: {len(self._history)} history entries, {len(self._learned)} learned facts, {len(self._commands)} learned commands.")

    def _load_json(self, path: str, default):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load {path}: {e}")
        return default

    def _save(self):
        self._save_json(self.memory_file, self._history)
        self._save_json(self.learned_file, self._learned)
        self._save_json("data/commands.json", self._commands)

    def _save_json(self, path: str, data):
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save {path}: {e}")

    # ─── Conversation History ────────────────────────────────────────────────────

    def add(self, role: str, text: str):
        """Add a conversation entry (role: 'user' or 'crax')."""
        entry = {
            "role": role,
            "text": text,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self._history.append(entry)

        # Trim to max history
        if len(self._history) > self.max_history:
            self._history = self._history[-self.max_history:]

        self._save()

        # Try to learn from user messages
        if self.learn_enabled and role == "user":
            self._extract_and_learn(text)

    def get_recent(self, n: int = 10) -> list:
        """Get the n most recent conversation entries."""
        return self._history[-n:]

    def search_history(self, keyword: str) -> list:
        """Search conversation history for a keyword."""
        keyword = keyword.lower()
        return [e for e in self._history if keyword in e["text"].lower()]

    # ─── Learning ───────────────────────────────────────────────────────────────

    def _extract_and_learn(self, text: str):
        """
        Extract learnable facts from user input.
        Patterns like:
          - "my name is X"
          - "I am X years old"
          - "I like X"
          - "remember that X"
          - "I live in X"
        """
        text_lower = text.lower().strip()

        patterns = [
            (r"my name is ([a-z]+)", "user_name"),
            (r"(?:i am|i'm) (\d+)(?: years old)?", "user_age"),
            (r"i live in ([a-z\s]+)", "user_location"),
            (r"i (?:like|love|enjoy) ([a-z\s]+)", "user_likes"),
            (r"i (?:hate|dislike|don't like) ([a-z\s]+)", "user_dislikes"),
            (r"remember (?:that )?(.+)", "user_note"),
            (r"my favourite (\w+) is ([a-z\s]+)", None),  # special case
        ]

        for pattern, key in patterns:
            match = re.search(pattern, text_lower)
            if match:
                if key == "user_likes":
                    self._learned.setdefault("user_likes", [])
                    val = match.group(1).strip()
                    if val not in self._learned["user_likes"]:
                        self._learned["user_likes"].append(val)
                        logger.info(f"Learned: user likes '{val}'")
                elif key == "user_dislikes":
                    self._learned.setdefault("user_dislikes", [])
                    val = match.group(1).strip()
                    if val not in self._learned["user_dislikes"]:
                        self._learned["user_dislikes"].append(val)
                        logger.info(f"Learned: user dislikes '{val}'")
                elif key == "user_note":
                    self._learned.setdefault("notes", [])
                    val = match.group(1).strip()
                    self._learned["notes"].append({
                        "note": val,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                    logger.info(f"Learned note: '{val}'")
                elif key is None:
                    # "my favourite X is Y"
                    fav_key = f"favourite_{match.group(1).strip()}"
                    self._learned[fav_key] = match.group(2).strip()
                    logger.info(f"Learned: {fav_key} = {self._learned[fav_key]}")
                else:
                    self._learned[key] = match.group(1).strip()
                    logger.info(f"Learned: {key} = {self._learned[key]}")

                self._save()

    def teach(self, key: str, value):
        """Manually store a learned fact."""
        self._learned[key] = value
        self._save()
        logger.info(f"Manually learned: {key} = {value}")

    def recall(self, key: str):
        """Retrieve a learned fact."""
        return self._learned.get(key)

    def get_all_learned(self) -> dict:
        return dict(self._learned)

    def get_user_name(self) -> str:
        return self._learned.get("user_name", "")

    # ─── Command Learning ───────────────────────────────────────────────────────

    def learn_command(self, phrase: str, intent: str):
        """Save a user phrase → intent mapping."""
        self._commands[phrase.lower().strip()] = intent
        self._save()
        logger.info(f"Learned command: '{phrase}' → {intent}")

    def get_learned_commands(self) -> dict:
        """Return all learned phrase → intent mappings."""
        return dict(self._commands)

    def learn_phrase_alias(self, alias: str, intent: str):
        """Explicitly teach Cravias that a phrase means a specific intent."""
        self._commands[alias.lower().strip()] = intent
        self._save()

    def get_command_intent(self, phrase: str) -> str | None:
        """Check if a phrase has a learned intent mapping."""
        return self._commands.get(phrase.lower().strip())

    def get_recent_commands(self, n: int = 20) -> list:
        """Get recent user commands from history."""
        return [e for e in self._history[-n:] if e["role"] == "user"]

    def summarize(self) -> str:
        """Return a short text summary of what Cravias knows."""
        lines = [f"I have {len(self._history)} conversation entries in memory."]
        if self._learned:
            lines.append("Here's what I've learned about you:")
            for k, v in self._learned.items():
                lines.append(f"  - {k}: {v}")
        else:
            lines.append("I haven't learned anything specific yet.")
        return "\n".join(lines)
