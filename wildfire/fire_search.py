import csv
import os
import re
import shutil
import warnings
import tarfile
from datetime import datetime
import numpy as np
import json
import glob

from pywebio.input import *
from scipy.ndimage import center_of_mass
from skimage.transform import resize
import rasterio
import cv2
from pywebio import start_server, config
from pywebio.output import *
from rasterio.errors import NotGeoreferencedWarning

from downloader import search_scenes as ss
from model import *

import downloader_link

# Данные пользователя для EarthExplorer
USER =
PASSWORD =

# Веса и модель
WEIGHTS_FILE = 'unet/train_output/model_unet_Schroeder_final_weights.h5'
MODEL_NAME = 'unet'

warnings.filterwarnings("ignore", category=NotGeoreferencedWarning)

N_FILTERS = 16
N_CHANNELS = 3
TH_FIRE = 0.25

IMAGE_SIZE = (256, 256)
MAX_PIXEL_VALUE = 65535


class MergeScene:
    def __init__(self):
        self.temp_folder = 'temp'

    def scene_merge(self, tar_path):
        # Создание временной папки, если она не существует
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)
        # Формирование имени выходного файла
        output_file = os.path.splitext(os.path.basename(tar_path))[0] + '.TIF'
        # Распаковка архива
        self.unpack(tar_path, self.temp_folder)
        # Получение метаданных
        metadata = self.get_metadata(self.temp_folder)
        # Объединение сцены
        self.merge(self.temp_folder, output_file)
        # Удаление следов распакованного архива
        self.delete_traces(tar_path)
        # Возвращение имени выходного файла и метаданных
        return output_file, metadata

    def unpack(self, tar_path, extract_dir):
        # Отображение информации о процессе распаковки
        with use_scope('info', clear=True):
            put_text('Распаковка архива...').style('text-align: center')
            put_loading().style('text-align: center')
        # Распаковка архива
        with tarfile.open(tar_path, 'r') as tar:
            tar.extractall(extract_dir)

    def get_metadata(self, temp_folder):
        try:
            # Поиск файла с метаданными формата JSON
            file_path = glob.glob(temp_folder + "/*MTL.json")[0]
            # Чтение и загрузка данных метаданных JSON
            with open(file_path, "r") as f:
                mtl_data = json.load(f)
            # Извлечение углов сцены и других метаданных
            UL_CORNER = (
            float(mtl_data["LANDSAT_METADATA_FILE"]["PROJECTION_ATTRIBUTES"]["CORNER_UL_LAT_PRODUCT"]),
            float(mtl_data["LANDSAT_METADATA_FILE"]["PROJECTION_ATTRIBUTES"]["CORNER_UL_LON_PRODUCT"]))
            UR_CORNER = (
            float(mtl_data["LANDSAT_METADATA_FILE"]["PROJECTION_ATTRIBUTES"]["CORNER_UR_LAT_PRODUCT"]),
            float(mtl_data["LANDSAT_METADATA_FILE"]["PROJECTION_ATTRIBUTES"]["CORNER_UR_LON_PRODUCT"]))
            LL_CORNER = (
            float(mtl_data["LANDSAT_METADATA_FILE"]["PROJECTION_ATTRIBUTES"]["CORNER_LL_LAT_PRODUCT"]),
            float(mtl_data["LANDSAT_METADATA_FILE"]["PROJECTION_ATTRIBUTES"]["CORNER_LL_LON_PRODUCT"]))
            LR_CORNER = (
                float(mtl_data["LANDSAT_METADATA_FILE"]["PROJECTION_ATTRIBUTES"]["CORNER_LR_LAT_PRODUCT"]),
                float(mtl_data["LANDSAT_METADATA_FILE"]["PROJECTION_ATTRIBUTES"]["CORNER_LR_LON_PRODUCT"]))

            date_acquired = mtl_data["LANDSAT_METADATA_FILE"]['IMAGE_ATTRIBUTES']["DATE_ACQUIRED"]
            time_acquired = mtl_data["LANDSAT_METADATA_FILE"]['IMAGE_ATTRIBUTES']["SCENE_CENTER_TIME"]
            print(UL_CORNER, UR_CORNER, LL_CORNER, date_acquired, time_acquired, LR_CORNER)
            return UL_CORNER, UR_CORNER, LL_CORNER, date_acquired, time_acquired, LR_CORNER
        except:
            # Поиск файла с метаданными формата TXT
            file_path = glob.glob(temp_folder + "/*MTL.txt")[0]
            with open(file_path, "r") as f:
                mtl_content = f.read()

            ul_corner_match = re.search(r'CORNER_UL_\s*=\s*([-+]?[0-9]*\.?[0-9]+)\s*', mtl_content)
            ur_corner_match = re.search(r'CORNER_UR_\s*=\s*([-+]?[0-9]*\.?[0-9]+)\s*', mtl_content)
            ll_corner_match = re.search(r'CORNER_LL_\s*=\s*([-+]?[0-9]*\.?[0-9]+)\s*', mtl_content)
            lr_corner_match = re.search(r'CORNER_LR_\s*=\s*([-+]?[0-9]*\.?[0-9]+)\s*', mtl_content)
            date_acquired_match = re.search(r'DATE_ACQUIRED\s*=\s*([\w\d]+)\s*', mtl_content)
            time_acquired_match = re.search(r'SCENE_CENTER_TIME\s*=\s*([\w\d:.]+)\s*', mtl_content)

            if ul_corner_match and ur_corner_match and ll_corner_match and date_acquired_match and time_acquired_match:
                ul_corner = float(ul_corner_match.group(1))
                ur_corner = float(ur_corner_match.group(1))
                ll_corner = float(ll_corner_match.group(1))
                date_acquired = date_acquired_match.group(1)
                time_acquired = time_acquired_match.group(1)

                return ul_corner, ur_corner, ll_corner, date_acquired, time_acquired, lr_corner_match

            return None

    def merge(self, channel_dir, output_file):
        # Получение списка файлов каналов
        channel_files = os.listdir(channel_dir)
        channel_paths = []
        # Фильтрация и выбор только файлов TIF, относящихся к каналам
        for file in channel_files:
            if file.endswith('.TIF') and file.split('_')[-1].startswith('B') and not file.split('_')[-1].startswith(
                    'B11') and not file.split('_')[-1].startswith('B10'):
                channel_paths.append(os.path.join(channel_dir, file))
        with use_scope('info', clear=True):
            put_text('Уменьшение...').style('text-align: center')
            put_loading().style('text-align: center')
        resized_channels = []
        # Уменьшение размеров каналов и сохранение их в список
        for path in channel_paths:
            with rasterio.open(path) as channel:
                channel_data = channel.read(1)
                resized_channel = resize(channel_data, (256, 256), preserve_range=True)
                resized_channels.append(resized_channel)
        # Объединение каналов в одно изображение
        merged_image = np.stack(resized_channels, axis=0)
        with use_scope('info', clear=True):
            put_text('Объединение каналов...').style('text-align: center')
            put_loading().style('text-align: center')
        # Запись объединенного изображения в файл формата GTiff
        with rasterio.open(
                output_file,
                'w',
                driver='GTiff',
                width=merged_image.shape[2],
                height=merged_image.shape[1],
                count=merged_image.shape[0],
                dtype=merged_image.dtype
        ) as dst:
            dst.write(merged_image)

    def delete_traces(self, tar_path):
        # Удаление исходного архива
        os.remove(tar_path)
        # Удаление временной папки
        shutil.rmtree(self.temp_folder)


