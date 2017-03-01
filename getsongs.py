
import json
import urllib2
import sys
import subprocess
import random
import time
import os
import fileinput
from glob import glob


def setup():
    global lyricsfile
    global api_url
    global loved_or_top
    howmanyfiles = len(os.listdir('lyricsstash'))
    newfilename = get_new_file(howmanyfiles)
    lyricsfile = open(newfilename, 'ab+')
 

    api_key = "8257fbe241e266367f27e30b0e866aba"
    last_fm_username = "schiz0rr"
    top_tracks_limit = "100" # The number of results to fetch per
    top_tracks_period = "6month" # overall | 7day | 1month | 3month | 6month | 12month - The time period over which to retrieve top tracks for.
    loved_or_top = random.randint(0,1)
    if loved_or_top == 0:
        api_url = "http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user="+last_fm_username+"&api_key="+api_key+"&format=json"
    else:
        api_url = "http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user="+last_fm_username+"&api_key="+api_key+"&limit="+top_tracks_limit+"&period="+top_tracks_period+"&format=json"

def get_new_file(howmanyfiles): 
    newfilenumber = howmanyfiles + 1
    newfilename = 'lyricsstash/' + str(newfilenumber) 
    try:
        if os.path.getsize(newfilename) > 0:
            return get_new_file(howmanyfiles+1)
    except OSError:
        pass
    return newfilename    

def get_random_song():
    response = json.loads(urllib2.urlopen(api_url).read())
    tracks = response.get("lovedtracks").get("track") if loved_or_top == 0 else response.get("toptracks").get("track") 
    randomtrack = random.choice(tracks)
    trackname = randomtrack.get('name').replace(')', '').replace('(','').replace("'", "")
    trackartist = randomtrack.get('artist').get('name')
    bashCommand = "songtext -t '" + trackname +  "' -a '" + trackartist +"'"    
    return bashCommand


def get_lyrics():   
    try:
        song = get_random_song()
        lyrics = subprocess.check_output(['bash','-c',song])
        if "Instrumental" in lyrics or len(lyrics) < 10:
            return get_lyrics()
        else:
            return lyrics
    except subprocess.CalledProcessError:
        return get_lyrics()

def write_file(lyrics):
    lines =  lyrics.splitlines()
    randomlinenumber = random.randint(0,len(lines))
    for i in range (randomlinenumber+2, randomlinenumber+7):
        try:
            if lines[i].strip() and not lines[i].isspace() and len(lines[i]) > 1:
                lyricsfile.write(lines[i] + "\n")
        except IndexError:
            pass

try:
    count = int(sys.argv[1])
except IndexError:
    count = 1 
for i in range(count):           
    setup()
    write_file(get_lyrics())
    lyricsfile.close()
