"""
Cravias - Music Module
Plays local music files using VLC or MPV (Linux-native players).
Also supports opening YouTube Music / Spotify in the browser.
"""

import os
import subprocess
import random
import logging
import glob

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = (".mp3", ".flac", ".wav", ".ogg", ".m4a", ".opus", ".aac")


class MusicPlayer:
    def __init__(self, config: dict):
        self.music_dir = os.path.expanduser(config.get("local_dir", "~/Music"))
        self.preferred_player = config.get("preferred_player", "vlc")
        self._process = None
        self._player_cmd = self._find_player()

    def _find_player(self) -> str | None:
        """Find an available media player on the system."""
        for player in [self.preferred_player, "vlc", "mpv", "rhythmbox", "cvlc"]:
            try:
                result = subprocess.run(["which", player], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"Music player: {player}")
                    return player
            except Exception:
                continue
        logger.warning("No media player found. Install vlc or mpv.")
        return None

    def _get_songs(self) -> list:
        """Get all music files from the music directory."""
        if not os.path.exists(self.music_dir):
            logger.warning(f"Music directory not found: {self.music_dir}")
            return []
        songs = []
        for ext in SUPPORTED_EXTENSIONS:
            songs.extend(glob.glob(os.path.join(self.music_dir, f"**/*{ext}"), recursive=True))
        return songs

    def play(self, query: str = "") -> str:
        """Play music. If query given, find matching track. Otherwise shuffle."""
        songs = self._get_songs()

        if not songs:
            return f"No music found in {self.music_dir}. Try adding some songs or asking me to open YouTube Music."

        if not self._player_cmd:
            return "No media player found. Please install vlc or mpv."

        # Find matching song
        target = None
        if query:
            query_lower = query.lower()
            for song in songs:
                if query_lower in os.path.basename(song).lower():
                    target = song
                    break
            if not target:
                return f"I couldn't find a song matching '{query}'. Playing a random track instead."

        target = target or random.choice(songs)
        song_name = os.path.splitext(os.path.basename(target))[0]

        self.stop()  # Stop any current playback
        self._launch_player(target)
        return f"Playing: {song_name}"

    def _launch_player(self, path: str):
        try:
            if self._player_cmd in ("vlc", "cvlc"):
                # cvlc = VLC without GUI
                cmd = ["cvlc", "--play-and-exit", path]
                if self._player_cmd == "vlc":
                    cmd = ["vlc", path]
            elif self._player_cmd == "mpv":
                cmd = ["mpv", "--no-video", path]
            else:
                cmd = [self._player_cmd, path]

            self._process = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            logger.info(f"Playing: {path}")
        except Exception as e:
            logger.error(f"Player launch error: {e}")

    def stop(self) -> str:
        """Stop current playback."""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            self._process = None
            return "Music stopped."
        return "Nothing is playing right now."

    def shuffle(self) -> str:
        """Play a random song."""
        return self.play()

    def open_youtube_music(self) -> str:
        import webbrowser
        webbrowser.open("https://music.youtube.com")
        return "Opening YouTube Music in your browser."

    def open_spotify(self) -> str:
        import webbrowser
        webbrowser.open("https://open.spotify.com")
        return "Opening Spotify in your browser."

    def list_songs(self) -> str:
        songs = self._get_songs()
        if not songs:
            return f"No songs found in {self.music_dir}."
        names = [os.path.splitext(os.path.basename(s))[0] for s in songs[:10]]
        result = f"Found {len(songs)} songs. Here are some: " + ", ".join(names)
        if len(songs) > 10:
            result += f", and {len(songs) - 10} more."
        return result
