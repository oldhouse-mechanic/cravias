"""
Cravias - Brain Module (Semantic NLP Edition)
Uses sentence-transformers to match user intent via semantic similarity.
No more fragile keyword matching — understands natural language.
Falls back to keyword matching if sentence-transformers is unavailable.
"""

import re
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

# ─── Intent Definitions ──────────────────────────────────────────────────────
# Each intent has a list of example phrases that describe what it does.
# The semantic model encodes these and finds the closest match to the user query.

INTENT_EXAMPLES = {
    # ── Search & Web ──────────────────────────────────────────────────────────
    "search": [
        "search for something online",
        "google this for me",
        "look this up on the internet",
        "find information about",
        "search the web for",
        "browse for",
        "find online",
    ],
    "wikipedia": [
        "look this up on wikipedia",
        "who is this person",
        "what is this thing",
        "tell me about",
        "explain what something is",
        "give me information about",
        "define something",
        "what does this mean",
        "search wikipedia",
    ],
    "youtube": [
        "open youtube",
        "go to youtube",
        "search youtube for a video",
        "watch something on youtube",
        "play a video on youtube",
        "find a video",
    ],
    "open_url": [
        "open a website",
        "go to a webpage",
        "navigate to a site",
        "visit a url",
        "open this link",
    ],

    # ── Time & Date ───────────────────────────────────────────────────────────
    "time": [
        "what time is it",
        "tell me the current time",
        "what's the hour",
        "check the time",
        "what time right now",
    ],
    "date": [
        "what is today's date",
        "what day is it today",
        "tell me the date",
        "what's today",
        "which day of the week is it",
    ],
    "datetime": [
        "what is the date and time",
        "tell me both the time and date",
        "current date and time",
    ],

    # ── Music ─────────────────────────────────────────────────────────────────
    "play_music": [
        "play some music",
        "put on a song",
        "play a track",
        "start playing music",
        "play something",
        "I want to listen to music",
        "play this song",
    ],
    "stop_music": [
        "stop the music",
        "pause what's playing",
        "turn off the music",
        "stop playing",
        "quiet the music",
    ],
    "shuffle_music": [
        "shuffle my music",
        "play something random",
        "random song please",
        "surprise me with a song",
    ],
    "list_music": [
        "what songs do I have",
        "list my music",
        "show my music library",
        "what's in my music folder",
    ],
    "youtube_music": [
        "open youtube music",
        "play music online",
        "stream music from youtube",
    ],

    # ── System ────────────────────────────────────────────────────────────────
    "battery": [
        "how much battery do I have",
        "check battery level",
        "what's the battery percentage",
        "is the charger connected",
        "power level",
    ],
    "system_info": [
        "show system information",
        "what cpu am I running",
        "how much ram is being used",
        "system stats",
        "computer information",
        "memory usage",
    ],
    "volume_up": [
        "turn the volume up",
        "make it louder",
        "increase the volume",
        "raise the volume",
        "volume higher",
    ],
    "volume_down": [
        "turn the volume down",
        "make it quieter",
        "decrease the volume",
        "lower the volume",
        "volume lower",
    ],
    "mute": [
        "mute the sound",
        "silence everything",
        "turn off the sound",
        "mute the volume",
        "quiet please",
    ],
    "open_app": [
        "open an application",
        "launch a program",
        "start an app",
        "open firefox",
        "launch the terminal",
        "open file manager",
    ],
    "lock": [
        "lock the screen",
        "lock my computer",
        "lock the desktop",
        "secure the screen",
    ],
    "shutdown": [
        "shut down the computer",
        "power off the system",
        "turn off the machine",
        "shut this down",
    ],
    "reboot": [
        "restart the computer",
        "reboot the system",
        "restart the machine",
    ],
    "cancel_shutdown": [
        "cancel the shutdown",
        "abort the restart",
        "stop the shutdown",
        "cancel reboot",
    ],

    # ── Keyboard & Automation ─────────────────────────────────────────────────
    "type_text": [
        "type this text for me",
        "write this out",
        "type what I say",
        "enter this text",
        "keyboard this",
        "type hello world",
        "type out this message",
    ],
    "copy": [
        "copy this",
        "copy selected text",
        "copy to clipboard",
    ],
    "paste": [
        "paste here",
        "paste from clipboard",
        "put it here",
    ],
    "cut": [
        "cut this",
        "cut selected text",
    ],
    "undo": [
        "undo that",
        "go back one step",
        "undo my last action",
        "ctrl z",
    ],
    "redo": [
        "redo that",
        "do it again",
        "redo last action",
    ],
    "select_all": [
        "select all",
        "select everything",
        "highlight all",
    ],
    "save": [
        "save the file",
        "save this document",
        "save my work",
    ],
    "press_enter": [
        "press enter",
        "hit enter",
        "confirm with enter",
        "submit this",
    ],
    "press_escape": [
        "press escape",
        "hit escape",
        "cancel with escape",
        "press esc",
    ],
    "press_space": [
        "press the spacebar",
        "hit space",
        "press space",
    ],
    "erase": [
        "erase that",
        "delete the last character",
        "backspace",
        "remove that",
    ],
    "close_window": [
        "close this window",
        "close the app",
        "kill this window",
        "close what's open",
    ],
    "switch_window": [
        "switch to another window",
        "alt tab",
        "go to next window",
        "switch apps",
    ],
    "new_tab": [
        "open a new tab",
        "new browser tab",
        "create a new tab",
    ],
    "close_tab": [
        "close this tab",
        "close the current tab",
    ],
    "fullscreen": [
        "go fullscreen",
        "make it full screen",
        "toggle fullscreen",
        "maximize the window",
    ],
    "scroll_up": [
        "scroll up",
        "go up the page",
        "move up",
        "roll up the page",
    ],
    "scroll_down": [
        "scroll down",
        "go down the page",
        "move down",
        "roll down the page",
    ],
    "scroll_top": [
        "go to the top of the page",
        "scroll to the beginning",
        "jump to top",
        "back to top",
    ],
    "scroll_bottom": [
        "go to the bottom of the page",
        "scroll to the end",
        "jump to bottom",
        "go to end",
    ],
    "media_play_pause": [
        "pause the media",
        "resume playing",
        "toggle play pause",
        "pause this",
    ],
    "media_next": [
        "next track",
        "skip this song",
        "play the next song",
        "go to next",
    ],
    "media_previous": [
        "previous track",
        "go back to the last song",
        "play previous",
        "last track",
    ],
    "screenshot": [
        "take a screenshot",
        "capture the screen",
        "screenshot please",
        "grab the screen",
    ],

    # ── Memory ────────────────────────────────────────────────────────────────
    "remember": [
        "remember this for me",
        "note this down",
        "keep this in mind",
        "don't forget this",
        "save this fact",
        "remember that",
    ],
    "recall": [
        "what do you know about this",
        "do you remember when I said",
        "recall something",
        "what did I tell you about",
    ],
    "memory_summary": [
        "what have you learned about me",
        "show me your memory",
        "what do you know about me",
        "summarize what you remember",
    ],

    # ── Exit ──────────────────────────────────────────────────────────────────
    "exit": [
        "goodbye",
        "bye",
        "shut yourself down",
        "exit the program",
        "quit cravias",
        "see you later",
        "that's all for now",
        "go to sleep",
        "stop cravias",
    ],
}


