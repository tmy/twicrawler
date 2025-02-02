#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import json
import re


class Instagram:
    def __init__(self, url):
        self.url = url

    def _get_json_data(self):

        res = requests.get(self.url)
        html = BeautifulSoup(res.content, 'html.parser')

        pattern = re.compile('window._sharedData = ({.*?});')
        script = html.find("script", text=pattern)
        data = pattern.search(script.text).group(1)
        json_user_data = json.loads(data)

        return json_user_data

    def get_media_urls(self):
        json_data = self._get_json_data()

        if "entry_data" not in json_data:
            return []
        if "PostPage" not in json_data['entry_data']:
            return []

        media_list = []
        for page in json_data['entry_data']['PostPage']:
            if "graphql" not in page:
                continue
            if "shortcode_media" not in page['graphql']:
                continue
            shortcode_media = page['graphql']['shortcode_media']
            if "edge_sidecar_to_children" not in shortcode_media:
                if "is_video" in shortcode_media and shortcode_media['is_video'] and "video_url" in shortcode_media:
                    media_list.append(shortcode_media['video_url'])
                    continue
                if "display_url" in shortcode_media:
                    media_list.append(shortcode_media['display_url'])
                    continue

            if "edges" not in shortcode_media['edge_sidecar_to_children']:
                continue

            for media in shortcode_media['edge_sidecar_to_children']['edges']:
                if "node" not in media:
                    continue
                if "is_video" in media['node'] and media['node']['is_video'] and "video_url" in media['node']:
                    media_list.append(media['node']['video_url'])
                elif "display_url" in media['node']:
                    media_list.append(media['node']['display_url'])

        return media_list


if __name__ == '__main__':
    insta = Instagram("https://www.instagram.com/p/B3IWnLkBD4M/")
    print(insta.get_media_urls())
