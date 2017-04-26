# -*- coding: utf-8 -*-
# TODO Либо всех поставщиков в разные модули, либо всех в один (лучше второе)
from .provdata import ProvData
from .tgk14 import TGK14
from .txtprovs import Domremstroy, Oblgaz, Dom, Lider, Region, ProvDataText
from xlprovs import Avangard, FondKapRem, ProvDataExcel

__all__ = (
    'ProvData', 'ProvDataText', 'ProvDataExcel',
    'Dom', 'Oblgaz', 'TGK14', 'Domremstroy', 'Lider', 'Region',
    'Avangard', 'FondKapRem'
)
