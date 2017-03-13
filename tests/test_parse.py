# -*- encoding: utf-8 -*-
from datetime import datetime

from provreg import srcutils
from provreg import TGK14, Domremstroy, Oblgaz, Dom


def try_tgk14():
    tgk14_registry = TGK14(r'.\src\Lstgks.DBF')
    tgk14_registry.error_processor = srcutils.source_error_print
    for _ in tgk14_registry.generate_accounts_decoded():
        pass


def try_oblgaz():
    gaz_registry = Oblgaz(r'.\src\kokuy_bad.txt')
    gaz_registry.error_processor = srcutils.source_error_print
    for _ in gaz_registry.generate_accounts_decoded():
        pass


def try_domremstroy():
    registry = Domremstroy(r'.\src\domrem.txt')
    registry.debt_date = datetime(2017, 3, 1)
    registry.delimiter = ','
    registry.error_processor = srcutils.source_error_print
    for _ in registry.generate_accounts_decoded():
        pass


def try_dom():
    registry = Dom(r'.\src\Dom1_2016_12.txt')
    registry.error_processor = srcutils.source_error_print
    for _ in registry.generate_accounts_decoded():
        pass


if __name__ == '__main__':
    try_tgk14()
    try_oblgaz()
    try_domremstroy()
    try_dom()
