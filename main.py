"""Main class"""

import datetime
import logging
import logging.handlers as loghandlers
import os
import sys

import telebot
from telebot import types

import config

BOT = telebot.TeleBot(config.TOKEN)


if not os.path.exists('tmp'):
    os.makedirs('tmp')
if not os.path.exists('logs'):
    os.makedirs('logs')

LOGGER = logging.getLogger('applog')
LOGGER.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s  %(filename)s  %(funcName)s  %(lineno)d  %(name)s  %(levelname)s: %(message)s')
log_handler = loghandlers.RotatingFileHandler(
    config.LOG_FILE, maxBytes=1000000, encoding="utf-8", backupCount=50)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(formatter)
LOGGER.addHandler(log_handler)
telebot.logger.setLevel(logging.INFO)
telebot.logger.addHandler(LOGGER)


@BOT.message_handler(commands=['start'])
def cmd_start(message):
    """Старт диалога с ботом"""
    mainmenu(message)


def mainmenu(message):
    """Главное меню"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_list = []
    keyboard_list.append('Скрин')
    keyboard.add(*keyboard_list, row_width=1)
    BOT.send_message(message.chat.id, 'Вы в главном меню',
                     reply_markup=keyboard)


@BOT.message_handler(content_types=['text'])
def mainmenu_choice(message):
    """Выбор пункта главного меню"""
    choice = message.text
    if choice == 'Скрин':
        take_screenshot(message)
    else:
        BOT.send_message(message.chat.id, 'Неизвестная команда')
        mainmenu(message)


def take_screenshot(message):
    """Сделать и отправить скриншот"""
    if not os.path.exists(f'tmp/{message.chat.id}'):
        os.makedirs(f'tmp/{message.chat.id}')

    now_timestamp = round(datetime.datetime.now().timestamp())
    filename = f'screen_{now_timestamp}.jpg'

    os.system(f'nircmd.exe savescreenshot tmp/{message.chat.id}/{filename}')
    LOGGER.info('screenshot taken')

    with open(f'tmp/{message.chat.id}/{filename}', 'rb') as img:
        # BOT.send_photo(message.chat.id, img)
        BOT.send_document(message.chat.id, img)
        mainmenu(message)


if __name__ == '__main__':
    try:
        BOT.infinity_polling()
    except Exception as ex:
        LOGGER.error(ex)
        sys.exit()
