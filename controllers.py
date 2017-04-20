# -*- encoding: utf-8 -*-
import MySQLdb
from datetime import datetime, date


def sql_format_params(params):
    formatted_params = {}
    for item in params:
        param_type = type(params[item])
        if param_type in [str, unicode]:
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
            _params['status'] = '1'
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
        sql = "select registry_loading_allowed({})".format(registry_id)
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

    def get_providers(self, params):
        """Возвращает список словарей"""
        _params = sql_format_params(params)

        cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
        where_clause = ' and '.join(['{}={}'.format(item, _params[item]) for item in _params])
        where_clause = where_clause if where_clause else 'True'
        sql = "SELECT * FROM provider WHERE {}".format(where_clause)
        cursor.execute(sql)

        return [rec for rec in cursor.fetchall()]


class Loader(object):
    def __init__(self, coco, tuk, log_file=None):
        self.coco = coco
        self.tuk = tuk
        # self.log_file = log_file

    def load_provs(self, provdatas):
        pass
