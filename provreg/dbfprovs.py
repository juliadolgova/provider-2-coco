# -*- encoding: utf-8 -*-
from dbfpy import dbf
from datetime import date, datetime, time

from provdata import ProvData


class ProvDataDBF(ProvData):
    def __init__(self, filename=''):
        ProvData.__init__(self)
        # исходный файл
        self.filename = filename
        # кодировка исходного файла
        self._coding = 'cp1251'

        # ключи словаря: ключи из API для импорта в кокос
        # значения словаря: список: имя поля в исходном файле, тип поля в исходном файле, тип в словаре для выгрузки
        self._fields_map = {}

    # создавалось для str->unicode, int->unicode, date->datetime
    # TODO: для остальных преобразований доделать
    def _mapped_decoded_dict(self, source_dict):
        mapped_dict = dict()
        for key in self._fields_map:
            record_field = source_dict[self._fields_map[key][0]]
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
            mapped_dict[key] = record_field
        return mapped_dict

    def _record_to_dict_api(self, record):
        dict_api = self._default_dict()
        dict_api.update(self._mapped_decoded_dict(record))
        return dict_api

    def generate_accounts_decoded(self):
        self.error_count = 0
        record_num = 0
        db = dbf.Dbf(self.filename)

        for record in db:
            record_num += 1
            try:
                yield self._record_to_dict_api(record)
            except Exception as exception_instance:
                if self.error_processor:
                    self.error_count += 1
                    self.error_processor(
                        file=self.filename,
                        at=record_num,
                        record=record,
                        exception=exception_instance
                    )
                else:
                    raise

    def source_data_correct(self):
        """Проверять нечего. Возвращает True"""
        return True


class TGK14(ProvDataDBF):
    def __init__(self, filename=''):
        ProvDataDBF.__init__(self, filename)

        # Заголовки в исходном файле ТГК14:
        # NLS	L_NAME	F_NAME	M_NAME	CITY	NAIM	DOM	FLAT	DATE	VID_SERV	SALDO_TGK	CHARGE
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


class Vodokanal(ProvDataDBF):
    def __init__(self, filename=''):
        ProvDataDBF.__init__(self, filename)
        self._coding = 'cp866'

        # Заголовки в исходном файле Водоканала:
        # L_NAME	F_NAME	M_NAME	TOWN	STREET	DOM	KORP	KW	LITERA	KOD	SERVICE	DATA	SALDO
        self._fields_map = {
            'number': ['KOD', int, unicode],
            'lastname': ['L_NAME', str, unicode],
            'firstname': ['F_NAME', str, unicode],
            'middlename': ['M_NAME', str, unicode],
            'city': ['TOWN', str, unicode],
            'street': ['STREET', str, unicode],
            'house': ['DOM', int, unicode],
            'flat': ['KW', int, unicode],
            'period': ['DATA', date, datetime],
            'service': ['SERVICE', int, unicode],
            'debt': ['SALDO', float, float],
            '_subflat': ['LITERA', str, unicode],
            '_house_liter': ['KORP', str, unicode]
        }

    def _record_to_dict_api(self, record):
        dict_api = self._default_dict()
        dict_api.update(self._mapped_decoded_dict(record))

        dict_api['house'] = '/'.join([dict_api['house'], dict_api['_house_liter']])
        dict_api['flat'] = '/'.join([dict_api['flat'], dict_api['_subflat']])
        del dict_api['_house_liter']
        del dict_api['_subflat']

        return dict_api


class Teplovodokanal(ProvDataDBF):
    def __init__(self, filename=''):
        ProvDataDBF.__init__(self, filename)
        self._coding = 'cp1251'

        # SERVICE	SUPPLIER	ACCOUNT	LAST_NAME	FIRST_NAME	MIDDLE_NAM	REGION	TERRITORY	TOWN
        # PREFSTREET	STREET	BUILDING	FLAT	PERIOD	DEBT	DEBT_FINE
        self._fields_map = {
            'number': ['ACCOUNT', str, unicode],
            'lastname': ['LAST_NAME', str, unicode],
            'firstname': ['FIRST_NAME', str, unicode],
            'middlename': ['MIDDLE_NAM', str, unicode],
            'city': ['TOWN', str, unicode],
            'street': ['STREET', str, unicode],
            'house': ['BUILDING', str, unicode],
            'flat': ['FLAT', str, unicode],
            'period': ['PERIOD', date, datetime],
            'service': ['SERVICE', int, unicode],
            'debt': ['DEBT', float, float],
            'territory': ['TERRITORY', str, unicode],
            'region': ['REGION', str, unicode],
            'pfxstreet': ['PREFSTREET', str, unicode],
            'fine': ['DEBT_FINE', float, float]
        }


class Severniy(ProvDataDBF):
    def __init__(self, filename=''):
        ProvDataDBF.__init__(self, filename)
        self._coding = 'cp1251'
        self._service_code = 'servid_unkn'

        # ACCOUNT	REGION	TERRITORY	TOWN	PREFSTREET	STREET	BUILDING
        # FLAT	PERIOD	DEBT	DEBT_FINE	INDEBTED	SPACE
        self._fields_map = {
            'number': ['ACCOUNT', str, unicode],
            'city': ['TOWN', str, unicode],
            'street': ['STREET', str, unicode],
            'house': ['BUILDING', str, unicode],
            'flat': ['FLAT', str, unicode],
            'territory': ['TERRITORY', str, unicode],
            'region': ['REGION', str, unicode],
            'pfxstreet': ['PREFSTREET', str, unicode],
            'fine': ['DEBT_FINE', float, float]
        }

    def _record_to_dict_api(self, record):
        dict_api = ProvDataDBF._record_to_dict_api(self, record)
        dict_api['lastname'] = ''
        dict_api['firstname'] = ''
        dict_api['middlename'] = ''
        dict_api['service'] = self._service_code
        dict_api['period'] = datetime.strptime(record['PERIOD'], '%d.%m.%Y')
        dict_api['debt'] = float(record['DEBT'].replace(chr(0xa0), '').replace(',', '.'))
        return dict_api
