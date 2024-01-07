import re
import os
import spotipy
import lasthop
import lastfm_user_data
import random

from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime


def go():
    PlaylistMaker.run()


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
                year = datetime.strptime(dates[0], "%Y/%m/%d %H:%M:%S").year
                artist = artist_track.split(" | ")[0]
                track_name = artist_track.split(" | ")[1].replace("'", "")
                if year != this_year:
                    if artist_tracks_dict.get(artist):
                        artist_tracks_dict[artist].append(track_name)
                    else:
                        artist_tracks_dict[artist] = [track_name]
                if artist_track not in artist_tracks and year != this_year:
                    artist_tracks.append(artist_track)

        return artist_tracks_dict

    @classmethod
    def spotify_search(cls, spotify_client, artist, track_name):
        search_result = spotify_client.search(q='track:' + f"{track_name} + {artist}", type='track')
        try:
            found_item = None
            if search_result.get("tracks"):
                search_result = search_result["tracks"]
                if search_result.get("items"):
                    search_result = search_result["items"]

                    found_item = None

                    for item in search_result:
                        album = item.get("album")
                        search_artists = album.get("artists")
                        for search_artist in search_artists:
                            search_artist_name = search_artist.get("name")
                            # TODO available markets config
                            if (search_artist_name.lower() in artist.lower() or artist.lower() in search_artist_name.lower()) and "ZA" in album.get("available_markets") and " - live" not in track_name.lower() and "live at " not in track_name.lower():
                                found_item = item
                                break
                        else:
                            continue
                        break

            if found_item:
                found_track_uri = found_item.get("uri")
                return found_track_uri
            elif ("(" in track_name and ")" in track_name) or ("[" in track_name and "]" in track_name):
                track_name_without_brackets = re.sub("[\(\[].*?[\)\]]", "", track_name)
                return cls.spotify_search(spotify_client, artist, track_name_without_brackets)

        except Exception as e:
            print(f"Error: {e} {search_result}")

    @classmethod
    def create_playlist(cls, spotify_client):
        user = spotify_client.current_user()
        user_id = user["id"]

        playlist_name = f"Lasthop {datetime.today().date().strftime('%Y-%m-%d')}"
        playlist = spotify_client.user_playlist_create(user_id, playlist_name, public=False, collaborative=False,
                                                       description="What were you listening to on this day in previous years?")
        playlist_url = playlist.get("external_urls", {}).get("spotify")
        playlist_id = playlist.get("id")
        return playlist_id, playlist_url

    @classmethod
    def add_track_to_playlist(cls, spotify_client, playlist_id, track_uri, track_name, artist):
        print(f"Adding '{track_name}' by {artist}")
        spotify_client.playlist_add_items(playlist_id, [track_uri])

    @classmethod
    def search_for_tracks(cls, spotify_client, playlist_id, artist_tracks):
        for artist, tracks in artist_tracks.items():
            if len(tracks) < 2:
                continue
            random.shuffle(tracks)
            selected_track = tracks[0]
            found_track_uri = cls.spotify_search(spotify_client, artist, selected_track)
            if found_track_uri:
                cls.add_track_to_playlist(spotify_client, playlist_id, found_track_uri, selected_track, artist)
            else:
                current_search = selected_track
                for retry_track in tracks[1:]:
                    print(f"Couldn't find '{current_search}' by {artist}... Searching for '{retry_track}'")
                    current_search = retry_track
                    found_track_uri = cls.spotify_search(spotify_client, artist, retry_track)
                    if found_track_uri:
                        cls.add_track_to_playlist(spotify_client, playlist_id, found_track_uri, retry_track, artist)
                        break
            if not found_track_uri:
                print(f"Couldn't find any tracks for {artist} :(")

    @classmethod
    def run(cls):
        scope = "playlist-modify-private"
        redirect_uri = "http://127.0.0.1:8000/"
        spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, redirect_uri=redirect_uri))

        artist_tracks = cls.get_tracks()
        if not artist_tracks:
            return

        playlist_id, playlist_url = cls.create_playlist(spotify_client)
        cls.search_for_tracks(spotify_client, playlist_id, artist_tracks)

        if playlist_url:
            print(f"Playlist created! {playlist_url}")


if __name__ == "__main__":
    PlaylistMaker.run()
