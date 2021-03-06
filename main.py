import sqlite3
import urllib.request
import json
import urllib.parse
import csv
import tkinter
from tkinter import messagebox

root = tkinter.Tk()


class DataTranslation(tkinter.Frame):
    """
    Программа для автоматической подготовки файла, готового для импорта в программу изучения слов
    anki - http://ankisrs.net/
    Использование - подключить kindle к компьютеру, указать путь до файла vocab.db (обычно
    находится в kindle/system/vocabulary)

    Так же присутствует возможность очистить базу данный слов на устройстве - это сделано потому что нет возможности очистить словарь непосредственно с устройства (только
    по 1 карточке).

    Перевести лучше, но медленнее? - этот параметр отвечает за то будут ли слова переводится все вместе через
    сервис яндекс.переводчик или по одному через яндекс.словари, второй вариант значительно лучше, однако
    занимает много времени ~150 секунд для 2000 слов.

    Получение ключа для работы api переводчика - https://tech.yandex.ru/keys/get/?service=trnsl
    Получение ключа для словаря - https://tech.yandex.ru/keys/get/?service=dict
    """
    def __init__(self, master):
        super(DataTranslation, self).__init__(master)
        self.pack()
        self.delete = tkinter.IntVar()
        self.speed = tkinter.IntVar()
        self.create_widgets()
        self.result = []

    def create_widgets(self):

        tkinter.Label(self, text='Импорт словаря из kindle в anki', font=("Helvetica", 22)).pack()
        tkinter.Label(self, text='В поле ниже укажите путь до файла vocab.db', font=("Helvetica", 18)).pack()
        tkinter.Label(self, text='по умолчанию /kindle/system/vocabulary/vocab.db', font=("Helvetica", 17)).pack()
        self.path = tkinter.Entry(self, font=("Helvetica", 20))
        self.path.pack()


        tkinter.Checkbutton(self, font=("Helvetica", 20), text='Перевести лучше, но медленнее',
                            variable=self.speed, onvalue = 1, offvalue = 0).pack()

        tkinter.Label(self, text='Ключ для переводчика:', font=("Helvetica", 18)).pack()
        self.get_key_trans = tkinter.Entry(self, font=("Helvetica", 20))
        self.get_key_trans.pack()

        tkinter.Label(self, text='Ключ для словаря:', font=("Helvetica", 18)).pack()
        self.get_key_vocab = tkinter.Entry(self, font=("Helvetica", 20))
        self.get_key_vocab.pack()

        self.bttn = tkinter.Button(self, text='Создать файл для импорта', command=self.main, font=("Helvetica", 20))
        self.bttn.pack()

        self.bttn = tkinter.Button(self, text='Очистить словарь на устройстве',
                                   command=self.clear_vocabulary, font=("Helvetica", 20))
        self.bttn.pack()

    @staticmethod
    def message_box(info):
        """
        Функция отвечает за вывод всплывающего окна, сообщающего о различных ошибках
        """
        messagebox.showinfo('Сообщение', info)

    def get_data(self, path):
        """
        Функция используется для извлечения данных из базы данных на kindle
        по указаному пользователем пути, или по пути по умолчанию, если поле
        пользователь не заполнил
        :param path: str
        """
        try:
            conn = sqlite3.connect(path)
            cursor = conn.execute("SELECT stem from WORDS")
            data = [word for word in set(row[0] for row in cursor)]
        except sqlite3.OperationalError:
            self.message_box('Не удалось извлечь данные, проверьте путь')
        finally:
            conn.close()

        assert data, self.message_box("Список данных пуст, проверьте корректность пути к файлу")
        return data

    def clear_vocabulary(self):
        """
        Функция выполняет очистку таблицы со словами в базе данных kindle
        """
        path = self.path.get() if self.path.get() else '/kindle/system/vocabulary/vocab.db'
        conn = sqlite3.connect(path)
        conn.execute("DELETE FROM WORDS")
        conn.execute("VACUUM")
        conn.commit()
        self.message_box("Очистка словаря завершена")

    def get_lang(self, data):
        """
        Функция используется для получения исходного языка слов в словаре,
        используется в функциях make_translation_translator/make_translation_vocabulary
        при передаче запроса на перевод
        :param data: list
        """
        url1 = 'https://translate.yandex.net/api/v1.5/tr.json/detect?' + \
               urllib.parse.urlencode({'text': data,
                                       'key': self.get_key_trans.get()})
        file = urllib.request.urlopen(url1).read()
        js = json.loads(file.decode('utf-8'))
        return js['lang']

    def make_translation_translator(self, data, language):
        """
        Функция использует api яндекс.переводчика для получения перевода
        слов извлеченных из базы данных, запрос одновременно обрабатывает 500 слов
        из-за ограничений api (10000 символов за раз).

        :param data: list
        :param language: str
        :return: None
        """
        translated_data = []

        for i in range(0, len(data), 500):
            request = 'https://translate.yandex.net/api/v1.5/tr.json/translate?' + \
                      urllib.parse.urlencode({'text': data[i:i+500],
                                              'key': self.get_key_trans.get(),
                                              'lang': language+'-ru'})
            result = urllib.request.urlopen(request).read()
            js = json.loads(result.decode('utf-8'))

            translated_data.extend([i.strip("' ") for i in js['text'][0][1:-2].split(',')])

        self.result.extend(zip(data, translated_data))

    def make_translation_vocabulary(self, data, language):
        """
        Функция использует api яндекс.словаря для получения перевода
        слов извлеченных из базы данных, по каждому слову посылается отдельный запрос -
        это и сказывается на времени работы программы в данном режиме (это ограничение
        накладывает api).

        :param data: list
        :param language: str
        :return: None
        """
        not_translated = []
        for i in data:
            try:
                request = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?' + \
                    urllib.parse.urlencode({'text': i,
                                            'key': self.get_key_vocab.get(),
                                            'lang': language+'-ru'})
                result = urllib.request.urlopen(request).read()
                js = json.loads(result.decode('utf-8'))
                self.result.append([i, js['def'][0]['tr'][0]['text']])
            except IndexError:
                not_translated.append(i)
        if not_translated:
            self.make_translation_translator(not_translated, language)

    def make_csv(self):
        """
        Функция формирует на основе списка из списков вида [слово,перевод] файл пригодный
        для импорта в программу anki
        :return: None
        """
        if self.result:
            with open("file_to_import.csv", "w", newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                writer.writerows(self.result)

            tkinter.Label(self, text='Файл создан', font=("Helvetica", 22)).pack()
        else:
            self.message_box("Результирующий файл пуст, проверьте корректность пути к файлу")

    def main(self):
        """
        Основная фукнция приложения, запускает процесс извлечения и перевода слов
        """
        path = self.path.get() if self.path.get() else '/kindle/system/vocabulary/vocab.db'
        data = self.get_data(path)
        try:
            language = self.get_lang(data[:10])
            if self.speed.get():
                self.make_translation_vocabulary(data, language)
            else:
                self.make_translation_translator(data, language)
            self.make_csv()
        except urllib.error.HTTPError:
            self.message_box("Произошла ошибка с работой api, проверьте валидность ключей")
        self.result.clear()


if __name__ == '__main__':
    root.geometry('600x400')
    app = DataTranslation(root)
    root.mainloop()
