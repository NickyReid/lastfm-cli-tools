
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
        topfile = os.listdir( os.path.dirname(os.path.realpath(__file__)) + '/lyricsstash')[0]
        topfilepath = os.path.dirname(os.path.realpath(__file__)) + '/lyricsstash/' + str(topfile)
        print topfilepath
        lyricsfile = open(topfilepath, 'r+')
        output = lyricsfile.read().rstrip('\n')
        lenoutput = len(output)
        #todo: empty files
        print output
        print lenoutput
        os.remove(topfilepath)
    except IndexError:
        print "Oh shit, I ran out of songs :("

get_song()
