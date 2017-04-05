# -*- coding: utf-8 -*-


import unittest
import exceptions
from datetime import datetime

from provreg import TGK14, Domremstroy, Oblgaz, Dom, Lider, Region, Avangard, FondKapRem

# TODO добавить проверку по количеству записей в файле
regs_data = {
    'TGK14': {
        'class': TGK14,
        'args_init': {'filename': r'.\src\Lstgks.DBF'},
        'debt': 33798.01
    },
    'Domremstroy': {
        'class': Domremstroy,
        'args_init': {'filename': r'.\src\domrem.txt'},
        'debt_date': datetime(2017, 3, 1),
        'debt': 17264479.69
    },
    'Oblgaz': {
        'class': Oblgaz,
        'args_init': {'filename': r'.\src\kokuy.txt'},
        'debt': -999598623.87
    },
    'Dom': {
        'class': Dom,
        'args_init': {'filename': r'.\src\Dom1_2016_12.txt', 'service_code': '3199'},
        'debt': 0
    },
    'Lider': {
        'class': Lider,
        'args_init': {'filename': r'.\src\lider.txt'},
        'debt': 161889893.93
    },
    'Region': {
        'class': Region,
        'args_init': {'filename': r'.\src\region.txt', 'service_code': '8373'},
        'debt_date': datetime(2017, 3, 1),
        'debt': 16686924.89
    },
    'Avangard': {
        'class': Avangard,
        'args_init': {'filename': r'.\src\ava.xlsx'},
        'debt': 0
    },
    'FondKapRem': {
        'class': FondKapRem,
        'args_init': {'filename': r'.\src\fkr.xlsx'},
        'debt_date': datetime(2017, 3, 1),
        'debt': 49629083.36
    },
}

not_correct_regs = ['Oblgaz']


class TestProvData(unittest.TestCase):

    def test_generate_accounts_decoded(self):
        for reg_name in regs_data:

            data = regs_data[reg_name]
            prov_class = data['class']

            # noinspection PyCallingNonCallable
            registry = prov_class(**data['args_init'])
            for key in data:
                if hasattr(registry, key):
                    setattr(registry, key, data[key])
            for _ in registry.generate_accounts_decoded():
                pass

    def test_total_debt(self):
        for reg_name in regs_data:

            data = regs_data[reg_name]
            prov_class = data['class']

            # noinspection PyCallingNonCallable
            registry = prov_class(**data['args_init'])
            for key in data:
                if hasattr(registry, key):
                    setattr(registry, key, data[key])

            debt = 0
            for item in registry.generate_accounts_decoded():
                debt += item['debt']

            # noinspection PyTypeChecker
            self.assertEqual(round((debt - data['debt']) * 100), 0,
                             ('Не совпадает итоговая сумма по поставщику {}\n' +
                              'Сумма в файле: {}. Ожидалось: {}'
                              ).format(reg_name, debt, data['debt']))

    def test_source_data_correct(self):
        _not_correct_regs = []

        for reg_name in regs_data:

            data = regs_data[reg_name]
            prov_class = data['class']

            # noinspection PyCallingNonCallable
            registry = prov_class(**data['args_init'])
            for key in data:
                if hasattr(registry, key):
                    setattr(registry, key, data[key])
            if not registry.source_data_correct():
                _not_correct_regs.append(reg_name)

        self.assertEqual(_not_correct_regs, not_correct_regs)

    def test_process_error(self):
        self.error_data = []

        def source_error_save(**kwargs):
            self.error_data.append(kwargs.copy())

        gaz_registry = Oblgaz(r'.\src\kokuy_bad.txt')
        gaz_registry.error_processor = source_error_save
        for _ in gaz_registry.generate_accounts_decoded():
            pass

        self.assertEqual(len(self.error_data), 1)
        self.assertEqual(self.error_data[0]['at'], 279)
        self.assertEqual(type(self.error_data[0]['exception']), exceptions.ValueError)


if __name__ == '__main__':
    unittest.main()
