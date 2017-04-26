# -*- encoding: utf-8 -*-
import MySQLdb
from datetime import datetime, date
from socket import gaierror
from urllib2 import HTTPError

from settings import TUK_ENCODING, LOGS_ENCODING, CRITICAL_ERROR_COUNT

# Статусы реестров
RS_READY_TO_IMPORT = 1
RS_LOADING = 2
RS_LOADED = 3
RS_ERROR_WHILE_LOADING = 4
RS_CRITICAL_ERROR_COUNT = 5

# Статусы заданий
TS_READY_TO_IMPLEMENT = 1
TS_IMPLEMENTING = 2
TS_FINISHED = 3
TS_ERROR = 4


def sql_format_params(params):
    formatted_params = {}
    for item in params:
        param_type = type(params[item])
        if param_type == unicode:
            formatted_param = "'{}'".format(params[item].encode(TUK_ENCODING))
        elif param_type == str:
            formatted_param = "'{}'".format(params[item])
        elif param_type == date:
            formatted_param = "'{}'".format(params[item].strftime('%Y-%m-%d'))
        elif param_type == datetime:
            formatted_param = "'{}'".format(params[item].strftime('%Y-%m-%d %H:%M:%S'))
        else:
            formatted_param = str(params[item])
        formatted_params[item] = formatted_param
    return formatted_params


class TukConnection(object):
    def __init__(self, db_connection_settings):
        self.db = MySQLdb.connect(**db_connection_settings)

    def __del__(self):
        self.db.close()

    def update_registry(self, registry_id, values):
        if not values:
            return
        _values = sql_format_params(values)
        set_clause = ', '.join(['{}={}'.format(item, _values[item]) for item in _values])
        sql = "UPDATE registry SET {} WHERE registry_id={}".format(set_clause, registry_id)
        self.db.query(sql)
        self.db.commit()

    def update_table(self, table_name, params, values):
        if not values:
            return
        _values = sql_format_params(values)
        set_clause = ', '.join(['{}={}'.format(item, _values[item]) for item in _values])

        _params = sql_format_params(params)
        where_clause = ' and '.join(['{}={}'. format(item, _params[item]) for item in _params])
        where_clause = where_clause if where_clause else 'True'

        sql = "UPDATE {} SET {} WHERE {}".format(table_name, set_clause, where_clause)
        self.db.query(sql)
        self.db.commit()

    def get_or_create_registry(self, params):
        """
        Ищет первый реестр, удовлетворяющий условиям поиска,
        либо создает новый с такими параметрами и статусом 1.
        Возвращает его ID.
        """

        _params = sql_format_params(params)

        where_clause = ' and '.join(['{}={}'. format(item, _params[item]) for item in _params])
        where_clause = where_clause if where_clause else 'True'
        sql = "SELECT registry_id FROM registry WHERE {}". format(where_clause)
        self.db.query(sql)
        data = self.db.store_result().fetch_row()

        if len(data) == 0:
            _params['status'] = str(RS_READY_TO_IMPORT)
            fields = ', '.join([item for item in _params])
            values = ', '.join([_params[item] for item in _params])
            sql = "INSERT INTO registry({}) VALUES ({})".format(fields, values)
            self.db.query(sql)
            insert_id = self.db.insert_id()
            self.db.commit()
            return insert_id
        else:
            return data[0][0]

    def start_registry_loading(self, registry_id):
        """
        Возвращает 0 если не разрешено грузить реестр,
        Устанавливает статус реестра равным 2 и возвращает 1, если разрешено грузить
        """
        sql = "select registry_loading_allowed({})".format(registry_id)
        self.db.query(sql)
        data = self.db.store_result().fetch_row()
        self.db.commit()
        return data[0][0]

    def task_deleting(self, task_id):
        """
        Возвращает 0 если не разрешено удалять по заданию в task_delete,
        Устанавливает статус задания равным 2 и возвращает 1, если разрешено удалять
        """
        sql = "select task_delete_allowed({})".format(task_id)
        self.db.query(sql)
        data = self.db.store_result().fetch_row()
        self.db.commit()
        return data[0][0]

    def get_registries_with_status(self, status):
        return self.get_registries({'status': status})

    def get_registries(self, params):
        """Возвращает список словарей"""
        _params = sql_format_params(params)

        cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
        where_clause = ' and '.join(['{}={}'.format(item, _params[item]) for item in _params])
        where_clause = where_clause if where_clause else 'True'
        sql = "SELECT * FROM registry WHERE {}".format(where_clause)
        cursor.execute(sql)

        return [rec for rec in cursor.fetchall()]

    # TODO: DRY
    def get_providers(self, params):
        """Возвращает список словарей"""
        _params = sql_format_params(params)

        cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
        where_clause = ' and '.join(['{}={}'.format(item, _params[item]) for item in _params])
        where_clause = where_clause if where_clause else 'True'
        sql = "SELECT * FROM provider WHERE {}".format(where_clause)
        cursor.execute(sql)

        return [rec for rec in cursor.fetchall()]

    def get_tasks_delete(self, params):
        """Возвращает список словарей"""
        _params = sql_format_params(params)

        cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
        where_clause = ' and '.join(['{}={}'.format(item, _params[item]) for item in _params])
        where_clause = where_clause if where_clause else 'True'
        sql = """SELECT task_delete.TASK_DELETE_ID, task_delete.DELETE_BEFORE, provider.MNEMO_COCO
            FROM task_delete
            LEFT JOIN provider ON provider.PROVIDER_ID=task_delete.PROVIDER_ID
            WHERE {}""" .format(where_clause)
        cursor.execute(sql)

        return [rec for rec in cursor.fetchall()]

    def get_as_dict_list(self, sql):
        cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        return [rec for rec in cursor.fetchall()]


