# -*- encoding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from datetime import datetime


# TODO Переделать как класс-итератор
# noinspection PyTypeChecker
class ProvData:
    __metaclass__ = ABCMeta

    def __init__(self):
        # Функция-обработчик исключений при чтении/преобразовании записи
        # в источнике данных в generate_accounts_decoded()
        self.error_processor = None
        # исходный файл
        self._filename = None
        # количество ошибок при обработке файла
        self.error_count = 0

    def set_filename(self, filename):
        self._filename = filename
        self.error_count = 0

    def get_filename(self):
        return self._filename

    filename = property(get_filename, set_filename, None, u'Путь к исходному файлу')

    def get_records_count(self):
        return None

    records_count = property(
        get_records_count,
        None,
        None,
        u'Количество записей либо None если количество не доступно. \
        Не обязательно совпадает с количеством строк на выходе(?)'  # TODO определиться на этот счет
    )

    @abstractmethod
    def generate_accounts_decoded(self):
        """Возвращает словарь для импорта в кокос"""
        pass

    def generate_block_accounts(self, blocksize):
        i = 0
        accounts_list = []
        for item in self.generate_accounts_decoded():
            i += 1
            accounts_list.append(item)
            if i % blocksize == 0:
                yield accounts_list
                accounts_list = []
        if accounts_list:
            yield accounts_list

    @abstractmethod
    def source_data_correct(self):
        """Сообщает корректные ли данные"""
        pass

    @staticmethod
    def _default_dict():
        """Заполняет необязательные параметры"""
        return {
            'fine': None,
            'charge': None,
            'region': u'',
            'territory': u'',
            'pfxstreet': u''
        }

    def get_max_debt_date(self):
        max_debt_date = datetime(2000, 1, 1)
        for item in self.generate_accounts_decoded():
            if item['period'] > max_debt_date:
                max_debt_date = item['period']
        return max_debt_date
