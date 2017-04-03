# -*- encoding: utf-8 -*-
import re
from datetime import datetime

from provreg import ProvDataExcel


class Avangard(ProvDataExcel):
    def __init__(self, filename=''):
        ProvDataExcel.__init__(self, filename)
        self.first_line = 1
        self._service_code = '13203'
        self.date_re = r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)?\d\d'
        self._format_datetime = r'%d.%m.%Y'

    def _row_to_dict_api(self, row):
        dict_api = ProvDataExcel._row_to_dict_api(self, row)
        dict_api['number'] = row[1].value
        dict_api['lastname'] = row[2].value
        dict_api['firstname'] = row[3].value
        dict_api['middlename'] = row[4].value
        dict_api['city'] = row[7].value
        dict_api['street'] = row[9].value
        dict_api['house'] = row[10].value
        dict_api['flat'] = row[11].value

        debt_date = re.search(self.date_re, row[12].value).group(0)
        dict_api['period'] = datetime.strptime(debt_date, self._format_datetime)

        dict_api['service'] = self._service_code
        dict_api['debt'] = float(row[13].value) if row[13].value else 0

        return dict_api

