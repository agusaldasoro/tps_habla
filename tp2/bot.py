#!/usr/bin/env python
# coding:utf-8:

"""
1) Para crear un nuevo bot en Telegram:

1a) Agregar al usuario @BotFather en Telegram.

1b) Crear un nuevo bot mandándole el comando /newbot
    al usuario @BotFather. Guardar el token del nuevo bot
    en el archivo token.txt.

1c) Deshabilitar la privacidad para el nuevo bot
    mandándole el comando /setprivacy al usuario @BotFather.
    Esto es para que el nuevo bot pueda ver todos los
    updates, inclusive los que no son mensajes dirigidos a él.

2) Para ejecutar este bot:

2a) Instalar twx.botapi con "pip install twx.botapi".
    (Alternativa: git clone https://github.com/datamachine/twx.botapi.git )

2b) Ejecutar este script y esperar a que diga "Bot levantado.".
    Para probarlo, agregar el nuevo bot a algún grupo de Telegram
    y mandar un mensaje de voz a ese grupo.
"""

"""
Librerias necesarias:
    pip install twx.botapi
    pip install --upgrade watson-developer-cloud
"""
import os
import time
import sys
import re
import random
import unicodedata
import twx.botapi as tb
from watson_developer_cloud import SpeechToTextV1, TextToSpeechV1
import subprocess
import copy
import player
import threading
import time

''' Usa la cuenta de la catedra, de hacer falta deberiamos tener una
'''
stt = SpeechToTextV1(username='6f01e8bb-2faa-42a6-bec3-c1e236337b05', password='wRfZa13pn5Ke')
tts = TextToSpeechV1(username='823bf474-b3a1-454c-9daa-f39f1fe7fba8', password='UgSusuE0f3PZ')


# Regex para STT
escucharMusica = r'(quiero|gust|musica|tema|cancion|genero|escuchar|play|pone|rock|nacional|espanol|ingles|pop|decada|años|cincuent|sesent|setent|ochent|novent|dos mil|dos mil diez|cumbia|latin|salsa)'
rockNacional = r'(nacional|argentino|espanol|rock de los ochen|rock ochen|rock de ochen)'
rockInternacional = r'(internacional|ingles)'
pop = r'pop'
sesenta = r'sesent'
setenta = r'setent'
ochenta = r'ochent'
noventa = r'novent'
dosMil = r'dos mil'
cumbia = r'(cumbia|colombianos)'
latinos = r'(latino|salsa|merengue|melodico|baladas)'

modificadores = r'(mas|menos|cambiar|subir|bajar|fuerte|alto|bajo|agudo|grave)'
subirVolumen = r'(subir el volumen|subir volumen|mas fuerte|mas alto|mas volumen)'
bajarVolumen = r'(bajar el volumen|bajar volumen|mas bajo|menos fuerte|menos volumen)'
subirTono = r'(subir el tono|subir tono|mas agudo|menos grave)'
bajarTono = r'(bajar el tono|bajar tono|mas grave|menos agudo)'
subirVelocidad = r'(subir la velocidad|subir velocidad|mas rapido|menos lento|sube la velocidad)'
bajarVelocidad = r'(bajar la velocidad|bajar velocidad|mas lento|menos rapido|baja la velocidad)'

pausar = r'(pasar|posar|pausa|para|stop|basta|no quiero|listo)'

nextSong = r'(avanzar|siguiente|next|proximo|lo escuche|la escuche|ya escuche|repetido|otro|otra|no me gust|no gust)'

insultos = r'(tonta|perra|estupida|puta|hija de|tarada|boluda|pelotuda|inutil)'

queEscucha = r'(escuch|suena|sonando|sono|que tema es|que cancion es|que es esto|que pusiste|no lo conozco|informacion)'


