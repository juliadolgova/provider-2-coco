# -*- encoding: utf-8 -*-
import logging
import os.path
from datetime import datetime

from settings import LOGS_ENCODING


def source_error_print(**kwargs):
    print 'Ошибка при преобразовании данных из файла {}'.format(kwargs['file'].encode(LOGS_ENCODING))
    print '#: {}'.format(kwargs['at'])
    print 'Запись: {}'.format(str(kwargs['record']).strip())
    print 'Exception: {}'.format(kwargs['exception'])
    print ''


def files_error_print(**kwargs):
    provdata = kwargs['provdata']
    _filename = provdata.filename
    if type(_filename) == unicode:
        _filename = _filename.encode(LOGS_ENCODING)
    print 'Ошибка при загрузке файла {}'.format(_filename)
    print 'Exception: {}'.format(kwargs['exception'])


def task_delete_error_print(**kwargs):
    task_id = kwargs['task_id']
    mnemo_coco = kwargs['mnemo_coco']
    print 'Ошибка при выполнении задания на удаление {}. Поставщик: {}'.format(task_id, mnemo_coco)
    exception = kwargs['exception']
    print 'Exception: {}, {}'.format(type(exception), exception)


def logger(path, name):
    level = int(logging.INFO)
    _date = datetime.now().strftime('%Y-%m-%d')
    logger_name = '{}_{}'.format(name, _date)
    _filename = '{}.log'.format(logger_name)
    if not os.path.isdir(path):
        os.makedirs(path)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    handler = logging.FileHandler(filename=os.path.join(path, _filename), encoding=None)
    handler.setFormatter(logging.Formatter(
        '%(levelname)s::%(asctime)s::%(module)s.%(funcName)s (%(lineno)d)::%(message)s'))
    logger.addHandler(handler)
    return logger
