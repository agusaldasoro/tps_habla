import threading
import vlc
import time

class playerThread(threading.Thread):

    def __init__(self,songPath):
        super(playerThread, self).__init__()
        self.player = vlc.MediaPlayer(songPath)
        self.isPaused = True
        self.player.audio_set_volume(75)
        self.volumen = 75

    def bajarVol(self):

        self.volumen -= 25
        print self.volumen
        self.player.audio_set_volume(self.volumen)

    def subirVol(self):

        self.volumen += 25
        print self.volumen
        self.player.audio_set_volume(self.volumen)
    def play(self):
        self.isPaused = False
        self.player.play()

    def userPause(self):
        self.isPaused = True
        self.player.pause()    

    def playerStatus(self):
        return self.player.get_state()
    
    def isPausedByUser(self):
        return self.isPaused

    def changeSong(self, songPath):
        ''' Changes the current media, player needs to be paused.''' 
        self.player.set_mrl(songPath)

class playlistHandler(threading.Thread):

    def __init__(self,playList,mediaPlayer, aNextSongEvent,stopEvent):
        super(playlistHandler, self).__init__()
        self.player = mediaPlayer
        self.play = stopEvent
        self.playlist = playList
        self.currentSong = 0
        self.nextSongEvent = aNextSongEvent

    

    def run(self):

        for i in self.playlist:
            self.player.changeSong(i)
            self.player.play()
            time.sleep(0.3)
            while (self.player.playerStatus() == vlc.State.Playing and not self.nextSongEvent.is_set() ) or (self.player.isPausedByUser()):
                if self.play.is_set():
                    return
                pass
            self.nextSongEvent.clear()
            if self.play.is_set():
                return

def main():

    p= playerThread('todoBien.wav')
    nextSong = threading.Event()
    handler = playlistHandler(['my.mp3','musica/rock/oasis_wonderwall.m4a'],p,nextSong)
    handler.start()
    time.sleep(4.0)
    handler.play = False   
    handler = playlistHandler(['todoBien.wav'], p, nextSong)
    handler.start()
if __name__ == '__main__':
    main()
