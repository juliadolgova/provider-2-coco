# -*- encoding: utf-8 -*-
from datetime import datetime
import re

from provdata import ProvData
from srcutils import split_fio, process_source_exception


class Oblgaz(ProvData):
    def __init__(self, filename=''):
        ProvData.__init__(self)
        # исходный файл
        self._filename = filename
        # кодировка исходного файла
        self._coding = 'cp1251'
        # Внешняя услуга
        self._ext_service_code = '3149'
        # Размер в байтах когда требуется проанализировать только начало файла (достаточное чтобы попали все заголовки)
        self.__bufferPreAnalyze = 3000
        # количество строк для предварительного анализа (достаточное чтобы попали все заголовки)
        self.__linesCountPreAnalyze = 100
        self.__errors = []

        # Пример строки для облгаза:
        # АВДЕЕВА НАДЕЖДА АЛЕКСЕЕВНА;Кокуй,Комсомольская,16,18;0984;-153.83;;01/06/15;30/06/15
        # Регулярки вспомогательные
        num_re = r'[-+]?[0-9]*[.,]?[0-9]+'
        date_re = r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)?\d\d'

        # Регулярки для сборки __line_re
        abonent_re = r'(?P<abonent>.*)'
        address_re = r'(?P<address>.*)'
        account_re = r'(?P<account>[a-z0-9A-Z]+)'
        debt_re = r'(?P<debt>%(num_re)s)' % {'num_re': num_re}
        f5_re = r'(?P<f5>.*)'
        datefrom_re = r'(?P<datefrom>%(date_re)s)' % {'date_re': date_re}
        dateto_re = r'(?P<dateto>%(date_re)s)' % {'date_re': date_re}

        self.__line_re = ';'.join([abonent_re, address_re, account_re, debt_re, f5_re, datefrom_re, dateto_re])

    def set_filename(self, filename):
        self._filename = filename
        self.__errors = []

    def get_filename(self):
        return self._filename

    filename = property(get_filename, set_filename, None, u'Имя исходного файла')

    def _dict_re_to_dict_api(self, dict_re):
        dict_api = dict()
        dict_api['number'] = dict_re['account']
        dict_api['lastname'], dict_api['firstname'], dict_api['middlename'] = split_fio(dict_re['abonent'])
        splitted_address = dict_re['address'].strip().rsplit(',', 4)
        dict_api['city'], dict_api['street'], dict_api['house'], dict_api['flat'] = splitted_address
        dict_api['service'] = self._ext_service_code
        dict_api['period'] = datetime.strptime(dict_re['dateto'], r'%d/%m/%y')
        dict_api['debt'] = float(dict_re['debt'])
        dict_api['fine'] = None
        dict_api['charge'] = None
        dict_api['region'] = u''
        dict_api['territory'] = u''
        dict_api['pfxstreet'] = u''
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
                    m = re.match(self.__line_re, line)
                    if m:
                        yield self._dict_re_to_dict_api(m.groupdict())
                except Exception as exception_instance:
                    error_message = 'Error while processing line %d in file %s'
                    process_source_exception(error_message % (line_num, self._filename), exception_instance)

    def source_data_correct(self):
        with open(self._filename, 'r') as f:
            first_lines = f.readlines(self.__bufferPreAnalyze)[:self.__linesCountPreAnalyze]
            file_sum_header = float(self._get_header_param_value(first_lines, 'FILESUM'))

            f.seek(0)
            file_sum_records = 0
            for line in f:
                m = re.match(self.__line_re, line)
                if m:
                    file_sum_records += float(m.group('debt'))
        return round(file_sum_header - file_sum_records, 2) == 0

    def source_data_errors(self):
        return self.__errors
