# kindle_to_anki
Программа для автоматической подготовки файла, готового для импорта в программу изучения слов
anki - http://ankisrs.net/
Использование - подключить kindle к компьютеру, указать путь до файла vocab.db (обычно
находится в kindle/system/vocabulary), указать api-ключ для перевода, нажать "Создать файл для импорта".

Так же присутствует возможность очистить базу данный слов на устройстве - это сделано потому что нет возможности очистить словарь непосредственно с устройства (только
по 1 карточке).

Перевести лучше, но медленнее? - этот параметр отвечает за то будут ли слова переводится все вместе через
сервис яндекс.переводчик или по одному через яндекс.словари, второй вариант значительно лучше, однако
занимает много времени ~150 секунд для 2000 слов. При этом слова, которые не были найдены в словаре будут найдены с использованием
переводчика.

Получение ключа для работы api переводчика - https://tech.yandex.ru/keys/get/?service=trnsl
Получение ключа для словаря - https://tech.yandex.ru/keys/get/?service=dict
