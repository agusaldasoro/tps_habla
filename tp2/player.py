import threading
import vlc


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
        return player.get_state()
    
    def isPausedByUser(self):of
        return isPaused

    def changeSong(self, songPath):
        ''' Changes the current media, player needs to be paused.''' 
        self.player.set_mrl(songPath)

class playlistHandler(threading.Thread):

    def __init__(self,playList,mediaPlayer):
        super(playerThread, self).__init__()
        self.player = mediaPlayer(playList[0])
        self.play = True
        self.playlist = playList
        self.currentSong = 0

    def runPlaylist(self):

        for i in self.playlist:
            self.player.changeSong(i)
            self.player.play()
            while (self.player.playerStatus() == playing) or (self.player.isPausedByUser()):
                if not self.play:
                    return
                pass
            
            if not self.play:
                return

