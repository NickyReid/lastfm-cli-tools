# lastfm-cli-tools
## A collection of python cli tools for personalised last.fm listening history and lyrics.
Best results when used with [lolcat cli colours](https://github.com/busyloop/lolcat) (```$ brew install lolcat``` )

## Fortunelyrics

### Print lyrics from songs on your last.fm.

Uses the [Last.fm API](https://www.last.fm/api) and [lyricsgenius python library](https://pypi.org/project/lyricsgenius/) 

_Note: You will need a [Genius API key](https://docs.genius.com/#/getting-started-h1)_

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

![sing for schiz0rr](https://nickyreid.github.io/images/lastfm-cli-tools-screenshots/fortunelyrics2018-06-09.png "$ sing")


##### Print lyrics of the song currently playing (or last song played):
```python
singthis
```

Example: (colourful output courtesy of [lolcat](https://github.com/busyloop/lolcat))

![singthis for schiz0rr](https://nickyreid.github.io/images/lastfm-cli-tools-screenshots/singthis2018-06-09.png "$ sing")




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

Example: (colourful output courtesy of [lolcat](https://github.com/busyloop/lolcat))

![schiz0rr musicstats 1](https://nickyreid.github.io/images/lastfm-cli-tools-screenshots/lasthop02018-06-09.png "$ musicstats")

![schiz0rr musicstats 2](https://nickyreid.github.io/images/lastfm-cli-tools-screenshots/Lasthop12018-06-09.png "$ musicstats")
