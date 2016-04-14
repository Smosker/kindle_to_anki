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

    ВАЖНО: после создания исходного файл, по умолчанию дата база на устройстве будет очищена -
    это сделано потому что нет возможности очистить словарь непосредственно с устройства (только
    по 1 карточке). Если не нужно стирать файл запускайте с параметром delete=False

    Получение ключа - https://tech.yandex.ru/keys/get/?service=trnsl
    """
    def __init__(self, master):
        super(DataTranslation, self).__init__(master)
        self.pack()
        self.data = []
        self.key = ''
        self.delete = tkinter.IntVar()
        self.translated_data = []
        self.create_widgets()

    def create_widgets(self):

        tkinter.Label(self, text='Импорт словаря из kindle в anki', font=("Helvetica", 22)).pack()
        tkinter.Label(self, text='В поле ниже укажите путь до файла vocab.db:', font=("Helvetica", 18)).pack()
        self.path = tkinter.Entry(self, font=("Helvetica", 20))
        self.path.pack()
        tkinter.Checkbutton(self, font=("Helvetica", 20), text='Очистить словарь?', variable=self.delete,onvalue = 1, offvalue = 0).pack()
        tkinter.Label(self, text='Ключ для переводчика:', font=("Helvetica", 18)).pack()
        self.get_key = tkinter.Entry(self, font=("Helvetica", 20))
        self.get_key.pack()
        self.bttn = tkinter.Button(self, text='Создать файл для импорта', command=self.main, font=("Helvetica", 20))
        self.bttn.pack()

    def message_box(self,info):
        messagebox.showinfo('Ошибка',info)

    def get_data(self):
        try:
            conn = sqlite3.connect(self.path.get())
            cursor = conn.execute("SELECT id, name, address, salary  from COMPANY")
        except sqlite3.OperationalError:
            self.message_box('Не удалось извлечь данные, проверьте путь')


        print(cursor.fetchall())

        for row in cursor:
            self.data.append(row[3])
        if self.delete.get():
            print('deleting')
            conn.execute("DELETE FROM COMPANY")
            conn.execute("VACUUM")
            conn.commit()
        conn.close()

    def get_lang(self, data):
        url1 = 'https://translate.yandex.net/api/v1.5/tr.json/detect?' + \
               urllib.parse.urlencode({'text': data,
                                       'key': self.key})
        file = urllib.request.urlopen(url1).read()
        js = json.loads(file.decode('utf-8'))
        return js['lang']

    def make_translation(self):
        assert self.data, self.message_box("Список файлов пуст, проверьте корректность пути к файлу")
        language = self.get_lang(self.data)
        url2 = 'https://translate.yandex.net/api/v1.5/tr.json/translate?' + \
               urllib.parse.urlencode({'text': self.data,
                                       'key': self.key,
                                       'lang': language+'-ru'})
        file = urllib.request.urlopen(url2).read()
        js = json.loads(file.decode('utf-8'))

        self.translated_data.append(js['text'][0])
        print(js)
        print(js['text'][0])
        'Нужно в духе ["hi","привет"],["bye","пока"]'

    def make_csv(self):
        with open("file_to_import.csv", "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerows([i for i in self.translated_data])

        tkinter.Label(self, text='Файл создан', font=("Helvetica", 22)).pack()

    def main(self):
        self.get_data()
        self.key = self.get_key.get()
        self.make_translation()

        print(self.delete.get())
        print(self.path.get())


if __name__ == '__main__':
    root.geometry('600x260')
    app = DataTranslation(root)
    root.mainloop()
