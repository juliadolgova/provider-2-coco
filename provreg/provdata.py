# -*- encoding: utf-8 -*-
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime

from srcutils import split_fio, process_source_exception


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

    @staticmethod
    def _default_dict():
        """Заполняем необязательные параметры"""
        return {
            'fine': None,
            'charge': None,
            'region': u'',
            'territory': u'',
            'pfxstreet': u''
        }


class ProvDataText(ProvData):
    """
    класс - поддержка текстового реестра имеющего заголовочные строки в формате
    # Параметр: Значение параметра
    Не делает проверку данных на корректность
    Cтроки начинающиеся с # - pfujkjdjxyst kb,j rj
    """
    def __init__(self, filename=''):
        ProvData.__init__(self)
        # код услуги, определить в наследнике
        self._service_code = ''
        # исходный файл
        self._filename = filename
        # кодировка исходного файла
        self._coding = 'cp1251'
        self.__errors = []
        # пример регулярного выражения, переопределить в наследнике при необходимости
        self._line_re = '(?P<abonent>.*);(?P<address>.*);(?P<account>.*);(?P<debt>.*);(?P<datefrom>.*);(?P<dateto>.*)'
        self._format_datetime = r'%d/%m/%Y'

    def set_filename(self, filename):
        self._filename = filename
        self.__errors = []

    def get_filename(self):
        return self._filename

    filename = property(get_filename, set_filename, None, u'Путь к исходному файлу')

    def _dict_re_to_dict_api(self, dict_re):
        dict_api = self._default_dict()
        dict_api['number'] = dict_re['account']
        dict_api['lastname'], dict_api['firstname'], dict_api['middlename'] = split_fio(dict_re['abonent'])
        splitted_address = dict_re['address'].strip().rsplit(',', 4)
        dict_api['city'], dict_api['street'], dict_api['house'], dict_api['flat'] = splitted_address
        dict_api['service'] = self._service_code
        dict_api['period'] = datetime.strptime(dict_re['dateto'], self._format_datetime)
        dict_api['debt'] = float(dict_re['debt']) if dict_re['debt'] else 0
        return dict_api

    @staticmethod
    def _get_header_param_value(source_lines, param_name):
        for line in source_lines:
            m = re.match(r"#%(ParamName)s\s(.*)(;.*)?" % {'ParamName': param_name}, line)
            if m:
                return m.group(1).strip()
        return None

    def generate_accounts_decoded(self):
        # TODO Заполнить __errors
        line_num = 0
        with open(self._filename, 'r') as f:
            for line in f:
                line_num += 1
                try:
                    line = line.decode(self._coding)
                    if line.startswith("#"):
                        continue
                    m = re.match(self._line_re, line)
                    if m:
                        yield self._dict_re_to_dict_api(m.groupdict())
                except Exception as exception_instance:
                    error_message = 'Error while processing line %d in file %s'
                    process_source_exception(error_message % (line_num, self._filename), exception_instance)

    def source_data_correct(self):
        return True

    def source_data_errors(self):
        return self.__errors
