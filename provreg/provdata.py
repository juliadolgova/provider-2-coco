# -*- encoding: utf-8 -*-
from abc import ABCMeta, abstractmethod


# TODO Добавить промежуточный класс ProvDataFile
# TODO Добавить метод seek либо посмотреть как в генератор передавать стартовую итерацию
# TODO Определить get_records_count в потомках
class ProvData:
    __metaclass__ = ABCMeta

    def __init__(self):
        self._records_count = None

    def get_records_count(self):
        return self._records_count

    records_count = property(get_records_count, None, None, u'Количество записей либо None если количество не доступно')

    @abstractmethod
    def generate_accounts_decoded(self): pass
    """Вернуть словарь для импорта в кокос"""

    @abstractmethod
    def source_data_correct(self): pass
    """Сообщить корректные ли данные"""

    @abstractmethod
    def source_data_errors(self): pass
    """Вернуть ошибки в исходных данных"""
