import json
import urllib2
import subprocess
from config import Config
from set_username import SetUsername


class SingThis:

    def __init__(self, username):
        self.api_key = Config.API_KEY
        self.username = username if username else open('defaultuser', 'r').read()
        self.api_url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" \
                       "{user}&limit=1&api_key={api_key}&format=json".format(user=self.username,api_key=self.api_key)

    def get_song(self):
        response = json.loads(urllib2.urlopen(self.api_url).read())
        track_name = response.get("recenttracks").get("track")[0].get("name")\
            .replace(')', '').replace('(', '').replace("'", "")
        track_artist = response.get("recenttracks").get("track")[0].get("artist").get("#text")\
            .replace(')', '').replace('(', '').replace("'", "")
        try:
            bash_command = "songtext -t '" + track_name + "' -a '" + track_artist + "'"
            return subprocess.check_output(['bash', '-c', bash_command])
        except subprocess.CalledProcessError:
            return track_artist + " - " + track_name + "\n. . . . . . ."


if __name__ == '__main__':
    username = SetUsername.set_username()
    sing_this = SingThis(username)
    try:
        print sing_this.get_song()
    except UnicodeEncodeError:
        import unicodedata
        import sys
        reload(sys)
        sys.setdefaultencoding("utf-8")
        nkfd_form = unicodedata.normalize('NFKD', unicode(sing_this.get_song()))
        print u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
