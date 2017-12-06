import requests
import dateparser
from xml.etree import ElementTree


class RSS:

    def __init__(self, url):
        self.url = url
        self.name = None
        self.items = []

    def parse(self):
        try:
            rss_content = requests.get(self.url).content
        except Exception:
            return False

        tree = ElementTree.fromstring(rss_content)[0]

        self.name = tree.find('title').text

        for item in tree.findall('item'):
            item_object = {
                'title': item.find('title').text,
                'link': item.find('link').text,
                'description': item.find('description').text,
                'date': dateparser.parse(item.find('pubDate').text),
                'categories': []
            }

            for cat in item.findall('category'):
                item_object['categories'].append(cat.text)

            self.items.append(item_object)

    def get_items(self):
        return self.items

    def get_name(self):
        return self.name
