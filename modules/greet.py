"""
Cravias - Greet Module
Handles greetings, farewells, time-based salutations, and personality responses.
"""

import datetime
import random
import logging

logger = logging.getLogger(__name__)


class Greeter:
    def __init__(self, config: dict, memory=None):
        self.crax_name = config.get("name", "Cravias")
        self.humor_level = config.get("humor_level", "medium")
        self.memory = memory

    def get_greeting(self) -> str:
        hour = datetime.datetime.now().hour
        name = self.memory.get_user_name() if self.memory else ""
        address = f", {name}" if name else ""

        if 0 <= hour < 12:
            time_greet = random.choice([
                f"Good morning{address}!",
                f"Rise and shine{address}!",
                f"Morning{address}! Hope you slept well.",
            ])
        elif 12 <= hour < 17:
            time_greet = random.choice([
                f"Good afternoon{address}!",
                f"Hope your day's going well{address}.",
                f"Hey{address}, good afternoon!",
            ])
        elif 17 <= hour < 21:
            time_greet = random.choice([
                f"Good evening{address}!",
                f"Evening{address}! How was your day?",
                f"Hey{address}, good evening!",
            ])
        else:
            time_greet = random.choice([
                f"You're up late{address}.",
                f"Burning the midnight oil{address}?",
                f"Good night{address}... or morning. I'm not judging.",
            ])

        return time_greet

    def get_intro(self) -> str:
        return (
            f"I am {self.crax_name}, your voice assistant. "
            "I'm here to help. Just say my name or give me a command."
        )

    def get_farewell(self) -> str:
        name = self.memory.get_user_name() if self.memory else ""
        address = f", {name}" if name else ""
        return random.choice([
            f"Goodbye{address}! Have a great one.",
            f"See you later{address}!",
            f"Shutting down. Take care{address}.",
            f"Until next time{address}!",
        ])

    def get_confused_response(self) -> str:
        return random.choice([
            "I didn't quite catch that. Could you repeat?",
            "Hmm, I'm not sure what you mean. Try again?",
            "I didn't understand that. Could you rephrase?",
            "Sorry, that went over my head. What did you say?",
        ])

    def get_acknowledgement(self) -> str:
        return random.choice([
            "Sure!", "On it!", "Got it!", "Right away!", "No problem!"
        ])

    def handle_smalltalk(self, query: str) -> str | None:
        """Handle basic small talk queries. Returns response or None."""
        q = query.lower().strip()

        smalltalk = {
            ("hi", "hello", "hey", "howdy"): lambda: random.choice([
                "Hey there!", "Hello!", "Hi! What can I do for you?"
            ]),
            ("how are you", "how are you doing", "how's it going"): lambda: random.choice([
                "I'm running at full power, thanks for asking!",
                "All systems operational. How about you?",
                "Great! Ready to help.",
            ]),
            ("what is your name", "who are you", "what are you"): lambda: (
                f"I'm {self.crax_name} — Carbon Robotic Artificial Xenium. Your personal assistant."
            ),
            ("who created you", "who made you", "who built you"): lambda: (
                "I was built by Om, as part of the CRA VI project."
            ),
            ("what can you do", "help", "what are your features"): lambda: (
                "I can search the web, look up Wikipedia, play music, "
                "control your system, tell the time and date, remember things you tell me, "
                "and much more. Just ask!"
            ),
            ("tell me a joke", "say something funny", "joke"): lambda: self._get_joke(),
            ("thank you", "thanks", "thank you cravias"): lambda: random.choice([
                "You're welcome!", "Happy to help!", "Anytime!"
            ]),
        }

        for keys, response_fn in smalltalk.items():
            if any(k in q for k in keys):
                return response_fn()

        return None

    def _get_joke(self) -> str:
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
            "Why was the robot so bad at soccer? Because it kept getting booted.",
            "I'm reading a great book about anti-gravity. It's impossible to put down.",
            "Why do Java developers wear glasses? Because they don't C-sharp.",
        ]
        return random.choice(jokes)
