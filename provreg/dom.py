# -*- encoding: utf-8 -*-
import re

from provdata import ProvDataText


class Dom(ProvDataText):
    def __init__(self, filename='', service_code=''):
        ProvDataText.__init__(self, filename)
        # Код услуги
        self._service_code = service_code
        # Размер в байтах когда требуется проанализировать только начало файла (достаточное чтобы попали все заголовки)
        self.__bufferPreAnalyze = 3000
        # количество строк для предварительного анализа (достаточное чтобы попали все заголовки)
        self.__linesCountPreAnalyze = 100

        # Пример строки для поставщика:
        # Ипатов Роман Михайлович;ЧИТА,БОГОМЯГКОВА,65,62;9010747;;;;;01/11/2016;30/11/2016;31:0
        # Регулярки вспомогательные
        num_re = r'[-+]?[0-9]*[.,]?[0-9]+'
        # В регулярке предусмотрен год длинный и короткий,
        # но в обработке полученного значения (например _dict_re_to_dict_api) не предусмотрено
        date_re = r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)?\d\d'

        # Регулярки для сборки _line_re
        abonent_re = r'(?P<abonent>.*)'
        address_re = r'(?P<address>.*)'
        account_re = r'(?P<account>[a-z0-9A-Z]+)'
        debt_re = r'(?P<debt>(%(num_re)s)?)' % {'num_re': num_re}
        f5_re = r'(?P<f5>.*)'
        f6_re = r'(?P<f6>.*)'
        f7_re = r'(?P<f7>.*)'
        datefrom_re = r'(?P<datefrom>%(date_re)s)' % {'date_re': date_re}
        dateto_re = r'(?P<dateto>%(date_re)s)' % {'date_re': date_re}
        f10_re = r'(?P<f10>.*)'

        self._line_re = ';'.join([
            abonent_re,
            address_re,
            account_re,
            debt_re,
            f5_re,
            f6_re,
            f7_re,
            datefrom_re,
            dateto_re,
            f10_re
        ])

    def source_data_correct(self):
        with open(self._filename, 'r') as f:
            first_lines = f.readlines(self.__bufferPreAnalyze)[:self.__linesCountPreAnalyze]
            file_sum_header = float(self._get_header_param_value(first_lines, 'FILESUM'))

            f.seek(0)
            file_sum_records = 0
            for line in f:
                m = re.match(self._line_re, line)
                if m:
                    file_sum_records += float(m.group('debt')) if m.group('debt') else 0
        return round(file_sum_header - file_sum_records, 2) == 0

