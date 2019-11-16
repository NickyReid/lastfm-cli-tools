"""
Write a CSV file of Last.fm listening data with format
Year|Month|Weekday|Date|Artist name|Album name|Song title|Lyrics
"""
import os
import json
import raw_file_writer
import lastfm_user_data as lud
from datetime import datetime, timedelta
from shared.config import Config

STATS_END_DATE = datetime.today()
CUSTOM_START_DATE = False


class CSVWriter:

    def __init__(self):
        lastfm_user_data = lud.UserData().get_lastfm_user_data()
        lastfm_username = lastfm_user_data.get("username")
        lastfm_join_date = lastfm_user_data.get("join_date")

        self.username = lastfm_username
        self.stat_start_date = CUSTOM_START_DATE if CUSTOM_START_DATE else lastfm_join_date
        self.api_key = Config.API_KEY
        self.timezone_diff = self.get_timezone_diff()
        self.raw_data_path = f"{Config.RAW_DATA_PATH}/users/{self.username}"
        self.file_path = os.path.dirname(os.path.realpath(__file__)) + '/users/{username}'.format(
            username=self.username)
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        self.lyrics_file_path = f"{self.raw_data_path}/users/{self.username}/lyricsstore"
        if not os.path.exists(self.lyrics_file_path):
            os.makedirs(self.lyrics_file_path)

    def process_data_for_all_days(self):
        rfw = raw_file_writer.RawFileWriter(start_date=self.stat_start_date,
                                            interval=raw_file_writer.Interval.DAY.value,
                                            include_lyrics=True)
        rfw.process_data_for_all_days()
        self.write_formatted_file_for_all_days()

    def write_formatted_file_for_all_days(self):
        formatted_file_name = self.get_formatted_filename()
        day = STATS_END_DATE
        with open(formatted_file_name, "w+") as file:
            file.write("Year|Month|Weekday|Date|Artist name|Album name|Song title|Lyrics\n")
            while True:
                if day < self.stat_start_date:
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
                    print(f"Finished processing {raw_file_name}")
                day = day - timedelta(days=1)
            print(f"Finished writing {formatted_file_name}")

    def get_raw_filename_for_date(self, date):
        date_string = datetime.strftime(date, "%Y-%m-%d")
        return f"{self.raw_data_path}/{date_string}raw.txt"

    def get_lyrics_file_name(self, artist, title):
        artist_track_string = f"{artist}{title}"
        artist_track_string = ''.join(e for e in artist_track_string if e.isalnum())[:35]
        return f"{self.lyrics_file_path}/{artist_track_string}.txt"

    def get_formatted_filename(self):
        return f"{self.file_path}/lastfmstats.csv"

    @staticmethod
    def get_timezone_diff():
        """
        Get difference in hours from UTC timezone. Daylight savings makes this variable.
        :return: Timezone diff in hours
        """
        return datetime.now().hour - datetime.utcnow().hour


if __name__ == '__main__':
    start_time = datetime.now()

    file_writer = CSVWriter()
    file_writer.process_data_for_all_days()

    print(f"\n(took {(datetime.now() - start_time).seconds} seconds)")


