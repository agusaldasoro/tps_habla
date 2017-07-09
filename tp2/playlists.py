import urllib
import urllib2
import pandas
import re
import threading
import pafy
import os
import pandas as pd

dir = os.path.dirname(__file__)

''' pip install pafy
    pip install youtube-dl'''

def bajarAudio(audiostream,search,playlist):

    search = re.sub(' ','_',search)
    filename = os.path.join(dir,'musica/' + playlist, search + '.' + audiostream.extension)
    #filename = 'musica\'+search+'.'+audiostream.extension
    if not os.path.isfile(filename):
        audiostream.download(filepath=filename)

    return

def getAudio(link,search,playlist):

    video = pafy.new(link)
    best = video.getbestaudio()
    audiostreams = video.audiostreams
    bajar = best
    for a in audiostreams:
        if a.bitrate == '128k':
            bajar = a
            break

    thread2 = threading.Thread(target=bajarAudio,args=(bajar,search,playlist))
    thread2.start()
    return


def ytQuery(query):

    query_string = urllib.urlencode({"search_query" : query})
    html_content = urllib2.urlopen("http://www.youtube.com/results?" + query_string)
    montoto = html_content.read().decode('utf-8')
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', montoto)
    return "http://www.youtube.com/watch?v=" + search_results[0]




if __name__ == '__main__':

    playlists = os.listdir('playlist/')
    for p in playlists:
        os.makedirs('musica/' + p[:-4])
    for p in playlists:
        df = pd.read_csv('playlist/' + p)
        for idx, row in df.iterrows():
            name = row[' artista'] + ' ' + row.nombre
            query = ytQuery(name)
            try:
                getAudio(query, name, p[:-4])
            except:
                print "no baje: " + name
    
    query =  ytQuery('Metallica - Fuel')


    getAudio(query, 'Metallica - Fuel', 'rock')
