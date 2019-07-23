# -*- coding: utf-8 -*-
import json
import requests
import sys
import re
import os
import time
from urllib import request
import urllib3

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


post_numbers = []  # массив с номерами тредов
post_text = []  # массив постов с ссылками внутри
dump = 'dump.json'  # имя дамп файла
TIMEOUT = 0.5  # таймаут проверки юрлов
stats = {
    'threads': None,
    'links': None
}

if sys.argv[1] != 'rewrite' and sys.argv[1] != 'use_argv':
    try:
        dump_list = open(dump, mode='r')  # попытка чтения файла дампа
        settings = json.load(dump_list)

    except:
        settings = {
        'max_thread': int(input('Не обнаружен файл дампа настроек, введите максимальное количество тредов> ')),
        'board': str(input('Введите доску> ')),
        'filename': str(input('Имя стандартного выходного файла> '))
        }

        try:
            dump_list = open(dump, mode='w')
            json.dump(settings, dump_list)
            dump_list.close

        except:
            print('Ошибка дампа аргументов')
            exit(0)

    else:
        print('Настройки успешно загружены!')


# дамп переменных
if sys.argv[1] == 'rewrite':
    settings = {
    'max_thread': int(input('Введен аргумент резагрузки настроек. \nвведите максимальное количество тредов> ')),
    'board': str(input('Введите доску> ')),
    'filename': str(input('Имя стандартного выходного файла> '))
    }

    try:
        dump_list = open(dump, mode='w')
        json.dump(settings, dump_list)
        dump_list.close()

    except:
        print('Ошибка дампа аргументов!')
        exit(0)

    else:
        print('Настройки успешно перезаписаны!')

elif sys.argv[1] == 'use_argv':
    print('Использование аргументов для настроек')
    if sys.argv[4]:
        settings = {
            'max_thread': int(sys.argv[2]),
            'board': sys.argv[3],
            'filename': sys.argv[4]
        }
        try:
            dump_list = open(dump, mode='w')
            json.dump(settings, dump_list)
            dump_list.close()
        except:
            print('Ошибка дампа аргументов')
            exit(0)

else:
    pass


def dump_json(renamed_obj, obj):
    try:
        dump_list = open(dump, mode='w')
        settings[renamed_obj] = obj
        json.dump(settings[renamed_obj], dump_list)
    except:
        print('Ошибка дампа новых настроек')
        exit(0)
    else:
        print('Дамп создан успешно')
    finally:
        dump_list.close()


cls()
file = open(settings['filename'], mode='w', encoding='UTF-8')  # открытие/создание выходного файла

# загрузка каталога тредов
try:
    load_str = json.loads(requests.get(''.join(["https://5.61.239.35/", settings['board'], "/catalog.json"]), verify=False).text)
except:
    print('Каталог тредов не был загружен!')
    try:
        load_str = json.loads(requests.get(''.join(["https://5.61.239.35/", settings['board'], "/catalog.json"]), verify=False).text)
    except:
        print('Повторная попытка загрузить каталок тредов не удалась! Выключение...')
        exit(0)
    else:
        print('Повторая попытка загрузки удалась!')
else:
    print('Каталог загружен!')

# загрузка в список номера тредов от 0 до переменной max_thread
for s in range(0, settings['max_thread']):
    try:
        post_numbers.append(load_str['threads'][s]['num'])
    except:
        print('Достигнуто максимально количество тредов на данной доске')
        if str(input('Перезаписать максимальное количество постов? Y/N> ')) == 'Y' or 'y' or 'yes' or 'да' or 'д':
            try:
                obj = len(post_numbers)
                dump_json('max_thread', obj)
            except:
                print("Ошибка дампа новых настроек")
                exit()
        else:
            print('Отмена перезаписи настроек (Может вызвать проблемы!)')
        break
    else:
        print(('Парсинг постов {0}%').format(int((len(post_numbers) / settings['max_thread']) * 100)))


