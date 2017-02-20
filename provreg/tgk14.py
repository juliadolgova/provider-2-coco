# -*- encoding: utf-8 -*-
from dbfpy import dbf
from datetime import date, datetime, time

from provdata import ProvData
from srcutils import process_source_exception


class TGK14(ProvData):
    def __init__(self, filename=''):
        ProvData.__init__(self)
        # исходный файл
        self._filename = filename
        # кодировка исходного файла
        self._coding = 'cp1251'
        self.__errors = []

        # Заголовки в исходном файле ТГК14:
        # NLS	L_NAME	F_NAME	M_NAME	CITY	NAIM	DOM	FLAT	DATE	VID_SERV	SALDO_TGK	CHARGE
        # ключи словаря: ключи из API для импорта в кокос
        # значения словаря: список: имя поля висходном файле, тип поля в исходном файле, тип в словаре для выгрузки
        # TODO Если потребуется изменять типы датовых полей, то доработать _record_to_dict_api
        self._fields_map = {
            'number': ['NLS', str, unicode],
            'lastname': ['L_NAME', str, unicode],
            'firstname': ['F_NAME', str, unicode],
            'middlename': ['M_NAME', str, unicode],
            'city': ['CITY', str, unicode],
            'street': ['NAIM', str, unicode],
            'house': ['DOM', str, unicode],
            'flat': ['FLAT', str, unicode],
            'period': ['DATE', date, datetime],
            'service': ['VID_SERV', int, unicode],
            'debt': ['CHARGE', float, float]
        }

    def set_filename(self, filename):
        self._filename = filename
        self.__errors = []

    def get_filename(self):
        return self._filename

    filename = property(get_filename, set_filename, None, u'Имя исходного файла')

    @staticmethod
    def _default_dict():
        return {
            'fine': None,
            'charge': None,
            'region': u'',
            'territory': u'',
            'pfxstreet': u''
        }

    def _record_to_dict_api(self, record):
        dict_api = self._default_dict()
        for key in self._fields_map:
            record_field = record[self._fields_map[key][0]]
            record_type = self._fields_map[key][1]
            destination_type = self._fields_map[key][2]
            if record_type == str:
                record_field = record_field.decode(self._coding)
                record_type = unicode
            if record_type == date and destination_type == datetime:
                record_field = datetime.combine(record_field, time(0, 0))
                record_type = datetime
            if record_type != destination_type:
                record_field = destination_type(record_field)
                # record_type = new_type # раскомментировать для дальнейшего преобразования
            dict_api[key] = record_field
        return dict_api

    def generate_accounts_decoded(self):
        # TODO Заполнить __errors
        record_num = 0
        db = dbf.Dbf(self._filename)
        for record in db:
            record_num += 1
            try:
                yield self._record_to_dict_api(record)
            except Exception as exception_instance:
                error_message = 'Error while processing line %d in file %s'
                process_source_exception(error_message % (record_num, self._filename), exception_instance)

    def source_data_correct(self):
        return True

    def source_data_errors(self):
        return self.__errors
