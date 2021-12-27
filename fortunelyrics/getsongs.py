import json
import urllib.request
import urllib.error
import urllib.parse
import sys
import subprocess
import random
import os
import lyricsgenius
import multiprocessing
from shared.config import Config
from profanity import profanity
from datetime import datetime
from shared.set_username import SetUsername


def go():
    SongGetter.run()


class SongGetter:
    def __init__(self, username):
        self.username = username if username else open("config/defaultuser", "r").read()
        self.clean = Config.CLEAN  # SFW option, doesn't write songs with swearing
        self.api_key = Config.API_KEY
        self.top_tracks_limit = Config.TOP_TRACKS_LIMIT
        self.loved_or_top = random.randint(0, 2)
        self.top_tracks_period = Config.TOP_TRACKS_PERIOD

        if "random" in self.top_tracks_period.lower():
            self.top_tracks_period = random.choice(Config.TOP_TRACKS_PERIOD_OPTIONS)

        self.lyric_stash_path = Config.LYRIC_STASH_PATH

        if not os.path.exists(self.lyric_stash_path):
            os.makedirs(self.lyric_stash_path)
        self.new_file_name = self.get_new_file()
        self.lyrics_file = None

        self.api_url = self.get_api_url()

    def get_api_url(self):
        """
        Queries api for either Top Tracks or Loved Tracks from the user
        :return: api url
        """
        self.loved_or_top = random.randint(0, 2)
        if self.loved_or_top == 0:
            api_url = (
                "http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user="
                "{username}&api_key={api_key}&format=json".format(
                    username=self.username, api_key=self.api_key
                )
            )
        else:
            api_url = (
                "http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user="
                "{username}&api_key={api_key}&limit={top_tracks_limit}"
                "&period={top_tracks_period}&format=json".format(
                    username=self.username,
                    api_key=self.api_key,
                    top_tracks_limit=self.top_tracks_limit,
                    top_tracks_period=self.top_tracks_period,
                )
            )
        return api_url

    def get_new_file(self):
        new_file_number = random.randint(0, 9000)
        new_file_name = self.lyric_stash_path + "/{filenum}".format(
            filenum=str(new_file_number)
        )
        try:
            if os.path.getsize(new_file_name) > 0:
                new_file_name = self.lyric_stash_path + "/{filenum}".format(
                    filenum=str(new_file_number + 1)
                )
        except OSError:
            pass
        return new_file_name

    def get_random_song(self):
        response = json.loads(urllib.request.urlopen(self.api_url).read())
        tracks = (
            response.get("lovedtracks").get("track")
            if self.loved_or_top == 0
            else response.get("toptracks").get("track")
        )
        track_name, track_artist = self.pick_song_from_list(tracks)
        return track_name, track_artist

    def pick_song_from_list(self, tracks):
        random_track = random.choice(tracks)
        try:
            track_name = (
                random_track.get("name")
                .replace(")", "")
                .replace("(", "")
                .replace("'", "")
            )
            track_artist = random_track.get("artist").get("name")
        except AttributeError:
            (track_name, track_artist) = self.pick_song_from_list(tracks)
        return track_name, track_artist

    def get_lyrics(self):
        try:
            track_name, track_artist = self.get_random_song()
            genius = lyricsgenius.Genius(os.getenv("GENIUS_ACCESS_TOKEN"))
            song = genius.search_song(track_name, track_artist)
            if song:
                song_lyrics = song.lyrics
                if (
                    "Instrumental" in song_lyrics
                    or song_lyrics.isspace()
                    or len(song_lyrics) < 30
                ):
                    return self.get_lyrics()
                else:
                    return song_lyrics
            else:
                return self.get_lyrics()
        except (subprocess.CalledProcessError, TypeError) as e:
            return self.get_lyrics()

    def write_file(self, song_lyrics):
        lines = song_lyrics.splitlines()
        random_line_number = random.randint(0, len(lines))
        stanza_to_write = ""
        for i in range(random_line_number, random_line_number + 4):
            try:
                line = lines[i]
                if (
                    line.strip()
                    and not line.isspace()
                    and len(line) > 1
                    and ("[" not in line and "]" not in line)
                ):
                    line.replace("EmbedShare", "").replace("URLCopyEmbedCopy", "")
                    stanza_to_write += line + "\n"
            except IndexError:
                pass
        if self.clean is True and (
            profanity.contains_profanity(stanza_to_write)
            or stanza_to_write.lower() in Config.SWEARS
        ):
            pass
        else:
            self.lyrics_file = open(self.new_file_name, "ab+")
            self.lyrics_file.write(stanza_to_write.encode("utf-8"))
            self.lyrics_file.close()
            if os.path.getsize(self.new_file_name) < 1:
                os.remove(self.new_file_name)

    def process_data(self):
        lyrics = self.get_lyrics()
        self.write_file(lyrics)

    @classmethod
    def run(cls):

        start_time = datetime.now()
        username = SetUsername.set_username()

        try:
            count = int(sys.argv[1])
        except IndexError:
            count = 1

        jobs = []
        for i in range(count):
            p = multiprocessing.Process(target=SongGetter(username).process_data)
            jobs.append(p)
            p.start()

        for job in jobs:
            job.join()

        end_time = datetime.now()
        print("(took {time} seconds)".format(time=(end_time - start_time).seconds))


if __name__ == "__main__":
    SongGetter.run()
