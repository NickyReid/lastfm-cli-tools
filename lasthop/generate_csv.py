import os
import json
import math
import requests
import subprocess
import multiprocessing
from datetime import datetime, timedelta
from config.set_username import SetUsername
from config.config import Config

STATS_END_DATE = datetime.today()


class UserData:
    def __init__(self):
        self.api_key = Config.API_KEY
        self.username = SetUsername.set_username()

    def get_lastfm_user_data(self):
        api_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo" \
                  f"&user={self.username}" \
                  f"&api_key={self.api_key}" \
                  f"&format=json"
        api_response = requests.get(api_url).json()

        return {
            "username": self.username,
            # "join_date": datetime.fromtimestamp(float(api_response.get("user").get("registered").get("unixtime"))),
            "join_date": datetime.today() - timedelta(days=2),
            "real_name": api_response.get("user").get("realname"),
            "total_tracks": api_response.get("user").get("playcount")
        }


class FileWriter:

    def __init__(self, lastfm_username=None, lastfm_join_date=None):
        if not lastfm_username or not lastfm_join_date:
            lastfm_user_data = UserData().get_lastfm_user_data()
            lastfm_username = lastfm_user_data.get("username")
            lastfm_join_date = lastfm_user_data.get("join_date")
        self.username = lastfm_username
        self.join_date = lastfm_join_date
        print(f"Join date {self.join_date}")
        self.api_key = Config.API_KEY
        self.timezone_diff = self.get_timezone_diff()
        self.file_path = os.path.dirname(os.path.realpath(__file__)) + '/users/{username}'.format(
            username=self.username)
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        self.lyrics_file_path = os.path.dirname(os.path.realpath(__file__)) + '/users/{username}/lyricsstore'.format(
            username=self.username)
        if not os.path.exists(self.lyrics_file_path):
            os.makedirs(self.lyrics_file_path)

    def get_lastfm_user_data(self):
        api_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo" \
                  f"&user={self.username}" \
                  f"&api_key={self.api_key}" \
                  f"&format=json"

        api_response = requests.get(api_url).json()
        return {
            "join_date": datetime.fromtimestamp(float(api_response.get("user").get("registered").get("unixtime"))),
            "real_name": api_response.get("user").get("realname"),
            "total_tracks": api_response.get("user").get("playcount")
        }

    def process_data_for_all_days(self):
        jobs = []
        day = STATS_END_DATE
        while True:
            print(f"day - {day}")
            if day < self.join_date:
                break
            job = multiprocessing.Process(target=self.write_raw_file_for_day, args=(day,))
            jobs.append(job)
            job.start()
            day = day - timedelta(days=1)
        for job in jobs:
            job.join()
        self.write_formatted_file_for_all_days()

    def write_raw_files_for_each_day(self):
        days = self.get_list_of_dates()

        jobs = []
        for day in days:
            job = multiprocessing.Process(target=self.write_raw_file_for_day, args=(day,))
            jobs.append(job)
            job.start()
        for job in jobs:
            job.join()

    def get_list_of_dates(self):
        date_to_process = STATS_END_DATE
        days = []
        while date_to_process >= self.join_date:
            days.append(date_to_process)
            date_to_process = date_to_process.replace(year=date_to_process.year-1)
        return days

    def get_raw_data_for_day(self, date):
        raw_file_name = self.get_raw_filename_for_date(date)
        if not os.path.exists(raw_file_name) or os.stat(raw_file_name).st_size < 1 \
                or date.date() == datetime.today().date():
            self.write_raw_file_for_day(date)
        with open(raw_file_name, "r+") as file:
            result = file.read()
        return result

    # def write_formatted_files_for_all_days(self):
    #     for day in self.get_list_of_dates():
    #         self.write_formatted_file_for_day(date=day)

    def write_formatted_file_for_all_days(self):
        formatted_file_name = self.get_formatted_filename()
        day = STATS_END_DATE
        with open(formatted_file_name, "w+") as file:
            file.write("Year|Month|Weekday|Date|Artist name|Album name|Song title|Lyrics\n")
            while True:
                if day < self.join_date:
                    break
                raw_file_name = self.get_raw_filename_for_date(day)
                with open(raw_file_name, "r+") as raw_file:
                    raw_data = raw_file.read()
                    json_data = json.loads(raw_data)
                    if not json_data:
                        day = day - timedelta(days=1)
                        continue
                    for line in json_data:
                        if isinstance(line, dict):
                            artist = line.get('artist', {}).get('#text').replace("|", "")
                            title = line.get('name').replace("|", "")
                            album = line.get('album', {}).get('#text').replace("|", "")
                            play_date = line.get('date', {}).get('#text', (datetime.now() - timedelta(
                                hours=self.timezone_diff)).strftime("%d %b %Y, %H:%M"))
                            play_date_datetime = datetime.strptime(play_date, "%d %b %Y, %H:%M") + timedelta(
                                hours=self.timezone_diff)

                            play_date_formatted = (play_date_datetime.date()).strftime("%Y/%m/%d")
                            day_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                            lyrics = line.get("lyrics")
                            line_to_write = f"{play_date_datetime.year}|" \
                                            f"{play_date_datetime.month}|" \
                                            f"{day_list[play_date_datetime.weekday()]}|" \
                                            f"{play_date_formatted}|" \
                                            f"{artist}|" \
                                            f"{album}|" \
                                            f"{title}|" \
                                            f"{lyrics}" \

                            file.write(line_to_write + "\n")
                    print(f"Processed {raw_file_name}")
                print(f"wrote {formatted_file_name}")
                day = day - timedelta(days=1)

    def write_raw_file_for_day(self, date):
        print(f"Writing raw file for {date}")
        raw_file_name = self.get_raw_filename_for_date(date)
        if not self.file_needs_to_be_written(raw_file_name, date):
            return

        raw_data = self.get_lastfm_tracks_for_day(date)
        with open(raw_file_name, "w+") as file:
            if not raw_data:
                file.write("0")
            else:
                for line in raw_data:
                    artist = line.get('artist', {}).get('#text')
                    title = line.get('name')
                    lyrics = self.get_lyrics_for_track(title, artist)
                    line["lyrics"] = lyrics
                file.write(json.dumps(raw_data))
        print(f"Finished writing raw file for {date}")

    def get_lyrics_for_track(self, title, artist):
        lyric_file_name = self.get_lyrics_file_name(artist, title)
        if os.path.exists(lyric_file_name):
            print(f"getting lyrics from store")
            with open(lyric_file_name, "r+") as file:
                song_lyrics = file.read()
        else:
            print(f"Fetching lyrics from api")
            bash_command = f"songtext -t '{title}' -a '{artist}'"
            try:
                song_lyrics = subprocess.check_output(['bash', '-c', bash_command])
                print(f"Success fetching lyrics from api")
                if isinstance(song_lyrics, bytes):
                    song_lyrics = song_lyrics.decode("utf-8")
            except:
                print(f"Error fetching lyrics from api")
                song_lyrics = "null"
            if "Instrumental" in song_lyrics:
                song_lyrics = "Instrumental"
            elif song_lyrics.isspace() or len(song_lyrics) < 1:
                song_lyrics = "null"
            else:
                song_lines = song_lyrics.split("\n")
                for line in song_lines:
                    print(f"line {line}")
                if len(song_lines) > 2:
                    title_removed = song_lines[3:]
                    song_lyrics = " ".join(title_removed)
            with open(lyric_file_name, "w+") as file:
                file.write(song_lyrics)
        return song_lyrics

    def lastfm_api_query(self, date, page_num):
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

    def get_lastfm_tracks_for_day(self, date):
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

    def get_raw_filename_for_date(self, date):
        date_string = datetime.strftime(date, "%Y-%m-%d")
        return f"{self.file_path}/{date_string}raw.txt"

    def get_lyrics_file_name(self, artist, title):
        artist_track_string = f"{artist}{title}"
        artist_track_string = ''.join(e for e in artist_track_string if e.isalnum())[:35]
        return f"{self.lyrics_file_path}/{artist_track_string}.txt"

    def get_formatted_filename(self):
        return f"{self.file_path}/lastfmstats.csv"

    def get_filename_for_date(self, date):
        date_string = datetime.strftime(date, "%Y-%m-%d")
        return f"{self.file_path}/{date_string}.csv"

    @staticmethod
    def get_timezone_diff():
        """
        Get difference in hours from UTC timezone. Daylight savings makes this variable.
        :return: Timezone diff in hours
        """
        return datetime.now().hour - datetime.utcnow().hour

    @staticmethod
    def file_needs_to_be_written(file_name, date):
        """
        Check that the file exists and if it does, only re-write it if it's today's file.
        :param file_name:
        :return:
        """
        file_exists = os.path.exists(file_name) and os.stat(file_name).st_size > 0
        file_is_today = date.date() == datetime.today().date()
        return not (file_exists and not file_is_today)


if __name__ == '__main__':
    start_time = datetime.now()
    user_data = UserData().get_lastfm_user_data()
    username = user_data.get("username")
    join_date = user_data.get("join_date")

    file_writer = FileWriter(username, join_date)
    file_writer.process_data_for_all_days()

    print(f"\n(took {(datetime.now() - start_time).seconds} seconds)")


