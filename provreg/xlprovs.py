# -*- encoding: utf-8 -*-
import re
from datetime import datetime

import xlrd

from provreg import ProvData
from provreg.srcutils import value_to_str


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


class Avangard(ProvDataExcel):
    def __init__(self, filename=''):
        ProvDataExcel.__init__(self, filename)
        self.first_line = 1
        self._service_code = '13203'
        self.date_re = r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)?\d\d'
        self._format_datetime = r'%d.%m.%Y'

    def _row_to_dict_api(self, row):
        dict_api = ProvDataExcel._row_to_dict_api(self, row)
        dict_api['number'] = value_to_str(row[1].value)
        dict_api['lastname'] = row[2].value
        dict_api['firstname'] = row[3].value
        dict_api['middlename'] = row[4].value
        dict_api['city'] = row[7].value
        dict_api['street'] = row[9].value
        dict_api['house'] = value_to_str(row[10].value)
        dict_api['flat'] = value_to_str(row[11].value)

        debt_date = re.search(self.date_re, row[12].value).group(0)
        dict_api['period'] = datetime.strptime(debt_date, self._format_datetime)

        dict_api['service'] = self._service_code
        dict_api['debt'] = float(row[13].value) if row[13].value else 0

        return dict_api


class FondKapRem(ProvDataExcel):
    def __init__(self, filename=''):
        ProvDataExcel.__init__(self, filename)
        self.first_line = 1
        self._service_code = '625765'

    def _row_to_dict_api(self, row):
        dict_api = ProvDataExcel._row_to_dict_api(self, row)
        dict_api['number'] = row[0].value
        dict_api['lastname'] = u''
        dict_api['firstname'] = u''
        dict_api['middlename'] = u''
        dict_api['territory'] = row[2].value
        dict_api['city'] = row[3].value
        dict_api['street'] = u'{} {}'.format(row[4].value, row[5].value)
        dict_api['house'] = row[6].value
        dict_api['flat'] = row[7].value
        dict_api['period'] = self.debt_date
        dict_api['service'] = self._service_code
        dict_api['debt'] = float(row[8].value) if row[8].value else 0
        return dict_api
