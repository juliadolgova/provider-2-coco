# -*- encoding: utf-8 -*-
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime

import xlrd

from srcutils import split_fio, array_pad


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


class ProvDataText(ProvData):
    """
    класс - поддержка текстового реестра имеющего заголовочные строки в формате
    # Параметр: Значение параметра
    Строки начинающиеся с # - заголовочные либо коментарии
    """
    def __init__(self, filename=''):
        ProvData.__init__(self)
        # код услуги, определить в наследнике
        self._service_code = ''
        # исходный файл
        self.filename = filename
        # кодировка исходного файла
        self._coding = 'cp1251'
        # пример регулярного выражения, переопределить в наследнике при необходимости
        self._line_re = '(?P<abonent>.*);(?P<address>.*);(?P<account>.*);(?P<debt>.*);(?P<datefrom>.*);(?P<dateto>.*)'
        # формат датовых полей в исходном файле
        self._format_datetime = r'%d/%m/%Y'

        # Размер в байтах когда требуется проанализировать только начало файла (достаточное чтобы попали все заголовки)
        self._bufferPreAnalyze = 3000
        # количество строк для предварительного анализа (достаточное чтобы попали все заголовки)
        self._linesCountPreAnalyze = 100

        # дата, которую использовать, если в реестре нет даты. Тип datetime
        self.debt_date = None
        # разделитель дробной и целой части
        self.delimiter = '.'

    def _dict_re_to_dict_api(self, dict_re):
        dict_api = self._default_dict()
        dict_api['number'] = dict_re.get('account')
        dict_api['lastname'], dict_api['firstname'], dict_api['middlename'] = split_fio(dict_re.get('abonent'))

        splitted_address = array_pad(dict_re.get('address').strip().rsplit(',', 4), 4, '')
        dict_api['city'], dict_api['street'], dict_api['house'], dict_api['flat'] = splitted_address

        dict_api['service'] = self._service_code

        dateto = dict_re.get('dateto')
        if dateto:
            dict_api['period'] = datetime.strptime(dateto, self._format_datetime)
        else:
            if self.debt_date:
                dict_api['period'] = self.debt_date
            else:
                raise IOError('No date specified')

        debt = dict_re.get('debt')
        if self.delimiter != '.':
            debt = debt.replace(self.delimiter, '.')
        dict_api['debt'] = float(debt) if debt else 0
        return dict_api

    def _get_header_param_value(self, param_name):
        with open(self.filename, 'r') as f:
            source_lines = f.readlines(self._bufferPreAnalyze)[:self._linesCountPreAnalyze]

        for line in source_lines:
            m = re.match(r"#%(ParamName)s\s(.*)(;.*)?" % {'ParamName': param_name}, line)
            if m:
                return m.group(1).strip()
        return None

    def generate_accounts_decoded(self):
        self.error_count = 0
        line_num = 0

        with open(self.filename, 'r') as f:
            for line in f:
                line_num += 1
                try:
                    line_decoded = line.decode(self._coding)
                    if line_decoded.startswith("#"):
                        continue
                    m = re.match(self._line_re, line_decoded)
                    if m:
                        yield self._dict_re_to_dict_api(m.groupdict())
                except Exception as exception_instance:
                    if self.error_processor:
                        self.error_count += 1
                        self.error_processor(
                            file=self.filename,
                            at=line_num,
                            record=line,
                            exception=exception_instance
                        )
                    else:
                        raise

    def source_data_correct(self):
        return True


class ProvDataExcel(ProvData):

    def __init__(self, filename=''):
        ProvData.__init__(self)
        # код услуги, определить в наследнике
        self._service_code = ''
        # исходный файл
        self.filename = filename
        # дата, которую использовать, если в реестре нет даты. Тип datetime
        self.debt_date = None
        # номер первой строки с данными
        self.first_line = 0

    def _row_to_dict_api(self, row):
        dict_api = self._default_dict()
        return dict_api

    def generate_accounts_decoded(self):
        self.error_count = 0
        workbook = xlrd.open_workbook(self.filename)
        sheet = workbook.sheet_by_index(0)

        for row_index in xrange(self.first_line, sheet.nrows):
            row = sheet.row(row_index)
            try:
                yield self._row_to_dict_api(row)
            except Exception as exception_instance:
                if self.error_processor:
                    self.error_count += 1
                    self.error_processor(
                        file=self.filename,
                        at=row_index,
                        record=row,
                        exception=exception_instance
                    )
                else:
                    raise

    def source_data_correct(self):
        return True
