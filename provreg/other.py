# -*- encoding: utf-8 -*-

from oblgaz import Oblgaz
from provdata import ProvDataText


# TODO Переделать: наследовать от облгаза неправильно. В данном случае лучше повториться
class Lider(Oblgaz):
    def __init__(self, filename=''):
        Oblgaz.__init__(self, filename=filename)
        self._format_datetime = r'%d/%m/%y'
        self._service_code = self._get_header_param_value('SERVICE')


class Region(ProvDataText):
    def __init__(self, filename='', service_code=''):
        ProvDataText.__init__(self, filename)
        # Код услуги
        self._service_code = service_code
        self.delimiter = ','

        # Пример строки для поставщика:
        # 109100028;Выскубов Михаил Сергеевич;Чита,славянская,10 А,28;16443,36;
        # Регулярки вспомогательные
        num_re = r'[-+]?[0-9]*[.,]?[0-9]+'

        # Регулярки для сборки _line_re
        abonent_re = r'(?P<abonent>.*)'
        address_re = r'(?P<address>.*)'
        account_re = r'(?P<account>[a-z0-9A-Z]+)'
        debt_re = r'(?P<debt>(%(num_re)s)?)' % {'num_re': num_re}

        self._line_re = ';'.join([
            account_re,
            abonent_re,
            address_re,
            debt_re,
            ''
        ])
