import requests
from datetime import datetime
from shared.config import Config
from shared.set_username import SetUsername


class UserData:
    def __init__(self):
        self.api_key = Config.API_KEY
        self.username = SetUsername.set_username()

    def get_lastfm_user_data(self):
        """
        Get the User's Last.fm profile information
        :return: Dict with user's username, join date, real name and total number of tracks played
        """
        api_url = (
            f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo"
            f"&user={self.username}"
            f"&api_key={self.api_key}"
            f"&format=json"
        )
        api_response = requests.get(api_url).json()

        return {
            "username": self.username,
            "join_date": datetime.fromtimestamp(
                float(api_response.get("user").get("registered").get("unixtime"))
            ),
            "real_name": api_response.get("user").get("realname"),
            "total_tracks": int(api_response.get("user").get("playcount")),
        }
