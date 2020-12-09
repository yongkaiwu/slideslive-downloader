import argparse
import json
import os
import time
from urllib.parse import urlparse

import requests


def extract_id_name(url):
    path = urlparse(url).path
    if '/' in path:
        _, event_id, event_name = path.split('/')
        return event_id, event_name
    else:
        print('id name extraction error!')
        exit(-1)


def http_get(url):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"}
    r = requests.get(url=url, headers=headers)

    if r.status_code == 200:
        return r
    else:
        print('HTTP request error!')
        exit(-1)


def fetch_json(event_id, folder):
    info_json_url = 'https://ben.slideslive.com/player/{}'.format(event_id)
    r = http_get(info_json_url)
    info_json = json.loads(r.text)

    slides_json_url = info_json['slides_json_url']
    r = http_get(slides_json_url)
    slides_json = json.loads(r.text)

    with open('{}/slides.json'.format(folder), 'w') as f:
        json.dump(slides_json, f, indent=4)

    return slides_json


def download_slides(slides_dict, args, event_id, folder):
    if args.slide_qualities in slides_dict['slide_qualities']:
        for i, slide in enumerate(slides_dict['slides']):
            name = slide['image']['name']
            url = 'https://d2ygwrecguqg66.cloudfront.net/data/presentations/{}/slides/{}/{}.jpg'.format(event_id,
                                                                                                        args.slide_qualities,
                                                                                                        name)
            r = http_get(url)

            with open('{}/{:04d}_{}_{}.jpg'.format(folder, i, name, args.slide_qualities), 'wb') as f:
                f.write(r.content)

            time.sleep(args.download_delay)

    else:
        print('slide_qualities error!')
        exit(-1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str)
    parser.add_argument('-q', '--slide_qualities', type=str, default='big')
    parser.add_argument('-d', '--download_delay', type=int, default=10)

    args = parser.parse_args()
    event_id, event_name = extract_id_name(args.url)

    folder = '{}_{}'.format(event_id, event_name)
    if not os.path.exists(folder):
        os.mkdir(folder)

    slides_json = fetch_json(event_id, folder)
    download_slides(slides_json, args, event_id, folder)
