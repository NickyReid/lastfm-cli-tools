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
import raw_file_writer
from shared.config import Config


class Consolidator:

    def __init__(self, start_date: datetime = None, end_date: datetime = datetime.today(),
                 interval: raw_file_writer.Interval = raw_file_writer.Interval.YEAR.value, include_lyrics: bool = False):
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
        self.username = lastfm_username
        self.api_key = Config.API_KEY
        self.lyrics_file_path = Config.RAW_DATA_PATH + '/users/{username}/lyricsstore'.format(
            username=self.username)
        if not os.path.exists(self.lyrics_file_path):
            os.makedirs(self.lyrics_file_path)
        self.raw_file_writer = raw_file_writer.RawFileWriter(interval=raw_file_writer.Interval.DAY.value,
                                                             include_lyrics=True)

    def process_data_for_all_days(self):
        """
        Use multiprocessing to fetch listening data for time range
        """
        list_of_days = self.raw_file_writer.get_list_of_dates()
        pool = multiprocessing.Pool()
        for day in list_of_days:
            pool.apply_async(self.consolidate_last_fm_data, args=(day,))
        pool.close()
        pool.join()

    def consolidate_last_fm_data(self, day):
        print(day.date())
        raw_file_name = self.raw_file_writer.get_raw_filename_for_date(day)
        with open(raw_file_name, "r+") as raw_file:
            raw_data = raw_file.read()
            json_data = json.loads(raw_data)
            if not json_data:
                return
            for line in json_data:
                if line.get("lyrics") in [None, "null"]:
                    artist = line.get('artist', {}).get('#text')
                    title = line.get('name')
                    if "[live]" in title.lower():
                        print("LIVE removed")
                        title = title.replace("[live]", "")
                    elif "(live)" in title.lower():
                        print("LIVE removed")
                        title = title.replace("(live", "")
                    lyrics = self.get_lyrics_for_track(title, artist)
                    line["lyrics"] = lyrics
                    raw_file.write(json.dumps(json_data))

    def get_lyrics_for_track(self, title, artist):
        lyric_file_name = self.raw_file_writer.get_lyrics_file_name(artist, title)
        if os.path.exists(lyric_file_name):
            with open(lyric_file_name, "r+") as file:
                song_lyrics = file.read()
            if len(song_lyrics) < 1 or song_lyrics == "null":
                self.get_song_lyrics_from_songtext_api(title, artist)
        else:
            print(f"{lyric_file_name} doesnt exist. Fetching")
            return self.get_song_lyrics_from_songtext_api(title, artist)

    def get_song_lyrics_from_songtext_api(self, title, artist):
        lyric_file_name = self.raw_file_writer.get_lyrics_file_name(artist, title)
        stripped_title = title.replace('"', "'")
        stripped_artist = artist.replace('"', "'")
        bash_command = f'songtext -t "{stripped_title}" -a "{stripped_artist}"'
        song_lyrics = "Null"
        try:
            song_lyrics = subprocess.check_output(['bash', '-c', bash_command])
            print(f"Success fetching {artist} - {title} lyrics from api")
            if isinstance(song_lyrics, bytes):
                song_lyrics = song_lyrics.decode("utf-8")
        except requests.exceptions.ConnectionError as e:
            print(f"CONNECTION ERROR: {e}")
            song_lyrics = "null"
        except Exception as e:
            if "non-zero" not in str(e):
                print(f"EXCEPTION: {e}")
                song_lyrics = "null"
        if "Instrumental" in song_lyrics:
            song_lyrics = "Instrumental"
        elif not song_lyrics.isspace() and not len(song_lyrics) < 1 and not song_lyrics.lower() == "null":
            song_lines = song_lyrics.split("\n")
            if len(song_lines) > 2:
                title_removed = song_lines[3:]
                song_lyrics = " ".join(title_removed)
            print(f"{lyric_file_name} was fucked up. it's fixed now.")
        with open(lyric_file_name, "w+") as file:
            file.write(song_lyrics)
        return song_lyrics


if __name__ == '__main__':
    start_time = datetime.now()

    start_date = datetime.today() - timedelta(days=2)
    consolidator = Consolidator()
    consolidator.process_data_for_all_days()


    print(f"\n(took {(datetime.now() - start_time).seconds} seconds)")