def load_model():
    # Загрузка модели
    model = get_model(MODEL_NAME, input_height=IMAGE_SIZE[0], input_width=IMAGE_SIZE[1], n_filters=N_FILTERS,
                      n_channels=N_CHANNELS)
    with use_scope('info', clear=True):
        put_text('Загрузка весов...').style('text-align: center')
        put_loading().style('text-align: center')
    # Загрузка весов модели
    model.load_weights(WEIGHTS_FILE)
    with use_scope('info', clear=True):
        put_text('Веса загружены').style('text-align: center')
    return model


def save_csv(data_list, filename):
    # Сохранение данных в CSV файл
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(data_list)


def get_fire_c(prediction, metadata):
    # Извлечение метаданных для четырех углов изображения
    UL_LAT = metadata[0][0]
    UL_LON = metadata[0][1]
    UR_LAT = metadata[1][0]
    UR_LON = metadata[1][1]
    LL_LAT = metadata[2][0]
    LL_LON = metadata[2][1]
    LR_LAT = metadata[5][0]
    LR_LON = metadata[5][1]
    # Рассчет широты и долготы центра изображения
    center_lat = (UL_LAT + UR_LAT + LL_LAT + LR_LAT) / 4
    center_lon = (UL_LON + UR_LON + LL_LON + LR_LON) / 4
    # Рассчет координатов центра пожара на изображении
    coords = center_of_mass(prediction)
    center_y, center_x = coords
    # Пиксельные координаты центра изображения
    image_center_pixel_x = 256 / 2
    image_center_pixel_y = 256 / 2
    # Разница между центром огня и центром изображения в направлениях x и y
    delta_x = center_x - image_center_pixel_x
    delta_y = center_y - image_center_pixel_y
    image_width = 256
    image_height = 256
    # Расчет масштабных коэффициентов для преобразования координат пикселей в широту и долготу
    lon_scale = (metadata[1][1] - metadata[0][1]) / image_width
    lat_scale = (metadata[0][0] - metadata[2][0]) / image_height
    #  Широта и долгота очага возгорания
    fire_center_lon = center_lon + delta_x * lon_scale
    fire_center_lat = center_lat - delta_y * lat_scale

    return fire_center_lat, fire_center_lon


