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

        print('TODO: procesar el archivo audio.ogg.')

        print('Enviando respuesta.')
        self._send_audio_file(update.message.chat.id, 'audio.ogg')
        
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
