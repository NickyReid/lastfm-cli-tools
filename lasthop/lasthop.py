import os
import csv
import json
import multiprocessing
import raw_file_writer
import lastfm_user_data as lud
from datetime import datetime, timedelta
from shared.config import Config

# STATS_START_DATE = datetime.today() - timedelta(days=1)
STATS_START_DATE = datetime.today()


class FormattedFileWriter:

    def __init__(self, lastfm_username, lastfm_join_date):
        self.username = lastfm_username
        self.join_date = lastfm_join_date
        self.api_key = Config.API_KEY
        self.timezone_diff = self.get_timezone_diff()
        self.raw_data_path = f"{Config.RAW_DATA_PATH}/users/{self.username}"
        self.file_path = os.path.dirname(os.path.realpath(__file__)) + '/users/{username}'.format(
            username=self.username)
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        self.raw_file_writer = raw_file_writer.RawFileWriter(start_date=self.join_date,
                                                             end_date=STATS_START_DATE,
                                                             interval=raw_file_writer.Interval.YEAR.value,
                                                             include_lyrics=False)

    def format_data_for_all_days(self):
        days = self.get_list_of_dates()
        jobs = []
        for day in days:
            job = multiprocessing.Process(target=self.write_files_for_day, args=(day,))
            jobs.append(job)
            job.start()
        for job in jobs:
            job.join()

    def write_files_for_day(self, day):
        self.raw_file_writer.write_raw_file_for_day(day)
        self.write_formatted_file_for_day(day)

    def get_list_of_dates(self):
        date_to_process = STATS_START_DATE
        days = []
        while date_to_process >= self.join_date:
            days.append(date_to_process)
            date_to_process = date_to_process.replace(year=date_to_process.year-1)
        return days

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
                    play_date_datetime = datetime.strptime(play_date, "%d %b %Y, %H:%M") + timedelta(
                        hours=self.timezone_diff)
                    play_date_formatted = play_date_datetime.strftime("%Y/%m/%d %H:%M:%S")
                    line_to_write = f"{artist}|{title}|{play_date_formatted}"
                    file.write(line_to_write + "\n")

    def get_raw_filename_for_date(self, date):
        date_string = datetime.strftime(date, "%Y-%m-%d")
        return f"{self.raw_data_path}/{date_string}raw.txt"

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
    def __init__(self, lastfm_username, lastfm_join_date):
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
        artist_playcount_dict = self.get_artist_playcount_dict_for_date(date)
        if artist_playcount_dict:
            print(f"* - {date.year} - *")
            for artist in sorted(artist_playcount_dict, key=artist_playcount_dict.__getitem__, reverse=True):
                print("\t{artist}: {plays}".format(artist=artist.replace('&#39;', '`'),
                                                   plays=artist_playcount_dict.get(artist)))

    def most_played_artists(self):
        days = self.get_list_of_dates()
        result = []
        for day in days:
            result.append(self.most_played_artist_for_date(day))
        return result

    def most_played_artist_for_date(self, date):
        artist_playcount_dict = self.get_artist_playcount_dict_for_date(date)
        if artist_playcount_dict:
            highest_playcount = max(artist_playcount_dict, key=artist_playcount_dict.get)
            day_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            count = artist_playcount_dict.get(highest_playcount)
            artist = highest_playcount.split("|")[0]
            return f"{date.year} ({day_list[date.weekday()]}): {artist} ({count})"

    def get_artist_playcount_dict_for_date(self, date):
        day_data_dict = self.yearly_data_dict.get(date)
        artist_playcount_dict = {}
        if day_data_dict:
            for entry in day_data_dict:
                artist_name = entry.split("|")[0]
                if not artist_playcount_dict.get(artist_name):
                    artist_playcount_dict[artist_name] = 1
                else:
                    artist_playcount_dict[artist_name] += 1
        return artist_playcount_dict

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
        date_to_process = STATS_START_DATE
        days = []
        while date_to_process >= self.join_date:
            days.append(date_to_process)
            date_to_process = date_to_process.replace(year=date_to_process.year-1)
        return days

    def get_filename_for_date(self, date):
        date_string = datetime.strftime(date, "%Y-%m-%d")
        return f"{self.file_path}/{date_string}.csv"


class StatsPresenter:

    def __init__(self, usermame, real_name, join_date, total_tracks):
        self.username = usermame
        self.real_name = real_name
        self.join_date = join_date
        self.total_tracks = total_tracks
        self.avg_daily_tracks = int(self.total_tracks / (STATS_START_DATE - self.join_date).days)
        self.stats_compiler = StatsCompiler(self.username, self.join_date)

    def present(self):
        intro = f"\n{self.real_name} has been on Last.fm for " \
                f"{(STATS_START_DATE.year - self.join_date.year)} years.\n" \
                f"They've played {self.total_tracks} tracks.\n" \
                f"That's an average of {self.avg_daily_tracks} track{'s' if self.avg_daily_tracks > 1 else ''} " \
                f"per day.\n"
        print(intro)
        print(f"- - - - - - - - - - - - - {STATS_START_DATE.strftime('%B %-d')} - - - - - - - - - - - - - -\n")
        print("- - - - - - - - - - - Most Played Artists - - - - - - - - - - - -")
        for most_played in self.stats_compiler.most_played_artists():
            if most_played:
                print(most_played)
        print("- - - - - - - - - - - - - All Artists - - - - - - - - - - - - - - -")
        self.stats_compiler.all_artists()

class Lasthop:

    def __init__(self):
        self.user_data = lud.UserData().get_lastfm_user_data()

    def lasthop(self):
        formatted_file_writer = FormattedFileWriter(self.user_data["username"],
                                                    self.user_data["join_date"])
        formatted_file_writer.format_data_for_all_days()
        presenter = StatsPresenter(self.user_data["username"],
                                   self.user_data["real_name"],
                                   self.user_data["join_date"],
                                   self.user_data["total_tracks"])
        presenter.present()


if __name__ == '__main__':
    start_time = datetime.now()
    Lasthop().lasthop()
    print(f"\n(took {(datetime.now() - start_time).seconds} seconds)")


