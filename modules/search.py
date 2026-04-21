"""
Cravias - Search Module
Handles web search (DuckDuckGo, no API key required) and Wikipedia lookups.
"""

import webbrowser
import logging
import re

logger = logging.getLogger(__name__)


class Searcher:
    def __init__(self, config: dict):
        self.engine = config.get("engine", "duckduckgo")
        self.wiki_sentences = config.get("wikipedia_sentences", 3)
        self.open_in_browser = config.get("open_results_in_browser", True)

    def search_web(self, query: str) -> str:
        """Search DuckDuckGo and open in browser. Returns status message."""
        query = query.strip()
        if not query:
            return "Please give me something to search for."

        url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
        logger.info(f"Web search: {query}")

        if self.open_in_browser:
            try:
                webbrowser.open(url)
                return f"Showing search results for: {query}"
            except Exception as e:
                logger.error(f"Browser open failed: {e}")
                return f"Couldn't open browser. Search URL: {url}"
        else:
            return self._ddg_text_search(query)

    def _ddg_text_search(self, query: str) -> str:
        """Attempt a text-based DuckDuckGo instant answer lookup."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
            if results:
                top = results[0]
                return f"{top.get('title', '')}: {top.get('body', '')}"
            return "No results found."
        except ImportError:
            logger.warning("duckduckgo_search not installed. Falling back to browser.")
            webbrowser.open(f"https://duckduckgo.com/?q={query.replace(' ', '+')}")
            return f"Opening browser search for: {query}"
        except Exception as e:
            logger.error(f"DDG search error: {e}")
            return "Search failed. Try again."

    def search_wikipedia(self, query: str) -> str:
        """Look up a topic on Wikipedia and return a summary."""
        query = query.strip()
        if not query:
            return "What would you like me to look up on Wikipedia?"

        try:
            import wikipedia
            wikipedia.set_lang("en")
            logger.info(f"Wikipedia search: {query}")
            summary = wikipedia.summary(query, sentences=self.wiki_sentences, auto_suggest=True)
            # Clean up the summary a bit
            summary = re.sub(r'\s+', ' ', summary).strip()
            return f"According to Wikipedia: {summary}"
        except Exception as e:
            if "may refer to" in str(e) or "DisambiguationError" in type(e).__name__:
                return f"Wikipedia returned multiple results for '{query}'. Could you be more specific?"
            elif "PageError" in type(e).__name__:
                return f"I couldn't find a Wikipedia page for '{query}'."
            else:
                logger.error(f"Wikipedia error: {e}")
                return f"I had trouble searching Wikipedia for '{query}'."

    def open_youtube(self, query: str = "") -> str:
        if query:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)
            return f"Opening YouTube search for: {query}"
        else:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube."

    def open_url(self, url: str) -> str:
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opening {url}"
