import sqlite3
import urllib.request
import json
import urllib.parse
import csv

class DataTranslation(object):
    """
    Программа для автоматической подготовки файла, готового для импорта в программу изучения слов
    anki - http://ankisrs.net/
    Использование - подключить kindle к компьютеру, указать путь до файла vocab.db (обычно
    находится в kindle/system/vocabulary)

    ВАЖНО: после создания исходного файл, по умолчанию дата база на устройстве будет очищена -
    это сделано потому что нет возможности очистить словарь непосредственно с устройства (только
    по 1 карточке). Если не нужно стирать файл запускайте с параметром delete=False

    Получение ключа - https://tech.yandex.ru/keys/get/?service=trnsl
    """
    def __init__(self, delete=True):
        self.data = []
        self.key = ''
        self.delete = delete
        self.translate_data = []

    def get_data(self, way_to_db_file):
        conn = sqlite3.connect(way_to_db_file)
        cursor = conn.execute("SELECT id, name, address, salary  from COMPANY")
        print(cursor.fetchall())
        for row in cursor:
            self.data.append(row[3])
        conn.execute("DELETE FROM COMPANY")
        conn.execute("VACUUM")
        conn.commit()
        conn.close()

    def get_lang(self):
        url1 = 'https://translate.yandex.net/api/v1.5/tr.json/detect?' + \
               urllib.parse.urlencode({'text': self.data,
                                       'key': self.key})
        file = urllib.request.urlopen(url1).read()
        js = json.loads(file.decode('utf-8'))
        return js['lang']

    def make_translation(self):
        assert self.data, "Список файлов пуст, проверьте корректность пути к файлу"

        language = self.get_lang()
        url2 = 'https://translate.yandex.net/api/v1.5/tr.json/translate?' + \
               urllib.parse.urlencode({'text': self.data,
                                      'key': self.key,
                                      'lang': language+'-ru'})
        file = urllib.request.urlopen(url2).read()
        js = json.loads(file.decode('utf-8'))
        print(js)
        print(js['text'][0])

    def make_csv(self):
        with open("file_to_import.csv", "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerows([i for i in self.translate_data])



if __name__ == '__main__':
    c = DataTranslation()
    c.data = ['hi', 'привет']
    c.make_translation()
    c.translate_data = [['hi','приветfdg'],['bye','пока']]
    c.make_csv()
