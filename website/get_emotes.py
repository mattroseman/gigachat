import os
import json

import requests

EMOTE_DIR = './public/assets/emotes'
EMOTE_INFO_FILE_PATH = os.path.join(EMOTE_DIR, 'emote_info.json')

DGG_EMOTE_DIR = os.path.join(EMOTE_DIR, 'dgg')
DGG_EMOTE_STYLES_FILE_PATH = './public/assets/emotes/dgg_emotes.css'
DGG_EMOTE_API_URL = 'https://cdn.destiny.gg/2.38.0/emotes'
DGG_EMOTE_INFO_API_URL = os.path.join(DGG_EMOTE_API_URL, 'emotes.json')
DGG_EMOTE_STYLES_API_URL = os.path.join(DGG_EMOTE_API_URL, 'emotes.css')

TWITCH_API_URL = 'https://api.twitch.tv/helix'
TWITCH_BROADCASTER_INFO_API_URL = os.path.join(TWITCH_API_URL, 'users')
TWITCH_EMOTE_API_URL = os.path.join(TWITCH_API_URL, 'chat/emotes')

# TWITCH_CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID', '<paste Twitch Client-ID here>')
TWITCH_CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID', 'q6batx0epp608isickayubi39itsckt')
# TWITCH_AUTH_TOKEN = os.environ.get('TWITCH_AUTH_TOKEN', '<paste Twitch Authentication Token here>')
TWITCH_AUTH_TOKEN = os.environ.get('TWITCH_AUTH_TOKEN', '02c08swk8t4hee8izv6syws0s27pq3')

emote_info = {
    'dgg': [],
    'twitch': [],
    'youtube': []
}


def main():
    get_dgg_emotes()
    get_twitch_emotes()

    with open(EMOTE_INFO_FILE_PATH, 'w') as emote_info_file:
        emote_info_file.write(json.dumps(emote_info))


def get_dgg_emotes():
    print('\nGETTING DGG EMOTES\n')

    response = requests.get(DGG_EMOTE_STYLES_API_URL).text

    with open(DGG_EMOTE_STYLES_FILE_PATH, 'w') as dgg_styles_file:
        dgg_styles_file.write(response)

    response = requests.get(DGG_EMOTE_INFO_API_URL).json()

    for emote in response:
        name = emote['prefix']
        url = emote['image'][0]['url']
        file_type = url.split('.')[-1]
        file_name = f'{name}.{file_type}'
        height = emote['image'][0]['height']
        width = emote['image'][0]['width']

        emote_info['dgg'].append({
            'name': name,
            'url': f'/assets/emotes/dgg/{file_name}',
            'height': height,
            'width': width
        })

        file_path = os.path.join(DGG_EMOTE_DIR, file_name)

        file_contents = requests.get(url).content

        with open(file_path, 'wb') as image_file:
            image_file.write(file_contents)

        print(f'name: {name} url: {url}')


def get_twitch_emotes():
    print('\nGETTING TWITCH EMOTES\n')

    headers = {
        'Authorization': f'Bearer {TWITCH_AUTH_TOKEN}',
        'Client-ID': TWITCH_CLIENT_ID
    }
    broadcaster_id = requests.get(
        TWITCH_BROADCASTER_INFO_API_URL,
        params={'login': 'Destiny'},
        headers=headers
    ).json()['data'][0]['id']

    response = requests.get(
        TWITCH_EMOTE_API_URL,
        params={'broadcaster_id': broadcaster_id},
        headers=headers
    ).json()

    for emote in response['data']:
        name = emote['name']
        url = emote['images']['url_1x']

        emote_info['twitch'].append({
            'name': name,
            'url': url
        })

        print(f'name: {name} url: {url}')


if __name__ == '__main__':
    main()
