# lastfm-cli-tools
## A collection of python cli tools for personalised last.fm listening history and lyrics.

## Fortunelyrics

### Print lyrics from songs on your last.fm.

#### Instructions:

##### Populate lyric stash with N lyrics (defaults to 1 if n not specified):
```python
getsongs 10
```
##### Print random lyric:
```python
sing
```

##### Print lyrics of the song currently playing (or last song played):
```python
singthis
```

## Lasthop Music Stats

### Lasthop fetches music stats from your last.fm profile about your listening habits from this day in the years gone by.

This is deprecated since I made a [Web app version](https://github.com/NickyReid/LasthopWeb).  

##### To run:

```
$  musicstats
```

### Stats:
* Years on Last.fm
* Total number of tracks scrobbled
* Average daily scrobbles
* Most Played Artists on this day, for each year since joining Last.fm
* All artists play counts on this day, for each year since joining Last.fm

## Make Spotify Playlist

Make a Spotify playlist with music from this day in history

```python
    python3 lasthop/spotify.py
```

### Note:
You will need the following access:
- [Last.fm API key](https://www.last.fm/api/authentication)
- [Genius API key](https://docs.genius.com/#/getting-started-h1)
- [Spotify access token](https://developer.spotify.com/documentation/web-api/tutorials/getting-started)

The following Environment variables must be set:
* LAST_FM_API_KEY
* GENIUS_ACCESS_TOKEN
* SPOTIPY_CLIENT_ID
* SPOTIPY_CLIENT_SECRET
