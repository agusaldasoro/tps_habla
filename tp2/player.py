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
    
    def isPausedByUser(self):
        return isPaused

    def changeSong(self, songPath):
        self.player.set_mrl(songPath)


    def run(self):
        player = vlc.MediaPlayer(self.songPath)
        print 'reproduciendo ' + self.songPath
        player.play()
        time.sleep(0.3)
        playing = player.get_state()
        print "reproduzco"
        while not ( clm.is_set() ) and (player.get_state() == playing):
            pass
        clm.clear()
        player.stop()
        onSongEnd()
        return


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

def main():
    
    p = playerThread('musica/todoBien.wav')
    p.run()


if __name__ == '__main__':
    main()

