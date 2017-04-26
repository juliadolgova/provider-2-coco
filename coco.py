# -*- encoding: utf-8 -*-
"""
В параметрах методов import_accounts, import_balances дата должна быть типа datetime
"""
import pgpxmlrpc
from functools import partial


class CoconutService(object):
    def __init__(self, dict_api):
        self.coconut = pgpxmlrpc.Service(
            uri=dict_api['uri'],
            service_key=dict_api['skey'],
            gpg_homedir=dict_api['dir_keyring'],
            gpg_key=dict_api['key'],
            gpg_password=dict_api['pswd']
        )
        self.company = 'mks'
        self.method_names = ('balance.import_providers',
                             'balance.import_services',
                             'balance.import_accounts',
                             'balance.import_balances',
                             'balance.account_balance',
                             'balance.search_account',
                             'balance.get_providers',
                             'balance.get_services',
                             'balance.del_accounts',
                             'balance.del_balances',
                             )

    def print_methods_help(self):
        for method in self.method_names:
            print method
            res = self.coconut.system.methodHelp(method)
            print res

    def __getattr__(self, item):
        method = '{}.{}'.format('balance', item)
        return partial(self.coconut.__getattr__(method), self.company)

    def something(self):
        return self.__dict__