def fire_s(pic, metadata):
    # Открытие файла
    img = rasterio.open(pic)
    # Чтение определенных участков изображения и транспонирование массива
    img = img.read((7, 6, 2)).transpose((1, 2, 0))
    # Преобразование массива изображений в float32 и нормализация значений пикселей
    img = np.float32(img) / MAX_PIXEL_VALUE
    # Загрузка модеолм
    model = load_model()
    # Сделать прогноз по изображению
    prediction = model.predict(np.array([img]), batch_size=1)
    # Порог предсказания для получения противопожарной маски
    prediction = prediction[0, :, :, 0] > TH_FIRE
    # Подсчет количества огненных пикселей
    count = (prediction > 0).sum()
    # Преобразование массива предсказания в массив uint8 для визуализации
    prediction = np.array(prediction * 255, dtype=np.uint8)

    with use_scope('info', clear=True):
        put_text('Результат распознавания:').style('text-align: center')
    if count > 0:
        # Рассчет координатов очага возгорания
        x, y = get_fire_c(prediction, metadata)
        with use_scope('info'):
            put_text('Пожар обнаружен').style('text-align: center')
            # Рассчет площади пожара в квадратных километрах
            s = round(((count*(936.21*936.21))/1000000), 3)
            put_text(f'Площадь возгорания: {s} кв.км').style('text-align: center')
        # Преобразование массива предсказаний в формат BGR для сохранения в виде изображения
        fire = cv2.cvtColor(prediction, cv2.COLOR_RGB2BGR)
        cv2.imwrite('fire_image.jpg', fire)
        with open('fire_image.jpg', 'rb') as img:
            put_image(img.read()).style('display: block; margin-left: auto; margin-right: auto')
        put_text("Координаты центра пожара :", x, y).style('text-align: center')
        # Подготовка данных для сохранения в файл CSV
        to_scv = [str(metadata[3]), str(metadata[4]), str(s), str(x), str(y)]
        file_name = datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(':', '_')
        save_csv(to_scv, f'{file_name}.csv')
        put_text(f"Данные записаны в {file_name}.csv").style('text-align: center')
    else:
        with use_scope('info'):
            put_text('Пожар не обнаружен').style('text-align: center')
        return ''


@config(theme="yeti")
def search_app():
    with use_scope('app', clear=True):
        with open('WILDFIRE.png', 'rb') as img:
            put_image(img.read()).style('width:100%')
        # Пользовательский ввод для параметров поиска
        data = input_group("Параметры", [
            input("Искать с:", type=DATE, name='search_from', required=True),
            input("По:", type=DATE, name='search_to', required=True),
            input("Широта:", type=FLOAT, name='latitude', required=True),
            input("Долгота:", type=FLOAT, name='longitude', required=True),
            slider("Облачность", min_value=0, max_value=10, step=1, name='cloudiness')
        ])
        # Выбор набор данных
        d_set = select("Dataset", options=["Landsat 8 Collection 2 Level 1", "Landsat 8 Collection 2 Level 2"],
               selected='Landsat 8 Collection 2 Level 1')
        with use_scope('info'):
            put_text('Отправляю запрос...').style('text-align: center')
            put_loading().style('text-align: center')
        # Поиск сцен на основе пользовательского ввода
        scenes = ss(USER, PASSWORD, data['search_from'], data['search_to'],
                    data['latitude'], data['longitude'], data['cloudiness'],
                    d_set)
        with use_scope('info', clear=True):
            put_text('')
        if len(scenes) < 1:
            scenes = ['Сцен с такими параметрами нет']
            put_button('Назад', onclick=search_app)
        scene = select("Сцены", options=scenes)
        with use_scope('info', clear=True):
            put_text('Скачиваю. Закройте всплывающее окно когда архив будет загружен полностью.').style('text-align: center')
            put_loading().style('text-align: center')
        try:
            # Загрузка выбранной сцены
            path = downloader_link.download(USER, PASSWORD, scene)
        except Exception as e:
            print(e)
            put_error('Сервер USGS перегружен. Попробуйте позже', closable=True, scope='info', position=-1)
        try:
            # Объединение файла сцены и получение метаданных
            merge_scene = MergeScene()
            pic, metadata = merge_scene.scene_merge(path)
            # Обработка объединенной сцены для обнаружения пожара
            fire_s(pic, metadata)
        except Exception as e:
            put_error(f'Неизвестная ошибка: {e}', closable=True, scope='info', position=-1)
        put_button('Назад', onclick=search_app).style('text-align: center')


if __name__ == '__main__':
    start_server(search_app, port=8080)
