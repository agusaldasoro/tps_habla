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
import os
import time
import sys
import twx.botapi as tb
from watson_developer_cloud import SpeechToTextV1, TextToSpeechV1
import subprocess
import copy


stt = SpeechToTextV1(username='6f01e8bb-2faa-42a6-bec3-c1e236337b05', password='wRfZa13pn5Ke')
tts = TextToSpeechV1(username='823bf474-b3a1-454c-9daa-f39f1fe7fba8', password='UgSusuE0f3PZ')


class Bot(object):

    def __init__(self, token):
        self._last_update_fn = 'last_update.txt'
        self._token = token
        self._bot = tb.TelegramBot(token)
        self._bot.update_bot_info().wait()
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
        text_to_speech("todoBien.wav", "todo bien, querido",  rate_change="+0%", f0mean_change="+0%")

        print('Enviando respuesta.')
        self._send_audio_file(update.message.chat.id, 'todoBien.wav')
        
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

# Síntesis del texto 'text', especificando cambios en tasa de habla y f0, ambos en 
# porcentaje respecto del default del sistema. El resultado se guarda en 'filename'.
# Es posible que el wav generado tenga mal el header, lo cual se arregla con:
# sox -r 22050 filename.wav tmp.wav && mv tmp.wav filename.wav
def text_to_speech(filename, text, rate_change="+0%", f0mean_change="+0%", tts=tts):
    ssml_text = '<prosody rate="%s" pitch="%s"> %s </prosody>' % (rate_change, f0mean_change, text)
    with open(filename, 'wb') as audio_file:
        audio_file.write(tts.synthesize(ssml_text,
                                    accept='audio/wav',
                                    voice="es-US_SofiaVoice"))
    audio_file.close()



def main():
    
    if not os.path.exists('token.txt'):
        sys.stderr.write('Poner el token en el archivo token.txt.\n')
        sys.exit(1)
    token = open('token.txt').read().strip(' \t\r\n')
    bot = Bot(token)
    while True:
        bot.poll()
        time.sleep(0.2)

if __name__ == '__main__':
    main()