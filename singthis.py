
import json
import urllib2
import subprocess

def setup():
    global api_url
    api_key = "8257fbe241e266367f27e30b0e866aba"
    last_fm_username = "schiz0rr"
    api_url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="+last_fm_username+"&limit=1&api_key="+api_key+"&format=json"

setup()
response = json.loads(urllib2.urlopen(api_url).read())
trackname = response.get("recenttracks").get("track")[0].get("name").replace(')', '').replace('(','').replace("'", "")
trackartist = response.get("recenttracks").get("track")[0].get("artist").get("#text").replace(')', '').replace('(','').replace("'", "")
bashCommand = "songtext -t '" + trackname +  "' -a '" + trackartist +"'"
print subprocess.check_output(['bash','-c',bashCommand])
