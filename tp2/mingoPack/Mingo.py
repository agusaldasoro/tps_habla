import threading
import json
import commands
import pafy
import subprocess
import re
import os
import urllib2
import urllib
import vlc
import time


dir = os.path.dirname(__file__)

pl = []
clm = threading.Event()


def popenAndCall(onExit, popenArgs):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    onExit when the subprocess completes.
    onExit is a callable object, and popenArgs is a list/tuple of args that
    would give to subprocess.Popen.
    """
    def runInThread(onExit, popenArgs):
        proc = subprocess.Popen(popenArgs)ytQuery
        proc.wait()
        onExit()
        return
    print 'popenAndCall AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaaa'
    thread = threading.Thread(target=runInThread, args=(onExit, popenArgs))
    thread.start()
    # returns immediately after the thread starts
    return thread

def onSongIn(search):
    ytlink = ytQuery(search)
    try:
        getAudio(ytlink,search)
    except:
        print 'se cago algo, no te bajo ' + search + ' una mierda'
    return




class playerThread(threading.Thread):

    def __init__(self,songPath):
        super(playerThread, self).__init__()
        self.songPath = songPath
        self.clm = True
    def run(self):
        player = vlc.MediaPlayer(self.songPath)
        print 'reproduciendo ' + self.songPath
        player.play()
        time.sleep(0.3)
        playing = player.get_state()
        while not ( clm.is_set() ) and (player.get_state() == playing):
            pass
        clm.clear()
        player.stop()
        onSongEnd()
        return
    def bastaChicos():
        sef.clm = False
        return




# def playSongThread(songPath,dummy):
#         player = vlc.MediaPlayer(songPath)
#         player.play()
#         global clm
#         # print player.is_playing()
#         # while(player.is_playing() == 0):
#         #     print clm
#         #     if clm:
#         #         clm = False
#         #         break
#         #     else:
#         #         pass
#         # player.stop()
#         # onSongEnd()
#         return


def playSong(songPath):
    dummy = 2
    pThread = playerThread(songPath)
    pThread.start()
    return pThread

def onSongDl(song):
    print song
    pl.append(song)
    if len(pl) == 1:
       # os.system('cvlc '+ ' -q ' +'musica/'+song + ' --play-and-exit')
        #popenAndCall(onSongEnd,['cvlc','-q', 'musica/'+song + ' --play-and-exit'])
        pThread = playSong(os.path.join(dir,'musica',song))

    return


def bajarAudio(audiostream,search):
    search = re.sub(' ','_',search)
    filename = os.path.join(dir,'musica', search + '.' + audiostream.extension)
    #filename = 'musica\'+search+'.'+audiostream.extension
    if not os.path.isfile(filename):
        audiostream.download(filepath=filename)
    print '#yalobaje'
    onSongDl(search+'.'+audiostream.extension)

    return



def getAudio(link,search):

    video = pafy.new(link)
    best = video.getbestaudio()
    audiostreams = video.audiostreams
    bajar = best
    for a in audiostreams:
        print 'pija'
        if a.bitrate == '128k':
            bajar = a
            break

    thread2 = threading.Thread(target=bajarAudio,args=(bajar,search))
    thread2.start()
    return






def onSongEnd():
    print 'onSongEnd'
    if len(pl) > 0:
        del pl[0]
        if len(pl) > 0:
            song = pl[0]
            threadPlayer = playSong(os.path.join(dir,'musica',song))
        #popenAndCall(onSongEnd,['cvlc', '-q', 'musica/'+song + ' --play-and-exit'])
       # print 'play'

    return


def ytQuery(query):

    query_string = urllib.urlencode({"search_query" : query})
    html_content = urllib2.urlopen("http://www.youtube.com/results?" + query_string)
    montoto = html_content.read().decode('utf-8')
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', montoto)
    return "http://www.youtube.com/watch?v=" + search_results[0]


#MingoCode hasta aca ------------------------------------------------------------------------------------------------------------------------------------------------

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')



def hacerTodo(bot, update):
    search = update.message.text
    if search == 'clm' or search == 'Clm':
        clm.set()
    elif search == 'playlist?' or search == 'Playlist?' or search == 'pl?' or search == 'Pl?' :
        for cosa in pl:
            bot.sendMessage(update.message.chat_id, text=str(cosa))
    else:
        onSongIn(search)




def echo(bot, update):
    bot.sendMessage(update.message.chat_id, text=update.message.text)
    bot.sendMessage(update.message.chat_id, text="puto")

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("252159229:AAGgf0O_MZIvRjc4CBYO5QOCd-HwuzL0NiY")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler([Filters.text], hacerTodo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
