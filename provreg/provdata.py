# -*- encoding: utf-8 -*-
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime

from srcutils import split_fio, array_pad


class ProvData:
    __metaclass__ = ABCMeta

    def __init__(self):
        # Обработчик исключений при чтении/преобразовании записи в источнике данных в generate_accounts_decoded()
        self.error_processor = None

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
        self._filename = filename
        # кодировка исходного файла
        self._coding = 'cp1251'
        # пример регулярного выражения, переопределить в наследнике при необходимости
        self._line_re = '(?P<abonent>.*);(?P<address>.*);(?P<account>.*);(?P<debt>.*);(?P<datefrom>.*);(?P<dateto>.*)'
        # формат датовых полей в исходном файле
        self._format_datetime = r'%d/%m/%Y'
        # дата, которую использовать, если в реестре нет даты. Тип datetime
        self.debt_date = None
        # разделитель дробной и целой части
        self.delimiter = '.'

    def set_filename(self, filename):
        self._filename = filename

    def get_filename(self):
        return self._filename

    filename = property(get_filename, set_filename, None, u'Путь к исходному файлу')

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
                raise IOError('No data specified')

        debt = dict_re.get('debt')
        if self.delimiter != '.':
            debt = debt.replace(self.delimiter, '.')
        dict_api['debt'] = float(debt) if debt else 0
        return dict_api

    @staticmethod
    def _get_header_param_value(source_lines, param_name):
        for line in source_lines:
            m = re.match(r"#%(ParamName)s\s(.*)(;.*)?" % {'ParamName': param_name}, line)
            if m:
                return m.group(1).strip()
        return None

    def generate_accounts_decoded(self):
        line_num = 0
        with open(self._filename, 'r') as f:
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
                        self.error_processor(
                            file=self._filename,
                            at=line_num,
                            record=line,
                            exception=exception_instance
                        )
                    else:
                        raise

    def source_data_correct(self):
        return True
