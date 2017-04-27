# -*- encoding: utf-8 -*-
from functools import partial

import controllers
import settings
import provgate
import coco
import utils


if __name__ == '__main__':
    # Самое первое - включить логирование
    logger = utils.logger(settings.LOG_PATH, 'main')
    logger.info('Task started')
    # Инициализируем службы
    error_logger = utils.logger(settings.LOG_PATH, 'errors')
    tuk = controllers.TukConnection(settings.TUK_DB)
    coco_service = coco.CoconutService(settings.WORK_COCONUT_SETTINGS)

    # Получить объекты для загрузки
    source_error_processor = partial(utils.source_error_log, logger=error_logger)
    provdatas = provgate.get_provdata_to_load(settings.REG_PATH, tuk, source_error_processor)

    # Загрузить в Кокос
    loader = controllers.Loader(coco_service, tuk, logger)
    loader.error_processor = partial(utils.files_error_log, logger=error_logger)
    logger.info('Loading started')
    loader.load_provs(provdatas)
    logger.info('Loading finished')

    # Удалить устаревшие данные из Кокоса
    deleter = controllers.Deleter(tuk, coco_service, logger)
    deleter.error_processor = partial(utils.task_delete_error_log, logger=error_logger)
    logger.info('Deleting started')
    deleter.smart_delete()
    logger.info('Deleting finished')

    logger.info('Task finished')
