
import json
import urllib2
import sys
import subprocess
import random
import time
import fileinput

begin = time.time()
lyricsfile = open('lyricsstash/lyrics', 'r+')
lyrics = lyricsfile.read().splitlines()
linecount = 0




# for line in fileinput.input("test.txt", inplace=True):
#     print "%d: %s" % (fileinput.filelineno(), line),

def read_new_lyric():
    first_lyric = False
    global linecount    
    for line in lyrics:
        if '%' in line and not first_lyric:
            continue
        else:
            first_lyric = True


        if '%' not in line:
            print "%s" % (line)
            linecount += 1
            line = lyrics[linecount]

        else:
            reconstruct(linecount)
            break    

buffer = ''
def reconstruct(linecount):
    lyricsfile.seek(0)
    lyricsfile.truncate()
    print linecount            
    print " === "
    global buffer
    for line in range(linecount,len(lyrics)-1):
        buffer += lyrics[line] + '\n'
    print buffer    
    lyricsfile.write(buffer)    
    # lyricsfile.truncate()



# l = str(lyrics[15:16])    



    # for line in lyrics:
    #     print line
    # line = lyricsfile.readline().rstrip('\n')
    # global linecount
    # while '%' not in line:
    #     if '$' in line:
    #         line =lyricsfile.readline()
    #     else:    
    #         # global linecount 
    #         # linecount += 1
    #         # print linecount
    #         print "%s" % (line)
    #         linecount += 1

read_new_lyric()
end = time.time()
print end - begin


    # for line in fileinput.input('lyricsstash/lyrics', inplace = 1): 
    #     print line
    #     if '$' in line: 
    #         print line.replace("$", "bar")
    #     else:
            # pass

    # global linecount
    # for line in fileinput.input('lyricsstash/lyrics', inplace=True):
    #     if '$' in line:
    #         print "%s" % ("asd")
    #         linecount += 1


    # line = lyricsfile.readline().rstrip('\n')
    # while '%' not in line:
    #     if '$' in line:
    #         line =lyricsfile.readline()
    #     else:    
    #         # global linecount 
    #         # linecount += 1
    #         # print linecount
    #         print "%s" % (line)
    #         line = lyricsfile.readline().rstrip('\n')

