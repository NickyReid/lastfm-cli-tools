import os
import json
import lyricsgenius
import urllib.request, urllib.error, urllib.parse
import subprocess
from shared.config import Config
from shared.set_username import SetUsername


def go():
    SingThis.run()


class SingThis:

    def __init__(self):
        self.api_key = Config.API_KEY
        self.username = SetUsername.set_username()
        self.api_url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" \
                       "{user}&limit=1&api_key={api_key}&format=json".format(user=self.username,api_key=self.api_key)

    def get_song(self):
        response = json.loads(urllib.request.urlopen(self.api_url).read())
        if response.get("message"):
            raise Exception(response.get("message"))
        track_name = response.get("recenttracks").get("track")[0].get("name")\
            .replace(')', '').replace('(', '').replace("'", "")
        track_artist = response.get("recenttracks").get("track")[0].get("artist").get("#text")\
            .replace(')', '').replace('(', '').replace("'", "")
        genius = lyricsgenius.Genius(os.getenv("GENIUS_ACCESS_TOKEN"))
        song = genius.search_song(track_name, track_artist)
        if song:
            return song.lyrics.replace("EmbedShare", "").replace("URLCopyEmbedCopy", "")

    @classmethod
    def run(cls):
        print(SingThis().get_song())


if __name__ == '__main__':
    SingThis.run()
