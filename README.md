# kindle_to_anki
Программа для импорта словаря из kindle в формат пригодный для anki

Берет данные из sql дата файла на kindle, получает перевод слов на русский с помощью API Яндекс.Переводчик, затем создает .csv файл, который
anki принимает для импорта. Данные из таблицы со словами на устройстве при этом удаляются (чтобы не удалялись нужно запускать с параметром delete=False) - 
это сделано по причине того, что на самом устройстве нет возможности удались сразу все слова из словаря, только по одному.