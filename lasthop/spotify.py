import csv
import spotipy
import lasthop
import lastfm_user_data
import random

from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

#TODO
client_id = "a9f3b551a34841b186c062860ea3ad7d"
secret = "53aca3578e6c4188b85ac8a08a25b303"
scope = "playlist-modify-private"


class PlaylistMaker:

    @classmethod
    def get_tracks(cls):
        this_year = datetime.today().year
        user_data = lastfm_user_data.UserData().get_lastfm_user_data()
        last_fm_username = user_data["username"]
        last_fm_join_date = user_data["join_date"]
        formatted_file_writer = lasthop.FormattedFileWriter(
            last_fm_username, last_fm_join_date
        )
        formatted_file_writer.format_data_for_all_days()
        stats_compiler = lasthop.StatsCompiler(last_fm_username, last_fm_join_date)
        listening_data = stats_compiler.compile_stats()

        artist_tracks = []
        artist_tracks_dict = {}
        for date, data in listening_data.items():
            for artist_track, dates in data.items():
                # print(dates[0])
                # print(artist_track)
                year = datetime.strptime(dates[0], "%Y/%m/%d %H:%M:%S").year
                artist = artist_track.split(" | ")[0]
                track_name = artist_track.split(" | ")[1].replace("'", "")
                if year != this_year:
                    if artist_tracks_dict.get(artist):
                        artist_tracks_dict[artist].append(track_name)
                    else:
                        artist_tracks_dict[artist] = [track_name]
                # print(this_year)
                if artist_track not in artist_tracks and year != this_year:
                    artist_tracks.append(artist_track)
        l = []
        for artist_x, tracks_x in artist_tracks_dict.items():
            if len(tracks_x) > 1:
                l.append(f"{artist_x} | {random.choice(tracks_x)}")

        # print(artist_tracks_dict)
        # print(l)
        # print(len(l))
        # print(len(artist_tracks))
        # print((artist_tracks))
        return l

    @classmethod
    def spotify_search(cls, spotify_client, artist, track_name):
        search_result = spotify_client.search(q='track:' + f"{track_name} + {artist}", limit=50, type='track')
        try:
            if search_result.get("tracks"):
                search_result = search_result["tracks"]
                if search_result.get("items"):
                    search_result = search_result["items"]
                else:
                    return

            found_album = None
            found_item = None

            for item in search_result:
                album = item.get("album")
                search_artists = album.get("artists")
                for search_artist in search_artists:
                    search_artist_name = search_artist.get("name")
                    # print(search_artist_name)
                    # print(search_artist_name.lower())
                    # print(artist.lower())
                    # TODO available markets config
                    if (search_artist_name.lower() in artist.lower() or artist.lower() in search_artist_name.lower()) and "ZA" in album.get("available_markets") and " - live" not in track_name.lower() and "live at " not in track_name.lower():
                        found_album = album
                        found_item = item
                        break
                # else:
                #     continue
                # break


            # print(found_item.get("uri"))
            # found_track_id = found_album.get("id")
            if found_item:
                # print(found_item)
                found_track_uri = found_item.get("uri")
                return found_track_uri
            else:
                print(f"{track_name} by {artist} not found {search_result}")

                # if artist.lower() == album.lower():
                #     print(album)
        except:
            print(f"Error: {search_result}")


    @classmethod
    def run(cls):

        # spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

        artist_tracks = cls.get_tracks()
        if not artist_tracks:
            return

        # print(artist_tracks)

        spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        user = spotify_client.current_user()
        user_id = user["id"]

        playlist_name = f"Lasthop {datetime.today().date().strftime( '%Y-%m-%d')}"
        playlist = spotify_client.user_playlist_create(user_id, playlist_name, public=False, collaborative=False,
                                           description="What were you listening to on this day in previous years?")
        playlist_id = playlist.get("id")

        for artist_track in artist_tracks:
            artist = artist_track.split(" | ")[0]
            track_name = artist_track.split(" | ")[1]
            print(f"adding '{track_name}' by '{artist}'...")
            found_track_uri = cls.spotify_search(spotify_client, artist, track_name)

            if found_track_uri:
                spotify_client.playlist_add_items(playlist_id, [found_track_uri])


if __name__ == "__main__":
    PlaylistMaker.run()