class SemanticMatcher:
    """
    TF-IDF + cosine similarity intent matcher using scikit-learn.
    Lightweight (~50MB), no GPU, no PyTorch. Works fully offline.
    Much smarter than keyword matching — handles natural phrasing.
    """

    def __init__(self, intent_examples: dict):
        self.intent_examples = intent_examples
        self._vectorizer = None
        self._intent_matrix = None
        self._intent_names = []
        self._available = False
        self._load_model()

    def _load_model(self):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            # Flatten all examples, keep track of which intent each belongs to
            all_examples = []
            for intent_name, examples in self.intent_examples.items():
                for ex in examples:
                    all_examples.append((intent_name, ex))

            self._intent_names_flat = [x[0] for x in all_examples]
            corpus = [x[1] for x in all_examples]

            # Fit TF-IDF on all example phrases
            self._vectorizer = TfidfVectorizer(
                ngram_range=(1, 3),   # unigrams, bigrams, trigrams
                analyzer="word",
                sublinear_tf=True,    # dampen high-frequency terms
            )
            self._intent_matrix = self._vectorizer.fit_transform(corpus)
            self._available = True
            logger.warning(f"TF-IDF intent engine ready ({len(corpus)} examples, {len(self.intent_examples)} intents)")
        except ImportError:
            logger.warning("scikit-learn not installed. Using keyword fallback.")
        except Exception as e:
            logger.warning(f"TF-IDF init failed: {e}. Using keyword fallback.")

    def match(self, query: str, threshold: float = 0.10) -> Optional[str]:
        if not self._available:
            return None

        from sklearn.metrics.pairwise import cosine_similarity

        query_vec = self._vectorizer.transform([query.lower()])
        scores = cosine_similarity(query_vec, self._intent_matrix)[0]

        # For each intent, take the highest-scoring example
        intent_scores = {}
        for idx, score in enumerate(scores):
            intent = self._intent_names_flat[idx]
            if score > intent_scores.get(intent, 0):
                intent_scores[intent] = score

        if not intent_scores:
            return None

        best_intent = max(intent_scores, key=intent_scores.get)
        best_score = intent_scores[best_intent]

        logger.warning(f"TF-IDF: '{query}' → {best_intent} ({best_score:.3f})")
        return best_intent if best_score >= threshold else None

    @property
    def available(self) -> bool:
        return self._available


