import os
import lyricsgenius


class GeniusClient:
    @classmethod
    def get_lyrics(cls, track_artist, track_name):
        genius = lyricsgenius.Genius(os.getenv("GENIUS_ACCESS_TOKEN"))
        song = genius.search_song(track_name, track_artist)
        if song:
            song_lyrics = song.lyrics
            if (
                "Instrumental" in song_lyrics
                or song_lyrics.isspace()
                or len(song_lyrics) < 30
            ):
                return None
            else:
                lines = song_lyrics.splitlines()
                for keyword in ["EmbedShare", "URLCopyEmbedCopy"]:
                    for idx, line in enumerate(lines):
                        if keyword in line:
                            line = line.replace(keyword, "")
                            line = ''.join([i for i in line if not i.isdigit()])
                            lines[idx] = line
                return "\n".join(lines)
        else:
            return None