cls()
for i in range(0, settings['max_thread']):
    stats['threads'] = i
    try:
        answ = json.loads(requests.get(''.join(["https://5.61.239.35/", settings['board'], "/res/", post_numbers[i], '.json']), verify=False, timeout=(TIMEOUT+1)).text)
    except:
        print('Ошибка загрузки страницы, возможно нету интернетов')
        try:
            answ = json.loads(requests.get(''.join(["https://5.61.239.35/", settings['board'], "/res/", post_numbers[i], '.json']),verify=False, timeout=(TIMEOUT+5)).text)
        except:
            print('Повторная попытка загрузки не удалась, выход...')
            continue
        else:
            print('Повторная попытка загрузки треда удалась!')
    else:
        print('Тред успешно загружен!')

        # начало парсинга в тредах
    for j in range(0, 10000):

        try:
            text = answ['threads'][0]['posts'][j]['comment']
        except:
            break
        else:
            # реплейс мусора и замена разметки
            text = text.replace('&#47', '/')
            text = text.replace(';', '')
            text = text.replace('<span class="spoiler">', ' ')
            text = text.replace('</span>', ' ')
            text = text.replace('?!<br><a href="', ' ')
            text = text.replace('" target="_blank">', ' ')
            text = text.replace('</a>', ' ')
            text = text.replace('<br>', '\n')
            text = text.replace('<a href="', '')
            text = text.replace('&quot', ' | ')
            text = text.replace('<em>', ' | ')
            text = text.replace('</em>', ' | ')
            text = text.replace('<strong>', ' >')
            text = text.replace('</strong>', '< ')
            text = text.replace('<span class="s">', ' ')
            text = text.replace('&#92', '||')
            text = text.replace('<span class="unkfunc">&gt', ' ')

            # список найденного мусора дял удаления
            shit_rm = []
            minus2 = re.findall(r'/[\S]+/res/[\d]+.html#[\d]+[\"][\s]class[=][\"]', text)
            minus3 = re.findall(r'post-reply-link" data-thread="[\d]+" data-num="[\d]+">>>[\d]+', text)
            minus1 = re.findall(r'" target="_blank" rel="nofollow noopener noreferrer">[\w]+:\S\S[\S]+', text)
            shit_rm = minus1 + minus2 + minus3  # добавление 3 списков в один

            # реплейс мусора
            for shit in shit_rm:
                text = text.replace(shit, '')

            # поиск юрлов
            finded_links_https = re.findall(r'https://[\w]+[.][\w]+', text)
            finded_links_normal = re.findall(r'www.[\w]+[.][\w]+', text) + re.findall(r'[\w]+[.][\S]+', text)

            stats['links'] = 0  # счетчик проверенных юрлов
            success = False  # переменная наличия юрла
            # проверка юрлов формата https://zalupa.ru
            for f in finded_links_https:
                if success:
                    break
                cls()
                print("Проверено тредов {0} из {1}".format(stats['threads']+1, settings['max_thread']))
                print('Проверено цельных юрлов {0}, осталось {1}'.format(stats['links'], len(finded_links_https)))
                stats['links'] += 1
                try:
                    trash = requests.get(f, verify=False, timeout=TIMEOUT)
                except:
                    finded_links_https.remove(f)
                else:
                    success = True
                    break
            # проверка юрлов формата zalupa.ru и www.zalupa.ru
            stats['links'] = 0
            for y in finded_links_normal:
                cls()
                print("Проверено тредов {0} из {1}".format(stats['threads']+1, settings['max_thread']))
                print('Проверено нецельных юрлов {0}, осталось {1}'.format(stats['links'], len(finded_links_normal)))
                stats['links'] += 1

                if success:
                    break
                try:
                    trash = requests.get(''.join(["https://", y]), verify=False, timeout=TIMEOUT)
                except:
                    finded_links_normal.remove(y)
                else:
                    success = True
                    break
            # добавление поста в список, если найден рабочий юрл
            if success:
                post_text.append(text)

    cls()
    print("Проверено тредов {0} из {1}".format(stats['threads']+1, settings['max_thread']))


for z in post_text:
    file.write('\n\n\n=================================NEW POST==============================================\n' + z)
file.close()
print('\n\n' + '==============================================' + 'Парсинг успешно завершен!' + '==============================================\n')

try:
    dump_list = open(dump, mode='w')
    json.dump(settings, dump_list)
    dump_list.close()
    print('Настройки сохранены!')
except:
    print('Ошибка дампа аргументов')
    exit(0)