class KeywordFallback:
    """Simple keyword fallback when semantic model is unavailable."""
    KEYWORDS = {
        "search": ["search", "google", "look up", "find", "browse"],
        "wikipedia": ["wikipedia", "wiki", "who is", "what is", "tell me about"],
        "youtube": ["youtube", "watch video"],
        "time": ["time", "what time", "hour"],
        "date": ["date", "today", "what day"],
        "play_music": ["play music", "play song"],
        "stop_music": ["stop music", "pause music"],
        "battery": ["battery", "charge"],
        "volume_up": ["volume up", "louder"],
        "volume_down": ["volume down", "quieter"],
        "mute": ["mute", "silence"],
        "open_app": ["open", "launch"],
        "lock": ["lock screen"],
        "shutdown": ["shutdown", "power off"],
        "reboot": ["reboot", "restart"],
        "type_text": ["type "],
        "copy": ["copy"],
        "paste": ["paste"],
        "undo": ["undo"],
        "redo": ["redo"],
        "save": ["save file", "save this"],
        "press_enter": ["press enter"],
        "erase": ["erase", "backspace"],
        "close_window": ["close window"],
        "fullscreen": ["fullscreen", "full screen"],
        "scroll_up": ["scroll up"],
        "scroll_down": ["scroll down"],
        "screenshot": ["screenshot"],
        "remember": ["remember", "note that"],
        "exit": ["bye", "goodbye", "exit", "quit"],
    }

    def match(self, query: str) -> Optional[str]:
        q = query.lower()
        best, best_len = None, 0
        for intent, keywords in self.KEYWORDS.items():
            for kw in keywords:
                if kw in q and len(kw) > best_len:
                    best, best_len = intent, len(kw)
        return best


