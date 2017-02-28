import os
import random
from config import Config


class FortuneLyrics:

    def __init__(self):
        self.lyric_stash = Config.LYRIC_STASH_PATH
        self.files = None
        self.random_file = None
        self.file_path = None

    def print_song(self):
        try:
            self.files = os.listdir(self.lyric_stash)
            self.random_file = random.choice(self.files)
            self.file_path = self.lyric_stash + "/" + self.random_file
            lyrics_file = open(self.file_path, 'r+')
            lyrics = lyrics_file.read().rstrip('\n')
            print lyrics
            os.remove(self.file_path)
        except (IndexError, OSError):
            print "Oh shit, I ran out of songs :( \nRun getsongs.py to repopulate lyric stash."

if __name__ == '__main__':
    fortune_lyrics = FortuneLyrics()
    fortune_lyrics.print_song()
