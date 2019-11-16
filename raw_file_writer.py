"""
Get data from Last.fm api and save to disk
"""
import os
import json
import math
import enum
import requests
import subprocess
import multiprocessing
import lastfm_user_data as lud
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from shared.config import Config


class Interval(enum.Enum):
    DAY = "day"
    YEAR = "year"


class RawFileWriter:

    def __init__(self, start_date: datetime = None, end_date: datetime = datetime.today(),
                 interval: Interval = Interval.YEAR.value, include_lyrics: bool = False):
        """
        :param start_date: Earliest date to get data for. Default to the day the user joined Last.fm
        :param end_date: Latest date to get data for. Default to today.
        :param interval: Interval of dates to get data for. Default to Yearly.
        :param include_lyrics: Fetch lyrics for songs. Default False.
        """
        lastfm_user_data = lud.UserData().get_lastfm_user_data()
        lastfm_username = lastfm_user_data.get("username")
        lastfm_join_date = lastfm_user_data.get("join_date")
        self.stats_start_date = start_date if start_date else lastfm_join_date
        self.stats_end_date = end_date
        self.interval = interval
        self.include_lyrics = include_lyrics
        print(f"Stats start date: {self.stats_start_date.date()}")
        print(f"Stats end date: {self.stats_end_date.date()}")
        print(f"Stats interval: {self.interval}")
        print(f"Include lyrics: {self.include_lyrics}")

        self.username = lastfm_username
        self.api_key = Config.API_KEY
        self.timezone_diff = self.get_timezone_diff()
        self.file_path = f"{Config.RAW_DATA_PATH}/users/{self.username}"
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        self.lyrics_file_path = Config.RAW_DATA_PATH + '/users/{username}/lyricsstore'.format(
            username=self.username)
        if not os.path.exists(self.lyrics_file_path):
            os.makedirs(self.lyrics_file_path)

    def process_data_for_all_days(self):
        """
        Use multiprocessing to fetch listening data for time range
        """
        list_of_days = self.get_list_of_dates()
        pool = multiprocessing.Pool()
        for day in list_of_days:
            pool.apply_async(self.write_raw_file_for_day, args=(day,))
        pool.close()
        pool.join()

    def get_list_of_dates(self):
        days = []
        day = self.stats_end_date
        while day >= self.stats_start_date:
            days.append(day)
            if self.interval == Interval.YEAR.value:
                day = day - relativedelta(years=1)
            elif self.interval == Interval.DAY.value:
                day = day - timedelta(days=1)
            else:
                raise ValueError(f"{self.interval} is not a valid interval")
        return days

    def write_raw_file_for_day(self, date: datetime):
        """
        Get data for specific day from Last.fm API and write to a file. If self.include_lyrics is True, fetch lyrics
        from Songtext api.
        :param date: Day for which to get data for
        """

        raw_file_name = self.get_raw_filename_for_date(date)
        if not self.file_needs_to_be_written(raw_file_name, date):
            return
        print(f'STARTING writing raw file for {date.date()}')
        raw_data = self.get_lastfm_tracks_for_day(date)
        with open(raw_file_name, "w+") as file:
            if not raw_data:
                file.write("0")
            else:
                for line in raw_data:
                    artist = line.get('artist', {}).get('#text')
                    title = line.get('name')
                    if "[live]" in title.lower():
                        title = title.replace("[live]", "")
                    elif "(live)" in title.lower():
                        title = title.replace("(live", "")
                    if self.include_lyrics:
                        lyrics = self.get_lyrics_for_track(title, artist)
                        line["lyrics"] = lyrics
                file.write(json.dumps(raw_data))
        print(f"FINISHED writing raw file for {date.date()}")

    def get_lyrics_for_track(self, title: str, artist: str) -> str or None:
        """
        Get song lyrics from Songtext api and write to file. If lyrics have been saved previously, return lyrics from
        file.
        :param title: Song title
        :param artist: Song artist
        :return: Song lyrics
        """
        lyric_file_name = self.get_lyrics_file_name(artist, title)
        if os.path.exists(lyric_file_name):
            print(f"Got  {artist} - {title}  from cache")
            with open(lyric_file_name, "r+") as file:
                song_lyrics = file.read()
        else:
            stripped_title = title.replace('"', "'")
            stripped_artist = artist.replace('"', "'")
            bash_command = f'songtext -t "{stripped_title}" -a "{stripped_artist}"'
            try:
                song_lyrics = subprocess.check_output(['bash', '-c', bash_command])
                print(f"Success fetching {artist} - {title} lyrics from api")
                if isinstance(song_lyrics, bytes):
                    song_lyrics = song_lyrics.decode("utf-8")
            except requests.exceptions.ConnectionError:
                return None
            except Exception:
                song_lyrics = "null"
            if "Instrumental" in song_lyrics:
                song_lyrics = "Instrumental"
            elif song_lyrics.isspace() or len(song_lyrics) < 1:
                song_lyrics = "null"
            else:
                song_lines = song_lyrics.split("\n")
                if len(song_lines) > 2:
                    title_removed = song_lines[3:]
                    song_lyrics = " ".join(title_removed)
            with open(lyric_file_name, "w+") as file:
                file.write(song_lyrics)
        return song_lyrics

    def lastfm_api_query(self, date: datetime, page_num: int) -> dict:
        """
        Get data from Last.fm api
        :param date: Day for which to get data
        :param page_num: Page number.
        :return: JSON response from API.
        """
        date_start = date.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)
        date_start_epoch = int(date_start.timestamp())
        date_end_epoch = int(date_start.replace(hour=23).replace(minute=59).replace(second=59).timestamp())
        api_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks" \
                  f"&user={self.username}&" \
                  f"api_key=8257fbe241e266367f27e30b0e866aba&" \
                  f"&from={date_start_epoch}" \
                  f"&to={date_end_epoch}" \
                  f"&limit=200" \
                  f"&page={page_num}" \
                  f"&format=json"
        response = requests.get(api_url).json()
        return response

    def get_lastfm_tracks_for_day(self, date: datetime) -> list:
        """
        Get and format Last.fm data into a list of dictionaries.
        :param date: Day for which to get data
        :return: List of track information dictionaries
        """
        lastfm_response = self.lastfm_api_query(date, 1)
        lastfm_tracks = lastfm_response.get("recenttracks", {}).get("track")
        total_track_count = lastfm_response.get("recenttracks", {}).get("total", 0)
        num_pages = math.ceil(total_track_count / 200)
        if num_pages > 1:
            for page_num in range(2, num_pages + 1):
                lastfm_response = self.lastfm_api_query(date, page_num)
                lastfm_tracks.extend(lastfm_response.get("recenttracks", {}).get("track"))
        if lastfm_tracks:
            if isinstance(lastfm_tracks, dict):
                lastfm_tracks = [lastfm_tracks]

            if lastfm_tracks and len(lastfm_tracks) > 0:
                #  Remove currently playing song from past results
                if lastfm_tracks[0].get("@attr", {}).get("nowplaying", False) \
                        and date.date() != datetime.today().date():
                    del lastfm_tracks[0]
                #  Remove duplicated playing song from current results
                elif lastfm_tracks[0].get("@attr", {}).get("nowplaying", False) \
                        and date.date() == datetime.today().date() \
                        and len(lastfm_tracks) > 1 \
                        and lastfm_tracks[0].get("name") == lastfm_tracks[1].get("name"):
                    del lastfm_tracks[0]
        return lastfm_tracks

    def get_raw_filename_for_date(self, date: datetime) -> str:
        """
        Get file path and name for a date's raw data file
        :param date: Date of file data
        :return: Filepath
        """
        date_string = datetime.strftime(date, "%Y-%m-%d")
        return f"{self.file_path}/{date_string}raw.txt"

    def get_lyrics_file_name(self, artist, title) -> str:
        """
        Get file path and name for lyrics
        :param artist: Song artist
        :param title: Song title
        :return: Filepath
        """
        artist_track_string = f"{artist}{title}"
        artist_track_string = ''.join(e for e in artist_track_string if e.isalnum())[:35]
        return f"{self.lyrics_file_path}/{artist_track_string}.txt"

    @staticmethod
    def get_timezone_diff() -> int:
        """
        Get difference in hours from UTC timezone.
        :return: Timezone diff in hours
        """
        return datetime.now().hour - datetime.utcnow().hour

    @staticmethod
    def file_needs_to_be_written(file_name: str, date: datetime) -> bool:
        """
        Check that the file exists and if it does, only re-write it if it's today's file.
        :param file_name:
        :param date:
        :return: if the file needs to be written
        """
        file_exists = os.path.exists(file_name) and os.stat(file_name).st_size > 0
        file_is_today = date.date() == datetime.today().date()
        return not (file_exists and not file_is_today)


if __name__ == '__main__':
    start_time = datetime.now()

    start_date = datetime.today() - timedelta(days=2)
    file_writer = RawFileWriter()
    file_writer.process_data_for_all_days()

    print(f"\n(took {(datetime.now() - start_time).seconds} seconds)")


