
import json
import os
import urllib2
import sys
import subprocess
import random
import time
import fileinput


def get_song():
    try:
        topfile = os.listdir('lyricsstash')[0]
        topfilepath = 'lyricsstash/' + str(topfile)
        lyricsfile = open(topfilepath, 'r+')
        output = lyricsfile.read().rstrip('\n')
        lenoutput = len(output)

        print output
        print lenoutput
        os.remove(topfilepath)
    except IndexError:
        print "Oh shit, I ran out of songs :("

get_song()
