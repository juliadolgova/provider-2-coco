# -*- encoding: utf-8 -*-
import re

from provdata import ProvDataText


class Oblgaz(ProvDataText):
    def __init__(self, filename=''):
        ProvDataText.__init__(self, filename)
        # Внешняя услуга
        self._service_code = '3149'
        self._format_datetime = r'%d/%m/%y'

        # Пример строки для облгаза:
        # АВДЕЕВА НАДЕЖДА АЛЕКСЕЕВНА;Кокуй,Комсомольская,16,18;0984;-153.83;;01/06/15;30/06/15
        # Регулярки вспомогательные
        num_re = r'[-+]?[0-9]*[.,]?[0-9]+'
        date_re = r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)?\d\d'

        # Регулярки для сборки _line_re
        abonent_re = r'(?P<abonent>.*)'
        address_re = r'(?P<address>.*)'
        account_re = r'(?P<account>[a-z0-9A-Z]+)'
        debt_re = r'(?P<debt>%(num_re)s)' % {'num_re': num_re}
        f5_re = r'(?P<f5>.*)'
        datefrom_re = r'(?P<datefrom>%(date_re)s)' % {'date_re': date_re}
        dateto_re = r'(?P<dateto>%(date_re)s)' % {'date_re': date_re}

        self._line_re = ';'.join([abonent_re, address_re, account_re, debt_re, f5_re, datefrom_re, dateto_re])

    def source_data_correct(self):
        file_sum_header = float(self._get_header_param_value('FILESUM'))

        with open(self._filename, 'r') as f:
            file_sum_records = 0
            for line in f:
                m = re.match(self._line_re, line)
                if m:
                    file_sum_records += float(m.group('debt'))
        return round(file_sum_header - file_sum_records, 2) == 0
