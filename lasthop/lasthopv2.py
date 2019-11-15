import os
import csv
import json
import math
import requests
import multiprocessing
from datetime import datetime, timedelta
from config.set_username import SetUsername
from config.config import Config

STATS_DATE_ANCHOR = datetime.today() - timedelta(days=31)
# STATS_DATE_ANCHOR = datetime.today()


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
            "join_date": datetime.fromtimestamp(float(api_response.get("user").get("registered").get("unixtime"))),
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
        self.api_key = Config.API_KEY
        self.timezone_diff = self.get_timezone_diff()
        self.file_path = os.path.dirname(os.path.realpath(__file__)) + '/users/{username}'.format(
            username=self.username)
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)

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
        days = self.get_list_of_dates()
        jobs = []
        for day in days:
            job = multiprocessing.Process(target=self.write_raw_file_and_formatted_file_for_day, args=(day,))
            jobs.append(job)
            job.start()
        for job in jobs:
            job.join()

    def write_raw_file_and_formatted_file_for_day(self, day):
        self.write_raw_file_for_day(day)
        self.write_formatted_file_for_day(day)

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
        date_to_process = STATS_DATE_ANCHOR
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

    def write_formatted_files_for_all_days(self):
        for day in self.get_list_of_dates():
            self.write_formatted_file_for_day(date=day)

    def write_formatted_file_for_day(self, date):
        formatted_file_name = self.get_formatted_filename_for_date(date)
        if not self.file_needs_to_be_written(formatted_file_name, date):
            return

        raw_file_name = self.get_raw_filename_for_date(date)
        with open(raw_file_name, "r+") as file:
            raw_data = file.read()
        json_data = json.loads(raw_data)

        with open(formatted_file_name, "w+") as file:
            if not json_data:
                file.write("0")
                return
            for line in json_data:
                if isinstance(line, dict):
                    artist = line.get('artist', {}).get('#text').replace("|", "")
                    title = line.get('name').replace(",", "")
                    play_date = line.get('date', {}).get('#text', (datetime.now() - timedelta(
                        hours=self.timezone_diff)).strftime("%d %b %Y, %H:%M"))
                    play_date_datetime = datetime.strptime(play_date, "%d %b %Y, %H:%M")
                    if self.timezone_diff != 0:
                        play_date_datetime = play_date_datetime + timedelta(hours=self.timezone_diff)
                    play_date_formatted = play_date_datetime.strftime("%Y/%m/%d %H:%M:%S")
                    line_to_write = f"{artist}|{title}|{play_date_formatted}"
                    file.write(line_to_write + "\n")

    def write_raw_file_for_day(self, date):
        raw_file_name = self.get_raw_filename_for_date(date)
        if not self.file_needs_to_be_written(raw_file_name, date):
            return

        raw_data = self.get_lastfm_tracks_for_day(date)
        with open(raw_file_name, "w+") as file:
            if not raw_data:
                file.write("0")
            else:
                file.write(json.dumps(raw_data))

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

    def get_formatted_filename_for_date(self, date):
        date_string = datetime.strftime(date, "%Y-%m-%d")
        return f"{self.file_path}/{date_string}.csv"

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


class StatsCompiler:
    def __init__(self, lastfm_username=None, lastfm_join_date=None):
        if not lastfm_username or not lastfm_join_date:
            lastfm_user_data = UserData().get_lastfm_user_data()
            lastfm_username = lastfm_user_data.get("username")
            lastfm_join_date = lastfm_user_data.get("join_date")
        self.username = lastfm_username
        self.join_date = lastfm_join_date
        self.file_path = os.path.dirname(os.path.realpath(__file__)) + '/users/{username}'.format(
            username=self.username)
        if not os.path.exists(self.file_path):
            print(f"No data found for {self.username}")
        self.yearly_data_dict = self.compile_stats()

    def compile_stats(self):
        days = self.get_list_of_dates()
        yearly_data_dict = {}
        for day in days:
            yearly_data_dict[day] = self.read_file_for_day(day)
        return yearly_data_dict

    def all_artists(self):
        days = self.get_list_of_dates()
        result = []
        for day in days:
            result.append(self.all_artists_for_date(day))
        return result

    def all_artists_for_date(self, date):
        day_data_dict = self.yearly_data_dict.get(date)
        if day_data_dict:
            artist

    def most_played_artists(self):
        days = self.get_list_of_dates()
        result = []
        for day in days:
            result.append(self.most_played_artist_for_date(day))
        return result

    def most_played_artist_for_date(self, date):
        day_data_dict = self.yearly_data_dict.get(date)
        if day_data_dict:
            highest_playcount = max(day_data_dict, key=lambda x: len(set(day_data_dict[x])))
            day_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            count = len(day_data_dict.get(highest_playcount))
            artist = highest_playcount.split("|")[0]
            return f"{date.year} ({day_list[date.weekday()]}): {artist} ({count})"

    def read_file_for_day(self, day):
        track_time_stamp_dict = {}
        with open(self.get_filename_for_date(day), "r+") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='|')
            for row in csv_reader:
                if row[0] == "0":
                    break
                artist = row[0]
                title = row[1]
                timestamp = row[2]
                artist_track = f"{artist} | {title}"
                if not track_time_stamp_dict.get(artist_track):
                    track_time_stamp_dict[artist_track] = [timestamp]
                else:
                    timestamp_list = track_time_stamp_dict.get(artist_track)
                    timestamp_list.append(timestamp)
                    track_time_stamp_dict[artist_track] = timestamp_list
        return track_time_stamp_dict



    def get_list_of_dates(self):
        date_to_process = STATS_DATE_ANCHOR
        days = []
        while date_to_process >= self.join_date:
            days.append(date_to_process)
            date_to_process = date_to_process.replace(year=date_to_process.year-1)
        return days

    def get_filename_for_date(self, date):
        date_string = datetime.strftime(date, "%Y-%m-%d")
        return f"{self.file_path}/{date_string}.csv"


class StatsPresenter:

    def __init__(self, lastfm_user_data):
        self.user_data = lastfm_user_data
        self.join_date = self.user_data.get("join_date")
        self.total_tracks = int(self.user_data.get("total_tracks"))
        self.avg_daily_tracks = int(self.total_tracks / (STATS_DATE_ANCHOR - self.join_date).days)
        self.stats_compiler = StatsCompiler(self.user_data.get("username"))

    def present(self):
        intro = f"\n{self.user_data.get('real_name')} has been on Last.fm for " \
                f"{(STATS_DATE_ANCHOR.year - self.join_date.year)} years.\n" \
                f"They've played {self.user_data.get('total_tracks')} tracks.\n" \
                f"That's an average of {self.avg_daily_tracks} track{'s' if self.avg_daily_tracks > 1 else ''} per day." \
                f"\n"
        print(intro)
        print(f"- - - - - - - - - - - - - {STATS_DATE_ANCHOR.strftime('%B %-d')} - - - - - - - - - - - - - -\n")
        print("- - - - - - - - - - - Most Played Artists - - - - - - - - - - - -")
        for most_played in self.stats_compiler.most_played_artists():
            if most_played:
                print(most_played)
        print("- - - - - - - - - - - - - All Artists - - - - - - - - - - - - - - -")


if __name__ == '__main__':
    start_time = datetime.now()
    user_data = UserData().get_lastfm_user_data()
    username = user_data.get("username")
    join_date = user_data.get("join_date")

    file_writer = FileWriter(username, join_date)
    file_writer.process_data_for_all_days()

    StatsPresenter(user_data).present()
    print(f"\n(took {(datetime.now() - start_time).seconds} seconds)")


