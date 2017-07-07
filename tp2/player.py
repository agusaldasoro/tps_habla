import threading
import vlc
import time

class playerThread(threading.Thread):

    def __init__(self,songPath):
        super(playerThread, self).__init__()
        self.player = vlc.MediaPlayer(songPath)
        self.isPaused = True
         
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

    def __init__(self,playList,mediaPlayer):
        super(playlistHandler, self).__init__()
        self.player = mediaPlayer
        self.play = True
        self.playlist = playList
        self.currentSong = 0

    def runPlaylist(self):

        for i in self.playlist:
            self.player.changeSong(i)
            self.player.play()
            time.sleep(0.3)
            while (self.player.playerStatus() == vlc.State.Playing) or (self.player.isPausedByUser()):
                if not self.play:
                    return
                pass
            
            if not self.play:
                return

