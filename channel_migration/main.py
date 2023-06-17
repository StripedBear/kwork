import argparse
import subprocess
import time
import yt_dlp as yt
from datetime import datetime
import shutil
import configparser
import jsonlines
import codecs
import scrapetube
from mysql import connector
from mysql.connector import *
import re

config = configparser.ConfigParser()
config.read_file(codecs.open("config.ini", 'r', 'utf8'))

# Видео-разрешение
formats = {
    'low': 'mp4[height<=480]',
    'medium': 'mp4[height<=720]',
    'high': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
}
table = config['DB']['table']


def remove_emoji_and_etc(string):
    """Удаление эмодзи"""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    no_emoji = emoji_pattern.sub(r'', string)
    remove_urls = re.sub(r'(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*', '', no_emoji)
    clear_slash = remove_urls.replace('\\', '').replace('"', '').replace("'", "")

    return clear_slash


def mysql_check(id):
    """Проверка если ли видео в БД"""
    try:
        with connect(
                host=config['DB']['host'],
                user=config['DB']['user'],
                password=config['DB']['password'],
                database=config['DB']['database']
        ) as connection:
            video_id = id + '.mp4'
            check_data_query = config['DB']['check_query']
            with connection.cursor(buffered=True) as cursor:
                cursor.execute(check_data_query, (video_id,))
                result = cursor.fetchone()
                return result
    except Error as e:
        print(e)


def mysql_insert(title, description, video, preview_video, preview, channel, category, publish):
    cnx = connector.connect(user=config['DB']['user'], password=config['DB']['password'],
                              host=config['DB']['host'],
                              database=config['DB']['database'])

    cursor = cnx.cursor()

    dt_object = datetime.now()
    timestamp1 = int(dt_object.timestamp())
    try:
        date_string = publish
        date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        timestamp = datetime.timestamp(date)
    except Exception as e:
        dt_object = datetime.now()
        timestamp = int(dt_object.timestamp())

    add_employee = ("INSERT INTO video "
               "(channel_id, title, description, preview, preview_video, video, created_at, updated_at) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    data_employee = (channel, title, description, preview, preview_video, video, timestamp1, timestamp1)

    cursor.execute(add_employee, data_employee)
    cnx.commit()

    iter = cursor.lastrowid

    add_employee = ("INSERT INTO categories_to_video "
               "(category_id, video_id) "
               "VALUES (%s, %s)")
    data_employee = (category, iter)

    cursor.execute(add_employee, data_employee)

    cnx.commit()

    cursor.close()
    cnx.close()


def links_prepare(file, quality, preview_length, ammount):
    """Открытие файла и подготовка к загрузке"""
    with open(file) as f:
        links = [line.strip() for line in f.readlines()]
    [check_video(link, quality, preview_length, ammount) for link in links]


def scrape(link, ammount):
    print('Получение ссылок')
    videos = scrapetube.get_channel(channel_url=link)
    ids = [next(videos)['videoId'] for i in range(ammount)]
    print('Ссылки получены')
    return ids


def check_video(link, quality, preview_length, ammount):

    """Проверка типа ссылки"""
    if link.startswith('https://www.youtube.com/watch?v='):
        with yt.YoutubeDL() as ydl:
            info = ydl.extract_info(link, download=False)
        if not mysql_check(info['id']):
            final_path = config['Path']['path_full'] + f'{info["id"]}.%(ext)s'
            preview_path = config['Path']['path_preview'] + f'{info["id"]}'
            download(final_path, quality, link, preview_length, preview_path)
        else:
            print('Запись уже имеется')
    else:
        playlist = scrape(link, ammount)

        for video in playlist:
            if not mysql_check(video):
                final_path = config['Path']['path_full'] + f"{video}.%(ext)s"
                preview_path = config['Path']['path_preview'] + f"{video}"
                download(final_path, quality, video, preview_length, preview_path)
            else:
                print('Запись уже имеется')


def download(final_path, quality, link, preview_length, preview_path):
    """Опции загрузки"""
    ydl_opts = {'writethumbnail': True,
                'outtmpl': final_path,
                "format": quality,
                'ignoreerrors': True,
                'skip_download': False,
                'write_description': True,
                'postprocessors': [{
                    'format': 'jpg',
                    'key': 'FFmpegThumbnailsConvertor',
                    'when': 'before_dl'
                    }],
                }
    """Загрузка видео, картинки, метаданных"""
    with yt.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        ydl.download(link)

    """Перемещение картинки"""
    src = f"{config['Path']['path_full']}{info['id']}.jpg"
    thumb = f"{config['Path']['path_full']}{config['Path']['path_thumb']}{info['id']}.jpg"
    shutil.move(src, thumb)

    """Превью"""
    cmd_str = f"yt-dlp --downloader ffmpeg " \
              f"--downloader-args 'ffmpeg:-t {preview_length}' '{link}' " \
              f"-o '{preview_path}-preview.%(ext)s' -f '{quality}'"
    subprocess.run(cmd_str, shell=True)

    """название и описание"""
    title = remove_emoji_and_etc(info['title'])
    description = remove_emoji_and_etc(info['description'])

    """publish, id и category"""
    publish = datetime.now()

    url = info['uploader_id']
    with jsonlines.open('preferences.jsonl') as f:
        preferences = [line for line in f]

    category_id = ''
    site_id = ''
    preview = f"{info['id']}.jpg"
    preview_video = f"{info['id']}-preview.mp4"
    video = f"{info['id']}.mp4"

    for line in preferences:
        if url in line["yt_channel"]:
            site_id = int(line["channel_id"])
            category_id = line["category"]
            break

    """Добавление в БД"""
    print('Добавляю базу')
    mysql_insert(title, description, video, preview_video, preview,  site_id, category_id, publish)


def main():
    """Аргументы"""
    parser = argparse.ArgumentParser(description='Парсер YouTube')
    parser.add_argument('-l', '--link', type=str, 
    	help='Ссылка на видео, канал, плейлист. Пример: -l "https://www.youtube.com/watch?v=VIDEO_EXAMPLE"')
    parser.add_argument('-p', '--preview', type=int, default=20, 
    	help='Длительность превью видео. По умолчанию: 20 сек')
    parser.add_argument('-a', '--ammount', type=int, default=20,
    	help='Количество видео. По умолчанию: 2')
    parser.add_argument('-q', '--quality', type=str, default='high', 
    	help='Качество видео. Варианты "low" mp4,480; "medium" mp4,720; "high" лучшее видео+лучший звук. '
             'По умолчанию: лучшее видео+лучший звук. Пример: -q "low"')
    parser.add_argument('-t', '--time', type=int,
    	help='Запуск парсера канала/плейлиста по таймеру в секундах. По умолчанию: 300 сек(5 мин). Пример: -t 500')
    parser.add_argument('-f', '--file', type=str, help='Файл с ссылками видео для загрузки. Пример: -f "my/file.txt"')
    args = parser.parse_args()

    """Проверка аргументов и запуск"""
    if args.link:
        if args.time:
            while True:
                print('Начало: ' + str(datetime.now()))
                check_video(args.link, formats[args.quality], args.preview, args.ammount)
                print(f"Готово. Перерыв - {args.time/60} мин.")
                time.sleep(args.time)
        else:
            check_video(args.link, formats[args.quality], args.preview, args.ammount)
    elif args.file:
        links_prepare(args.file, formats[args.quality], args.preview, args.ammount)


if __name__ == "__main__":
    main()
