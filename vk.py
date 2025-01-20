

import requests
from pprint import pprint
from progress.bar import IncrementalBar
import time
import json


class VK:
    ACCESS_TOKEN = 'vk1.a.xX8ibI9CaZivlOZPqCTg1jUpwb0pJ2Fg_0EQmYuYqCBglWMf8eW9JQ3_bv561lHGlPXntByvI_VEAKVr2znzmZAre67wsPhujCrxtu56DYgbBzk7ZbvGM6ZxOTKXPQu0QEaIhd0VpJc5EqgQRyZfuOqYookxdff2nGz_nk1BfL_Tca0U2UtnRpKbqCFbw6SyzBBm_oNd5IAuoKutx543kw' # токен полученный из инструкции

    def __init__(self, user_id: str, token_yandex: str, version='5.131', access_token=ACCESS_TOKEN, count: int=5):
        self.token_yandex = token_yandex
        self.token = access_token
        self.id = user_id
        self.version = version
        self.count = count
        self.params = {'access_token': self.token, 'v': self.version}
        self._folder = self.create_folder_on_yandex()
        self.get_info = self._get_info(self.count)
        self.photos_max_size = self._get_photos_max_size()

    def _get_info(self, count):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': 'profile', 'count': count, 'extended': 1}
        response = requests.get(url, params={**self.params, **params})
        if 'error' in response.json():
            raise Exception(f'Get_info:\nКод ошибки: {response.json()['error']['error_code']}.\n'
                            f'Информация: {response.json()['error']['error_msg']}')
        else:
            print('Get_info:\nДанные из VK получены.\n')

        return response.json()


    def _get_photos_max_size(self):
        items = self.get_info['response']['items']
        photos_max_size = []
        bar = IncrementalBar('Get photos max size:'.ljust(40, ' '), max=len(items))

        for item in items:
            url_max_photo = item['orig_photo']
            max_size = item['orig_photo']['height'] * item['orig_photo']['width']
            photo_likes = item['likes']['count']
            date = item["date"]

            for size in item['sizes']:
                if size['height'] * size['width'] > max_size:
                    url_max_photo = size
                    max_size = size['height'] * size['width']
                    pprint(size)

            url_max_photo['name'] = f'{photo_likes}_{time.ctime(date).replace(' ', '_').replace(':', '_')}'
            photos_max_size.append(url_max_photo)
            bar.next()
        bar.finish()
        print()


        return photos_max_size

    def _save_json_info(self, photos_info: list, name: str):
        with open(f'{name}.json', 'w', encoding='utf-8') as f:
            json.dump(photos_info, f)

    def create_folder_on_yandex(self, token_yandex: str=None, folder_name: str='folder'):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': f'/{folder_name}'}
        if token_yandex == None:
            token = self.token_yandex
        headers = {'Authorization': token}
        resp = requests.put(url, params=params, headers=headers)
        if 'error' in resp.json():
            print(f'create_folder_on_yandex:\n{resp.json()['message']} Удалите папку или создайте с другим именем.\n')
        else:
            print(f'Create folder on the yandex:\nУспешное создание папки {folder_name}\n')


    def send_photos_to_yandex(self, photos: list, token_yandex: str=None, folder_name: str='folder',  ):
        if token_yandex == None:
            token = self.token_yandex
        photos_save_info = []
        photos_save_error = []
        bar = IncrementalBar('Send photos to yandex:'.ljust(40, ' '), max=len(photos))
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Authorization': token}

        for photo in photos:
            params = {'path': f'/{folder_name}/{photo['name']}.jpeg', 'url': photo['url']}
            resp = requests.post(url, params=params, headers=headers)
            if 'error' in resp.json():
                photos_save_error.append({'file_name': f'{photo['name']}.jpeg',
                                         'error': f'{resp.json()['message']}'})
            else:
                photos_save_info.append({'file_name': f'{photo['name']}.jpeg',
                                         'size': photo['type']})
            bar.next()
        bar.finish()
        self._save_json_info(photos_save_info, 'save_complete')
        print(f'Сохранено на яндекс диске: {len(photos_save_info)} из {len(photos)}')

        if len(photos_save_error) != 0:
            print('Ошибки смотреть в errors.json')
            self._save_json_info(photos_save_error, 'errors')
        if len(photos_save_info) != 0:
            print('Результаты сохранения смотреть в save_complete.json')




token_yandex = 'y0__wgBEJ-dhNgHGNuWAyCyhpSGEjonA8Oso71VgEJwnKz265VaQofZ' # Токен яндекса
user_id = '1022983605' # идентификатор пользователя vk

vk = VK(user_id, token_yandex, count=2)


# vk.create_folder_on_yandex(folder_name='folder')
vk.send_photos_to_yandex(photos=vk.photos_max_size)
