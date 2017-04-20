# -*- coding: utf-8 -*-
# TODO Либо всех поставщиков в разные модули, либо всех в один (лучше второе)
from .provdata import ProvData, ProvDataText, ProvDataExcel
from .dom import Dom
from .oblgaz import Oblgaz
from .tgk14 import TGK14
from .domremstroy import Domremstroy
from .other import Lider, Region
from xlprovs import Avangard, FondKapRem

__all__ = (
    'ProvData', 'ProvDataText', 'ProvDataExcel',
    'Dom', 'Oblgaz', 'TGK14', 'Domremstroy', 'Lider', 'Region',
    'Avangard', 'FondKapRem'
)
