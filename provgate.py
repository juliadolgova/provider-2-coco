# -*- encoding: utf-8 -*-
"""
Реализация функции get_provdata_to_load().
"""
import hashlib
import os.path
from datetime import datetime
from os import walk

import provreg

DS_DATE_FILE_CREATED = 'date_file_created'  # будет браться дата создания файла
DS_DATE_FILE_MODIFIED = 'date_file_modified'  # будет браться дата изменения файла
DS_DATE_NOW = 'date_now'  # будет браться текущая дата
DS_MONTH_BEGIN = 'month_begin'  # будет браться первое число текущего месяца


def get_debt_date(filename, date_source):
    debt_date = datetime(2000, 1, 1)

    if date_source == DS_DATE_NOW:
        debt_date = datetime.today()
    elif date_source == DS_MONTH_BEGIN:
        _today = datetime.today()
        debt_date = datetime(_today.year, _today.month, 1)
    elif date_source == DS_DATE_FILE_MODIFIED:
        debt_date = datetime.fromtimestamp(os.path.getmtime(filename))
    elif date_source == DS_DATE_FILE_CREATED:
        debt_date = datetime.fromtimestamp(os.path.getctime(filename))
    debt_date = datetime(debt_date.year, debt_date.month, debt_date.day)
    return debt_date


def get_hash(filename):
    block_size = 65536
    hasher = hashlib.md5()
    with open(filename, 'rb') as _file:
        buf = _file.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = _file.read(block_size)
    return hasher.hexdigest()


# TODO: Написать тест для разных путей (., относительный путь, полный путь)
def get_provdata_to_load(path, tuk, error_processor=None):
    """
        Возвращает словарь {mnemo_coco: [provdata],...}, который нужно загрузить в кокос.
        Создает для них строки в tuk.registry (если не были созданы)

        Берет все файлы из указанного пути,
        фильтрует в соответствии с tuk.registry
        (не берет уже загруженные файлы с тем же названием, кэшем, родительской папкой),
        инициализирует в соответствии с tuk.provider
        error_processor - обработчик ошибок во время преобразования к формату кокоса
        Файлы нужно отсортировать по подпапкам, названия подпапок = мнемо поставщиков в кокосе
        Объектам ProvData добавляется свойство registry_id (код записи в таблице tuk.registry)
    """
    provdatas = dict()

    for item in walk(path):
        # Определяем настройки поставщика прописанные в tuk.provider
        mnemo_coco = os.path.split(item[0])[1]
        providers = tuk.get_providers({'MNEMO_COCO': mnemo_coco})
        if not providers:
            continue
        provider = providers[0]

        provdatas[mnemo_coco] = []

        for _file in item[2]:
            # Определяем уникальные параметры реестра (код поставщика, хэш файла)
            provider_id = provider['PROVIDER_ID']
            _hash = get_hash(os.path.join(item[0], _file))

            registry_id = tuk.get_or_create_registry({
                'FILENAME': _file,
                'PROVIDER_ID': provider_id,
                'HASH': _hash
            })
            status = tuk.get_registries({'REGISTRY_ID': registry_id})[0]['STATUS']

            if status == 1:
                full_filename = os.path.join(item[0], _file)
                init_params = dict()
                init_params['filename'] = full_filename
                if provider['SERVICE_CODE'].strip():
                    init_params['service_code'] = provider['SERVICE_CODE']
                prov_class = getattr(provreg, provider['CLASS_NAME'])

                registry = prov_class(**init_params)
                if provider['DATE_SOURCE'].strip():
                    registry.debt_date = get_debt_date(full_filename, provider['DATE_SOURCE'])
                registry.error_processor = error_processor

                registry.registry_id = registry_id

                provdatas[mnemo_coco].append(registry)

        if not provdatas[mnemo_coco]:
            del provdatas[mnemo_coco]

    return provdatas