playlists = {}
nextSongEvent = threading.Event()
stopEvent = threading.Event()
p = player.playerThread('todoBien.wav')
handler = player.playlistHandler([],p,nextSongEvent,stopEvent)
class Bot(object):

    def __init__(self, token):
        self._last_update_fn = 'last_update.txt'
        self._token = token
        self._bot = tb.TelegramBot(token)
        self._bot.update_bot_info().wait()
        self.mediaPlayer = player.playerThread('todoBien.wav')
        print('Bot levantado.')

    def poll(self):
        updates = self._bot.get_updates(offset=self._get_last_update() + 1).wait()
        for update in updates:
            self._set_last_update(update.update_id)
            self.handle_update(update)

    def handle_update(self, update):
        if update.message is None or update.message.voice is None:
            print('Update {id} ignorado (no contiene un mensaje de voz).'.format(id=update.update_id))
            return

        print('Procesando update {id}.'.format(id=update.update_id))

        print('Bajando audio.')
        self._receive_audio_file(update.message.voice.file_id, 'audio.ogg')

        '''Transforms the voice message received by the bot in to text '''

        os.system('ffmpeg  -i audio.ogg audio.wav')

        mensajeAAnalizar = speech_to_text("audio.wav")
        print("ESTE ES EL MENSAJE: ")
        print(mensajeAAnalizar)
        os.remove("audio.wav")
        response = self.obtenerRespuesta(mensajeAAnalizar)

        text_to_speech("response.wav", response,  rate_change="+0%", f0mean_change="+0%")

        print('Enviando respuesta.')
        self._send_audio_file(update.message.chat.id, 'response.wav')

        print('Listo.\n')

    def _receive_audio_file(self, file_id, filename):
        info = self._bot.get_file(file_id).wait()
        self._bot.download_file(info.file_path, filename).wait()

    def _send_audio_file(self, chat_id, filename):
        f = open(filename, 'r')
        info = tb.InputFileInfo(filename, f, 'audio/ogg')
        self._bot.send_voice(chat_id, tb.InputFile('voice', info)).wait()
        f.close()

    def _set_last_update(self, last_update_id):
        f = open(self._last_update_fn, 'w')
        f.write(str(last_update_id) + '\n')
        f.close()

    def _get_last_update(self):
        if os.path.exists(self._last_update_fn):
            f = open(self._last_update_fn, 'r')
            line = f.readline()
            f.close()
            return int(line.strip(' \t\r\n'))
        else:
            return -1

    def obtenerRespuesta(self, voiceMessage):
        ''' Finds the correct answer and action for the message '''
        try:
            transcript = voiceMessage[u'results'][0][u'alternatives'][0][u'transcript']
            print(transcript)
            return procesarPedido(transcript)
        except:
            return noEntendiNada()

def procesarPedido(transcript):
    transcript = unicodedata.normalize('NFKD', transcript).encode('ascii','ignore')
    print(transcript)

    if insulto(transcript):
        return devolverInsulto()
    if quierePausa(transcript):
        return pausa()
    if cambiarModo(transcript):
        return modo(transcript)
    if siguiente(transcript):
        return avanzar()
    if quiereMusica(transcript):
        return genero(transcript)
    if quiereSaberTema(transcript):
        return queEstoyEscuchando()
    return noEntendiNada()

def quiereMusica(transcript):
    return re.search(escucharMusica, transcript, re.M|re.I)

def genero(transcript):
    if re.search(r'rock', transcript, re.M|re.I):
        if re.search(rockNacional, transcript, re.M|re.I) and not(re.search(rockInternacional, transcript, re.M|re.I)):
            handler = startPlaylist(playlists['rockNacional'])
            return "Qué sea Rock entonces"
        else:
            handler = startPlaylist(playlists['rock'])
            return "Divertite con un poco de lo mejor del Rock."
    if re.search(rockInternacional, transcript, re.M|re.I):
        handler = startPlaylist(playlists['rock'])
        return "Divertite con un poco de lo mejor del Rock."
    if re.search(rockNacional, transcript, re.M|re.I):
        handler = startPlaylist(playlists['rockNacional'])
        return "Qué sea Rock entonces"
    if re.search(pop, transcript, re.M|re.I):
        handler = startPlaylist(playlists['pop'])
        return "Vamos con los reyes y reinas del Pop."
    if re.search(sesenta, transcript, re.M|re.I):
        handler = startPlaylist(playlists['sesenta'])
        return "Bienvenido, bienvenido amor. Te esperaba sesenta primavera."
    if re.search(setenta, transcript, re.M|re.I):
        handler = startPlaylist(playlists['setenta'])
        return "Viajemos un poco en el tiempo, hacia la década del setenta."
    if re.search(ochenta, transcript, re.M|re.I):
        handler = startPlaylist(playlists['ochenta'])
        return "Tirá, tirá para arriba, ochenta"
    if re.search(noventa, transcript, re.M|re.I):
        handler = startPlaylist(playlists['noventa'])
        return "Noventa, viviendo la vida loca."
    if re.search(dosMil, transcript, re.M|re.I):
        handler = startPlaylist(playlists['dosMil'])
        return "El no fin del mundo, los años dos mil."
    if re.search(cumbia, transcript, re.M|re.I):
        handler = startPlaylist(playlists['cumbia'])
        return "Muestrame un poquito para ver cómo es. Esa cumbia."
    if re.search(latinos, transcript, re.M|re.I):
        handler = startPlaylist(playlists['latinos'])
        return "Baila latinos, que ritmo te sobra."

    verificarGenero = ["Qué te gustaría escuchar", "Qué género de música preferís", "Qué querés escuchar en especial", "Hoy qué tenés ganas de escuchar", "Te gustaría escuchar música de alguna década"]

    return random.choice(verificarGenero)

def cambiarModo(transcript):
    return re.search(modificadores, transcript, re.M|re.I)

