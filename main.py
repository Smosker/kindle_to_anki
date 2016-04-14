import sqlite3
import urllib.request, json, urllib.parse

class DataTranslation(object):
    """
    Получение ключа - https://tech.yandex.ru/keys/get/?service=trnsl
    """
    def __init__(self):
        self.data = []
        self.key = ''

    def get_data(self, way_to_db_file):
        conn = sqlite3.connect(way_to_db_file)
        cursor = conn.execute("SELECT id, name, address, salary  from COMPANY")
        for row in cursor:
            self.data.append(row[3])

    def get_lang(self):
        url1 = 'https://translate.yandex.net/api/v1.5/tr.json/detect?'+\
               urllib.parse.urlencode({'text': self.data,
                                       'key': self.key})
        file = urllib.request.urlopen(url1).read()
        js = json.loads(file.decode('utf-8'))
        return js['lang']

    def make_translation(self):
        language = self.get_lang(self.data)
        if self.data:
            url2 = 'https://translate.yandex.net/api/v1.5/tr.json/translate?'+\
               urllib.parse.urlencode({'text': self.data,
                                       'key': self.key,
                                       'lang': language+'-ru'})
            file = urllib.request.urlopen(url2).read()
            js = json.loads(file.decode('utf-8'))
            print(js)
            print(js['text'][0])