class Loader(object):
    def __init__(self, coco, tuk, logger=None):
        # Количество записей отправляемых за раз
        self.BLOCK_COUNT = 50 if __debug__ else 500
        self.coco = coco
        self.tuk = tuk
        self.error_processor = None
        self.logger = logger

    def _log_imported(self, filename, registry_id, first_item, last_item):
        if self.logger:
            self.logger.info('File: {}. Registry: {}. Imported elements: {} - {}'.format(
                filename.encode(LOGS_ENCODING),
                registry_id,
                first_item,
                last_item
            ))

    @staticmethod
    def _calc_registry_date(provdata):
        if hasattr(provdata, 'debt_date') and provdata.debt_date:
            return provdata.debt_date
        else:
            return provdata.get_max_debt_date()

    def load_provs(self, provdata_dict):
        """
        Загружает поставщиков в кокос,
        дозагружает если LAST_IMPORTED_ITEM>0 (статус должен быть 1).
        Устанавливает LAST_IMPORTED_ITEM (нумерация с нуля)
        Если у передаваемого ProvData отсутствует registry_id, то он пропускается

        :param provdata_dict: словарь, ключи - мнемокоды кокоса, значения - списки из элементов ProvData.
        :return: None
        """
        for mnemo_coco in provdata_dict:

            for provdata in provdata_dict[mnemo_coco]:
                if not hasattr(provdata, 'registry_id'):
                    continue
                registry = self.tuk.get_registries({'REGISTRY_ID': provdata.registry_id})[0]

                if self.tuk.start_registry_loading(provdata.registry_id):
                    i = 0
                    last_imported_item = registry['LAST_IMPORTED_ITEM'] if registry['LAST_IMPORTED_ITEM'] else 0

                    try:
                        for block in provdata.generate_block_accounts(self.BLOCK_COUNT):
                            # если последний элемент текущей итерации меньше последнего имортированного в кокос,
                            # то пропустить блок
                            if (i + len(block)-1) <= last_imported_item:
                                i += len(block)
                                continue

                            if __debug__ and i >= 200:
                                print 'debug stop', i
                                break

                            self.coco.import_accounts(mnemo_coco, block)
                            self.coco.import_balances(mnemo_coco, block)
                            self._log_imported(provdata.filename, provdata.registry_id, i, i + len(block) - 1)
                            i += len(block)

                    except Exception as exception_instance:

                        # Сохраняем все что можем в БД
                        if isinstance(exception_instance, HTTPError) or \
                           isinstance(exception_instance, gaierror):
                            # Если ошибка связи то пытаться в следующий раз грузить
                            self.tuk.update_registry(provdata.registry_id, {'STATUS': RS_READY_TO_IMPORT,
                                                                            'LAST_IMPORTED_ITEM': i-1})
                        else:
                            # Если не ошибка связи то сначала разобраться
                            self.tuk.update_registry(provdata.registry_id, {'STATUS': RS_ERROR_WHILE_LOADING,
                                                                            'LAST_IMPORTED_ITEM': i-1})

                        # Вызываем обработчик если есть
                        if self.error_processor:
                            self.error_processor(
                                provdata=provdata,
                                exception=exception_instance
                            )
                        else:
                            raise
                    else:
                        if provdata.error_count < CRITICAL_ERROR_COUNT:
                            max_debt_date = self._calc_registry_date(provdata)
                            self.tuk.update_registry(provdata.registry_id, {
                                'STATUS': RS_LOADED,
                                'MAX_DEBT_DATE': max_debt_date,
                                'LAST_IMPORTED_ITEM': i-1,
                                'ERROR_COUNT': provdata.error_count
                            })
                        else:
                            self.tuk.update_registry(provdata.registry_id, {
                                'STATUS': RS_CRITICAL_ERROR_COUNT,
                                'LAST_IMPORTED_ITEM': i-1,
                                'ERROR_COUNT': provdata.error_count
                            })


