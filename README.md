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

Example: (colourful output courtesy of [lolcat](https://github.com/busyloop/lolcat))

[comment]: <> (![sing for schiz0rr]&#40;https://nickyreid.github.io/images/lastfm-cli-tools-screenshots/fortunelyrics2018-06-09.png "$ sing"&#41;)


##### Print lyrics of the song currently playing (or last song played):
```python
singthis
```

Example: (colourful output courtesy of [lolcat](https://github.com/busyloop/lolcat))

[comment]: <> (![singthis for schiz0rr]&#40;https://nickyreid.github.io/images/lastfm-cli-tools-screenshots/singthis2018-06-09.png "$ sing"&#41;)




## Lasthop Music Stats

### Lasthop fetches music stats from your last.fm profile about your listening habits from this day in the years gone by.

Since the last.fm API doesn't support track history, this program scrapes users' Last.fm profile for track data.

##### To run:

```
$  musicstats
```

### Stats:
* Years on Last.fm
* Total number of tracks scrobbled
* Average daily scrobbles
* Most Played Artists on this day, for each year since joining Last.fm
* Songs played around this time of day, each year since joining Last.fm
* All artist play counts on this day, for each year since joining Last.fm

## Make Spotify Playlist

Make a Spotify playlist with music from this day in history

```python
makeplaylist
```

### Note:
You will need the following access:
- [Last.fm API key](https://www.last.fm/api/authentication)
- [Genius API key](https://docs.genius.com/#/getting-started-h1)
- [Spotify access token](https://developer.spotify.com/documentation/web-api/tutorials/getting-started) 

[comment]: <> (Example: &#40;colourful output courtesy of [lolcat]&#40;https://github.com/busyloop/lolcat&#41;&#41;)

[comment]: <> (![schiz0rr musicstats 1]&#40;https://nickyreid.github.io/images/lastfm-cli-tools-screenshots/lasthop02018-06-09.png "$ musicstats"&#41;)

[comment]: <> (![schiz0rr musicstats 2]&#40;https://nickyreid.github.io/images/lastfm-cli-tools-screenshots/Lasthop12018-06-09.png "$ musicstats"&#41;)

[comment]: <> (&#40; Best results when used with [lolcat cli colours]&#40;https://github.com/busyloop/lolcat&#41; &#40;```$ brew install lolcat`` `&#41;)