
import json
import urllib2
import sys
import subprocess
import random

api_key = "8257fbe241e266367f27e30b0e866aba"
last_fm_username = "schiz0rr"
top_tracks_limit = "50" # The number of results to fetch per
top_tracks_period = "6month" # overall | 7day | 1month | 3month | 6month | 12month - The time period over which to retrieve top tracks for.


loved_or_top = random.randint(0,1)

if loved_or_top == 0:
    api_url = "http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user="+last_fm_username+"&api_key="+api_key+"&format=json"
else:
    api_url = "http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user="+last_fm_username+"&api_key="+api_key+"&limit="+top_tracks_limit+"&period="+top_tracks_period+"&format=json"

def get_random_song():
    response = json.loads(urllib2.urlopen(api_url).read())
    tracks = response.get("lovedtracks").get("track") if loved_or_top == 0 else response.get("toptracks").get("track") 
    randomtrack = random.choice(tracks)
    trackname = randomtrack.get('name')
    trackartist = randomtrack.get('artist').get('name')
    bashCommand = "songtext -t '" + randomtrack.get('name') +  "' -a '" + randomtrack.get('artist').get('name') +"'"
    return bashCommand

def get_lyrics(song):   
    try:
        return subprocess.check_output(['bash','-c', song])
    except subprocess.CalledProcessError:
        return subprocess.check_output(['bash','-c', get_random_song()])
    finally:
        pass    


randomsong = get_random_song()
try:
    lyrics = get_lyrics(randomsong)
except subprocess.CalledProcessError:
    new_song = get_random_song()
    lyrics = get_lyrics(new_song)

lines =  lyrics.splitlines()
randomlinenumber = random.randint(0,len(lines))
for i in range (randomlinenumber, randomlinenumber+5):
    try:
        if lines[i].strip():
            print lines[i]
    except IndexError:
        pass