class Brain:
    def __init__(self, memory, searcher, music_player, system_ctrl,
                 greeter, speaker, keyboard=None):
        self.memory = memory
        self.searcher = searcher
        self.music = music_player
        self.system = system_ctrl
        self.greeter = greeter
        self.speaker = speaker
        self.keyboard = keyboard
        self.semantic = SemanticMatcher(INTENT_EXAMPLES)
        self.keyword_fallback = KeywordFallback()
        self._handlers = self._build_handlers()
        # State for correction & confirmation tracking
        self._last_query = None
        self._last_intent = None
        self._last_response = None
        self._pending_intent = None
        self._pending_query = None

    def _build_handlers(self) -> dict:
        return {
            "search":           self._handle_search,
            "wikipedia":        self._handle_wikipedia,
            "youtube":          self._handle_youtube,
            "open_url":         self._handle_open_url,
            "time":             self._handle_time,
            "date":             self._handle_date,
            "datetime":         self._handle_datetime,
            "play_music":       self._handle_play_music,
            "stop_music":       self._handle_stop_music,
            "shuffle_music":    self._handle_shuffle,
            "list_music":       self._handle_list_music,
            "youtube_music":    self._handle_youtube_music,
            "battery":          self._handle_battery,
            "system_info":      self._handle_system_info,
            "volume_up":        self._handle_volume_up,
            "volume_down":      self._handle_volume_down,
            "mute":             self._handle_mute,
            "open_app":         self._handle_open_app,
            "lock":             self._handle_lock,
            "shutdown":         self._handle_shutdown,
            "reboot":           self._handle_reboot,
            "cancel_shutdown":  self._handle_cancel_shutdown,
            "type_text":        self._handle_type_text,
            "copy":             self._handle_copy,
            "paste":            self._handle_paste,
            "cut":              self._handle_cut,
            "undo":             self._handle_undo,
            "redo":             self._handle_redo,
            "select_all":       self._handle_select_all,
            "save":             self._handle_save,
            "press_enter":      self._handle_enter,
            "press_escape":     self._handle_escape,
            "press_space":      self._handle_space,
            "erase":            self._handle_backspace,
            "close_window":     self._handle_close_window,
            "switch_window":    self._handle_switch_window,
            "new_tab":          self._handle_new_tab,
            "close_tab":        self._handle_close_tab,
            "fullscreen":       self._handle_fullscreen,
            "scroll_up":        self._handle_scroll_up,
            "scroll_down":      self._handle_scroll_down,
            "scroll_top":       self._handle_scroll_top,
            "scroll_bottom":    self._handle_scroll_bottom,
            "media_play_pause": self._handle_play_pause,
            "media_next":       self._handle_media_next,
            "media_previous":   self._handle_media_previous,
            "screenshot":       self._handle_screenshot,
            "remember":         self._handle_remember,
            "recall":           self._handle_recall,
            "memory_summary":   self._handle_memory_summary,
            "exit":             self._handle_exit,
        }

    # ─── Dispatch ────────────────────────────────────────────────────────────

    def process(self, query: str) -> tuple[str, bool]:
        q = query.lower().strip()

        # -1. Check yes/no confirmation for pending intents
        if self._pending_intent:
            confirmation = self.greeter.handle_confirmation(q, self)
            if confirmation:
                self.memory.add("user", query)
                self.memory.add("crax", confirmation)
                return confirmation, False

        # 0. Check for correction mode ("no I meant X")
        correction = self._check_correction(q)
        if correction:
            self.memory.add("user", query)
            self.memory.add("crax", correction)
            return correction, False

        # 0b. Check for explicit phrase teaching ("whenever I say X mean Y")
        teaching = self._check_teaching(q)
        if teaching:
            self.memory.add("user", query)
            self.memory.add("crax", teaching)
            return teaching, False

        # 1. Small talk (fast path)
        smalltalk = self.greeter.handle_smalltalk(q)
        if smalltalk:
            self._last_query = q
            self._last_intent = None
            self._last_response = smalltalk
            self.memory.add("user", query)
            self.memory.add("crax", smalltalk)
            return smalltalk, False

        # 2. Check learned command mappings first (highest priority)
        learned_intent = self.memory.get_command_intent(q)
        if learned_intent and learned_intent in self._handlers:
            response = self._handlers[learned_intent](q)
            self._last_query = q
            self._last_intent = learned_intent
            self._last_response = response
            self.memory.add("user", query)
            self.memory.add("crax", response)
            return response, learned_intent == "exit"

        # 3. TF-IDF semantic match
        intent_name = self.semantic.match(q)
        confidence = self._get_confidence(q, intent_name)

        # 4. Keyword fallback if no semantic match
        if not intent_name:
            intent_name = self.keyword_fallback.match(q)
            confidence = "low"

        if intent_name and intent_name in self._handlers:
            # Low confidence — ask for confirmation instead of acting blindly
            if confidence == "low":
                self._pending_intent = intent_name
                self._pending_query = q
                friendly = intent_name.replace("_", " ")
                confirm_msg = f"Just to confirm — did you want me to {friendly}?"
                self._last_query = q
                self._last_intent = intent_name
                self._last_response = confirm_msg
                self.memory.add("user", query)
                self.memory.add("crax", confirm_msg)
                return confirm_msg, False

            response = self._handlers[intent_name](q)
            self._last_query = q
            self._last_intent = intent_name
            self._last_response = response
            self.memory.add("user", query)
            self.memory.add("crax", response)
            return response, intent_name == "exit"

        # 5. Confused fallback
        self._last_query = q
        self._last_intent = None
        fallback = self.greeter.get_confused_response()
        self.memory.add("user", query)
        self.memory.add("crax", fallback)
        return fallback, False

    def _get_confidence(self, query: str, intent: str | None) -> str:
        """Return 'high' or 'low' confidence based on TF-IDF score."""
        if not intent or not self.semantic.available:
            return "low"
        from sklearn.metrics.pairwise import cosine_similarity
        try:
            query_vec = self.semantic._vectorizer.transform([query.lower()])
            scores = cosine_similarity(query_vec, self.semantic._intent_matrix)[0]
            intent_indices = [i for i, n in enumerate(self.semantic._intent_names_flat) if n == intent]
            best = max(scores[i] for i in intent_indices) if intent_indices else 0
            return "high" if best >= 0.25 else "low"
        except Exception:
            return "high"  # default to high to avoid annoying confirmations

    def _check_correction(self, q: str) -> str | None:
        """
        Handle corrections like:
        "no I meant scroll down"
        "wrong, I wanted to search"
        "no that's not right, type hello"
        """
        correction_triggers = ["no i meant", "no, i meant", "wrong i meant",
                                "that's not right", "not that", "i wanted to",
                                "i said", "no i said", "i meant"]
        for trigger in correction_triggers:
            if q.startswith(trigger) or q.startswith("no, ") or q.startswith("no "):
                # Extract the corrected intent
                corrected = q
                for t in correction_triggers + ["no,", "no"]:
                    corrected = re.sub(rf'^{re.escape(t)}\s*', '', corrected).strip()

                new_intent = self.semantic.match(corrected)
                if not new_intent:
                    new_intent = self.keyword_fallback.match(corrected)

                if new_intent and new_intent in self._handlers:
                    # Save the original misunderstood query → correct intent
                    if hasattr(self, '_last_query') and self._last_query:
                        self.memory.learn_command(self._last_query, new_intent)

                    response = self._handlers[new_intent](corrected)
                    self._last_intent = new_intent
                    return f"Got it! {response} — I'll remember that for next time."
        return None

    def _check_teaching(self, q: str) -> str | None:
        """
        Handle explicit teaching like:
        "whenever I say the thing, mean search"
        "if I say tunes, play music"
        "teach yourself: yo means hello"
        """
        patterns = [
            r"whenever i say (.+?),?\s+(?:mean|do|it means|you should) (.+)",
            r"if i say (.+?),?\s+(?:mean|do|it means|you should) (.+)",
            r"teach yourself[:\s]+(.+?) means (.+)",
            r"learn that (.+?) means (.+)",
            r"(.+?) is my word for (.+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, q)
            if match:
                alias = match.group(1).strip()
                intent_phrase = match.group(2).strip()
                # Map the phrase to an intent
                intent = self.semantic.match(intent_phrase) or self.keyword_fallback.match(intent_phrase)
                if intent:
                    self.memory.learn_phrase_alias(alias, intent)
                    return f"Understood! Whenever you say '{alias}', I'll treat it as {intent.replace('_', ' ')}."
                else:
                    return f"I understood the alias '{alias}' but couldn't figure out what '{intent_phrase}' maps to. Try being more specific."
        return None

    # ─── Query extraction ────────────────────────────────────────────────────

    def _extract(self, query: str, remove: list) -> str:
        q = query.lower().strip()
        for phrase in sorted(remove, key=len, reverse=True):
            q = re.sub(rf'^{re.escape(phrase)}\s*', '', q).strip()
        return q

    # ─── Handlers ────────────────────────────────────────────────────────────

    def _handle_search(self, q):
        q = self._extract(q, ["search for", "search", "google", "look up", "find", "browse"])
        return self.searcher.search_web(q)

    def _handle_wikipedia(self, q):
        q = self._extract(q, ["search wikipedia for", "wikipedia", "wiki", "who is",
                               "what is", "tell me about", "explain", "define"])
        return self.searcher.search_wikipedia(q)

    def _handle_youtube(self, q):
        q = self._extract(q, ["search youtube for", "play on youtube", "open youtube", "youtube"])
        return self.searcher.open_youtube(q)

    def _handle_open_url(self, q):
        q = self._extract(q, ["open", "go to", "navigate to", "visit"])
        return self.searcher.open_url(q)

    def _handle_time(self, _):     return self.system.get_time()
    def _handle_date(self, _):     return self.system.get_date()
    def _handle_datetime(self, _): return self.system.get_datetime()
    def _handle_battery(self, _):  return self.system.get_battery()
    def _handle_system_info(self, _): return self.system.get_system_info()
    def _handle_volume_up(self, _):   return self.system.volume_up()
    def _handle_volume_down(self, _): return self.system.volume_down()
    def _handle_mute(self, _):        return self.system.mute()
    def _handle_lock(self, _):        return self.system.lock_screen()
    def _handle_shutdown(self, _):    return self.system.shutdown()
    def _handle_reboot(self, _):      return self.system.reboot()
    def _handle_cancel_shutdown(self, _): return self.system.cancel_shutdown()
    def _handle_stop_music(self, _):  return self.music.stop()
    def _handle_shuffle(self, _):     return self.music.shuffle()
    def _handle_list_music(self, _):  return self.music.list_songs()
    def _handle_youtube_music(self, _): return self.music.open_youtube_music()
    def _handle_memory_summary(self, _): return self.memory.summarize()
    def _handle_exit(self, _):        return self.greeter.get_farewell()

    def _handle_play_music(self, q):
        q = self._extract(q, ["play some music", "play music", "put on", "listen to", "play"])
        q = re.sub(r'\b(music|song|track|audio)\b', '', q).strip()
        return self.music.play(q)

    def _handle_open_app(self, q):
        q = self._extract(q, ["open", "launch", "start"])
        return self.system.open_app(q)

    def _handle_remember(self, q):
        q = self._extract(q, ["remember that", "remember", "note that", "keep in mind", "don't forget"])
        if q:
            self.memory.teach("user_note_manual", q)
            return f"Got it, I'll remember that: '{q}'"
        return "What would you like me to remember?"

    def _handle_recall(self, q):
        q = self._extract(q, ["what do you know about", "recall"])
        history = self.memory.search_history(q)
        if history:
            return f"I recall you mentioned '{history[-1]['text']}' on {history[-1]['timestamp'][:10]}."
        return f"I don't have anything specific about '{q}' in memory."

    # ── Keyboard ─────────────────────────────────────────────────────────────

    def _kb(self): return self.keyboard
    def _no_kb(self): return "Keyboard module not loaded."

    def _handle_type_text(self, q):
        if not self._kb(): return self._no_kb()
        q = self._extract(q, ["type out", "type the words", "type the text", "please type", "can you type", "type"])
        return self._kb().type_text(q)

    def _handle_copy(self, _):        return self._kb().copy() if self._kb() else self._no_kb()
    def _handle_paste(self, _):       return self._kb().paste() if self._kb() else self._no_kb()
    def _handle_cut(self, _):         return self._kb().cut() if self._kb() else self._no_kb()
    def _handle_undo(self, _):        return self._kb().undo() if self._kb() else self._no_kb()
    def _handle_redo(self, _):        return self._kb().redo() if self._kb() else self._no_kb()
    def _handle_select_all(self, _):  return self._kb().select_all() if self._kb() else self._no_kb()
    def _handle_save(self, _):        return self._kb().save() if self._kb() else self._no_kb()
    def _handle_enter(self, _):       return self._kb().press_enter() if self._kb() else self._no_kb()
    def _handle_escape(self, _):      return self._kb().press_escape() if self._kb() else self._no_kb()
    def _handle_space(self, _):       return self._kb().press_space() if self._kb() else self._no_kb()
    def _handle_backspace(self, _):   return self._kb().press_backspace() if self._kb() else self._no_kb()
    def _handle_close_window(self, _): return self._kb().close_window() if self._kb() else self._no_kb()
    def _handle_switch_window(self, _): return self._kb().switch_window() if self._kb() else self._no_kb()
    def _handle_new_tab(self, _):     return self._kb().new_tab() if self._kb() else self._no_kb()
    def _handle_close_tab(self, _):   return self._kb().close_tab() if self._kb() else self._no_kb()
    def _handle_fullscreen(self, _):  return self._kb().fullscreen() if self._kb() else self._no_kb()
    def _handle_scroll_up(self, _):   return self._kb().scroll_up() if self._kb() else self._no_kb()
    def _handle_scroll_down(self, _): return self._kb().scroll_down() if self._kb() else self._no_kb()
    def _handle_scroll_top(self, _):  return self._kb().scroll_to_top() if self._kb() else self._no_kb()
    def _handle_scroll_bottom(self, _): return self._kb().scroll_to_bottom() if self._kb() else self._no_kb()
    def _handle_play_pause(self, _):  return self._kb().media_play_pause() if self._kb() else self._no_kb()
    def _handle_media_next(self, _):  return self._kb().media_next() if self._kb() else self._no_kb()
    def _handle_media_previous(self, _): return self._kb().media_previous() if self._kb() else self._no_kb()
    def _handle_screenshot(self, _):  return self._kb().screenshot() if self._kb() else self._no_kb()
