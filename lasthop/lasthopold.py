import os
import json
import math
import urllib.request, urllib.error, urllib.parse
import requests
import multiprocessing
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from shared.set_username import SetUsername
from shared.config import Config

def go():
    LastHop.run()


class LastHop:

    def __init__(self, username, real_name, join_date, total_tracks):
        self.timezone_diff = self.get_timezone_diff()
        self.join_date = join_date.date()
        self.stats_date = datetime.today()
        self.username = username
        self.real_name = real_name if real_name else self.username
        self.total_tracks = int(total_tracks)
        self.avg_daily_tracks = self.total_tracks / (self.stats_date.date() - self.join_date).days
        self.user_profile = "https://www.last.fm/user/{user}/library".format(user=username)
        self.file_path = os.path.dirname(os.path.realpath(__file__)) + '/users/{username}'.format(username=username)
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)

    @staticmethod
    def get_timezone_diff():
        """
        Get difference in hours from UTC timezone. Daylight savings makes this variable.
        :return: Timezone diff in hours
        """
        return datetime.now().hour - datetime.utcnow().hour

    def get_date_filename(self, date):
        """
        Get file name for given day
        """

        if isinstance(date, datetime):
            date = date.date()
        print(type(date))
        # print( "{path}/{date}.csv".format(path=self.file_path, date=date))
        return "{path}/{date}.csv".format(path=self.file_path, date=date)

    def user_stats(self):
        print("{user} has been on Last.fm for {years} years " \
              "\nThey've played {total_tracks} tracks \n" \
              "That's an average of {avg} track{s} per day.".format(user=self.real_name,
                                                                    years=(self.stats_date.year - self.join_date.year),
                                                                    total_tracks="{:,}".format(self.total_tracks),
                                                                    avg=int(self.avg_daily_tracks),
                                                                    s="s" if self.avg_daily_tracks > 1 else ""))

    def music_stats(self):
        print("- - - - - - - - - - - - - {date} - - - - - - - - - - - - - -".format(
            date=self.stats_date.date().strftime("%B %-d")))
        print("- - - - - - - - - - Most Played Artists - - - - - - - - - -")
        self.yearly_most_played_artists()
        print("\n- - - - - - - - - Played around this time - - - - - - - - -")
        # self.yearly_around_this_time()
        print("\n- - - - - - - - - - - All Artists  - - - - - - - - - - - - -")
        # self.yearly_all_artists()
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        # if self.stats_date.date() == datetime.today().date() and datetime.today().time().hour < 2:
        #     try:
        #         day_file_path = self.get_date_filename(self.stats_date.date())
        #         os.remove(day_file_path)
        #     except OSError:
        #         pass

    def process_day(self, date):
        """
        Scrapes the user profile for this day on each year since joining last.fm
        :param date: Date to process and write files for
        :param prev: Is this the day before? Used for timezone difference. I know it's hideous.
        :return: dictionary of artist and track information
        """
        today_file_path = self.get_date_filename(date.date())
        print(today_file_path)
        tracks_and_dates_list = []
        page = 1
        date_start = date.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)
        date_start_epoch = int(date_start.timestamp())
        date_end_epoch = int(date_start.replace(hour=23).replace(minute=59).replace(second=59).timestamp())
        api_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks" \
                  f"&user={self.username}&" \
                  f"api_key=8257fbe241e266367f27e30b0e866aba&" \
                  f"&from={date_start_epoch}" \
                  f"&to={date_end_epoch}" \
                  f"&limit=200" \
                  f"&page=1" \
                  f"&format=json"


        response = requests.get(api_url).json()

        recenttracks = response.get("recenttracks", {}).get("track")
        total_track_count = response.get("recenttracks", {}).get("total", 0)
        # if total_track_count == 0:
        #     today_file = open(today_file_path, 'w+')
        #     today_file.write("0")
        #     today_file.close()
        #     return []

        num_pages = math.ceil(total_track_count / 200)
        tracks_and_dates = []
        artist_track_date_map = {}
        if num_pages > 1:
            for page_num in range(2, num_pages + 1):
                api_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks" \
                          f"&user={self.username}&" \
                          f"api_key=8257fbe241e266367f27e30b0e866aba&" \
                          f"&from={date_start_epoch}" \
                          f"&to={date_end_epoch}" \
                          f"&limit=200" \
                          f"&page={page_num}" \
                          f"&format=json"
                response = requests.get(api_url).json()
                recenttracks.append(response.get("recenttracks", {}).get("track"))
        for track in recenttracks:
            artist = track.get('artist', {}).get('#text').replace(",", "")
            title = track.get('name').replace(",", "")
            play_date = track.get('date', {}).get('#text', datetime.now())
            play_date_datetime = datetime.strptime(play_date, "%d %b %Y, %H:%M")
            play_date_formatted = play_date_datetime.strftime("%Y/%m/%d %H:%M:%S")

            with open(today_file_path, 'w+') as stats_file:
                stats_file.write(f"{artist},{title},{play_date_formatted}")
            # today_file = open(today_file_path, 'w+')
            # for key in artist_dict:
            #     today_file.write("{track}: {date}\n".format(track=key, date=artist_dict.get(key)))
            # today_file.close()
            # if artist_track_date_map.get()
            # tracks_and_dates.append(f"{artist} - {title}: m[{play_date}]")
        # print(tracks_and_dates)
        #
        # if artist_dict.get(tracks_and_dates[i]):
        #     date_list = artist_dict.get(tracks_and_dates[i])
        #     date_list.append(tracks_and_dates[i + 1])
        #     artist_dict[tracks_and_dates[i]] = date_list
        # else:
        #     artist_dict[tracks_and_dates[i]] = [tracks_and_dates[i + 1]]
        # tracks_and_dates_list.append({"track": tracks_and_dates[i], "date": tracks_and_dates[i + 1]})


        # while True:  # paging
        #     response = requests.get(api_url).json()
        #     if response.get("recenttracks", {}).get("total", 0) < 1:
        #         break
        #
        #
        # url = '{user_profile}?rangetype=1day&from={date}&page={page}'.format(user_profile=self.user_profile,
        #                                                                      date=date,
        #                                                                      page=str(page))
        # artist_dict = {}
        # tracks_and_dates = []
        # while True:  # paging
        #     response = requests.get(url)
        #     if response.url != url:
        #         break
        #
        #     if "didn't scrobble anything" in response.content:
        #         today_file = open(today_file_path, 'w+')
        #         today_file.write("0")
        #         today_file.close()
        #         return []
        #     lines = response.content.split('title="')[1:]
        #     tracks_and_dates = []
        #     for line in lines:
        #         l = line.split('">')[0].split("\n")[0]
        #         if l[0] is not " ":
        #             tracks_and_dates.append(l.replace('"', '').replace('&amp;', '&'))
        #     for i in range(0, len(tracks_and_dates)):
        #         if '\xe2\x80\x94' in tracks_and_dates[i]:
        #             if (datetime.strptime(tracks_and_dates[i + 1], '%A %d %b %Y, %I:%M%p').time().hour > 21 and
        #                     self.stats_date.date().day == date.day):
        #                 continue
        #             else:
        #                 if artist_dict.get(tracks_and_dates[i]):
        #                     date_list = artist_dict.get(tracks_and_dates[i])
        #                     date_list.append(tracks_and_dates[i + 1])
        #                     artist_dict[tracks_and_dates[i]] = date_list
        #                 else:
        #                     artist_dict[tracks_and_dates[i]] = [tracks_and_dates[i + 1]]
        #                 tracks_and_dates_list.append({"track": tracks_and_dates[i], "date": tracks_and_dates[i + 1]})
        #     page += 1
        #     url = '{user_profile}?rangetype=1day&from={date}&page={page}'.format(user_profile=self.user_profile,
        #                                                                          date=date,
        #                                                                          page=str(page))
        # today_file = open(today_file_path, 'w+')
        # for key in artist_dict:
        #     today_file.write("{track}: {date}\n".format(track=key, date=artist_dict.get(key)))
        # today_file.close()
        # return artist_dict

    def write_day_file(self, date):
        """
        Writes track data for one day
        :param date:
        :return:
        """
        day_file_path = self.get_date_filename(date.date())
        open(day_file_path, 'ab+').close()
        if (not os.path.getsize(day_file_path) > 0 or date == datetime.today() or
                (date == datetime.today() - relativedelta(days=1) and
                 datetime.today().time().hour < self.timezone_diff)):
            self.process_day(date)
        return day_file_path

    def write_all_files(self, year=None):
        """
        Writes track data for each day on this day from join date until today
        """
        date = self.stats_date
        if year:
            date = date.replace(year=year)
        day_file_path = self.get_date_filename(date.date())
        day_file_path = "{path}/{date}.csv".format(path=self.file_path, date=date.date())
        try:
            open(day_file_path, 'r+')
        except IOError:
            for f in os.listdir(self.file_path):
                if os.path.isfile(f):
                    os.remove(f)
        new_day = True
        while True:
            if self.timezone_diff == 0:
                self.write_day_file(date)
            else:
                day_before = date - relativedelta(days=1)
                day_before_file_path = self.get_date_filename(day_before)
                try:
                    open(day_file_path, 'r+')
                except IOError:
                    new_day = True
                try:
                    open(day_before_file_path, 'r+')
                except Exception:
                    new_day = True
                    self.write_day_file(date)
                if new_day:
                    if self.timezone_diff != 0:
                        self.first_n_hours(date=date)
                    new_day = False

            if year:
                break

            date = date - relativedelta(years=1)
            if date < self.join_date:
                break

    @classmethod
    def st_to_dict(cls, line):
        track_dict = {}
        if line == "0":
            return 0
        artist = line.split(':')[0]
        time = line.split(':', 1)[1]
        track_dict[artist] = time
        return track_dict

    def most_played_artist(self, date):
        day_file_path = self.get_date_filename(date)
        # print(day_file_path)
        today_file = open(day_file_path, 'r+')
        track_dict = {}
        artists = {}
        for line in today_file:
            if line == "\n":
                continue
            if line == "0":
                return 0
            track = line.split(':', 1)[0]
            time = line.split(':', 1)[1]
            if track_dict.get(track):
                date_list = track_dict.get(track)
                date_list.append(time.strip("["))
                track_dict[track] = date_list
            else:
                track_dict[track] = [time]
        for track in track_dict:
            date_list = track_dict.get(track)
            count = 0
            for dat in date_list:
                count += dat.count('am') + dat.count('pm')
            track = track.split('\xe2\x80\x94')[0]
            if track[0] == '0':
                track = track[1:]
            artists[track] = artists.get(track, 0) + count
        day_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekday = day_list[date.weekday()]
        today_file.close()
        artist = max(artists, key=artists.get).replace('&#39;', '`') if artists else None
        count = artists.get(max(artists, key=artists.get)) if artist else 0
        return "{date} ({weekday}): {artist} ({count})".format(date=date.year,
                                                               artist=artist,
                                                               count=count,
                                                               weekday=weekday)

    def yearly_most_played_artists(self):
        date = self.stats_date.date()
        while True:
            most_played = self.most_played_artist(date)
            if most_played:
                print(most_played)
            date = date - relativedelta(years=1)
            if date < self.join_date:
                break

    @staticmethod
    def seconds_to_time(seconds):
        hours = seconds / 60
        min = seconds % 60
        return "{h}:{m}".format(h=hours, m=min)

    def around_this_time(self, date):
        day_file_path = self.get_date_filename(date)
        # print(day_file_path)
        # day_file_path = "{path}/{date}.csv".format(path=self.file_path, date=date.day())
        day_file = open(day_file_path, "r+")
        times = {}
        now = self.stats_date
        seconds_passed_today = now.hour * 60 + now.minute
        track_dict = {}
        track_time_dict = {} # maps seconds passed to actual play times
        for line in day_file:
            if line == "\n":
                continue
            if line == "0":
                return 0
            track = line.split(":")[0]
            if track[0] == '0':
                track = track[1:]
            track_time_dict[track] = []
            date = line.split(":", 1)[1].lstrip().rstrip()
            if track_dict.get(track):
                date_list = track_dict.get(track)
                date_list.append(date)
                track_dict[track] = date_list
            else:
                track_dict[track] = [date]
            date_list = track_dict.get(track)
            for date in date_list:
                if len(date) > 33:
                    for i in date.split(','):
                        if len(i) < 12:
                            time = i[1:8]
                            if time[len(time)-1:] == "'":
                                time = time[:6]
                            time = datetime.strptime(time, '%I:%M%p') + relativedelta(hours=self.timezone_diff)
                            time = time.time()
                            seconds_passed = time.hour * 60 + time.minute
                            track_time_dict[seconds_passed] = time
                            times[seconds_passed] = track
                else:
                    time = date[len(date)-9:len(date)-2]
                    if time[0] == " ":
                        time = time[1:]
                    time = datetime.strptime(time, '%I:%M%p') + relativedelta(hours=self.timezone_diff)
                    time = time.time()
                    seconds_passed = time.hour * 60 + time.minute
                    track_time_dict[seconds_passed] = time
                    times[seconds_passed] = track
        diff_times = {}
        for s in list(times.keys()):
            diff = abs(seconds_passed_today - int(s))
            diff_times[times.get(s)] = diff
        track = min(diff_times, key=diff_times.get) if diff_times else None
        return {"track": track}

    def yearly_around_this_time(self):
        date = self.stats_date.date()
        while True:
            played_nowish = self.around_this_time(date)
            if type(played_nowish) != dict:
                break
            if played_nowish.get('track'):
                song = played_nowish.get('track').replace('&#39;', '`')
            else:
                continue
            if played_nowish:
                print("{year}: {song}".format(year=date.year,
                                              song=song))
            date = date - relativedelta(years=1)
            if date < self.join_date:
                break

    def first_n_hours(self, date):
        """
        When the response from last.fm is in a different time zone than ours,
        we need to some some grotesque hacking.
        :param date:
        :return:
        """
        day_before = date - relativedelta(days=1)
        day_before_songs = self.write_day_file(day_before)
        song_dict = {}

        if type(day_before_songs) == str:
            song_file = open(day_before_songs, 'r+')
            for song in song_file:
                d = self.st_to_dict(song)
                if d == 0:
                    return []
                song_dict[list(d.keys())[0]] = list(d.values())[0]
        else:
            for song in day_before_songs:
                if day_before_songs[0].get('track'):
                    date_list = song.get('date')
                    song_dict[song.get('track')] = date_list
                else:
                    song_dict[song.get('track')] = [song.get('date')]

        late_night_songs = {}
        for song in song_dict:
            times = song_dict.get(song)
            times_played = []
            late_night_songs[song] = []
            for time in times.split("'"):
                if "[" not in time and ']' not in time and len(time) > 3:
                    times_played.append(time)
                    if datetime.strptime(time.lstrip().rstrip(), '%A %d %b %Y, %I:%M%p').time().hour \
                            >= (24 - self.timezone_diff):
                        late_night_songs[song].append(time)
        day_file_path = self.get_date_filename(date)
        day_file = open(day_file_path, 'a+')
        for song in late_night_songs:
            if len(late_night_songs.get(song)) > 0:
                line = "{song}: {time}\n".format(song=song, time=late_night_songs.get(song))
                day_file.write(line)
        day_file.close()
        return late_night_songs

    def all_artists_that_day(self, date):
        day_file_path = self.get_date_filename(date.date())
        day_file = open(day_file_path, "r+")
        track_dict = {}
        artists = {}
        for line in day_file:
            if line == "\n":
                continue
            if line == "0":
                return 0
            track = line.split(':', 1)[0]
            times = line.split(':', 1)[1]
            if track_dict.get(track):
                date_list = track_dict.get(track)
                date_list.append(times)
                track_dict[track] = date_list
            else:
                track_dict[track] = [times]
        for track in track_dict:
            times = track_dict.get(track)
            play_count = 0
            for dat in times:
                play_count += dat.count('am') + dat.count('pm')
            track = track.split('\xe2\x80\x94')[0]
            if '0' in track[0]:
                artists[track[1:]] = artists.get(track[1:], 0) + play_count
            else:
                artists[track] = artists.get(track, 0) + play_count
        day_file.close()
        return artists

    def yearly_all_artists(self):
        date = self.stats_date.date()
        while True:
            artists = self.all_artists_that_day(date)
            if artists:
                print("* - {year} - *".format(year=date.year))
                for artist in sorted(artists, key=artists.__getitem__, reverse=True):
                    print("\t{artist}: {plays}".format(artist=artist.replace('&#39;', '`'),
                                                       plays=artists.get(artist)))
                total = 0
                for count in artists:
                    total += artists.get(count)
                print("       -  \n\tTotal tracks: {total}".format(total=total))
            date = date - relativedelta(years=1)
            if date < self.join_date:
                break

    @classmethod
    def run(cls):
        start_time = datetime.now()
        username = SetUsername.set_username()

        print("Getting music stats for {0}".format(username))

        user_data = get_lastfm_user_data(username)

        lastfm_user = LastHop(username=username,
                              real_name=user_data.get("real_name"),
                              join_date=user_data.get("join_date"),
                              total_tracks=user_data.get("total_tracks"),)

        lastfm_user.user_stats()

        jobs = []
        for i in range(user_data.get('join_date').year, datetime.today().year + 1):
            p = multiprocessing.Process(target=lastfm_user.write_all_files, args=(i,))
            jobs.append(p)
            p.start()

        for job in jobs:
            job.join()

        lastfm_user.stats_date = datetime.today()
        lastfm_user.music_stats()

        end_time = datetime.now()
        total = end_time - start_time
        print("(took {time} seconds)".format(time=total.seconds))


def get_lastfm_user_data(username):
    api_key = Config.API_KEY

    api_url = "http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={user}&api_key={api_key}&format=json" \
        .format(user=username, api_key=api_key)
    api_response = json.loads(urllib.request.urlopen(api_url).read())
    join_date = datetime.fromtimestamp(float(api_response.get("user").get("registered").get("unixtime")))
    real_name = api_response.get("user").get("realname")
    total_tracks = api_response.get("user").get("playcount")
    return {
        "join_date": join_date,
        "real_name": real_name,
        "total_tracks": total_tracks
        }


if __name__ == '__main__':
    LastHop.run()
