import os
import json
import lyricsgenius
import urllib.request, urllib.error, urllib.parse
from shared.config import Config
from shared.set_username import SetUsername
from fortunelyrics.genius_client import GeniusClient

def go():
    SingThis.run()


class SingThis:
    def __init__(self):
        self.api_key = Config.API_KEY
        self.username = SetUsername.set_username()
        self.api_url = (
            "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="
            "{user}&limit=1&api_key={api_key}&format=json".format(
                user=self.username, api_key=self.api_key
            )
        )

    def get_song(self):
        response = json.loads(urllib.request.urlopen(self.api_url).read())
        if response.get("message"):
            raise Exception(response.get("message"))
        track_name = (
            response.get("recenttracks")
            .get("track")[0]
            .get("name")
            .replace(")", "")
            .replace("(", "")
            .replace("'", "")
        )
        track_artist = (
            response.get("recenttracks")
            .get("track")[0]
            .get("artist")
            .get("#text")
            .replace(")", "")
            .replace("(", "")
            .replace("'", "")
        )
        return GeniusClient.get_lyrics(track_artist, track_name)

    @classmethod
    def run(cls):
        print(SingThis().get_song())


if __name__ == "__main__":
    SingThis.run()
