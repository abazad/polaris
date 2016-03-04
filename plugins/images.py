from core.utils import *
from requests.auth import HTTPBasicAuth
import random, re

commands = [
    ('/image', ['query'])
]
description = 'This command performs a Google Images search for the given query.'

exts = {
    '.jpg$',
    '.jpeg$',
    '.gif$',
    '.png$',
    '.tif$',
    '.bmp$'
}


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, 'No input')

    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/Image'
    params = {
        'Query': "'" + input + "'",
        'Adult': "'Moderate'",
        '$format': 'json',
        '$top': '8'
    }
    auth = HTTPBasicAuth(config.keys.azure_key, config.keys.azure_key)

    if get_command(m) == 'insfw':
        params['Adult'] = "'Off'"

    jstr = requests.get(url, params=params, auth=auth)

    if jstr.status_code != 200:
        return send_message(m, '%s\n%s' % (lang.errors.connection, jstr.text))

    jdat = json.loads(jstr.text)

    if not len(jdat['d']['results']) != 0:
        return send_message(m, lang.errors.results)

    is_real = False
    counter = 0
    while not is_real:
        counter = counter + 1
        if counter > 5 or jdat['d']['results'] == '0':
            return send_message(m, lang.errors.results)

        i = random.randint(1, len(jdat['d']['results'])) - 1
        result_url = jdat['d']['results'][i]['MediaUrl']
        caption = '"{0}"  {1}'.format(input, get_short_url(result_url).lstrip('https://'))

        for v in exts:
            if re.compile(v).search(result_url):
                is_real = True

    photo = download(result_url)

    if photo:
        send_photo(m, photo, caption)
    else:
        send_message(m, lang.errors.download)


def inline(m):
    input = get_input(m)

    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/Image'
    params = {
        'Query': "'" + str(input) + "'",
        'Adult': "'Moderate'",
        '$format': 'json',
        '$top': '16'
    }
    auth = HTTPBasicAuth(config.keys.azure_key, config.keys.azure_key)

    if get_command(m) == 'insfw':
        params['Adult'] = "'Off'"

    jstr = requests.get(url, params=params, auth=auth)
    jdat = json.loads(jstr.text)

    results_json = []
    for item in jdat['d']['results']:
        ext = os.path.splitext(item['MediaUrl'])[1].split('?')[0]
        if ext != '.gif':
            result = {
                'type': 'photo',
                'id': item['ID'],
                'photo_url': item['MediaUrl'],
                'photo_width': int(item['Width']),
                'photo_height': int(item['Height']),
                'thumb_url': item['Thumbnail']['MediaUrl']
            }
        else:
            result = {
                'type': 'gif',
                'id': item['ID'],
                'gif_url': item['MediaUrl'],
                'gif_width': int(item['Width']),
                'gif_height': int(item['Height']),
                'thumb_url': item['Thumbnail']['MediaUrl']
            }
        results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(m, results)
