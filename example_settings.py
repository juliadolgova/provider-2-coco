# -*- coding: utf-8 -*-
# Переименуйте этот файл в settings.py. Укажите свои настройки
import os.path


WORK_COCONUT_SETTINGS = {
    'uri': 'http://client-coconut.ros-billing.ru',
    'dir_keyring': os.path.join(os.path.dirname(__file__), 'keyring'),
    'skey': 'FAD5BF8D5508C50993EA6B32344A74CB15F4DE94',
    'key':  'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'pswd': 'XXX'
}

TEST_COCONUT_SETTINGS = {
    'uri': 'http://cdev2-coconut.ros-billing.ru',
    'dir_keyring': os.path.join(os.path.dirname(__file__), 'keyring'),
    'skey': 'FAD5BF8D5508C50993EA6B32344A74CB15F4DE94',
    'key':  'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'pswd': 'XXX'
}

# Путь к папке, содержащий реестры поставщиков.
# Реестры поставщиков должны быть рассортированы по подпапкам.
# Названия подпапок = коды в кокосе
REG_PATH = u'x:\МКС\#registries\provider'

# MySQL настройки для подключения к базе tuk
TUK_DB = {
    'host': "127.0.0.1",
    'user': "root",
    'passwd': "XXXXX",
    'db': "tuk",
    'charset': 'utf8',
}

TUK_ENCODING = 'utf-8'

LOG_PATH = r'd:\LOGS\prov2coco'

LOGS_ENCODING = 'cp1251'

# Критическое количество ошибок при обработке файла при котором не создавать задание на удаление балансов
# CRITICAL_ERROR_COUNT = 100
CRITICAL_ERROR_COUNT = 5 if __debug__ else 100
