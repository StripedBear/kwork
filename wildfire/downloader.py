from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
from landsatxplore.errors import EarthExplorerError


dataset = {'Landsat 8 Collection 2 Level 1': 'landsat_ot_c2_l1', 'Landsat 8 Collection 2 Level 2': 'landsat_ot_c2_l2'}


def search_scenes(user, password, search_f, search_t, latitude, longitude, cloudiness, d_set):
    # Создание экземпляра API с указанием пользовательских данных
    api = API(user, password)
    print('Connected, searching...')
    # Поиск сцен с использованием API
    scenes = api.search(
        dataset=dataset[d_set],
        latitude=latitude,
        longitude=longitude,
        start_date=search_f,
        end_date=search_t,
        max_cloud_cover=cloudiness
    )
    # Извлечение идентификаторов найденных сцен
    found_scenes = [scene['entity_id'] for scene in scenes]
    api.logout()
    print(f'Found... {len(found_scenes)} scenes')
    return found_scenes


def download_scene(user, password, scene):
    try:
        ee = EarthExplorer(user, password)
    except EarthExplorerError:
        ee = EarthExplorer(user, password)
        print('Connection problem. Trying again later')
    try:
        name = ee.download(scene, output_dir='.')
    except:
        name = ee.download(scene, output_dir='.', skip=True, timeout=500)
    ee.logout()
    return name










