
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
        files = os.listdir(os.path.dirname(os.path.realpath(__file__)) + '/lyricsstash')
        # print files
        # print len(files)
        randomfile = random.choice(files)
        # print randomfile
        filepath = os.path.dirname(os.path.realpath(__file__)) + '/lyricsstash/' + randomfile
        # topfile = os.listdir( os.path.dirname(os.path.realpath(__file__)) + '/lyricsstash')[0]
        # topfilepath = os.path.dirname(os.path.realpath(__file__)) + '/lyricsstash/' + str(topfile)
        # print topfilepath
        lyricsfile = open(filepath, 'r+')
        output = lyricsfile.read().rstrip('\n')
        lenoutput = len(output)
        #todo: empty files
        print output
        print lenoutput
        os.remove(filepath)
    except IndexError:
        print "Oh shit, I ran out of songs :("

get_song()