def modo(transcript):
    if (re.search(subirVolumen, transcript, re.M|re.I)):
        p.subirVol()
        return "Subiré un poco más el volumen para que puedas oir mejor."
    if re.search(bajarVolumen, transcript, re.M|re.I):
        p.bajarVol()
        return "Bajaré un poco más el volumen para que tus timpanos se conserven."
    # if re.search(subirTono, transcript, re.M|re.I):
    #     return "Un poco más agudo será entonces."
    # if re.search(bajarTono, transcript, re.M|re.I):
    #     return "Vamos a agravar esta situación."
    # if re.search(subirVelocidad, transcript, re.M|re.I):
    #     return "Te gustan las ardillitas."
    # if re.search(bajarVelocidad, transcript, re.M|re.I):
    #     return "Hablemos cetáseo."

    verificarModo = ["Quisieras modificar el volumen", "Te gusta como está sonando", "Podés escucharlo más fuerte si querés"]
    return random.choice(verificarModo)

def quierePausa(transcript):
    return re.search(pausar, transcript, re.M|re.I)

def pausa():
    darPausa = ["Disculpa si este tema no fue de tu agrado", "No escucharemos más entonces", "Cuando quieras volvemos a escuchar la música que desees", "Mejor estemos en silencio por un rato", "Jugamos al oficio mudo"]
    stopPlaylist()
    return random.choice(darPausa)

def siguiente(transcript):
    return re.search(nextSong, transcript, re.M|re.I)

def avanzar():
    darNext = ["Avancemos", "OOtro tema", "Que pase el que sigue", "Mejor otra canción"]
    nextSongEvent.set()
    return random.choice(darNext)

def insulto(transcript):
    return re.search(insultos, transcript, re.M|re.I)

def devolverInsulto():
    devolvidas = ["Cree lo que quieras, pero yo soy superior a vos", "Y tú, sabés cuál es último dígito de Pi conocido", "Bueno, pero yo sigo aquí", "Justo aquí tienes el botón de cerrar aplicación"]
    stopPlaylist()
    return random.choice(devolvidas)

def quiereSaberTema(transcript):
    return re.search(queEscucha, transcript, re.M|re.I)

def queEstoyEscuchando():
    return "Lo Artesanal de Viejas Locas"

def noEntendiNada():
    instrucciones = ["Si quieres escuchar alguna canción sólo dime qué género te gustaría", "Te gustaría escuchar algo de música", "Para escuchar algún tema, sólo dime qué estilo te gusta y yo eligiré lo mejor para ti.", "Cuál es tu década favorita", "Tienes ganas de escuchar algo de pop", "Cómo está tu ánimo para escuchar unas cumbias", "Qué tipo de música te gustaría escuchar"]
    return random.choice(instrucciones)

def speech_to_text(filename, stt=stt):
    ''' Reconocimiento del archivo de audio 'filename'. 'max_alternatives' es la cantidad de hipótesis más probables a devolver.'''
    audio_file = open(filename, "rb")
    ibm_recognized = stt.recognize(audio_file,
                                 content_type="audio/wav",
                                 model="es-ES_BroadbandModel",
                                 timestamps="true",
                                 max_alternatives="1",
                                 continuous="true")
    return(ibm_recognized)

def text_to_speech(filename, text, rate_change="+0%", f0mean_change="+0%", tts=tts):
    ''' Síntesis del texto 'text', especificando cambios en tasa de habla y f0, ambos en
    porcentaje respecto del default del sistema. El resultado se guarda en 'filename'.
    Es posible que el wav generado tenga mal el header, lo cual se arregla con:
    sox -r 22050 filename.wav tmp.wav && mv tmp.wav filename.wav'''
    ssml_text = '<prosody rate="%s" pitch="%s"> %s </prosody>' % (rate_change, f0mean_change, text)
    with open(filename, 'wb') as audio_file:
        audio_file.write(tts.synthesize(ssml_text,
                                    accept='audio/wav',
                                    voice="es-US_SofiaVoice"))
    audio_file.close()



def stopPlaylist():
    #NO ME JUZGUES AGUSTINA
    p.userPause()
    stopEvent.set()
    time.sleep(0.5)

def startPlaylist(playList):

    #DO SOMETHING TO BUILD A PLAYLIST LIST?
    stopPlaylist()
    nextSongEvent.clear()
    stopEvent.clear()
    handler = player.playlistHandler(playList,p, nextSongEvent,stopEvent)
    print handler.playlist
    handler.start()
    return handler


def main():

    '''Build playlists from folders in musica/'''
    playlistsDir = os.listdir('musica/')
    for i in playlistsDir:
        playlists[i] = ['musica/' + i + '/' + j for j in os.listdir('musica/' + i + '/')]

    if not os.path.exists('token.txt'):
        sys.stderr.write('Poner el token en el archivo token.txt.\n')
        sys.exit(1)
    token = open('token.txt').read().strip(' \t\r\n')
    bot = Bot(token)
    while True:
        bot.poll()
        time.sleep(0.2)

def main2():

    '''Build playlists from folders in musica/'''
    playlistsDir = os.listdir('musica/')
    for i in playlistsDir:
        playlists[i] = ['musica/' + i + '/' + j for j in os.listdir('musica/' + i + '/')]
    handler = startPlaylist(playlists['rockNacional'])
    stopPlaylist()
if __name__ == '__main__':
    main()