class Deleter(object):
    def __init__(self, tuk, coco, logger=None):
        self.tuk = tuk
        self.coco = coco
        self.logger = logger
        self.error_processor = None

    def _log_deleted(self, mnemo_coco, len_accounts, date_from, date_to):
        if self.logger:
            log_string = 'Balances deleted. Provider:{},accounts count:{}, date_from:{:%Y-%m-%d}, date_to:{:%Y-%m-%d}'
            self.logger.info(log_string.format(
                    mnemo_coco,
                    len_accounts,
                    date_from,
                    date_to
                ))

    def smart_delete(self):
        self.tuk.db.query('call CREATE_TASKS_DELETE()')
        self.tuk.db.commit()
        tasks = self.tuk.get_tasks_delete({'STATUS': TS_READY_TO_IMPLEMENT})
        for task in tasks:
            task_id = task['TASK_DELETE_ID']
            if self.tuk.task_deleting(task_id):
                mnemo_coco = task['MNEMO_COCO']
                try:
                    delete_before = task['DELETE_BEFORE']
                    search_results = self.coco.search_account(mnemo_coco, {'number': '%'})
                    all_accounts = []
                    for account in search_results:
                        all_accounts.append(account)

                    self.coco.del_balances(mnemo_coco, all_accounts, datetime(2000, 1, 1), delete_before)
                    self._log_deleted(mnemo_coco, len(all_accounts), datetime(2000, 1, 1), delete_before)

                except Exception as exception_instance:
                    self.tuk.update_table('task_delete', {'TASK_DELETE_ID': task_id}, {'STATUS': TS_ERROR})
                    if self.error_processor:
                        self.error_processor(
                            task_id=task_id,
                            mnemo_coco=mnemo_coco,
                            exception=exception_instance
                        )
                    else:
                        raise
                else:
                    self.tuk.update_table('task_delete', {'TASK_DELETE_ID': task_id}, {'STATUS': TS_FINISHED})
