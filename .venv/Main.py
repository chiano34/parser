import logging
import asyncio
import tgcrypto
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.errors import UsernameNotOccupied
from pyrogram.raw.functions.contacts import ResolveUsername
import datetime
import string
import time
import os
from Config import PHONE_NUMBER,API_ID,API_HASH

# Инициализация Pyrogram клиента с использованием номера телефона
pyrogram_client = Client("my_account", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)

#Переменные для хранения наборов слов и каналов
#Путь для хранения файлов
path_files='files/'
#Каналы для мониторинга
channels_monitoring_filename='channels_monitoring.txt'
#Результаты обработки каналов
file_save='results.txt'
#Хранение слов для поиска
words_filename="words.txt"
# Настройка логирования 
logging.basicConfig(level=logging.INFO)
#Словарь для хранения слов
words_monitoring={}
#создание словоря для хранения каналов
channels_monitoring={}
#переменная для проверки статуса мониторинга
comments_check=False
#переменная для проверки статуса мониторинга
message_check=True
#Функция для чтения каналов для мониторинга
def read_channels_monitoring():
    with open(path_files+channels_monitoring_filename, 'r') as file:
        lines = file.readlines()
    global channels_monitoring
    channels_monitoring={}
    for line in lines:
        print(line)
        channels_monitoring[line] = 0
#Функция для получения даты, которая была указанное количество часов назад
def minute_ago(minute,time):
    past = time - datetime.timedelta(minutes=int(minute))
    return past
#включение комментариев
def comments_on():
    global comments_check
    comments_check=True
#отключение комментариев
def comments_off():
    global comments_check
    comments_check=False
#включение постов
async def post_on():
    global message_check
    message_check=True
#отключение постов
async def post_off():
    global message_check
    message_check=False
#Функция для нахождение слов в строке
def find_words(text, search_words):
    words = search_words.split()
    count=0
    text_lower = text.lower()
    for word in words:
        if word.lower() in text_lower:
            count+= 1
    if len(words)==count:
        return True
    else:
        return False
#Функция для чтения слов для мониторинга
def read_words_monitoring():
    with open(path_files+words_filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    global words_monitoring
    words_monitoring={}
    for line in lines:
        words_monitoring[line] = 0
#Функция для сохранения постов в txt
def add_results(filename,time,text):
    try:
        with open(path_files+filename, 'a') as file:  # Открываем файл в режиме добавления
            file.write("\nВремя:\n" +str(time)+"\nТекст:\n"+str(text)+"\n")  # Записываем строку с переводом строки
        print(f'Строка добавлена в файл {filename}.')
    except Exception as e:
        print(f'Произошла ошибка: {e}')
def add_channel_to_file(filename, channel):
    try:
        with open(path_files+filename, 'a') as file:  # Открываем файл в режиме добавления
            file.write("\nКанал:"+str(channel)+"\n")  # Записываем строку с переводом строки
        print(f'Строка добавлена в файл {filename}.')
    except Exception as e:
        print(f'Произошла ошибка: {e}')

async def monitoring_start(time_msg):
    global message_check
    global comments_check
    read_channels_monitoring()
    read_words_monitoring()
    # Если необходимо установить диапозон по времени
    # datecheck=minute_ago(time_msg,datetime.datetime.now())
    for channel_name in channels_monitoring:
        print(f"обработка канала:{channel_name}")
        try:
            add_channel_to_file(file_save,channel_name)
            async for message in pyrogram_client.get_chat_history(channel_name):
                try:
                    # Если необходимо установить диапозон по времени
                    # if message.date<datecheck:
                    #     break
                    if message_check:
                        #Для скачивания фотографий
                        # if message.photo:
                        #     await pyrogram_client.download_media(message.photo, file_name=os.path.join(DOWNLOAD_FOLDER, f"{message.id}.jpg"))
                        if message.text!=None:
                            for word in words_monitoring:
                                if find_words(message.text,word):
                                    add_results(file_save,message.date,message.text)
                        elif message.caption!=None:
                            for word in words_monitoring:
                                if find_words(message.caption,word):
                                    add_results(file_save,message.date,message.caption)
                    #Обработка комментариев
                    #replies = pyrogram_client.get_discussion_replies(message.chat.id, message.id)
                    # try:
                    #     count = await pyrogram_client.get_discussion_replies_count(message.chat.id, message.id)
                    # except Exception as e:
                    #     continue
                    # #Вывод комментариев
                    # if comments_check:
                    #     async for reply in replies:
                    #         if reply.photo:
                    #             await pyrogram_client.download_media(reply.photo, file_name=os.path.join(DOWNLOAD_FOLDER, f"{reply.id}.jpg"))
                    #         if reply.text!=None:
                    #             print(reply.text)
                    #         if reply.caption!=None:
                    #             print(reply.caption)
                except FloodWait as e:
                    time.sleep(e.value)
        except UsernameNotOccupied:
            print(f"Канал не существует\n")



async def main():
    await pyrogram_client.start()
    #проверка существования папки для сохранения изображений
    #Чтение всех постов в часах
    await monitoring_start(240)


if __name__ == '__main__':
    asyncio.run(main())