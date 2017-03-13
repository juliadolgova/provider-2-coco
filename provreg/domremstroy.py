# -*- encoding: utf-8 -*-

from provdata import ProvDataText
from srcutils import array_pad


class Domremstroy(ProvDataText):
    def __init__(self, filename=''):
        ProvDataText.__init__(self, filename)
        # Код услуги
        self._service_code = '2834'

        # Пример строки для поставщика:
        # 006589;Ломов Леонид Георгиевич 1-я Малая 1а 12;Чита,1-я Малая,1а,12;456,86
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
            debt_re
        ])

    def _dict_re_to_dict_api(self, dict_re):
        dict_api = ProvDataText._dict_re_to_dict_api(self, dict_re)
        fio = array_pad(dict_re['abonent'].replace('.', ' ').split(), 3, '')[:3]
        dict_api['lastname'], dict_api['firstname'], dict_api['middlename'] = fio
        return dict_api
